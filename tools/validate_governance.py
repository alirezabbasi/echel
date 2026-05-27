#!/usr/bin/env python3
from pathlib import Path
import sys

required = [
    "ruleset.md",
    "docs/ruleset.md",
    "docs/development/README.md",
    "docs/development/work.md",
    "docs/development/state/current-state.md",
    "docs/development/state/session-ledger.md",
    "docs/development/state/decision-log.md",
    "docs/development/state/risks-and-assumptions.md",
    "docs/development/bugs/debug-commands.md",
]

missing = [p for p in required if not Path(p).exists()]
if missing:
    print("Missing governance artifacts:")
    for m in missing:
        print(f"- {m}")
    sys.exit(2)

print("Governance artifacts validated")
sys.exit(0)
