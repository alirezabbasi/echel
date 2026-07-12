from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from pathlib import Path

from .config import ProjectConfig, resolve_symbolic_path
from .graph import write_graph


VALID_SOURCE_KINDS = {"incident", "rca", "feedback", "roadmap-change", "strategy-change"}
VALID_ACTIONS = {"task", "adr", "risk", "assumption", "strategy-change", "none"}


@dataclass(frozen=True)
class LearningResult:
    learning_id: str
    record_path: Path
    target_kind: str
    target_path: Path | None


def ensure_learning_files(repo_root: Path, cfg: ProjectConfig) -> list[Path]:
    root = _wiki_root(repo_root, cfg)
    templates = {
        "learning-loop.md": _learning_loop_template(),
        "learning-records.md": _learning_records_template(),
        "rca-log.md": _rca_log_template(),
        "customer-feedback.md": _customer_feedback_template(),
        "roadmap-change-log.md": _roadmap_change_template(),
        "strategy-change-log.md": _strategy_change_template(),
    }
    changed: list[Path] = []
    operations = root / "operations"
    operations.mkdir(parents=True, exist_ok=True)
    for name, text in templates.items():
        path = operations / name
        if not path.exists():
            path.write_text(text, encoding="utf-8")
            changed.append(path)
    return changed


def learning_status(repo_root: Path, cfg: ProjectConfig) -> str:
    ensure_learning_files(repo_root, cfg)
    root = _wiki_root(repo_root, cfg)
    records = _learning_rows(root / "operations" / "learning-records.md")
    by_kind: dict[str, int] = {}
    for row in records:
        by_kind[row.get("Source Kind", "unknown")] = by_kind.get(row.get("Source Kind", "unknown"), 0) + 1
    lines = ["# Learning Loop", "", f"- Records: {len(records)}"]
    for kind in sorted(by_kind):
        lines.append(f"- {kind}: {by_kind[kind]}")
    lines.append("- Command: `python3 tools/echel.py learning add --source-kind incident --title \"...\" --summary \"...\" --action task`")
    return "\n".join(lines)


def record_learning(
    repo_root: Path,
    cfg: ProjectConfig,
    *,
    source_kind: str,
    title: str,
    summary: str,
    action: str,
    owner: str = "Operations Steward",
    severity: str = "medium",
    source_id: str = "",
) -> LearningResult:
    source_kind = source_kind.strip().lower()
    action = action.strip().lower()
    if source_kind not in VALID_SOURCE_KINDS:
        raise ValueError(f"unknown learning source kind `{source_kind}`; expected one of: {', '.join(sorted(VALID_SOURCE_KINDS))}")
    if action not in VALID_ACTIONS:
        raise ValueError(f"unknown learning action `{action}`; expected one of: {', '.join(sorted(VALID_ACTIONS))}")
    if not title.strip() or not summary.strip():
        raise ValueError("learning title and summary are required")

    ensure_learning_files(repo_root, cfg)
    root = _wiki_root(repo_root, cfg)
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    learning_id = _next_learning_id(root / "operations" / "learning-records.md")
    target_kind, target_path = _apply_action(
        repo_root,
        cfg,
        learning_id=learning_id,
        source_kind=source_kind,
        title=title.strip(),
        summary=summary.strip(),
        action=action,
        owner=owner.strip() or "Operations Steward",
        severity=severity.strip() or "medium",
        created_at=created_at,
    )
    target_ref = str(target_path.relative_to(root)) if target_path and _is_relative_to(target_path, root) else (str(target_path) if target_path else "None")
    records = root / "operations" / "learning-records.md"
    _append_table_row(
        records,
        "## Learning Records",
        f"| `{learning_id}` | {source_kind} | {_escape(title)} | {_escape(summary)} | {action} | {target_kind} | {target_ref} | {owner or 'Operations Steward'} | {severity or 'medium'} | captured | {created_at} |",
    )
    _append_source_log(root, learning_id, source_kind, title, summary, action, target_ref, owner, severity, created_at, source_id)
    _append_lifecycle_log(root, learning_id, source_kind, title, action, target_ref, created_at)
    write_graph(repo_root, cfg)
    return LearningResult(learning_id, records, target_kind, target_path)


