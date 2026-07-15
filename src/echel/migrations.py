from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any
from uuid import uuid4

from echel.domain.value_objects import Identifier
from echel.schemas import SchemaRegistry, SchemaValidationError
from echel.storage import CanonicalRepository


@dataclass
class MigrationError(RuntimeError):
    code: str
    path: Path
    detail: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.detail}"


@dataclass(frozen=True)
class MigrationEntry:
    path: str
    record_id: str
    source_digest: str
    target_digest: str
    source_content: bytes
    target_content: bytes


@dataclass(frozen=True)
class MigrationPlan:
    migration_id: str
    source_version: int
    target_version: int
    entries: tuple[MigrationEntry, ...]
    backup: Path
    journal: Path

    def to_dict(self) -> dict[str, Any]:
        return {
            "migration_id": self.migration_id,
            "source_version": self.source_version,
            "target_version": self.target_version,
            "record_count": len(self.entries),
            "records": [entry.record_id for entry in self.entries],
            "backup": str(self.backup),
            "journal": str(self.journal),
            "mutation": "preview",
        }


@dataclass(frozen=True)
class MigrationResult:
    migration_id: str
    outcome: str
    record_count: int


class MigrationService:
    """Upgrade canonical bytes through explicit, backed-up, recoverable plans."""

    def __init__(self, repository: CanonicalRepository, schemas: SchemaRegistry | None = None):
        self.repository = repository
        self.schemas = schemas or SchemaRegistry()
        self.backups = repository.root / "backups"
        self.journals = repository.root / "migrations"

    def preview(
        self,
        migration_id: str,
        target_version: int,
        migrated_at: str,
        resolutions: dict[str, dict[str, Any]] | None = None,
    ) -> MigrationPlan:
        identifier = self._migration_identifier(migration_id)
        if target_version != 1:
            raise MigrationError(
                "ECHEL-MIGRATION-TARGET-UNSUPPORTED",
                self.repository.root,
                "this release supports migration target version 1",
            )
        raw = self._raw_records()
        versions = {self._version(path, record) for path, record, _ in raw}
        if len(versions) > 1:
            raise MigrationError(
                "ECHEL-MIGRATION-MIXED-VERSIONS",
                self.repository.root,
                f"repository contains schema versions {sorted(versions)}; normalize one version at a time",
            )
        source_version = next(iter(versions), target_version)
        if source_version > target_version:
            raise MigrationError(
                "ECHEL-MIGRATION-DOWNGRADE-UNSUPPORTED",
                self.repository.root,
                f"cannot migrate version {source_version} to {target_version}",
            )
        if source_version not in {0, 1}:
            raise MigrationError(
                "ECHEL-MIGRATION-PATH-UNAVAILABLE",
                self.repository.root,
                f"no migration path from version {source_version} to {target_version}",
            )
        entries = []
        resolution_map = resolutions or {}
        known_ids = {str(record.get("id", "")) for _, record, _ in raw}
        unknown_resolutions = sorted(set(resolution_map) - known_ids)
        if unknown_resolutions:
            raise MigrationError(
                "ECHEL-MIGRATION-RESOLUTION-UNKNOWN",
                self.repository.root,
                f"resolutions reference unknown records: {unknown_resolutions}",
            )
        for path, record, source_content in raw:
            record_id = str(record.get("id", ""))
            if source_version == target_version:
                target_content = source_content
            else:
                migrated = self._migrate_v0(record, resolution_map.get(record_id, {}), migrated_at)
                try:
                    self.schemas.validate(migrated)
                except SchemaValidationError as exc:
                    raise MigrationError(
                        "ECHEL-MIGRATION-RESOLUTION-REQUIRED",
                        path,
                        f"target record is invalid; provide an explicit resolution: {exc}",
                    ) from exc
                target_content = self._json_bytes(migrated)
            entries.append(
                MigrationEntry(
                    path=str(path.relative_to(self.repository.root)),
                    record_id=record_id,
                    source_digest=self._digest(source_content),
                    target_digest=self._digest(target_content),
                    source_content=source_content,
                    target_content=target_content,
                )
            )
        local = identifier.local
        return MigrationPlan(
            migration_id=migration_id,
            source_version=source_version,
            target_version=target_version,
            entries=tuple(entries),
            backup=self.backups / local,
            journal=self.journals / local,
        )

    def apply(self, plan: MigrationPlan) -> MigrationResult:
        if plan.source_version == plan.target_version:
            return MigrationResult(plan.migration_id, "already-current", 0)
        self.prepare(plan)
        return self.commit(plan.migration_id)

    def prepare(self, plan: MigrationPlan) -> None:
        """Persist exact backup and staged intent without changing canonical records."""

        self._validate_operational_root(self.backups)
        self._validate_operational_root(self.journals)
        if plan.backup.exists() or plan.journal.exists():
            raise MigrationError(
                "ECHEL-MIGRATION-EXISTS",
                plan.backup if plan.backup.exists() else plan.journal,
                "choose a new migration id or recover the existing operation",
            )
        self._verify_sources(plan.entries)
        backup_temp = self.backups / f".{plan.backup.name}.{uuid4().hex}.tmp"
        journal_temp = self.journals / f".{plan.journal.name}.{uuid4().hex}.tmp"
        try:
            self.backups.mkdir(exist_ok=True)
            self.journals.mkdir(exist_ok=True)
            for entry in plan.entries:
                self._write_new(backup_temp / "records" / entry.path, entry.source_content)
                self._write_new(journal_temp / "staged" / entry.path, entry.target_content)
            manifest = self._manifest(plan, "prepared")
            self._write_new(backup_temp / "manifest.json", self._json_bytes(manifest))
            self._write_new(journal_temp / "journal.json", self._json_bytes(manifest))
            os.replace(backup_temp, plan.backup)
            os.replace(journal_temp, plan.journal)
            self._sync_directory(self.backups)
            self._sync_directory(self.journals)
        except OSError as exc:
            shutil.rmtree(backup_temp, ignore_errors=True)
            shutil.rmtree(journal_temp, ignore_errors=True)
            raise MigrationError("ECHEL-MIGRATION-PREPARE", plan.journal, str(exc)) from exc

    def commit(self, migration_id: str) -> MigrationResult:
        identifier = self._migration_identifier(migration_id)
        journal = self.journals / identifier.local
        manifest = self._load_manifest(journal / "journal.json")
        state = manifest.get("state")
        if state not in {"prepared", "committing"}:
            raise MigrationError(
                "ECHEL-MIGRATION-STATE", journal, f"cannot commit state {state!r}"
            )
        try:
            if state == "prepared":
                manifest["state"] = "committing"
                self._replace_json(journal / "journal.json", manifest)
            self._roll_forward(journal, manifest)
        except (OSError, MigrationError) as exc:
            raise MigrationError(
                "ECHEL-MIGRATION-INCOMPLETE",
                journal,
                "commit intent is durable; run recovery to finish: " + str(exc),
            ) from exc
        count = len(manifest["entries"])
        shutil.rmtree(journal)
        self._sync_directory(self.journals)
        return MigrationResult(migration_id, "upgraded", count)

    def recover(self) -> list[MigrationResult]:
        if not self.journals.exists():
            return []
        results = []
        for journal in sorted(path for path in self.journals.iterdir() if path.is_dir()):
            if journal.name.startswith("."):
                shutil.rmtree(journal)
                continue
            manifest = self._load_manifest(journal / "journal.json")
            migration_id = str(manifest["migration_id"])
            if manifest["state"] == "prepared":
                count = len(manifest["entries"])
                shutil.rmtree(journal)
                results.append(MigrationResult(migration_id, "rolled-back", count))
            elif manifest["state"] == "committing":
                results.append(self.commit(migration_id))
            else:
                raise MigrationError(
                    "ECHEL-MIGRATION-STATE", journal, f"unknown state {manifest['state']!r}"
                )
        self._sync_directory(self.journals)
        return results

    def rollback(self, migration_id: str) -> MigrationResult:
        identifier = self._migration_identifier(migration_id)
        backup = self.backups / identifier.local
        manifest = self._load_manifest(backup / "manifest.json")
        for entry in manifest["entries"]:
            path = self._canonical_path(entry["path"])
            if not path.is_file() or self._digest(path.read_bytes()) != entry["target_digest"]:
                raise MigrationError(
                    "ECHEL-MIGRATION-ROLLBACK-CONFLICT",
                    path,
                    "record changed after migration; preserve or reconcile it before rollback",
                )
        for entry in manifest["entries"]:
            path = self._canonical_path(entry["path"])
            source = self._operational_entry(backup / "records", entry["path"])
            self._replace_bytes(path, source.read_bytes())
        return MigrationResult(migration_id, "restored-backup", len(manifest["entries"]))

    def _raw_records(self) -> list[tuple[Path, dict[str, Any], bytes]]:
        paths = []
        project = self.repository.root / "project.json"
        if project.is_file():
            paths.append(project)
        paths.extend(sorted(self.repository.records.glob("*/*.json")))
        records = []
        for path in paths:
            if not path.resolve().is_relative_to(self.repository.workspace):
                raise MigrationError("ECHEL-MIGRATION-PATH-ESCAPE", path, "record escapes repository")
            content = path.read_bytes()
            try:
                record = json.loads(content)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise MigrationError("ECHEL-MIGRATION-SOURCE-INVALID", path, str(exc)) from exc
            if not isinstance(record, dict) or not isinstance(record.get("id"), str):
                raise MigrationError(
                    "ECHEL-MIGRATION-SOURCE-INVALID", path, "record must be an object with an id"
                )
            records.append((path, record, content))
        return records

    @staticmethod
    def _migrate_v0(
        record: dict[str, Any], resolution: dict[str, Any], migrated_at: str
    ) -> dict[str, Any]:
        migrated = json.loads(json.dumps(record))
        remove_fields = resolution.get("remove_fields", [])
        set_fields = resolution.get("set_fields", {})
        if not isinstance(remove_fields, list) or not all(
            isinstance(field, str) for field in remove_fields
        ) or not isinstance(set_fields, dict):
            raise MigrationError(
                "ECHEL-MIGRATION-RESOLUTION-INVALID",
                Path(str(record.get("id", "record"))),
                "resolution requires string remove_fields and object set_fields",
            )
        for field in remove_fields:
            migrated.pop(field, None)
        migrated.update(set_fields)
        migrated["schema_version"] = 1
        revision = migrated.get("revision")
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
            raise MigrationError(
                "ECHEL-MIGRATION-SOURCE-INVALID",
                Path(str(record.get("id", "record"))),
                "revision must be a positive integer",
            )
        migrated["revision"] = revision + 1
        migrated["updated_at"] = migrated_at
        extensions = migrated.setdefault("extensions", {})
        if not isinstance(extensions, dict):
            raise MigrationError(
                "ECHEL-MIGRATION-SOURCE-INVALID",
                Path(str(record.get("id", "record"))),
                "extensions must be an object",
            )
        extensions["dev.echel.migration"] = {
            "from": 0,
            "to": 1,
            "migrated_at": migrated_at,
        }
        return migrated

    def _roll_forward(self, journal: Path, manifest: dict[str, Any]) -> None:
        for entry in manifest["entries"]:
            path = self._canonical_path(entry["path"])
            current = self._digest(path.read_bytes()) if path.is_file() else None
            if current == entry["target_digest"]:
                continue
            if current != entry["source_digest"]:
                raise MigrationError(
                    "ECHEL-MIGRATION-CONFLICT", path, "source changed after preview or preparation"
                )
            staged = self._operational_entry(journal / "staged", entry["path"])
            content = staged.read_bytes()
            if self._digest(content) != entry["target_digest"]:
                raise MigrationError(
                    "ECHEL-MIGRATION-STAGED-CORRUPT", staged, "target digest does not match"
                )
            self._replace_bytes(path, content)

    def _verify_sources(self, entries: tuple[MigrationEntry, ...]) -> None:
        for entry in entries:
            path = self.repository.root / entry.path
            if not path.is_file() or self._digest(path.read_bytes()) != entry.source_digest:
                raise MigrationError(
                    "ECHEL-MIGRATION-CONFLICT", path, "source changed after migration preview"
                )

    @staticmethod
    def _version(path: Path, record: dict[str, Any]) -> int:
        version = record.get("schema_version")
        if isinstance(version, bool) or not isinstance(version, int) or version < 0:
            raise MigrationError(
                "ECHEL-MIGRATION-SOURCE-INVALID", path, "schema_version must be a non-negative integer"
            )
        return version

    @staticmethod
    def _manifest(plan: MigrationPlan, state: str) -> dict[str, Any]:
        return {
            "format": 1,
            "migration_id": plan.migration_id,
            "source_version": plan.source_version,
            "target_version": plan.target_version,
            "state": state,
            "entries": [
                {
                    "path": entry.path,
                    "record_id": entry.record_id,
                    "source_digest": entry.source_digest,
                    "target_digest": entry.target_digest,
                }
                for entry in plan.entries
            ],
        }

    @staticmethod
    def _load_manifest(path: Path) -> dict[str, Any]:
        try:
            manifest = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise MigrationError("ECHEL-MIGRATION-JOURNAL-INVALID", path, str(exc)) from exc
        if (
            not isinstance(manifest, dict)
            or manifest.get("format") != 1
            or manifest.get("state") not in {"prepared", "committing"}
            or not isinstance(manifest.get("entries"), list)
            or any(
                not isinstance(entry, dict)
                or not isinstance(entry.get("path"), str)
                or not isinstance(entry.get("record_id"), str)
                or not isinstance(entry.get("source_digest"), str)
                or not isinstance(entry.get("target_digest"), str)
                for entry in manifest.get("entries", [])
            )
        ):
            raise MigrationError(
                "ECHEL-MIGRATION-JOURNAL-INVALID", path, "unsupported migration manifest"
            )
        return manifest

    def _validate_operational_root(self, path: Path) -> None:
        if path.is_symlink() or not path.resolve().is_relative_to(self.repository.workspace):
            raise MigrationError(
                "ECHEL-MIGRATION-PATH-ESCAPE", path, "operational state must remain in repository"
            )

    def _canonical_path(self, value: str) -> Path:
        relative = Path(value)
        path = self.repository.root / relative
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or not path.resolve().is_relative_to(self.repository.workspace)
        ):
            raise MigrationError(
                "ECHEL-MIGRATION-PATH-ESCAPE", path, "manifest path escapes repository"
            )
        return path

    @staticmethod
    def _operational_entry(root: Path, value: str) -> Path:
        relative = Path(value)
        path = root / relative
        if relative.is_absolute() or ".." in relative.parts or not path.resolve().is_relative_to(root.resolve()):
            raise MigrationError(
                "ECHEL-MIGRATION-PATH-ESCAPE", path, "manifest path escapes operational state"
            )
        return path

    @staticmethod
    def _migration_identifier(value: str) -> Identifier:
        identifier = Identifier(value)
        if identifier.namespace != "migration":
            raise MigrationError(
                "ECHEL-MIGRATION-ID-INVALID", Path(value), "must use migration:local form"
            )
        return identifier

    @staticmethod
    def _digest(content: bytes) -> str:
        return "sha256:" + hashlib.sha256(content).hexdigest()

    @staticmethod
    def _json_bytes(value: dict[str, Any]) -> bytes:
        return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()

    @staticmethod
    def _write_new(path: Path, content: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())

    @staticmethod
    def _replace_bytes(path: Path, content: bytes) -> None:
        temporary = path.parent / f".{path.name}.{uuid4().hex}.tmp"
        try:
            with temporary.open("xb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)

    def _replace_json(self, path: Path, value: dict[str, Any]) -> None:
        self._replace_bytes(path, self._json_bytes(value))

    @staticmethod
    def _sync_directory(path: Path) -> None:
        descriptor: int | None = None
        try:
            descriptor = os.open(path, os.O_RDONLY)
            os.fsync(descriptor)
        except OSError:
            pass
        finally:
            if descriptor is not None:
                os.close(descriptor)
