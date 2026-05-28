#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TMP = Path("/tmp/echel_phase5_verify")


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
            "Product owners need to know whether progress is real and releasable.",
            "--solution",
            "Milestone readiness, proof packs, and release summaries generated from product memory.",
            "--direction",
            "Certify progress through graph, evidence, risks, reviews, and work state.",
            "--users",
            "Domain experts and AI-assisted product teams",
            "--success",
            "A readiness report, proof pack, and release summary can be generated from a new project.",
        ],
        ROOT,
    )
    core = TMP / "echel-core"
    run(["python3", "tools/echel.py", "clarify", "--field", "mvp", "--answer", "- Readiness report\n- Proof pack\n- Release summary"], core)
    run(["python3", "tools/echel.py", "clarify", "--field", "needs", "--answer", "- Understand blockers\n- Package release evidence"], core)
    run(["python3", "tools/echel.py", "clarify", "--field", "components", "--answer", "- Readiness engine\n- Proof pack generator\n- Cockpit readiness view"], core)
    run(["python3", "tools/echel.py", "feature", "add", "--title", "Release readiness", "--summary", "Milestone and release certification over product memory."], core)
    run(["python3", "tools/echel.py", "plan"], core)
    run(["python3", "tools/echel.py", "build"], core)
    run(["python3", "tools/echel.py", "review"], core)
    run(["python3", "tools/echel.py", "milestone", "--name", "MVP", "--kind", "release", "--summary", "First release readiness target"], core)
    run(["python3", "tools/echel.py", "readiness", "--target", "mvp"], core)
    run(["python3", "tools/echel.py", "proof-pack", "--target", "mvp"], core)
    run(["python3", "tools/echel.py", "release-summary", "--target", "mvp"], core)
    run(["python3", "tools/echel.py", "graph", "validate"], core)

    sys.path.insert(0, str(core / "tools"))
    from echel.platform.cockpit import cockpit_snapshot, run_cockpit_command

    snapshot = cockpit_snapshot(core)
    if "readiness_detail" not in snapshot:
        print("phase5 verification failed: cockpit readiness missing", file=sys.stderr)
        return 1
    result = run_cockpit_command(core, "proof-pack", {"target": "mvp"})
    if not result.ok:
        print(f"phase5 verification failed: cockpit proof-pack failed {result.output}", file=sys.stderr)
        return 1
    wiki = TMP / "wiki"
    for rel in [
        "reports/readiness/mvp-readiness.md",
        "reports/proof-packs/mvp-proof-pack.md",
        "reports/releases/mvp-release-summary.md",
    ]:
        if not (wiki / rel).exists():
            print(f"phase5 verification failed: missing {rel}", file=sys.stderr)
            return 1

    run(["make", "wiki-health"], core)
    run(["python3", "tools/echel.py", "doctor"], core)
    print("phase5 verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
