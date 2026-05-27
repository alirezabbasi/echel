#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TMP = Path("/tmp/echel_phase2_verify")


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
            "A product graph that connects intent, decisions, risks, work, and architecture.",
            "--direction",
            "Guide domain experts from intent to graph-backed verified work.",
            "--users",
            "Domain experts and AI-assisted engineering teams",
            "--success",
            "The graph can be built, validated, reported, and used during planning.",
        ],
        ROOT,
    )
    core = TMP / "echel-core"
    run(["python3", "tools/echel.py", "clarify", "--field", "mvp", "--answer", "- Product graph\n- Graph-backed work packet"], core)
    run(["python3", "tools/echel.py", "clarify", "--field", "needs", "--answer", "- Preserve product continuity across AI sessions"], core)
    run(["python3", "tools/echel.py", "clarify", "--field", "components", "--answer", "- Product wiki\n- Product graph\n- Agent command surface"], core)
    run(
        [
            "python3",
            "tools/echel.py",
            "feature",
            "add",
            "--title",
            "Product memory graph",
            "--summary",
            "A typed relationship map extracted from product memory and work artifacts.",
        ],
        core,
    )
    run(
        [
            "python3",
            "tools/echel.py",
            "risk",
            "add",
            "--title",
            "Ambiguous requirements",
            "--impact",
            "Agents may create work that does not serve product intent.",
            "--mitigation",
            "Validate requirements, tasks, risks, and decisions through the product graph.",
        ],
        core,
    )
    run(["python3", "tools/echel.py", "plan"], core)
    run(["python3", "tools/echel.py", "graph", "build"], core)
    run(["python3", "tools/echel.py", "graph", "validate"], core)
    run(["python3", "tools/echel.py", "graph", "report"], core)
    run(["python3", "tools/echel.py", "status"], core)
    run(["make", "wiki-health"], core)
    run(["python3", "tools/echel.py", "doctor"], core)
    print("phase2 verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
