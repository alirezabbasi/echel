from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from benchmarks.kernel.gate import GATE_VERSION, run_kernel_gate
from echel.portability import PortableRepositoryService, PortabilityError
from echel.storage import (
    CanonicalRecordStore,
    CanonicalRepository,
    DisposableIndex,
    RecordExpectation,
    TransactionJournal,
)


ROOT = Path(__file__).resolve().parents[2]
VALID_RECORDS = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)


class KernelGateTests(unittest.TestCase):
    def make_store(self, workspace: Path, *, populated: bool = True) -> CanonicalRecordStore:
        (workspace / ".git").mkdir()
        store = CanonicalRecordStore(CanonicalRepository.create(workspace))
        if populated:
            for fixture in VALID_RECORDS:
                record = deepcopy(fixture)
                record["revision"] = 1
                store.write(record, RecordExpectation.absent())
        return store

    def test_g_m1_scale_and_latency_targets_pass_on_frozen_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = run_kernel_gate(Path(directory) / "kernel.sqlite3")

            self.assertEqual(1_100_000, report.record_count)
            self.assertEqual(1_000_000, report.relationship_count)
            self.assertTrue(report.passed, report.to_dict())
            self.assertTrue(all(timing.p90_ms < 200 for timing in report.timings))
            self.assertEqual(GATE_VERSION, report.to_dict()["gate"])

    def test_captured_evidence_discloses_environment_targets_and_limitations(self) -> None:
        evidence = json.loads(
            (ROOT / "benchmarks" / "kernel" / "evidence" / "2026-07-15-local.json").read_text()
        )
        self.assertEqual(GATE_VERSION, evidence["gate"])
        self.assertEqual(1_100_000, evidence["dataset"]["records"])
        self.assertEqual(1_000_000, evidence["dataset"]["relationships"])
        self.assertTrue(evidence["passed"])
        self.assertTrue(all(item["p90_ms"] < item["target_ms"] for item in evidence["timings"]))
        self.assertEqual(
            {"python", "sqlite", "platform"}, set(evidence["environment"])
        )
        self.assertGreaterEqual(len(evidence["limitations"]), 3)

    def test_prepared_transaction_recovery_is_non_mutating(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory), populated=False)
            claim = deepcopy(next(record for record in VALID_RECORDS if record["record_type"] == "claim"))
            journal = TransactionJournal(store)
            journal.prepare("transaction:gate-prepared", [claim])

            result = journal.recover()

            self.assertEqual("rolled_back", result[0].outcome)
            self.assertFalse(store.repository.collection("claims").joinpath("need.json").exists())

    def test_projection_rebuild_recovers_equivalent_queries_without_truth_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(Path(directory))
            index = DisposableIndex(store)
            canonical = {
                path.relative_to(store.repository.root).as_posix(): path.read_bytes()
                for path in store.repository.root.glob("**/*.json")
            }
            index.rebuild()
            first = tuple(hit.to_dict() for hit in index.search("traceability"))
            index.path.write_bytes(b"corrupt")
            index.discard()
            index.rebuild()

            self.assertEqual(first, tuple(hit.to_dict() for hit in index.search("traceability")))
            self.assertEqual(
                canonical,
                {
                    path.relative_to(store.repository.root).as_posix(): path.read_bytes()
                    for path in store.repository.root.glob("**/*.json")
                },
            )

    def test_tampered_import_plan_recovery_preserves_empty_target(self) -> None:
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            source = self.make_store(Path(source_dir))
            target = self.make_store(Path(target_dir), populated=False)
            importer = PortableRepositoryService(target)
            plan = importer.preview_import(
                PortableRepositoryService(source).export().content, "transaction:gate-import"
            )
            plan.entries[0].record["name"] = "tampered"

            with self.assertRaises(PortabilityError):
                importer.apply_import(plan)

            self.assertFalse((target.repository.root / "project.json").exists())
            self.assertEqual([], list(target.repository.records.glob("*/*.json")))


if __name__ == "__main__":
    unittest.main()
