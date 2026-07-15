from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from echel.authority import Principal
from echel.domain.value_objects import Identifier
from echel.relationships import RelationshipService
from echel.storage import CanonicalRecordStore, RecordExpectation, RecordWritePlan, TransactionJournal


FINDING_CAPABILITY = "finding:decide"
FINDING_KINDS = frozenset({"contradiction", "risk", "gap", "defect", "question"})
FINDING_SEVERITIES = frozenset({"info", "warning", "error", "critical"})
ACTIVE_FINDING_STATES = frozenset({"open", "accepted"})


@dataclass
class FindingError(RuntimeError):
    code: str
    field: str
    detail: str

    def __str__(self) -> str:
        return f"{self.code} at /{self.field}: {self.detail}"


@dataclass(frozen=True)
class FindingImpact:
    finding_id: str
    status: str
    severity: str
    level: str
    maturity_usable: bool
    affected: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "status": self.status,
            "severity": self.severity,
            "level": self.level,
            "maturity_usable": self.maturity_usable,
            "affected": list(self.affected),
        }


@dataclass(frozen=True)
class FindingCreation:
    transaction_id: str
    records: tuple[dict[str, Any], ...]
    impact: FindingImpact

    def to_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "finding_id": self.records[0]["id"],
            "relationships": [record["id"] for record in self.records[1:]],
            "impact": self.impact.to_dict(),
            "mutation": "preview",
        }


@dataclass(frozen=True)
class FindingDecision:
    record: dict[str, Any]
    expectation: RecordExpectation
    action: str
    actor: str
    impact: FindingImpact

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.record["id"],
            "from_revision": self.expectation.revision,
            "to_revision": self.record["revision"],
            "to_status": self.action,
            "actor": self.actor,
            "impact": self.impact.to_dict(),
            "mutation": "preview",
        }


