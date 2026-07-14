from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "docs" / "product" / "evaluation-metrics.md"
CATALOG = ROOT / "benchmarks" / "metrics" / "v1.json"


class EvaluationMetricSpecificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SPEC.read_text(encoding="utf-8")
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.metrics = {item["id"]: item for item in cls.catalog["metrics"]}

    def test_required_metric_families_are_machine_readable(self):
        self.assertIn("Status: accepted", self.text)
        self.assertEqual(self.catalog["status"], "accepted")
        categories = {item["category"] for item in self.metrics.values()}
        self.assertEqual(categories, {"context", "task", "rework", "onboarding", "evidence"})
        for metric_id in (
            "CTX-PRECISION",
            "CTX-RECALL",
            "TASK-FIRST-PASS",
            "TASK-SUCCESS",
            "REWORK-RATE",
            "ONBOARD-TIME",
            "ONBOARD-NEXT",
            "EVID-COVERAGE",
            "EVID-REPRO",
            "EVID-PROVENANCE",
        ):
            self.assertIn(metric_id, self.metrics)

    def test_ratio_metrics_define_reproducible_terms(self):
        for metric_id, metric in self.metrics.items():
            if metric["unit"] != "ratio":
                continue
            with self.subTest(metric=metric_id):
                self.assertTrue(metric["numerator"])
                self.assertTrue(metric["denominator"])
                self.assertIn(metric["direction"], {"higher", "lower"})
        self.assertEqual(self.catalog["zero_denominator"], "not_applicable")

    def test_thresholds_are_preregistered_but_not_claimed_as_results(self):
        self.assertIn("Thresholds in version 1 are provisional engineering targets", self.text)
        self.assertIn("not evidence that Echel already achieves them", self.text)
        self.assertEqual(self.metrics["CTX-PROTECTED"]["threshold"]["value"], 1.0)
        self.assertEqual(self.metrics["TASK-FIRST-PASS"]["threshold"]["value"], 0.70)
        self.assertIsNone(self.metrics["REWORK-CHURN"]["threshold"])

    def test_safety_and_evidence_gates_cannot_be_traded(self):
        for metric_id in ("CTX-PROTECTED", "CTX-BUDGET", "EVID-COVERAGE", "EVID-PROVENANCE"):
            self.assertTrue(self.metrics[metric_id]["gate"])
        self.assertIn("fails the affected run and release safety gate", self.text)
        self.assertIn("There is no composite “Echel score.”", self.text)
        self.assertIsNone(self.catalog["composite_score"])

    def test_human_labels_have_blind_review_and_agreement_rules(self):
        labeling = self.catalog["human_labeling"]
        self.assertEqual(labeling["independent_reviewers"], 2)
        self.assertTrue(labeling["adjudicator_on_disagreement"])
        self.assertEqual(labeling["minimum_cohens_kappa"], 0.70)
        self.assertIn("blinded to runtime/model identity", self.text)
        self.assertIn("original labels remain available", self.text)

    def test_failures_invalid_runs_and_missing_values_are_distinct(self):
        self.assertIn("## Invalid, interrupted, and missing data", self.text)
        self.assertIn("Invalid; exclude from metric denominator", self.text)
        self.assertIn("Eligible task failure", self.text)
        self.assertIn("Not applicable; never coerce to zero or one", self.text)
        self.assertIn("Post-hoc exclusions based on result quality are prohibited", self.text)

    def test_aggregation_is_scenario_balanced_and_reproducible(self):
        self.assertEqual(
            self.catalog["suite_aggregation"],
            "macro_average_scenario_values_with_equal_greenfield_brownfield_weight",
        )
        self.assertEqual(self.catalog["comparative_repetitions"], 5)
        self.assertEqual(self.catalog["confidence_interval"], "bootstrap_95_percent")
        self.assertIn("Report greenfield and brownfield results separately", self.text)
        self.assertIn("Every published result includes", self.text)


if __name__ == "__main__":
    unittest.main()
