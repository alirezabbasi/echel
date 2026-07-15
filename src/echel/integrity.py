from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from echel.domain.value_objects import Identifier
from echel.relationships import ENDPOINT_TYPES
from echel.schemas import SchemaValidationError
from echel.schemas.registry import SUPPORTED_SCHEMA_VERSIONS
from echel.storage import CanonicalRecordStore, DisposableIndex, IndexError, RECORD_LOCATIONS


@dataclass(frozen=True)
class IntegrityIssue:
    code: str
    severity: str
    path: str
    detail: str
    remedy: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "path": self.path,
            "detail": self.detail,
            "remedy": self.remedy,
        }


@dataclass(frozen=True)
class IntegrityReport:
    healthy: bool
    records_checked: int
    issues: tuple[IntegrityIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "healthy": self.healthy,
            "records_checked": self.records_checked,
            "issues": [issue.to_dict() for issue in self.issues],
        }


class IntegrityService:
    """Inspect canonical truth and disposable index without mutating either."""

    def __init__(self, store: CanonicalRecordStore, index: DisposableIndex | None = None):
        self.store = store
        self.index = index or DisposableIndex(store)

    def inspect(self) -> IntegrityReport:
        issues = []
        valid_records: list[tuple[Path, dict[str, Any]]] = []
        identities: dict[str, Path] = {}
        paths = list(sorted(self.store.repository.records.glob("*/*.json")))
        project = self.store.repository.root / "project.json"
        if project.is_file():
            paths.insert(0, project)
        for path in paths:
            relative = path.relative_to(self.store.repository.root).as_posix()
            try:
                content = path.read_bytes()
                record = json.loads(content)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                issues.append(
                    self._issue(
                        "ECHEL-INTEGRITY-CORRUPT",
                        "error",
                        relative,
                        str(exc),
                        "restore this record from Git or a verified migration backup",
                    )
                )
                continue
            if not isinstance(record, dict):
                issues.append(
                    self._issue(
                        "ECHEL-INTEGRITY-CORRUPT",
                        "error",
                        relative,
                        "canonical record is not a JSON object",
                        "restore this record from Git or a verified export",
                    )
                )
                continue
            version = record.get("schema_version")
            if version not in SUPPORTED_SCHEMA_VERSIONS:
                issues.append(
                    self._issue(
                        "ECHEL-INTEGRITY-VERSION-UNSUPPORTED",
                        "error",
                        relative,
                        f"supported versions are {sorted(SUPPORTED_SCHEMA_VERSIONS)}; received {version!r}",
                        "open with a compatible Echel release or run a reviewed schema migration",
                    )
                )
                continue
            try:
                self.store.schemas.validate(record)
                expected = self._relative_path(record)
            except (SchemaValidationError, ValueError, KeyError) as exc:
                issues.append(
                    self._issue(
                        "ECHEL-INTEGRITY-SCHEMA",
                        "error",
                        relative,
                        str(exc),
                        "repair the record from authoritative evidence, then validate it before writing",
                    )
                )
                continue
            if expected != relative:
                issues.append(
                    self._issue(
                        "ECHEL-INTEGRITY-IDENTITY",
                        "error",
                        relative,
                        f"record identity belongs at {expected}",
                        "move it to its canonical path after checking for identity conflicts",
                    )
                )
                continue
            record_id = str(record["id"])
            if record_id in identities:
                issues.append(
                    self._issue(
                        "ECHEL-INTEGRITY-DUPLICATE-ID",
                        "error",
                        relative,
                        f"identity also exists at {identities[record_id]}",
                        "retain the authoritative revision and reconcile the duplicate through review",
                    )
                )
                continue
            identities[record_id] = path
            valid_records.append((path, record))
        for path, record in valid_records:
            if record["record_type"] != "relationship":
                continue
            for field in ("source", "target"):
                endpoint = record[field]
                namespace = Identifier(endpoint).namespace
                if namespace not in ENDPOINT_TYPES or endpoint not in identities:
                    issues.append(
                        self._issue(
                            "ECHEL-INTEGRITY-ORPHAN-LINK",
                            "error",
                            path.relative_to(self.store.repository.root).as_posix(),
                            f"{field} endpoint {endpoint!r} does not exist",
                            "restore the endpoint or remove the relationship through a reviewed canonical change",
                        )
                    )
        self._inspect_index(issues, canonical_valid=len(valid_records) == len(paths))
        ordered = tuple(sorted(issues, key=lambda issue: (issue.path, issue.code, issue.detail)))
        healthy = not any(issue.severity == "error" for issue in ordered)
        return IntegrityReport(healthy, len(paths), ordered)

    def _inspect_index(self, issues: list[IntegrityIssue], canonical_valid: bool) -> None:
        if not self.index.path.is_file():
            issues.append(
                self._issue(
                    "ECHEL-INTEGRITY-INDEX-MISSING",
                    "warning",
                    "cache/index.sqlite3",
                    "disposable query index has not been built",
                    "build the disposable index when local search or traversal is needed",
                )
            )
            return
        if not canonical_valid:
            issues.append(
                self._issue(
                    "ECHEL-INTEGRITY-INDEX-UNCHECKED",
                    "warning",
                    "cache/index.sqlite3",
                    "index freshness cannot be trusted while canonical records are invalid",
                    "repair canonical records, then discard and rebuild the index",
                )
            )
            return
        try:
            self.index.assert_current()
        except IndexError as exc:
            code = {
                "ECHEL-INDEX-STALE": "ECHEL-INTEGRITY-INDEX-STALE",
                "ECHEL-INDEX-CORRUPT": "ECHEL-INTEGRITY-INDEX-CORRUPT",
                "ECHEL-INDEX-FORMAT-UNSUPPORTED": "ECHEL-INTEGRITY-INDEX-UNSUPPORTED",
            }.get(exc.code, "ECHEL-INTEGRITY-INDEX")
            issues.append(
                self._issue(
                    code,
                    "warning",
                    "cache/index.sqlite3",
                    exc.detail,
                    "discard and rebuild the disposable index from canonical records",
                )
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
    def _issue(code: str, severity: str, path: str, detail: str, remedy: str) -> IntegrityIssue:
        return IntegrityIssue(code, severity, path, detail, remedy)
