from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from echel.schemas import SchemaValidationError
from echel.storage import CanonicalRecordStore, CanonicalRepository, RepositoryError


ROOT = Path(__file__).resolve().parents[2]
VALID_RECORDS = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)


class AtomicRecordWriteTests(unittest.TestCase):
    def make_store(self, workspace: Path) -> CanonicalRecordStore:
        (workspace / ".git").mkdir()
        return CanonicalRecordStore(CanonicalRepository.create(workspace))

    def test_every_core_record_has_a_safe_deterministic_location(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            store = self.make_store(workspace)
            paths = []
            for record in VALID_RECORDS:
                plan = store.write(record)
                paths.append(plan.path)
                self.assertTrue(plan.path.is_file())
                self.assertTrue(plan.path.resolve().is_relative_to(workspace.resolve()))
                self.assertNotIn(":", plan.path.name)
                self.assertEqual(record, json.loads(plan.path.read_text()))
            self.assertEqual(12, len(set(paths)))
            self.assertEqual(store.repository.root / "project.json", paths[0])

    def test_preview_validates_and_explains_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            plan = store.preview_write(VALID_RECORDS[1])
            self.assertFalse(plan.path.exists())
            self.assertFalse(plan.replacing)
            self.assertTrue(plan.changed)
            self.assertRegex(plan.digest, r"^sha256:[0-9a-f]{64}$")
            self.assertNotIn("content", plan.to_dict())

    def test_invalid_record_fails_before_any_file_is_created(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            invalid = deepcopy(VALID_RECORDS[1])
            invalid.pop("provenance")
            with self.assertRaises(SchemaValidationError):
                store.write(invalid)
            self.assertEqual([], list(store.repository.records.rglob("*.json")))
            self.assertEqual([], list(store.repository.records.rglob("*.tmp")))

    def test_interrupted_replace_preserves_previous_valid_record_and_cleans_temp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            original = VALID_RECORDS[1]
            path = store.write(original).path
            previous_bytes = path.read_bytes()
            replacement = deepcopy(original)
            replacement["revision"] = 2
            replacement["statement"] = "Updated statement"

            with patch.object(os, "replace", side_effect=OSError("interrupted")):
                with self.assertRaises(RepositoryError) as caught:
                    store.write(replacement)

            self.assertEqual("ECHEL-RECORD-WRITE", caught.exception.code)
            self.assertEqual(previous_bytes, path.read_bytes())
            self.assertEqual([], list(path.parent.glob(f".{path.name}.*.tmp")))
            store.schemas.validate(json.loads(path.read_text()))

    def test_failed_first_write_leaves_no_record_or_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            plan = store.preview_write(VALID_RECORDS[2])
            with patch.object(os, "replace", side_effect=PermissionError("denied")):
                with self.assertRaises(RepositoryError):
                    store.write(VALID_RECORDS[2])
            self.assertFalse(plan.path.exists())
            self.assertEqual([], list(plan.path.parent.glob("*.tmp")))

    def test_serialization_is_deterministic_and_unchanged_write_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            record = VALID_RECORDS[4]
            first = store.write(record)
            expected = (json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
            self.assertEqual(expected, first.path.read_bytes())
            with patch.object(os, "replace") as replace:
                second = store.write(deepcopy(record))
            replace.assert_not_called()
            self.assertTrue(second.replacing)
            self.assertFalse(second.changed)
            self.assertEqual(first.digest, second.digest)

    def test_identifier_namespace_must_match_record_type(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            record = deepcopy(VALID_RECORDS[1])
            record["id"] = "decision:need"
            with self.assertRaises(RepositoryError) as caught:
                store.preview_write(record)
            self.assertEqual("ECHEL-ID-NAMESPACE-MISMATCH", caught.exception.code)

    def test_collection_swap_after_discovery_cannot_redirect_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside_dir:
            store = self.make_store(Path(directory))
            claims = store.repository.collection("claims")
            claims.rmdir()
            claims.symlink_to(Path(outside_dir), target_is_directory=True)
            with self.assertRaises(RepositoryError) as caught:
                store.write(VALID_RECORDS[1])
            self.assertEqual("ECHEL-REPOSITORY-ESCAPE", caught.exception.code)
            self.assertEqual([], list(Path(outside_dir).iterdir()))


if __name__ == "__main__":
    unittest.main()
