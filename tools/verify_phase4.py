#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TMP = Path("/tmp/echel_phase4_verify")


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
            "Product owners need a clear cockpit for AI-native product creation.",
            "--solution",
            "A local Echel cockpit with product status, graph, work, packets, reviews, risks, and decisions.",
            "--direction",
            "Make Echel understandable without asking users to browse framework internals.",
            "--users",
            "Domain experts and AI-assisted product teams",
            "--success",
            "The cockpit data surface exposes project state and safe product actions.",
        ],
        ROOT,
    )
    core = TMP / "echel-core"
    run(["python3", "tools/echel.py", "clarify", "--field", "mvp", "--answer", "- Product cockpit\n- Cockpit command bridge"], core)
    run(["python3", "tools/echel.py", "clarify", "--field", "needs", "--answer", "- Understand product readiness\n- Trigger safe Echel actions"], core)
    run(["python3", "tools/echel.py", "clarify", "--field", "components", "--answer", "- Cockpit data API\n- Cockpit UI\n- Command bridge"], core)
    run(["python3", "tools/echel.py", "feature", "add", "--title", "Product cockpit", "--summary", "A local product steering interface over Echel memory and workflows."], core)
    run(["python3", "tools/echel.py", "plan"], core)
    run(["python3", "tools/echel.py", "build"], core)
    run(["python3", "tools/echel.py", "review"], core)
    run(["python3", "tools/echel.py", "platform", "init"], core)

    sys.path.insert(0, str(core / "tools"))
    from echel.platform.cockpit import cockpit_snapshot, run_cockpit_command

    snapshot = cockpit_snapshot(core)
    required = ["project", "readiness", "clarifications", "roadmap", "work", "graph", "risks", "decisions"]
    missing = [key for key in required if key not in snapshot]
    if missing:
        print(f"phase4 verification failed: missing snapshot keys {missing}", file=sys.stderr)
        return 1
    if not snapshot["graph"]["nodes"]:
        print("phase4 verification failed: graph nodes missing", file=sys.stderr)
        return 1
    if not snapshot["work"]["tasks"]:
        print("phase4 verification failed: work queue missing", file=sys.stderr)
        return 1
    result = run_cockpit_command(core, "graph-report", {})
    if not result.ok:
        print(f"phase4 verification failed: command bridge failed {result.output}", file=sys.stderr)
        return 1
    app_source = (core / "tools" / "echel" / "platform" / "app.py").read_text(encoding="utf-8")
    for route in ["/api/cockpit", "/api/cockpit/command"]:
        if route not in app_source:
            print(f"phase4 verification failed: missing route {route}", file=sys.stderr)
            return 1

    run(["make", "wiki-health"], core)
    run(["python3", "tools/echel.py", "doctor"], core)
    print("phase4 verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
