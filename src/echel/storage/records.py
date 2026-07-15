from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Iterator
from uuid import uuid4

from echel.domain.value_objects import Identifier
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
class RecordExpectation:
    revision: int | None
    digest: str | None = None

    def __post_init__(self) -> None:
        if self.revision is not None and (
            isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 1
        ):
            raise RepositoryError(
                "ECHEL-PRECONDITION-INVALID", Path("revision"), "revision must be a positive integer"
            )
        if self.digest is not None and not re.fullmatch(r"sha256:[0-9a-f]{64}", self.digest):
            raise RepositoryError(
                "ECHEL-PRECONDITION-INVALID", Path("digest"), "digest must use sha256:<64 lowercase hex>"
            )

    @classmethod
    def absent(cls) -> RecordExpectation:
        return cls(None)

    @classmethod
    def at_revision(cls, revision: int, digest: str | None = None) -> RecordExpectation:
        return cls(revision, digest)

    def to_dict(self) -> dict[str, int | str | None]:
        return {"revision": self.revision, "digest": self.digest}


@dataclass
class RecordConflictError(RuntimeError):
    path: Path
    record_id: str
    expected: RecordExpectation
    actual_revision: int | None
    actual_digest: str | None

    code: str = "ECHEL-RECORD-CONFLICT"

    def __str__(self) -> str:
        return (
            f"{self.code} at {self.path}: {self.record_id} changed; "
            f"expected revision {self.expected.revision!r}, actual {self.actual_revision!r}; "
            "reload, merge, and retry with a fresh precondition"
        )

    def to_dict(self) -> dict[str, str | int | None | dict[str, int | str | None]]:
        return {
            "code": self.code,
            "path": str(self.path),
            "record_id": self.record_id,
            "expected": self.expected.to_dict(),
            "actual_revision": self.actual_revision,
            "actual_digest": self.actual_digest,
        }


@dataclass(frozen=True)
class RecordWritePlan:
    path: Path
    record_id: str
    digest: str
    replacing: bool
    changed: bool
    content: bytes
    expectation: RecordExpectation

    def to_dict(self) -> dict[str, str | bool | int | None]:
        return {
            "path": str(self.path),
            "record_id": self.record_id,
            "digest": self.digest,
            "replacing": self.replacing,
            "changed": self.changed,
            "expected_revision": self.expectation.revision,
            "expected_digest": self.expectation.digest,
        }


@dataclass(frozen=True)
class LoadedRecord:
    record: dict[str, Any]
    expectation: RecordExpectation
    path: Path


