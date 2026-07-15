from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from echel.authority import AUTHORITY_CAPABILITY, KnowledgeAuthorityService, Principal
from echel.lifecycle import LifecycleService
from echel.methodology.lifecycle import STAGES
from echel.profiles import PROFILE_CAPABILITY, PROFILES, ProfileError, ProfileService
from echel.schemas import SchemaValidationError
from echel.storage import CanonicalRecordStore, CanonicalRepository, RecordConflictError, RecordExpectation


ROOT = Path(__file__).resolve().parents[2]
VALID_RECORDS = json.loads(
    (ROOT / "schemas" / "v1" / "fixtures" / "valid-records.json").read_text()
)
T1 = "2026-07-15T05:00:00Z"
T2 = "2026-07-15T05:01:00Z"


class LifecycleProfileTests(unittest.TestCase):
    def make_service(self, workspace: Path) -> ProfileService:
        (workspace / ".git").mkdir()
        store = CanonicalRecordStore(CanonicalRepository.create(workspace))
        project = deepcopy(next(item for item in VALID_RECORDS if item["record_type"] == "project"))
        store.write(project, RecordExpectation.absent())
        return ProfileService(store)

    @staticmethod
    def human() -> Principal:
        return Principal("user:owner", "human", frozenset({PROFILE_CAPABILITY}))

    def add_accepted_claim(self, store: CanonicalRecordStore, record_id: str, kind: str) -> None:
        claim = deepcopy(next(item for item in VALID_RECORDS if item["record_type"] == "claim"))
        claim["id"] = record_id
        claim["kind"] = kind
        claim["stage"] = "problem"
        store.write(claim, RecordExpectation.absent())
        authority = KnowledgeAuthorityService(store)
        principal = Principal("user:owner", "human", frozenset({AUTHORITY_CAPABILITY}))
        authority.apply(
            authority.preview(
                "claim", record_id, "accepted", principal, "Profile evidence accepted.", T1
            )
        )

    def test_all_profiles_use_same_stages_with_distinct_inspectable_minimums(self) -> None:
        stage_ids = [stage.id for stage in STAGES]
        self.assertEqual(
            ["prototype", "product", "production", "regulated"], list(PROFILES)
        )
        requirements = {}
        for profile_id, policy in PROFILES.items():
            effective = {
                stage.id: policy.required_for(stage.id, stage.required_kinds) for stage in STAGES
            }
            self.assertEqual(stage_ids, list(effective))
            self.assertFalse(policy.to_dict()["certification"])
            requirements[profile_id] = effective
        self.assertEqual(("architecture",), requirements["prototype"]["architecture"])
        self.assertIn("constraint", requirements["product"]["architecture"])
        self.assertIn("security", requirements["production"]["architecture"])
        self.assertIn("threat-model", requirements["regulated"]["architecture"])

    def test_inspection_explains_selected_policy_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            project_before = deepcopy(service.store.load("project", "project:demo").record)
            inspection = service.inspect("project:demo").to_dict()
            self.assertEqual("prototype", inspection["selected"])
            self.assertEqual(["problem", "user"], inspection["requirements"]["problem"])
            self.assertEqual(project_before, service.store.load("project", "project:demo").record)

    def test_profile_change_is_previewed_attributable_and_concurrent_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            transition = service.preview_change(
                "project:demo", "production", self.human(), "Preparing for live operation.", T1
            )
            self.assertEqual("prototype", transition.to_dict()["from"])
            self.assertEqual("production", transition.to_dict()["to"])
            self.assertEqual("prototype", service.store.load("project", "project:demo").record["profile"])
            competing = service.preview_change(
                "project:demo", "regulated", self.human(), "Additional governance needed.", T1
            )
            service.apply_change(transition)
            with self.assertRaises(RecordConflictError):
                service.apply_change(competing)
            stored = service.store.load("project", "project:demo").record
            self.assertEqual("production", stored["profile"])
            self.assertEqual("user:owner", stored["profile_transition"]["actor"])

    def test_profile_changes_policy_not_flow_or_existing_knowledge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            for record_id, kind in (("claim:problem", "problem"), ("claim:user", "user")):
                self.add_accepted_claim(service.store, record_id, kind)
            claims_before = tuple(
                deepcopy(loaded.record) for loaded in service.store.scan("claim")
            )
            baseline = LifecycleService(service.store).assess("project:demo")
            self.assertTrue(baseline.usable)
            transition = service.preview_change(
                "project:demo", "regulated", self.human(), "Generic governance floor required.", T2
            )
            service.apply_change(transition)
            assessed = LifecycleService(service.store).assess("project:demo")
            self.assertEqual("problem", assessed.current)
            self.assertEqual("vision", assessed.next)
            self.assertEqual("regulated", assessed.profile)
            self.assertEqual(("data-classification",), assessed.missing_kinds)
            self.assertEqual(
                claims_before, tuple(loaded.record for loaded in service.store.scan("claim"))
            )

    def test_agent_unscoped_human_unknown_and_unchanged_changes_are_denied(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            principals = (
                Principal("agent:hermes", "agent", frozenset({PROFILE_CAPABILITY})),
                Principal("user:viewer", "human", frozenset()),
            )
            for principal in principals:
                with self.subTest(principal=principal.id):
                    with self.assertRaises(ProfileError) as caught:
                        service.preview_change(
                            "project:demo", "product", principal, "Attempt.", T1
                        )
                    self.assertEqual("ECHEL-PROFILE-AUTHORITY-DENIED", caught.exception.code)
            with self.assertRaises(ProfileError) as unknown:
                service.preview_change(
                    "project:demo", "certified", self.human(), "Attempt.", T1
                )
            self.assertEqual("ECHEL-PROFILE-UNKNOWN", unknown.exception.code)
            with self.assertRaises(ProfileError) as unchanged:
                service.preview_change(
                    "project:demo", "prototype", self.human(), "No change.", T1
                )
            self.assertEqual("ECHEL-PROFILE-UNCHANGED", unchanged.exception.code)

    def test_tampered_transition_and_invalid_time_fail_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            with self.assertRaises(ProfileError) as invalid_time:
                service.preview_change(
                    "project:demo", "product", self.human(), "Change.", "tomorrow"
                )
            self.assertEqual("ECHEL-PROFILE-TIME-INVALID", invalid_time.exception.code)
            transition = service.preview_change(
                "project:demo", "product", self.human(), "Change.", T1
            )
            transition.record["profile_transition"]["actor_kind"] = "agent"
            with self.assertRaises(ProfileError) as tampered:
                service.apply_change(transition)
            self.assertEqual("ECHEL-PROFILE-TRANSITION-INVALID", tampered.exception.code)
            self.assertEqual("prototype", service.store.load("project", "project:demo").record["profile"])

    def test_project_schema_requires_known_profile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(Path(directory))
            project = deepcopy(service.store.load("project", "project:demo").record)
            project.pop("profile")
            with self.assertRaises(SchemaValidationError):
                service.store.schemas.validate(project)
            project["profile"] = "certified"
            with self.assertRaises(SchemaValidationError):
                service.store.schemas.validate(project)


if __name__ == "__main__":
    unittest.main()
