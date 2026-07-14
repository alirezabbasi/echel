from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "docs" / "product" / "responsibility-matrix.md"


class ResponsibilityMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = MATRIX.read_text(encoding="utf-8")
        cls.capabilities = re.findall(
            r"^\| (CAP-[A-Z-]+) \| ([^|]+?) \| ([^|]+?) \|",
            cls.text,
            flags=re.MULTILINE,
        )

    def test_every_critical_capability_has_one_owner(self):
        self.assertIn("Status: accepted", self.text)
        self.assertGreaterEqual(len(self.capabilities), 30)
        ids = [capability_id for capability_id, _, _ in self.capabilities]
        self.assertEqual(len(ids), len(set(ids)))
        allowed_owners = {
            "Echel",
            "Hermes",
            "Git",
            "CI",
            "Authorized human",
            "Executing tool",
            "Configured artifact authority",
            "Deployment system",
            "Secret provider",
            "Telemetry system",
        }
        for capability_id, owner, state in self.capabilities:
            with self.subTest(capability=capability_id):
                self.assertIn(owner.strip(), allowed_owners)
                self.assertTrue(state.strip())

    def test_core_authority_is_not_split(self):
        expected = {
            "CAP-KNOWLEDGE": "Echel",
            "CAP-KNOWLEDGE-ACCEPT": "Authorized human",
            "CAP-REPOSITORY-REVISION": "Git",
            "CAP-TASK": "Echel",
            "CAP-CONTEXT": "Echel",
            "CAP-MODEL": "Hermes",
            "CAP-SESSION": "Hermes",
            "CAP-BUILD": "CI",
            "CAP-DEPLOY": "Deployment system",
            "CAP-TELEMETRY": "Telemetry system",
        }
        actual = {capability_id: owner.strip() for capability_id, owner, _ in self.capabilities}
        for capability_id, owner in expected.items():
            self.assertEqual(actual.get(capability_id), owner)

    def test_runtime_boundary_is_explicit_and_portable(self):
        self.assertIn("## Boundary interaction contracts", self.text)
        self.assertIn("### Echel to runtime", self.text)
        self.assertIn("versioned runtime protocol", self.text)
        self.assertIn("Runtime-specific prompts", self.text)
        self.assertIn("Another conforming runtime can replace it", self.text)

    def test_git_ci_and_deployment_keep_raw_system_authority(self):
        self.assertIn("Git remains authoritative for file and revision state", self.text)
        self.assertIn("CI owns execution and raw status", self.text)
        self.assertIn("deployment system owns execution and environment state", self.text)
        self.assertIn("A green CI check is evidence, not automatic product acceptance", self.text)

    def test_human_accountability_cannot_be_impersonated(self):
        self.assertIn("## Decision accountability", self.text)
        self.assertIn("No agent, model, analyzer, CI result, score, or policy engine", self.text)
        self.assertIn("pre-authorize low-risk decisions through explicit policy", self.text)

    def test_conflicts_preserve_each_authority(self):
        self.assertIn("## Denial, interruption, and conflict handling", self.text)
        for condition in (
            "Hermes lacks a requested capability",
            "Task or repository revision is stale",
            "Local result and CI result disagree",
            "Echel record and Git disagree about a commit",
            "Deployment reports failure despite release approval",
            "Owner is unavailable",
        ):
            self.assertIn(condition, self.text)

    def test_extensions_cannot_introduce_owner_gaps(self):
        self.assertIn("## Extension rule", self.text)
        self.assertIn("exactly one authoritative owner", self.text)
        self.assertIn("no owner, multiple owners, implicit authority transfer", self.text)


if __name__ == "__main__":
    unittest.main()
