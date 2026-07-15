from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from echel.migrations import MigrationError, MigrationService
from echel.storage import CanonicalRecordStore, CanonicalRepository, RecordExpectation


ROOT = Path(__file__).resolve().parents[2]
VALID_RECORDS = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)
MIGRATED_AT = "2026-07-15T06:00:00Z"


class SchemaMigrationTests(unittest.TestCase):
    def make_legacy(self, workspace: Path) -> tuple[MigrationService, dict[str, bytes]]:
        (workspace / ".git").mkdir()
        repository = CanonicalRepository.create(workspace)
        project = deepcopy(next(item for item in VALID_RECORDS if item["record_type"] == "project"))
        project["schema_version"] = 0
        project.pop("profile")
        claim = deepcopy(next(item for item in VALID_RECORDS if item["record_type"] == "claim"))
        claim["schema_version"] = 0
        claim.pop("kind")
        claim.pop("stage")
        paths = {
            "project:demo": repository.root / "project.json",
            "claim:need": repository.collection("claims") / "need.json",
        }
        originals = {}
        for record, record_id in ((project, "project:demo"), (claim, "claim:need")):
            content = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
            paths[record_id].write_bytes(content)
            originals[record_id] = content
        return MigrationService(repository), originals

    @staticmethod
    def resolutions() -> dict[str, dict]:
        return {
            "project:demo": {"set_fields": {"profile": "prototype"}},
            "claim:need": {"set_fields": {"kind": "problem", "stage": "problem"}},
        }

    def test_preview_is_dry_run_and_explains_explicit_resolutions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service, originals = self.make_legacy(Path(directory))
            plan = service.preview(
                "migration:v0-v1", 1, MIGRATED_AT, self.resolutions()
            )
            preview = plan.to_dict()
            self.assertEqual(0, preview["source_version"])
            self.assertEqual(1, preview["target_version"])
            self.assertEqual(2, preview["record_count"])
            self.assertEqual("preview", preview["mutation"])
            self.assertFalse(plan.backup.exists())
            self.assertFalse(plan.journal.exists())
            self.assertEqual(
                originals["project:demo"], (service.repository.root / "project.json").read_bytes()
            )

    def test_apply_creates_exact_backup_and_valid_current_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service, originals = self.make_legacy(Path(directory))
            plan = service.preview(
                "migration:v0-v1", 1, MIGRATED_AT, self.resolutions()
            )
            result = service.apply(plan)
            self.assertEqual("upgraded", result.outcome)
            self.assertFalse(plan.journal.exists())
            self.assertEqual(
                originals["project:demo"],
                (plan.backup / "records" / "project.json").read_bytes(),
            )
            store = CanonicalRecordStore(service.repository)
            project = store.load("project", "project:demo").record
            claim = store.load("claim", "claim:need").record
            self.assertEqual(1, project["schema_version"])
            self.assertEqual(2, project["revision"])
            self.assertEqual("prototype", project["profile"])
            self.assertEqual("problem", claim["kind"])
            self.assertEqual(0, claim["extensions"]["dev.echel.migration"]["from"])

    def test_rollback_restores_exact_source_bytes_and_refuses_newer_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service, originals = self.make_legacy(Path(directory))
            plan = service.preview(
                "migration:v0-v1", 1, MIGRATED_AT, self.resolutions()
            )
            service.apply(plan)
            result = service.rollback("migration:v0-v1")
            self.assertEqual("restored-backup", result.outcome)
            self.assertEqual(
                originals["project:demo"], (service.repository.root / "project.json").read_bytes()
            )

        with tempfile.TemporaryDirectory() as directory:
            service, _ = self.make_legacy(Path(directory))
            plan = service.preview(
                "migration:v0-v1", 1, MIGRATED_AT, self.resolutions()
            )
            service.apply(plan)
            (service.repository.root / "project.json").write_bytes(b"newer external edit\n")
            with self.assertRaises(MigrationError) as caught:
                service.rollback("migration:v0-v1")
            self.assertEqual("ECHEL-MIGRATION-ROLLBACK-CONFLICT", caught.exception.code)

    def test_mixed_versions_fail_before_backup_or_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service, originals = self.make_legacy(Path(directory))
            claim_path = service.repository.collection("claims") / "need.json"
            claim = json.loads(claim_path.read_text())
            claim["schema_version"] = 1
            claim_path.write_text(json.dumps(claim))
            with self.assertRaises(MigrationError) as caught:
                service.preview("migration:mixed", 1, MIGRATED_AT, self.resolutions())
            self.assertEqual("ECHEL-MIGRATION-MIXED-VERSIONS", caught.exception.code)
            self.assertEqual(
                originals["project:demo"], (service.repository.root / "project.json").read_bytes()
            )
            self.assertFalse(service.backups.exists())

    def test_missing_or_unknown_resolution_returns_actionable_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service, _ = self.make_legacy(Path(directory))
            with self.assertRaises(MigrationError) as missing:
                service.preview("migration:v0-v1", 1, MIGRATED_AT, {})
            self.assertEqual("ECHEL-MIGRATION-RESOLUTION-REQUIRED", missing.exception.code)
            with self.assertRaises(MigrationError) as unknown:
                service.preview(
                    "migration:v0-v1",
                    1,
                    MIGRATED_AT,
                    {**self.resolutions(), "claim:unknown": {"set_fields": {}}},
                )
            self.assertEqual("ECHEL-MIGRATION-RESOLUTION-UNKNOWN", unknown.exception.code)

    def test_source_change_after_preview_conflicts_without_backup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service, _ = self.make_legacy(Path(directory))
            plan = service.preview(
                "migration:v0-v1", 1, MIGRATED_AT, self.resolutions()
            )
            (service.repository.root / "project.json").write_bytes(b"changed\n")
            with self.assertRaises(MigrationError) as caught:
                service.apply(plan)
            self.assertEqual("ECHEL-MIGRATION-CONFLICT", caught.exception.code)
            self.assertFalse(plan.backup.exists())

    def test_prepared_interruption_rolls_back_and_committing_recovery_rolls_forward(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service, originals = self.make_legacy(Path(directory))
            plan = service.preview(
                "migration:prepared", 1, MIGRATED_AT, self.resolutions()
            )
            service.prepare(plan)
            result = service.recover()[0]
            self.assertEqual("rolled-back", result.outcome)
            self.assertEqual(
                originals["project:demo"], (service.repository.root / "project.json").read_bytes()
            )

        with tempfile.TemporaryDirectory() as directory:
            service, _ = self.make_legacy(Path(directory))
            plan = service.preview(
                "migration:committing", 1, MIGRATED_AT, self.resolutions()
            )
            service.prepare(plan)
            journal_path = plan.journal / "journal.json"
            journal = json.loads(journal_path.read_text())
            journal["state"] = "committing"
            journal_path.write_text(json.dumps(journal))
            result = service.recover()[0]
            self.assertEqual("upgraded", result.outcome)
            CanonicalRecordStore(service.repository).load("project", "project:demo")

    def test_current_repository_is_noop_and_does_not_create_backup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / ".git").mkdir()
            repository = CanonicalRepository.create(Path(directory))
            project = deepcopy(
                next(item for item in VALID_RECORDS if item["record_type"] == "project")
            )
            CanonicalRecordStore(repository).write(project, RecordExpectation.absent())
            service = MigrationService(repository)
            plan = service.preview("migration:noop", 1, MIGRATED_AT)
            self.assertEqual("already-current", service.apply(plan).outcome)
            self.assertFalse(plan.backup.exists())


if __name__ == "__main__":
    unittest.main()
