#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TMP = Path("/tmp") / f"echel_vnext_generated_project_verify_{os.getpid()}"


LIFECYCLE_FILES = [
    "discovery/product-discovery-spec.md",
    "discovery/research-plan.md",
    "discovery/assumptions.md",
    "canon/product-canon.md",
    "canon/vision.md",
    "canon/product-principles.md",
    "canon/non-negotiables.md",
    "strategy/icp.md",
    "strategy/buyer-user-model.md",
    "strategy/market-wedge.md",
    "strategy/competitive-analysis.md",
    "strategy/positioning.md",
    "strategy/pricing-and-packaging.md",
    "strategy/pmf-evidence.md",
    "requirements/product-requirements.md",
    "requirements/functional-requirements.md",
    "requirements/non-functional-requirements.md",
    "requirements/mvp-scope.md",
    "requirements/out-of-scope.md",
    "requirements/acceptance-criteria.md",
    "domain/domain-overview.md",
    "domain/ubiquitous-language.md",
    "domain/bounded-contexts.md",
    "domain/entities.md",
    "domain/aggregates.md",
    "domain/domain-events.md",
    "domain/workflows.md",
    "domain/policies-and-rules.md",
    "architecture/overview.md",
    "architecture/context-map.md",
    "architecture/component-architecture.md",
    "architecture/data-architecture.md",
    "architecture/api-architecture.md",
    "architecture/event-architecture.md",
    "architecture/workflow-architecture.md",
    "architecture/security-architecture.md",
    "architecture/observability-architecture.md",
    "roadmap/master-roadmap.md",
    "roadmap/mvp-roadmap.md",
    "roadmap/architecture-roadmap.md",
    "roadmap/engineering-roadmap.md",
    "roadmap/release-plan.md",
    "execution/phase-0-foundation.md",
    "execution/phase-1-mvp.md",
    "execution/phase-2-hardening.md",
    "execution/phase-3-production.md",
    "execution/phase-4-evolution.md",
    "validation/test-strategy.md",
    "validation/acceptance-tests.md",
    "validation/integration-tests.md",
    "validation/e2e-tests.md",
    "validation/security-tests.md",
    "validation/performance-tests.md",
    "validation/validation-report.md",
    "deployment/deployment-architecture.md",
    "deployment/environments.md",
    "deployment/release-process.md",
    "deployment/rollback-plan.md",
    "deployment/secrets-management.md",
    "deployment/production-checklist.md",
    "operations/runbook.md",
    "operations/observability.md",
    "operations/incident-response.md",
    "operations/backup-and-recovery.md",
    "operations/sla-and-slo.md",
    "operations/change-management.md",
    "operations/evolution-backlog.md",
    "governance/documentation-governance.md",
    "governance/architecture-governance.md",
    "governance/adr-process.md",
    "governance/traceability-model.md",
    "governance/quality-gates.md",
    "governance/repository-integrity-audit.md",
    "governance/contradictions.md",
    "governance/migration-compatibility.md",
    "engineering/repository-structure.md",
    "engineering/coding-standards.md",
    "engineering/development-workflow.md",
    "engineering/configuration-strategy.md",
    "engineering/local-development.md",
    "agents/role-model.md",
    "agents/handoff-protocol.md",
    "work/TASK_INDEX.md",
]


def run(cmd: list[str], cwd: Path) -> str:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.returncode != 0:
        print(f"FAILED: {' '.join(cmd)}", file=sys.stderr)
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    return proc.stdout


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"vNext generated-project verification failed: {message}", file=sys.stderr)
        raise SystemExit(1)


def verify_structure(workspace: Path) -> None:
    wiki = workspace / "wiki"
    core = workspace / "echel-core"
    require(wiki.is_dir(), "root product wiki is missing")
    require(core.is_dir(), "echel-core is missing")
    require(not (core / "wiki").exists(), "product wiki must not live inside echel-core")

    config = json.loads((core / "project.echel").read_text(encoding="utf-8"))
    require(config["roots"]["WIKI_ROOT"] == "../wiki", "generated core must point WIKI_ROOT to ../wiki")
    require("echel-core/" in (workspace / ".gitignore").read_text(encoding="utf-8"), "echel-core/ must be ignored by the product repository")

    missing = [rel for rel in LIFECYCLE_FILES if not (wiki / rel).exists()]
    require(not missing, f"missing lifecycle templates: {', '.join(missing)}")

    pds = (wiki / "discovery/product-discovery-spec.md").read_text(encoding="utf-8")
    for heading in ["## 13 Non-Goals", "## 14 Constraints", "## 15 Assumptions", "## 17 Risks", "## 22 Open Questions"]:
        require(heading in pds, f"PDS heading missing: {heading}")


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP)

    run(
        [
            "python3",
            "tools/project_init.py",
            "--name",
            TMP.name,
            "--mode",
            "scratch",
            "--dest",
            str(TMP.parent),
            "--problem",
            "AI-assisted product teams need a verifiable product-to-repository lifecycle.",
            "--solution",
            "A lifecycle operating system that preserves product memory and verifies generated projects.",
            "--direction",
            "Make every generated project start with discovery through governance memory.",
            "--users",
            "Domain experts and AI-assisted engineering teams",
            "--buyers",
            "Product owners and technical founders",
            "--operators",
            "Delivery leads and operations stewards",
            "--mvp",
            "Initialize a full lifecycle project and run commands from Echel Core",
            "--business-model",
            "Subscription or services-led adoption",
            "--non-goals",
            "No product code before approved task packets",
            "--constraints",
            "Product memory must remain outside framework internals",
            "--risks",
            "Generated projects can drift if lifecycle templates are incomplete",
            "--stack",
            "Python CLI and Markdown product memory",
            "--success",
            "A generated project passes lifecycle structure and core command checks",
            "--research",
            "Which lifecycle gates should be mandatory before implementation?",
        ],
        ROOT,
    )

    workspace = TMP
    core = workspace / "echel-core"
    verify_structure(workspace)

    run(["python3", "tools/echel.py", "start"], core)
    run(["python3", "tools/echel.py", "discover", "--field", "workflow", "--value", "Teams currently recreate product context manually across AI sessions."], core)
    run(["python3", "tools/echel.py", "readiness", "--stage", "discovery"], core)
    run(["python3", "tools/echel.py", "discover"], core)
    run(["python3", "tools/echel.py", "status"], core)
    run(["python3", "tools/echel.py", "graph", "report"], core)
    run(["python3", "tools/echel.py", "graph", "validate"], core)
    run(["python3", "tools/echel.py", "traceability"], core)
    run(["python3", "tools/echel.py", "migration", "compatibility"], core)
    run(["make", "wiki-health"], core)

    print("vNext generated-project verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
