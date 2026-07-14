from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "quality.yml"
QUALITY = ROOT / "docs" / "contributing" / "quality.md"
MAKEFILE = ROOT / "Makefile"
PYPROJECT = ROOT / "pyproject.toml"


class CiQualityBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.quality = QUALITY.read_text(encoding="utf-8")
        cls.makefile = MAKEFILE.read_text(encoding="utf-8")
        cls.pyproject = PYPROJECT.read_text(encoding="utf-8")

    def test_workflow_has_all_required_jobs(self):
        for job in ("unit", "scenarios", "typing", "lint", "packaging", "security", "dependency-review", "baseline"):
            self.assertRegex(self.workflow, rf"(?m)^  {re.escape(job)}:$")
        self.assertIn("needs: [unit, scenarios, typing, lint, packaging, security]", self.workflow)
        self.assertIn('result != "success"', self.workflow)

    def test_supported_python_matrix_is_explicit(self):
        matrix = 'python-version: ["3.11", "3.12", "3.13", "3.14"]'
        self.assertEqual(self.workflow.count(matrix), 2)
        for version in ("3.11", "3.12", "3.13", "3.14"):
            self.assertIn(version, self.quality)
        self.assertIn('requires-python = ">=3.11"', self.pyproject)

    def test_ci_uses_least_privilege_and_bounded_jobs(self):
        self.assertIn("permissions:\n  contents: read", self.workflow)
        self.assertGreaterEqual(self.workflow.count("persist-credentials: false"), 7)
        self.assertGreaterEqual(self.workflow.count("timeout-minutes:"), 8)
        self.assertNotIn("contents: write", self.workflow)
        self.assertNotIn("pull-requests: write", self.workflow)
        self.assertIn("cancel-in-progress: true", self.workflow)

    def test_local_targets_match_ci_commands(self):
        for target in ("unit", "scenarios", "typing", "lint", "package-check", "security", "verify", "quality"):
            self.assertRegex(self.makefile, rf"(?m)^{re.escape(target)}:")
        for command in ("make unit", "make scenarios", "make typing", "make lint", "make package-check", "make security"):
            self.assertIn(command, self.workflow)

    def test_typing_lint_packaging_and_security_tools_are_declared(self):
        for tool in ("bandit", "build", "mypy", "ruff", "twine"):
            self.assertIn(f'"{tool}', self.pyproject)
        self.assertIn("[tool.mypy]", self.pyproject)
        self.assertIn("[tool.ruff]", self.pyproject)
        self.assertIn("[tool.bandit]", self.pyproject)
        self.assertIn("clean wheel install", self.quality)

    def test_failure_skip_and_external_authority_are_documented(self):
        for phrase in (
            "Required job is skipped",
            "skipped is not success",
            "CI and local results disagree",
            "Retries do not erase failures",
            "does not prove product correctness",
            "does not mutate repository settings",
        ):
            self.assertIn(phrase, self.quality)

    def test_workflow_does_not_publish_or_deploy(self):
        self.assertNotIn("permissions: write-all", self.workflow)
        self.assertNotRegex(self.workflow, r"(?m)^\s*(publish|deploy|release):")
        self.assertIn("Pull requests never execute deployment or release behavior", self.quality)


if __name__ == "__main__":
    unittest.main()
