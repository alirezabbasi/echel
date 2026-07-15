from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from echel.authority import Principal
from echel.methodology.lifecycle import STAGES
from echel.storage import CanonicalRecordStore, RecordExpectation, RecordWritePlan


PROFILE_CAPABILITY = "profile:change"


@dataclass
class ProfileError(RuntimeError):
    code: str
    field: str
    detail: str

    def __str__(self) -> str:
        return f"{self.code} at /{self.field}: {self.detail}"


@dataclass(frozen=True)
class ProfilePolicy:
    id: str
    level: int
    additions: tuple[tuple[str, tuple[str, ...]], ...]
    assurance: str

    def additions_for(self, stage: str) -> tuple[str, ...]:
        return next((kinds for stage_id, kinds in self.additions if stage_id == stage), ())

    def required_for(self, stage: str, base: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(dict.fromkeys((*base, *self.additions_for(stage))))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "level": self.level,
            "assurance": self.assurance,
            "stage_additions": {stage: list(kinds) for stage, kinds in self.additions},
            "certification": False,
        }


PROFILES = {
    "prototype": ProfilePolicy(
        "prototype",
        0,
        (),
        "Validate the idea with the base lifecycle and minimal irreversible commitment.",
    ),
    "product": ProfilePolicy(
        "product",
        1,
        (
            ("vision", ("non-goal",)),
            ("requirements", ("acceptance",)),
            ("architecture", ("constraint",)),
            ("validation", ("test-evidence",)),
        ),
        "Add explicit scope, acceptance, constraints, and product validation.",
    ),
    "production": ProfilePolicy(
        "production",
        2,
        (
            ("vision", ("non-goal",)),
            ("requirements", ("acceptance",)),
            ("architecture", ("constraint", "security")),
            ("validation", ("test-evidence",)),
            ("deployment", ("rollback", "owner")),
            ("operations", ("observability", "incident-response")),
        ),
        "Add security, ownership, rollback, observability, and incident readiness.",
    ),
    "regulated": ProfilePolicy(
        "regulated",
        3,
        (
            ("problem", ("data-classification",)),
            ("vision", ("non-goal",)),
            ("requirements", ("acceptance", "traceability")),
            ("architecture", ("constraint", "security", "threat-model")),
            ("validation", ("test-evidence", "audit-evidence")),
            ("deployment", ("rollback", "owner", "approval")),
            ("operations", ("observability", "incident-response", "retention")),
        ),
        "Add a generic governance evidence floor without asserting certification.",
    ),
}


def get_profile(profile_id: str) -> ProfilePolicy:
    try:
        return PROFILES[profile_id]
    except KeyError as exc:
        raise ProfileError(
            "ECHEL-PROFILE-UNKNOWN",
            "profile",
            f"known profiles: {sorted(PROFILES)}; received {profile_id!r}",
        ) from exc


@dataclass(frozen=True)
class ProfileInspection:
    project_id: str
    selected: str
    policy: ProfilePolicy
    requirements: tuple[tuple[str, tuple[str, ...]], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "selected": self.selected,
            "policy": self.policy.to_dict(),
            "requirements": {stage: list(kinds) for stage, kinds in self.requirements},
        }


@dataclass(frozen=True)
class ProfileTransition:
    record: dict[str, Any]
    expectation: RecordExpectation
    actor: str
    inspection: ProfileInspection

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.record["id"],
            "from": self.inspection.selected,
            "to": self.record["profile"],
            "next_revision": self.record["revision"],
            "actor": self.actor,
            "policy": get_profile(str(self.record["profile"])).to_dict(),
            "mutation": "preview",
        }


class ProfileService:
    """Inspect and explicitly select risk-proportional lifecycle policy."""

    def __init__(self, store: CanonicalRecordStore):
        self.store = store

    def inspect(self, project_id: str) -> ProfileInspection:
        project = self.store.load("project", project_id).record
        policy = get_profile(str(project["profile"]))
        requirements = tuple(
            (stage.id, policy.required_for(stage.id, stage.required_kinds)) for stage in STAGES
        )
        return ProfileInspection(project_id, policy.id, policy, requirements)

    def preview_change(
        self,
        project_id: str,
        target: str,
        principal: Principal,
        rationale: str,
        decided_at: str,
    ) -> ProfileTransition:
        if principal.kind != "human" or PROFILE_CAPABILITY not in principal.capabilities:
            raise ProfileError(
                "ECHEL-PROFILE-AUTHORITY-DENIED",
                "principal",
                "an authorized human with profile:change capability is required",
            )
        policy = get_profile(target)
        if not rationale.strip():
            raise ProfileError(
                "ECHEL-PROFILE-RATIONALE-REQUIRED", "rationale", "must not be empty"
            )
        self._validate_time(decided_at)
        inspection = self.inspect(project_id)
        if inspection.selected == target:
            raise ProfileError(
                "ECHEL-PROFILE-UNCHANGED", "profile", "target profile is already selected"
            )
        loaded = self.store.load("project", project_id)
        updated = deepcopy(loaded.record)
        updated["profile"] = policy.id
        updated["revision"] = loaded.record["revision"] + 1
        updated["updated_at"] = decided_at
        updated["profile_transition"] = {
            "actor": principal.id,
            "actor_kind": "human",
            "capability": PROFILE_CAPABILITY,
            "from": inspection.selected,
            "to": policy.id,
            "rationale": rationale.strip(),
            "decided_at": decided_at,
            "project_revision": loaded.record["revision"],
        }
        self.store.preview_write(updated, loaded.expectation)
        return ProfileTransition(updated, loaded.expectation, principal.id, inspection)

    def apply_change(self, transition: ProfileTransition) -> RecordWritePlan:
        evidence = transition.record.get("profile_transition")
        if (
            not isinstance(evidence, dict)
            or evidence.get("actor") != transition.actor
            or evidence.get("actor_kind") != "human"
            or evidence.get("capability") != PROFILE_CAPABILITY
            or evidence.get("from") != transition.inspection.selected
            or evidence.get("to") != transition.record.get("profile")
            or evidence.get("project_revision") != transition.expectation.revision
        ):
            raise ProfileError(
                "ECHEL-PROFILE-TRANSITION-INVALID",
                "transition",
                "profile evidence does not match the previewed transition",
            )
        return self.store.write(transition.record, transition.expectation)

    @staticmethod
    def _validate_time(value: str) -> None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise ProfileError(
                "ECHEL-PROFILE-TIME-INVALID", "decided_at", "must be an RFC 3339 date-time"
            ) from exc
        if parsed.tzinfo is None:
            raise ProfileError(
                "ECHEL-PROFILE-TIME-INVALID", "decided_at", "must include a timezone"
            )
