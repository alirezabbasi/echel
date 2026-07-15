from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from echel.relationships import (
    RelationshipError,
    RelationshipService,
    RelationshipTransition,
)
from echel.schemas import SchemaValidationError
from echel.storage import CanonicalRecordStore, CanonicalRepository, RecordConflictError, RecordExpectation


ROOT = Path(__file__).resolve().parents[2]
VALID_RECORDS = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)
CREATED_AT = "2026-07-15T02:00:00Z"
PROVENANCE = {"actor": "agent:analyst", "origin": "run:impact", "method": "inference"}


class ExplicitRelationshipTests(unittest.TestCase):
    def make_service(self, workspace: Path) -> RelationshipService:
        (workspace / ".git").mkdir()
        store = CanonicalRecordStore(CanonicalRepository.create(workspace))
        for record_type in ("project", "claim", "artifact"):
            record = deepcopy(
                next(item for item in VALID_RECORDS if item["record_type"] == record_type)
            )
            store.write(record, RecordExpectation.absent())
        return RelationshipService(store)

    def preview(self, service: RelationshipService):
        return service.preview(
            "relationship:need-project",
            "claim:need",
            "informs",
            "project:demo",
            "The need explains the project's purpose.",
            PROVENANCE,
            CREATED_AT,
        )

    def test_preview_validates_and_explains_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            transition = self.preview(service)
            explanation = transition.to_dict()
            self.assertEqual("claim", explanation["source_type"])
            self.assertEqual("project", explanation["target_type"])
            self.assertEqual("core/v1", explanation["policy"])
            self.assertEqual("preview", explanation["mutation"])
            self.assertFalse(Path(transition.path).exists())

    def test_apply_persists_justified_provenanced_policy_checked_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            service.apply(self.preview(service))
            stored = service.store.load(
                "relationship", "relationship:need-project"
            ).record
            self.assertEqual("The need explains the project's purpose.", stored["reason"])
            self.assertEqual("core/v1", stored["policy"])
            self.assertEqual(PROVENANCE, stored["provenance"])
            self.assertEqual(1, stored["revision"])

    def test_missing_invalid_and_unsupported_endpoints_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            cases = (
                ("claim:missing", "ECHEL-RELATIONSHIP-ENDPOINT-NOT-FOUND"),
                ("not-an-id", "ECHEL-RELATIONSHIP-ENDPOINT-INVALID"),
                ("runtime:hermes", "ECHEL-RELATIONSHIP-ENDPOINT-INVALID"),
            )
            for source, code in cases:
                with self.subTest(source=source):
                    with self.assertRaises(RelationshipError) as caught:
                        service.preview(
                            "relationship:test",
                            source,
                            "informs",
                            "project:demo",
                            "Reason.",
                            PROVENANCE,
                            CREATED_AT,
                        )
                    self.assertEqual(code, caught.exception.code)

    def test_unknown_predicate_and_invalid_direction_are_denied_by_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            cases = (
                ("claim:need", "related_to", "project:demo"),
                ("project:demo", "informs", "claim:need"),
            )
            for source, predicate, target in cases:
                with self.subTest(predicate=predicate, source=source):
                    with self.assertRaises(RelationshipError) as caught:
                        service.preview(
                            "relationship:test",
                            source,
                            predicate,
                            target,
                            "Reason.",
                            PROVENANCE,
                            CREATED_AT,
                        )
                    self.assertEqual("ECHEL-RELATIONSHIP-POLICY-DENIED", caught.exception.code)

    def test_blank_reason_and_self_link_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            with self.assertRaises(RelationshipError) as blank:
                service.preview(
                    "relationship:test", "claim:need", "informs", "project:demo", " ", PROVENANCE, CREATED_AT
                )
            self.assertEqual("ECHEL-RELATIONSHIP-REASON-REQUIRED", blank.exception.code)
            with self.assertRaises(RelationshipError) as self_link:
                service.preview(
                    "relationship:test", "claim:need", "informs", "claim:need", "Reason.", PROVENANCE, CREATED_AT
                )
            self.assertEqual("ECHEL-RELATIONSHIP-SELF-LINK", self_link.exception.code)

    def test_invalid_provenance_and_time_fail_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            with self.assertRaises(SchemaValidationError):
                service.preview(
                    "relationship:test", "claim:need", "informs", "project:demo", "Reason.", {}, CREATED_AT
                )
            with self.assertRaises(RelationshipError) as caught:
                service.preview(
                    "relationship:test", "claim:need", "informs", "project:demo", "Reason.", PROVENANCE, "today"
                )
            self.assertEqual("ECHEL-RELATIONSHIP-TIME-INVALID", caught.exception.code)

    def test_parallel_creation_cannot_overwrite_winner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            first = self.preview(service)
            second = service.preview(
                "relationship:need-project",
                "claim:need",
                "informs",
                "project:demo",
                "A concurrent but different rationale.",
                PROVENANCE,
                CREATED_AT,
            )
            service.apply(first)
            with self.assertRaises(RecordConflictError):
                service.apply(second)

    def test_tampered_policy_and_endpoint_removal_fail_safely(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            transition = self.preview(service)
            tampered_record = deepcopy(transition.record)
            tampered_record["policy"] = "extension/unreviewed"
            tampered = RelationshipTransition(
                tampered_record,
                transition.expectation,
                transition.source_type,
                transition.target_type,
                transition.path,
            )
            with self.assertRaises(RelationshipError) as caught:
                service.apply(tampered)
            self.assertEqual("ECHEL-RELATIONSHIP-TRANSITION-INVALID", caught.exception.code)

            service.store.load("claim", "claim:need").path.unlink()
            with self.assertRaises(RelationshipError) as missing:
                service.apply(transition)
            self.assertEqual("ECHEL-RELATIONSHIP-ENDPOINT-NOT-FOUND", missing.exception.code)
            self.assertFalse(Path(transition.path).exists())


if __name__ == "__main__":
    unittest.main()
