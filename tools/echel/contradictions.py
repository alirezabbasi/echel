from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path
from .graph import write_graph
from .memory_kernel import MemoryRecord, query_records


CONTRADICTIONS_PATH = "governance/contradictions.md"


@dataclass(frozen=True)
class ContradictionRow:
    contradiction_id: str
    title: str
    source_record: str
    record_type: str
    links: list[str]
    impact: str
    resolution_task: str
    status: str


def contradictions_path(repo_root: Path, cfg: ProjectConfig) -> Path:
    root = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    return root / CONTRADICTIONS_PATH


def sync_contradictions(repo_root: Path, cfg: ProjectConfig) -> tuple[Path, list[ContradictionRow]]:
    records = query_records(repo_root, contradiction_only=True)
    rows = [_row_from_record(record, idx) for idx, record in enumerate(records, start=1)]
    root = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    path = root / CONTRADICTIONS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_contradictions(rows), encoding="utf-8")
    _append_log(root, f"Synced contradiction artifact [[{CONTRADICTIONS_PATH.removesuffix('.md')}]].")
    write_graph(repo_root, cfg)
    return path, rows


def render_contradictions(rows: list[ContradictionRow]) -> str:
    lines = [
        "---",
        "type: contradiction-register",
        "status: active",
        "stage: governance-integrity",
        "owner: Governance Auditor",
        "---",
        "# Contradiction Register",
        "",
        "## Purpose",
        "",
        "This artifact promotes contradiction records from local runtime memory into committed product memory so conflicting claims are visible, traceable, and resolvable by future agents.",
        "",
        "## Resolution Workflow",
        "",
        "1. Capture the conflicting claim as a contradiction memory record or refresh this register with `python3 tools/echel.py contradictions sync`.",
        "2. Link both sides of the conflict through source IDs, files, ADRs, requirements, risks, or task IDs.",
        "3. Assign the generated resolution task to the accountable lifecycle role.",
        "4. Resolve by updating the upstream source of truth, creating an ADR, accepting an exception, or opening a scoped execution task.",
        "5. Mark the contradiction `Resolved` only after downstream artifacts and graph traceability are synchronized.",
        "",
        "## Register",
        "",
        "| ID | Status | Title | Source Record | Type | Links | Impact | Resolution Task | Owner |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if rows:
        for row in rows:
            lines.append(
                "| {id} | {status} | {title} | `{source}` | {record_type} | {links} | {impact} | {task} | Governance Auditor |".format(
                    id=row.contradiction_id,
                    status=_escape(row.status),
                    title=_escape(row.title),
                    source=_escape(row.source_record),
                    record_type=_escape(row.record_type),
                    links=_escape(", ".join(row.links) if row.links else "Unlinked"),
                    impact=_escape(row.impact),
                    task=row.resolution_task,
                )
            )
    else:
        lines.append("| CONTR-000 | Resolved | No product-memory contradictions recorded | `none` | none | None | No current contradiction impact. | CONTR-TASK-000 | Governance Auditor |")
    lines.extend(
        [
            "",
            "## Resolution Tasks",
            "",
            "| Task ID | Contradiction | Required Action | Verification | Status |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if rows:
        for row in rows:
            lines.append(
                "| {task} | {contradiction} | Resolve conflict by updating source truth, ADR, risk, or scoped work item. | Re-run `python3 tools/echel.py contradictions sync`, `python3 tools/echel.py graph report`, and `python3 tools/echel.py integrity audit`. | Open |".format(
                    task=row.resolution_task,
                    contradiction=row.contradiction_id,
                )
            )
    else:
        lines.append("| CONTR-TASK-000 | CONTR-000 | No action required. | Re-run sync after new contradiction records are captured. | Resolved |")
    lines.extend(
        [
            "",
            "## Graph Contract",
            "",
            "- Each register row becomes a `contradiction` node in `wiki/graph.json`.",
            "- Open contradiction rows remain governance-stage observations until resolved.",
            "- Resolution tasks keep contradictions actionable without hiding them in local memory.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_contradiction_rows(path: Path) -> list[ContradictionRow]:
    rows: list[ContradictionRow] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not re.match(r"^\| CONTR-\d{3}\b", stripped) or "---" in stripped:
            continue
        cells = [cell.strip().strip("`") for cell in stripped.strip("|").split("|")]
        if len(cells) < 8 or cells[0] == "CONTR-000":
            continue
        rows.append(
            ContradictionRow(
                contradiction_id=cells[0],
                status=cells[1],
                title=cells[2],
                source_record=cells[3],
                record_type=cells[4],
                links=[] if cells[5] == "Unlinked" else [link.strip() for link in cells[5].split(",") if link.strip()],
                impact=cells[6],
                resolution_task=cells[7],
            )
        )
    return rows


def _row_from_record(record: MemoryRecord, idx: int) -> ContradictionRow:
    impact = _payload_summary(record.payload) or "Conflicting product memory may mislead downstream agents until resolved."
    return ContradictionRow(
        contradiction_id=f"CONTR-{idx:03d}",
        title=record.title,
        source_record=record.record_id,
        record_type=record.record_type,
        links=record.links,
        impact=impact,
        resolution_task=f"CONTR-TASK-{idx:03d}",
        status="Open",
    )


def _payload_summary(payload: dict) -> str:
    for key in ["impact", "summary", "note", "message"]:
        value = str(payload.get(key, "")).strip()
        if value:
            return value
    if payload:
        return re.sub(r"\s+", " ", str(payload))[:180]
    return ""


def _escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _append_log(root: Path, line: str) -> None:
    log = root / "log.md"
    if not log.exists():
        return
    text = log.read_text(encoding="utf-8")
    entry = f"\n## [2026-07-13] governance | contradictions\n- {line}\n"
    if line not in text:
        log.write_text(text.rstrip() + entry, encoding="utf-8")
