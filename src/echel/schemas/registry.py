from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError


SUPPORTED_SCHEMA_VERSIONS = frozenset({1})
ENTITY_DEFINITIONS = {
    "project": "project",
    "claim": "claim",
    "decision": "decision",
    "artifact": "artifact",
    "relationship": "relationship",
    "finding": "finding",
    "work_item": "workItem",
    "task_specification": "taskSpecification",
    "run": "run",
    "evidence": "evidence",
    "release": "release",
    "learning": "learning",
}


@dataclass
class SchemaValidationError(ValueError):
    code: str
    path: str
    detail: str

    def __str__(self) -> str:
        location = self.path or "/"
        return f"{self.code} at {location}: {self.detail}"


class SchemaRegistry:
    """Validate canonical records without coupling storage to entity classes."""

    def __init__(self, schema_root: Path | None = None):
        root = schema_root or Path(__file__).resolve().parent / "v1"
        schema_path = root / "record.schema.json"
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
        except (OSError, json.JSONDecodeError, SchemaError) as exc:
            raise SchemaValidationError("ECHEL-SCHEMA-LOAD", "", str(exc)) from exc
        self.schema_path = schema_path
        self.schema = schema
        self.validators = {
            record_type: Draft202012Validator(
                {
                    "$schema": schema["$schema"],
                    "$ref": f"#/$defs/{definition}",
                    "$defs": schema["$defs"],
                },
                format_checker=FormatChecker(),
            )
            for record_type, definition in ENTITY_DEFINITIONS.items()
        }

    def validate(self, record: dict[str, Any]) -> None:
        version = record.get("schema_version")
        if version not in SUPPORTED_SCHEMA_VERSIONS:
            raise SchemaValidationError(
                "ECHEL-SCHEMA-VERSION-UNSUPPORTED",
                "/schema_version",
                f"supported versions: {sorted(SUPPORTED_SCHEMA_VERSIONS)}; received: {version!r}",
            )
        record_type = record.get("record_type")
        if not isinstance(record_type, str):
            raise SchemaValidationError(
                "ECHEL-RECORD-TYPE-UNKNOWN", "/record_type", "record_type must be a string"
            )
        validator = self.validators.get(record_type)
        if validator is None:
            raise SchemaValidationError(
                "ECHEL-RECORD-TYPE-UNKNOWN",
                "/record_type",
                f"known types: {sorted(self.validators)}; received: {record_type!r}",
            )
        errors = sorted(validator.iter_errors(record), key=self._error_key)
        if errors:
            raise self._validation_error(errors[0])
        for field in ("created_at", "updated_at"):
            try:
                datetime.fromisoformat(record[field].replace("Z", "+00:00"))
            except (AttributeError, ValueError) as exc:
                raise SchemaValidationError(
                    "ECHEL-SCHEMA-INVALID", f"/{field}", "must be an RFC 3339 date-time"
                ) from exc

    @staticmethod
    def _error_key(error: ValidationError) -> tuple[str, str]:
        return ("/".join(str(part) for part in error.absolute_path), error.message)

    @staticmethod
    def _validation_error(error: ValidationError) -> SchemaValidationError:
        path = "/" + "/".join(str(part) for part in error.absolute_path)
        return SchemaValidationError("ECHEL-SCHEMA-INVALID", path.rstrip("/"), error.message)
