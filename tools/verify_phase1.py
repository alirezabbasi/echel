#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TMP = Path("/tmp/echel_phase1_verify")


def run(cmd: list[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.returncode != 0:
        print(f"FAILED: {' '.join(cmd)}", file=sys.stderr)
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP)

    run(
        [
            "python3",
            "tools/project_init.py",
            "--name",
            TMP.name,
            "--mode",
            "scratch",
            "--dest",
            str(TMP.parent),
            "--problem",
            "AI coding sessions lose product continuity.",
            "--solution",
            "A product memory and orchestration layer.",
            "--direction",
            "Guide domain experts from intent to verified software.",
            "--users",
            "Domain experts",
            "--mvp",
            "Product definition and first work packet",
            "--constraints",
            "Non-technical users must understand the product memory.",
            "--risks",
            "Agent context may drift without durable memory.",
            "--stack",
            "Python CLI and Markdown wiki",
            "--success",
            "The first MVP work packet can be generated.",
        ],
        ROOT,
    )
    core = TMP / "echel-core"
    run(["python3", "tools/echel.py", "clarify", "--field", "mvp", "--answer", "- Product definition\n- First work packet"], core)
    run(["python3", "tools/echel.py", "plan"], core)
    run(["python3", "tools/echel.py", "packet"], core)
    run(["python3", "tools/echel.py", "status"], core)
    run(["make", "wiki-health"], core)
    run(["python3", "tools/echel.py", "doctor"], core)
    print("phase1 verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
