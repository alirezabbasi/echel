from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from echel.canon import canon_generate, canon_status, detect_canon_drift, ensure_canon_files
from echel.config import load_config
from echel.discovery import ensure_discovery_files
from echel.gates import run_stage_gate
from echel.strategy import strategy_generate, ensure_strategy_files


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class VNextLifecycleTests(unittest.TestCase):
    def test_canon_generation_does_not_promote_template_tbd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            ensure_discovery_files(repo, cfg)
            ensure_canon_files(repo, cfg)

            canon_generate(repo, cfg, force=True)

            canon = (repo / "wiki/canon/product-canon.md").read_text(encoding="utf-8")
            self.assertIn("## What This Product Is\n\nTBD", canon)
            self.assertNotIn("This product solves: **Statement type:**", canon)
            self.assertIn("section(s) still TBD", canon_status(repo, cfg))

    def test_strategy_generation_uses_canon_not_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            ensure_strategy_files(repo, cfg)
            write(
                repo / "wiki/canon/product-canon.md",
                """---
type: product-canon
status: draft
stage: canon
---
# Product Canon

## What This Product Is
Canon product truth

## What This Product Is Not
Canon alternative truth

## Why This Product Exists
Canon problem truth

## Who This Product Serves
Canon customer truth

## Why Customers Would Pay or Adopt
Canon buyer truth

## Strategic Risks
Canon risk truth

## Execution Risks
Canon execution risk truth
""",
            )
            write(
                repo / "wiki/canon/vision.md",
                """# Product Vision

## Vision Statement
Canon vision truth

## Business Transformation
Canon success truth
""",
            )
            write(
                repo / "wiki/canon/product-principles.md",
                """# Product Principles

## Principles in Practice
Canon assumption truth
""",
            )
            write(
                repo / "wiki/canon/non-negotiables.md",
                """# Non-Negotiables

## Hard Constraints
Canon constraint truth
""",
            )
            write(
                repo / "wiki/discovery/product-discovery-spec.md",
                """# Product Discovery Specification

## 03 Users
Discovery user truth
""",
            )

            strategy_generate(repo, cfg, force=True)

            icp = (repo / "wiki/strategy/icp.md").read_text(encoding="utf-8")
            self.assertIn("Canon customer truth", icp)
            self.assertNotIn("Discovery user truth", icp)

    def test_canon_drift_creates_artifact_and_stale_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write(
                repo / "wiki/discovery/product-discovery-spec.md",
                """# Product Discovery Specification

## 02 Problem
New discovery problem
""",
            )
            write(
                repo / "wiki/canon/product-canon.md",
                """# Product Canon

## What This Product Is
Old canon problem
""",
            )

            issues = detect_canon_drift(repo, cfg)

            self.assertEqual(len(issues), 1)
            self.assertTrue((repo / "wiki/canon/canon-drift.md").exists())
            canon = (repo / "wiki/canon/product-canon.md").read_text(encoding="utf-8")
            self.assertIn("Stale: discovery field `problem` changed", canon)

    def test_discovery_gate_checks_operator_business_value_and_research_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            ensure_discovery_files(repo, cfg)

            result = run_stage_gate(repo, cfg, "discovery")
            failures = "\n".join(result.failures)

            self.assertIn("operators", failures)
            self.assertIn("business-model", failures)
            self.assertIn("research plan is incomplete", failures)


if __name__ == "__main__":
    unittest.main()
