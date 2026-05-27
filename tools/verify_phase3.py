#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TMP = Path("/tmp/echel_phase3_verify")


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
            "AI coding agents lose implementation context between sessions.",
            "--solution",
            "Graph-backed work packets and review reports for reliable agent execution.",
            "--direction",
            "Turn product intent into implementation handoffs with reviewable evidence.",
            "--users",
            "Domain experts and AI coding agents",
            "--success",
            "A graph-backed packet and review report can be generated from a new project.",
        ],
        ROOT,
    )
    core = TMP / "echel-core"
    run(["python3", "tools/echel.py", "clarify", "--field", "mvp", "--answer", "- Graph-backed build packet\n- Review report"], core)
    run(["python3", "tools/echel.py", "clarify", "--field", "needs", "--answer", "- Preserve implementation context\n- Review agent output against product intent"], core)
    run(["python3", "tools/echel.py", "clarify", "--field", "components", "--answer", "- Product wiki\n- Product graph\n- Work packet generator\n- Review reporter"], core)
    run(
        [
            "python3",
            "tools/echel.py",
            "feature",
            "add",
            "--title",
            "Graph-backed agent packets",
            "--summary",
            "Agent handoffs include related product graph context, evidence obligations, and memory updates.",
        ],
        core,
    )
    run(["python3", "tools/echel.py", "plan"], core)
    run(["python3", "tools/echel.py", "graph", "build"], core)
    run(["python3", "tools/echel.py", "build"], core)
    run(["python3", "tools/echel.py", "review"], core)
    run(["python3", "tools/echel.py", "next"], core)
    run(["python3", "tools/echel.py", "graph", "validate"], core)
    run(["make", "wiki-health"], core)
    run(["python3", "tools/echel.py", "doctor"], core)

    wiki = TMP / "wiki"
    packets = sorted((wiki / "reports" / "work-packets").glob("*-packet.md"))
    reviews = sorted((wiki / "reports" / "reviews").glob("*-review.md"))
    if not packets or "## Graph Context" not in packets[-1].read_text(encoding="utf-8"):
        print("phase3 verification failed: graph-backed packet missing", file=sys.stderr)
        return 1
    if not reviews or "## Review Checks" not in reviews[-1].read_text(encoding="utf-8"):
        print("phase3 verification failed: review report missing", file=sys.stderr)
        return 1
    print("phase3 verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
