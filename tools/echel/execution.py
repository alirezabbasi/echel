from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path
from .gates import run_stage_gate
from .graph import write_graph


PHASE_FILES = [
    "phase-0-foundation.md",
    "phase-1-mvp.md",
    "phase-2-hardening.md",
    "phase-3-production.md",
    "phase-4-evolution.md",
]
GENERATED_TASK_START = 1001


@dataclass(frozen=True)
class ExecutionTaskSource:
    phase_file: str
    phase_title: str
    phase_task_id: str
    title: str
    objective: str
    business_reason: str
    scope: str
    dependencies: str
    acceptance_criteria: str
    tests_required: str
    validation_command: str
    documentation_updates: str
    expected_repo_changes: str
    status: str


def wiki_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    return resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)


def execution_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    return wiki_root(repo_root, cfg) / "execution"


def work_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    return wiki_root(repo_root, cfg) / "work"


def execution_status(repo_root: Path, cfg: ProjectConfig) -> str:
    root = execution_root(repo_root, cfg)
    sources = read_execution_task_sources(repo_root, cfg)
    generated = sorted(work_root(repo_root, cfg).glob("TASK-1*.md"))
    missing = [name for name in PHASE_FILES if not (root / name).exists()]

    lines = ["Execution Task Generation Status"]
    lines.append(f"- Phase artifacts present: {len(PHASE_FILES) - len(missing)}/{len(PHASE_FILES)}")
    if missing:
        lines.append(f"- Missing phase artifacts: {', '.join(missing)}")
    lines.append(f"- Phase task rows available: {len(sources)}")
    lines.append(f"- Generated agent task files: {len(generated)}")
    lines.append("- Command: `python3 tools/echel.py execution-tasks`")
    return "\n".join(lines)


def execution_tasks_generate(repo_root: Path, cfg: ProjectConfig, force: bool = False) -> list[Path]:
    if not force:
        result = run_stage_gate(repo_root, cfg, "architecture")
        if not result.passed:
            failures = "\n".join(f"- {failure}" for failure in result.failures)
            raise ValueError(f"architecture readiness failed; use --force only for draft task generation\n{failures}")

    sources = read_execution_task_sources(repo_root, cfg)
    if not sources:
        raise ValueError("no execution phase tasks found under wiki/execution")

    output = work_root(repo_root, cfg)
    output.mkdir(parents=True, exist_ok=True)

    changed: list[Path] = []
    task_records: list[tuple[str, str, str, ExecutionTaskSource]] = []
    for offset, source in enumerate(sources):
        task_id = f"TASK-{GENERATED_TASK_START + offset:04d}"
        filename = f"{task_id}-{_slug(source.title)}.md"
        path = output / filename
        text = render_execution_task(task_id, source)
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
            changed.append(path)
        task_records.append((task_id, filename, path.name, source))

    index_path = output / "TASK_INDEX.md"
    index_text = render_task_index(task_records)
    if not index_path.exists() or index_path.read_text(encoding="utf-8") != index_text:
        index_path.write_text(index_text, encoding="utf-8")
        changed.append(index_path)

    write_graph(repo_root, cfg)
    return changed


def read_execution_task_sources(repo_root: Path, cfg: ProjectConfig) -> list[ExecutionTaskSource]:
    root = execution_root(repo_root, cfg)
    rows: list[ExecutionTaskSource] = []
    for phase_name in PHASE_FILES:
        path = root / phase_name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        phase_title = _first_heading(text) or phase_name
        for row in _table_rows(text):
            if len(row) < 12 or not re.match(r"^EP\d+-\d+$", row[0]):
                continue
            row = [_clean_cell(cell) for cell in row]
            rows.append(
                ExecutionTaskSource(
                    phase_file=f"execution/{phase_name}",
                    phase_title=phase_title,
                    phase_task_id=row[0],
                    title=row[1],
                    objective=row[2],
                    business_reason=row[3],
                    scope=row[4],
                    dependencies=row[5],
                    acceptance_criteria=row[6],
                    tests_required=row[7],
                    validation_command=row[8],
                    documentation_updates=row[9],
                    expected_repo_changes=row[10],
                    status=row[11],
                )
            )
    return rows


