from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, cast

from echel.domain.value_objects import Identifier
from echel.relationships import ENDPOINT_TYPES
from echel.schemas import SchemaValidationError
from echel.schemas.registry import SUPPORTED_SCHEMA_VERSIONS
from echel.storage import CanonicalRecordStore, RECORD_LOCATIONS, TransactionJournal


EXPORT_FORMAT = "echel-export/v1"
MAX_BUNDLE_BYTES = 100 * 1024 * 1024


@dataclass
class PortabilityError(RuntimeError):
    code: str
    path: str
    detail: str
    remedy: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.detail}; remedy: {self.remedy}"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "path": self.path,
            "detail": self.detail,
            "remedy": self.remedy,
        }


@dataclass(frozen=True)
class ExportBundle:
    content: bytes
    fingerprint: str
    record_count: int
    format: str = EXPORT_FORMAT

    def to_dict(self) -> dict[str, str | int]:
        return {
            "format": self.format,
            "fingerprint": self.fingerprint,
            "record_count": self.record_count,
        }


@dataclass(frozen=True)
class ImportEntry:
    path: str
    record: dict[str, Any]


@dataclass(frozen=True)
class ImportPlan:
    transaction_id: str
    fingerprint: str
    entries: tuple[ImportEntry, ...]

    def to_dict(self) -> dict[str, str | int | list[str]]:
        return {
            "transaction_id": self.transaction_id,
            "fingerprint": self.fingerprint,
            "record_count": len(self.entries),
            "records": [str(entry.record["id"]) for entry in self.entries],
            "mutation": "preview",
        }


@dataclass(frozen=True)
class ImportResult:
    transaction_id: str
    fingerprint: str
    record_count: int
    outcome: str


