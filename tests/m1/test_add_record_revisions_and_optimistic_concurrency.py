from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from echel.storage import (
    CanonicalRecordStore,
    CanonicalRepository,
    RecordConflictError,
    RecordExpectation,
    RepositoryError,
)


ROOT = Path(__file__).resolve().parents[2]
CLAIM = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)[1]


class OptimisticConcurrencyTests(unittest.TestCase):
    def make_store(self, workspace: Path) -> CanonicalRecordStore:
        (workspace / ".git").mkdir()
        return CanonicalRecordStore(CanonicalRepository.create(workspace))

    def test_create_requires_explicit_absence_and_revision_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            with self.assertRaises(RepositoryError) as caught:
                store.write(CLAIM)
            self.assertEqual("ECHEL-PRECONDITION-REQUIRED", caught.exception.code)
            invalid = deepcopy(CLAIM)
            invalid["revision"] = 2
            with self.assertRaises(RepositoryError) as caught:
                store.write(invalid, RecordExpectation.absent())
            self.assertEqual("ECHEL-REVISION-SEQUENCE", caught.exception.code)
            store.write(CLAIM, RecordExpectation.absent())

    def test_observed_revision_allows_exactly_next_revision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            store.write(CLAIM, RecordExpectation.absent())
            observed = store.observe(CLAIM)
            updated = deepcopy(CLAIM)
            updated["revision"] = 2
            updated["statement"] = "Updated once"
            plan = store.write(updated, observed)
            self.assertEqual(1, plan.expectation.revision)
            self.assertEqual(2, json.loads(plan.path.read_text())["revision"])

    def test_stale_update_returns_semantic_conflict_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            store.write(CLAIM, RecordExpectation.absent())
            stale = store.observe(CLAIM)
            winner = deepcopy(CLAIM)
            winner["revision"] = 2
            winner["statement"] = "Winner"
            store.write(winner, stale)
            winning_bytes = store.preview_write(winner, store.observe(winner)).path.read_bytes()
            loser = deepcopy(CLAIM)
            loser["revision"] = 2
            loser["statement"] = "Loser"
            with self.assertRaises(RecordConflictError) as caught:
                store.write(loser, stale)
            conflict = caught.exception
            self.assertEqual("ECHEL-RECORD-CONFLICT", conflict.code)
            self.assertEqual(1, conflict.expected.revision)
            self.assertEqual(2, conflict.actual_revision)
            self.assertEqual("claim:need", conflict.to_dict()["record_id"])
            self.assertIn("reload, merge, and retry", str(conflict))
            self.assertEqual(winning_bytes, conflict.path.read_bytes())

    def test_digest_detects_external_change_that_did_not_advance_revision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            path = store.write(CLAIM, RecordExpectation.absent()).path
            observed = store.observe(CLAIM)
            external = deepcopy(CLAIM)
            external["statement"] = "Externally edited without revision"
            path.write_text(json.dumps(external, indent=2, sort_keys=True) + "\n")
            update = deepcopy(CLAIM)
            update["revision"] = 2
            update["statement"] = "Legitimate update"
            with self.assertRaises(RecordConflictError) as caught:
                store.write(update, observed)
            self.assertEqual(1, caught.exception.actual_revision)
            self.assertNotEqual(observed.digest, caught.exception.actual_digest)
            self.assertEqual(external, json.loads(path.read_text()))

    def test_skipped_or_repeated_revision_is_rejected_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            path = store.write(CLAIM, RecordExpectation.absent()).path
            before = path.read_bytes()
            for revision in (1, 3):
                update = deepcopy(CLAIM)
                update["revision"] = revision
                update["statement"] = f"Revision {revision}"
                with self.subTest(revision=revision):
                    with self.assertRaises(RepositoryError) as caught:
                        store.write(update, store.observe(CLAIM))
                    self.assertEqual("ECHEL-REVISION-SEQUENCE", caught.exception.code)
                    self.assertEqual(before, path.read_bytes())

    def test_create_race_conflicts_but_identical_retry_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            absent = RecordExpectation.absent()
            store.write(CLAIM, absent)
            retry = store.write(deepcopy(CLAIM), absent)
            self.assertFalse(retry.changed)
            competitor = deepcopy(CLAIM)
            competitor["statement"] = "Different create"
            with self.assertRaises(RecordConflictError):
                store.write(competitor, absent)

    def test_corrupt_current_record_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            path = store.write(CLAIM, RecordExpectation.absent()).path
            path.write_text("not json")
            with self.assertRaises(RepositoryError) as caught:
                store.observe(CLAIM)
            self.assertEqual("ECHEL-RECORD-CURRENT-INVALID", caught.exception.code)
            self.assertEqual("not json", path.read_text())

    def test_active_write_lock_denies_racing_writer_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            lock = store.repository.root / "write.lock"
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            try:
                with self.assertRaises(RepositoryError) as caught:
                    store.write(CLAIM, RecordExpectation.absent())
                self.assertEqual("ECHEL-WRITE-LOCKED", caught.exception.code)
                self.assertFalse(store.preview_write(CLAIM, RecordExpectation.absent()).path.exists())
            finally:
                os.close(descriptor)
                lock.unlink()


if __name__ == "__main__":
    unittest.main()
