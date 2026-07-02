from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from echel.canon import canon_generate, canon_status, detect_canon_drift, ensure_canon_files
from echel.config import load_config
from echel.discovery import ensure_discovery_files
from echel.domain import domain_generate, domain_status
from echel.gates import run_stage_gate
from echel.requirements import ensure_requirements_files, requirements_generate, requirements_status
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

    def test_requirements_generation_marks_phase_and_adds_graph_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)

            changed = requirements_generate(repo, cfg, force=True)

            self.assertTrue(changed)
            product = (repo / "wiki/requirements/product-requirements.md").read_text(encoding="utf-8")
            functional = (repo / "wiki/requirements/functional-requirements.md").read_text(encoding="utf-8")
            graph = (repo / "wiki/graph.json").read_text(encoding="utf-8")
            manual = (repo / "wiki/graph.manual.json").read_text(encoding="utf-8")
            self.assertIn("REQ-101", product)
            self.assertIn("| P0 | MVP |", product)
            self.assertIn("REQ-104", functional)
            self.assertIn("| P1 | V1 |", functional)
            self.assertIn("requirement:REQ-101", graph)
            self.assertIn("trace:ICP-001", manual)
            self.assertIn("Graph requirement nodes", requirements_status(repo, cfg))

    def test_requirements_generation_rejects_vague_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo, canon_is="The best platform for modern seamless operations.")

            with self.assertRaises(ValueError) as ctx:
                requirements_generate(repo, cfg, force=True)

            self.assertIn("too vague", str(ctx.exception))
            self.assertIn("best platform", str(ctx.exception))

    def test_requirements_gate_passes_generated_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)

            result = run_stage_gate(repo, cfg, "requirements")

            self.assertTrue(result.passed, "\n".join(result.failures))

    def test_requirements_gate_blocks_missing_generated_graph_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            (repo / "wiki/graph.manual.json").unlink()

            result = run_stage_gate(repo, cfg, "requirements")

            self.assertFalse(result.passed)
            self.assertIn("REQ-101 is missing from the product graph", "\n".join(result.failures))

    def test_requirements_gate_blocks_missing_acceptance_criteria(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            ac_path = repo / "wiki/requirements/acceptance-criteria.md"
            ac_path.write_text(ac_path.read_text(encoding="utf-8").replace("| AC-101 |", "| AC-999 |", 1), encoding="utf-8")

            result = run_stage_gate(repo, cfg, "requirements")

            self.assertFalse(result.passed)
            self.assertIn("REQ-101 references missing acceptance criteria", "\n".join(result.failures))

    def test_domain_generation_creates_domain_artifacts_and_graph_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)

            changed = domain_generate(repo, cfg)

            self.assertTrue(changed)
            overview = (repo / "wiki/domain/domain-overview.md").read_text(encoding="utf-8")
            graph = (repo / "wiki/graph.json").read_text(encoding="utf-8")
            manual = (repo / "wiki/graph.manual.json").read_text(encoding="utf-8")
            self.assertIn("Generated by `echel domain`", overview)
            self.assertIn("REQ-101", overview)
            self.assertIn("DM-201", overview)
            self.assertIn("domain-concept:DM-201", graph)
            self.assertIn("bounded-context:BC-201", graph)
            self.assertIn("business-rule:BR-201", manual)
            self.assertIn("Graph domain nodes", domain_status(repo, cfg))

    def test_domain_generation_requires_requirements_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            ensure_requirements_files(repo, cfg)

            with self.assertRaises(ValueError) as ctx:
                domain_generate(repo, cfg)

            self.assertIn("requirements readiness failed", str(ctx.exception))

    def test_domain_gate_passes_generated_domain_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)

            result = run_stage_gate(repo, cfg, "domain")

            self.assertTrue(result.passed, "\n".join(result.failures))

    def test_domain_gate_blocks_unmapped_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)
            overview = repo / "wiki/domain/domain-overview.md"
            overview.write_text(overview.read_text(encoding="utf-8").replace("| REQ-101 |", "| REQ-999 |", 1), encoding="utf-8")

            result = run_stage_gate(repo, cfg, "domain")

            self.assertFalse(result.passed)
            self.assertIn("REQ-101 is not mapped", "\n".join(result.failures))

    def test_domain_gate_blocks_undefined_domain_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)
            language = repo / "wiki/domain/ubiquitous-language.md"
            language.write_text(language.read_text(encoding="utf-8").replace("BC-201", "BC-999", 1), encoding="utf-8")

            result = run_stage_gate(repo, cfg, "domain")

            self.assertFalse(result.passed)
            self.assertIn("BC-999 is referenced", "\n".join(result.failures))

    def test_domain_gate_blocks_duplicate_meaning_and_technology_leakage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)
            language = repo / "wiki/domain/ubiquitous-language.md"
            text = language.read_text(encoding="utf-8")
            text = text.replace(
                "| DM-201 | Non Negotiables Concept | Domain concept derived from `NFR-101`: Non-Negotiables. | Concept | NFR-101 | BC-201, BR-201 | Generated |",
                "| DM-201 | Non Negotiables Concept | Domain concept derived from `NFR-101`: Non-Negotiables. | Concept | NFR-101 | BC-201, BR-201 | Generated |\n"
                "| DM-999 | Non Negotiables Concept | A PostgreSQL table for storing workflow records. | Concept | REQ-101 | DM-201 | Draft |",
            )
            language.write_text(text, encoding="utf-8")

            result = run_stage_gate(repo, cfg, "domain")
            failures = "\n".join(result.failures)

            self.assertFalse(result.passed)
            self.assertIn("Non Negotiables Concept has duplicate meanings", failures)
            self.assertIn("technology leakage", failures)


