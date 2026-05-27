#!/usr/bin/env python3
from pathlib import Path
import re
from echel_paths import configured_root


def next_task_number(tasks_dir: Path) -> int:
    numbers = []
    for p in tasks_dir.glob("TASK-*.md"):
        m = re.match(r"TASK-(\d+)-", p.name)
        if m:
            numbers.append(int(m.group(1)))
    return max(numbers or [0]) + 1


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]


tasks = configured_root("WIKI_ROOT", "wiki") / "work"
tasks.mkdir(parents=True, exist_ok=True)
num = next_task_number(tasks)
title = input("Task title: ").strip()
if not title:
    raise SystemExit("Task title cannot be empty")

slug = slugify(title)
out = tasks / f"TASK-{num:04d}-{slug}.md"

out.write_text(
    f"""---
type: task
status: planned
---
# TASK-{num:04d} — {title}

## Context
- [[../knowledge/ai-native-engineering-os]]

## Objective
TBD

## Scope
- TBD

## Out of Scope
- TBD

## Implementation Steps
1. TBD

## Acceptance Criteria
- TBD

## Definition of Done
- TBD

## Verification Commands
```bash
make wiki-health
```

## Documentation Updates
- Update wiki and memory artifacts touched by this task.
""",
    encoding="utf-8",
)

print(out)
