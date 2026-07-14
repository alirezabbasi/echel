from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
JOURNEY = ROOT / "docs" / "product" / "brownfield-reference-journey.md"


class BrownfieldReferenceJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = JOURNEY.read_text(encoding="utf-8")

    def test_scenario_covers_ingestion_change_and_evolution(self):
        self.assertIn("Status: accepted", self.text)
        self.assertIn("## Scenario and measurable outcome", self.text)
        self.assertIn("inspect the repository without modifying it", self.text)
        self.assertIn("reviewed waitlist increment", self.text)
        self.assertIn("later operational evidence", self.text)

    def test_preflight_is_safe_by_default(self):
        self.assertIn("## Starting inputs and preflight", self.text)
        self.assertIn("local, read-only, offline, and non-executing", self.text)
        self.assertIn("Ingestion never writes to the target repository's source tree", self.text)
        self.assertIn("stops before canonical mutation", self.text)

    def test_observations_inferences_and_approval_are_distinct(self):
        self.assertIn("## Observation, inference, and approval contract", self.text)
        self.assertIn("is an observation citing the migration", self.text)
        self.assertIn("is an inference citing relevant observations", self.text)
        self.assertIn("only through authorized review", self.text)
        self.assertIn("accept, amend, reject, defer, or mark each consequential item disputed", self.text)

    def test_progression_covers_complete_brownfield_path(self):
        self.assertIn("## Progression contract", self.text)
        for step in range(1, 14):
            self.assertIn(f"| {step}.", self.text)
        for phase in ("Classify", "Observe", "Infer", "Approve baseline", "Analyze impact", "Re-ingest and evolve"):
            self.assertIn(phase, self.text)

    def test_failure_paths_cover_security_staleness_and_recovery(self):
        self.assertIn("## Failure, interruption, and recovery paths", self.text)
        for condition in (
            "Symlink or nested repository escapes authorized scope",
            "Secret or personal data is detected",
            "Repository content contains agent instructions",
            "Parser or analyzer fails",
            "Repository changes after task compilation",
            "Verification or migration fails",
        ):
            self.assertIn(condition, self.text)

    def test_incremental_ingestion_preserves_reviewed_knowledge(self):
        self.assertIn("## Incremental evolution rules", self.text)
        self.assertIn("preserves unchanged accepted knowledge", self.text)
        self.assertIn("does not automatically delete product intent", self.text)
        self.assertIn("never resets the baseline", self.text)

    def test_greenfield_and_brownfield_converge(self):
        self.assertIn("## Required decision trail and convergence", self.text)
        self.assertIn("Greenfield and brownfield differ", self.text)
        self.assertIn("same canonical knowledge states", self.text)
        self.assertIn("does not create a separate brownfield domain model", self.text)

    def test_benchmark_measures_quality_not_volume(self):
        self.assertIn("## Benchmark observations", self.text)
        self.assertIn("without setting thresholds before E2-007", self.text)
        self.assertIn("Impact-analysis precision", self.text)
        self.assertIn("More extracted artifacts do not imply better understanding", self.text)


if __name__ == "__main__":
    unittest.main()
