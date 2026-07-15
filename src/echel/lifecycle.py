from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from echel.authority import AUTHORITY_CAPABILITY, Principal
from echel.domain.value_objects import Identifier
from echel.findings import ACTIVE_FINDING_STATES
from echel.methodology.lifecycle import get_stage, next_stage
from echel.profiles import get_profile
from echel.relationships import ENDPOINT_TYPES
from echel.storage import CanonicalRecordStore, RecordExpectation, RecordWritePlan, TransactionJournal


LIFECYCLE_CAPABILITY = "lifecycle:advance"
PROTECTED_TYPES = frozenset({"claim", "decision", "learning"})
FORWARD_PROPAGATION_PREDICATES = frozenset({"informs", "supports"})


@dataclass
class LifecycleError(RuntimeError):
    code: str
    field: str
    detail: str

    def __str__(self) -> str:
        return f"{self.code} at /{self.field}: {self.detail}"


@dataclass(frozen=True)
class MaturityAssessment:
    project_id: str
    current: str
    next: str | None
    profile: str
    policy: str
    required_kinds: tuple[str, ...]
    usable: bool
    missing_kinds: tuple[str, ...]
    blocking_findings: tuple[str, ...]
    cautions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        if self.usable:
            explanation = (
                "Current maturity has the minimum accepted knowledge and no blocking findings."
            )
        else:
            explanation = "Advance is blocked; resolve missing knowledge or active findings."
        return {
            "project_id": self.project_id,
            "current": self.current,
            "next": self.next,
            "profile": self.profile,
            "policy": self.policy,
            "required_kinds": list(self.required_kinds),
            "usable": self.usable,
            "missing_kinds": list(self.missing_kinds),
            "blocking_findings": list(self.blocking_findings),
            "cautions": list(self.cautions),
            "explanation": explanation,
        }


@dataclass(frozen=True)
class MaturityTransition:
    record: dict[str, Any]
    expectation: RecordExpectation
    assessment: MaturityAssessment
    actor: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.record["id"],
            "from": self.assessment.current,
            "to": self.record["maturity"],
            "next_revision": self.record["revision"],
            "actor": self.actor,
            "assessment": self.assessment.to_dict(),
            "mutation": "preview",
        }


@dataclass(frozen=True)
class BackwardRevision:
    transaction_id: str
    records: tuple[dict[str, Any], ...]
    finding_id: str
    root_id: str
    actor: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "finding_id": self.finding_id,
            "root_id": self.root_id,
            "stale_records": [record["id"] for record in self.records],
            "actor": self.actor,
            "mutation": "preview",
        }


