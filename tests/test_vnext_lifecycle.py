from pathlib import Path
import hashlib
import json
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
from echel.evidence import register_evidence, validate_links, validate_registry
from echel.execution import (
    ExecutionTaskSource,
    execution_status,
    execution_tasks_generate,
    render_execution_task,
)
from echel.gates import run_stage_gate
from echel.graph import build_graph, validate_graph
from echel.learning import ensure_learning_files, record_learning
from echel.platform.cockpit import cockpit_snapshot, run_cockpit_command
from echel.requirements import ensure_requirements_files, requirements_generate, requirements_status
from echel.repository_factory import repository_factory_generate, repository_factory_status
from echel.strategy import strategy_generate, ensure_strategy_files
from echel.traceability import traceability_matrix_report, write_traceability_matrix
from echel.validation import run_validation


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class VNextLifecycleTests(unittest.TestCase):
    def test_cockpit_snapshot_exposes_lifecycle_stage_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            snapshot = cockpit_snapshot(repo)

            lifecycle = snapshot["lifecycle"]
            stage_ids = [stage["id"] for stage in lifecycle["stages"]]

            self.assertEqual(
                stage_ids,
                [
                    "discovery",
                    "canon",
                    "strategy",
                    "requirements",
                    "domain",
                    "architecture",
                    "roadmap",
                    "execution",
                    "build",
                    "validate",
                    "release",
                    "operate",
                    "governance",
                ],
            )
            self.assertIn(lifecycle["current"]["id"], stage_ids)
            for stage in lifecycle["stages"]:
                self.assertIn("role", stage)
                self.assertIn("blockers", stage)
                self.assertIn("next_action", stage)
                self.assertIn("safe_action", stage)
                self.assertIn("safe_actions", stage)

    def test_cockpit_lifecycle_exposes_guided_stage_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            snapshot = cockpit_snapshot(repo)

            actions_by_stage = {
                stage["id"]: {action["action"] for action in stage["safe_actions"]}
                for stage in snapshot["lifecycle"]["stages"]
            }

            self.assertIn("discover", actions_by_stage["discovery"])
            self.assertIn("canon", actions_by_stage["canon"])
            self.assertIn("strategy-readiness", actions_by_stage["strategy"])
            self.assertIn("requirements", actions_by_stage["requirements"])
            self.assertIn("domain", actions_by_stage["domain"])
            self.assertIn("architecture", actions_by_stage["architecture"])
            self.assertIn("execution-tasks", actions_by_stage["roadmap"])
            self.assertIn("packet", actions_by_stage["execution"])
            self.assertIn("build", actions_by_stage["build"])
            self.assertIn("validate", actions_by_stage["validate"])
            self.assertIn("evidence-add", actions_by_stage["validate"])
            self.assertIn("proof-pack", actions_by_stage["release"])
            self.assertIn("learning-add", actions_by_stage["operate"])
            self.assertIn("traceability", actions_by_stage["governance"])

    def test_cockpit_readiness_command_accepts_stage_argument(self) -> None:
        result = run_cockpit_command(ROOT, "readiness", {"stage": "discovery"})

        self.assertIn("GATE-DISCOVERY", result.output)
        self.assertIn(result.code, {0, 1})

    def test_cockpit_guided_command_validates_required_arguments(self) -> None:
        result = run_cockpit_command(ROOT, "evidence-add", {"subject": "TASK-0040"})

        self.assertFalse(result.ok)
        self.assertEqual(result.code, 2)
        self.assertIn("evidence add requires", result.output)

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
            write(repo / "wiki/deployment/deployment-architecture.md", "# Deployment Architecture\n\n## Purpose\n\nDeployment path.")
            write(repo / "prompts/playbooks/operate.md", "# Operations Playbook\n")
            write(repo / "wiki/operations/runbook.md", "# Runbook\n\n## Purpose\n\nSupport operations guide.")
            write(repo / "prompts/playbooks/govern.md", "# Governance Playbook\n")
            write(repo / "wiki/governance/documentation-governance.md", "# Documentation Governance\n\n## Purpose\n\nGovernance guide.")
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
            deployment_sources = {node.get("source") for node in nodes if node.get("type") == "deployment-artifact"}
            self.assertIn("deployment/deployment-architecture.md", deployment_sources)
            operation_sources = {node.get("source") for node in nodes if node.get("type") == "operation-artifact"}
            self.assertIn("operations/runbook.md", operation_sources)
            governance_sources = {node.get("source") for node in nodes if node.get("type") == "governance-artifact"}
            self.assertIn("governance/documentation-governance.md", governance_sources)
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
                    "governance-artifact",
                    "contradiction",
                    "learning",
                }.issubset(node_types)
            )

    def test_governance_docs_define_source_truth_duplication_and_deprecation(self) -> None:
        root = ROOT / "wiki" / "governance"
        expected = [
            "documentation-governance.md",
            "architecture-governance.md",
            "adr-process.md",
            "traceability-model.md",
            "quality-gates.md",
            "repository-integrity-audit.md",
        ]

        for name in expected:
            with self.subTest(name=name):
                self.assertTrue((root / name).exists())

        documentation = (root / "documentation-governance.md").read_text(encoding="utf-8")
        self.assertIn("## Source Of Truth Hierarchy", documentation)
        self.assertIn("## Duplication Rules", documentation)
        self.assertIn("## Deprecation Process", documentation)
        audit = (root / "repository-integrity-audit.md").read_text(encoding="utf-8")
        for phrase in ["Missing docs", "Stale docs", "Broken traceability", "Missing ADRs", "Missing tests", "Missing evidence", "Methodology violations"]:
            self.assertIn(phrase, audit)

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

    def test_traceability_does_not_count_planned_evidence_targets_as_registered_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            graph = {
                "version": 1,
                "nodes": [
                    {
                        "id": "requirement:REQ-001",
                        "type": "requirement",
                        "title": "Requirement",
                        "source": "requirements/product-requirements.md",
                        "trace_id": "REQ-001",
                        "source_stage": "requirements",
                    },
                    {
                        "id": "evidence:EVID-VALIDATION-001",
                        "type": "evidence",
                        "title": "EVID-VALIDATION-001",
                        "source": "validation/validation-report.md",
                        "trace_id": "EVID-VALIDATION-001",
                        "source_stage": "validation",
                        "verification_status": "planned",
                    },
                ],
                "edges": [{"from_id": "evidence:EVID-VALIDATION-001", "to_id": "requirement:REQ-001", "type": "evidence_for"}],
            }

            report = traceability_matrix_report(repo, cfg, graph=graph)

            self.assertIn("| Evidence | 0 | 0 | 0% |", report)
            self.assertIn("Missing: Discovery, Canon, Strategy, Domain, Architecture, Task, Test, Evidence", report)

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

    def test_evidence_registration_records_required_fields_and_satisfies_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            proof = repo / "wiki/reports/proof.md"
            write(proof, "proof artifact\n")
            task = repo / "wiki/work/TASK-9000-proof.md"
            write(task, "# TASK-9000\n\n## Evidence\n\nEVID-VALIDATION-001\n")

            evid, record = register_evidence(
                repo,
                cfg,
                evidence_id="EVID-VALIDATION-001",
                subject="TASK-9000",
                kind="validation-report",
                path="wiki/reports/proof.md",
                producer="QA Agent",
                summary="Proof that validation ran.",
            )
            registry = (repo / ".echel/evidence_registry.json").read_text(encoding="utf-8")
            graph = build_graph(repo, cfg)
            node_ids = {node.get("id") for node in graph.get("nodes", []) if isinstance(node, dict)}

            self.assertEqual("EVID-VALIDATION-001", evid)
            self.assertEqual("TASK-9000", record["subject"])
            self.assertEqual("validation-report", record["kind"])
            self.assertEqual("wiki/reports/proof.md", record["path"])
            self.assertEqual("QA Agent", record["producer"])
            self.assertEqual("Proof that validation ran.", record["summary"])
            self.assertEqual(
                "sha256:" + hashlib.sha256(b"proof artifact\n").hexdigest(),
                record["checksum"],
            )
            loaded_registry = json.loads(registry)
            self.assertEqual([], validate_registry(loaded_registry, "registry"))
            self.assertEqual([], validate_links([task], loaded_registry))
            self.assertIn("evidence:EVID-VALIDATION-001", node_ids)

    def test_release_gate_passes_with_validation_deployment_evidence_and_accepted_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_release_gate_sources(repo, checklist_status="Passed")
            proof = repo / "wiki/reports/proof.md"
            write(proof, "release proof\n")
            register_evidence(
                repo,
                cfg,
                evidence_id="EVID-RELEASE-001",
                subject="release",
                kind="release-proof",
                path="wiki/reports/proof.md",
                producer="QA Agent",
                summary="Release proof artifact.",
            )

            result = run_stage_gate(repo, cfg, "release")

            self.assertTrue(result.passed, "\n".join(result.failures))

    def test_release_gate_blocks_pending_checklist_and_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            write_release_gate_sources(repo, checklist_status="Pending")

            result = run_stage_gate(repo, cfg, "release")
            failures = "\n".join(result.failures)

            self.assertFalse(result.passed)
            self.assertIn("production checklist is not passed", failures)
            self.assertIn("release evidence is missing", failures)

    def test_learning_loop_routes_post_release_signals_to_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cfg = load_config(repo)
            ensure_learning_files(repo, cfg)
            actions = ["task", "adr", "risk", "assumption", "strategy-change"]
            results = [
                record_learning(
                    repo,
                    cfg,
                    source_kind="incident" if action != "strategy-change" else "strategy-change",
                    title=f"{action} follow up",
                    summary=f"Route {action} into product memory.",
                    action=action,
                    owner="Operations Steward",
                    severity="medium",
                )
                for action in actions
            ]

            records = (repo / "wiki/operations/learning-records.md").read_text(encoding="utf-8")
            self.assertIn("LEARN-001", records)
            self.assertIn("LEARN-005", records)
            self.assertTrue(any(path.name.startswith("TASK-2001") for path in (repo / "wiki/work").glob("TASK-*.md")))
            self.assertTrue(any(path.name.startswith("ADR-0006") for path in (repo / "wiki/decisions").glob("ADR-*.md")))
            self.assertIn("risk follow up", (repo / "wiki/risks.md").read_text(encoding="utf-8"))
            self.assertIn("A-001", (repo / "wiki/discovery/assumptions.md").read_text(encoding="utf-8"))
            self.assertIn("strategy-change follow up", (repo / "wiki/operations/strategy-change-log.md").read_text(encoding="utf-8"))

            graph = build_graph(repo, cfg)
            learning_nodes = {node.get("trace_id") for node in graph.get("nodes", []) if node.get("type") == "learning"}
            self.assertIn(results[0].learning_id, learning_nodes)

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


