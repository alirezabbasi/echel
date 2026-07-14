from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from echel.schemas import ENTITY_DEFINITIONS, SchemaRegistry, SchemaValidationError


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "schemas" / "v1" / "fixtures"


class CoreSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = SchemaRegistry()
        cls.valid = json.loads((FIXTURES / "valid-records.json").read_text())
        cls.invalid = json.loads((FIXTURES / "invalid-records.json").read_text())

    def test_schema_is_valid_draft_2020_12(self) -> None:
        Draft202012Validator.check_schema(self.registry.schema)

    def test_fixture_covers_and_validates_every_core_entity(self) -> None:
        self.assertEqual(set(ENTITY_DEFINITIONS), {r["record_type"] for r in self.valid})
        self.assertEqual(12, len(self.valid))
        for record in self.valid:
            with self.subTest(record_type=record["record_type"]):
                self.registry.validate(record)
                for field in ("id", "revision", "created_at", "updated_at", "provenance"):
                    self.assertIn(field, record)

    def test_invalid_fixtures_return_stable_error_codes(self) -> None:
        for fixture in self.invalid:
            with self.subTest(name=fixture["name"]):
                with self.assertRaises(SchemaValidationError) as caught:
                    self.registry.validate(fixture["record"])
                self.assertEqual(fixture["expected_code"], caught.exception.code)

    def test_namespaced_extension_round_trips_without_interpretation(self) -> None:
        record = deepcopy(self.valid[0])
        value = {"nested": [1, True, {"future": "value"}]}
        record["extensions"] = {"dev.example.future": value}
        self.registry.validate(record)
        decoded = json.loads(json.dumps(record))
        self.assertEqual(value, decoded["extensions"]["dev.example.future"])

    def test_unknown_top_level_data_is_rejected(self) -> None:
        record = deepcopy(self.valid[0])
        record["future"] = True
        with self.assertRaisesRegex(SchemaValidationError, "ECHEL-SCHEMA-INVALID"):
            self.registry.validate(record)

    def test_formats_and_immutable_task_revision_are_enforced(self) -> None:
        bad_time = deepcopy(self.valid[0])
        bad_time["created_at"] = "yesterday"
        with self.assertRaises(SchemaValidationError):
            self.registry.validate(bad_time)
        task = deepcopy(next(r for r in self.valid if r["record_type"] == "task_specification"))
        task["revision"] = 2
        with self.assertRaises(SchemaValidationError):
            self.registry.validate(task)

    def test_contract_defines_no_silent_defaults(self) -> None:
        def has_default(value: object) -> bool:
            if isinstance(value, dict):
                return "default" in value or any(has_default(item) for item in value.values())
            if isinstance(value, list):
                return any(has_default(item) for item in value)
            return False

        self.assertFalse(has_default(self.registry.schema))


if __name__ == "__main__":
    unittest.main()
