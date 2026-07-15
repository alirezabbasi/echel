from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from echel.integrity import IntegrityService
from echel.portability import PortableRepositoryService, PortabilityError
from echel.storage import CanonicalRecordStore, CanonicalRepository, DisposableIndex, RecordExpectation


ROOT = Path(__file__).resolve().parents[2]
VALID_RECORDS = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)


class PortabilityAndIntegrityTests(unittest.TestCase):
    def make_store(self, workspace: Path, *, populated: bool = True) -> CanonicalRecordStore:
        (workspace / ".git").mkdir()
        store = CanonicalRecordStore(CanonicalRepository.create(workspace))
        if populated:
            for fixture in VALID_RECORDS:
                record = deepcopy(fixture)
                record["revision"] = 1
                store.write(record, RecordExpectation.absent())
        return store

    @staticmethod
    def semantic_records(store: CanonicalRecordStore) -> dict[str, dict]:
        records = {}
        for fixture in VALID_RECORDS:
            record_type = fixture["record_type"]
            for loaded in store.scan(record_type):
                records[str(loaded.record["id"])] = loaded.record
        return records

    def test_deterministic_export_and_atomic_import_round_trip_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            source = self.make_store(Path(source_dir))
            service = PortableRepositoryService(source)
            first = service.export()
            second = service.export()
            self.assertEqual(first.content, second.content)
            self.assertEqual(len(VALID_RECORDS), first.record_count)

            target = self.make_store(Path(target_dir), populated=False)
            importer = PortableRepositoryService(target)
            plan = importer.preview_import(first.content, "transaction:portable-import")
            self.assertEqual("preview", plan.to_dict()["mutation"])
            self.assertEqual({}, self.semantic_records(target))

            result = importer.apply_import(plan)
            self.assertEqual("imported", result.outcome)
            self.assertEqual(first.fingerprint, result.fingerprint)
            self.assertEqual(self.semantic_records(source), self.semantic_records(target))
            self.assertEqual(
                "user:owner", target.load("claim", "claim:need").record["provenance"]["actor"]
            )

    def test_tampered_bundle_plan_and_nonempty_target_are_denied_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            source = self.make_store(Path(source_dir))
            bundle = PortableRepositoryService(source).export()
            target = self.make_store(Path(target_dir), populated=False)
            importer = PortableRepositoryService(target)

            payload = json.loads(bundle.content)
            payload["records"][0]["record"]["name"] = "Tampered"
            tampered = json.dumps(payload).encode()
            with self.assertRaises(PortabilityError) as digest:
                importer.preview_import(tampered, "transaction:tampered")
            self.assertEqual("ECHEL-IMPORT-DIGEST-MISMATCH", digest.exception.code)
            self.assertIn("re-export", digest.exception.remedy)
            self.assertEqual({}, self.semantic_records(target))

            plan = importer.preview_import(bundle.content, "transaction:plan")
            plan.entries[0].record["name"] = "Plan tamper"
            with self.assertRaises(PortabilityError) as invalid_plan:
                importer.apply_import(plan)
            self.assertEqual("ECHEL-IMPORT-PLAN-INVALID", invalid_plan.exception.code)
            self.assertEqual({}, self.semantic_records(target))

            populated_target = PortableRepositoryService(source)
            with self.assertRaises(PortabilityError) as nonempty:
                populated_target.preview_import(bundle.content, "transaction:merge")
            self.assertEqual("ECHEL-IMPORT-TARGET-NOT-EMPTY", nonempty.exception.code)

    def test_unsupported_format_version_and_orphan_import_have_remedies(self) -> None:
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            source = self.make_store(Path(source_dir))
            payload = json.loads(PortableRepositoryService(source).export().content)
            target = PortableRepositoryService(self.make_store(Path(target_dir), populated=False))

            unsupported_format = deepcopy(payload)
            unsupported_format["format"] = "echel-export/v99"
            with self.assertRaises(PortabilityError) as format_error:
                target.preview_import(json.dumps(unsupported_format).encode(), "transaction:format")
            self.assertEqual("ECHEL-IMPORT-FORMAT-UNSUPPORTED", format_error.exception.code)
            self.assertTrue(format_error.exception.remedy)

            unsupported_version = deepcopy(payload)
            unsupported_version["records"][0]["record"]["schema_version"] = 99
            with self.assertRaises(PortabilityError) as version_error:
                target.preview_import(json.dumps(unsupported_version).encode(), "transaction:version")
            self.assertEqual("ECHEL-IMPORT-VERSION-UNSUPPORTED", version_error.exception.code)
            self.assertIn("migrate", version_error.exception.remedy)

            orphan = deepcopy(payload)
            orphan["records"] = [
                entry for entry in orphan["records"] if entry["record"]["id"] != "claim:need"
            ]
            orphan["fingerprint"] = PortableRepositoryService._fingerprint(orphan["records"])
            with self.assertRaises(PortabilityError) as orphan_error:
                target.preview_import(json.dumps(orphan).encode(), "transaction:orphan")
            self.assertEqual("ECHEL-IMPORT-ORPHAN-LINK", orphan_error.exception.code)
            self.assertIn("endpoint", orphan_error.exception.remedy)

    def test_healthy_repository_and_missing_optional_index_are_explained(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            missing = IntegrityService(store).inspect()
            self.assertTrue(missing.healthy)
            self.assertEqual(["ECHEL-INTEGRITY-INDEX-MISSING"], [issue.code for issue in missing.issues])
            self.assertTrue(missing.issues[0].remedy)

            index = DisposableIndex(store)
            index.rebuild()
            healthy = IntegrityService(store, index).inspect()
            self.assertTrue(healthy.healthy)
            self.assertEqual((), healthy.issues)
            self.assertEqual(len(VALID_RECORDS), healthy.records_checked)

    def test_corruption_orphan_link_and_stale_index_each_have_remedies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            index = DisposableIndex(store)
            index.rebuild()
            store.load("claim", "claim:need").path.unlink()

            report = IntegrityService(store, index).inspect()
            issues = {issue.code: issue for issue in report.issues}
            self.assertFalse(report.healthy)
            self.assertIn("ECHEL-INTEGRITY-ORPHAN-LINK", issues)
            self.assertIn("ECHEL-INTEGRITY-INDEX-STALE", issues)
            self.assertTrue(issues["ECHEL-INTEGRITY-ORPHAN-LINK"].remedy)
            self.assertIn("rebuild", issues["ECHEL-INTEGRITY-INDEX-STALE"].remedy)

            relationship = store.load("relationship", "relationship:need-project").path
            relationship.write_text("not json")
            corrupted = IntegrityService(store, index).inspect()
            corruption = next(
                issue for issue in corrupted.issues if issue.code == "ECHEL-INTEGRITY-CORRUPT"
            )
            self.assertIn("restore", corruption.remedy)

    def test_unsupported_canonical_version_reports_migration_remedy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            path = store.load("claim", "claim:need").path
            record = json.loads(path.read_text())
            record["schema_version"] = 99
            path.write_text(json.dumps(record))

            report = IntegrityService(store).inspect()
            issue = next(
                issue
                for issue in report.issues
                if issue.code == "ECHEL-INTEGRITY-VERSION-UNSUPPORTED"
            )
            self.assertFalse(report.healthy)
            self.assertIn("migration", issue.remedy)


if __name__ == "__main__":
    unittest.main()
