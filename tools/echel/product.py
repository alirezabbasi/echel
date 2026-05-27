from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path


PRODUCT_FILES = {
    "project": "project.md",
    "problem": "problem.md",
    "users": "users.md",
    "solution": "solution.md",
    "scope": "scope.md",
    "roadmap": "roadmap.md",
    "architecture": "architecture.md",
}


@dataclass(frozen=True)
class ClarificationField:
    key: str
    file: str
    heading: str
    question: str


CLARIFICATION_FIELDS = [
    ClarificationField("problem", "problem.md", "Problem Statement", "What exact problem are we solving, and for whom?"),
    ClarificationField("why", "problem.md", "Why It Matters", "Why does this problem matter now?"),
    ClarificationField("alternatives", "problem.md", "Current Alternatives", "What alternatives do users rely on today?"),
    ClarificationField("users", "users.md", "Primary Users", "Who are the primary users?"),
    ClarificationField("needs", "users.md", "Needs", "What do those users need from the product?"),
    ClarificationField("constraints", "users.md", "Constraints", "What constraints shape the users' workflow?"),
    ClarificationField("solution", "solution.md", "Solution Concept", "What is the smallest useful solution that proves the direction?"),
    ClarificationField("capabilities", "solution.md", "Core Capabilities", "What core capabilities must the solution include?"),
    ClarificationField("differentiation", "solution.md", "Differentiation", "What should make this product meaningfully different?"),
    ClarificationField("mvp", "scope.md", "MVP", "What belongs in the MVP?"),
    ClarificationField("later", "scope.md", "Later", "What should wait until after the MVP?"),
    ClarificationField("out-of-scope", "scope.md", "Out of Scope", "What is explicitly out of scope?"),
    ClarificationField("success", "project.md", "Success Criteria", "What measurable success criteria tell us the product is working?"),
    ClarificationField("system", "architecture.md", "System Shape", "What is the expected system shape?"),
    ClarificationField("components", "architecture.md", "Key Components", "What are the key technical components?"),
    ClarificationField("architecture-questions", "architecture.md", "Open Architecture Questions", "What technical constraints or integration points are still unknown?"),
]


def _stamp() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def wiki_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    return resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)


def ensure_product_pages(repo_root: Path, cfg: ProjectConfig, product_name: str) -> Path:
    root = wiki_root(repo_root, cfg)
    root.mkdir(parents=True, exist_ok=True)
    for folder in ["knowledge", "decisions", "work", "reports"]:
        (root / folder).mkdir(parents=True, exist_ok=True)

    defaults = {
        "project": f"""---
type: product
status: active
---
# {product_name}

## Problem
TBD

## Intended Solution
TBD

## Product Direction
TBD

## Success Criteria
- TBD
""",
        "problem": """---
type: product-problem
status: draft
---
# Problem

## Problem Statement
TBD

## Why It Matters
TBD

## Current Alternatives
TBD
""",
        "users": """---
type: product-users
status: draft
---
# Users

## Primary Users
- TBD

## Needs
- TBD

## Constraints
- TBD
""",
        "solution": """---
type: product-solution
status: draft
---
# Solution

## Solution Concept
TBD

## Core Capabilities
- TBD

## Differentiation
TBD
""",
        "scope": """---
type: product-scope
status: draft
---
# Scope

## MVP
- TBD

## Later
- TBD

## Out of Scope
- TBD
""",
        "roadmap": """---
type: roadmap
status: draft
---
# Roadmap

## Now
- Clarify product intent.

## Next
- Define MVP work.

## Later
- TBD
""",
        "architecture": """---
type: product-architecture
status: draft
---
# Product Architecture

## System Shape
TBD

## Key Components
- TBD

## Open Architecture Questions
- TBD
""",
    }

    for key, rel in PRODUCT_FILES.items():
        path = root / rel
        if not path.exists():
            path.write_text(defaults[key], encoding="utf-8")
    return root