def _apply_action(
    repo_root: Path,
    cfg: ProjectConfig,
    *,
    learning_id: str,
    source_kind: str,
    title: str,
    summary: str,
    action: str,
    owner: str,
    severity: str,
    created_at: str,
) -> tuple[str, Path | None]:
    root = _wiki_root(repo_root, cfg)
    if action == "none":
        return "none", None
    if action == "task":
        return "task", _create_learning_task(root, learning_id, title, summary, owner)
    if action == "adr":
        return "adr", _create_learning_adr(root, learning_id, title, summary)
    if action == "risk":
        return "risk", _append_learning_risk(root, learning_id, title, summary, severity)
    if action == "assumption":
        return "assumption", _append_learning_assumption(root, learning_id, title, summary, created_at)
    if action == "strategy-change":
        return "strategy-change", _append_strategy_change(root, learning_id, source_kind, title, summary, owner, created_at)
    raise ValueError(f"unsupported learning action `{action}`")


def _create_learning_task(root: Path, learning_id: str, title: str, summary: str, owner: str) -> Path:
    task_id = _next_numeric_id(root / "work", "TASK", start=2001)
    slug = _slug(title)
    path = root / "work" / f"{task_id}-learning-{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
type: task
status: planned
stage: operations-evolution
source_learning: {learning_id}
---
# {task_id} - Learning Follow-up: {title}

## Context
- [[../operations/learning-records]]
- [[../operations/evolution-backlog]]

## Objective
Resolve learning `{learning_id}`: {summary}

## Scope
- Investigate the learning signal.
- Update the authoritative product memory named by the resolution.
- Add tests, evidence, or documentation if behavior changes.

## Out of Scope
- Unrelated lifecycle or architecture changes.
- Product implementation without an approved task packet.

## Implementation Steps
1. Review `wiki/operations/learning-records.md` and the source operations artifact.
2. Identify affected requirements, strategy, roadmap, risks, decisions, tests, or evidence.
3. Implement the smallest safe follow-up.
4. Register or link evidence before closure.

## Acceptance Criteria
- Learning `{learning_id}` has a documented resolution.
- Affected product memory is updated.
- Verification evidence is registered or explicitly deferred with owner approval.

## Definition of Done
- [ ] Follow-up scope is complete.
- [ ] Verification command passes.
- [ ] Product memory and learning record are updated.
- [ ] Evidence is registered or deferral is documented.

## Verification Commands
```bash
python3 -m unittest discover -s tests
```

## Documentation Updates
- Update operations, strategy, roadmap, risk, decision, or task docs affected by this learning.

## Rollback Notes
- Revert the follow-up files and restore the learning record to captured state if validation fails.

## Owner
{owner}
""",
        encoding="utf-8",
    )
    return path


def _create_learning_adr(root: Path, learning_id: str, title: str, summary: str) -> Path:
    adr_id = _next_numeric_id(root / "decisions", "ADR", start=6)
    path = root / "decisions" / f"{adr_id}-learning-{_slug(title)}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
type: decision
status: proposed
stage: governance
source_learning: {learning_id}
---
# {adr_id} - Learning Follow-up: {title}

## Status

Proposed

## Context

Learning `{learning_id}` reported: {summary}

## Decision

TBD

## Alternatives Considered

- Keep current behavior.
- Change product memory, workflow, or architecture according to the learning.

## Consequences

- Product memory must be updated after the decision is accepted or rejected.
- Related tasks, risks, assumptions, or strategy records must reference this ADR.

## Rollback Strategy

Revert the decision and affected follow-up artifacts if validation or governance review rejects the change.
""",
        encoding="utf-8",
    )
    return path


def _append_learning_risk(root: Path, learning_id: str, title: str, summary: str, severity: str) -> Path:
    path = root / "risks.md"
    if not path.exists():
        path.write_text("---\ntype: risks\nstatus: active\n---\n# Risks\n", encoding="utf-8")
    text = path.read_text(encoding="utf-8").rstrip()
    text += (
        f"\n\n## {title}\n\n"
        f"- Source: {learning_id}\n"
        f"- Impact: {summary}\n"
        f"- Severity: {severity}\n"
        "- Mitigation: Triage through `wiki/operations/evolution-backlog.md` and assign a follow-up owner.\n"
    )
    path.write_text(text + "\n", encoding="utf-8")
    return path


def _append_learning_assumption(root: Path, learning_id: str, title: str, summary: str, created_at: str) -> Path:
    path = root / "discovery" / "assumptions.md"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_assumptions_template(), encoding="utf-8")
    assumption_id = _next_table_id(path, "A", default=1)
    row = f"| `{assumption_id}` | {learning_id}: {_escape(title)} - {_escape(summary)} | medium | Product direction may be stale. | Review learning source and update downstream artifacts. | active | TBD |"
    _append_table_row(path, "## Active Assumptions", row)
    return path


