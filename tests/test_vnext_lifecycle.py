from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from echel.architecture import architecture_generate, architecture_status
from echel.canon import canon_generate, canon_status, detect_canon_drift, ensure_canon_files
from echel.config import load_config
from echel.discovery import ensure_discovery_files
from echel.domain import domain_generate, domain_status
from echel.execution import (
    ExecutionTaskSource,
    execution_status,
    execution_tasks_generate,
    render_execution_task,
)
from echel.gates import run_stage_gate
from echel.graph import build_graph, validate_graph
from echel.requirements import ensure_requirements_files, requirements_generate, requirements_status
from echel.repository_factory import repository_factory_generate, repository_factory_status
from echel.strategy import strategy_generate, ensure_strategy_files
from echel.traceability import write_traceability_matrix
from echel.validation import run_validation


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

    def test_architecture_generation_creates_artifacts_and_graph_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)

            changed = architecture_generate(repo, cfg)

            self.assertTrue(changed)
            overview = (repo / "wiki/architecture/overview.md").read_text(encoding="utf-8")
            component = (repo / "wiki/architecture/component-architecture.md").read_text(encoding="utf-8")
            graph = (repo / "wiki/graph.json").read_text(encoding="utf-8")
            manual = (repo / "wiki/graph.manual.json").read_text(encoding="utf-8")
            legacy = (repo / "wiki/architecture.md").read_text(encoding="utf-8")
            self.assertIn("Generated by `echel architecture`", overview)
            self.assertIn("ARCH-901", overview)
            self.assertIn("ADR suggested", overview)
            self.assertIn("future task packets", component)
            self.assertIn("architecture:ARCH-901", graph)
            self.assertIn("preserved_by", manual)
            self.assertIn("Architecture artifact surface", legacy)
            self.assertIn("Graph architecture nodes", architecture_status(repo, cfg))

    def test_architecture_generation_requires_domain_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)
            overview = repo / "wiki/domain/domain-overview.md"
            overview.write_text(overview.read_text(encoding="utf-8").replace("| REQ-101 |", "| REQ-999 |", 1), encoding="utf-8")

            with self.assertRaises(ValueError) as ctx:
                architecture_generate(repo, cfg)

            self.assertIn("domain readiness failed", str(ctx.exception))

    def test_architecture_gate_passes_generated_architecture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)
            architecture_generate(repo, cfg)

            result = run_stage_gate(repo, cfg, "architecture")

            self.assertTrue(result.passed, "\n".join(result.failures))

    def test_architecture_gate_blocks_missing_graph_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)
            architecture_generate(repo, cfg)
            graph = repo / "wiki/graph.manual.json"
            graph.write_text(graph.read_text(encoding="utf-8").replace('"id": "architecture:ARCH-901"', '"id": "architecture:ARCH-999"', 1), encoding="utf-8")

            result = run_stage_gate(repo, cfg, "architecture")

            self.assertFalse(result.passed)
            self.assertIn("ARCH-901 is missing from the product graph", "\n".join(result.failures))

    def test_architecture_gate_blocks_missing_security_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)
            architecture_generate(repo, cfg)
            write(
                repo / "wiki/architecture/security-architecture.md",
                """# Security Architecture

| ID | Boundary | Assets Protected | Threats | Controls | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | Draft |
""",
            )

            result = run_stage_gate(repo, cfg, "architecture")

            self.assertFalse(result.passed)
            self.assertIn("security model is incomplete", "\n".join(result.failures))

    def test_architecture_gate_blocks_unjustified_complexity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)
            architecture_generate(repo, cfg)
            overview = repo / "wiki/architecture/overview.md"
            overview.write_text(
                overview.read_text(encoding="utf-8")
                + "\n\n| ID | Choice | Rationale | Source IDs | Domain Boundaries Preserved | ADR Coverage | Status |\n"
                + "| --- | --- | --- | --- | --- | --- | --- |\n"
                + "| ARCH-099 | Kubernetes microservice deployment | TBD | REQ-101 | BC-201 | TBD | Proposed |\n",
                encoding="utf-8",
            )

            result = run_stage_gate(repo, cfg, "architecture")

            self.assertFalse(result.passed)
            self.assertIn("unjustified complexity risk", "\n".join(result.failures))

    def test_graph_expands_lifecycle_node_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            ensure_discovery_files(repo, cfg)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)
            architecture_generate(repo, cfg)
            write(repo / "generated/product-repository/tests/test_health.py", "def test_health():\n    assert True\n")
            write(repo / "generated/product-repository/.github/workflows/ci.yml", "name: CI\n")
            write(repo / "prompts/playbooks/operate.md", "# Operations Playbook\n")
            write(repo / "wiki/knowledge/contradiction-management.md", "# Contradiction Management\n")

            graph = build_graph(repo, cfg)
            issues = validate_graph(graph)
            nodes = [node for node in graph.get("nodes", []) if isinstance(node, dict)]
            node_types = {node.get("type") for node in nodes}

            self.assertFalse([issue for issue in issues if issue.severity == "critical"])
            for node in nodes:
                with self.subTest(node=node.get("id")):
                    self.assertTrue(node.get("statement_type"))
                    self.assertTrue(node.get("confidence"))
                    self.assertTrue(node.get("source_stage"))
                    self.assertTrue(node.get("verification_status"))
            self.assertTrue(
                {
                    "discovery-item",
                    "assumption",
                    "hypothesis",
                    "buyer",
                    "stakeholder",
                    "business-rule",
                    "strategy",
                    "requirement",
                    "domain-concept",
                    "bounded-context",
                    "architecture-component",
                    "test",
                    "deployment-artifact",
                    "operation-artifact",
                    "contradiction",
                    "learning",
                }.issubset(node_types)
            )

    def test_traceability_matrix_reports_lifecycle_and_broken_chains(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            ensure_discovery_files(repo, cfg)
            write_requirements_sources(repo)
            requirements_generate(repo, cfg, force=True)
            domain_generate(repo, cfg)
            architecture_generate(repo, cfg)
            write(repo / "generated/product-repository/tests/test_health.py", "def test_health():\n    assert True\n")

            report_path = write_traceability_matrix(repo, cfg)
            report = report_path.read_text(encoding="utf-8")

            self.assertEqual(repo / "wiki/reports/traceability-matrix.md", report_path)
            self.assertIn("discovery -> canon -> strategy -> requirement -> domain -> architecture -> task -> test -> evidence", report)
            self.assertIn("| Anchor | Discovery | Canon | Strategy | Requirement | Domain | Architecture | Task | Test | Evidence | Broken Links |", report)
            self.assertIn("REQ-101", report)
            self.assertIn("Missing: Canon", report)
            self.assertIn("Evidence", report)

    def test_validate_command_summarizes_items_and_updates_graph(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write(
                repo / "wiki/validation/test-strategy.md",
                """# Test Strategy

| Validation ID | Scope | Requirement IDs | Task IDs | Domain IDs | Acceptance Criteria | Evidence Target | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TEST-001 | Requirements traceability | REQ-001, NFR-002 | TASK-0033 | DM-012, BC-001 | AC-001 | EVID-VALIDATION-001 | Passing |
| TEST-002 | Evidence readiness | REQ-004 | TASK-0034 | DM-006 | AC-003 | EVID-VALIDATION-002 | Blocked |
""",
            )
            write(
                repo / "wiki/validation/acceptance-tests.md",
                """# Acceptance Tests

| Risk ID | Description | Impact | Owner Task | Status |
| --- | --- | --- | --- | --- |
| VAL-RISK-001 | Evidence is manual. | Release proof is incomplete. | TASK-0034 | Open |

| Blocker ID | Description | Owner Task | Status |
| --- | --- | --- | --- |
| VAL-BLOCK-001 | Validation command missing. | TASK-0033 | Open |
""",
            )
            write(repo / "wiki/validation/validation-report.md", "# Validation Report\n")

            report_path, summary = run_validation(repo, cfg)
            report = report_path.read_text(encoding="utf-8")
            graph = build_graph(repo, cfg)
            node_ids = {node.get("id") for node in graph.get("nodes", []) if isinstance(node, dict)}

            self.assertEqual(repo / "wiki/reports/validation-summary.md", report_path)
            self.assertEqual(summary.passed, 1)
            self.assertEqual(summary.blocked, 2)
            self.assertIn("TEST-001", report)
            self.assertIn("EVID-VALIDATION-001", report)
            self.assertIn("test:TEST-001", node_ids)
            self.assertIn("evidence:EVID-VALIDATION-001", node_ids)

    def test_low_confidence_assumptions_block_graph_validation(self) -> None:
        graph = {
            "version": 1,
            "nodes": [
                {
                    "id": "product:root",
                    "type": "product",
                    "title": "Product",
                    "source": "project.md",
                    "summary": "Product",
                    "statement_type": "decision",
                    "confidence": "high",
                    "source_stage": "product-memory",
                    "verification_status": "accepted",
                },
                {
                    "id": "problem:primary",
                    "type": "problem",
                    "title": "Problem",
                    "source": "problem.md",
                    "summary": "Problem",
                    "statement_type": "observation",
                    "confidence": "high",
                    "source_stage": "discovery",
                    "verification_status": "verified",
                },
                {
                    "id": "user:primary",
                    "type": "user",
                    "title": "User",
                    "source": "users.md",
                    "summary": "User",
                    "statement_type": "observation",
                    "confidence": "medium",
                    "source_stage": "discovery",
                    "verification_status": "active",
                },
                {
                    "id": "solution:primary",
                    "type": "solution",
                    "title": "Solution",
                    "source": "solution.md",
                    "summary": "Solution",
                    "statement_type": "decision",
                    "confidence": "medium",
                    "source_stage": "canon",
                    "verification_status": "accepted",
                },
                {
                    "id": "requirement:primary",
                    "type": "requirement",
                    "title": "Requirement",
                    "source": "scope.md",
                    "summary": "Requirement",
                    "statement_type": "decision",
                    "confidence": "medium",
                    "source_stage": "requirements",
                    "verification_status": "active",
                },
                {
                    "id": "task:TASK-9999",
                    "type": "task",
                    "title": "Task",
                    "source": "work/TASK-9999-test.md",
                    "summary": "Task",
                    "statement_type": "decision",
                    "confidence": "medium",
                    "source_stage": "execution",
                    "verification_status": "active",
                },
                {
                    "id": "assumption:A-999",
                    "type": "assumption",
                    "title": "A-999 risky assumption",
                    "source": "discovery/assumptions.md",
                    "summary": "Low confidence assumption",
                    "trace_id": "A-999",
                    "statement_type": "assumption",
                    "confidence": "low",
                    "source_stage": "discovery",
                    "verification_status": "active",
                },
            ],
            "edges": [
                {"from_id": "task:TASK-9999", "to_id": "requirement:primary", "type": "delivers"},
            ],
        }

        issues = validate_graph(graph)

        self.assertTrue(
            any(
                issue.severity == "critical"
                and "assumption:A-999 has low confidence and is not verified" in issue.message
                for issue in issues
            )
        )

    def test_execution_task_generation_creates_agent_executable_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_execution_phase_sources(repo)

            changed = execution_tasks_generate(repo, cfg, force=True)

            self.assertTrue(changed)
            task = (repo / "wiki/work/TASK-1001-define-task-contract-source-map.md").read_text(encoding="utf-8")
            index = (repo / "wiki/work/TASK_INDEX.md").read_text(encoding="utf-8")
            graph = (repo / "wiki/graph.json").read_text(encoding="utf-8")
            self.assertIn("# TASK-1001 - Define task contract source map", task)
            self.assertIn("## Business Reason", task)
            self.assertIn("## Files to Create", task)
            self.assertIn("## Files to Modify", task)
            self.assertIn("## Validation Command", task)
            self.assertIn("## Rollback Notes", task)
            self.assertIn("## Definition of Done", task)
            self.assertIn("## Out of Scope", task)
            self.assertIn("EP0-001", index)
            self.assertIn("task:TASK-1001", graph)
            self.assertIn("Phase task rows available: 3", execution_status(repo, cfg))

    def test_done_execution_tasks_render_completed_definition_of_done(self) -> None:
        source = ExecutionTaskSource(
            phase_file="phase-1-mvp.md",
            phase_title="Phase 1 MVP",
            phase_task_id="EP1-002",
            title="Add local development docs",
            objective="Document local setup.",
            business_reason="Agents need executable setup guidance.",
            scope="Engineering documentation.",
            dependencies="EP1-001",
            acceptance_criteria="Docs explain setup and verification.",
            tests_required="Documentation review.",
            validation_command="make wiki-health",
            documentation_updates="Update engineering docs.",
            expected_repo_changes="Engineering documentation files.",
            status="Done",
        )

        task = render_execution_task("TASK-1005", source)

        self.assertIn("status: done", task)
        self.assertIn("- [x] TASK-1005 satisfies source phase task EP1-002.", task)

    def test_execution_task_generation_requires_architecture_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_execution_phase_sources(repo)

            with self.assertRaises(ValueError) as ctx:
                execution_tasks_generate(repo, cfg)

            self.assertIn("architecture readiness failed", str(ctx.exception))

    def test_repository_factory_generates_verifiable_skeleton(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_repository_factory_sources(repo)
            execution_tasks_generate(repo, cfg, force=True)

            changed = repository_factory_generate(repo, cfg, force=True)

            root = repo / "generated/product-repository"
            self.assertTrue(changed)
            self.assertTrue((root / "app/main.py").exists())
            self.assertTrue((root / "config/settings.example.json").exists())
            self.assertTrue((root / "tests/test_health.py").exists())
            self.assertTrue((root / ".github/workflows/ci.yml").exists())
            self.assertTrue((root / ".env.example").exists())
            self.assertTrue((root / "docs/engineering/local-development.md").exists())
            self.assertTrue((repo / "wiki/reports/repository-factory/generated-repository.md").exists())
            self.assertIn("Required skeleton files present: 7/7", repository_factory_status(repo, cfg))
            readme = (root / "README.md").read_text(encoding="utf-8")
            verify = (root / "scripts/verify.sh").read_text(encoding="utf-8")
            ci = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
            self.assertIn("python -m compileall -q app tests", readme)
            self.assertIn("python -m unittest discover -s tests", readme)
            self.assertIn("python app/main.py", readme)
            self.assertIn("python -m compileall -q app tests", verify)
            self.assertIn("python -m compileall -q app tests", ci)

            proc = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", str(root / "tests")],
                cwd=repo,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_repository_factory_requires_generated_execution_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)

            with self.assertRaises(ValueError) as ctx:
                repository_factory_generate(repo, cfg, force=True)

            self.assertIn("requires generated execution tasks", str(ctx.exception))

    def test_agent_role_model_has_required_sections(self) -> None:
        method = (ROOT / "docs/development/methodology.md").read_text(encoding="utf-8")
        role_model = (ROOT / "wiki/agents/role-model.md").read_text(encoding="utf-8")

        start = method.index("## AI-Agent Role Model")
        end = method.index("## Execution Safety Rules", start)
        section = method[start:end]

        roles = [
            "Founder Interviewer",
            "Business Analyst",
            "Product Manager",
            "Strategy Analyst",
            "Domain Modeler",
            "Solution Architect",
            "Delivery Planner",
            "Implementation Agent",
            "QA Agent",
            "Security Reviewer",
            "Release Manager",
            "Operations Steward",
            "Governance Auditor",
        ]
        required_subsections = ("Responsibilities", "Inputs", "Outputs", "Forbidden actions")

        for role in roles:
            self.assertIn(role, section, f"role {role} missing from AI-Agent Role Model")
            self.assertIn(role, role_model, f"role {role} missing from product-memory role model")

        for role in roles:
            with self.subTest(role=role):
                role_start = section.index(f"### {role}")
                role_end = section.find("\n### ", role_start + 1)
                role_end = end if role_end == -1 else role_end
                role_block = section[role_start:role_end]
                role_model_start = role_model.index(f"### {role}")
                role_model_end = role_model.find("\n### ", role_model_start + 1)
                role_model_end = len(role_model) if role_model_end == -1 else role_model_end
                role_model_block = role_model[role_model_start:role_model_end]

                for sub in required_subsections:
                    self.assertIn(
                        sub,
                        role_block,
                        f"role {role} is missing required subsection '{sub}'",
                    )
                    self.assertIn(
                        sub,
                        role_model_block,
                        f"role {role} is missing product-memory subsection '{sub}'",
                    )

    def test_canonical_playbooks_are_renderable_and_safe(self) -> None:
        playbook_root = ROOT / "prompts/playbooks"
        playbooks = [
            "discover.md",
            "canon.md",
            "strategy.md",
            "requirements.md",
            "domain.md",
            "architecture.md",
            "roadmap.md",
            "execute.md",
            "validate.md",
            "release.md",
            "operate.md",
            "govern.md",
        ]
        required_sections = [
            "## Objective",
            "## Primary Role",
            "## Required Inputs",
            "## Required Outputs",
            "## Guardrails",
            "## Canonical Prompt",
        ]
        guardrail = "Do not write product implementation code before an approved task packet exists"
        handoff = "Handoff Summary using `wiki/agents/handoff-protocol.md`"

        index = (playbook_root / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Rendering Contract", index)
        self.assertIn("Do not write product implementation code", index)
        self.assertIn("Handoff Summary", index)

        for playbook in playbooks:
            with self.subTest(playbook=playbook):
                text = (playbook_root / playbook).read_text(encoding="utf-8")
                for section in required_sections:
                    self.assertIn(section, text)
                self.assertIn(guardrail, text)
                self.assertIn(handoff, text)

        for tool in ("codex", "claude-code", "cursor"):
            with self.subTest(tool=tool):
                text = (ROOT / f"prompts/{tool}/README.md").read_text(encoding="utf-8")
                self.assertIn("prompts/playbooks/execute.md", text)
                self.assertIn("Do not remove the playbook guardrails", text)
                implement = (ROOT / f"prompts/{tool}/02-implement-task.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn("prompts/playbooks/execute.md", implement)
                self.assertIn("approved `wiki/work/TASK-*.md` task packet", implement)

    def test_agent_handoff_protocol_has_required_fields(self) -> None:
        protocol = (ROOT / "wiki/agents/handoff-protocol.md").read_text(encoding="utf-8")
        methodology = (ROOT / "docs/development/methodology.md").read_text(encoding="utf-8")
        required_fields = [
            "From role",
            "To role",
            "Lifecycle stage",
            "Source artifacts",
            "Changed artifacts",
            "Decision summary",
            "Assumptions",
            "Risks",
            "Unresolved questions",
            "Evidence and verification",
            "Stale or impacted upstream artifacts",
            "Next-stage instructions",
            "Do not proceed if",
        ]

        self.assertIn("# Agent Handoff Protocol", protocol)
        self.assertIn("## Required Handoff Summary", protocol)
        self.assertIn("## Stage Routing", protocol)
        self.assertIn("## Blocking Rules", protocol)
        self.assertIn("## Agent Handoff Protocol", methodology)
        for field in required_fields:
            self.assertIn(field, protocol)
            self.assertIn(field, methodology)


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


def write_execution_phase_sources(repo: Path) -> None:
    write(
        repo / "wiki/execution/phase-0-foundation.md",
        """---
type: execution-phase
status: planned
stage: execution-planning
---
# Phase 0 Foundation

| Phase Task ID | Task | Objective | Business Reason | Scope | Dependencies | Acceptance Criteria | Tests Required | Validation Command | Documentation Updates | Expected Repo Changes | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EP0-001 | Define task contract source map | Identify source fields for generated tasks. | Agents need source-grounded tasks. | Source map for objective, scope, validation, rollback, docs, and DoD. | RM-002, REQ-004 | Source map covers all required fields. | Documentation review | `make wiki-health` | Update execution docs and methodology notes. | No code; execution docs only. | Planned |
| EP0-002 | Define phase handoff rules | State how phase rows become task packets. | Prevents vague backlog lists. | Handoff rules for assumptions, blockers, validation, and owner role. | EP0-001 | Handoff rules reference generated tasks. | Documentation review | `python3 tools/echel.py graph validate` | Update execution docs and state docs. | No code; execution docs only. | Planned |
| EP0-003 | Preserve gate-first validation baseline | Require readiness checks before task generation. | Downstream task generation must not bypass lifecycle gates. | Requirements, domain, architecture, wiki health, graph validation, and unit test expectations. | GATE-REQUIREMENTS, GATE-DOMAIN, GATE-ARCHITECTURE | Future tasks cite validation commands. | Gate command review | `python3 tools/echel.py readiness --stage architecture` | Update quick start if command order changes. | No code; execution docs only. | Planned |
""",
    )


def write_repository_factory_sources(repo: Path) -> None:
    write_execution_phase_sources(repo)
    write(
        repo / "wiki/execution/phase-1-mvp.md",
        """---
type: execution-phase
status: planned
stage: execution-planning
---
# Phase 1 MVP

| Phase Task ID | Task | Objective | Business Reason | Scope | Dependencies | Acceptance Criteria | Tests Required | Validation Command | Documentation Updates | Expected Repo Changes | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EP1-001 | Generate repository skeleton | Create the initial app, config, test, CI, and environment structure from architecture and tasks. | A product-to-repository factory must produce a usable local baseline, not only documents. | App folders, config folders, tests, CI skeleton, env examples, health check stub if applicable. | EP0-001, TASK-0023, TASK-0024 | Generated repo structure matches architecture and can be inspected locally. | Generated-project verification | `python3 tools/echel.py graph validate` | Update roadmap and engineering docs. | New repository skeleton generator outputs. | Planned |
""",
    )


if __name__ == "__main__":
    unittest.main()
