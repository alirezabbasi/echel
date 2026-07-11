from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path
from .graph import write_graph


SUMMARY_REPORT = "reports/validation-summary.md"
VALIDATION_REPORT = "validation/validation-report.md"


@dataclass(frozen=True)
class ValidationItem:
    test_id: str
    title: str
    source: str
    requirement_ids: tuple[str, ...]
    task_ids: tuple[str, ...]
    domain_ids: tuple[str, ...]
    acceptance_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    status: str


@dataclass(frozen=True)
class ValidationIssue:
    issue_id: str
    kind: str
    title: str
    owner_task: str
    status: str
    source: str


@dataclass(frozen=True)
class ValidationSummary:
    passed: int
    failed: int
    skipped: int
    blocked: int
    planned: int
    risks: tuple[ValidationIssue, ...]
    blockers: tuple[ValidationIssue, ...]


def run_validation(repo_root: Path, cfg: ProjectConfig) -> tuple[Path, ValidationSummary]:
    root = _wiki_root(repo_root, cfg)
    items = collect_validation_items(repo_root, cfg)
    risks, blockers = collect_validation_issues(repo_root, cfg)
    summary = summarize_validation(items, risks, blockers)
    report = render_validation_summary(items, summary, title="Validation Summary")
    validation_report = render_validation_summary(items, summary, title="Validation Report")
    report_path = root / SUMMARY_REPORT
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    (root / VALIDATION_REPORT).write_text(validation_report, encoding="utf-8")
    _upsert_graph_nodes(repo_root, cfg, items)
    write_graph(repo_root, cfg)
    return report_path, summary


def collect_validation_items(repo_root: Path, cfg: ProjectConfig) -> list[ValidationItem]:
    root = _wiki_root(repo_root, cfg)
    validation_root = root / "validation"
    items: dict[str, ValidationItem] = {}
    for path in sorted(validation_root.glob("*.md")):
        if path.name == "validation-report.md":
            continue
        for row in _table_rows(path):
            test_id = row[0] if row and re.fullmatch(r"TEST-[A-Z0-9-]+", row[0]) else ""
            if not test_id:
                continue
            title = _clean(row[1] if len(row) > 1 else test_id)
            raw = " ".join(row)
            status = _normalize_status(row[-1] if row else "")
            items[test_id] = ValidationItem(
                test_id=test_id,
                title=title or test_id,
                source=str(path.relative_to(root)),
                requirement_ids=tuple(_ids(raw, r"\b(?:REQ|NFR)-\d+\b")),
                task_ids=tuple(_ids(raw, r"\bTASK-\d+\b")),
                domain_ids=tuple(_ids(raw, r"\b(?:DM|BC|AGG|DE|BR|ARCH|WF-DM)-\d+\b")),
                acceptance_ids=tuple(_ids(raw, r"\bAC-\d+\b")),
                evidence_ids=tuple(_ids(raw, r"\bEVID-[A-Z0-9-]+\b")),
                status=status,
            )
    return sorted(items.values(), key=lambda item: _sort_key(item.test_id))


def collect_validation_issues(repo_root: Path, cfg: ProjectConfig) -> tuple[tuple[ValidationIssue, ...], tuple[ValidationIssue, ...]]:
    root = _wiki_root(repo_root, cfg)
    validation_root = root / "validation"
    risks: dict[str, ValidationIssue] = {}
    blockers: dict[str, ValidationIssue] = {}
    for path in sorted(validation_root.glob("*.md")):
        if path.name == "validation-report.md":
            continue
        for row in _table_rows(path):
            raw = " ".join(row)
            issue_id = _first_id(row, r"\b(?:VAL|SEC)-(?:RISK|BLOCK)-\d+\b")
            if not issue_id:
                continue
            issue = ValidationIssue(
                issue_id=issue_id,
                kind="blocker" if "BLOCK" in issue_id else "risk",
                title=_clean(row[1] if len(row) > 1 else issue_id),
                owner_task=", ".join(_ids(raw, r"\bTASK-\d+\b")) or "Unassigned",
                status=_normalize_issue_status(row[-1] if row else ""),
                source=str(path.relative_to(root)),
            )
            if issue.kind == "blocker":
                blockers[issue.issue_id] = issue
            else:
                risks[issue.issue_id] = issue
    return (
        tuple(sorted(risks.values(), key=lambda issue: issue.issue_id)),
        tuple(sorted(blockers.values(), key=lambda issue: issue.issue_id)),
    )


