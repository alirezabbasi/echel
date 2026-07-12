from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
import subprocess

from ..config import ConfigError, load_config, resolve_symbolic_path
from ..gates import run_stage_gate
from ..graph import build_graph, graph_summary, validate_graph
from ..memory_kernel import query_records
from ..product import clarification_gaps, product_status
from ..readiness import readiness_snapshot


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    code: int
    output: str


SAFE_COMMANDS = {
    "clarify": ["clarify"],
    "discover": ["discover"],
    "canon": ["canon"],
    "canon-drift": ["canon-drift"],
    "strategy": ["strategy"],
    "strategy-readiness": ["strategy-readiness"],
    "requirements": ["requirements"],
    "domain": ["domain"],
    "architecture": ["architecture"],
    "execution-tasks": ["execution-tasks"],
    "repository-factory": ["repository-factory"],
    "steer": ["steer"],
    "plan": ["plan"],
    "packet": ["packet"],
    "build": ["build"],
    "review": ["review"],
    "graph-report": ["graph", "report"],
    "traceability": ["traceability"],
    "validate": ["validate"],
    "evidence-add": ["evidence", "add"],
    "learning": ["learning"],
    "learning-add": ["learning", "add"],
    "readiness": ["readiness"],
    "proof-pack": ["proof-pack"],
    "release-summary": ["release-summary"],
    "status": ["status"],
    "next": ["next"],
}


def cockpit_snapshot(repo_root: Path) -> dict:
    cfg = load_config(repo_root)
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    graph = build_graph(repo_root, cfg)
    graph_issues = validate_graph(graph)
    tasks = _tasks(wiki)
    risks = _heading_items(wiki / "risks.md")
    decisions = _decisions(wiki)
    packets = _report_files(wiki / "reports" / "work-packets")
    reviews = _report_files(wiki / "reports" / "reviews")
    gaps = clarification_gaps(repo_root, cfg)
    lifecycle = _lifecycle_stages(repo_root, cfg, wiki, tasks, graph_issues)

    return {
        "project": {
            "title": _title(wiki / "project.md") or "Product",
            "problem": _section(wiki / "problem.md", "Problem Statement"),
            "solution": _section(wiki / "solution.md", "Solution Concept"),
            "direction": _section(wiki / "project.md", "Product Direction"),
            "success": _section(wiki / "project.md", "Success Criteria"),
        },
        "readiness": {
            "clarification_open": len(gaps),
            "mvp_ready": not any(field.key in {"problem", "users", "solution", "mvp", "success"} for field in gaps),
            "open_tasks": sum(1 for item in tasks if item["status"] != "done"),
            "done_tasks": sum(1 for item in tasks if item["status"] == "done"),
            "graph_critical": sum(1 for issue in graph_issues if issue.severity == "critical"),
            "graph_major": sum(1 for issue in graph_issues if issue.severity == "major"),
        },
        "clarifications": [asdict(field) for field in gaps],
        "roadmap": {
            "now": _bullets(_section(wiki / "roadmap.md", "Now")),
            "mvp": _bullets(_section(wiki / "roadmap.md", "MVP")),
            "next": _bullets(_section(wiki / "roadmap.md", "Next")),
            "later": _bullets(_section(wiki / "roadmap.md", "Later")),
        },
        "work": {
            "tasks": tasks,
            "next": _run_safe(repo_root, "next", {})["output"].strip(),
            "packets": packets,
            "reviews": reviews,
        },
        "graph": {
            "summary": graph_summary(graph, graph_issues),
            "nodes": graph.get("nodes", []),
            "edges": graph.get("edges", []),
            "issues": [asdict(issue) for issue in graph_issues],
        },
        "architecture": {
            "system": _section(wiki / "architecture.md", "System Shape"),
            "components": _bullets(_section(wiki / "architecture.md", "Key Components")),
            "stack": _bullets(_section(wiki / "architecture.md", "Preferred Stack")),
            "workflows": _bullets(_section(wiki / "workflows.md", "Core Workflows")),
        },
        "contradictions": [
            {"id": rec.record_id, "title": rec.title, "type": rec.record_type, "links": rec.links}
            for rec in query_records(repo_root, contradiction_only=True)
        ],
        "agent_activity": {
            "packets": packets[-10:],
            "reviews": reviews[-10:],
            "log": _recent_log(wiki / "log.md"),
        },
        "risks": risks,
        "decisions": decisions,
        "readiness_detail": readiness_snapshot(repo_root, cfg),
        "lifecycle": lifecycle,
        "status_markdown": product_status(repo_root, cfg),
    }


