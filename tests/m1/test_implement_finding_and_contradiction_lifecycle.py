from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from echel.authority import Principal
from echel.findings import (
    FINDING_CAPABILITY,
    FindingCreation,
    FindingError,
    FindingService,
)
from echel.schemas import SchemaValidationError
from echel.storage import CanonicalRecordStore, CanonicalRepository, RecordConflictError, RecordExpectation


ROOT = Path(__file__).resolve().parents[2]
VALID_RECORDS = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)
CREATED_AT = "2026-07-15T03:00:00Z"
DECIDED_AT = "2026-07-15T03:05:00Z"
PROVENANCE = {"actor": "agent:reviewer", "origin": "run:review", "method": "inference"}


class FindingLifecycleTests(unittest.TestCase):
    def make_service(self, workspace: Path) -> FindingService:
        (workspace / ".git").mkdir()
        store = CanonicalRecordStore(CanonicalRepository.create(workspace))
        for record_type in ("project", "claim"):
            record = deepcopy(
                next(item for item in VALID_RECORDS if item["record_type"] == record_type)
            )
            store.write(record, RecordExpectation.absent())
        return FindingService(store)

    @staticmethod
    def human() -> Principal:
        return Principal("user:reviewer", "human", frozenset({FINDING_CAPABILITY}))

    def preview(self, service: FindingService, severity: str = "error") -> FindingCreation:
        return service.preview_create(
            "transaction:finding-gap",
            "finding:gap",
            "contradiction",
            "Observed behavior contradicts the stated need.",
            severity,
            ("claim:need",),
            PROVENANCE,
            CREATED_AT,
        )

    def test_preview_explains_maturity_impact_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            creation = self.preview(service)
            preview = creation.to_dict()
            self.assertEqual("blocked", preview["impact"]["level"])
            self.assertFalse(preview["impact"]["maturity_usable"])
            self.assertEqual(["claim:need"], preview["impact"]["affected"])
            self.assertEqual("preview", preview["mutation"])
            self.assertEqual(2, len(creation.records))
            self.assertEqual((), service.store.scan("finding"))

    def test_create_atomically_records_finding_and_explicit_impact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            claim_before = deepcopy(service.store.load("claim", "claim:need").record)
            service.apply_create(self.preview(service))
            finding = service.store.load("finding", "finding:gap").record
            relationship = service.store.scan("relationship")[0].record
            self.assertEqual("open", finding["status"])
            self.assertEqual(PROVENANCE, finding["provenance"])
            self.assertEqual("finding:gap", relationship["source"])
            self.assertEqual("affects", relationship["predicate"])
            self.assertEqual("claim:need", relationship["target"])
            self.assertEqual(claim_before, service.store.load("claim", "claim:need").record)

    def test_impact_is_derived_from_finding_and_relationship_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            service.apply_create(self.preview(service, severity="warning"))
            impact = service.assess("finding:gap")
            self.assertEqual("caution", impact.level)
            self.assertTrue(impact.maturity_usable)
            self.assertEqual(("claim:need",), impact.affected)

    def test_authorized_resolution_clears_impact_without_rewriting_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            service.apply_create(self.preview(service))
            source_before = deepcopy(service.store.load("claim", "claim:need").record)
            decision = service.preview_decision(
                "finding:gap", "resolved", self.human(), "The source was corrected externally.", DECIDED_AT
            )
            self.assertEqual("none", decision.impact.level)
            service.apply_decision(decision)
            self.assertTrue(service.assess("finding:gap").maturity_usable)
            self.assertEqual(source_before, service.store.load("claim", "claim:need").record)
            stored = service.store.load("finding", "finding:gap").record
            self.assertEqual("user:reviewer", stored["decision"]["actor"])

    def test_acceptance_keeps_finding_active_and_requires_human_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            service.apply_create(self.preview(service))
            principals = (
                Principal("agent:hermes", "agent", frozenset({FINDING_CAPABILITY})),
                Principal("user:viewer", "human", frozenset()),
            )
            for principal in principals:
                with self.subTest(principal=principal.id):
                    with self.assertRaises(FindingError) as caught:
                        service.preview_decision(
                            "finding:gap", "dismissed", principal, "Attempt.", DECIDED_AT
                        )
                    self.assertEqual("ECHEL-FINDING-AUTHORITY-DENIED", caught.exception.code)
            accepted = service.preview_decision(
                "finding:gap", "accepted", self.human(), "Confirmed contradiction.", DECIDED_AT
            )
            service.apply_decision(accepted)
            self.assertEqual("blocked", service.assess("finding:gap").level)

    def test_stale_parallel_decision_cannot_overwrite_winner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            service.apply_create(self.preview(service))
            resolved = service.preview_decision(
                "finding:gap", "resolved", self.human(), "Resolved.", DECIDED_AT
            )
            dismissed = service.preview_decision(
                "finding:gap", "dismissed", self.human(), "Not relevant.", DECIDED_AT
            )
            service.apply_decision(resolved)
            with self.assertRaises(RecordConflictError):
                service.apply_decision(dismissed)

    def test_interrupted_preparation_recovers_without_partial_impact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            creation = self.preview(service)
            service.transactions.prepare(creation.transaction_id, list(creation.records))
            results = service.transactions.recover()
            self.assertEqual("rolled_back", results[0].outcome)
            self.assertEqual((), service.store.scan("finding"))
            self.assertEqual((), service.store.scan("relationship"))

    def test_invalid_input_policy_and_tampering_fail_without_partial_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            cases = (
                ("unknown", "Statement", "error", ("claim:need",), "ECHEL-FINDING-KIND-INVALID"),
                ("gap", " ", "error", ("claim:need",), "ECHEL-FINDING-STATEMENT-REQUIRED"),
                ("gap", "Statement", "urgent", ("claim:need",), "ECHEL-FINDING-SEVERITY-INVALID"),
                ("gap", "Statement", "error", (), "ECHEL-FINDING-AFFECTS-INVALID"),
            )
            for kind, statement, severity, affected, code in cases:
                with self.subTest(code=code):
                    with self.assertRaises(FindingError) as caught:
                        service.preview_create(
                            "transaction:test", "finding:test", kind, statement, severity, affected, PROVENANCE, CREATED_AT
                        )
                    self.assertEqual(code, caught.exception.code)

            creation = self.preview(service)
            records = list(deepcopy(creation.records))
            records[1]["policy"] = "unreviewed/v1"
            tampered = FindingCreation(creation.transaction_id, tuple(records), creation.impact)
            with self.assertRaises(FindingError):
                service.apply_create(tampered)
            self.assertEqual((), service.store.scan("finding"))
            self.assertEqual((), service.store.scan("relationship"))

    def test_schema_requires_matching_human_decision_for_closed_finding(self) -> None:
        finding = deepcopy(next(item for item in VALID_RECORDS if item["record_type"] == "finding"))
        finding["status"] = "resolved"
        service_schema = None
        with tempfile.TemporaryDirectory() as directory:
            service_schema = self.make_service(Path(directory)).store.schemas
            with self.assertRaises(SchemaValidationError):
                service_schema.validate(finding)
            finding["decision"] = {
                "action": "dismissed",
                "actor": "user:reviewer",
                "actor_kind": "human",
                "capability": FINDING_CAPABILITY,
                "rationale": "Mismatch.",
                "decided_at": DECIDED_AT,
                "finding_revision": 1,
            }
            with self.assertRaises(SchemaValidationError):
                service_schema.validate(finding)


if __name__ == "__main__":
    unittest.main()
