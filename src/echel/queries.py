from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any

from echel.domain.value_objects import Identifier
from echel.relationships import ENDPOINT_TYPES
from echel.storage import CanonicalRecordStore, DisposableIndex, IndexError, SearchHit


FORWARD_IMPACT_PREDICATES = frozenset({"informs", "supports", "contradicts", "affects"})
REVERSE_IMPACT_PREDICATES = frozenset({"depends_on", "implements", "verifies"})
QUERY_RECORD_TYPES = {**ENDPOINT_TYPES, "relationship": "relationship"}


@dataclass
class QueryError(RuntimeError):
    code: str
    field: str
    detail: str

    def __str__(self) -> str:
        return f"{self.code} at /{self.field}: {self.detail}"

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "field": self.field, "detail": self.detail}


@dataclass(frozen=True)
class ProvenancedRecord:
    record: dict[str, Any]
    path: str

    @property
    def record_id(self) -> str:
        return str(self.record["id"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "record_type": self.record["record_type"],
            "revision": self.record["revision"],
            "path": self.path,
            "provenance": self.record["provenance"],
            "record": self.record,
        }


@dataclass(frozen=True)
class LinkExplanation:
    relationship: ProvenancedRecord
    related: ProvenancedRecord
    direction: str

    def to_dict(self) -> dict[str, Any]:
        relationship = self.relationship.record
        return {
            "relationship_id": relationship["id"],
            "source": relationship["source"],
            "predicate": relationship["predicate"],
            "target": relationship["target"],
            "reason": relationship["reason"],
            "direction": self.direction,
            "provenance": relationship["provenance"],
            "related": self.related.to_dict(),
        }


@dataclass(frozen=True)
class ImpactStep:
    source: str
    target: str
    predicate: str
    traversal: str
    relationship_id: str
    reason: str
    provenance: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "predicate": self.predicate,
            "traversal": self.traversal,
            "relationship_id": self.relationship_id,
            "reason": self.reason,
            "provenance": self.provenance,
        }


@dataclass(frozen=True)
class ImpactPath:
    target: ProvenancedRecord
    steps: tuple[ImpactStep, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target.to_dict(),
            "depth": len(self.steps),
            "steps": [step.to_dict() for step in self.steps],
        }


@dataclass(frozen=True)
class ImpactResult:
    origin: ProvenancedRecord
    max_depth: int
    paths: tuple[ImpactPath, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "origin": self.origin.to_dict(),
            "max_depth": self.max_depth,
            "policy": "explicit-impact/v1",
            "paths": [path.to_dict() for path in self.paths],
        }


class QueryService:
    """Read-only canonical queries accelerated, but never authorized, by the index."""

    def __init__(self, store: CanonicalRecordStore, index: DisposableIndex):
        if index.store.repository != store.repository:
            raise QueryError(
                "ECHEL-QUERY-REPOSITORY-MISMATCH",
                "index",
                "record store and disposable index must belong to the same repository",
            )
        self.store = store
        self.index = index

    def search(
        self, query: str, *, record_type: str | None = None, limit: int = 20
    ) -> tuple[ProvenancedRecord, ...]:
        hits = self.index.search(query, record_type=record_type, limit=limit)
        records = tuple(self._from_search_hit(hit) for hit in hits)
        self.index.assert_current()
        return records

    def reverse_links(
        self, record_id: str, *, predicate: str | None = None
    ) -> tuple[LinkExplanation, ...]:
        self._load(record_id)
        results = []
        for hit in self.index.related(record_id, direction="in", predicate=predicate):
            relationship = self._load(hit.relationship_id)
            self._assert_relationship_hit(relationship, hit.to_dict())
            results.append(
                LinkExplanation(
                    relationship=relationship,
                    related=self._load(hit.source),
                    direction="incoming",
                )
            )
        self.index.assert_current()
        return tuple(results)

    def impact(self, record_id: str, *, max_depth: int = 3) -> ImpactResult:
        if isinstance(max_depth, bool) or not isinstance(max_depth, int) or not 1 <= max_depth <= 10:
            raise QueryError(
                "ECHEL-QUERY-INVALID",
                "max_depth",
                "max_depth must be an integer from 1 through 10",
            )
        origin = self._load(record_id)
        queue: deque[tuple[str, tuple[ImpactStep, ...]]] = deque([(record_id, tuple())])
        visited = {record_id}
        paths = []
        while queue:
            current, previous_steps = queue.popleft()
            if len(previous_steps) >= max_depth:
                continue
            for hit in self.index.related(current):
                relationship = self._load(hit.relationship_id)
                self._assert_relationship_hit(relationship, hit.to_dict())
                step = self._impact_step(current, relationship.record)
                if step is None or step.target in visited:
                    continue
                target = self._load(step.target)
                steps = (*previous_steps, step)
                visited.add(step.target)
                paths.append(ImpactPath(target, steps))
                queue.append((step.target, steps))
        self.index.assert_current()
        return ImpactResult(origin, max_depth, tuple(paths))

    def _from_search_hit(self, hit: SearchHit) -> ProvenancedRecord:
        result = self._load(hit.record_id)
        if (
            result.record["record_type"] != hit.record_type
            or result.record["revision"] != hit.revision
            or result.path != hit.path
        ):
            raise IndexError(
                "ECHEL-INDEX-STALE",
                self.index.path,
                "indexed identity changed; rebuild the index",
            )
        return result

    def _load(self, record_id: str) -> ProvenancedRecord:
        try:
            identifier = Identifier(record_id)
        except (TypeError, ValueError) as exc:
            raise QueryError("ECHEL-QUERY-ID-INVALID", "record_id", str(exc)) from exc
        record_type = QUERY_RECORD_TYPES.get(identifier.namespace)
        if record_type is None:
            raise QueryError(
                "ECHEL-QUERY-ID-INVALID",
                "record_id",
                f"unsupported record namespace {identifier.namespace!r}",
            )
        try:
            loaded = self.store.load(record_type, record_id)
        except RuntimeError as exc:
            raise QueryError(
                "ECHEL-QUERY-RECORD-NOT-FOUND",
                "record_id",
                f"canonical record {record_id!r} does not exist",
            ) from exc
        path = loaded.path.relative_to(self.store.repository.root).as_posix()
        return ProvenancedRecord(loaded.record, path)

    @staticmethod
    def _assert_relationship_hit(relationship: ProvenancedRecord, hit: dict[str, str]) -> None:
        record = relationship.record
        if any(record[field] != hit[field] for field in ("source", "predicate", "target", "reason")):
            raise QueryError(
                "ECHEL-QUERY-STALE",
                "relationship",
                "indexed relationship changed; rebuild and retry",
            )

    @staticmethod
    def _impact_step(current: str, relationship: dict[str, Any]) -> ImpactStep | None:
        predicate = relationship["predicate"]
        if predicate in FORWARD_IMPACT_PREDICATES and relationship["source"] == current:
            target = relationship["target"]
            traversal = "source_to_target"
        elif predicate in REVERSE_IMPACT_PREDICATES and relationship["target"] == current:
            target = relationship["source"]
            traversal = "target_to_source"
        else:
            return None
        return ImpactStep(
            source=current,
            target=target,
            predicate=predicate,
            traversal=traversal,
            relationship_id=relationship["id"],
            reason=relationship["reason"],
            provenance=relationship["provenance"],
        )