def run_cockpit_command(repo_root: Path, action: str, args: dict | None = None) -> CommandResult:
    args = args or {}
    try:
        result = _run_safe(repo_root, action, args)
    except ConfigError as exc:
        return CommandResult(False, 2, f"CONFIG_ERROR: {exc}")
    return CommandResult(result["code"] == 0, result["code"], result["output"])


def _run_safe(repo_root: Path, action: str, args: dict) -> dict:
    base = SAFE_COMMANDS.get(action)
    if base is None:
        return {"code": 1, "output": f"blocked action; allowed: {', '.join(sorted(SAFE_COMMANDS))}"}
    cmd = ["python3", "tools/echel.py", *base]
    if action == "clarify":
        field = str(args.get("field", "")).strip()
        answer = str(args.get("answer", "")).strip()
        if not field or not answer:
            return {"code": 2, "output": "clarify requires field and answer"}
        cmd.extend(["--field", field, "--answer", answer])
    elif action == "discover":
        field = str(args.get("field", "")).strip()
        value = str(args.get("value", "")).strip()
        if bool(field) != bool(value):
            return {"code": 2, "output": "discover requires both field and value when updating discovery"}
        if field and value:
            cmd.extend(["--field", field, "--value", value])
    elif action == "steer":
        field = str(args.get("field", "")).strip()
        value = str(args.get("value", "")).strip()
        if not field or not value:
            return {"code": 2, "output": "steer requires field and value"}
        cmd.extend(["--field", field, "--value", value])
    elif action in {"canon", "strategy", "requirements", "domain", "architecture", "execution-tasks", "repository-factory"} and args.get("force"):
        cmd.append("--force")
    if action == "repository-factory" and args.get("output"):
        cmd.extend(["--output", str(args["output"])])
    elif action in {"packet", "build", "review"} and args.get("task"):
        cmd.extend(["--task", str(args["task"])])
    elif action == "readiness" and args.get("stage"):
        cmd.extend(["--stage", str(args["stage"])])
    elif action in {"readiness", "proof-pack", "release-summary"} and args.get("target"):
        cmd.extend(["--target", str(args["target"])])
    elif action == "evidence-add":
        required = ["subject", "kind", "path", "producer", "summary"]
        missing = [key for key in required if not str(args.get(key, "")).strip()]
        if missing:
            return {"code": 2, "output": f"evidence add requires: {', '.join(missing)}"}
        if args.get("id"):
            cmd.extend(["--id", str(args["id"])])
        for key in required:
            cmd.extend([f"--{key}", str(args[key])])
        if args.get("checksum"):
            cmd.extend(["--checksum", str(args["checksum"])])
    elif action == "learning-add":
        required = ["source_kind", "title", "summary", "action"]
        missing = [key for key in required if not str(args.get(key, "")).strip()]
        if missing:
            return {"code": 2, "output": f"learning add requires: {', '.join(missing)}"}
        cmd.extend(["--source-kind", str(args["source_kind"])])
        cmd.extend(["--title", str(args["title"])])
        cmd.extend(["--summary", str(args["summary"])])
        cmd.extend(["--action", str(args["action"])])
        for key in ["owner", "severity", "source_id"]:
            if args.get(key):
                cmd.extend([f"--{key.replace('_', '-')}", str(args[key])])
    proc = subprocess.run(cmd, cwd=repo_root, text=True, capture_output=True)
    return {"code": proc.returncode, "output": (proc.stdout + "\n" + proc.stderr).strip()[:12000]}