def _append_strategy_change(root: Path, learning_id: str, source_kind: str, title: str, summary: str, owner: str, created_at: str) -> Path:
    path = root / "operations" / "strategy-change-log.md"
    row = f"| `{learning_id}` | {source_kind} | {_escape(title)} | {_escape(summary)} | strategy-change | strategy/pmf-evidence.md | {owner} | medium | proposed | {created_at} |"
    _append_table_row(path, "## Strategy Change Records", row)
    pmf = root / "strategy" / "pmf-evidence.md"
    if pmf.exists():
        text = pmf.read_text(encoding="utf-8")
        section = "## Learning-Driven Strategy Changes"
        line = f"- `{learning_id}`: {title} - {summary}"
        if section not in text:
            text = text.rstrip() + f"\n\n{section}\n\n{line}\n"
        elif line not in text:
            text = text.rstrip() + f"\n{line}\n"
        pmf.write_text(text, encoding="utf-8")
    return path


def _append_source_log(
    root: Path,
    learning_id: str,
    source_kind: str,
    title: str,
    summary: str,
    action: str,
    target_ref: str,
    owner: str,
    severity: str,
    created_at: str,
    source_id: str,
) -> None:
    mapping = {
        "incident": ("incident-response.md", "## Learning Intake"),
        "rca": ("rca-log.md", "## RCA Records"),
        "feedback": ("customer-feedback.md", "## Feedback Records"),
        "roadmap-change": ("roadmap-change-log.md", "## Roadmap Change Records"),
        "strategy-change": ("strategy-change-log.md", "## Strategy Change Records"),
    }
    filename, heading = mapping[source_kind]
    path = root / "operations" / filename
    source = source_id or learning_id
    row = f"| `{learning_id}` | {source} | {_escape(title)} | {_escape(summary)} | {action} | {target_ref} | {owner} | {severity} | captured | {created_at} |"
    _append_table_row(path, heading, row)


def _append_lifecycle_log(root: Path, learning_id: str, source_kind: str, title: str, action: str, target_ref: str, created_at: str) -> None:
    path = root / "log.md"
    if not path.exists():
        path.write_text("---\ntype: log\nstatus: active\n---\n# Log\n", encoding="utf-8")
    text = path.read_text(encoding="utf-8").rstrip()
    text += f"\n\n## [{created_at}] learning | {source_kind}\n- Captured `{learning_id}`: {title}.\n- Action: {action}; target: {target_ref}.\n"
    path.write_text(text + "\n", encoding="utf-8")


def _append_table_row(path: Path, heading: str, row: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if row in text:
        return
    if heading not in text:
        text = text.rstrip() + f"\n\n{heading}\n\n"
    start = text.index(heading)
    next_heading = text.find("\n## ", start + len(heading))
    insert_at = next_heading if next_heading != -1 else len(text)
    before = text[:insert_at].rstrip()
    after = text[insert_at:]
    text = before + "\n" + row + "\n" + after
    path.write_text(text.lstrip(), encoding="utf-8")


def _learning_rows(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not path.exists():
        return rows
    headers: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip().strip("`") for cell in stripped.strip("|").split("|")]
        if not headers:
            headers = cells
            continue
        if cells and cells[0].startswith("LEARN-") and len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows


def _next_learning_id(path: Path) -> str:
    rows = _learning_rows(path)
    highest = 0
    for row in rows:
        match = re.search(r"LEARN-(\d+)", row.get("ID", ""))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"LEARN-{highest + 1:03d}"


def _next_table_id(path: Path, prefix: str, default: int = 1) -> str:
    highest = default - 1
    if path.exists():
        for match in re.finditer(rf"\b{re.escape(prefix)}-(\d{{3,4}})\b", path.read_text(encoding="utf-8")):
            highest = max(highest, int(match.group(1)))
    return f"{prefix}-{highest + 1:03d}"


def _next_numeric_id(root: Path, prefix: str, start: int) -> str:
    root.mkdir(parents=True, exist_ok=True)
    highest = start - 1
    for path in root.glob(f"{prefix}-*.md"):
        match = re.match(rf"{re.escape(prefix)}-(\d+)", path.name)
        if match:
            highest = max(highest, int(match.group(1)))
    width = 4 if prefix in {"TASK", "ADR"} else 3
    return f"{prefix}-{highest + 1:0{width}d}"


def _wiki_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    return resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:60] or "learning"


