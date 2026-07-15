from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from echel.authority import AUTHORITY_CAPABILITY, KnowledgeAuthorityService, Principal
from echel.findings import FindingService
from echel.lifecycle import LIFECYCLE_CAPABILITY, LifecycleError, LifecycleService
from echel.relationships import RelationshipService
from echel.storage import CanonicalRecordStore, CanonicalRepository, RecordConflictError, RecordExpectation


ROOT = Path(__file__).resolve().parents[2]
VALID_RECORDS = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)
T0 = "2026-07-15T04:00:00Z"
T1 = "2026-07-15T04:01:00Z"
T2 = "2026-07-15T04:02:00Z"
PROVENANCE = {"actor": "user:owner", "origin": "review", "method": "human"}


class LifecycleMaturityTests(unittest.TestCase):
    def make_service(self, workspace: Path, complete: bool = True) -> LifecycleService:
        (workspace / ".git").mkdir()
        store = CanonicalRecordStore(CanonicalRepository.create(workspace))
        project = deepcopy(next(item for item in VALID_RECORDS if item["record_type"] == "project"))
        store.write(project, RecordExpectation.absent())
        self.add_claim(store, "claim:problem", "problem", accepted=True)
        if complete:
            self.add_claim(store, "claim:user", "user", accepted=True)
        return LifecycleService(store)

    def add_claim(
        self, store: CanonicalRecordStore, record_id: str, kind: str, accepted: bool
    ) -> None:
        claim = deepcopy(next(item for item in VALID_RECORDS if item["record_type"] == "claim"))
        claim["id"] = record_id
        claim["kind"] = kind
        claim["stage"] = "problem"
        claim["status"] = "proposed"
        claim["revision"] = 1
        claim.pop("authority", None)
        store.write(claim, RecordExpectation.absent())
        if accepted:
            authority = KnowledgeAuthorityService(store)
            authority.apply(
                authority.preview(
                    "claim",
                    record_id,
                    "accepted",
                    self.knowledge_human(),
                    "Required maturity knowledge approved.",
                    T1,
                )
            )

    @staticmethod
    def lifecycle_human() -> Principal:
        return Principal("user:owner", "human", frozenset({LIFECYCLE_CAPABILITY}))

    @staticmethod
    def knowledge_human() -> Principal:
        return Principal("user:owner", "human", frozenset({AUTHORITY_CAPABILITY}))

    def add_finding(self, service: LifecycleService, severity: str = "error") -> FindingService:
        findings = FindingService(service.store)
        creation = findings.preview_create(
            "transaction:maturity-finding",
            "finding:maturity-gap",
            "contradiction",
            "Evidence contradicts required problem knowledge.",
            severity,
            ("claim:problem",),
            {"actor": "agent:reviewer", "origin": "run:review", "method": "inference"},
            T2,
        )
        findings.apply_create(creation)
        return findings

    def test_missing_required_knowledge_explains_blocked_advance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory), complete=False)
            assessment = service.assess("project:demo")
            self.assertFalse(assessment.usable)
            self.assertEqual(("user",), assessment.missing_kinds)
            with self.assertRaises(LifecycleError) as caught:
                service.preview_advance(
                    "project:demo", self.lifecycle_human(), "Advance.", T2
                )
            self.assertEqual("ECHEL-LIFECYCLE-ADVANCE-BLOCKED", caught.exception.code)

    def test_active_findings_block_or_caution_without_mutating_knowledge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            claim_before = deepcopy(service.store.load("claim", "claim:problem").record)
            self.add_finding(service, severity="error")
            assessment = service.assess("project:demo")
            self.assertFalse(assessment.usable)
            self.assertEqual(("finding:maturity-gap",), assessment.blocking_findings)
            self.assertEqual(claim_before, service.store.load("claim", "claim:problem").record)

        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            self.add_finding(service, severity="warning")
            assessment = service.assess("project:demo")
            self.assertTrue(assessment.usable)
            self.assertEqual(("finding:maturity-gap",), assessment.cautions)

    def test_preview_and_authorized_advance_are_explained_and_concurrent_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            transition = service.preview_advance(
                "project:demo", self.lifecycle_human(), "Problem framing is sufficient.", T2
            )
            self.assertEqual("problem", transition.to_dict()["from"])
            self.assertEqual("vision", transition.to_dict()["to"])
            self.assertEqual("problem", service.store.load("project", "project:demo").record["maturity"])
            competing = service.preview_advance(
                "project:demo", self.lifecycle_human(), "Also advance.", T2
            )
            service.apply_advance(transition)
            with self.assertRaises(RecordConflictError):
                service.apply_advance(competing)
            stored = service.store.load("project", "project:demo").record
            self.assertEqual("vision", stored["maturity"])
            self.assertEqual("user:owner", stored["maturity_transition"]["actor"])

    def test_agents_and_unscoped_humans_cannot_advance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            principals = (
                Principal("agent:hermes", "agent", frozenset({LIFECYCLE_CAPABILITY})),
                Principal("user:viewer", "human", frozenset()),
            )
            for principal in principals:
                with self.subTest(principal=principal.id):
                    with self.assertRaises(LifecycleError) as caught:
                        service.preview_advance("project:demo", principal, "Advance.", T2)
                    self.assertEqual("ECHEL-LIFECYCLE-AUTHORITY-DENIED", caught.exception.code)

    def test_backward_revision_marks_root_and_explicit_downstream_knowledge_stale(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            decision = deepcopy(next(item for item in VALID_RECORDS if item["record_type"] == "decision"))
            decision["status"] = "proposed"
            decision["revision"] = 1
            decision["updated_at"] = decision["created_at"]
            decision.pop("authority", None)
            service.store.write(decision, RecordExpectation.absent())
            authority = KnowledgeAuthorityService(service.store)
            authority.apply(
                authority.preview(
                    "decision", "decision:store", "accepted", self.knowledge_human(), "Approved.", T1
                )
            )
            relationships = RelationshipService(service.store)
            relationships.apply(
                relationships.preview(
                    "relationship:problem-informs-store",
                    "claim:problem",
                    "informs",
                    "decision:store",
                    "The storage choice follows from the problem constraint.",
                    PROVENANCE,
                    T2,
                )
            )
            self.add_finding(service)
            project_before = deepcopy(service.store.load("project", "project:demo").record)
            revision = service.preview_stale(
                "transaction:backward-revision",
                "finding:maturity-gap",
                "claim:problem",
                self.knowledge_human(),
                "Contradicting evidence invalidates dependent knowledge.",
                T2,
            )
            self.assertEqual(
                ["claim:problem", "decision:store"], revision.to_dict()["stale_records"]
            )
            service.apply_stale(revision)
            self.assertEqual("stale", service.store.load("claim", "claim:problem").record["status"])
            self.assertEqual("stale", service.store.load("decision", "decision:store").record["status"])
            self.assertEqual(project_before, service.store.load("project", "project:demo").record)
            assessment = service.assess("project:demo")
            self.assertIn("problem", assessment.missing_kinds)

    def test_unrelated_inactive_and_unauthorized_stale_requests_are_denied(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            self.add_finding(service)
            with self.assertRaises(LifecycleError) as unrelated:
                service.preview_stale(
                    "transaction:stale", "finding:maturity-gap", "claim:user", self.knowledge_human(), "Reason.", T2
                )
            self.assertEqual("ECHEL-LIFECYCLE-FINDING-UNRELATED", unrelated.exception.code)
            with self.assertRaises(LifecycleError) as denied:
                service.preview_stale(
                    "transaction:stale", "finding:maturity-gap", "claim:problem", Principal("agent:hermes", "agent", frozenset({AUTHORITY_CAPABILITY})), "Reason.", T2
                )
            self.assertEqual("ECHEL-LIFECYCLE-AUTHORITY-DENIED", denied.exception.code)

    def test_stale_preview_is_non_mutating_and_prepared_interruption_rolls_back(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            self.add_finding(service)
            revision = service.preview_stale(
                "transaction:stale", "finding:maturity-gap", "claim:problem", self.knowledge_human(), "Reason.", T2
            )
            self.assertEqual("accepted", service.store.load("claim", "claim:problem").record["status"])
            service.transactions.prepare(revision.transaction_id, list(revision.records))
            self.assertEqual("rolled_back", service.transactions.recover()[0].outcome)
            self.assertEqual("accepted", service.store.load("claim", "claim:problem").record["status"])


if __name__ == "__main__":
    unittest.main()
