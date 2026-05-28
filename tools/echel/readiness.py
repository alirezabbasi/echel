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