def update_project_definition(
    repo_root: Path,
    cfg: ProjectConfig,
    name: str | None,
    problem: str | None,
    solution: str | None,
    direction: str | None,
    users: str | None,
    success: str | None,
) -> list[Path]:
    root = wiki_root(repo_root, cfg)
    product_name = name or _read_title(root / "project.md") or "Product"
    ensure_product_pages(repo_root, cfg, product_name)

    changed: list[Path] = []
    project_path = root / "project.md"
    project_text = project_path.read_text(encoding="utf-8")
    if name:
        project_text = re.sub(r"^# .*$", f"# {name}", project_text, count=1, flags=re.MULTILINE)
    replacements = {
        "Problem": problem,
        "Intended Solution": solution,
        "Product Direction": direction,
    }
    for heading, value in replacements.items():
        if value:
            project_text = _replace_section_body(project_text, heading, value)
    if success:
        project_text = _replace_section_body(project_text, "Success Criteria", f"- {success}")
    project_path.write_text(project_text, encoding="utf-8")
    changed.append(project_path)

    section_updates = [
        ("problem.md", "Problem Statement", problem),
        ("solution.md", "Solution Concept", solution),
        ("users.md", "Primary Users", f"- {users}" if users else None),
    ]
    for rel, heading, value in section_updates:
        if not value:
            continue
        path = root / rel
        text = path.read_text(encoding="utf-8")
        path.write_text(_replace_section_body(text, heading, value), encoding="utf-8")
        changed.append(path)

    _append_log(root, "define", "Updated product definition through `echel define`.")
    return changed