class LifecycleService:
    """Explain forward maturity and explicit backward knowledge revision."""

    def __init__(self, store: CanonicalRecordStore):
        self.store = store
        self.transactions = TransactionJournal(store)

    def assess(self, project_id: str) -> MaturityAssessment:
        project = self.store.load("project", project_id).record
        stage = get_stage(str(project["maturity"]))
        profile = get_profile(str(project["profile"]))
        required_kinds = profile.required_for(stage.id, stage.required_kinds)
        accepted = {
            str(loaded.record["kind"]): str(loaded.record["id"])
            for loaded in self.store.scan("claim")
            if loaded.record.get("status") == "accepted"
            and loaded.record.get("stage") == stage.id
        }
        missing = tuple(kind for kind in required_kinds if kind not in accepted)
        required_ids = frozenset(accepted.get(kind) for kind in required_kinds) - {None}
        blocking: list[str] = []
        cautions: list[str] = []
        affected_by_finding = self._finding_targets()
        for loaded in self.store.scan("finding"):
            finding = loaded.record
            if finding.get("status") not in ACTIVE_FINDING_STATES:
                continue
            if not required_ids.intersection(affected_by_finding.get(str(finding["id"]), ())):
                continue
            if finding["severity"] in {"error", "critical"}:
                blocking.append(str(finding["id"]))
            elif finding["severity"] in {"warning", "info"}:
                cautions.append(str(finding["id"]))
        following = next_stage(stage.id)
        return MaturityAssessment(
            project_id=project_id,
            current=stage.id,
            next=following.id if following else None,
            profile=profile.id,
            policy=f"{profile.id}/v1",
            required_kinds=required_kinds,
            usable=not missing and not blocking,
            missing_kinds=missing,
            blocking_findings=tuple(sorted(blocking)),
            cautions=tuple(sorted(cautions)),
        )

    def preview_advance(
        self,
        project_id: str,
        principal: Principal,
        rationale: str,
        decided_at: str,
    ) -> MaturityTransition:
        self._authorize(principal, LIFECYCLE_CAPABILITY)
        self._validate_reason_time(rationale, decided_at)
        assessment = self.assess(project_id)
        if not assessment.usable or assessment.next is None:
            raise LifecycleError(
                "ECHEL-LIFECYCLE-ADVANCE-BLOCKED",
                "maturity",
                str(assessment.to_dict()),
            )
        loaded = self.store.load("project", project_id)
        updated = deepcopy(loaded.record)
        updated["maturity"] = assessment.next
        updated["revision"] = loaded.record["revision"] + 1
        updated["updated_at"] = decided_at
        updated["maturity_transition"] = {
            "actor": principal.id,
            "actor_kind": "human",
            "capability": LIFECYCLE_CAPABILITY,
            "from": assessment.current,
            "to": assessment.next,
            "rationale": rationale.strip(),
            "decided_at": decided_at,
            "project_revision": loaded.record["revision"],
        }
        self.store.preview_write(updated, loaded.expectation)
        return MaturityTransition(updated, loaded.expectation, assessment, principal.id)

    def apply_advance(self, transition: MaturityTransition) -> RecordWritePlan:
        evidence = transition.record.get("maturity_transition")
        if (
            not isinstance(evidence, dict)
            or evidence.get("actor") != transition.actor
            or evidence.get("actor_kind") != "human"
            or evidence.get("capability") != LIFECYCLE_CAPABILITY
            or evidence.get("from") != transition.assessment.current
            or evidence.get("to") != transition.record.get("maturity")
            or evidence.get("project_revision") != transition.expectation.revision
        ):
            raise LifecycleError(
                "ECHEL-LIFECYCLE-TRANSITION-INVALID",
                "transition",
                "maturity evidence does not match the previewed transition",
            )
        return self.store.write(transition.record, transition.expectation)

    def preview_stale(
        self,
        transaction_id: str,
        finding_id: str,
        root_id: str,
        principal: Principal,
        reason: str,
        decided_at: str,
    ) -> BackwardRevision:
        self._authorize(principal, AUTHORITY_CAPABILITY)
        self._validate_reason_time(reason, decided_at)
        finding = self.store.load("finding", finding_id).record
        if finding.get("status") not in ACTIVE_FINDING_STATES:
            raise LifecycleError(
                "ECHEL-LIFECYCLE-FINDING-INACTIVE", "finding_id", "finding must be open or accepted"
            )
        if root_id not in self._finding_targets().get(finding_id, ()):
            raise LifecycleError(
                "ECHEL-LIFECYCLE-FINDING-UNRELATED",
                "root_id",
                "finding must explicitly affect the backward-revision root",
            )
        stale_ids = self._propagate(root_id)
        records = []
        for record_id in stale_ids:
            record_type = self._record_type(record_id)
            loaded = self.store.load(record_type, record_id)
            if loaded.record.get("status") != "accepted":
                continue
            updated = deepcopy(loaded.record)
            updated["status"] = "stale"
            updated["revision"] = loaded.record["revision"] + 1
            updated["updated_at"] = decided_at
            updated["staleness"] = {
                "actor": principal.id,
                "actor_kind": "human",
                "capability": AUTHORITY_CAPABILITY,
                "finding": finding_id,
                "root": root_id,
                "previous_status": "accepted",
                "reason": reason.strip(),
                "decided_at": decided_at,
                "record_revision": loaded.record["revision"],
            }
            records.append(updated)
        if not records or records[0]["id"] != root_id:
            raise LifecycleError(
                "ECHEL-LIFECYCLE-ROOT-NOT-ACCEPTED",
                "root_id",
                "backward revision starts from accepted protected knowledge",
            )
        self.transactions.preview(transaction_id, records)
        return BackwardRevision(
            transaction_id, tuple(records), finding_id, root_id, principal.id
        )

    def apply_stale(self, revision: BackwardRevision) -> None:
        for record in revision.records:
            staleness = record.get("staleness")
            if (
                record.get("status") != "stale"
                or not isinstance(staleness, dict)
                or staleness.get("actor") != revision.actor
                or staleness.get("actor_kind") != "human"
                or staleness.get("capability") != AUTHORITY_CAPABILITY
                or staleness.get("finding") != revision.finding_id
                or staleness.get("root") != revision.root_id
            ):
                raise LifecycleError(
                    "ECHEL-LIFECYCLE-STALE-INVALID",
                    "revision",
                    "staleness evidence does not match the previewed propagation",
                )
        self.transactions.execute(revision.transaction_id, list(revision.records))

    def _finding_targets(self) -> dict[str, frozenset[str]]:
        targets: dict[str, set[str]] = {}
        for loaded in self.store.scan("relationship"):
            relationship = loaded.record
            if relationship.get("predicate") == "affects" and str(
                relationship.get("source", "")
            ).startswith("finding:"):
                targets.setdefault(str(relationship["source"]), set()).add(
                    str(relationship["target"])
                )
        return {key: frozenset(value) for key, value in targets.items()}

    def _propagate(self, root_id: str) -> tuple[str, ...]:
        edges: dict[str, set[str]] = {}
        for loaded in self.store.scan("relationship"):
            relationship = loaded.record
            if relationship.get("predicate") in FORWARD_PROPAGATION_PREDICATES:
                edges.setdefault(str(relationship["source"]), set()).add(
                    str(relationship["target"])
                )
        ordered: list[str] = []
        queue = [root_id]
        seen: set[str] = set()
        while queue:
            current = queue.pop(0)
            if current in seen:
                continue
            seen.add(current)
            identifier = Identifier(current)
            if ENDPOINT_TYPES.get(identifier.namespace) not in PROTECTED_TYPES:
                continue
            ordered.append(current)
            queue.extend(sorted(edges.get(current, ())))
        return tuple(ordered)

    @staticmethod
    def _record_type(record_id: str) -> str:
        identifier = Identifier(record_id)
        record_type = ENDPOINT_TYPES.get(identifier.namespace)
        if record_type not in PROTECTED_TYPES:
            raise LifecycleError(
                "ECHEL-LIFECYCLE-KNOWLEDGE-TYPE-INVALID",
                "record_id",
                f"{record_id!r} is not protected lifecycle knowledge",
            )
        return record_type

    @staticmethod
    def _authorize(principal: Principal, capability: str) -> None:
        if principal.kind != "human" or capability not in principal.capabilities:
            raise LifecycleError(
                "ECHEL-LIFECYCLE-AUTHORITY-DENIED",
                "principal",
                f"an authorized human with {capability} capability is required",
            )

    @staticmethod
    def _validate_reason_time(reason: str, value: str) -> None:
        if not reason.strip():
            raise LifecycleError(
                "ECHEL-LIFECYCLE-RATIONALE-REQUIRED", "rationale", "must not be empty"
            )
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise LifecycleError(
                "ECHEL-LIFECYCLE-TIME-INVALID", "decided_at", "must be an RFC 3339 date-time"
            ) from exc
        if parsed.tzinfo is None:
            raise LifecycleError(
                "ECHEL-LIFECYCLE-TIME-INVALID", "decided_at", "must include a timezone"
            )
