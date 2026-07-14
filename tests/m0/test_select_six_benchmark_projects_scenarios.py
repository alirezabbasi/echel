from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ROOT / "benchmarks" / "scenarios"
CONTRACT = ROOT / "docs" / "product" / "benchmark-suite.md"


class BenchmarkSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = CONTRACT.read_text(encoding="utf-8")
        cls.index = json.loads((SCENARIOS / "index.json").read_text(encoding="utf-8"))
        cls.manifests = [
            json.loads((SCENARIOS / name).read_text(encoding="utf-8"))
            for name in cls.index["scenarios"]
        ]

    def test_catalog_has_exactly_three_scenarios_per_entry_mode(self):
        self.assertEqual(len(self.manifests), 6)
        self.assertEqual(sum(item["mode"] == "greenfield" for item in self.manifests), 3)
        self.assertEqual(sum(item["mode"] == "brownfield" for item in self.manifests), 3)
        ids = [item["id"] for item in self.manifests]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, ["GF-01", "GF-02", "GF-03", "BF-01", "BF-02", "BF-03"])

    def test_every_fixture_has_version_authorship_license_and_baseline(self):
        for item in self.manifests:
            with self.subTest(scenario=item["id"]):
                self.assertEqual(item["schema_version"], 1)
                self.assertEqual(item["version"], 1)
                self.assertEqual(item["state"], "selected")
                self.assertEqual(item["authorship"], "Echel-authored synthetic fixture")
                self.assertEqual(item["license"], "Apache-2.0")
                self.assertTrue(item["baseline"])
                self.assertTrue(item["target_outcome"])
                self.assertTrue(item["evaluation_evidence"])
                self.assertTrue(item["materialization"])

    def test_greenfield_baselines_start_only_from_raw_idea(self):
        greenfield = [item for item in self.manifests if item["mode"] == "greenfield"]
        for item in greenfield:
            with self.subTest(scenario=item["id"]):
                self.assertTrue(item["visible_input"]["idea"])
                self.assertEqual(item["baseline"]["initial_canonical_records"], ["idea"])
                self.assertTrue(item["baseline"]["evaluator_only_expected_discoveries"])
                self.assertIsNone(item["materialization"]["content_digest"])

    def test_brownfield_set_is_varied_and_has_ground_truth(self):
        brownfield = [item for item in self.manifests if item["mode"] == "brownfield"]
        shapes = {item["product_shape"] for item in brownfield}
        toolchains = {item["visible_input"]["expected_toolchain"] for item in brownfield}
        self.assertEqual(len(shapes), 3)
        self.assertEqual(len(toolchains), 3)
        self.assertTrue(any("Python" in value for value in toolchains))
        self.assertTrue(any("TypeScript" in value for value in toolchains))
        self.assertTrue(any("Go" in value for value in toolchains))
        for item in brownfield:
            self.assertTrue(item["baseline"]["ground_truth_observations"])
            self.assertTrue(item["baseline"]["reviewable_inferences"])
            self.assertEqual(item["materialization"]["kind"], "synthetic_git_repository")

    def test_selected_state_cannot_be_reported_as_executed_result(self):
        self.assertIn("No performance or release claim may cite a `selected` fixture", self.contract)
        self.assertIn("does not claim unexecuted results", self.contract)
        for item in self.manifests:
            self.assertTrue(all(value is None for key, value in item["materialization"].items() if key != "kind"))

    def test_suite_defines_fair_run_license_and_failure_rules(self):
        for heading in (
            "## Fair-run protocol",
            "## License and data policy",
            "## Selection criteria and rejected alternatives",
            "## Failure and maintenance rules",
        ):
            self.assertIn(heading, self.contract)
        self.assertIn("Evaluator oracle leaks", self.contract)
        self.assertIn("License or provenance is disputed", self.contract)
        self.assertIn("new suite version", self.contract)


if __name__ == "__main__":
    unittest.main()