def clarification_questions(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    return [f"{field.key}: {field.question}" for field in clarification_gaps(repo_root, cfg)]


def clarification_gaps(repo_root: Path, cfg: ProjectConfig) -> list[ClarificationField]:
    root = wiki_root(repo_root, cfg)
    ensure_product_pages(repo_root, cfg, "Product")
    gaps: list[ClarificationField] = []
    for field in CLARIFICATION_FIELDS:
        text = (root / field.file).read_text(encoding="utf-8")
        if _is_tbd(_section_body(text, field.heading)):
            gaps.append(field)
    return gaps


def answer_clarification(repo_root: Path, cfg: ProjectConfig, key: str, answer: str) -> Path:
    root = wiki_root(repo_root, cfg)
    ensure_product_pages(repo_root, cfg, "Product")
    field = next((item for item in CLARIFICATION_FIELDS if item.key == key), None)
    if field is None:
        known = ", ".join(item.key for item in CLARIFICATION_FIELDS)
        raise ValueError(f"unknown clarification field '{key}'. Known fields: {known}")
    path = root / field.file
    text = path.read_text(encoding="utf-8")
    path.write_text(_replace_section_body(text, field.heading, _format_answer(answer)), encoding="utf-8")
    _sync_summary_from_field(root, field, answer)
    _append_log(root, "clarify", f"Answered `{key}` clarification.")
    return path


def create_plan_task(repo_root: Path, cfg: ProjectConfig, title: str, goal: str | None) -> Path:
    root = wiki_root(repo_root, cfg)
    ensure_product_pages(repo_root, cfg, "Product")
    task_dir = root / "work"
    num = _next_task_number(task_dir)
    slug = _slugify(title)
    path = task_dir / f"TASK-{num:04d}-{slug}.md"
    objective = goal or "Deliver the next product planning milestone."
    path.write_text(
        f"""---
type: task
status: planned
---
# TASK-{num:04d} - {title}

## Context
- [[../project]]
- [[../roadmap]]
- [[../scope]]

## Objective
{objective}

## Scope
- TBD

## Out of Scope
- TBD

## Implementation Steps
1. Clarify requirements.
2. Define acceptance criteria.
3. Implement the smallest verified slice.

## Acceptance Criteria
- TBD

## Definition of Done
- Work is implemented or explicitly planned.
- Verification evidence is recorded.
- Product memory is updated.

## Verification Commands
```bash
make wiki-health
python3 tools/echel.py doctor
```

## Documentation Updates
- Update relevant product wiki pages and append `wiki/log.md`.
""",
        encoding="utf-8",
    )
    _append_log(root, "plan", f"Created product work item [[work/TASK-{num:04d}-{slug}]].")
    _add_to_work_board(repo_root, cfg, f"TASK-{num:04d}", title)
    return path


def synthesize_mvp_plan(repo_root: Path, cfg: ProjectConfig) -> tuple[Path, Path]:
    root = wiki_root(repo_root, cfg)
    ensure_product_pages(repo_root, cfg, "Product")
    problem = _section_body((root / "problem.md").read_text(encoding="utf-8"), "Problem Statement")
    users = _section_body((root / "users.md").read_text(encoding="utf-8"), "Primary Users")
    solution = _section_body((root / "solution.md").read_text(encoding="utf-8"), "Solution Concept")
    mvp = _section_body((root / "scope.md").read_text(encoding="utf-8"), "MVP")
    success = _section_body((root / "project.md").read_text(encoding="utf-8"), "Success Criteria")

    roadmap = root / "roadmap.md"
    roadmap.write_text(
        f"""---
type: roadmap
status: active
---
# Roadmap

## Now
- Resolve remaining clarification gaps.
- Finalize MVP acceptance criteria.

## MVP
- Problem: {_compact(problem)}
- Users: {_compact(users)}
- Solution: {_compact(solution)}
- Scope: {_compact(mvp)}
- Success: {_compact(success)}

## Next
- Generate an agent work packet for the first MVP slice.
- Verify implementation against acceptance criteria.

## Later
{_section_body((root / "scope.md").read_text(encoding="utf-8"), "Later") or "- TBD"}
""",
        encoding="utf-8",
    )
    task_title = "Define MVP" if _is_tbd(mvp) else "Build First MVP Slice"
    task_goal = (
        "Clarify MVP scope and acceptance criteria."
        if _is_tbd(mvp)
        else f"Deliver the first verified MVP slice for {_compact(solution)}"
    )
    task = create_plan_task(repo_root, cfg, task_title, task_goal)
    _append_log(root, "plan", "Synthesized MVP roadmap and next work item.")
    return roadmap, task


def generate_work_packet(repo_root: Path, cfg: ProjectConfig, task_id: str | None = None) -> Path:
    root = wiki_root(repo_root, cfg)
    ensure_product_pages(repo_root, cfg, "Product")
    task = _find_task(root, task_id)
    if task is None:
        raise ValueError("no open task found for work packet")
    packet_dir = root / "reports" / "work-packets"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet = packet_dir / f"{task.stem}-packet.md"
    task_text = task.read_text(encoding="utf-8")
    packet.write_text(
        f"""---
type: work-packet
status: active
task: {task.stem}
---
# Work Packet - {task.stem}

## Task
{_read_title(task)}

## Product Context
- Project: {_read_title(root / "project.md")}
- Problem: {_compact(_section_body((root / "problem.md").read_text(encoding="utf-8"), "Problem Statement"))}
- Users: {_compact(_section_body((root / "users.md").read_text(encoding="utf-8"), "Primary Users"))}
- Solution: {_compact(_section_body((root / "solution.md").read_text(encoding="utf-8"), "Solution Concept"))}

## Task Objective
{_section_body(task_text, "Objective") or "TBD"}

## Acceptance Criteria
{_section_body(task_text, "Acceptance Criteria") or "- TBD"}

## Constraints
- Preserve product memory in `wiki/`.
- Keep Echel framework procedure in `echel-core/`.
- Update relevant product pages when implementation changes product reality.

## Verification
{_section_body(task_text, "Verification Commands") or "```bash\nmake wiki-health\npython3 tools/echel.py doctor\n```"}

## Required Memory Updates
- Update the task artifact.
- Update affected product pages.
- Append `wiki/log.md`.

## Agent Instructions
Implement the smallest safe slice that satisfies the task objective. Verify before closure and record durable knowledge updates.
""",
        encoding="utf-8",
    )
    _append_log(root, "packet", f"Generated work packet [[reports/work-packets/{task.stem}-packet]].")
    return packet


def product_status(repo_root: Path, cfg: ProjectConfig) -> str:
    root = wiki_root(repo_root, cfg)
    ensure_product_pages(repo_root, cfg, "Product")
    title = _read_title(root / "project.md") or "Product"
    gaps = clarification_gaps(repo_root, cfg)
    task_files = sorted((root / "work").glob("TASK-*.md"))
    done = 0
    planned = 0
    for task in task_files:
        text = task.read_text(encoding="utf-8")
        if "status: done" in text:
            done += 1
        else:
            planned += 1
    total_fields = len(CLARIFICATION_FIELDS)
    answered = total_fields - len(gaps)
    readiness = round((answered / total_fields) * 100) if total_fields else 0
    mvp_ready = not any(field.key in {"problem", "users", "solution", "mvp", "success"} for field in gaps)
    lines = [
        f"# {title}",
        "",
        "## Readiness",
        f"- Product clarity: {readiness}%",
        f"- MVP readiness: {'ready for work-packet generation' if mvp_ready else 'needs clarification'}",
        f"- Open clarification questions: {len(gaps)}",
        f"- Planned/in-progress tasks: {planned}",
        f"- Done tasks: {done}",
        "",
        "## Blocked Decisions",
    ]
    lines.extend([f"- `{field.key}`: {field.question}" for field in gaps[:8]] or ["- None"])
    lines += ["", "## Suggested Next Work", f"- {next_task(repo_root, cfg) or 'No open task found.'}"]
    return "\n".join(lines)


def next_task(repo_root: Path, cfg: ProjectConfig) -> str | None:
    root = wiki_root(repo_root, cfg)
    task = _find_task(root, None)
    if task is None:
        return None
    return f"{task.stem}: {_read_title(task) or task.stem}"


def _find_task(root: Path, task_id: str | None) -> Path | None:
    tasks = sorted((root / "work").glob("TASK-*.md"))
    for task in tasks:
        if task_id and not task.name.startswith(task_id):
            continue
        text = task.read_text(encoding="utf-8")
        if "status: done" not in text:
            return task
    return None


def _sync_summary_from_field(root: Path, field: ClarificationField, answer: str) -> None:
    project = root / "project.md"
    if not project.exists():
        return
    text = project.read_text(encoding="utf-8")
    if field.key == "problem":
        text = _replace_section_body(text, "Problem", answer)
    elif field.key == "solution":
        text = _replace_section_body(text, "Intended Solution", answer)
    elif field.key == "success":
        text = _replace_section_body(text, "Success Criteria", _format_answer(answer))
    else:
        return
    project.write_text(text, encoding="utf-8")


def _format_answer(answer: str) -> str:
    stripped = answer.strip()
    if "\n" in stripped or stripped.startswith("- "):
        return stripped
    return stripped


def _compact(value: str) -> str:
    cleaned = " ".join(line.strip("- ").strip() for line in value.splitlines() if line.strip())
    if not cleaned or cleaned == "TBD":
        return "TBD"
    return cleaned


def _replace_section_body(text: str, heading: str, body: str) -> str:
    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    if re.search(pattern, text, flags=re.DOTALL):
        return re.sub(
            pattern,
            lambda match: f"{match.group(1)}{body.rstrip()}\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


def _read_title(path: Path) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _section_body(text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, text, flags=re.DOTALL)
    return m.group(1).strip() if m else ""


def _is_tbd(value: str) -> bool:
    cleaned = value.strip()
    return cleaned in {"", "TBD", "- TBD"}


def _next_task_number(task_dir: Path) -> int:
    nums = []
    for path in task_dir.glob("TASK-*.md"):
        m = re.match(r"TASK-(\d{4})-", path.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums or [0]) + 1


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80] or "product-work"


def _append_log(root: Path, label: str, line: str) -> None:
    log = root / "log.md"
    if not log.exists():
        log.write_text("---\ntype: log\nstatus: active\n---\n# Log\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{_stamp()}] {label} | product-flow\n- {line}\n")


def _add_to_work_board(repo_root: Path, cfg: ProjectConfig, task_id: str, title: str) -> None:
    work_path = resolve_symbolic_path("$MEMORY_ROOT", cfg, repo_root).parent / "work.md"
    if not work_path.exists():
        return
    text = work_path.read_text(encoding="utf-8")
    line = f"- [ ] {task_id} {title}"
    if task_id in text:
        return
    if "## Backlog" in text:
        text = text.replace("## Backlog\n", f"## Backlog\n\n{line}\n", 1)
    else:
        text = text.rstrip() + f"\n\n## Backlog\n\n{line}\n"
    work_path.write_text(text, encoding="utf-8")
