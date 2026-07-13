---
type: migration-compatibility
status: active
stage: governance-integrity
owner: Governance Auditor
---
# Migration Compatibility Map

## Purpose

This map preserves old root wiki pages while Echel moves product memory into the vNext lifecycle folders. Legacy pages are compatibility summaries, not deleted history.

## Directory Preparation

- All lifecycle directories already existed.

## Legacy To Lifecycle Map

| Legacy Surface | Lifecycle Stage | Canonical Lifecycle Artifacts | Compatibility Mode |
| --- | --- | --- | --- |
| `wiki/project.md` | repository-initialization | `wiki/project.md`, `wiki/canon/product-canon.md`, `wiki/canon/vision.md` | source summary |
| `wiki/problem.md` | discovery | `wiki/discovery/product-discovery-spec.md`, `wiki/canon/product-canon.md` | compatibility summary |
| `wiki/solution.md` | canon | `wiki/canon/product-canon.md`, `wiki/requirements/product-requirements.md` | compatibility summary |
| `wiki/scope.md` | requirements | `wiki/requirements/mvp-scope.md`, `wiki/requirements/out-of-scope.md` | compatibility summary |
| `wiki/roadmap.md` | roadmap | `wiki/roadmap/master-roadmap.md`, `wiki/roadmap/mvp-roadmap.md`, `wiki/roadmap/release-plan.md` | compatibility summary |
| `wiki/architecture.md` | architecture | `wiki/architecture/overview.md`, `wiki/architecture/component-architecture.md`, `wiki/architecture/data-architecture.md` | compatibility summary |
| `wiki/work/` | execution | `wiki/work/TASK_INDEX.md`, `wiki/execution/phase-0-foundation.md`, `wiki/execution/phase-4-evolution.md` | directory compatibility |

## Compatibility Rules

- Do not delete `wiki/project.md`, `wiki/problem.md`, `wiki/solution.md`, `wiki/scope.md`, `wiki/roadmap.md`, `wiki/architecture.md`, or `wiki/work/` while product code, graph extraction, cockpit views, or older prompts still reference them.
- New lifecycle work should update the canonical lifecycle artifact first, then refresh or summarize the legacy page when compatibility readers need it.
- Old links remain valid through the preserved files and the compatibility sections appended to each root page.
- Initialization now creates the lifecycle folders directly while still preserving these root compatibility surfaces.
- Generated projects keep product memory at root `wiki/` and Echel Core under `echel-core/` with `WIKI_ROOT` set to `../wiki`.

## Verification

- `make wiki-health` validates links and governance artifacts.
- `python3 tools/echel.py migration compatibility` regenerates this map and root-page compatibility sections.
