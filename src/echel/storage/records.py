from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from echel.domain import Identifier
from echel.schemas import SchemaRegistry
from echel.storage.layout import CanonicalRepository, RepositoryError


RECORD_LOCATIONS: dict[str, tuple[str | None, str]] = {
    "project": (None, "project"),
    "claim": ("claims", "claim"),
    "decision": ("decisions", "decision"),
    "artifact": ("artifacts", "artifact"),
    "relationship": ("relationships", "relationship"),
    "finding": ("findings", "finding"),
    "work_item": ("work", "work"),
    "task_specification": ("tasks", "task"),
    "run": ("runs", "run"),
    "evidence": ("evidence", "evidence"),
    "release": ("releases", "release"),
    "learning": ("learnings", "learning"),
}


@dataclass(frozen=True)
class RecordWritePlan:
    path: Path
    record_id: str
    digest: str
    replacing: bool
    changed: bool
    content: bytes

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "path": str(self.path),
            "record_id": self.record_id,
            "digest": self.digest,
            "replacing": self.replacing,
            "changed": self.changed,
        }


class CanonicalRecordStore:
    """Schema-validating, atomic writes for one canonical record at a time."""

    def __init__(self, repository: CanonicalRepository, schemas: SchemaRegistry | None = None):
        self.repository = repository
        self.schemas = schemas or SchemaRegistry()

    def preview_write(self, record: dict[str, Any]) -> RecordWritePlan:
        """Validate and explain a write without changing repository state."""

        self.schemas.validate(record)
        path = self._record_path(record)
        content = (json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
        existing = path.read_bytes() if path.is_file() else None
        return RecordWritePlan(
            path=path,
            record_id=str(record["id"]),
            digest="sha256:" + hashlib.sha256(content).hexdigest(),
            replacing=existing is not None,
            changed=existing != content,
            content=content,
        )

    def write(self, record: dict[str, Any]) -> RecordWritePlan:
        """Atomically install a validated record, preserving old state on failure."""

        plan = self.preview_write(record)
        if not plan.changed:
            return plan

        temporary = plan.path.parent / f".{plan.path.name}.{uuid4().hex}.tmp"
        try:
            with temporary.open("xb") as stream:
                stream.write(plan.content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, plan.path)
        except OSError as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise RepositoryError("ECHEL-RECORD-WRITE", plan.path, str(exc)) from exc
        return plan

    def _record_path(self, record: dict[str, Any]) -> Path:
        record_type = str(record["record_type"])
        location = RECORD_LOCATIONS.get(record_type)
        if location is None:
            raise RepositoryError(
                "ECHEL-RECORD-TYPE-UNMAPPED",
                self.repository.root,
                f"no canonical location for {record_type!r}",
            )
        collection, namespace = location
        identifier = Identifier(str(record["id"]))
        if identifier.namespace != namespace:
            raise RepositoryError(
                "ECHEL-ID-NAMESPACE-MISMATCH",
                self.repository.root,
                f"{record_type} identifiers must use the {namespace!r} namespace",
            )
        if collection is None:
            path = self.repository.root / "project.json"
        else:
            path = self.repository.collection(collection) / f"{identifier.local}.json"
        if not path.parent.resolve().is_relative_to(self.repository.workspace):
            raise RepositoryError(
                "ECHEL-REPOSITORY-ESCAPE", path, "record location resolves outside its repository"
            )
        return path
