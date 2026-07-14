from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from .config import ProjectConfig
from .evidence import ensure_registry, extract_evidence_links
from .graph import add_milestone_node, build_graph, validate_graph, wiki_root, write_graph_report
from .product import clarification_gaps


READINESS_STATES = [
    "idea clarified",
    "mvp scoped",
    "feature ready",
    "feature verified",
    "release candidate",
    "production ready",
]


@dataclass(frozen=True)
class ReadinessIssue:
    severity: str
    message: str


def create_milestone(repo_root: Path, cfg: ProjectConfig, name: str, kind: str = "milestone", summary: str = "") -> Path:
    if kind not in {"milestone", "release"}:
        raise ValueError("milestone kind must be 'milestone' or 'release'")
    root = wiki_root(repo_root, cfg)
    path = add_milestone_node(repo_root, cfg, name=name, kind=kind, summary=summary)
    _append_log(root, "milestone", f"Updated {kind} `{name}`.")
    return path


def readiness_report(repo_root: Path, cfg: ProjectConfig, target: str = "mvp") -> Path:
    root = wiki_root(repo_root, cfg)
    write_graph_report(repo_root, cfg)
    graph = build_graph(repo_root, cfg)
    issues = evaluate_readiness(repo_root, cfg, target, graph)
    report_dir = root / "reports" / "readiness"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / f"{_slug(target)}-readiness.md"
    summary = readiness_summary(repo_root, cfg, target, graph, issues)
    report.write_text(summary, encoding="utf-8")
    _append_log(root, "readiness", f"Generated readiness report [[reports/readiness/{report.stem}]].")
    return report


def proof_pack(repo_root: Path, cfg: ProjectConfig, target: str = "mvp") -> Path:
    root = wiki_root(repo_root, cfg)
    readiness = readiness_report(repo_root, cfg, target)
    graph = build_graph(repo_root, cfg)
    issues = evaluate_readiness(repo_root, cfg, target, graph)
    report_dir = root / "reports" / "proof-packs"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / f"{_slug(target)}-proof-pack.md"
    tasks = _tasks(root)
    reviews = sorted((root / "reports" / "reviews").glob("*.md"))
    evidence = ensure_registry(Path(repo_root) / cfg.evidence_registry)
    vnext_sections = _vnext_proof_sections(root, graph) if _slug(target) == "vnext" else ""
    report.write_text(
        f"""---
type: proof-pack
status: active
target: {target}
---
# Proof Pack - {target}

## Readiness
- Report: [[../readiness/{readiness.stem}]]
- Status: {_status_label(issues)}

## Tasks
{_format_tasks(tasks)}

## Reviews
{_format_paths(root, reviews, report.parent) or "- None"}

## Evidence Registry
- Registered artifacts: {len(evidence.get("artifacts", {})) if isinstance(evidence, dict) else 0}

{vnext_sections}

## Graph Issues
{_format_issues(validate_graph(graph))}

## Readiness Issues
{_format_issues(issues)}

## Decisions
{_format_paths(root, sorted((root / "decisions").glob("ADR-*.md")), report.parent) or "- None"}

## Risks
{_risks(root)}

## Verification Commands
```bash
make wiki-health
python3 tools/echel.py doctor
python3 tools/echel.py graph validate
```
""",
        encoding="utf-8",
    )
    _append_log(root, "proof-pack", f"Generated proof pack [[reports/proof-packs/{report.stem}]].")
    return report


def release_summary(repo_root: Path, cfg: ProjectConfig, target: str = "mvp") -> Path:
    root = wiki_root(repo_root, cfg)
    graph = build_graph(repo_root, cfg)
    issues = evaluate_readiness(repo_root, cfg, target, graph)
    report_dir = root / "reports" / "releases"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / f"{_slug(target)}-release-summary.md"
    report.write_text(
        f"""---
type: release-summary
status: active
target: {target}
---
# Release Summary - {target}

## What Changed
- Product memory, tasks, graph, packets, reviews, readiness, and proof artifacts are summarized for `{target}`.

## Why It Matters
- This summary gives product owners a plain-language checkpoint for progress and remaining risk.

## Verification
- Readiness status: {_status_label(issues)}
- Graph issues: {len(validate_graph(graph))}

## Known Risks
{_risks(root)}

## Remaining Work
{_format_issues(issues)}
""",
        encoding="utf-8",
    )
    _append_log(root, "release", f"Generated release summary [[reports/releases/{report.stem}]].")
    return report


