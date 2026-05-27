#!/usr/bin/env python3
import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

CORE_ITEMS = [
    "assets",
    "docs",
    "prompts",
    "raw",
    "schema",
    "tools",
    "LICENSE",
    "ruleset.md",
    "README.md",
    "Makefile",
    "project.echel",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Project/workspace name")
    parser.add_argument("--mode", choices=["scratch", "existing"], required=True)
    parser.add_argument("--source", help="Path to existing codebase (required for existing mode)")
    parser.add_argument("--problem", default="", help="Initial product problem statement")
    parser.add_argument("--solution", default="", help="Initial intended solution")
    parser.add_argument("--direction", default="", help="Initial product direction")
    parser.add_argument("--users", default="", help="Initial target users")
    parser.add_argument("--success", default="", help="Initial success criteria")
    parser.add_argument(
        "--dest",
        default=".",
        help="Destination parent directory where the new workspace will be created",
    )
    return parser.parse_args()


def copy_core_template(repo_root: Path, echel_core_dir: Path) -> None:
    echel_core_dir.mkdir(parents=True, exist_ok=False)
    for item in CORE_ITEMS:
        src = repo_root / item
        dst = echel_core_dir / item
        if not src.exists():
            continue
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def copy_project_wiki_template(repo_root: Path, workspace_dir: Path) -> None:
    _ = repo_root
    dst = workspace_dir / "wiki"
    dst.mkdir(parents=True, exist_ok=True)
    for folder in ["knowledge", "decisions", "work", "reports"]:
        (dst / folder).mkdir(parents=True, exist_ok=True)
    (dst / "project-brief.md").write_text(
        """---
type: project-brief
status: active
---
# Project Brief

This wiki is the product-owned memory for the software being built with Echel.

## Ownership

- Product knowledge, decisions, tasks, reports, and evolving context live here.
- Echel framework method, tools, prompts, and schemas live under `echel-core/`.
""",
        encoding="utf-8",
    )
    (dst / "log.md").write_text("---\ntype: log\nstatus: active\n---\n# Log\n", encoding="utf-8")
    (dst / "index.md").write_text("---\ntype: index\nstatus: active\n---\n# Index\n", encoding="utf-8")


def write_generated_core_config(echel_core_dir: Path) -> None:
    config_path = echel_core_dir / "project.echel"
    config_path.write_text(
        """{
  "version": 2,
  "roots": {
    "SRC_ROOT": "..",
    "LANG_ROOT": "tools",
    "MEMORY_ROOT": "docs/development/state",
    "WIKI_ROOT": "../wiki"
  },
  "migration_map": {},
  "gate_policy": ".echel/gates.json",
  "evidence_registry": ".echel/evidence_registry.json"
}
""",
        encoding="utf-8",
    )


def reset_generated_core_state(echel_core_dir: Path) -> None:
    work = echel_core_dir / "docs" / "development" / "work.md"
    if work.exists():
        work.write_text(
            """# Work

## Backlog

## In Progress

## Done
""",
            encoding="utf-8",
        )


def copy_existing_source(source_dir: Path, workspace_dir: Path) -> None:
    shutil.copytree(
        source_dir,
        workspace_dir,
        ignore=shutil.ignore_patterns(".git", "echel-core"),
    )


def ensure_workspace_gitignore(workspace_dir: Path) -> None:
    gitignore_path = workspace_dir / ".gitignore"
    required_line = "echel-core/"
    if gitignore_path.exists():
        current = gitignore_path.read_text(encoding="utf-8")
        if required_line not in current.splitlines():
            suffix = "" if current.endswith("\n") else "\n"
            gitignore_path.write_text(
                current
                + f"{suffix}\n# Keep Echel framework out of project repository\n{required_line}\n",
                encoding="utf-8",
            )
        return

    gitignore_path.write_text(
        "# Keep Echel framework out of project repository\n"
        "echel-core/\n"
        "\n"
        "# Common local artifacts\n"
        ".DS_Store\n"
        "__pycache__/\n"
        "*.pyc\n",
        encoding="utf-8",
    )


def write_project_identity_files(workspace_dir: Path, project_name: str, mode: str, source: str | None) -> None:
    readme_path = workspace_dir / "README.md"
    license_path = workspace_dir / "LICENSE"

    if readme_path.exists():
        return

    lines = [
        f"# {project_name}",
        "",
        "This is the software project repository initialized by Echel.",
        "",
        "## Structure",
        "",
        "- `./`: Project codebase and repository root",
        "- `./wiki/`: Product memory, decisions, tasks, reports, and accumulated project intelligence",
        "- `./echel-core/`: Internal Echel framework for methodology, tools, prompts, schemas, and workflow orchestration",
        "",
        "## Next steps",
        "",
        "1. Start implementing software in this repository root.",
        "2. Commit and maintain `./wiki` with the product; it is part of the project.",
        "3. Use `./echel-core` for Echel's operating method and automation.",
        "4. Keep `echel-core/` ignored by this repository's Git history.",
        "",
        f"Initialization mode: `{mode}`",
    ]
    if source:
        lines.append(f"Source path: `{source}`")
    lines.append("")
    readme_path.write_text("\n".join(lines), encoding="utf-8")

    if not license_path.exists():
        license_path.write_text(
            "Copyright (c) "
            f"{datetime.now(timezone.utc).year} {project_name}\n\n"
            "All rights reserved.\n",
            encoding="utf-8",
        )


def _replace_section_body(text: str, heading: str, body: str) -> str:
    import re

    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    if re.search(pattern, text, flags=re.DOTALL):
        return re.sub(
            pattern,
            lambda match: f"{match.group(1)}{body.rstrip()}\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


def write_product_pages(
    workspace_dir: Path,
    project_name: str,
    problem: str,
    solution: str,
    direction: str,
    users: str,
    success: str,
) -> None:
    wiki = workspace_dir / "wiki"
    pages = {
        "project.md": f"""---
type: product
status: active
---
# {project_name}

## Problem
{problem or "TBD"}

## Intended Solution
{solution or "TBD"}

## Product Direction
{direction or "TBD"}

## Success Criteria
- {success or "TBD"}
""",
        "problem.md": f"""---
type: product-problem
status: draft
---
# Problem

## Problem Statement
{problem or "TBD"}

## Why It Matters
TBD
""",
        "users.md": f"""---
type: product-users
status: draft
---
# Users

## Primary Users
- {users or "TBD"}

## Needs
- TBD
""",
        "solution.md": f"""---
type: product-solution
status: draft
---
# Solution

## Solution Concept
{solution or "TBD"}

## Core Capabilities
- TBD
""",
        "scope.md": """---
type: product-scope
status: draft
---
# Scope

## MVP
- TBD

## Later
- TBD

## Out of Scope
- TBD
""",
        "roadmap.md": """---
type: roadmap
status: draft
---
# Roadmap

## Now
- Clarify product intent.

## Next
- Define MVP work.

## Later
- TBD
""",
        "architecture.md": """---
type: product-architecture
status: draft
---
# Product Architecture

## System Shape
TBD

## Key Components
- TBD
""",
    }
    for rel, content in pages.items():
        path = wiki / rel
        path.write_text(content, encoding="utf-8")


def update_project_wiki_context(
    workspace_dir: Path,
    project_name: str,
    mode: str,
    source: str | None,
    problem: str,
    solution: str,
    direction: str,
    users: str,
    success: str,
) -> None:
    write_product_pages(workspace_dir, project_name, problem, solution, direction, users, success)
    brief = workspace_dir / "wiki" / "project-brief.md"
    if brief.exists() and "# Project Brief" in brief.read_text(encoding="utf-8"):
        text = brief.read_text(encoding="utf-8").replace("# Project Brief", f"# Project Brief - {project_name}", 1)
        if problem:
            text = _replace_section_body(text, "Product Problem", problem)
        if solution:
            text = _replace_section_body(text, "Intended Solution", solution)
        if direction:
            text = _replace_section_body(text, "Product Direction", direction)
        brief.write_text(text, encoding="utf-8")

    log = workspace_dir / "wiki" / "log.md"
    stamp = datetime.now(timezone.utc).date()
    with log.open("a", encoding="utf-8") as f:
        f.write(
            f"\n## [{stamp}] init | {project_name}\n"
            f"- Initialized project in `{mode}` mode.\n"
            f"- Generated project-root workspace with `wiki/` as product memory and internal `echel-core/` orchestration.\n"
        )
        if source:
            f.write(f"- Source path: `{source}`.\n")


def main() -> int:
    args = parse_args()
    if args.mode == "existing" and not args.source:
        raise SystemExit("--source is required when --mode=existing")

    repo_root = Path(__file__).resolve().parents[1]
    dest_parent = Path(args.dest).resolve()
    workspace_dir = dest_parent / args.name
    source_dir = Path(args.source).resolve() if args.source else None

    if workspace_dir.exists():
        raise SystemExit(f"Target workspace already exists: {workspace_dir}")
    if args.mode == "existing":
        if source_dir is None or not source_dir.is_dir():
            raise SystemExit(f"Invalid --source path: {args.source}")

    echel_core_dir = workspace_dir / "echel-core"

    if args.mode == "existing":
        copy_existing_source(source_dir, workspace_dir)
    else:
        workspace_dir.mkdir(parents=True, exist_ok=False)

    copy_core_template(repo_root, echel_core_dir)
    copy_project_wiki_template(repo_root, workspace_dir)
    write_generated_core_config(echel_core_dir)
    reset_generated_core_state(echel_core_dir)
    ensure_workspace_gitignore(workspace_dir)
    write_project_identity_files(workspace_dir, args.name, args.mode, args.source)
    update_project_wiki_context(
        workspace_dir,
        args.name,
        args.mode,
        args.source,
        args.problem,
        args.solution,
        args.direction,
        args.users,
        args.success,
    )

    print(f"Initialized workspace: {workspace_dir}")
    print(f"- Echel framework: {echel_core_dir}")
    print(f"- Project wiki: {workspace_dir / 'wiki'}")
    print(f"- Project repository root: {workspace_dir}")
    print("Next:")
    print(f"  cd {workspace_dir} && git init")
    print(f"  cd {workspace_dir}/echel-core && make session-bootstrap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