def summarize_validation(
    items: list[ValidationItem],
    risks: tuple[ValidationIssue, ...],
    blockers: tuple[ValidationIssue, ...],
) -> ValidationSummary:
    passed = sum(1 for item in items if item.status == "passed")
    failed = sum(1 for item in items if item.status == "failed")
    skipped = sum(1 for item in items if item.status == "skipped")
    blocked_items = sum(1 for item in items if item.status == "blocked")
    planned = sum(1 for item in items if item.status == "planned")
    open_blockers = sum(1 for issue in blockers if issue.status == "open")
    return ValidationSummary(
        passed=passed,
        failed=failed,
        skipped=skipped + planned,
        blocked=blocked_items + open_blockers,
        planned=planned,
        risks=risks,
        blockers=blockers,
    )


def render_validation_summary(items: list[ValidationItem], summary: ValidationSummary, title: str = "Validation Summary") -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "---",
        "type: validation-report",
        "status: active",
        "stage: validation",
        "---",
        f"# {title}",
        "",
        f"Generated by `python3 tools/echel.py validate` at `{generated_at}`.",
        "",
        "## Current Summary",
        "",
        "| Passed | Failed | Skipped | Blocked | Planned | Risks | Blockers |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| {summary.passed} | {summary.failed} | {summary.skipped} | {summary.blocked} | {summary.planned} | {len(summary.risks)} | {len(summary.blockers)} |",
        "",
        "## Validation Items",
        "",
        "| Test ID | Status | Requirements | Tasks | Domain IDs | Acceptance Criteria | Evidence Targets | Source |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{item.test_id}`",
                    item.status.title(),
                    _join(item.requirement_ids),
                    _join(item.task_ids),
                    _join(item.domain_ids),
                    _join(item.acceptance_ids),
                    _join(item.evidence_ids),
                    item.source,
                ]
            )
            + " |"
        )
    lines.extend(["", "## Risks", ""])
    if summary.risks:
        lines.extend(["| Risk ID | Status | Owner Task | Source | Description |", "| --- | --- | --- | --- | --- |"])
        for issue in summary.risks:
            lines.append(f"| `{issue.issue_id}` | {issue.status.title()} | {issue.owner_task} | {issue.source} | {_escape(issue.title)} |")
    else:
        lines.append("- No validation risks found.")
    lines.extend(["", "## Blockers", ""])
    if summary.blockers:
        lines.extend(["| Blocker ID | Status | Owner Task | Source | Description |", "| --- | --- | --- | --- | --- |"])
        for issue in summary.blockers:
            lines.append(f"| `{issue.issue_id}` | {issue.status.title()} | {issue.owner_task} | {issue.source} | {_escape(issue.title)} |")
    else:
        lines.append("- No validation blockers found.")
    lines.extend(
        [
            "",
            "## Graph Updates",
            "",
            f"- Test nodes upserted: {len(items)}",
            f"- Evidence target nodes upserted: {len({evid for item in items for evid in item.evidence_ids})}",
            "- Product graph regenerated after validation summary.",
            "",
            "## Handoff To Evidence",
            "",
            "TASK-0034 / TASK-1013 should turn evidence targets into registered evidence records with subject, kind, path, checksum, producer, and summary.",
        ]
    )
    return "\n".join(lines) + "\n"