def write_requirements_sources(repo: Path, canon_is: str = "A workflow control product for regulated operators.") -> None:
    write(
        repo / "wiki/canon/product-canon.md",
        f"""---
type: product-canon
status: draft
stage: canon
---
# Product Canon

## What This Product Is
{canon_is}

## What This Product Is Not
Consumer social network and general-purpose marketplace.

## Who This Product Serves
Operations teams at regulated B2B companies.

## Why Customers Would Pay or Adopt
Customers pay to reduce manual handoffs and preserve audit-ready operational memory.
""",
    )
    write(
        repo / "wiki/canon/vision.md",
        """# Product Vision

## Business Transformation
Teams can turn repeated operational work into auditable, AI-assisted delivery flows.
""",
    )
    write(
        repo / "wiki/canon/product-principles.md",
        """# Product Principles

## Principles in Practice
Evidence before automation and explicit source memory before execution.
""",
    )
    write(
        repo / "wiki/canon/non-negotiables.md",
        """# Non-Negotiables

## Hard Constraints
Audit trails must preserve source decisions before downstream implementation.
""",
    )
    write(
        repo / "wiki/strategy/icp.md",
        """# Ideal Customer Profile

## Primary ICP
Mid-market regulated operations teams with repeated approval workflows.
""",
    )
    write(
        repo / "wiki/strategy/buyer-user-model.md",
        """# Buyer and User Model

## Economic Buyer
Operations leader accountable for audit cost and delivery throughput.

## User
Operations specialist who executes repeated handoff workflows.

## Operator
Platform owner responsible for workflow reliability and access control.
""",
    )
    write(
        repo / "wiki/strategy/market-wedge.md",
        """# Market Wedge

## Wedge Definition
First wedge is approval-heavy operational workflows with audit evidence gaps.
""",
    )
    write(
        repo / "wiki/strategy/positioning.md",
        """# Positioning

## Positioning Statement
For regulated operations teams, the product preserves operational memory while coordinating AI-assisted delivery.
""",
    )
    write(
        repo / "wiki/strategy/pricing-and-packaging.md",
        """# Pricing and Packaging

## Pricing Model
Subscription pricing based on active workflows and retained audit history.
""",
    )
    write(
        repo / "wiki/strategy/pmf-evidence.md",
        """# PMF Evidence

## Continue Criteria
Teams complete repeated workflows faster while retaining audit evidence.

## Stop Criteria
Users cannot connect workflow memory to execution decisions.
""",
    )


if __name__ == "__main__":
    unittest.main()
