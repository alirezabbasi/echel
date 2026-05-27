#!/usr/bin/env python3
from pathlib import Path
from echel_paths import configured_root

query = input("Query/title to file: ").strip()
if not query:
    raise SystemExit("Query cannot be empty")

slug = "".join(c.lower() if c.isalnum() else "-" for c in query).strip("-")[:80]
out = configured_root("WIKI_ROOT", "wiki") / "reports" / f"{slug}.md"
out.parent.mkdir(parents=True, exist_ok=True)

out.write_text(
    f"""---
type: analysis
status: draft
---
# {query}

## Question
{query}

## Answer
TBD

## Evidence
- TBD

## Decision / Recommendation
TBD

## Follow-up Tasks
- TBD
""",
    encoding="utf-8",
)

print(out)
