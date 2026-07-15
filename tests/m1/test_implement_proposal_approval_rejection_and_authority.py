from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from echel.authority import (
    AUTHORITY_CAPABILITY,
    AuthorityError,
    AuthorityTransition,
    KnowledgeAuthorityService,
    Principal,
)
from echel.schemas import SchemaValidationError
from echel.storage import (
    CanonicalRecordStore,
    CanonicalRepository,
    RecordConflictError,
    RecordExpectation,
)


ROOT = Path(__file__).resolve().parents[2]
VALID_RECORDS = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)
DECIDED_AT = "2026-07-15T01:00:00Z"


def proposed(record_type: str) -> dict:
    record = deepcopy(next(item for item in VALID_RECORDS if item["record_type"] == record_type))
    record["revision"] = 1
    record["status"] = "proposed"
    record["updated_at"] = record["created_at"]
    record.pop("authority", None)
    return record


class KnowledgeAuthorityTests(unittest.TestCase):
    def make_service(self, workspace: Path, record: dict) -> KnowledgeAuthorityService:
        (workspace / ".git").mkdir()
        store = CanonicalRecordStore(CanonicalRepository.create(workspace))
        store.write(record, RecordExpectation.absent())
        return KnowledgeAuthorityService(store)

    @staticmethod
    def human() -> Principal:
        return Principal("user:owner", "human", frozenset({AUTHORITY_CAPABILITY}))

    def test_preview_is_non_mutating_and_explains_authoritative_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = proposed("claim")
            service = self.make_service(Path(directory), record)
            transition = service.preview(
                "claim", record["id"], "accepted", self.human(), "Evidence supports it.", DECIDED_AT
            )
            preview = transition.to_dict()
            self.assertEqual("proposed", preview["from_status"])
            self.assertEqual("accepted", preview["to_status"])
            self.assertEqual(2, preview["next_revision"])
            self.assertEqual("preview", preview["mutation"])
            self.assertEqual("proposed", service.store.load("claim", record["id"]).record["status"])

    def test_authorized_human_can_accept_with_attributable_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = proposed("decision")
            service = self.make_service(Path(directory), record)
            transition = service.preview(
                "decision", record["id"], "accepted", self.human(), "Tradeoff approved.", DECIDED_AT
            )
            service.apply(transition)
            stored = service.store.load("decision", record["id"]).record
            self.assertEqual("accepted", stored["status"])
            self.assertEqual(2, stored["revision"])
            self.assertEqual("user:owner", stored["authority"]["actor"])
            self.assertEqual("human", stored["authority"]["actor_kind"])
            self.assertEqual(AUTHORITY_CAPABILITY, stored["authority"]["capability"])
            self.assertEqual(1, stored["authority"]["proposal_revision"])

    def test_authorized_human_can_reject_without_deleting_proposal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = proposed("learning")
            service = self.make_service(Path(directory), record)
            transition = service.preview(
                "learning", record["id"], "rejected", self.human(), "Evidence is weak.", DECIDED_AT
            )
            service.apply(transition)
            stored = service.store.load("learning", record["id"]).record
            self.assertEqual("rejected", stored["status"])
            self.assertEqual("Evidence is weak.", stored["authority"]["rationale"])
            self.assertEqual(record["observation"], stored["observation"])

    def test_agents_systems_and_unscoped_humans_cannot_decide(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = proposed("claim")
            service = self.make_service(Path(directory), record)
            principals = (
                Principal("agent:hermes", "agent", frozenset({AUTHORITY_CAPABILITY})),
                Principal("system:ci", "system", frozenset({AUTHORITY_CAPABILITY})),
                Principal("user:viewer", "human", frozenset()),
            )
            for principal in principals:
                with self.subTest(principal=principal.id):
                    with self.assertRaises(AuthorityError) as caught:
                        service.preview(
                            "claim", record["id"], "accepted", principal, "Attempt.", DECIDED_AT
                        )
                    self.assertEqual("ECHEL-AUTHORITY-DENIED", caught.exception.code)
            self.assertEqual("proposed", service.store.load("claim", record["id"]).record["status"])

    def test_stale_parallel_decision_cannot_overwrite_winner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = proposed("claim")
            service = self.make_service(Path(directory), record)
            accepted = service.preview(
                "claim", record["id"], "accepted", self.human(), "Accept.", DECIDED_AT
            )
            rejected = service.preview(
                "claim", record["id"], "rejected", self.human(), "Reject.", DECIDED_AT
            )
            service.apply(accepted)
            with self.assertRaises(RecordConflictError):
                service.apply(rejected)
            self.assertEqual("accepted", service.store.load("claim", record["id"]).record["status"])

    def test_invalid_action_rationale_time_state_and_kind_are_denied(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = proposed("claim")
            service = self.make_service(Path(directory), record)
            cases = (
                ("claim", "deferred", "reason", DECIDED_AT, "ECHEL-AUTHORITY-ACTION-INVALID"),
                ("claim", "accepted", " ", DECIDED_AT, "ECHEL-AUTHORITY-RATIONALE-REQUIRED"),
                ("claim", "accepted", "reason", "yesterday", "ECHEL-AUTHORITY-TIME-INVALID"),
                ("run", "accepted", "reason", DECIDED_AT, "ECHEL-AUTHORITY-KIND-UNSUPPORTED"),
            )
            for record_type, action, rationale, decided_at, code in cases:
                with self.subTest(code=code):
                    with self.assertRaises(AuthorityError) as caught:
                        service.preview(
                            record_type, record["id"], action, self.human(), rationale, decided_at
                        )
                    self.assertEqual(code, caught.exception.code)

    def test_schema_requires_matching_human_authority_for_decided_knowledge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = proposed("claim")
            service = self.make_service(Path(directory), record)
            accepted = deepcopy(record)
            accepted["status"] = "accepted"
            with self.assertRaises(SchemaValidationError):
                service.store.schemas.validate(accepted)
            accepted["authority"] = {
                "action": "rejected",
                "actor": "user:owner",
                "actor_kind": "human",
                "capability": AUTHORITY_CAPABILITY,
                "rationale": "Mismatch",
                "decided_at": DECIDED_AT,
                "proposal_revision": 1,
            }
            with self.assertRaises(SchemaValidationError):
                service.store.schemas.validate(accepted)

    def test_tampered_transition_is_rejected_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = proposed("claim")
            service = self.make_service(Path(directory), record)
            transition = service.preview(
                "claim", record["id"], "accepted", self.human(), "Accept.", DECIDED_AT
            )
            tampered_record = deepcopy(transition.record)
            tampered_record["authority"]["actor_kind"] = "agent"
            tampered = AuthorityTransition(
                tampered_record,
                transition.expectation,
                transition.action,
                transition.actor,
                transition.path,
            )
            with self.assertRaises(AuthorityError) as caught:
                service.apply(tampered)
            self.assertEqual("ECHEL-AUTHORITY-TRANSITION-INVALID", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
