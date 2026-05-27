#!/usr/bin/env python3
import subprocess
from pathlib import Path


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    raw = input(f"{prompt}{suffix}: ").strip()
    return raw or (default or "")


def main() -> int:
    print("Echel Initialization Wizard")
    print("This creates a target software project repository where:")
    print("- <project-name>/ is the repository root for your software")
    print("- <project-name>/wiki/ is the product memory committed with the project")
    print("- <project-name>/echel-core/ is the internal Echel framework\n")

    name = ask("Project name")
    while not name:
        name = ask("Project name (required)")

    mode = ask("Mode (scratch/existing)", "scratch").lower()
    while mode not in {"scratch", "existing"}:
        mode = ask("Mode must be scratch or existing", "scratch").lower()

    source = ""
    if mode == "existing":
        source = ask("Path to existing source repo")
        while not source:
            source = ask("Path to existing source repo (required)")

    dest = ask("Destination parent directory", ".")
    problem = ask("Problem statement", "")
    solution = ask("Intended solution", "")
    direction = ask("Product direction", "")
    users = ask("Target users", "")
    success = ask("Success criteria", "")

    cmd = [
        "python3",
        str(Path(__file__).with_name("project_init.py")),
        "--name",
        name,
        "--mode",
        mode,
        "--dest",
        dest,
    ]
    if source:
        cmd.extend(["--source", source])
    for flag, value in [
        ("--problem", problem),
        ("--solution", solution),
        ("--direction", direction),
        ("--users", users),
        ("--success", success),
    ]:
        if value:
            cmd.extend([flag, value])

    subprocess.run(cmd, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
