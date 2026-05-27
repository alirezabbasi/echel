#!/usr/bin/env python3
import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from echel_paths import configured_root

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("--title", required=True)
parser.add_argument("--kind", default="source")
args = parser.parse_args()

src = Path(args.source)
if not src.exists():
    raise SystemExit(f"missing source: {src}")

slug = re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")
wiki = configured_root("WIKI_ROOT", "wiki")
out = wiki / "reports" / f"{slug}.md"
out.parent.mkdir(parents=True, exist_ok=True)

out.write_text(
    "\n".join(
        [
            "---",
            "type: source-summary",
            "status: active",
            f"source-kind: {args.kind}",
            "---",
            f"# {args.title}",
            "",
            "## Source",
            f"`{src.as_posix()}`",
            "",
            "## Summary",
            "TBD by agent after reading source.",
            "",
            "## Extracted Entities",
            "- TBD",
            "",
            "## Extracted Concepts",
            "- TBD",
            "",
            "## Follow-up Tasks",
            "- TBD",
            "",
        ]
    ),
    encoding="utf-8",
)

stamp = datetime.now(timezone.utc).date()
with (wiki / "log.md").open("a", encoding="utf-8") as f:
    f.write(
        f"\n## [{stamp}] ingest | {args.title}\n"
        f"- Created source summary: [[reports/{slug}]].\n"
    )

print(out)
