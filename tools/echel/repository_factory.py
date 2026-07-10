from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path
from .gates import run_stage_gate


OUTPUT_REL = "generated/product-repository"
FACTORY_REPORT = "reports/repository-factory/generated-repository.md"
REQUIRED_TASK_ID = "TASK-1004"


@dataclass(frozen=True)
class FactoryContext:
    product_name: str
    output_rel: str
    output_root: Path
    architecture_components: list[str]
    execution_tasks: list[str]


def wiki_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    return resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)


def repository_factory_status(repo_root: Path, cfg: ProjectConfig, output_rel: str = OUTPUT_REL) -> str:
    root = repo_root / output_rel
    task_index = wiki_root(repo_root, cfg) / "work" / "TASK_INDEX.md"
    required = [
        root / "README.md",
        root / "app" / "main.py",
        root / "config" / "settings.example.json",
        root / "tests" / "test_health.py",
        root / ".github" / "workflows" / "ci.yml",
        root / ".env.example",
        root / "docs" / "engineering" / "local-development.md",
    ]
    present = sum(1 for path in required if path.exists())
    lines = ["Repository Factory Status"]
    lines.append(f"- Output root: `{output_rel}`")
    lines.append(f"- Required skeleton files present: {present}/{len(required)}")
    lines.append(f"- Execution task index present: {'yes' if task_index.exists() else 'no'}")
    lines.append("- Command: `python3 tools/echel.py repository-factory`")
    return "\n".join(lines)


def repository_factory_generate(
    repo_root: Path,
    cfg: ProjectConfig,
    force: bool = False,
    output_rel: str = OUTPUT_REL,
) -> list[Path]:
    if not force:
        result = run_stage_gate(repo_root, cfg, "architecture")
        if not result.passed:
            failures = "\n".join(f"- {failure}" for failure in result.failures)
            raise ValueError(f"architecture readiness failed; use --force only for draft repository generation\n{failures}")

    context = _factory_context(repo_root, cfg, output_rel)
    _require_execution_tasks(repo_root, cfg)

    changed: list[Path] = []
    files = _render_files(context)
    for rel, content in files.items():
        path = context.output_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")
            changed.append(path)
        if rel == "scripts/verify.sh":
            path.chmod(0o755)

    report = wiki_root(repo_root, cfg) / FACTORY_REPORT
    report.parent.mkdir(parents=True, exist_ok=True)
    report_text = _render_report(context)
    if not report.exists() or report.read_text(encoding="utf-8") != report_text:
        report.write_text(report_text, encoding="utf-8")
        changed.append(report)

    return changed


def _factory_context(repo_root: Path, cfg: ProjectConfig, output_rel: str) -> FactoryContext:
    return FactoryContext(
        product_name=_product_name(wiki_root(repo_root, cfg)),
        output_rel=output_rel,
        output_root=repo_root / output_rel,
        architecture_components=_architecture_components(wiki_root(repo_root, cfg)),
        execution_tasks=_execution_tasks(wiki_root(repo_root, cfg)),
    )


def _require_execution_tasks(repo_root: Path, cfg: ProjectConfig) -> None:
    root = wiki_root(repo_root, cfg)
    index = root / "work" / "TASK_INDEX.md"
    required = sorted((root / "work").glob(f"{REQUIRED_TASK_ID}-*.md"))
    if not index.exists() or not required:
        raise ValueError(
            "repository factory requires generated execution tasks; run `python3 tools/echel.py execution-tasks` first"
        )


def _product_name(root: Path) -> str:
    for candidate in [root / "project.md", root / "project-brief.md"]:
        if not candidate.exists():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                if title and title.lower() not in {"project brief", "product"}:
                    return title
    return "Generated Product"


def _architecture_components(root: Path) -> list[str]:
    path = root / "architecture" / "component-architecture.md"
    if not path.exists():
        return ["ARCH-202 Lifecycle CLI", "ARCH-203 Gate Engine", "ARCH-204 Product Graph"]
    components: list[str] = []
    for row in _table_rows(path.read_text(encoding="utf-8")):
        if len(row) >= 3 and re.match(r"^ARCH-\d+$", row[0]) and row[-1] in {"Existing", "New", "Generated"}:
            components.append(f"{row[0]} {row[1]}: {row[2]}")
    return components[:12] or ["ARCH-202 Lifecycle CLI", "ARCH-203 Gate Engine", "ARCH-204 Product Graph"]


