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
    root = wiki_root(repo_root, cfg)
    ensure_product_pages(repo_root, cfg, "Product")
    checks = [
        ("problem.md", "Problem Statement", "What exact problem are we solving, and for whom?"),
        ("problem.md", "Why It Matters", "Why does this problem matter now?"),
        ("users.md", "Primary Users", "Who are the primary users?"),
        ("users.md", "Needs", "What do those users need from the product?"),
        ("users.md", "Constraints", "What constraints shape the users' workflow?"),
        ("solution.md", "Solution Concept", "What is the smallest useful solution that proves the direction?"),
        ("solution.md", "Core Capabilities", "What core capabilities must the solution include?"),
        ("solution.md", "Differentiation", "What should make this product meaningfully different?"),
        ("scope.md", "MVP", "What belongs in the MVP?"),
        ("scope.md", "Later", "What should wait until after the MVP?"),
        ("scope.md", "Out of Scope", "What is explicitly out of scope?"),
        ("project.md", "Success Criteria", "What measurable success criteria tell us the product is working?"),
        ("architecture.md", "System Shape", "What is the expected system shape?"),
        ("architecture.md", "Key Components", "What are the key technical components?"),
        ("architecture.md", "Open Architecture Questions", "What technical constraints or integration points are still unknown?"),
    ]
    questions: list[str] = []
    for rel, heading, question in checks:
        text = (root / rel).read_text(encoding="utf-8")
        if _is_tbd(_section_body(text, heading)):
            questions.append(question)
    return questions


def product_status(repo_root: Path, cfg: ProjectConfig) -> str:
    root = wiki_root(repo_root, cfg)
    ensure_product_pages(repo_root, cfg, "Product")
    title = _read_title(root / "project.md") or "Product"
    questions = clarification_questions(repo_root, cfg)
    task_files = sorted((root / "work").glob("TASK-*.md"))
    done = 0
    planned = 0
    for task in task_files:
        text = task.read_text(encoding="utf-8")
        if "status: done" in text:
            done += 1
        else:
            planned += 1
    lines = [
        f"# {title}",
        "",
        f"- Open clarification questions: {len(questions)}",
        f"- Planned/in-progress tasks: {planned}",
        f"- Done tasks: {done}",
        "",
        "## Next Clarifications",
    ]
    lines.extend([f"- {q}" for q in questions[:5]] or ["- None"])
    lines += ["", "## Suggested Next Work", f"- {next_task(repo_root, cfg) or 'No open task found.'}"]
    return "\n".join(lines)


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


def next_task(repo_root: Path, cfg: ProjectConfig) -> str | None:
    root = wiki_root(repo_root, cfg)
    for task in sorted((root / "work").glob("TASK-*.md")):
        text = task.read_text(encoding="utf-8")
        if "status: done" not in text:
            h1 = _read_title(task) or task.stem
            return f"{task.stem}: {h1}"
    return None


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
