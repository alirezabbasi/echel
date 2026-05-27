#!/usr/bin/env python3
from pathlib import Path
import re
import sys
from echel_paths import configured_root

WIKI = configured_root("WIKI_ROOT", "wiki")
ISSUES: list[tuple[str, str, str]] = []

REQUIRED_WIKI_FILES = [
    "project-brief.md",
    "log.md",
    "index.md",
    "knowledge/source-ingest-flow.md",
    "knowledge/query-to-artifact-flow.md",
    "knowledge/session-development-flow.md",
    "knowledge/wiki-lint-flow.md",
]

TASK_REQUIRED_HEADERS = [
    "## Context",
    "## Objective",
    "## Scope",
    "## Out of Scope",
    "## Implementation Steps",
    "## Acceptance Criteria",
    "## Definition of Done",
    "## Verification Commands",
    "## Documentation Updates",
]


def add(severity: str, path: str, message: str) -> None:
    ISSUES.append((severity, path, message))


for req in REQUIRED_WIKI_FILES:
    if not (WIKI / req).exists():
        add("critical", str(WIKI / req), "missing required wiki artifact")

files = list(WIKI.rglob("*.md"))
file_set = {p.relative_to(WIKI).with_suffix("").as_posix() for p in files}

titles = {}
for p in files:
    rel = p.relative_to(WIKI).as_posix()
    text = p.read_text(encoding="utf-8")

    if not text.startswith("---"):
        add("critical", rel, "missing YAML frontmatter")

    first_h1 = next((ln for ln in text.splitlines() if ln.startswith("# ")), "")
    if first_h1:
        title = first_h1[2:].strip().lower()
        if title in titles:
            add("major", rel, f"duplicate title with {titles[title]}")
        else:
            titles[title] = rel

    if rel == "reports/wiki-health-report.md":
        continue

    pos = 0
    while True:
        start = text.find("[[", pos)
        if start == -1:
            break
        end = text.find("]]", start + 2)
        if end == -1:
            add("major", rel, "unclosed wiki link")
            break
        target = text[start + 2 : end].split("|", 1)[0].split("#", 1)[0].strip()
        pos = end + 2
        if not target or target in {"index", "log"}:
            continue
        resolved = target
        # Resolve all relative wiki links from current file directory.
        if not target.startswith("/"):
            try:
                resolved = (
                    (p.parent / target)
                    .resolve()
                    .relative_to(WIKI.resolve())
                    .with_suffix("")
                    .as_posix()
                )
            except ValueError:
                continue
        if resolved not in file_set:
            add("critical", rel, f"unresolved wiki link: [[{target}]]")

for task in sorted((WIKI / "work").glob("TASK-*.md")):
    text = task.read_text(encoding="utf-8")
    rel = task.relative_to(WIKI).as_posix()
    for header in TASK_REQUIRED_HEADERS:
        if header not in text:
            add("critical", rel, f"missing required section: {header}")
    if "- [[" not in text.split("## Context", 1)[-1].split("##", 1)[0]:
        add("critical", rel, "context section requires at least one wiki link")

report = WIKI / "reports/wiki-health-report.md"
report.parent.mkdir(parents=True, exist_ok=True)

critical = [i for i in ISSUES if i[0] == "critical"]
major = [i for i in ISSUES if i[0] == "major"]
minor = [i for i in ISSUES if i[0] == "minor"]

lines = [
    "---",
    "type: analysis",
    "status: active",
    "---",
    "",
    "# Wiki Health Report",
    "",
    f"- Critical: {len(critical)}",
    f"- Major: {len(major)}",
    f"- Minor: {len(minor)}",
    "",
]

if not ISSUES:
    lines.append("No issues found.")
else:
    for sev, path, msg in ISSUES:
        lines.append(f"- **{sev}** `{path}` - {msg}")

report.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {report} with {len(ISSUES)} issue(s)")

if critical:
    sys.exit(2)
sys.exit(0)