def render_execution_task(task_id: str, source: ExecutionTaskSource) -> str:
    files_to_create, files_to_modify = _file_obligations(source)
    dependencies = _bullets(_split_csv(source.dependencies))
    instructions = _implementation_instructions(source)
    validation_command = source.validation_command.strip() or "make wiki-health"
    documentation_updates = _bullets(_split_sentences(source.documentation_updates))
    acceptance = _bullets(_split_sentences(source.acceptance_criteria))
    tests = _bullets(_split_sentences(source.tests_required))
    scope = _bullets(_split_sentences(source.scope))
    out_of_scope = _out_of_scope(source)
    phase_link = f"../{source.phase_file[:-3]}"
    status = _task_status(source.status)
    dod = [
        f"{task_id} satisfies source phase task {source.phase_task_id}.",
        "All acceptance criteria are met without broadening the task scope.",
        "Required tests and validation command pass.",
        "Relevant project memory and documentation are updated.",
        "Changed files are limited to the task scope or explicitly justified in the task notes.",
    ]

    return f"""---
type: task
status: {status}
stage: execution
source_phase_task: {source.phase_task_id}
source_phase_file: {source.phase_file}
---
# {task_id} - {source.title}

## Context
- [[{phase_link}]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `{source.phase_task_id}`
- Phase artifact: `wiki/{source.phase_file}`
- Phase title: {source.phase_title}
- Upstream dependencies: {source.dependencies}

## Objective
{source.objective}

## Business Reason
{source.business_reason}

## Technical Scope
{scope}

## Scope
{scope}

## Files to Create
{_bullets(files_to_create)}

## Files to Modify
{_bullets(files_to_modify)}

## Dependencies
{dependencies}

## Implementation Instructions
{_numbered(instructions)}

## Implementation Steps
{_numbered(instructions)}

## Acceptance Criteria
{acceptance}

## Tests Required
{tests}

## Validation Command
```bash
{validation_command}
```

## Verification Commands
```bash
{validation_command}
```

## Rollback Notes
- Revert the files listed in this task if validation fails.
- Remove any generated artifacts created by this task before retrying.
- Preserve unrelated user changes and record any rollback decision in the project memory if scope or architecture changes.

## Documentation Updates
{documentation_updates}

## Definition of Done
{_checklist(dod)}

## Out of Scope
{_bullets(out_of_scope)}
"""


def render_task_index(records: list[tuple[str, str, str, ExecutionTaskSource]]) -> str:
    lines = [
        "---",
        "type: task-index",
        "status: active",
        "stage: execution",
        "---",
        "# Execution Task Index",
        "",
        "Generated from `wiki/execution/` phase artifacts by `python3 tools/echel.py execution-tasks`.",
        "",
        "## Task Contract",
        "- One source phase row becomes one agent-executable task.",
        "- Generated tasks must stay small enough for one AI coding session.",
        "- Each task carries objective, business reason, technical scope, files, dependencies, instructions, acceptance criteria, tests, validation, rollback, documentation updates, DoD, and out-of-scope.",
        "- Repository factory work must consume these task records instead of roadmap prose.",
        "",
        "## Tasks",
        "",
        "| Task ID | Phase Task | Title | Source | Dependencies | Validation | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for task_id, filename, _path_name, source in records:
        lines.append(
            f"| {task_id} ([[{filename[:-3]}]]) | {source.phase_task_id} | {source.title} | `{source.phase_file}` | {source.dependencies} | `{source.validation_command}` | {_display_status(source.status)} |"
        )
    lines.append("")
    return "\n".join(lines)


def _table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip().replace("\\|", "|") for cell in stripped.strip("|").split("|")]
        if not cells or all(re.fullmatch(r"-+", cell.replace(" ", "")) for cell in cells):
            continue
        rows.append(cells)
    return rows


def _clean_cell(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        return value[1:-1].strip()
    return value


def _task_status(value: str) -> str:
    return "done" if value.strip().lower() == "done" else "planned"


def _display_status(value: str) -> str:
    return "Done" if _task_status(value) == "done" else "Planned"


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "execution-task"


def _split_csv(value: str) -> list[str]:
    parts = [part.strip() for part in re.split(r",|;", value) if part.strip()]
    return parts or ["None beyond source phase readiness."]


def _split_sentences(value: str) -> list[str]:
    clean = value.strip()
    if not clean:
        return ["Not specified by source phase artifact."]
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", clean) if part.strip()]
    return parts or [clean]


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _numbered(items: list[str]) -> str:
    return "\n".join(f"{idx}. {item}" for idx, item in enumerate(items, start=1))


def _checklist(items: list[str]) -> str:
    return "\n".join(f"- [ ] {item}" for item in items)


def _file_obligations(source: ExecutionTaskSource) -> tuple[list[str], list[str]]:
    expected = source.expected_repo_changes.strip()
    docs = source.documentation_updates.strip()
    creates: list[str] = []
    modifies: list[str] = []

    if "No code" in expected:
        modifies.extend(["wiki/execution/*.md", "docs/development/state/*.md", "self/*.md"])
    elif "New " in expected or "files" in expected or "outputs" in expected:
        creates.append(expected)
    else:
        modifies.append(expected or "Repository files named by the implementation instructions.")

    if "docs" in docs.lower() or "documentation" in docs.lower() or "roadmap" in docs.lower():
        modifies.append(docs)

    if not creates:
        creates.append("No new files expected unless the implementation instructions require a generated artifact.")
    if not modifies:
        modifies.append("No existing files expected unless validation reveals required documentation synchronization.")

    return _dedupe(creates), _dedupe(modifies)


def _implementation_instructions(source: ExecutionTaskSource) -> list[str]:
    return [
        f"Read `wiki/{source.phase_file}` and locate `{source.phase_task_id}` before editing.",
        f"Implement only this source scope: {source.scope}",
        "Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.",
        f"Apply the expected repository change: {source.expected_repo_changes}",
        f"Run the required verification: `{source.validation_command}`.",
        "Update the documentation listed in this task and record any new architectural decision only if one was actually made.",
    ]


def _out_of_scope(source: ExecutionTaskSource) -> list[str]:
    return [
        "Work from later execution phase rows.",
        "Repository-wide refactors unrelated to this source phase task.",
        "New lifecycle stages, gates, or agent roles not named by this task scope.",
        "Implementation beyond the stated expected repository changes.",
    ]


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.strip()
        if key and key not in seen:
            seen.add(key)
            out.append(key)
    return out
