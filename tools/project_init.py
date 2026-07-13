#!/usr/bin/env python3
import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

CORE_ITEMS = [
    "assets",
    "docs",
    "prompts",
    "raw",
    "schema",
    "tools",
    "LICENSE",
    "ruleset.md",
    "README.md",
    "Makefile",
    "project.echel",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Project/workspace name")
    parser.add_argument("--mode", choices=["scratch", "existing"], required=True)
    parser.add_argument("--source", help="Path to existing codebase (required for existing mode)")
    parser.add_argument("--problem", default="", help="Initial product problem statement")
    parser.add_argument("--solution", default="", help="Initial intended solution")
    parser.add_argument("--direction", default="", help="Initial product direction")
    parser.add_argument("--users", default="", help="Initial target users")
    parser.add_argument("--buyers", default="", help="Initial buyers or approvers")
    parser.add_argument("--operators", default="", help="Initial operators or support owners")
    parser.add_argument("--mvp", default="", help="Initial MVP scope")
    parser.add_argument("--business-model", default="", help="Initial business model or value model")
    parser.add_argument("--non-goals", default="", help="Initial explicit non-goals")
    parser.add_argument("--constraints", default="", help="Initial product/user constraints")
    parser.add_argument("--risks", default="", help="Initial product risks")
    parser.add_argument("--stack", default="", help="Initial preferred technical stack")
    parser.add_argument("--success", default="", help="Initial success criteria")
    parser.add_argument("--research", default="", help="Initial research plan item")
    parser.add_argument(
        "--dest",
        default=".",
        help="Destination parent directory where the new workspace will be created",
    )
    return parser.parse_args()


def copy_core_template(repo_root: Path, echel_core_dir: Path) -> None:
    echel_core_dir.mkdir(parents=True, exist_ok=False)
    for item in CORE_ITEMS:
        src = repo_root / item
        dst = echel_core_dir / item
        if not src.exists():
            continue
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def copy_project_wiki_template(repo_root: Path, workspace_dir: Path, project_name: str) -> None:
    _ = repo_root
    dst = workspace_dir / "wiki"
    dst.mkdir(parents=True, exist_ok=True)
    for folder in [
        "agents",
        "architecture",
        "canon",
        "decisions",
        "deployment",
        "discovery",
        "domain",
        "engineering",
        "execution",
        "governance",
        "knowledge",
        "operations",
        "reports",
        "requirements",
        "roadmap",
        "strategy",
        "validation",
        "work",
    ]:
        (dst / folder).mkdir(parents=True, exist_ok=True)
    (dst / "project-brief.md").write_text(
        """---
type: project-brief
status: active
---
# Project Brief

This wiki is the product-owned memory for the software being built with Echel.

## Ownership

- Product knowledge, decisions, tasks, reports, and evolving context live here.
- Echel framework method, tools, prompts, and schemas live under `echel-core/`.
""",
        encoding="utf-8",
    )
    (dst / "log.md").write_text("---\ntype: log\nstatus: active\n---\n# Log\n", encoding="utf-8")
    (dst / "index.md").write_text("---\ntype: index\nstatus: active\n---\n# Index\n", encoding="utf-8")
    write_lifecycle_templates(dst, project_name)


def write_lifecycle_templates(wiki: Path, project_name: str) -> None:
    templates = {
        "discovery/product-discovery-spec.md": """---
type: product-discovery-spec
status: draft
stage: discovery
---
# Product Discovery Specification

## 01 Executive Summary

| Field | Value | Statement Type | Confidence | Source ID |
| --- | --- | --- | --- | --- |
| Product Name | TBD | fact | medium | P-001 |
| One-sentence description | TBD | assumption | low | P-002 |
| Category | TBD | assumption | low | P-003 |
| Target industry | TBD | assumption | low | P-004 |

## 02 Problem

TBD

## 03 Users

TBD

## 04 Buyers

TBD

## 05 Operators

TBD

## 06 Current Workflow

TBD

## 07 Proposed Solution

TBD

## 08 Business Model

TBD

## 09 Success Criteria

TBD

## 10 Scope

TBD

## 11 Non Goals

TBD

## 12 Constraints

TBD

## 13 Assumptions

TBD

## 14 Risks

TBD

## 15 Open Questions

TBD

## Quality Gate

- [ ] Problem clearly defined.
- [ ] Buyer, user, and operator identified.
- [ ] Current workflow documented.
- [ ] Business value and success criteria measurable.
- [ ] Non-goals, constraints, risks, assumptions, open questions, and research plan recorded.
""",
        "discovery/research-plan.md": """---
type: research-plan
status: draft
stage: discovery
---
# Research Plan

| ID | Topic | Question | Method | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| RES-001 | Product discovery | What must be validated before canon? | Interview/research | Founder Interviewer | Planned |
""",
        "discovery/assumptions.md": """---
type: assumptions
status: draft
stage: discovery
---
# Assumptions

| ID | Statement | Type | Confidence | Validation Method | Status |
| --- | --- | --- | --- | --- | --- |
| A-001 | Initial product assumptions are not yet validated. | assumption | low | Discovery research | Open |
""",
        "canon/product-canon.md": "# Product Canon\n\n## What This Product Is\n\nTBD\n\n## What This Product Is Not\n\nTBD\n\n## Why This Product Exists\n\nTBD\n",
        "canon/vision.md": "# Product Vision\n\n## Vision Statement\n\nTBD\n\n## Business Transformation\n\nTBD\n",
        "canon/product-principles.md": "# Product Principles\n\n## Principles\n\n- TBD\n",
        "canon/non-negotiables.md": "# Non-Negotiables\n\n## Hard Constraints\n\n- TBD\n",
        "strategy/icp.md": "# Ideal Customer Profile\n\n## Primary ICP\n\nTBD\n",
        "strategy/buyer-user-model.md": "# Buyer and User Model\n\n## Economic Buyer\n\nTBD\n\n## User\n\nTBD\n\n## Operator\n\nTBD\n",
        "strategy/market-wedge.md": "# Market Wedge\n\n## Wedge Definition\n\nTBD\n",
        "strategy/competitive-analysis.md": "# Competitive Analysis\n\n## Alternatives\n\n- TBD\n",
        "strategy/positioning.md": "# Positioning\n\n## Positioning Statement\n\nTBD\n",
        "strategy/pricing-and-packaging.md": "# Pricing and Packaging\n\n## Pricing Model\n\nTBD\n",
        "strategy/pmf-evidence.md": "# PMF Evidence\n\n## Continue Criteria\n\nTBD\n\n## Stop Criteria\n\nTBD\n",
        "requirements/product-requirements.md": "# Product Requirements\n\n| ID | Requirement | Source IDs | Priority | Phase | Status |\n| --- | --- | --- | --- | --- | --- |\n| REQ-001 | TBD | P-001 | P0 | MVP | Draft |\n",
        "requirements/functional-requirements.md": "# Functional Requirements\n\n| ID | Requirement | Source IDs | Acceptance Criteria | Status |\n| --- | --- | --- | --- | --- |\n| REQ-001 | TBD | P-001 | AC-001 | Draft |\n",
        "requirements/non-functional-requirements.md": "# Non-Functional Requirements\n\n| ID | Category | Requirement | Source IDs | Status |\n| --- | --- | --- | --- | --- |\n| NFR-001 | Reliability | TBD | P-001 | Draft |\n",
        "requirements/mvp-scope.md": "# MVP Scope\n\n## MVP\n\n- TBD\n",
        "requirements/out-of-scope.md": "# Out Of Scope\n\n## Exclusions\n\n- TBD\n",
        "requirements/acceptance-criteria.md": "# Acceptance Criteria\n\n| ID | Requirement ID | Criteria | Status |\n| --- | --- | --- | --- |\n| AC-001 | REQ-001 | TBD | Draft |\n",
        "domain/domain-overview.md": "# Domain Overview\n\n## Purpose\n\nTBD\n",
        "domain/ubiquitous-language.md": "# Ubiquitous Language\n\n| ID | Term | Definition | Source IDs | Status |\n| --- | --- | --- | --- | --- |\n| DM-001 | TBD | TBD | REQ-001 | Draft |\n",
        "domain/bounded-contexts.md": "# Bounded Contexts\n\n| ID | Context | Responsibility | Source IDs | Status |\n| --- | --- | --- | --- | --- |\n| BC-001 | TBD | TBD | REQ-001 | Draft |\n",
        "domain/entities.md": "# Entities\n\n| ID | Entity | Context | Source IDs | Status |\n| --- | --- | --- | --- | --- |\n| ENT-001 | TBD | BC-001 | REQ-001 | Draft |\n",
        "domain/aggregates.md": "# Aggregates\n\n| ID | Aggregate | Root Entity | Source IDs | Status |\n| --- | --- | --- | --- | --- |\n| AGG-001 | TBD | ENT-001 | REQ-001 | Draft |\n",
        "domain/domain-events.md": "# Domain Events\n\n| ID | Event | Producer | Consumer | Status |\n| --- | --- | --- | --- | --- |\n| DE-001 | TBD | TBD | TBD | Draft |\n",
        "domain/workflows.md": "# Domain Workflows\n\n| ID | Workflow | Source IDs | Status |\n| --- | --- | --- | --- |\n| WF-001 | TBD | REQ-001 | Draft |\n",
        "domain/policies-and-rules.md": "# Policies And Rules\n\n| ID | Rule | Source IDs | Status |\n| --- | --- | --- | --- |\n| BR-001 | TBD | REQ-001 | Draft |\n",
        "architecture/overview.md": "# Architecture Overview\n\n## Purpose\n\nTBD\n",
        "architecture/context-map.md": "# Context Map\n\n## Contexts\n\nTBD\n",
        "architecture/component-architecture.md": "# Component Architecture\n\n| ID | Component | Responsibility | Source IDs | Status |\n| --- | --- | --- | --- | --- |\n| ARCH-001 | TBD | TBD | BC-001 | Draft |\n",
        "architecture/data-architecture.md": "# Data Architecture\n\n## Data Model\n\nTBD\n",
        "architecture/api-architecture.md": "# API Architecture\n\n## API Surface\n\nTBD\n",
        "architecture/event-architecture.md": "# Event Architecture\n\n## Events\n\nTBD\n",
        "architecture/workflow-architecture.md": "# Workflow Architecture\n\n## Workflows\n\nTBD\n",
        "architecture/security-architecture.md": "# Security Architecture\n\n## Security Model\n\nTBD\n",
        "architecture/observability-architecture.md": "# Observability Architecture\n\n## Signals\n\nTBD\n",
        "roadmap/master-roadmap.md": "# Master Roadmap\n\n| ID | Phase | Objective | Dependencies | Status |\n| --- | --- | --- | --- | --- |\n| RM-001 | Foundation | TBD | REQ-001 | Planned |\n",
        "roadmap/mvp-roadmap.md": "# MVP Roadmap\n\n## MVP Goal\n\nTBD\n",
        "roadmap/architecture-roadmap.md": "# Architecture Roadmap\n\n## Architecture Work\n\nTBD\n",
        "roadmap/engineering-roadmap.md": "# Engineering Roadmap\n\n## Engineering Work\n\nTBD\n",
        "roadmap/release-plan.md": "# Release Plan\n\n| ID | Release | Scope | Gate | Status |\n| --- | --- | --- | --- | --- |\n| REL-001 | MVP | TBD | Release readiness | Planned |\n",
        "execution/phase-0-foundation.md": _phase_template("Phase 0 Foundation", "EP0-001"),
        "execution/phase-1-mvp.md": _phase_template("Phase 1 MVP", "EP1-001"),
        "execution/phase-2-hardening.md": _phase_template("Phase 2 Hardening", "EP2-001"),
        "execution/phase-3-production.md": _phase_template("Phase 3 Production", "EP3-001"),
        "execution/phase-4-evolution.md": _phase_template("Phase 4 Evolution", "EP4-001"),
        "validation/test-strategy.md": "# Test Strategy\n\n| Validation ID | Scope | Requirement IDs | Task IDs | Evidence Target | Status |\n| --- | --- | --- | --- | --- | --- |\n| TEST-001 | TBD | REQ-001 | TASK-1001 | EVID-VALIDATION-001 | Planned |\n",
        "validation/acceptance-tests.md": "# Acceptance Tests\n\n| ID | Scenario | Requirement IDs | Status |\n| --- | --- | --- | --- |\n| TEST-ACC-001 | TBD | REQ-001 | Planned |\n",
        "validation/integration-tests.md": "# Integration Tests\n\n| ID | Scenario | Requirement IDs | Status |\n| --- | --- | --- | --- |\n| TEST-INT-001 | TBD | REQ-001 | Planned |\n",
        "validation/e2e-tests.md": "# E2E Tests\n\n| ID | Scenario | Requirement IDs | Status |\n| --- | --- | --- | --- |\n| TEST-E2E-001 | TBD | REQ-001 | Planned |\n",
        "validation/security-tests.md": "# Security Tests\n\n| ID | Scenario | Requirement IDs | Status |\n| --- | --- | --- | --- |\n| TEST-SEC-001 | TBD | NFR-001 | Planned |\n",
        "validation/performance-tests.md": "# Performance Tests\n\n| ID | Scenario | Requirement IDs | Status |\n| --- | --- | --- | --- |\n| TEST-PERF-001 | TBD | NFR-001 | Planned |\n",
        "validation/validation-report.md": "# Validation Report\n\n## Summary\n\nNo validation has run yet.\n",
        "deployment/deployment-architecture.md": "# Deployment Architecture\n\n## Deployment Path\n\nTBD\n",
        "deployment/environments.md": "# Environments\n\n| ID | Environment | Purpose | Status |\n| --- | --- | --- | --- |\n| ENV-001 | Local | Development and verification | Active |\n",
        "deployment/release-process.md": "# Release Process\n\n## Process\n\nTBD\n",
        "deployment/rollback-plan.md": "# Rollback Plan\n\n| ID | Failure Mode | Rollback Action | Owner | Status |\n| --- | --- | --- | --- | --- |\n| RB-001 | TBD | TBD | Release Manager | Draft |\n",
        "deployment/secrets-management.md": "# Secrets Management\n\n## Strategy\n\nNo secrets are committed to the repository.\n",
        "deployment/production-checklist.md": "# Production Checklist\n\n| ID | Area | Check | Owner | Status |\n| --- | --- | --- | --- | --- |\n| PROD-001 | Validation | Validation report exists. | QA Agent | Pending |\n",
        "operations/runbook.md": "# Runbook\n\n## Routine Operations\n\nTBD\n",
        "operations/observability.md": "# Observability\n\n## Signals\n\nTBD\n",
        "operations/incident-response.md": "# Incident Response\n\n## Severity Model\n\nTBD\n",
        "operations/backup-and-recovery.md": "# Backup And Recovery\n\n## Recovery Strategy\n\nTBD\n",
        "operations/sla-and-slo.md": "# SLA And SLO\n\n## Service Objectives\n\nTBD\n",
        "operations/change-management.md": "# Change Management\n\n## Change Classes\n\nTBD\n",
        "operations/evolution-backlog.md": "# Evolution Backlog\n\n| ID | Item | Source | Status |\n| --- | --- | --- | --- |\n| EVO-001 | TBD | Learning loop | Planned |\n",
        "operations/learning-records.md": "# Learning Records\n\n| ID | Source | Summary | Action | Status |\n| --- | --- | --- | --- | --- |\n| LEARN-001 | Initialization | No learning recorded yet. | none | Captured |\n",
        "governance/documentation-governance.md": "# Documentation Governance\n\n## Source Of Truth Hierarchy\n\nDiscovery -> Canon -> Strategy -> Requirements -> Domain -> Architecture -> Roadmap -> Execution -> Validation -> Deployment -> Operations -> Governance.\n\n## Duplication Rules\n\nOne authoritative location per decision.\n\n## Deprecation Process\n\nLegacy pages remain until migration compatibility is verified.\n",
        "governance/architecture-governance.md": "# Architecture Governance\n\n## Review Rules\n\nMajor architecture choices require ADR coverage.\n",
        "governance/adr-process.md": "# ADR Process\n\n## When To Create ADRs\n\nCreate ADRs for architecture, release, security, data, or source-of-truth decisions.\n",
        "governance/traceability-model.md": "# Traceability Model\n\n## Chain\n\nDiscovery -> Canon -> Strategy -> Requirement -> Domain -> Architecture -> Task -> Test -> Evidence.\n",
        "governance/quality-gates.md": "# Quality Gates\n\n## Gates\n\nDiscovery, requirements, domain, architecture, release, integrity.\n",
        "governance/repository-integrity-audit.md": "# Repository Integrity Audit Model\n\n## Scope\n\nMissing docs, stale docs, broken traceability, missing ADRs, missing tests, missing evidence, methodology violations, contradictions, and migration compatibility.\n",
        "governance/contradictions.md": "# Contradiction Register\n\n| ID | Status | Title | Source Record | Type | Links | Impact | Resolution Task | Owner |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n| CONTR-000 | Resolved | No contradictions recorded | none | none | None | No current impact. | CONTR-TASK-000 | Governance Auditor |\n",
        "governance/migration-compatibility.md": "# Migration Compatibility Map\n\n## Purpose\n\nLegacy root pages remain supported while lifecycle folders become canonical.\n",
        "engineering/repository-structure.md": "# Repository Structure\n\n## Purpose\n\nTBD\n",
        "engineering/coding-standards.md": "# Coding Standards\n\n## Standards\n\nTBD\n",
        "engineering/development-workflow.md": "# Development Workflow\n\n## Rule\n\nDo not implement product code before an approved task packet exists.\n",
        "engineering/configuration-strategy.md": "# Configuration Strategy\n\n## Strategy\n\nTBD\n",
        "engineering/local-development.md": "# Local Development\n\n## Commands\n\nTBD\n",
        "agents/role-model.md": "# Agent Role Model\n\n## Roles\n\nFounder Interviewer, Product Manager, Domain Modeler, Solution Architect, Delivery Planner, Implementation Agent, QA Agent, Release Manager, Operations Steward, Governance Auditor.\n",
        "agents/handoff-protocol.md": "# Agent Handoff Protocol\n\n## Required Handoff Summary\n\nSource artifacts, changed artifacts, decisions, assumptions, risks, unresolved questions, evidence, stale artifacts, and next-stage instructions.\n",
        "work/TASK_INDEX.md": "# Execution Task Index\n\n| Task ID | Title | Source | Dependencies | Status |\n| --- | --- | --- | --- | --- |\n| TASK-1001 | Define first implementation task | execution/phase-0-foundation.md | REQ-001 | Planned |\n",
    }
    from echel.discovery import _default_assumptions, _default_pds, _default_research

    templates["discovery/product-discovery-spec.md"] = _default_pds(project_name)
    templates["discovery/research-plan.md"] = _default_research()
    templates["discovery/assumptions.md"] = _default_assumptions()
    for rel, content in templates.items():
        path = wiki / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(_with_frontmatter(rel, content), encoding="utf-8")


def _phase_template(title: str, task_id: str) -> str:
    return f"""# {title}

| Phase Task ID | Task | Objective | Business Reason | Scope | Dependencies | Acceptance Criteria | Tests Required | Validation Command | Documentation Updates | Expected Repo Changes | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {task_id} | Define first scoped task | Convert lifecycle memory into one agent-executable task. | Agents need explicit bounded work. | Task definition only. | REQ-001 | Task has objective, files, tests, rollback, and DoD. | Documentation review | `make wiki-health` | Update work index. | No product code. | Planned |
"""


def _with_frontmatter(rel: str, content: str) -> str:
    if content.startswith("---"):
        return content
    doc_type = Path(rel).stem.replace("_", "-")
    stage = rel.split("/", 1)[0] if "/" in rel else "product-memory"
    return f"---\ntype: {doc_type}\nstatus: draft\nstage: {stage}\n---\n{content}"


def write_generated_core_config(echel_core_dir: Path) -> None:
    config_path = echel_core_dir / "project.echel"
    config_path.write_text(
        """{
  "version": 2,
  "roots": {
    "SRC_ROOT": "..",
    "LANG_ROOT": "tools",
    "MEMORY_ROOT": "docs/development/state",
    "WIKI_ROOT": "../wiki"
  },
  "migration_map": {},
  "gate_policy": ".echel/gates.json",
  "evidence_registry": ".echel/evidence_registry.json"
}
""",
        encoding="utf-8",
    )


def reset_generated_core_state(echel_core_dir: Path) -> None:
    work = echel_core_dir / "docs" / "development" / "work.md"
    if work.exists():
        work.write_text(
            """# Work

## Backlog

## In Progress

## Done
""",
            encoding="utf-8",
        )


def copy_existing_source(source_dir: Path, workspace_dir: Path) -> None:
    shutil.copytree(
        source_dir,
        workspace_dir,
        ignore=shutil.ignore_patterns(".git", "echel-core"),
    )


def ensure_workspace_gitignore(workspace_dir: Path) -> None:
    gitignore_path = workspace_dir / ".gitignore"
    required_line = "echel-core/"
    if gitignore_path.exists():
        current = gitignore_path.read_text(encoding="utf-8")
        if required_line not in current.splitlines():
            suffix = "" if current.endswith("\n") else "\n"
            gitignore_path.write_text(
                current
                + f"{suffix}\n# Keep Echel framework out of project repository\n{required_line}\n",
                encoding="utf-8",
            )
        return

    gitignore_path.write_text(
        "# Keep Echel framework out of project repository\n"
        "echel-core/\n"
        "\n"
        "# Common local artifacts\n"
        ".DS_Store\n"
        "__pycache__/\n"
        "*.pyc\n",
        encoding="utf-8",
    )


def write_project_identity_files(workspace_dir: Path, project_name: str, mode: str, source: str | None) -> None:
    readme_path = workspace_dir / "README.md"
    license_path = workspace_dir / "LICENSE"

    if readme_path.exists():
        return

    lines = [
        f"# {project_name}",
        "",
        "This is the software project repository initialized by Echel.",
        "",
        "## Structure",
        "",
        "- `./`: Project codebase and repository root",
        "- `./wiki/`: Product memory, decisions, tasks, reports, and accumulated project intelligence",
        "- `./echel-core/`: Internal Echel framework for methodology, tools, prompts, schemas, and workflow orchestration",
        "",
        "## Next steps",
        "",
        "1. Start implementing software in this repository root.",
        "2. Commit and maintain `./wiki` with the product; it is part of the project.",
        "3. Use `./echel-core` for Echel's operating method and automation.",
        "4. Keep `echel-core/` ignored by this repository's Git history.",
        "",
        f"Initialization mode: `{mode}`",
    ]
    if source:
        lines.append(f"Source path: `{source}`")
    lines.append("")
    readme_path.write_text("\n".join(lines), encoding="utf-8")

    if not license_path.exists():
        license_path.write_text(
            "Copyright (c) "
            f"{datetime.now(timezone.utc).year} {project_name}\n\n"
            "All rights reserved.\n",
            encoding="utf-8",
        )


def _replace_section_body(text: str, heading: str, body: str) -> str:
    import re

    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    if re.search(pattern, text, flags=re.DOTALL):
        return re.sub(
            pattern,
            lambda match: f"{match.group(1)}{body.rstrip()}\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


def write_product_pages(
    workspace_dir: Path,
    project_name: str,
    problem: str,
    solution: str,
    direction: str,
    users: str,
    buyers: str,
    operators: str,
    mvp: str,
    business_model: str,
    non_goals: str,
    constraints: str,
    risks: str,
    stack: str,
    success: str,
    research: str,
) -> None:
    wiki = workspace_dir / "wiki"
    pages = {
        "project.md": f"""---
type: product
status: active
---
# {project_name}

## Problem
{problem or "TBD"}

## Intended Solution
{solution or "TBD"}

## Product Direction
{direction or "TBD"}

## Success Criteria
- {success or "TBD"}

## Preferred Stack
- {stack or "TBD"}

## Lifecycle Compatibility

This legacy root page remains supported for old links and product-memory continuity.

- Lifecycle stage: `repository-initialization`
- Compatibility mode: source summary
- Canonical lifecycle artifacts:
  - [[canon/product-canon]]
  - [[canon/vision]]
- Migration map: [[governance/migration-compatibility]]
""",
        "problem.md": f"""---
type: product-problem
status: draft
---
# Problem

## Problem Statement
{problem or "TBD"}

## Why It Matters
TBD

## Current Alternatives
TBD

## Risks
- {risks or "TBD"}

## Lifecycle Compatibility

This legacy root page remains supported for old links and product-memory continuity.

- Lifecycle stage: `discovery`
- Compatibility mode: compatibility summary
- Canonical lifecycle artifacts:
  - [[discovery/product-discovery-spec]]
  - [[canon/product-canon]]
- Migration map: [[governance/migration-compatibility]]
""",
        "users.md": f"""---
type: product-users
status: draft
---
# Users

## Primary Users
- {users or "TBD"}

## Needs
- TBD

## Constraints
- {constraints or "TBD"}
""",
        "solution.md": f"""---
type: product-solution
status: draft
---
# Solution

## Solution Concept
{solution or "TBD"}

## Core Capabilities
- TBD

## Lifecycle Compatibility

This legacy root page remains supported for old links and product-memory continuity.

- Lifecycle stage: `canon`
- Compatibility mode: compatibility summary
- Canonical lifecycle artifacts:
  - [[canon/product-canon]]
  - [[requirements/product-requirements]]
- Migration map: [[governance/migration-compatibility]]
""",
        "scope.md": f"""---
type: product-scope
status: draft
---
# Scope

## MVP
- {mvp or "TBD"}

## Later
- TBD

## Out of Scope
- {non_goals or "TBD"}

## Lifecycle Compatibility

This legacy root page remains supported for old links and product-memory continuity.

- Lifecycle stage: `requirements`
- Compatibility mode: compatibility summary
- Canonical lifecycle artifacts:
  - [[requirements/mvp-scope]]
  - [[requirements/out-of-scope]]
- Migration map: [[governance/migration-compatibility]]
""",
        "roadmap.md": """---
type: roadmap
status: draft
---
# Roadmap

## Now
- Clarify product intent.

## Next
- Define MVP work.

## Later
- TBD

## Lifecycle Compatibility

This legacy root page remains supported for old links and product-memory continuity.

- Lifecycle stage: `roadmap`
- Compatibility mode: compatibility summary
- Canonical lifecycle artifacts:
  - [[roadmap/master-roadmap]]
  - [[roadmap/mvp-roadmap]]
  - [[roadmap/release-plan]]
- Migration map: [[governance/migration-compatibility]]
""",
        "architecture.md": f"""---
type: product-architecture
status: draft
---
# Product Architecture

## System Shape
TBD

## Key Components
- TBD

## Preferred Stack
- {stack or "TBD"}

## Open Architecture Questions
- TBD

## Lifecycle Compatibility

This legacy root page remains supported for old links and product-memory continuity.

- Lifecycle stage: `architecture`
- Compatibility mode: compatibility summary
- Canonical lifecycle artifacts:
  - [[architecture/overview]]
  - [[architecture/component-architecture]]
  - [[architecture/data-architecture]]
- Migration map: [[governance/migration-compatibility]]
""",
        "workflows.md": """---
type: product-workflows
status: draft
---
# Workflows

## Core Workflows
- TBD
""",
    }
    for rel, content in pages.items():
        path = wiki / rel
        path.write_text(content, encoding="utf-8")
    update_lifecycle_context(wiki, project_name, problem, solution, direction, users, buyers, operators, mvp, business_model, non_goals, constraints, risks, stack, success, research)


def update_lifecycle_context(
    wiki: Path,
    project_name: str,
    problem: str,
    solution: str,
    direction: str,
    users: str,
    buyers: str,
    operators: str,
    mvp: str,
    business_model: str,
    non_goals: str,
    constraints: str,
    risks: str,
    stack: str,
    success: str,
    research: str,
) -> None:
    pds = wiki / "discovery" / "product-discovery-spec.md"
    text = pds.read_text(encoding="utf-8")
    text = _replace_section_body(text, "02 Problem", problem or "TBD")
    text = _replace_section_body(text, "03 Users", users or "TBD")
    text = _replace_section_body(text, "04 Buyers", buyers or "TBD")
    text = _replace_section_body(text, "05 Operators", operators or "TBD")
    text = _replace_section_body(text, "08 Proposed Solution", solution or "TBD")
    text = _replace_section_body(text, "09 Product Vision", direction or "TBD")
    text = _replace_section_body(text, "10 Business Model", business_model or "TBD")
    text = _replace_section_body(text, "11 Success Criteria", success or "TBD")
    text = _replace_section_body(text, "12 Scope", mvp or "TBD")
    text = _replace_section_body(text, "13 Non-Goals", non_goals or "TBD")
    text = _replace_section_body(text, "14 Constraints", constraints or "TBD")
    text = _replace_section_body(text, "15 Assumptions", "Initial assumptions require discovery validation.")
    text = _replace_section_body(text, "17 Risks", risks or "TBD")
    text = _replace_section_body(text, "22 Open Questions", research or "TBD")
    text = _replace_section_body(text, "23 Research Plan", research or "TBD")
    pds.write_text(text, encoding="utf-8")

    replacements = {
        "canon/product-canon.md": {
            "What This Product Is": solution or direction or "TBD",
            "What This Product Is Not": non_goals or "TBD",
            "Why This Product Exists": problem or "TBD",
        },
        "canon/vision.md": {"Vision Statement": direction or "TBD", "Business Transformation": success or "TBD"},
        "strategy/icp.md": {"Primary ICP": buyers or users or "TBD"},
        "strategy/buyer-user-model.md": {"Economic Buyer": buyers or "TBD", "User": users or "TBD", "Operator": operators or "TBD"},
        "requirements/mvp-scope.md": {"MVP": f"- {mvp or 'TBD'}"},
        "requirements/out-of-scope.md": {"Exclusions": f"- {non_goals or 'TBD'}"},
        "architecture/overview.md": {"Purpose": f"Preferred stack: {stack or 'TBD'}"},
    }
    for rel, sections in replacements.items():
        path = wiki / rel
        doc = path.read_text(encoding="utf-8")
        for heading, body in sections.items():
            doc = _replace_section_body(doc, heading, body)
        path.write_text(doc, encoding="utf-8")

    research_path = wiki / "discovery" / "research-plan.md"
    research_text = research_path.read_text(encoding="utf-8")
    if research:
        research_text = """---
type: discovery-research-plan
status: draft
stage: discovery
---
# Research Plan

This document tracks research activities required before later lifecycle stages can proceed. Research findings must be recorded with statement type and confidence.

## Research Areas

### Market Research

| ID | Topic | Method | Owner | Due Date | Status | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| RES-001 | Product discovery | Interview/research | Founder Interviewer | Accepted during initialization | planned | Initial research question: """ + research + """ |

## Research Rules

- Every research finding must be tagged with statement type (`fact`, `observation`, `assumption`, `hypothesis`).
- Every research finding must include confidence level.
- Research that invalidates upstream assumptions must trigger a contradiction record and propagate the change.
- Research results feed into the Product Discovery Specification, Product Canon, and Product Strategy.

## Research Completion Criteria

- [ ] Market size and wedge are validated or explicitly marked as hypothesis.
- [ ] Technology constraints are confirmed.
- [ ] Legal and compliance requirements are identified.
- [ ] Domain terminology is stable.
- [ ] Competitive landscape is mapped.
- [ ] All high-priority open questions from the PDS are answered or accepted.
"""
        research_path.write_text(research_text, encoding="utf-8")


def update_project_wiki_context(
    workspace_dir: Path,
    project_name: str,
    mode: str,
    source: str | None,
    problem: str,
    solution: str,
    direction: str,
    users: str,
    buyers: str,
    operators: str,
    mvp: str,
    business_model: str,
    non_goals: str,
    constraints: str,
    risks: str,
    stack: str,
    success: str,
    research: str,
) -> None:
    write_product_pages(
        workspace_dir,
        project_name,
        problem,
        solution,
        direction,
        users,
        buyers,
        operators,
        mvp,
        business_model,
        non_goals,
        constraints,
        risks,
        stack,
        success,
        research,
    )
    brief = workspace_dir / "wiki" / "project-brief.md"
    if brief.exists() and "# Project Brief" in brief.read_text(encoding="utf-8"):
        text = brief.read_text(encoding="utf-8").replace("# Project Brief", f"# Project Brief - {project_name}", 1)
        if problem:
            text = _replace_section_body(text, "Product Problem", problem)
        if solution:
            text = _replace_section_body(text, "Intended Solution", solution)
        if direction:
            text = _replace_section_body(text, "Product Direction", direction)
        if mvp:
            text = _replace_section_body(text, "MVP", mvp)
        if business_model:
            text = _replace_section_body(text, "Business Model", business_model)
        if non_goals:
            text = _replace_section_body(text, "Non Goals", non_goals)
        if constraints:
            text = _replace_section_body(text, "Constraints", constraints)
        if risks:
            text = _replace_section_body(text, "Risks", risks)
        if stack:
            text = _replace_section_body(text, "Preferred Stack", stack)
        brief.write_text(text, encoding="utf-8")

    log = workspace_dir / "wiki" / "log.md"
    stamp = datetime.now(timezone.utc).date()
    with log.open("a", encoding="utf-8") as f:
        f.write(
            f"\n## [{stamp}] init | {project_name}\n"
            f"- Initialized project in `{mode}` mode.\n"
            f"- Generated project-root workspace with `wiki/` as product memory and internal `echel-core/` orchestration.\n"
        )
        if source:
            f.write(f"- Source path: `{source}`.\n")


def main() -> int:
    args = parse_args()
    if args.mode == "existing" and not args.source:
        raise SystemExit("--source is required when --mode=existing")

    repo_root = Path(__file__).resolve().parents[1]
    dest_parent = Path(args.dest).resolve()
    workspace_dir = dest_parent / args.name
    source_dir = Path(args.source).resolve() if args.source else None

    if workspace_dir.exists():
        raise SystemExit(f"Target workspace already exists: {workspace_dir}")
    if args.mode == "existing":
        if source_dir is None or not source_dir.is_dir():
            raise SystemExit(f"Invalid --source path: {args.source}")

    echel_core_dir = workspace_dir / "echel-core"

    if args.mode == "existing":
        copy_existing_source(source_dir, workspace_dir)
    else:
        workspace_dir.mkdir(parents=True, exist_ok=False)

    copy_core_template(repo_root, echel_core_dir)
    copy_project_wiki_template(repo_root, workspace_dir, args.name)
    write_generated_core_config(echel_core_dir)
    reset_generated_core_state(echel_core_dir)
    ensure_workspace_gitignore(workspace_dir)
    write_project_identity_files(workspace_dir, args.name, args.mode, args.source)
    update_project_wiki_context(
        workspace_dir,
        args.name,
        args.mode,
        args.source,
        args.problem,
        args.solution,
        args.direction,
        args.users,
        args.buyers,
        args.operators,
        args.mvp,
        args.business_model,
        args.non_goals,
        args.constraints,
        args.risks,
        args.stack,
        args.success,
        args.research,
    )

    print(f"Initialized workspace: {workspace_dir}")
    print(f"- Echel framework: {echel_core_dir}")
    print(f"- Project wiki: {workspace_dir / 'wiki'}")
    print(f"- Project repository root: {workspace_dir}")
    print("Next:")
    print(f"  cd {workspace_dir} && git init")
    print(f"  cd {workspace_dir}/echel-core && make session-bootstrap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
