from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from echel.storage import (
    CanonicalRecordStore,
    CanonicalRepository,
    RepositoryError,
    TransactionJournal,
)


ROOT = Path(__file__).resolve().parents[2]
VALID_RECORDS = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)


class TransactionJournalTests(unittest.TestCase):
    def make_journal(self, workspace: Path) -> TransactionJournal:
        (workspace / ".git").mkdir()
        repository = CanonicalRepository.create(workspace)
        return TransactionJournal(CanonicalRecordStore(repository))

    def test_preview_validates_all_records_without_creating_journal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = self.make_journal(Path(directory))
            plan = journal.preview("transaction:preview", VALID_RECORDS[1:3])
            self.assertEqual(("claim:need", "decision:store"), plan.record_ids)
            self.assertEqual(2, plan.changed_records)
            self.assertFalse(plan.journal.exists())
            self.assertFalse(journal.root.exists())

    def test_commit_applies_all_records_and_removes_completed_journal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = self.make_journal(Path(directory))
            result = journal.execute("transaction:complete", VALID_RECORDS[1:4])
            self.assertEqual("committed", result.outcome)
            self.assertEqual(3, result.record_count)
            self.assertFalse((journal.root / "complete").exists())
            for record in VALID_RECORDS[1:4]:
                self.assertFalse(journal.store.preview_write(record).changed)

    def test_explicit_rollback_discards_prepared_intent_without_record_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = self.make_journal(Path(directory))
            journal.prepare("transaction:cancel", VALID_RECORDS[1:3])
            result = journal.rollback("transaction:cancel")
            self.assertEqual("rolled_back", result.outcome)
            self.assertEqual([], list(journal.store.repository.records.rglob("*.json")))
            self.assertFalse((journal.root / "cancel").exists())

    def test_recovery_rolls_back_prepared_transactions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = self.make_journal(Path(directory))
            journal.prepare("transaction:abandoned", VALID_RECORDS[1:3])
            self.assertEqual("rolled_back", journal.recover()[0].outcome)
            self.assertEqual([], list(journal.store.repository.records.rglob("*.json")))

    def test_partial_commit_is_durably_recovered_by_roll_forward(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = self.make_journal(Path(directory))
            journal.prepare("transaction:recover", VALID_RECORDS[1:4])
            original_write = journal.store.write
            calls = 0

            def interrupted(record):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise RepositoryError("ECHEL-RECORD-WRITE", Path("simulated"), "interrupted")
                return original_write(record)

            with patch.object(journal.store, "write", side_effect=interrupted):
                with self.assertRaises(RepositoryError) as caught:
                    journal.commit("transaction:recover")
            self.assertEqual("ECHEL-TRANSACTION-INCOMPLETE", caught.exception.code)
            state = json.loads((journal.root / "recover" / "journal.json").read_text())
            self.assertEqual("committing", state["state"])
            self.assertFalse(journal.store.preview_write(VALID_RECORDS[1]).changed)
            self.assertTrue(journal.store.preview_write(VALID_RECORDS[2]).changed)

            result = journal.recover()[0]
            self.assertEqual("committed", result.outcome)
            for record in VALID_RECORDS[1:4]:
                self.assertFalse(journal.store.preview_write(record).changed)

    def test_commit_decision_cannot_be_rolled_back(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = self.make_journal(Path(directory))
            journal.prepare("transaction:decided", VALID_RECORDS[1:3])
            path = journal.root / "decided" / "journal.json"
            payload = json.loads(path.read_text())
            payload["state"] = "committing"
            path.write_text(json.dumps(payload))
            with self.assertRaises(RepositoryError) as caught:
                journal.rollback("transaction:decided")
            self.assertEqual("ECHEL-TRANSACTION-COMMIT-DECIDED", caught.exception.code)

    def test_corrupt_staged_content_stops_recovery_without_canonical_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = self.make_journal(Path(directory))
            journal.prepare("transaction:corrupt", VALID_RECORDS[1:3])
            transaction = journal.root / "corrupt"
            payload = json.loads((transaction / "journal.json").read_text())
            payload["state"] = "committing"
            (transaction / "journal.json").write_text(json.dumps(payload))
            (transaction / "staged" / "0000.json").write_text("{}")
            with self.assertRaises(RepositoryError) as caught:
                journal.recover()
            self.assertEqual("ECHEL-TRANSACTION-INCOMPLETE", caught.exception.code)
            self.assertEqual([], list(journal.store.repository.records.rglob("*.json")))

    def test_empty_duplicate_and_invalid_transaction_ids_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = self.make_journal(Path(directory))
            with self.assertRaises(RepositoryError) as caught:
                journal.preview("transaction:empty", [])
            self.assertEqual("ECHEL-TRANSACTION-EMPTY", caught.exception.code)
            with self.assertRaises(RepositoryError) as caught:
                journal.preview("transaction:duplicate", [VALID_RECORDS[1], deepcopy(VALID_RECORDS[1])])
            self.assertEqual("ECHEL-TRANSACTION-DUPLICATE", caught.exception.code)
            with self.assertRaises(RepositoryError) as caught:
                journal.preview("run:wrong", VALID_RECORDS[1:2])
            self.assertEqual("ECHEL-TRANSACTION-ID", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