def write_release_gate_sources(repo: Path, checklist_status: str = "Passed") -> None:
    write(repo / "wiki/validation/validation-report.md", "# Validation Report\n")
    write(repo / "wiki/reports/validation-summary.md", "# Validation Summary\n")
    write(
        repo / "wiki/validation/security-tests.md",
        """# Security Tests

## Security Blockers

- No open security blockers.
""",
    )
    write(
        repo / "wiki/risks.md",
        """# Risks

## Release Risk

- Impact: Release could proceed without proof.
- Mitigation: Release gate requires evidence and checklist approval.
""",
    )
    write(
        repo / "wiki/deployment/deployment-architecture.md",
        "# Deployment Architecture\n\n## Deployment Path\n\nLocal release candidate is promoted after validation and evidence registration.\n",
    )
    write(
        repo / "wiki/deployment/environments.md",
        "# Environments\n\n| ID | Environment | Purpose | Status |\n| --- | --- | --- | --- |\n| ENV-001 | Local | Release verification | Active |\n",
    )
    write(
        repo / "wiki/deployment/release-process.md",
        "# Release Process\n\n| Step | Owner Role | Required Action | Evidence | Gate Behavior |\n| --- | --- | --- | --- | --- |\n| REL-PROC-001 | Release Manager | Verify release candidate. | Evidence registry | Block on missing proof. |\n",
    )
    write(
        repo / "wiki/deployment/rollback-plan.md",
        "# Rollback Plan\n\n| ID | Failure Mode | Detection Signal | Rollback Action | Data Handling | Owner | Status |\n| --- | --- | --- | --- | --- | --- | --- |\n| RB-001 | Release command fails | Gate output | Restore previous commit | Preserve evidence | Release Manager | Draft |\n",
    )
    write(
        repo / "wiki/deployment/secrets-management.md",
        "# Secrets Management\n\n| ID | Secret Class | Examples | Allowed Storage | Prohibited Storage | Owner | Status |\n| --- | --- | --- | --- | --- | --- | --- |\n| SEC-DEP-001 | Provider credentials | API keys | Environment | Repository | Security Reviewer | Draft |\n",
    )
    write(
        repo / "wiki/deployment/production-checklist.md",
        f"""# Production Checklist

| ID | Area | Check | Required Evidence | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| PROD-001 | Validation | Validation report exists. | wiki/validation/validation-report.md | QA Agent | {checklist_status} |
| PROD-002 | Evidence | Release proof is registered. | EVID-### | QA Agent | {checklist_status} |
| PROD-003 | Deployment | Deployment path is documented. | deployment-architecture.md | Release Manager | {checklist_status} |
| PROD-004 | Rollback | Rollback is documented. | rollback-plan.md | Release Manager | {checklist_status} |
| PROD-005 | Secrets | Secrets strategy exists. | secrets-management.md | Security Reviewer | {checklist_status} |
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