def vnext_final_readiness(repo_root: Path, cfg: ProjectConfig, target: str = "vnext") -> Path:
    root = wiki_root(repo_root, cfg)
    graph = build_graph(repo_root, cfg)
    proof = proof_pack(repo_root, cfg, target=target)
    summary = release_summary(repo_root, cfg, target=target)
    checks = _vnext_final_checks(repo_root, cfg, root, graph, proof, summary)
    blocked = [check for check in checks if check["status"] != "PASS"]
    report_dir = root / "reports" / "readiness"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / f"{_slug(target)}-final-readiness.md"
    report.write_text(_vnext_final_report(target, checks, proof, summary), encoding="utf-8")
    _append_log(root, "readiness", f"Generated vNext final readiness gate [[reports/readiness/{report.stem}]].")
    return report


def readiness_snapshot(repo_root: Path, cfg: ProjectConfig, target: str = "mvp") -> dict:
    graph = build_graph(repo_root, cfg)
    issues = evaluate_readiness(repo_root, cfg, target, graph)
    root = wiki_root(repo_root, cfg)
    return {
        "target": target,
        "states": READINESS_STATES,
        "status": _status_label(issues),
        "issues": [asdict(issue) for issue in issues],
        "reports": {
            "readiness": _report_files(root / "reports" / "readiness"),
            "proof_packs": _report_files(root / "reports" / "proof-packs"),
            "release_summaries": _report_files(root / "reports" / "releases"),
        },
    }


def readiness_summary(repo_root: Path, cfg: ProjectConfig, target: str, graph: dict, issues: list[ReadinessIssue]) -> str:
    root = wiki_root(repo_root, cfg)
    tasks = _tasks(root)
    return f"""---
type: readiness
status: active
target: {target}
---
# Readiness - {target}

## Status
- {_status_label(issues)}

## Scope
- Target: {target}
- States: {", ".join(READINESS_STATES)}

## Coverage
- Graph nodes: {len(graph.get("nodes", []))}
- Graph edges: {len(graph.get("edges", []))}
- Tasks: {len(tasks)}
- Done tasks: {sum(1 for task in tasks if task["status"] == "done")}
- Open tasks: {sum(1 for task in tasks if task["status"] != "done")}

## Blockers
{_format_issues(issues)}

## Next Action
- {next_action(issues)}
"""


def evaluate_readiness(repo_root: Path, cfg: ProjectConfig, target: str, graph: dict | None = None) -> list[ReadinessIssue]:
    root = wiki_root(repo_root, cfg)
    graph = graph or build_graph(repo_root, cfg)
    issues: list[ReadinessIssue] = []
    for issue in validate_graph(graph):
        severity = "blocker" if issue.severity == "critical" else "warning"
        issues.append(ReadinessIssue(severity, f"graph: {issue.message}"))
    gaps = clarification_gaps(repo_root, cfg)
    if gaps:
        issues.append(ReadinessIssue("warning", f"{len(gaps)} open clarification question(s)"))
    tasks = _tasks(root)
    release_bound = tasks
    open_tasks = [task for task in release_bound if task["status"] != "done"]
    if open_tasks:
        issues.append(ReadinessIssue("warning", f"{len(open_tasks)} open task(s) remain"))
    registry = ensure_registry(Path(repo_root) / cfg.evidence_registry)
    known = set(registry.get("artifacts", {}).keys()) if isinstance(registry, dict) else set()
    done_without_evidence = []
    for task in release_bound:
        if task["status"] != "done":
            continue
        text = task["path"].read_text(encoding="utf-8")
        links = extract_evidence_links(text)
        if not links or any(link not in known for link in links):
            done_without_evidence.append(task["id"])
    if done_without_evidence:
        issues.append(ReadinessIssue("blocker", f"done tasks missing registered evidence: {', '.join(done_without_evidence[:8])}"))
    risks = _risk_blocks(root)
    if risks:
        issues.append(ReadinessIssue("blocker", f"unmitigated risk(s): {', '.join(risks[:8])}"))
    reviews = sorted((root / "reports" / "reviews").glob("*.md"))
    if not reviews:
        issues.append(ReadinessIssue("warning", "no review reports found"))
    else:
        open_review_gaps = []
        for review in reviews:
            text = review.read_text(encoding="utf-8")
            if "- [ ]" in text:
                open_review_gaps.append(review.stem)
        if open_review_gaps:
            issues.append(ReadinessIssue("warning", f"review reports have open checks: {', '.join(open_review_gaps[:8])}"))
    return issues


