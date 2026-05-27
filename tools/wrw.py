#!/usr/bin/env python3
from pathlib import Path
import re
import sys


WHERE_ARE_WE = Path("docs/development/state/where-are-we.md")
CURRENT_STATE = Path("docs/development/state/current-state.md")
SESSION_LEDGER = Path("docs/development/state/session-ledger.md")
KANBAN = Path("docs/development/work.md")

REQUIRED_HEADINGS = [
    "## Completed",
    "## Recent",
    "## Current",
    "## Next",
    "## Risks/Blocks",
]


def fail(msg: str) -> None:
    print(f"WRW_FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"required file missing: {path}")
    return path.read_text(encoding="utf-8")


def extract_last_updated(text: str, path: Path) -> str:
    m = re.search(r"^Last updated:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$", text, re.MULTILINE)
    if not m:
        fail(f"missing or invalid 'Last updated:' in {path}")
    return m.group(1)


def ensure_headings(text: str, path: Path) -> None:
    for heading in REQUIRED_HEADINGS:
        if re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE) is None:
            fail(f"missing heading '{heading}' in {path}")


def main() -> None:
    wrw_text = read_text(WHERE_ARE_WE)
    current_text = read_text(CURRENT_STATE)
    read_text(SESSION_LEDGER)
    read_text(KANBAN)

    ensure_headings(wrw_text, WHERE_ARE_WE)

    wrw_date = extract_last_updated(wrw_text, WHERE_ARE_WE)
    current_date = extract_last_updated(current_text, CURRENT_STATE)
    if wrw_date != current_date:
        fail(
            f"memory drift: WHERE_ARE_WE ({wrw_date}) != CURRENT_STATE ({current_date})"
        )

    # Print the quick status snapshot with exact required sections.
    print(wrw_text.strip())


if __name__ == "__main__":
    main()
