from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from echel.domain.value_objects import Identifier
from echel.storage.records import CanonicalRecordStore, RecordExpectation, RecordWritePlan


ENDPOINT_TYPES = {
    "project": "project",
    "claim": "claim",
    "decision": "decision",
    "artifact": "artifact",
    "finding": "finding",
    "work": "work_item",
    "task": "task_specification",
    "run": "run",
    "evidence": "evidence",
    "release": "release",
    "learning": "learning",
}


@dataclass
class RelationshipError(RuntimeError):
    code: str
    field: str
    detail: str

    def __str__(self) -> str:
        return f"{self.code} at /{self.field}: {self.detail}"


@dataclass(frozen=True)
class RelationshipRule:
    predicate: str
    sources: frozenset[str]
    targets: frozenset[str]


@dataclass(frozen=True)
class RelationshipPolicy:
    id: str
    rules: tuple[RelationshipRule, ...]

    def allows(self, predicate: str, source_type: str, target_type: str) -> bool:
        return any(
            rule.predicate == predicate
            and source_type in rule.sources
            and target_type in rule.targets
            for rule in self.rules
        )


KNOWLEDGE_TYPES = frozenset({"claim", "decision", "learning"})
DELIVERY_TYPES = frozenset({"work_item", "task_specification", "release"})
EVIDENCE_TYPES = frozenset({"artifact", "evidence", "run"})

CORE_RELATIONSHIP_POLICY = RelationshipPolicy(
    id="core/v1",
    rules=(
        RelationshipRule(
            "informs",
            KNOWLEDGE_TYPES | frozenset({"finding"}),
            KNOWLEDGE_TYPES | DELIVERY_TYPES | frozenset({"project"}),
        ),
        RelationshipRule(
            "supports",
            KNOWLEDGE_TYPES | EVIDENCE_TYPES,
            KNOWLEDGE_TYPES | DELIVERY_TYPES | frozenset({"finding"}),
        ),
        RelationshipRule(
            "contradicts",
            KNOWLEDGE_TYPES | frozenset({"finding", "evidence"}),
            KNOWLEDGE_TYPES,
        ),
        RelationshipRule(
            "depends_on",
            frozenset({"work_item", "task_specification"}),
            frozenset({"work_item", "task_specification"}),
        ),
        RelationshipRule(
            "implements",
            frozenset({"work_item", "task_specification", "artifact"}),
            KNOWLEDGE_TYPES,
        ),
        RelationshipRule(
            "verifies", frozenset({"evidence", "run"}), KNOWLEDGE_TYPES | DELIVERY_TYPES
        ),
        RelationshipRule(
            "affects",
            KNOWLEDGE_TYPES | frozenset({"finding", "work_item"}),
            KNOWLEDGE_TYPES | DELIVERY_TYPES,
        ),
    ),
)


@dataclass(frozen=True)
class RelationshipTransition:
    record: dict[str, Any]
    expectation: RecordExpectation
    source_type: str
    target_type: str
    path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record["id"],
            "source": self.record["source"],
            "source_type": self.source_type,
            "predicate": self.record["predicate"],
            "target": self.record["target"],
            "target_type": self.target_type,
            "reason": self.record["reason"],
            "policy": self.record["policy"],
            "path": self.path,
            "mutation": "preview",
        }


class RelationshipService:
    """Create sparse, justified links between existing canonical records."""

    def __init__(
        self,
        store: CanonicalRecordStore,
        policy: RelationshipPolicy = CORE_RELATIONSHIP_POLICY,
    ):
        self.store = store
        self.policy = policy

    def preview(
        self,
        relationship_id: str,
        source: str,
        predicate: str,
        target: str,
        reason: str,
        provenance: dict[str, str],
        created_at: str,
    ) -> RelationshipTransition:
        source_type, target_type = self._validate_link(source, predicate, target, reason)
        record: dict[str, Any] = {
            "schema_version": 1,
            "record_type": "relationship",
            "id": relationship_id,
            "revision": 1,
            "created_at": created_at,
            "updated_at": created_at,
            "provenance": provenance,
            "source": source,
            "predicate": predicate,
            "target": target,
            "reason": reason.strip(),
            "policy": self.policy.id,
        }
        self._validate_timestamp(created_at)
        plan = self.store.preview_write(record, RecordExpectation.absent())
        return RelationshipTransition(
            record=record,
            expectation=RecordExpectation.absent(),
            source_type=source_type,
            target_type=target_type,
            path=str(plan.path),
        )

    def apply(self, transition: RelationshipTransition) -> RecordWritePlan:
        record = transition.record
        source_type, target_type = self._validate_link(
            str(record.get("source", "")),
            str(record.get("predicate", "")),
            str(record.get("target", "")),
            str(record.get("reason", "")),
        )
        if (
            record.get("record_type") != "relationship"
            or record.get("policy") != self.policy.id
            or transition.expectation.revision is not None
            or transition.source_type != source_type
            or transition.target_type != target_type
        ):
            raise RelationshipError(
                "ECHEL-RELATIONSHIP-TRANSITION-INVALID",
                "transition",
                "preview evidence does not match the relationship or active policy",
            )
        return self.store.write(record, transition.expectation)

    def _validate_link(
        self, source: str, predicate: str, target: str, reason: str
    ) -> tuple[str, str]:
        if not reason.strip():
            raise RelationshipError(
                "ECHEL-RELATIONSHIP-REASON-REQUIRED",
                "reason",
                "state why this relationship is useful",
            )
        source_type = self._endpoint_type(source, "source")
        target_type = self._endpoint_type(target, "target")
        if source == target:
            raise RelationshipError(
                "ECHEL-RELATIONSHIP-SELF-LINK",
                "target",
                "source and target must be different canonical records",
            )
        if not self.policy.allows(predicate, source_type, target_type):
            raise RelationshipError(
                "ECHEL-RELATIONSHIP-POLICY-DENIED",
                "predicate",
                f"{self.policy.id} does not allow {source_type} -[{predicate}]-> {target_type}",
            )
        return source_type, target_type

    def _endpoint_type(self, value: str, field: str) -> str:
        try:
            identifier = Identifier(value)
        except (TypeError, ValueError) as exc:
            raise RelationshipError(
                "ECHEL-RELATIONSHIP-ENDPOINT-INVALID", field, str(exc)
            ) from exc
        record_type = ENDPOINT_TYPES.get(identifier.namespace)
        if record_type is None:
            raise RelationshipError(
                "ECHEL-RELATIONSHIP-ENDPOINT-INVALID",
                field,
                f"unsupported endpoint namespace {identifier.namespace!r}",
            )
        try:
            self.store.load(record_type, value)
        except RuntimeError as exc:
            raise RelationshipError(
                "ECHEL-RELATIONSHIP-ENDPOINT-NOT-FOUND",
                field,
                f"canonical endpoint {value!r} does not exist",
            ) from exc
        return record_type

    @staticmethod
    def _validate_timestamp(value: str) -> None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise RelationshipError(
                "ECHEL-RELATIONSHIP-TIME-INVALID", "created_at", "must be an RFC 3339 date-time"
            ) from exc
        if parsed.tzinfo is None:
            raise RelationshipError(
                "ECHEL-RELATIONSHIP-TIME-INVALID", "created_at", "must include a timezone"
            )