def next_action(issues: list[ReadinessIssue]) -> str:
    if any(issue.severity == "blocker" for issue in issues):
        return "Resolve readiness blockers, then regenerate the proof pack."
    if issues:
        return "Resolve warnings or explicitly accept them before release."
    return "Ready to promote to the next milestone."


def _tasks(root: Path) -> list[dict]:
    rows = []
    for path in sorted((root / "work").glob("TASK-*.md")):
        text = path.read_text(encoding="utf-8")
        rows.append({"id": path.name.split("-", 2)[0] + "-" + path.name.split("-", 2)[1], "status": "done" if "status: done" in text else "planned", "path": path, "title": _title(path)})
    return rows


def _risk_blocks(root: Path) -> list[str]:
    path = root / "risks.md"
    if not path.exists():
        return []
    blocks = []
    current = ""
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if current and _risk_unmitigated(lines):
                blocks.append(current)
            current = line[3:].strip()
            lines = []
        elif current:
            lines.append(line.strip())
    if current and _risk_unmitigated(lines):
        blocks.append(current)
    return blocks


def _risk_unmitigated(lines: list[str]) -> bool:
    joined = " ".join(lines)
    return "Mitigation:" not in joined or "Mitigation: TBD" in joined or "Status: unresolved" in joined


def _risks(root: Path) -> str:
    path = root / "risks.md"
    if not path.exists():
        return "- None"
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("## ") or line.startswith("- ")]
    return "\n".join(lines) if lines else "- None"


def _vnext_proof_sections(root: Path, graph: dict) -> str:
    return f"""## Methodology Coverage Matrix
{_methodology_coverage(root)}

## Command Coverage
{_command_coverage()}

## Graph Coverage
{_graph_coverage(graph)}

## Cockpit Coverage
{_cockpit_coverage()}

## Remaining Risks
{_vnext_remaining_risks()}
"""


