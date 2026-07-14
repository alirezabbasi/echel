from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONTRIBUTING = ROOT / "CONTRIBUTING.md"
WORKFLOW = ROOT / "docs" / "contributing" / "task-workflow.md"
TEMPLATE = ROOT / "docs" / "contributing" / "task-packet-template.md"
PULL_REQUEST = ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"


class ContributionWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contributing = CONTRIBUTING.read_text(encoding="utf-8")
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.template = TEMPLATE.read_text(encoding="utf-8")
        cls.pull_request = PULL_REQUEST.read_text(encoding="utf-8")

    def test_public_entrypoint_does_not_depend_on_private_workspace(self):
        self.assertIn("private `echelit/` planning workspace is intentionally ignored", self.contributing)
        self.assertIn("public contributors must not depend on files unavailable", self.workflow)
        self.assertIn("task-packet workflow", self.contributing)
        self.assertIn("task-packet template", self.contributing)

    def test_workflow_covers_selection_execution_verification_and_review(self):
        for heading in (
            "## 1. Propose or select",
            "## 2. Prepare and preview",
            "## 3. Execute",
            "## 4. Verify",
            "## 5. Handoff and review",
            "## 6. Commit and integration",
        ):
            self.assertIn(heading, self.workflow)
        self.assertIn("A one-line title", self.workflow)
        self.assertIn("acceptance-condition-to-evidence mapping", self.workflow)

    def test_states_have_entry_exit_and_authority_rules(self):
        self.assertIn("## Workflow states", self.workflow)
        for state in ("Proposed", "Planned", "Ready", "In progress", "Review", "Changes requested", "Blocked", "Done"):
            self.assertIn(f"| {state} |", self.workflow)
        self.assertIn("every other state transition is an attributable decision", self.workflow)
        self.assertIn("Self-review does not satisfy", self.workflow)

    def test_template_is_complete_execution_contract(self):
        for heading in (
            "## Control",
            "## Objective",
            "## Rationale and source",
            "## Scope",
            "## Out of scope",
            "## Inputs and constraints",
            "## Implementation approach",
            "## Acceptance criteria",
            "## Verification",
            "## Hermes execution contract",
            "## Risks and rollback",
            "## Knowledge updates",
            "## Evidence and handoff",
        ):
            self.assertIn(heading, self.template)
        self.assertIn("Start revision", self.template)
        self.assertIn("token/cost/time budgets", self.template)

    def test_denial_interruption_staleness_and_recovery_are_defined(self):
        self.assertIn("## Interruption, denial, and recovery", self.workflow)
        for condition in (
            "Dependency or source revision changed",
            "Required permission is denied",
            "Tool/runtime is interrupted",
            "Verification fails",
            "Contributor becomes unavailable",
        ):
            self.assertIn(condition, self.workflow)
        self.assertIn("without deleting evidence or accepted history", self.workflow)

    def test_pull_request_template_requires_evidence_and_boundaries(self):
        for heading in ("## Task", "## Outcome", "## Acceptance and evidence", "## Boundaries and risk", "## Knowledge and handoff"):
            self.assertIn(heading, self.pull_request)
        self.assertIn("make verify", self.pull_request)
        self.assertIn("External effects and approvals", self.pull_request)
        self.assertIn("separated findings/proposals", self.pull_request)

    def test_git_and_external_actions_are_not_implicitly_authorized(self):
        self.assertIn("Push, merge, release, deployment", self.workflow)
        self.assertIn("occur only when requested or explicitly part", self.workflow)
        self.assertIn("A merge is not automatically a task acceptance", self.workflow)


if __name__ == "__main__":
    unittest.main()
