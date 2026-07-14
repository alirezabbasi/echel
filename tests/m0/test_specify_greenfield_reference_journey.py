from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
JOURNEY = ROOT / "docs" / "product" / "greenfield-reference-journey.md"


class GreenfieldReferenceJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = JOURNEY.read_text(encoding="utf-8")

    def test_scenario_has_bounded_input_and_measurable_outcome(self):
        self.assertIn("## Scenario and measurable outcome", self.text)
        self.assertIn("## Starting inputs", self.text)
        self.assertIn("running, verified MVP increment", self.text)
        self.assertIn("correct Echel outcome may be to stop", self.text)

    def test_progression_records_inputs_decisions_outputs_and_evidence(self):
        self.assertIn("## Progression contract", self.text)
        for column in (
            "Minimum input",
            "Material decision",
            "Canonical knowledge created or revised",
            "Exit evidence",
        ):
            self.assertIn(column, self.text)
        for step in range(1, 14):
            self.assertIn(f"| {step}.", self.text)

    def test_journey_is_progressive_not_document_first(self):
        self.assertIn("smallest next question", self.text)
        self.assertIn("Missing optional inputs remain unknown", self.text)
        self.assertIn("no future-stage skeletons", self.text)
        self.assertIn("low-risk experiments may begin", self.text)

    def test_authority_and_traceability_remain_separated(self):
        self.assertIn("## Actors and authority", self.text)
        self.assertIn("Cannot turn runtime output or memory into accepted product knowledge", self.text)
        self.assertIn("## Required decision trail", self.text)
        self.assertIn("Every connection must state why it exists", self.text)

    def test_failure_paths_cover_validation_denial_interruption_and_recovery(self):
        self.assertIn("## Failure, interruption, and recovery paths", self.text)
        for condition in (
            "Idea is vague or solution-first",
            "Hermes is interrupted or times out",
            "Tool permission is denied",
            "Verification fails",
            "Repository or knowledge revision is stale",
            "Secret or sensitive value is supplied",
        ):
            self.assertIn(condition, self.text)

    def test_benchmark_uses_observations_without_premature_thresholds(self):
        self.assertIn("## Benchmark observations", self.text)
        self.assertIn("without inventing target thresholds before E2-007", self.text)
        self.assertIn("Context precision", self.text)
        self.assertIn("Task acceptance on first review", self.text)
        self.assertIn("Artifact count is a diagnostic", self.text)

    def test_journey_does_not_freeze_implementation_design(self):
        self.assertIn("## Non-goals", self.text)
        for excluded in (
            "screen design",
            "storage schemas",
            "programming language",
            "model provider",
            "fixed agent personas",
        ):
            self.assertIn(excluded, self.text)


if __name__ == "__main__":
    unittest.main()