def _lifecycle_stages(repo_root: Path, cfg, wiki: Path, tasks: list[dict], graph_issues: list) -> dict:
    force_field = {"name": "force", "label": "Force", "type": "checkbox", "required": False}
    target_field = {"name": "target", "label": "Target", "type": "text", "default": "mvp", "required": False}
    specs = [
        {
            "id": "discovery",
            "title": "Discovery",
            "role": "Founder Interviewer",
            "artifacts": ["discovery/product-discovery-spec.md", "discovery/research-plan.md", "discovery/assumptions.md"],
            "gate": "discovery",
            "next_action": "Answer discovery gaps or run `python3 tools/echel.py discover`.",
            "safe_actions": [
                {"label": "List Discovery Gaps", "action": "discover", "args": {}, "description": "Inspect missing Product Discovery Specification fields."},
                {
                    "label": "Answer Discovery Field",
                    "action": "discover",
                    "args": {},
                    "description": "Write a discovery answer into the PDS.",
                    "fields": [
                        {"name": "field", "label": "Field", "type": "text", "required": True, "placeholder": "problem"},
                        {"name": "value", "label": "Answer", "type": "textarea", "required": True},
                    ],
                },
                {"label": "Check Discovery", "action": "readiness", "args": {"stage": "discovery"}, "description": "Run the discovery stage gate."},
            ],
        },
        {
            "id": "canon",
            "title": "Canon",
            "role": "Product Manager",
            "artifacts": ["canon/product-canon.md", "canon/vision.md", "canon/product-principles.md", "canon/non-negotiables.md"],
            "next_action": "Refresh product canon from gated discovery.",
            "safe_actions": [
                {"label": "Generate Canon", "action": "canon", "args": {}, "description": "Generate or refresh canon files from discovery.", "fields": [force_field]},
                {"label": "Check Canon Drift", "action": "canon-drift", "args": {}, "description": "Detect contradictions between discovery and canon."},
            ],
        },
        {
            "id": "strategy",
            "title": "Strategy",
            "role": "Strategy Analyst",
            "artifacts": [
                "strategy/icp.md",
                "strategy/buyer-user-model.md",
                "strategy/market-wedge.md",
                "strategy/competitive-analysis.md",
                "strategy/positioning.md",
                "strategy/pricing-and-packaging.md",
                "strategy/pmf-evidence.md",
            ],
            "next_action": "Review ICP, buyer/user model, wedge, PMF evidence, and pricing hypotheses.",
            "safe_actions": [
                {"label": "Evaluate Strategy", "action": "strategy-readiness", "args": {}, "description": "Check strategy readiness before requirements."},
                {"label": "Generate Strategy", "action": "strategy", "args": {}, "description": "Generate strategy artifacts from canon.", "fields": [force_field]},
            ],
        },
        {
            "id": "requirements",
            "title": "Requirements",
            "role": "Product Manager",
            "artifacts": [
                "requirements/product-requirements.md",
                "requirements/functional-requirements.md",
                "requirements/non-functional-requirements.md",
                "requirements/mvp-scope.md",
                "requirements/out-of-scope.md",
                "requirements/acceptance-criteria.md",
            ],
            "gate": "requirements",
            "next_action": "Run requirement readiness before domain work.",
            "safe_actions": [
                {"label": "Generate Requirements", "action": "requirements", "args": {}, "description": "Generate requirements from canon and strategy.", "fields": [force_field]},
                {"label": "Check Requirements", "action": "readiness", "args": {"stage": "requirements"}, "description": "Run the requirements stage gate."},
            ],
        },
        {
            "id": "domain",
            "title": "Domain",
            "role": "Domain Modeler",
            "artifacts": [
                "domain/domain-overview.md",
                "domain/ubiquitous-language.md",
                "domain/bounded-contexts.md",
                "domain/entities.md",
                "domain/aggregates.md",
                "domain/domain-events.md",
                "domain/workflows.md",
                "domain/policies-and-rules.md",
            ],
            "gate": "domain",
            "next_action": "Resolve domain coverage, duplicate terms, or technology leakage before architecture.",
            "safe_actions": [
                {"label": "Build Domain Model", "action": "domain", "args": {}, "description": "Generate domain artifacts from gated requirements.", "fields": [force_field]},
                {"label": "Check Domain", "action": "readiness", "args": {"stage": "domain"}, "description": "Run the domain stage gate."},
            ],
        },
        {
            "id": "architecture",
            "title": "Architecture",
            "role": "Solution Architect",
            "artifacts": [
                "architecture/overview.md",
                "architecture/context-map.md",
                "architecture/component-architecture.md",
                "architecture/data-architecture.md",
                "architecture/api-architecture.md",
                "architecture/event-architecture.md",
                "architecture/workflow-architecture.md",
                "architecture/security-architecture.md",
                "architecture/observability-architecture.md",
            ],
            "gate": "architecture",
            "next_action": "Pass architecture readiness before roadmap and repository-factory work.",
            "safe_actions": [
                {"label": "Generate Architecture", "action": "architecture", "args": {}, "description": "Generate architecture mappings from gated domain artifacts.", "fields": [force_field]},
                {"label": "Check Architecture", "action": "readiness", "args": {"stage": "architecture"}, "description": "Run the architecture stage gate."},
            ],
        },
        {
            "id": "roadmap",
            "title": "Roadmap",
            "role": "Delivery Planner",
            "artifacts": [
                "roadmap/master-roadmap.md",
                "roadmap/mvp-roadmap.md",
                "roadmap/architecture-roadmap.md",
                "roadmap/engineering-roadmap.md",
                "roadmap/release-plan.md",
            ],
            "next_action": "Keep phase objectives, dependencies, demos, risks, and exit gates current.",
            "safe_actions": [
                {"label": "Create Roadmap Plan", "action": "plan", "args": {}, "description": "Synthesize current planning output."},
                {"label": "Generate Execution Tasks", "action": "execution-tasks", "args": {}, "description": "Create agent-executable tasks from phase rows.", "fields": [force_field]},
            ],
        },
        {
            "id": "execution",
            "title": "Execution",
            "role": "Delivery Planner",
            "artifacts": [
                "execution/phase-0-foundation.md",
                "execution/phase-1-mvp.md",
                "execution/phase-2-hardening.md",
                "execution/phase-3-production.md",
                "execution/phase-4-evolution.md",
                "work/TASK_INDEX.md",
            ],
            "next_action": "Select the next planned task packet and verify dependencies.",
            "safe_actions": [
                {"label": "Next Task", "action": "next", "args": {}, "description": "Select the next graph-aware task."},
                {"label": "Create Work Packet", "action": "packet", "args": {}, "description": "Generate or inspect a task packet.", "fields": [{"name": "task", "label": "Task ID", "type": "text", "required": False, "placeholder": "TASK-1017"}]},
            ],
        },
        {
            "id": "build",
            "title": "Build",
            "role": "Implementation Agent",
            "artifacts": ["engineering/development-workflow.md", "engineering/local-development.md"],
            "next_action": "Generate or inspect the current build packet before changing code.",
            "safe_actions": [
                {"label": "Build Packet", "action": "build", "args": {}, "description": "Create implementation handoff for the selected task.", "fields": [{"name": "task", "label": "Task ID", "type": "text", "required": False, "placeholder": "TASK-1017"}]},
                {"label": "Review Task", "action": "review", "args": {}, "description": "Create a review report for a task.", "fields": [{"name": "task", "label": "Task ID", "type": "text", "required": False, "placeholder": "TASK-1017"}]},
            ],
        },
        {
            "id": "validate",
            "title": "Validate",
            "role": "QA Agent",
            "artifacts": [
                "validation/test-strategy.md",
                "validation/acceptance-tests.md",
                "validation/integration-tests.md",
                "validation/e2e-tests.md",
                "validation/security-tests.md",
                "validation/performance-tests.md",
                "validation/validation-report.md",
            ],
            "next_action": "Refresh validation summary and register missing evidence.",
            "safe_actions": [
                {"label": "Run Validation Summary", "action": "validate", "args": {}, "description": "Refresh validation report and graph evidence targets."},
                {
                    "label": "Register Evidence",
                    "action": "evidence-add",
                    "args": {},
                    "description": "Add checksum-backed evidence for task closure or release.",
                    "fields": [
                        {"name": "id", "label": "Evidence ID", "type": "text", "required": False, "placeholder": "EVID-001"},
                        {"name": "subject", "label": "Subject", "type": "text", "required": True, "placeholder": "TASK-1017"},
                        {"name": "kind", "label": "Kind", "type": "text", "required": True, "placeholder": "test"},
                        {"name": "path", "label": "Path", "type": "text", "required": True, "placeholder": "wiki/reports/..."},
                        {"name": "producer", "label": "Producer", "type": "text", "required": True, "default": "QA Agent"},
                        {"name": "summary", "label": "Summary", "type": "textarea", "required": True},
                    ],
                },
            ],
        },
        {
            "id": "release",
            "title": "Release",
            "role": "Release Manager",
            "artifacts": [
                "deployment/deployment-architecture.md",
                "deployment/environments.md",
                "deployment/release-process.md",
                "deployment/rollback-plan.md",
                "deployment/secrets-management.md",
                "deployment/production-checklist.md",
            ],
            "gate": "release",
            "next_action": "Resolve release blockers: checklist rows, evidence, validation blockers, rollback, or risk acceptance.",
            "safe_actions": [
                {"label": "Check Release", "action": "readiness", "args": {"stage": "release"}, "description": "Run the release stage gate."},
                {"label": "Create Proof Pack", "action": "proof-pack", "args": {}, "description": "Generate proof pack for a target.", "fields": [target_field]},
                {"label": "Release Summary", "action": "release-summary", "args": {}, "description": "Generate release summary for a target.", "fields": [target_field]},
            ],
        },
        {
            "id": "operate",
            "title": "Operate",
            "role": "Operations Steward",
            "artifacts": [
                "operations/runbook.md",
                "operations/observability.md",
                "operations/incident-response.md",
                "operations/backup-and-recovery.md",
                "operations/sla-and-slo.md",
                "operations/change-management.md",
                "operations/evolution-backlog.md",
                "operations/learning-records.md",
            ],
            "next_action": "Capture operational learning and route follow-up through governed memory.",
            "safe_actions": [
                {"label": "Learning Status", "action": "learning", "args": {}, "description": "Inspect operation learning records."},
                {
                    "label": "Record Learning",
                    "action": "learning-add",
                    "args": {},
                    "description": "Route incident, RCA, feedback, roadmap, or strategy learning into product memory.",
                    "fields": [
                        {"name": "source_kind", "label": "Source", "type": "select", "required": True, "options": ["incident", "rca", "feedback", "roadmap-change", "strategy-change"]},
                        {"name": "title", "label": "Title", "type": "text", "required": True},
                        {"name": "summary", "label": "Summary", "type": "textarea", "required": True},
                        {"name": "action", "label": "Action", "type": "select", "required": True, "options": ["task", "adr", "risk", "assumption", "strategy-change", "none"]},
                        {"name": "owner", "label": "Owner", "type": "text", "required": False, "default": "Operations Steward"},
                        {"name": "severity", "label": "Severity", "type": "text", "required": False, "default": "medium"},
                    ],
                },
            ],
        },
        {
            "id": "governance",
            "title": "Governance",
            "role": "Governance Auditor",
            "artifacts": ["reports/traceability-matrix.md", "reports/product-graph-report.md", "reports/wiki-health-report.md"],
            "next_action": "Audit source-of-truth integrity, traceability, graph health, and stale artifacts.",
            "safe_actions": [
                {"label": "Graph Report", "action": "graph-report", "args": {}, "description": "Regenerate product graph report."},
                {"label": "Traceability Matrix", "action": "traceability", "args": {}, "description": "Regenerate lifecycle traceability matrix."},
                {"label": "Status", "action": "status", "args": {}, "description": "Inspect current product status."},
            ],
        },
    ]
    stages = []
    for spec in specs:
        blockers = []
        for rel in spec["artifacts"]:
            path = wiki / rel
            if not path.exists():
                blockers.append(f"missing artifact: wiki/{rel}")
        gate_id = spec.get("gate")
        if gate_id:
            result = run_stage_gate(repo_root, cfg, gate_id)
            blockers.extend(result.failures)
        if spec["id"] == "execution":
            open_tasks = sum(1 for item in tasks if item["status"] != "done")
            if not tasks:
                blockers.append("no execution tasks found")
            elif open_tasks:
                spec = {**spec, "next_action": f"Continue the next planned task; {open_tasks} task(s) remain open."}
        if spec["id"] == "build" and not any(item["status"] != "done" for item in tasks):
            spec = {**spec, "next_action": "No open task is ready for build; return to roadmap or evolution planning."}
        if spec["id"] == "governance" and graph_issues:
            blockers.extend(f"{issue.severity}: {issue.message}" for issue in graph_issues[:8])
        status = "blocked" if blockers else "ready"
        safe_actions = spec.get("safe_actions") or [spec["safe_action"]]
        stages.append(
            {
                "id": spec["id"],
                "title": spec["title"],
                "status": status,
                "role": spec["role"],
                "blockers": blockers,
                "next_action": spec["next_action"],
                "safe_action": safe_actions[0],
                "safe_actions": safe_actions,
                "artifacts": spec["artifacts"],
            }
        )
    current = next((stage for stage in stages if stage["status"] == "blocked"), stages[-1] if stages else {})
    return {"current": current, "stages": stages}