class PortableRepositoryService:
    """Deterministic export and all-or-nothing import of canonical records."""

    def __init__(self, store: CanonicalRecordStore):
        self.store = store

    def export(self) -> ExportBundle:
        entries: list[dict[str, Any]] = []
        try:
            for record_type in RECORD_LOCATIONS:
                for loaded in self.store.scan(record_type):
                    entries.append(
                        {
                            "path": loaded.path.relative_to(self.store.repository.root).as_posix(),
                            "record": loaded.record,
                        }
                    )
        except RuntimeError as exc:
            raise PortabilityError(
                "ECHEL-EXPORT-SOURCE-INVALID",
                str(self.store.repository.root),
                str(exc),
                "run integrity diagnostics and repair canonical records before export",
            ) from exc
        entries.sort(key=lambda entry: entry["path"])
        fingerprint = self._fingerprint(entries)
        payload = {"format": EXPORT_FORMAT, "fingerprint": fingerprint, "records": entries}
        content = self._json_bytes(payload)
        return ExportBundle(content, fingerprint, len(entries))

    def preview_import(self, content: bytes, transaction_id: str) -> ImportPlan:
        identifier = self._transaction_identifier(transaction_id)
        if not isinstance(content, bytes) or len(content) > MAX_BUNDLE_BYTES:
            raise PortabilityError(
                "ECHEL-IMPORT-SIZE",
                "/",
                f"bundle must be bytes no larger than {MAX_BUNDLE_BYTES}",
                "export a smaller canonical repository bundle",
            )
        if self._canonical_paths():
            raise PortabilityError(
                "ECHEL-IMPORT-TARGET-NOT-EMPTY",
                str(self.store.repository.root),
                "portable import does not merge with existing canonical records",
                "initialize an empty Echel repository or use explicit record workflows",
            )
        payload = self._decode(content)
        if payload.get("format") != EXPORT_FORMAT:
            raise PortabilityError(
                "ECHEL-IMPORT-FORMAT-UNSUPPORTED",
                "/format",
                f"supported format is {EXPORT_FORMAT!r}",
                "use a compatible Echel release to re-export the bundle",
            )
        raw_entries = payload.get("records")
        if not isinstance(raw_entries, list):
            raise PortabilityError(
                "ECHEL-IMPORT-INVALID",
                "/records",
                "records must be an array",
                "re-export the bundle from its source repository",
            )
        normalized: list[dict[str, Any]] = []
        record_ids = set()
        for index, entry in enumerate(raw_entries):
            path = f"/records/{index}"
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                raise self._invalid(path, "entry requires a path and record")
            record = entry.get("record")
            if not isinstance(record, dict):
                raise self._invalid(path + "/record", "record must be an object")
            version = record.get("schema_version")
            if version not in SUPPORTED_SCHEMA_VERSIONS:
                raise PortabilityError(
                    "ECHEL-IMPORT-VERSION-UNSUPPORTED",
                    path + "/record/schema_version",
                    f"supported versions are {sorted(SUPPORTED_SCHEMA_VERSIONS)}; received {version!r}",
                    "open with a compatible Echel release or migrate before export",
                )
            try:
                self.store.schemas.validate(record)
                expected = self._relative_path(record)
            except (SchemaValidationError, ValueError, KeyError) as exc:
                raise self._invalid(path + "/record", str(exc)) from exc
            if entry["path"] != expected:
                raise self._invalid(path + "/path", f"canonical path must be {expected!r}")
            record_id = str(record["id"])
            if record_id in record_ids:
                raise self._invalid(path + "/record/id", f"duplicate id {record_id!r}")
            record_ids.add(record_id)
            normalized.append({"path": expected, "record": record})
        if normalized != sorted(normalized, key=lambda entry: entry["path"]):
            raise self._invalid("/records", "records must use deterministic canonical path order")
        self._validate_relationships(normalized, record_ids)
        fingerprint = self._fingerprint(normalized)
        if payload.get("fingerprint") != fingerprint:
            raise PortabilityError(
                "ECHEL-IMPORT-DIGEST-MISMATCH",
                "/fingerprint",
                "bundle content does not match its fingerprint",
                "discard the modified copy and re-export from the source repository",
            )
        entries = tuple(
            ImportEntry(str(entry["path"]), cast(dict[str, Any], entry["record"]))
            for entry in normalized
        )
        return ImportPlan(str(identifier), fingerprint, entries)

    def apply_import(self, plan: ImportPlan) -> ImportResult:
        self._transaction_identifier(plan.transaction_id)
        if self._canonical_paths():
            raise PortabilityError(
                "ECHEL-IMPORT-TARGET-NOT-EMPTY",
                str(self.store.repository.root),
                "target changed after preview",
                "preview again against an empty repository",
            )
        normalized = [{"path": entry.path, "record": entry.record} for entry in plan.entries]
        if self._fingerprint(normalized) != plan.fingerprint:
            raise PortabilityError(
                "ECHEL-IMPORT-PLAN-INVALID",
                "/fingerprint",
                "previewed import plan was modified",
                "discard it and create a new preview",
            )
        if not plan.entries:
            return ImportResult(plan.transaction_id, plan.fingerprint, 0, "empty")
        TransactionJournal(self.store).execute(
            plan.transaction_id, [entry.record for entry in plan.entries]
        )
        return ImportResult(plan.transaction_id, plan.fingerprint, len(plan.entries), "imported")

    def _canonical_paths(self) -> tuple[Path, ...]:
        paths = list(self.store.repository.records.glob("*/*.json"))
        project = self.store.repository.root / "project.json"
        if project.is_file():
            paths.append(project)
        return tuple(sorted(paths))

    def _validate_relationships(
        self, entries: list[dict[str, Any]], record_ids: set[str]
    ) -> None:
        for entry in entries:
            record = entry["record"]
            if record["record_type"] != "relationship":
                continue
            for field in ("source", "target"):
                endpoint = record[field]
                namespace = Identifier(endpoint).namespace
                if namespace not in ENDPOINT_TYPES or endpoint not in record_ids:
                    raise PortabilityError(
                        "ECHEL-IMPORT-ORPHAN-LINK",
                        f"/{record['id']}/{field}",
                        f"canonical endpoint {endpoint!r} is absent from the bundle",
                        "include the endpoint record or remove the relationship before export",
                    )

    @staticmethod
    def _relative_path(record: dict[str, Any]) -> str:
        record_type = str(record["record_type"])
        collection, namespace = RECORD_LOCATIONS[record_type]
        identifier = Identifier(str(record["id"]))
        if identifier.namespace != namespace:
            raise ValueError(f"{record_type} id must use namespace {namespace!r}")
        return "project.json" if collection is None else f"records/{collection}/{identifier.local}.json"

    @staticmethod
    def _fingerprint(entries: list[dict[str, Any]]) -> str:
        content = json.dumps(entries, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        return "sha256:" + hashlib.sha256(content).hexdigest()

    @staticmethod
    def _json_bytes(payload: dict[str, Any]) -> bytes:
        return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()

    @staticmethod
    def _decode(content: bytes) -> dict[str, Any]:
        try:
            payload = json.loads(content)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PortabilityError(
                "ECHEL-IMPORT-CORRUPT",
                "/",
                str(exc),
                "restore or re-export the bundle from its source repository",
            ) from exc
        if not isinstance(payload, dict):
            raise PortableRepositoryService._invalid("/", "bundle must be an object")
        return payload

    @staticmethod
    def _transaction_identifier(transaction_id: str) -> Identifier:
        try:
            identifier = Identifier(transaction_id)
        except (TypeError, ValueError) as exc:
            raise PortabilityError(
                "ECHEL-IMPORT-TRANSACTION-ID",
                "/transaction_id",
                str(exc),
                "use a unique transaction:local identifier",
            ) from exc
        if identifier.namespace != "transaction":
            raise PortabilityError(
                "ECHEL-IMPORT-TRANSACTION-ID",
                "/transaction_id",
                "import transaction must use the transaction namespace",
                "use a unique transaction:local identifier",
            )
        return identifier

    @staticmethod
    def _invalid(path: str, detail: str) -> PortabilityError:
        return PortabilityError(
            "ECHEL-IMPORT-INVALID",
            path,
            detail,
            "discard the modified copy and re-export from a valid source repository",
        )