def _execution_tasks(root: Path) -> list[str]:
    path = root / "work" / "TASK_INDEX.md"
    if not path.exists():
        return []
    tasks: list[str] = []
    for row in _table_rows(path.read_text(encoding="utf-8")):
        if len(row) >= 3 and "TASK-" in row[0]:
            task_id = re.sub(r".*(TASK-\d{4}).*", r"\1", row[0])
            tasks.append(f"{task_id} {row[2]}")
    return tasks


def _render_files(context: FactoryContext) -> dict[str, str]:
    component_lines = "\n".join(f"- {item}" for item in context.architecture_components)
    task_lines = "\n".join(f"- {item}" for item in context.execution_tasks[:8])
    return {
        "README.md": f"""# {context.product_name} Generated Repository

This repository skeleton was generated by Echel from architecture artifacts and execution tasks.

## Source Inputs

- Architecture: `wiki/architecture/`
- Execution tasks: `wiki/work/TASK_INDEX.md`
- Required generator task: `{REQUIRED_TASK_ID}`

## Architecture Components Preserved

{component_lines}

## Execution Tasks Considered

{task_lines}

## Local Commands

```bash
python -m unittest discover -s tests
python app/main.py
./scripts/verify.sh
```
""",
        ".gitignore": """.env
.venv/
__pycache__/
*.pyc
.DS_Store
""",
        ".env.example": """APP_ENV=local
APP_NAME=generated-product
LOG_LEVEL=INFO
""",
        "pyproject.toml": """[project]
name = "generated-product"
version = "0.1.0"
description = "Echel generated repository baseline"
requires-python = ">=3.11"
dependencies = []

[tool.echel]
source = "repository-factory"
""",
        "app/__init__.py": '"""Generated application package."""\n',
        "app/main.py": '''from __future__ import annotations

import json


def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "generated-product",
        "architecture": "local-first",
        "source": "echel-repository-factory",
    }


if __name__ == "__main__":
    print(json.dumps(health_check(), sort_keys=True))
''',
        "config/settings.example.json": """{
  "app_name": "generated-product",
  "environment": "local",
  "log_level": "INFO",
  "health_check": "app.main.health_check"
}
""",
        "tests/test_health.py": """from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import health_check


class HealthCheckTests(unittest.TestCase):
    def test_health_check_reports_ok(self):
        self.assertEqual(health_check()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
""",
        "scripts/verify.sh": """#!/usr/bin/env sh
set -eu
python -m unittest discover -s tests
python app/main.py
""",
        ".github/workflows/ci.yml": """name: Generated Repository CI

on:
  push:
  pull_request:

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m unittest discover -s tests
      - run: python app/main.py
""",
        "docs/engineering/repository-structure.md": f"""# Repository Structure

This structure is generated from Echel TASK-0024 and source task `{REQUIRED_TASK_ID}`.

```text
app/                 application entry points
config/              checked-in example configuration
tests/               generated baseline tests
scripts/             local verification commands
.github/workflows/   CI skeleton
docs/engineering/    generated local development notes
```

The skeleton is intentionally local-first and dependency-light until later implementation tasks add product behavior.
""",
        "docs/engineering/local-development.md": """# Local Development

## Setup

```bash
python -m venv .venv
. .venv/bin/activate
```

## Verify

```bash
python -m unittest discover -s tests
python app/main.py
./scripts/verify.sh
```

## Configuration

Copy `.env.example` to `.env` for local-only settings. Do not commit `.env`.
""",
    }


def _render_report(context: FactoryContext) -> str:
    components = "\n".join(f"- {item}" for item in context.architecture_components)
    tasks = "\n".join(f"- {item}" for item in context.execution_tasks)
    return f"""---
type: repository-factory-report
status: active
stage: repository-factory
---
# Generated Repository Baseline

## Output

- Path: `{context.output_rel}`
- Required source task: `{REQUIRED_TASK_ID}`

## Architecture Inputs

{components}

## Execution Task Inputs

{tasks}

## Generated Capabilities

- Application package with a health check entry point.
- Example configuration and environment files.
- Unit test baseline.
- CI workflow skeleton.
- Local verification script.
- Generated repository structure and local development docs.

## Verification

```bash
python -m unittest discover -s generated/product-repository/tests
python generated/product-repository/app/main.py
```
"""


def _table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or all(re.fullmatch(r"-+", cell.replace(" ", "")) for cell in cells):
            continue
        rows.append(cells)
    return rows