def _upsert_graph_nodes(repo_root: Path, cfg: ProjectConfig, items: list[ValidationItem]) -> None:
    root = _wiki_root(repo_root, cfg)
    path = root / "graph.manual.json"
    manual = _manual_graph(path)
    nodes = manual.setdefault("nodes", [])
    edges = manual.setdefault("edges", [])

    def upsert_node(node: dict) -> None:
        for idx, existing in enumerate(nodes):
            if isinstance(existing, dict) and existing.get("id") == node["id"]:
                nodes[idx] = {**existing, **node}
                return
        nodes.append(node)

    def upsert_edge(edge: dict) -> None:
        if edge not in edges:
            edges.append(edge)

    evidence_ids = sorted({evid for item in items for evid in item.evidence_ids})
    for item in items:
        test_node = f"test:{item.test_id}"
        upsert_node(
            {
                "id": test_node,
                "type": "test",
                "title": f"{item.test_id} {item.title}",
                "source": item.source,
                "summary": item.title,
                "trace_id": item.test_id,
                "statement_type": "fact",
                "confidence": "medium",
                "source_stage": "validation",
                "verification_status": _graph_status(item.status),
            }
        )
        upsert_edge({"from_id": "product:root", "to_id": test_node, "type": "has_validation"})
        for req_id in item.requirement_ids:
            upsert_edge({"from_id": test_node, "to_id": f"requirement:{req_id}", "type": "verifies"})
        for task_id in item.task_ids:
            upsert_edge({"from_id": test_node, "to_id": f"task:{task_id}", "type": "validates"})
        for domain_id in item.domain_ids:
            upsert_edge({"from_id": test_node, "to_id": _domain_node_id(domain_id), "type": "covers"})
        for evidence_id in item.evidence_ids:
            evidence_node = f"evidence:{evidence_id}"
            upsert_edge({"from_id": evidence_node, "to_id": test_node, "type": "evidence_for"})

    for evidence_id in evidence_ids:
        upsert_node(
            {
                "id": f"evidence:{evidence_id}",
                "type": "evidence",
                "title": evidence_id,
                "source": VALIDATION_REPORT,
                "summary": "Validation evidence target; registration is handled by TASK-0034.",
                "trace_id": evidence_id,
                "statement_type": "fact",
                "confidence": "low",
                "source_stage": "validation",
                "verification_status": "planned",
            }
        )
        upsert_edge({"from_id": "product:root", "to_id": f"evidence:{evidence_id}", "type": "expects_evidence"})

    manual["version"] = 1
    path.write_text(json.dumps(manual, indent=2) + "\n", encoding="utf-8")


def _table_rows(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip().strip("`") for cell in stripped.strip("|").split("|")]
        rows.append(cells)
    return rows


def _manual_graph(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "nodes": [], "edges": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "nodes": [], "edges": []}
    if not isinstance(raw, dict):
        return {"version": 1, "nodes": [], "edges": []}
    raw.setdefault("version", 1)
    raw.setdefault("nodes", [])
    raw.setdefault("edges", [])
    return raw


def _wiki_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    return resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)


def _first_id(row: list[str], pattern: str) -> str:
    match = re.search(pattern, " ".join(row))
    return match.group(0) if match else ""


def _ids(text: str, pattern: str) -> list[str]:
    return sorted(set(re.findall(pattern, text)), key=_sort_key)


def _normalize_status(raw: str) -> str:
    lowered = _clean(raw).lower()
    if lowered in {"passing", "passed", "pass"}:
        return "passed"
    if lowered in {"failing", "failed", "fail"}:
        return "failed"
    if lowered in {"blocked", "blocker"}:
        return "blocked"
    if lowered in {"skipped", "skip"}:
        return "skipped"
    return "planned"


def _normalize_issue_status(raw: str) -> str:
    lowered = _clean(raw).lower()
    if lowered in {"closed", "resolved", "done"}:
        return "closed"
    if lowered in {"accepted"}:
        return "accepted"
    return "open"


def _graph_status(status: str) -> str:
    return {
        "passed": "verified",
        "failed": "failed",
        "blocked": "blocked",
        "skipped": "skipped",
    }.get(status, "planned")


def _domain_node_id(trace_id: str) -> str:
    if trace_id.startswith("BC-"):
        return f"bounded-context:{trace_id}"
    if trace_id.startswith("BR-"):
        return f"business-rule:{trace_id}"
    if trace_id.startswith("AGG-"):
        return f"domain-aggregate:{trace_id}"
    if trace_id.startswith("DE-"):
        return f"domain-event:{trace_id}"
    if trace_id.startswith("WF-DM-"):
        return f"domain-workflow:{trace_id}"
    if trace_id.startswith("ARCH-"):
        return f"architecture-component:{trace_id}"
    return f"domain-concept:{trace_id}"


def _sort_key(value: str) -> tuple[str, int, str]:
    prefix = re.sub(r"\d+", "", value)
    digits = "".join(re.findall(r"\d+", value))
    return (prefix, int(digits or 0), value)


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("<br>", " ")).strip()


def _join(values: tuple[str, ...]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "Missing"


def _escape(value: str) -> str:
    return value.replace("|", "\\|")