class CanonicalRecordStore:
    """Schema-validating, atomic writes for one canonical record at a time."""

    def __init__(self, repository: CanonicalRepository, schemas: SchemaRegistry | None = None):
        self.repository = repository
        self.schemas = schemas or SchemaRegistry()

    def observe(self, record: dict[str, Any]) -> RecordExpectation:
        """Capture the current state a later optimistic write must still match."""

        self.schemas.validate(record)
        path = self._record_path(record)
        if not path.exists():
            return RecordExpectation.absent()
        current, digest = self._read_current(path)
        return RecordExpectation.at_revision(current["revision"], digest)

    def load(self, record_type: str, record_id: str) -> LoadedRecord:
        """Load one canonical identity with the precondition needed to update it."""

        path = self._identity_path(record_type, record_id)
        if not path.is_file():
            raise RepositoryError("ECHEL-RECORD-NOT-FOUND", path, f"record {record_id!r} does not exist")
        record, digest = self._read_current(path)
        if record.get("record_type") != record_type or record.get("id") != record_id:
            raise RepositoryError(
                "ECHEL-RECORD-IDENTITY-MISMATCH",
                path,
                "stored record identity does not match its canonical path",
            )
        return LoadedRecord(
            record=record,
            expectation=RecordExpectation.at_revision(record["revision"], digest),
            path=path,
        )

    def preview_write(
        self, record: dict[str, Any], expectation: RecordExpectation | None = None
    ) -> RecordWritePlan:
        """Validate and explain a write without changing repository state."""

        if expectation is None:
            raise RepositoryError(
                "ECHEL-PRECONDITION-REQUIRED",
                self.repository.root,
                "state whether the record must be absent or provide the observed revision",
            )
        self.schemas.validate(record)
        path = self._record_path(record)
        content = (json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
        existing = path.read_bytes() if path.is_file() else None
        if existing == content:
            return self._plan(path, record, content, existing, expectation)
        if existing is None:
            if expectation.revision is not None:
                raise RecordConflictError(path, str(record["id"]), expectation, None, None)
            if record["revision"] != 1:
                raise RepositoryError(
                    "ECHEL-REVISION-SEQUENCE", path, "a new record must begin at revision 1"
                )
        else:
            current, current_digest = self._decode_current(path, existing)
            actual_revision = current["revision"]
            if expectation.revision != actual_revision or (
                expectation.digest is not None and expectation.digest != current_digest
            ):
                raise RecordConflictError(
                    path, str(record["id"]), expectation, actual_revision, current_digest
                )
            if record["revision"] != actual_revision + 1:
                raise RepositoryError(
                    "ECHEL-REVISION-SEQUENCE",
                    path,
                    f"next revision must be {actual_revision + 1}; received {record['revision']!r}",
                )
        return self._plan(path, record, content, existing, expectation)

    @staticmethod
    def _plan(
        path: Path,
        record: dict[str, Any],
        content: bytes,
        existing: bytes | None,
        expectation: RecordExpectation,
    ) -> RecordWritePlan:
        return RecordWritePlan(
            path=path,
            record_id=str(record["id"]),
            digest="sha256:" + hashlib.sha256(content).hexdigest(),
            replacing=existing is not None,
            changed=existing != content,
            content=content,
            expectation=expectation,
        )

    def write(
        self, record: dict[str, Any], expectation: RecordExpectation | None = None
    ) -> RecordWritePlan:
        """Atomically install a validated record, preserving old state on failure."""

        with self._write_lock():
            plan = self.preview_write(record, expectation)
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

    @contextmanager
    def _write_lock(self) -> Iterator[None]:
        lock = self.repository.root / "write.lock"
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise RepositoryError(
                "ECHEL-WRITE-LOCKED",
                lock,
                "another Echel write is active; retry after it completes or inspect a stale lock",
            ) from exc
        try:
            os.write(descriptor, f"pid={os.getpid()}\n".encode())
            os.fsync(descriptor)
            yield
        finally:
            os.close(descriptor)
            try:
                lock.unlink()
            except OSError:
                pass

    def _read_current(self, path: Path) -> tuple[dict[str, Any], str]:
        content = path.read_bytes()
        return self._decode_current(path, content)

    def _decode_current(self, path: Path, content: bytes) -> tuple[dict[str, Any], str]:
        try:
            current = json.loads(content)
            if not isinstance(current, dict):
                raise ValueError("expected a JSON object")
            self.schemas.validate(current)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            raise RepositoryError(
                "ECHEL-RECORD-CURRENT-INVALID", path, "repair or restore the current record: " + str(exc)
            ) from exc
        digest = "sha256:" + hashlib.sha256(content).hexdigest()
        return current, digest

    def _record_path(self, record: dict[str, Any]) -> Path:
        return self._identity_path(str(record["record_type"]), str(record["id"]))

    def _identity_path(self, record_type: str, record_id: str) -> Path:
        location = RECORD_LOCATIONS.get(record_type)
        if location is None:
            raise RepositoryError(
                "ECHEL-RECORD-TYPE-UNMAPPED",
                self.repository.root,
                f"no canonical location for {record_type!r}",
            )
        collection, namespace = location
        identifier = Identifier(record_id)
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
