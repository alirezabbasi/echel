from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from echel.domain.value_objects import Identifier
from echel.storage.records import CanonicalRecordStore, RecordExpectation, RecordWritePlan


PROTECTED_KNOWLEDGE_TYPES = frozenset({"claim", "decision", "learning"})
AUTHORITY_CAPABILITY = "knowledge:decide"


@dataclass
class AuthorityError(RuntimeError):
    code: str
    field: str
    detail: str

    def __str__(self) -> str:
        return f"{self.code} at /{self.field}: {self.detail}"


@dataclass(frozen=True)
class Principal:
    id: str
    kind: str
    capabilities: frozenset[str]

    def __post_init__(self) -> None:
        Identifier(self.id)
        if self.kind not in {"human", "agent", "system"}:
            raise AuthorityError("ECHEL-PRINCIPAL-INVALID", "kind", "must be human, agent, or system")


@dataclass(frozen=True)
class AuthorityTransition:
    record: dict[str, Any]
    expectation: RecordExpectation
    action: str
    actor: str
    path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record["id"],
            "record_type": self.record["record_type"],
            "from_status": "proposed",
            "to_status": self.action,
            "next_revision": self.record["revision"],
            "actor": self.actor,
            "path": self.path,
            "mutation": "preview",
        }


class KnowledgeAuthorityService:
    """Preview and record human decisions without granting authority to runtimes."""

    def __init__(self, store: CanonicalRecordStore):
        self.store = store

    def preview(
        self,
        record_type: str,
        record_id: str,
        action: str,
        principal: Principal,
        rationale: str,
        decided_at: str,
    ) -> AuthorityTransition:
        if record_type not in PROTECTED_KNOWLEDGE_TYPES:
            raise AuthorityError(
                "ECHEL-AUTHORITY-KIND-UNSUPPORTED",
                "record_type",
                f"authority transitions are defined for {sorted(PROTECTED_KNOWLEDGE_TYPES)}",
            )
        self._authorize(principal)
        if action not in {"accepted", "rejected"}:
            raise AuthorityError(
                "ECHEL-AUTHORITY-ACTION-INVALID", "action", "must be accepted or rejected"
            )
        if not rationale.strip():
            raise AuthorityError(
                "ECHEL-AUTHORITY-RATIONALE-REQUIRED",
                "rationale",
                "an attributable decision requires a non-empty rationale",
            )
        self._validate_timestamp(decided_at)
        loaded = self.store.load(record_type, record_id)
        if loaded.record.get("status") != "proposed":
            raise AuthorityError(
                "ECHEL-AUTHORITY-STATE-CONFLICT",
                "status",
                f"only proposed records can be decided; current status is {loaded.record.get('status')!r}",
            )
        updated = deepcopy(loaded.record)
        updated["status"] = action
        updated["revision"] = loaded.record["revision"] + 1
        updated["updated_at"] = decided_at
        updated["authority"] = {
            "action": action,
            "actor": principal.id,
            "actor_kind": "human",
            "capability": AUTHORITY_CAPABILITY,
            "rationale": rationale.strip(),
            "decided_at": decided_at,
            "proposal_revision": loaded.record["revision"],
        }
        plan = self.store.preview_write(updated, loaded.expectation)
        return AuthorityTransition(
            record=updated,
            expectation=loaded.expectation,
            action=action,
            actor=principal.id,
            path=str(plan.path),
        )

    def apply(self, transition: AuthorityTransition) -> RecordWritePlan:
        self._validate_transition(transition)
        return self.store.write(transition.record, transition.expectation)

    @staticmethod
    def _authorize(principal: Principal) -> None:
        if principal.kind != "human" or AUTHORITY_CAPABILITY not in principal.capabilities:
            raise AuthorityError(
                "ECHEL-AUTHORITY-DENIED",
                "principal",
                "an authorized human with knowledge:decide capability must make this decision",
            )

    @staticmethod
    def _validate_timestamp(value: str) -> None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise AuthorityError(
                "ECHEL-AUTHORITY-TIME-INVALID", "decided_at", "must be an RFC 3339 date-time"
            ) from exc
        if parsed.tzinfo is None:
            raise AuthorityError(
                "ECHEL-AUTHORITY-TIME-INVALID", "decided_at", "must include a timezone"
            )

    @staticmethod
    def _validate_transition(transition: AuthorityTransition) -> None:
        authority = transition.record.get("authority")
        if (
            transition.record.get("record_type") not in PROTECTED_KNOWLEDGE_TYPES
            or transition.record.get("status") != transition.action
            or transition.action not in {"accepted", "rejected"}
            or not isinstance(authority, dict)
            or authority.get("actor") != transition.actor
            or authority.get("actor_kind") != "human"
            or authority.get("capability") != AUTHORITY_CAPABILITY
            or authority.get("action") != transition.action
            or authority.get("proposal_revision") != transition.expectation.revision
        ):
            raise AuthorityError(
                "ECHEL-AUTHORITY-TRANSITION-INVALID",
                "transition",
                "authority evidence does not match the proposed state transition",
            )
