from __future__ import annotations

from dataclasses import dataclass
import re
from typing import ClassVar


_IDENTIFIER_PATTERN = re.compile(
    r"^(?P<namespace>[a-z][a-z0-9_-]*):(?P<local>[A-Za-z0-9][A-Za-z0-9._-]*)$"
)


@dataclass
class DomainValidationError(ValueError):
    """A stable domain-boundary failure suitable for machine and human callers."""

    code: str
    field: str
    detail: str

    def __str__(self) -> str:
        return f"{self.code} at /{self.field}: {self.detail}"


@dataclass(frozen=True, order=True)
class Identifier:
    """A stable, typed reference in ``namespace:local`` form."""

    value: str
    namespace: str
    local: str

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise DomainValidationError("ECHEL-ID-INVALID", "id", "must be a string")
        match = _IDENTIFIER_PATTERN.fullmatch(value)
        if match is None or len(value) > 160:
            raise DomainValidationError(
                "ECHEL-ID-INVALID",
                "id",
                "must match namespace:local, begin with a lowercase namespace, and be at most 160 characters",
            )
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "namespace", match.group("namespace"))
        object.__setattr__(self, "local", match.group("local"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, order=True)
class Revision:
    """A positive canonical-record revision."""

    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int) or self.value < 1:
            raise DomainValidationError(
                "ECHEL-REVISION-INVALID", "revision", "must be an integer greater than or equal to 1"
            )

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True, order=True)
class Confidence:
    """A normalized confidence score; it is evidence metadata, not authority."""

    value: float

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise DomainValidationError(
                "ECHEL-CONFIDENCE-INVALID", "confidence", "must be a number from 0 through 1"
            )
        normalized = float(self.value)
        if not 0 <= normalized <= 1:
            raise DomainValidationError(
                "ECHEL-CONFIDENCE-INVALID", "confidence", "must be a number from 0 through 1"
            )
        object.__setattr__(self, "value", normalized)

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True, order=True)
class RecordStatus:
    """A status validated within the lifecycle vocabulary of one record type."""

    ALLOWED: ClassVar[dict[str, frozenset[str]]] = {
        "claim": frozenset({"proposed", "accepted", "rejected", "superseded"}),
        "decision": frozenset({"proposed", "accepted", "rejected", "superseded"}),
        "finding": frozenset({"open", "accepted", "resolved", "dismissed"}),
        "work_item": frozenset(
            {"planned", "ready", "in_progress", "review", "done", "blocked", "cancelled"}
        ),
        "run": frozenset({"created", "running", "cancelled", "failed", "succeeded"}),
        "release": frozenset({"planned", "candidate", "released", "withdrawn"}),
        "learning": frozenset({"proposed", "accepted", "rejected", "applied"}),
    }

    record_type: str
    value: str

    def __post_init__(self) -> None:
        allowed = self.ALLOWED.get(self.record_type)
        if allowed is None:
            raise DomainValidationError(
                "ECHEL-STATUS-TYPE-UNKNOWN",
                "record_type",
                f"status is not defined for record type {self.record_type!r}",
            )
        if self.value not in allowed:
            raise DomainValidationError(
                "ECHEL-STATUS-INVALID",
                "status",
                f"allowed for {self.record_type}: {', '.join(sorted(allowed))}",
            )

    def __str__(self) -> str:
        return self.value
