from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path


REPORT_PATH = "governance/migration-compatibility.md"


@dataclass(frozen=True)
class LegacyMapping:
    legacy_path: str
    stage: str
    canonical_paths: tuple[str, ...]
    compatibility_mode: str


LEGACY_MAPPINGS = [
    LegacyMapping("project.md", "repository-initialization", ("project.md", "canon/product-canon.md", "canon/vision.md"), "source summary"),
    LegacyMapping("problem.md", "discovery", ("discovery/product-discovery-spec.md", "canon/product-canon.md"), "compatibility summary"),
    LegacyMapping("solution.md", "canon", ("canon/product-canon.md", "requirements/product-requirements.md"), "compatibility summary"),
    LegacyMapping("scope.md", "requirements", ("requirements/mvp-scope.md", "requirements/out-of-scope.md"), "compatibility summary"),
    LegacyMapping("roadmap.md", "roadmap", ("roadmap/master-roadmap.md", "roadmap/mvp-roadmap.md", "roadmap/release-plan.md"), "compatibility summary"),
    LegacyMapping("architecture.md", "architecture", ("architecture/overview.md", "architecture/component-architecture.md", "architecture/data-architecture.md"), "compatibility summary"),
    LegacyMapping("work/", "execution", ("work/TASK_INDEX.md", "execution/phase-0-foundation.md", "execution/phase-4-evolution.md"), "directory compatibility"),
]


LIFECYCLE_DIRS = [
    "discovery",
    "canon",
    "strategy",
    "requirements",
    "domain",
    "architecture",
    "roadmap",
    "execution",
    "validation",
    "deployment",
    "operations",
    "governance",
    "agents",
    "engineering",
    "work",
    "reports",
]


def ensure_migration_compatibility(repo_root: Path, cfg: ProjectConfig) -> tuple[Path, list[str]]:
    root = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    created_dirs = _ensure_lifecycle_dirs(root)
    for mapping in LEGACY_MAPPINGS:
        if mapping.legacy_path.endswith("/"):
            continue
        legacy = root / mapping.legacy_path
        if legacy.exists():
            _upsert_compatibility_section(legacy, mapping)
    report = root / REPORT_PATH
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_render_report(created_dirs), encoding="utf-8")
    _append_log(root, f"Generated migration compatibility map [[{REPORT_PATH.removesuffix('.md')}]].")
    return report, created_dirs


def _ensure_lifecycle_dirs(root: Path) -> list[str]:
    created = []
    for rel in LIFECYCLE_DIRS:
        path = root / rel
        if not path.exists():
            path.mkdir(parents=True)
            created.append(rel)
    return created


def _upsert_compatibility_section(path: Path, mapping: LegacyMapping) -> None:
    text = path.read_text(encoding="utf-8")
    section = "\n".join(
        [
            "## Lifecycle Compatibility",
            "",
            "This legacy root page remains supported for old links and product-memory continuity.",
            "",
            f"- Lifecycle stage: `{mapping.stage}`",
            f"- Compatibility mode: {mapping.compatibility_mode}",
            "- Canonical lifecycle artifacts:",
            *[f"  - [[{target.removesuffix('.md')}]]" for target in mapping.canonical_paths],
            f"- Migration map: [[{REPORT_PATH.removesuffix('.md')}]]",
            "",
        ]
    )
    pattern = r"\n## Lifecycle Compatibility\n.*?(?=\n## |\Z)"
    if re.search(pattern, text, flags=re.DOTALL):
        updated = re.sub(pattern, "\n" + section.rstrip(), text, count=1, flags=re.DOTALL)
    else:
        updated = text.rstrip() + "\n\n" + section.rstrip()
    path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def _render_report(created_dirs: list[str]) -> str:
    lines = [
        "---",
        "type: migration-compatibility",
        "status: active",
        "stage: governance-integrity",
        "owner: Governance Auditor",
        "---",
        "# Migration Compatibility Map",
        "",
        "## Purpose",
        "",
        "This map preserves old root wiki pages while Echel moves product memory into the vNext lifecycle folders. Legacy pages are compatibility summaries, not deleted history.",
        "",
        "## Directory Preparation",
        "",
    ]
    if created_dirs:
        lines.extend(f"- Created `wiki/{rel}/`." for rel in created_dirs)
    else:
        lines.append("- All lifecycle directories already existed.")
    lines.extend(
        [
            "",
            "## Legacy To Lifecycle Map",
            "",
            "| Legacy Surface | Lifecycle Stage | Canonical Lifecycle Artifacts | Compatibility Mode |",
            "| --- | --- | --- | --- |",
        ]
    )
    for mapping in LEGACY_MAPPINGS:
        targets = ", ".join(f"`wiki/{target}`" for target in mapping.canonical_paths)
        lines.append(f"| `wiki/{mapping.legacy_path}` | {mapping.stage} | {targets} | {mapping.compatibility_mode} |")
    lines.extend(
        [
            "",
            "## Compatibility Rules",
            "",
            "- Do not delete `wiki/project.md`, `wiki/problem.md`, `wiki/solution.md`, `wiki/scope.md`, `wiki/roadmap.md`, `wiki/architecture.md`, or `wiki/work/` while product code, graph extraction, cockpit views, or older prompts still reference them.",
            "- New lifecycle work should update the canonical lifecycle artifact first, then refresh or summarize the legacy page when compatibility readers need it.",
            "- Old links remain valid through the preserved files and the compatibility sections appended to each root page.",
            "- Initialization creates the lifecycle folders directly while still preserving these root compatibility surfaces.",
            "- Generated projects keep product memory at root `wiki/` and Echel Core under `echel-core/` with `WIKI_ROOT` set to `../wiki`.",
            "",
            "## Verification",
            "",
            "- `make wiki-health` validates links and governance artifacts.",
            "- `python3 tools/echel.py migration compatibility` regenerates this map and root-page compatibility sections.",
            "",
        ]
    )
    return "\n".join(lines)


def _append_log(root: Path, line: str) -> None:
    log = root / "log.md"
    if not log.exists():
        return
    text = log.read_text(encoding="utf-8")
    entry = f"\n## [2026-07-13] migration | compatibility\n- {line}\n"
    if line not in text:
        log.write_text(text.rstrip() + entry, encoding="utf-8")
