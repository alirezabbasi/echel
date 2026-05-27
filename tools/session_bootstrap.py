#!/usr/bin/env python3
from pathlib import Path
from echel_paths import configured_root

FILES = [
    "ruleset.md",
    "docs/ruleset.md",
    "schema/AGENTS.md",
    "schema/INGEST.md",
    "schema/QUERY.md",
    "schema/LINT.md",
    "schema/TASKS.md",
    "schema/STANDARDS.md",
    "$WIKI_ROOT/index.md",
    "$WIKI_ROOT/project-brief.md",
    "$WIKI_ROOT/log.md",
    "docs/development/state/where-are-we.md",
    "docs/development/state/current-state.md",
    "docs/development/work.md",
]

print("# Session Bootstrap Context\n")
for file_path in FILES:
    display_path = file_path
    if file_path.startswith("$WIKI_ROOT/"):
        p = configured_root("WIKI_ROOT", "wiki") / file_path.removeprefix("$WIKI_ROOT/")
        display_path = f"wiki/{file_path.removeprefix('$WIKI_ROOT/')}"
    else:
        p = Path(file_path)
    print(f"## {display_path}")
    if not p.exists():
        print("MISSING")
    else:
        text = p.read_text(encoding="utf-8")
        if display_path.endswith("wiki/log.md"):
            print("\n".join(text.splitlines()[-120:]))
        else:
            print(text[:6000])
    print("\n---\n")
