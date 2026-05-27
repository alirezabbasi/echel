from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .config import load_config, resolve_symbolic_path


@dataclass
class DriftIssue:
    category: str
    severity: str
    source: str
    message: str
    suggestion: str


TASK_FILENAME_RE = re.compile(r"(TASK-\d{4})-")


def _extract_task_id(path: Path) -> str | None:
    m = TASK_FILENAME_RE.search(path.name)
    return m.group(1) if m else None


def _parse_kanban_task_states(kanban_text: str) -> dict[str, bool]:
    states: dict[str, bool] = {}
    for line in kanban_text.splitlines():
        m = re.search(r"- \[( |x)\] (TASK-\d{4})", line)
        if not m:
            continue
        states[m.group(2)] = m.group(1) == "x"
    return states


def _parse_where_date(text: str) -> str | None:
    m = re.search(r"^Last updated:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$", text, re.MULTILINE)
    return m.group(1) if m else None


def detect_drift(repo_root: Path) -> list[DriftIssue]:
    issues: list[DriftIssue] = []
    cfg = load_config(repo_root)
    wiki_root = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    memory_root = resolve_symbolic_path("$MEMORY_ROOT", cfg, repo_root)

    task_files = sorted((wiki_root / "work").glob("TASK-*.md"))
    task_ids = {tid for path in task_files if (tid := _extract_task_id(path))}

    kanban_path = memory_root.parent / "work.md"
    kanban_text = kanban_path.read_text(encoding="utf-8") if kanban_path.exists() else ""
    kanban_states = _parse_kanban_task_states(kanban_text)

    for tid in sorted(task_ids - set(kanban_states)):
        issues.append(
            DriftIssue(
                category="missing",
                severity="major",
                source=str(kanban_path),
                message=f"task {tid} exists but not present in KANBAN",
                suggestion=f"add `{tid}` to Backlog/In Progress/Done",
            )
        )

    for tid in sorted(set(kanban_states) - task_ids):
        issues.append(
            DriftIssue(
                category="orphaned",
                severity="major",
                source=str(kanban_path),
                message=f"KANBAN references {tid} but task file is missing",
                suggestion=f"restore `{(wiki_root / 'work').as_posix()}/{tid}-*.md` or remove stale entry",
            )
        )

    for task in task_files:
        tid = _extract_task_id(task)
        if not tid:
            continue
        task_text = task.read_text(encoding="utf-8")
        done_in_file = "status: done" in task_text
        done_in_kanban = kanban_states.get(tid)
        if done_in_kanban is None:
            continue
        if done_in_file != done_in_kanban:
            issues.append(
                DriftIssue(
                    category="conflicting",
                    severity="major",
                    source=str(task),
                    message=f"{tid} status mismatch between task frontmatter and KANBAN checkbox",
                    suggestion="sync task status and KANBAN checkbox",
                )
            )

    wrw = memory_root / "where-are-we.md"
    current = memory_root / "current-state.md"
    if wrw.exists() and current.exists():
        d1 = _parse_where_date(wrw.read_text(encoding="utf-8"))
        d2 = _parse_where_date(current.read_text(encoding="utf-8"))
        if d1 and d2 and d1 != d2:
            issues.append(
                DriftIssue(
                    category="stale",
                    severity="major",
                    source=str(wrw),
                    message=f"memory date drift: WHERE_ARE_WE={d1}, CURRENT_STATE={d2}",
                    suggestion="run `echel sync-memory` to align memory snapshots",
                )
            )

    return issues