def _escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _learning_loop_template() -> str:
    return """---
type: operations-learning-loop
stage: operations-evolution
status: draft
owner: operations-steward
updated: 2026-07-13
---
# Learning Loop

## Purpose

The learning loop turns post-release signals into governed product memory updates. It prevents incidents, RCA, customer feedback, roadmap changes, and strategy changes from staying in chat or local memory only.

## Command Contract

Use:

```bash
python3 tools/echel.py learning add --source-kind incident --title "..." --summary "..." --action task
```

Allowed source kinds: `incident`, `rca`, `feedback`, `roadmap-change`, `strategy-change`.

Allowed actions: `task`, `adr`, `risk`, `assumption`, `strategy-change`, `none`.

## Learning Flow

| ID | Step | Action | Output | Owner |
| --- | --- | --- | --- | --- |
| LRN-FLOW-001 | Capture | Record the signal with source kind, title, summary, owner, and severity. | [[learning-records]] | Operations Steward |
| LRN-FLOW-002 | Classify | Choose whether it creates task, ADR, risk, assumption, strategy change, or no-op. | Learning record action | Governance Auditor |
| LRN-FLOW-003 | Route | Update the authoritative artifact for the chosen action. | Work, decisions, risks, assumptions, or strategy memory | Responsible role |
| LRN-FLOW-004 | Verify | Run validation and register evidence when behavior changes. | Evidence record | QA Agent |
| LRN-FLOW-005 | Close | Update evolution backlog and learning record status. | [[evolution-backlog]] | Operations Steward |

## Quality Gate

- [ ] Learning records have source kind, owner, severity, action, and target artifact.
- [ ] Product behavior changes route through task packets.
- [ ] Architecture decisions route through ADRs.
- [ ] Risks, assumptions, roadmap changes, and strategy changes update their authoritative memory surfaces.
"""


def _learning_records_template() -> str:
    return """---
type: operations-learning-records
stage: operations-evolution
status: active
owner: operations-steward
updated: 2026-07-13
---
# Learning Records

## Purpose

This register is the durable index of post-release learning signals and their routed follow-up actions.

## Learning Records

| ID | Source Kind | Title | Summary | Action | Target Kind | Target Artifact | Owner | Severity | Status | Created |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""


def _rca_log_template() -> str:
    return """---
type: operations-rca-log
stage: operations-evolution
status: active
owner: governance-auditor
updated: 2026-07-13
---
# RCA Log

## Purpose

This log records root-cause-analysis learnings and routes them into tasks, decisions, risks, assumptions, or strategy changes.

## RCA Records

| ID | Source | Title | Summary | Action | Target Artifact | Owner | Severity | Status | Created |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""


def _customer_feedback_template() -> str:
    return """---
type: operations-customer-feedback
stage: operations-evolution
status: active
owner: product-manager
updated: 2026-07-13
---
# Customer Feedback

## Purpose

This log captures customer, user, operator, and buyer feedback after release and routes it through governed product memory.

## Feedback Records

| ID | Source | Title | Summary | Action | Target Artifact | Owner | Severity | Status | Created |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""


def _roadmap_change_template() -> str:
    return """---
type: operations-roadmap-change-log
stage: operations-evolution
status: active
owner: product-manager
updated: 2026-07-13
---
# Roadmap Change Log

## Purpose

This log captures roadmap change signals and keeps phase, release, and task planning tied to post-release learning.

## Roadmap Change Records

| ID | Source | Title | Summary | Action | Target Artifact | Owner | Severity | Status | Created |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""


def _strategy_change_template() -> str:
    return """---
type: operations-strategy-change-log
stage: operations-evolution
status: active
owner: product-manager
updated: 2026-07-13
---
# Strategy Change Log

## Purpose

This log captures strategy change signals and keeps product strategy updates tied to evidence and post-release learning.

## Strategy Change Records

| ID | Source | Title | Summary | Action | Target Artifact | Owner | Severity | Status | Created |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""


def _assumptions_template() -> str:
    return """---
type: discovery-assumptions
status: draft
stage: discovery
---
# Assumptions

## Active Assumptions

| ID | Assumption | Confidence | Impact if Wrong | Validation Method | Status | Resolved By |
| --- | --- | --- | --- | --- | --- | --- |
"""
