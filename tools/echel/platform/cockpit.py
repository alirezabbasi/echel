from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
import subprocess

from ..config import ConfigError, load_config, resolve_symbolic_path
from ..graph import build_graph, graph_summary, validate_graph
from ..product import clarification_gaps, product_status


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    code: int
    output: str


SAFE_COMMANDS = {
    "clarify": ["clarify"],
    "plan": ["plan"],
    "build": ["build"],
    "review": ["review"],
    "graph-report": ["graph", "report"],
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
        "risks": risks,
        "decisions": decisions,
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
    elif action in {"build", "review"} and args.get("task"):
        cmd.extend(["--task", str(args["task"])])
    proc = subprocess.run(cmd, cwd=repo_root, text=True, capture_output=True)
    return {"code": proc.returncode, "output": (proc.stdout + "\n" + proc.stderr).strip()[:12000]}


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