def _methodology_coverage(root: Path) -> str:
    rows = _vnext_methodology_rows()
    lines = [
        "| Stage | Artifact coverage | Command or gate coverage | Responsible role | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for stage, artifacts, commands, role in rows:
        present = sum(1 for rel in artifacts if (root / rel).exists())
        status = "Covered" if present == len(artifacts) else f"Partial ({present}/{len(artifacts)})"
        lines.append(f"| {stage} | {present}/{len(artifacts)} artifacts | `{commands}` | {role} | {status} |")
    return "\n".join(lines)


def _command_coverage() -> str:
    rows = [
        ("discover", "Product Discovery Specification initialization and updates", "Implemented"),
        ("canon", "Discovery-gated product canon generation", "Implemented"),
        ("strategy", "Canon-informed strategy generation", "Implemented"),
        ("requirements", "Strategy-to-requirements generation", "Implemented"),
        ("domain", "Requirements-to-domain generation", "Implemented"),
        ("architecture", "Domain-to-architecture generation", "Implemented"),
        ("roadmap", "Roadmap artifact review after architecture readiness", "Command-backed by `readiness --stage architecture` and `plan`"),
        ("plan", "Product-owner planning and execution task generation", "Implemented through `plan` and `execution-tasks`"),
        ("build", "Repository factory and task implementation packet", "Implemented through `repository-factory` and `build`"),
        ("validate", "Validation summary and evidence target generation", "Implemented"),
        ("release", "Release readiness, proof pack, and release summary", "Implemented through `readiness --stage release`, `proof-pack`, and `release-summary`"),
        ("operate", "Operations learning capture and routed follow-up", "Implemented through `learning` and `learning add`"),
    ]
    lines = [
        "| Lifecycle command | Coverage | Status |",
        "| --- | --- | --- |",
    ]
    for command, coverage, status in rows:
        lines.append(f"| `{command}` | {coverage} | {status} |")
    return "\n".join(lines)


def _graph_coverage(graph: dict) -> str:
    nodes = graph.get("nodes", [])
    by_stage: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for node in nodes:
        if not isinstance(node, dict):
            continue
        stage = str(node.get("stage") or node.get("source_stage") or "unspecified")
        node_type = str(node.get("type") or "unknown")
        by_stage[stage] = by_stage.get(stage, 0) + 1
        by_type[node_type] = by_type.get(node_type, 0) + 1
    expected_stages = [
        "discovery",
        "canon",
        "strategy",
        "requirements",
        "domain",
        "architecture",
        "execution",
        "validation",
        "deployment",
        "operations",
        "governance",
    ]
    lines = [
        f"- Nodes: {len(nodes)}",
        f"- Edges: {len(graph.get('edges', []))}",
        "",
        "| Stage | Nodes | Status |",
        "| --- | ---: | --- |",
    ]
    for stage in expected_stages:
        count = by_stage.get(stage, 0)
        lines.append(f"| {stage} | {count} | {'Covered' if count else 'Missing'} |")
    lines.extend(["", "| Node type | Count |", "| --- | ---: |"])
    for node_type, count in sorted(by_type.items()):
        lines.append(f"| {node_type} | {count} |")
    return "\n".join(lines)


def _cockpit_coverage() -> str:
    rows = [
        ("Discovery", "discover, readiness"),
        ("Canon", "canon, canon-drift"),
        ("Strategy", "strategy, strategy-readiness"),
        ("Requirements", "requirements, readiness"),
        ("Domain", "domain, readiness"),
        ("Architecture", "architecture, readiness"),
        ("Roadmap", "plan, execution-tasks"),
        ("Execution", "next, packet"),
        ("Build", "build, review"),
        ("Validate", "validate, evidence-add"),
        ("Release", "readiness, proof-pack, release-summary"),
        ("Operate", "learning, learning-add"),
        ("Governance", "graph-report, traceability, integrity-audit, contradictions-sync, migration-compatibility"),
    ]
    lines = [
        "| Cockpit stage | Safe action coverage | Status |",
        "| --- | --- | --- |",
    ]
    for stage, actions in rows:
        lines.append(f"| {stage} | `{actions}` | Covered |")
    return "\n".join(lines)


def _vnext_remaining_risks() -> str:
    return "\n".join(
        [
            "- Discovery gate remains blocked for the current Echel product memory until founder-grade PDS fields are completed.",
            "- Release gate remains blocked until production checklist rows are passed or accepted and release evidence is registered.",
            "- Final readiness gate reports existing evidence, stale-doc, and traceability gaps until they are closed or accepted by governance.",
            "- Traceability still needs tighter canon statement linkage before final certification can claim full chain closure.",
        ]
    )


def _vnext_final_checks(
    repo_root: Path,
    cfg: ProjectConfig,
    root: Path,
    graph: dict,
    proof: Path,
    summary: Path,
) -> list[dict]:
    graph_issues = validate_graph(graph)
    critical_graph = [issue.message for issue in graph_issues if issue.severity == "critical"]
    missing_templates = _missing_vnext_templates(root)
    missing_command_docs = _missing_vnext_command_docs(repo_root)
    missing_evidence = _done_tasks_missing_evidence(repo_root, cfg, root)
    unreviewed_major = _unreviewed_major_changes(root)
    missing_release_summary = [] if summary.exists() else [summary.relative_to(root).as_posix()]
    missing_proof = [] if proof.exists() else [proof.relative_to(root).as_posix()]
    return [
        _final_check("No critical graph issues", critical_graph, "Graph validation has no critical findings."),
        _final_check("No missing stage templates", missing_templates, "All required lifecycle stage templates exist."),
        _final_check("No missing command docs", missing_command_docs, "Technical quick start documents the vNext command surface."),
        _final_check("No missing evidence for completed tasks", missing_evidence, "Completed tasks reference registered evidence."),
        _final_check("No unreviewed major changes", unreviewed_major, "Major release changes have review or governance coverage."),
        _final_check("vNext proof pack generated", missing_proof, "vNext proof pack exists."),
        _final_check("vNext release summary generated", missing_release_summary, "vNext release summary exists."),
    ]


def _vnext_final_report(target: str, checks: list[dict], proof: Path, summary: Path) -> str:
    status = "blocked" if any(check["status"] != "PASS" for check in checks) else "ready"
    lines = [
        "---",
        "type: vnext-final-readiness",
        f"status: {status}",
        f"target: {target}",
        "---",
        f"# vNext Final Readiness - {target}",
        "",
        "## Certification",
        f"- Status: {status}",
        f"- Proof pack: [[../proof-packs/{proof.stem}]]",
        f"- Release summary: [[../releases/{summary.stem}]]",
        "",
        "## Gate Checks",
        "",
        "| Check | Status | Findings |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        findings = "; ".join(check["findings"][:8]) if check["findings"] else check["pass_message"]
        if len(check["findings"]) > 8:
            findings += f"; ... {len(check['findings']) - 8} more"
        lines.append(f"| {check['name']} | {check['status']} | {_escape_pipe(findings)} |")
    lines.extend(
        [
            "",
            "## Required Remediation",
        ]
    )
    blockers = [check for check in checks if check["status"] != "PASS"]
    if not blockers:
        lines.append("- None. vNext is ready for release certification.")
    else:
        for check in blockers:
            lines.append(f"- {check['name']}: resolve {len(check['findings'])} finding(s) before certifying vNext as ready.")
    return "\n".join(lines) + "\n"


def _final_check(name: str, findings: list[str], pass_message: str) -> dict:
    return {
        "name": name,
        "status": "PASS" if not findings else "BLOCKED",
        "findings": findings,
        "pass_message": pass_message,
    }


def _missing_vnext_templates(root: Path) -> list[str]:
    missing = []
    for stage, artifacts, _commands, _role in _vnext_methodology_rows():
        for rel in artifacts:
            if not (root / rel).exists():
                missing.append(f"{stage}: wiki/{rel}")
    return missing


def _missing_vnext_command_docs(repo_root: Path) -> list[str]:
    quick_start = repo_root / "docs" / "technical-quick-start.md"
    if not quick_start.exists():
        return ["docs/technical-quick-start.md"]
    text = quick_start.read_text(encoding="utf-8")
    required = [
        "`discover`",
        "`canon`",
        "`strategy`",
        "`requirements`",
        "`domain`",
        "`architecture`",
        "`roadmap`",
        "`plan`",
        "`build`",
        "`validate`",
        "`release`",
        "`operate`",
        "python3 tools/echel.py proof-pack --target vnext",
        "python3 tools/echel.py vnext-final",
    ]
    return [item for item in required if item not in text]


def _done_tasks_missing_evidence(repo_root: Path, cfg: ProjectConfig, root: Path) -> list[str]:
    registry = ensure_registry(Path(repo_root) / cfg.evidence_registry)
    known = set(registry.get("artifacts", {}).keys()) if isinstance(registry, dict) else set()
    missing = []
    for task in _tasks(root):
        if task["status"] != "done":
            continue
        text = task["path"].read_text(encoding="utf-8", errors="ignore")
        links = extract_evidence_links(text)
        if not links:
            missing.append(f"{task['id']}: no evidence reference")
        else:
            unknown = [link for link in links if link not in known]
            if unknown:
                missing.append(f"{task['id']}: unregistered evidence {', '.join(unknown)}")
    return missing


def _unreviewed_major_changes(root: Path) -> list[str]:
    reviews = sorted((root / "reports" / "reviews").glob("*.md"))
    if not reviews:
        return ["No review reports found."]
    open_checks = []
    for review in reviews:
        text = review.read_text(encoding="utf-8", errors="ignore")
        if "- [ ]" in text:
            open_checks.append(f"{review.relative_to(root).as_posix()} has open review checks")
    return open_checks


def _vnext_methodology_rows() -> list[tuple[str, list[str], str, str]]:
    return [
        ("Discovery", ["discovery/product-discovery-spec.md", "discovery/research-plan.md", "discovery/assumptions.md"], "discover, readiness --stage discovery", "Founder Interviewer"),
        ("Canon", ["canon/product-canon.md", "canon/vision.md", "canon/product-principles.md", "canon/non-negotiables.md"], "canon, canon-drift", "Product Manager"),
        ("Strategy", ["strategy/icp.md", "strategy/buyer-user-model.md", "strategy/market-wedge.md", "strategy/competitive-analysis.md", "strategy/positioning.md", "strategy/pricing-and-packaging.md", "strategy/pmf-evidence.md"], "strategy, strategy-readiness", "Product Strategist"),
        ("Requirements", ["requirements/product-requirements.md", "requirements/functional-requirements.md", "requirements/non-functional-requirements.md", "requirements/mvp-scope.md", "requirements/out-of-scope.md", "requirements/acceptance-criteria.md"], "requirements, readiness --stage requirements", "Business Analyst"),
        ("Domain", ["domain/domain-overview.md", "domain/ubiquitous-language.md", "domain/bounded-contexts.md", "domain/entities.md", "domain/aggregates.md", "domain/domain-events.md", "domain/workflows.md", "domain/policies-and-rules.md"], "domain, readiness --stage domain", "Domain Modeler"),
        ("Architecture", ["architecture/overview.md", "architecture/context-map.md", "architecture/component-architecture.md", "architecture/data-architecture.md", "architecture/api-architecture.md", "architecture/event-architecture.md", "architecture/workflow-architecture.md", "architecture/security-architecture.md", "architecture/observability-architecture.md"], "architecture, readiness --stage architecture", "Solution Architect"),
        ("Roadmap", ["roadmap/master-roadmap.md", "roadmap/mvp-roadmap.md", "roadmap/architecture-roadmap.md", "roadmap/engineering-roadmap.md", "roadmap/release-plan.md"], "plan, execution-tasks", "Delivery Planner"),
        ("Execution", ["execution/phase-0-foundation.md", "execution/phase-1-mvp.md", "execution/phase-2-hardening.md", "execution/phase-3-production.md", "execution/phase-4-evolution.md", "work/TASK_INDEX.md"], "execution-tasks, packet, next", "Delivery Planner"),
        ("Build", ["engineering/development-workflow.md", "engineering/local-development.md"], "repository-factory, build, review", "Implementation Agent"),
        ("Validate", ["validation/test-strategy.md", "validation/acceptance-tests.md", "validation/integration-tests.md", "validation/e2e-tests.md", "validation/security-tests.md", "validation/performance-tests.md", "validation/validation-report.md"], "validate, evidence add", "QA Agent"),
        ("Release", ["deployment/deployment-architecture.md", "deployment/environments.md", "deployment/release-process.md", "deployment/rollback-plan.md", "deployment/secrets-management.md", "deployment/production-checklist.md"], "readiness --stage release, proof-pack, release-summary", "Release Manager"),
        ("Operate", ["operations/runbook.md", "operations/observability.md", "operations/incident-response.md", "operations/backup-and-recovery.md", "operations/sla-and-slo.md", "operations/change-management.md", "operations/evolution-backlog.md", "operations/learning-records.md"], "learning, learning add", "Operations Steward"),
        ("Governance", ["governance/documentation-governance.md", "governance/architecture-governance.md", "governance/adr-process.md", "governance/traceability-model.md", "governance/quality-gates.md", "governance/repository-integrity-audit.md", "governance/contradictions.md", "governance/migration-compatibility.md"], "traceability, integrity audit, contradictions sync, migration compatibility", "Governance Auditor"),
    ]


def _escape_pipe(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _format_tasks(tasks: list[dict]) -> str:
    if not tasks:
        return "- None"
    return "\n".join(f"- {task['id']} ({task['status']}): {task['title']}" for task in tasks)


def _format_paths(root: Path, paths: list[Path], from_dir: Path) -> str:
    links = []
    for path in paths:
        rel = path.with_suffix("").relative_to(root)
        source_rel = from_dir.relative_to(root)
        target = Path(rel)
        prefix = Path("..")
        try:
            target = Path(*([".."] * len(source_rel.parts))) / rel
        except TypeError:
            target = prefix / rel
        links.append(f"- [[{target.as_posix()}]]")
    return "\n".join(links)


def _format_issues(issues: list[ReadinessIssue]) -> str:
    if not issues:
        return "- None"
    return "\n".join(f"- **{issue.severity}** {issue.message}" for issue in issues)


def _status_label(issues: list[ReadinessIssue]) -> str:
    if any(issue.severity == "blocker" for issue in issues):
        return "blocked"
    if issues:
        return "at risk"
    return "ready"


def _report_files(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [{"title": _title(item) or item.stem, "path": str(item)} for item in sorted(path.glob("*.md"))]


def _title(path: Path) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80] or "target"


def _append_log(root: Path, label: str, line: str) -> None:
    log = root / "log.md"
    if not log.exists():
        log.write_text("---\ntype: log\nstatus: active\n---\n# Log\n", encoding="utf-8")
    stamp = datetime.now(timezone.utc).date().isoformat()
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{stamp}] {label} | readiness\n- {line}\n")
