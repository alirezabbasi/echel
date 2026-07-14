from __future__ import annotations

import json
from pathlib import Path
import unittest

from echel.domain import Confidence, DomainValidationError, Identifier, RecordStatus, Revision


ROOT = Path(__file__).resolve().parents[2]


class DomainValueObjectTests(unittest.TestCase):
    def test_identifier_is_typed_immutable_and_round_trips(self) -> None:
        identifier = Identifier("work:E2-012")
        self.assertEqual("work", identifier.namespace)
        self.assertEqual("E2-012", identifier.local)
        self.assertEqual("work:E2-012", str(identifier))
        self.assertEqual(identifier, Identifier(str(identifier)))

    def test_invalid_identifiers_fail_with_stable_error(self) -> None:
        for value in ("", "Claim:one", "missing-colon", "claim:has space", 12):
            with self.subTest(value=value):
                with self.assertRaises(DomainValidationError) as caught:
                    Identifier(value)  # type: ignore[arg-type]
                self.assertEqual("ECHEL-ID-INVALID", caught.exception.code)
                self.assertEqual("id", caught.exception.field)

    def test_revision_rejects_non_positive_non_integer_and_boolean_values(self) -> None:
        self.assertEqual(1, int(Revision(1)))
        for value in (0, -1, 1.5, True, "1"):
            with self.subTest(value=value):
                with self.assertRaises(DomainValidationError) as caught:
                    Revision(value)  # type: ignore[arg-type]
                self.assertEqual("ECHEL-REVISION-INVALID", caught.exception.code)

    def test_confidence_is_normalized_and_bounded(self) -> None:
        self.assertEqual(0.0, float(Confidence(0)))
        self.assertEqual(0.75, float(Confidence(0.75)))
        self.assertEqual(1.0, float(Confidence(1)))
        for value in (-0.01, 1.01, True, "high"):
            with self.subTest(value=value):
                with self.assertRaises(DomainValidationError) as caught:
                    Confidence(value)  # type: ignore[arg-type]
                self.assertEqual("ECHEL-CONFIDENCE-INVALID", caught.exception.code)

    def test_status_is_scoped_to_its_record_lifecycle(self) -> None:
        self.assertEqual("proposed", str(RecordStatus("claim", "proposed")))
        self.assertEqual("running", str(RecordStatus("run", "running")))
        with self.assertRaises(DomainValidationError) as caught:
            RecordStatus("claim", "running")
        self.assertEqual("ECHEL-STATUS-INVALID", caught.exception.code)
        with self.assertRaises(DomainValidationError) as caught:
            RecordStatus("artifact", "created")
        self.assertEqual("ECHEL-STATUS-TYPE-UNKNOWN", caught.exception.code)

    def test_status_vocabulary_accepts_every_status_in_schema_fixtures(self) -> None:
        records = json.loads(
            (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
        )
        checked = 0
        for record in records:
            if "status" in record:
                RecordStatus(record["record_type"], record["status"])
                checked += 1
        self.assertEqual(7, checked)

    def test_status_vocabulary_matches_schema_contract(self) -> None:
        schema = json.loads((ROOT / "schemas" / "v1" / "record.schema.json").read_text())
        definitions = {
            "claim": "claim",
            "decision": "decision",
            "finding": "finding",
            "work_item": "workItem",
            "run": "run",
            "release": "release",
            "learning": "learning",
        }
        for record_type, definition in definitions.items():
            schema_values = schema["$defs"][definition]["properties"]["status"]["enum"]
            self.assertEqual(RecordStatus.ALLOWED[record_type], frozenset(schema_values))

    def test_value_objects_are_hashable_for_relationship_and_index_keys(self) -> None:
        values = {Identifier("claim:one"), Identifier("claim:one"), Identifier("claim:two")}
        self.assertEqual(2, len(values))


if __name__ == "__main__":
    unittest.main()