class FindingService:
    """Record findings and derive impact without rewriting affected records."""

    def __init__(self, store: CanonicalRecordStore):
        self.store = store
        self.relationships = RelationshipService(store)
        self.transactions = TransactionJournal(store)

    def preview_create(
        self,
        transaction_id: str,
        finding_id: str,
        kind: str,
        statement: str,
        severity: str,
        affected: tuple[str, ...],
        provenance: dict[str, str],
        created_at: str,
    ) -> FindingCreation:
        self._validate_new(kind, statement, severity, affected, created_at)
        finding_identifier = Identifier(finding_id)
        if finding_identifier.namespace != "finding":
            raise FindingError("ECHEL-FINDING-ID-INVALID", "finding_id", "must use finding:local form")
        finding: dict[str, Any] = {
            "schema_version": 1,
            "record_type": "finding",
            "id": finding_id,
            "revision": 1,
            "created_at": created_at,
            "updated_at": created_at,
            "provenance": provenance,
            "kind": kind,
            "statement": statement.strip(),
            "status": "open",
            "severity": severity,
        }
        pending = {finding_id: "finding"}
        records = [finding]
        for index, target in enumerate(affected, start=1):
            target_id = Identifier(target)
            transition = self.relationships.preview(
                f"relationship:{finding_identifier.local}-affects-{index}-{target_id.namespace}-{target_id.local}",
                finding_id,
                "affects",
                target,
                f"{kind} finding impacts {target}: {statement.strip()}",
                provenance,
                created_at,
                pending_endpoints=pending,
            )
            records.append(transition.record)
        self.transactions.preview(transaction_id, records)
        impact = self._impact(finding, tuple(sorted(set(affected))))
        return FindingCreation(transaction_id, tuple(records), impact)

    def apply_create(self, creation: FindingCreation) -> None:
        finding = creation.records[0]
        pending = {str(finding.get("id")): "finding"}
        for relationship in creation.records[1:]:
            validated = self.relationships.preview(
                str(relationship.get("id", "")),
                str(relationship.get("source", "")),
                str(relationship.get("predicate", "")),
                str(relationship.get("target", "")),
                str(relationship.get("reason", "")),
                relationship.get("provenance", {}),
                str(relationship.get("created_at", "")),
                pending_endpoints=pending,
            )
            if validated.record != relationship:
                raise FindingError(
                    "ECHEL-FINDING-TRANSITION-INVALID",
                    "creation",
                    "relationship no longer matches its validated preview",
                )
        self.transactions.execute(creation.transaction_id, list(creation.records))

    def assess(self, finding_id: str) -> FindingImpact:
        finding = self.store.load("finding", finding_id).record
        affected = tuple(
            sorted(
                str(loaded.record["target"])
                for loaded in self.store.scan("relationship")
                if loaded.record.get("source") == finding_id
                and loaded.record.get("predicate") == "affects"
            )
        )
        return self._impact(finding, affected)

    def preview_decision(
        self,
        finding_id: str,
        action: str,
        principal: Principal,
        rationale: str,
        decided_at: str,
    ) -> FindingDecision:
        self._authorize(principal)
        if action not in {"accepted", "resolved", "dismissed"}:
            raise FindingError(
                "ECHEL-FINDING-ACTION-INVALID", "action", "must be accepted, resolved, or dismissed"
            )
        if not rationale.strip():
            raise FindingError(
                "ECHEL-FINDING-RATIONALE-REQUIRED", "rationale", "a decision requires a rationale"
            )
        self._validate_time(decided_at)
        loaded = self.store.load("finding", finding_id)
        current_status = loaded.record.get("status")
        if current_status not in ACTIVE_FINDING_STATES:
            raise FindingError(
                "ECHEL-FINDING-STATE-CONFLICT",
                "status",
                f"cannot decide a finding in state {current_status!r}",
            )
        if current_status == "accepted" and action == "accepted":
            raise FindingError(
                "ECHEL-FINDING-STATE-CONFLICT", "status", "finding is already accepted"
            )
        updated = deepcopy(loaded.record)
        updated["status"] = action
        updated["revision"] = loaded.record["revision"] + 1
        updated["updated_at"] = decided_at
        updated["decision"] = {
            "action": action,
            "actor": principal.id,
            "actor_kind": "human",
            "capability": FINDING_CAPABILITY,
            "rationale": rationale.strip(),
            "decided_at": decided_at,
            "finding_revision": loaded.record["revision"],
        }
        self.store.preview_write(updated, loaded.expectation)
        affected = self.assess(finding_id).affected
        return FindingDecision(
            updated,
            loaded.expectation,
            action,
            principal.id,
            self._impact(updated, affected),
        )

    def apply_decision(self, decision: FindingDecision) -> RecordWritePlan:
        evidence = decision.record.get("decision")
        if (
            decision.record.get("status") != decision.action
            or decision.action not in {"accepted", "resolved", "dismissed"}
            or not isinstance(evidence, dict)
            or evidence.get("action") != decision.action
            or evidence.get("actor") != decision.actor
            or evidence.get("actor_kind") != "human"
            or evidence.get("capability") != FINDING_CAPABILITY
            or evidence.get("finding_revision") != decision.expectation.revision
        ):
            raise FindingError(
                "ECHEL-FINDING-TRANSITION-INVALID",
                "decision",
                "decision evidence does not match the finding transition",
            )
        return self.store.write(decision.record, decision.expectation)

    @staticmethod
    def _impact(finding: dict[str, Any], affected: tuple[str, ...]) -> FindingImpact:
        active = finding["status"] in ACTIVE_FINDING_STATES
        severity = str(finding["severity"])
        level = "none" if not active else {"info": "notice", "warning": "caution", "error": "blocked", "critical": "blocked"}[severity]
        return FindingImpact(
            finding_id=str(finding["id"]),
            status=str(finding["status"]),
            severity=severity,
            level=level,
            maturity_usable=not active or severity in {"info", "warning"},
            affected=affected,
        )

    @staticmethod
    def _validate_new(
        kind: str, statement: str, severity: str, affected: tuple[str, ...], created_at: str
    ) -> None:
        if kind not in FINDING_KINDS:
            raise FindingError("ECHEL-FINDING-KIND-INVALID", "kind", f"known kinds: {sorted(FINDING_KINDS)}")
        if not statement.strip():
            raise FindingError("ECHEL-FINDING-STATEMENT-REQUIRED", "statement", "must not be empty")
        if severity not in FINDING_SEVERITIES:
            raise FindingError("ECHEL-FINDING-SEVERITY-INVALID", "severity", f"known severities: {sorted(FINDING_SEVERITIES)}")
        if not affected or len(affected) != len(set(affected)):
            raise FindingError("ECHEL-FINDING-AFFECTS-INVALID", "affected", "requires unique affected records")
        FindingService._validate_time(created_at)

    @staticmethod
    def _authorize(principal: Principal) -> None:
        if principal.kind != "human" or FINDING_CAPABILITY not in principal.capabilities:
            raise FindingError(
                "ECHEL-FINDING-AUTHORITY-DENIED",
                "principal",
                "an authorized human with finding:decide capability must decide findings",
            )

    @staticmethod
    def _validate_time(value: str) -> None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise FindingError(
                "ECHEL-FINDING-TIME-INVALID", "timestamp", "must be an RFC 3339 date-time"
            ) from exc
        if parsed.tzinfo is None:
            raise FindingError(
                "ECHEL-FINDING-TIME-INVALID", "timestamp", "must include a timezone"
            )