def _tasks(wiki: Path) -> list[dict]:
    rows = []
    for path in sorted((wiki / "work").glob("TASK-*.md")):
        text = path.read_text(encoding="utf-8")
        rows.append(
            {
                "id": path.name.split("-", 2)[0] + "-" + path.name.split("-", 2)[1],
                "title": _title(path) or path.stem,
                "status": "done" if "status: done" in text else "planned",
                "objective": _section_text(text, "Objective"),
                "path": str(path.relative_to(wiki)),
            }
        )
    return rows


def _decisions(wiki: Path) -> list[dict]:
    rows = []
    for path in sorted((wiki / "decisions").glob("ADR-*.md")):
        match = re.search(r"(ADR-\d{4})", path.name)
        rows.append({"id": match.group(1) if match else path.stem, "title": _title(path) or path.stem, "path": str(path.relative_to(wiki))})
    return rows


def _report_files(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [{"title": _title(item) or item.stem, "path": str(item)} for item in sorted(path.glob("*.md"))]


def _heading_items(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    current = ""
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if current:
                rows.append({"title": current, "summary": " ".join(lines).strip()})
            current = line[3:].strip()
            lines = []
        elif current:
            lines.append(line.strip())
    if current:
        rows.append({"title": current, "summary": " ".join(lines).strip()})
    return rows


def _section(path: Path, heading: str) -> str:
    if not path.exists():
        return ""
    return _section_text(path.read_text(encoding="utf-8"), heading)


def _section_text(text: str, heading: str) -> str:
    match = re.search(rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)", text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _bullets(text: str) -> list[str]:
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            rows.append(stripped[2:].strip())
        elif stripped:
            rows.append(stripped)
    return rows


def _title(path: Path) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _recent_log(path: Path) -> list[str]:
    if not path.exists():
        return []
    headings = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("## ")]
    return headings[-10:]
