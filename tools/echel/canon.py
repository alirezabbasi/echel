from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path
from .discovery import DISCOVERY_FIELDS, PDS_FILE, discovery_root, _section_body, _is_tbd
from .memory_kernel import append_record, query_records


CANON_DIR = "canon"
CANON_FILE = "product-canon.md"
VISION_FILE = "vision.md"
PRINCIPLES_FILE = "product-principles.md"
NON_NEGOTIABLES_FILE = "non-negotiables.md"


def _stamp() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def canon_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    return wiki / CANON_DIR


def ensure_canon_files(repo_root: Path, cfg: ProjectConfig) -> Path:
    root = canon_root(repo_root, cfg)
    root.mkdir(parents=True, exist_ok=True)

    for name, default_fn in [
        (CANON_FILE, _default_canon),
        (VISION_FILE, _default_vision),
        (PRINCIPLES_FILE, _default_principles),
        (NON_NEGOTIABLES_FILE, _default_non_negotiables),
    ]:
        path = root / name
        if not path.exists():
            path.write_text(default_fn(), encoding="utf-8")

    return root


def canon_generate(repo_root: Path, cfg: ProjectConfig, force: bool = False) -> list[Path]:
    from .gates import run_stage_gate

    if not force:
        result = run_stage_gate(repo_root, cfg, "discovery")
        if not result.passed:
            raise ValueError(
                "discovery gate failed. Canon cannot be generated until discovery is complete.\n"
                "Use --force to override, or fix discovery gaps first.\n"
                + "\n".join(f"  - {f}" for f in result.failures)
            )

    root = ensure_canon_files(repo_root, cfg)
    d_root = discovery_root(repo_root, cfg)
    pds = d_root / "product-discovery-spec.md"
    pds_text = pds.read_text(encoding="utf-8") if pds.exists() else ""

    changed: list[Path] = []

    canon_path = root / CANON_FILE
    canon_text = canon_path.read_text(encoding="utf-8")
    new_canon = _populate_canon(canon_text, pds_text)
    if new_canon != canon_text:
        canon_path.write_text(new_canon, encoding="utf-8")
        changed.append(canon_path)

    vision_path = root / VISION_FILE
    vision_text = vision_path.read_text(encoding="utf-8")
    new_vision = _populate_vision(vision_text, pds_text)
    if new_vision != vision_text:
        vision_path.write_text(new_vision, encoding="utf-8")
        changed.append(vision_path)

    principles_path = root / PRINCIPLES_FILE
    principles_text = principles_path.read_text(encoding="utf-8")
    new_principles = _populate_principles(principles_text, pds_text)
    if new_principles != principles_text:
        principles_path.write_text(new_principles, encoding="utf-8")
        changed.append(principles_path)

    non_neg_path = root / NON_NEGOTIABLES_FILE
    non_neg_text = non_neg_path.read_text(encoding="utf-8")
    new_non_neg = _populate_non_negotiables(non_neg_text, pds_text)
    if new_non_neg != non_neg_text:
        non_neg_path.write_text(new_non_neg, encoding="utf-8")
        changed.append(non_neg_path)

    _append_log(root, "canon", "Generated or refreshed Product Canon from discovery.")
    return changed


def canon_status(repo_root: Path, cfg: ProjectConfig) -> str:
    root = canon_root(repo_root, cfg)
    if not root.exists():
        return "Canon not initialized. Run `echel canon` to start."

    files = {
        "product-canon": root / CANON_FILE,
        "vision": root / VISION_FILE,
        "principles": root / PRINCIPLES_FILE,
        "non-negotiables": root / NON_NEGOTIABLES_FILE,
    }

    lines = ["# Canon Status", ""]
    all_ready = True
    for name, path in files.items():
        if not path.exists():
            lines.append(f"- {name}: MISSING")
            all_ready = False
            continue
        text = path.read_text(encoding="utf-8")
        incomplete = _count_tbd_sections(text)
        if incomplete > 0:
            lines.append(f"- {name}: {incomplete} section(s) still TBD")
            all_ready = False
        else:
            lines.append(f"- {name}: ready")

    if all_ready:
        lines.append("")
        lines.append("Canon is ready for downstream planning.")
    else:
        lines.append("")
        lines.append("Run `echel canon` to refresh from discovery, or `echel canon --force` to override gaps.")

    return "\n".join(lines)


@dataclass(frozen=True)
class CanonDriftIssue:
    severity: str
    canon_file: str
    section: str
    message: str
    suggestion: str


DRIFT_SECTIONS = [
    ("product-canon.md", "What This Product Is", "02 Problem", "problem"),
    ("product-canon.md", "Who This Product Serves", "03 Users", "users"),
    ("product-canon.md", "Why Customers Would Pay or Adopt", "10 Business Model", "business-model"),
    ("vision.md", "Vision Statement", "09 Product Vision", "vision"),
    ("vision.md", "End State", "13 Non-Goals", "non-goals"),
    ("non-negotiables.md", "Hard Constraints", "14 Constraints", "constraints"),
]


def detect_canon_drift(repo_root: Path, cfg: ProjectConfig) -> list[CanonDriftIssue]:
    d_root = discovery_root(repo_root, cfg)
    c_root = canon_root(repo_root, cfg)
    pds = d_root / PDS_FILE
    if not pds.exists():
        return []
    pds_text = pds.read_text(encoding="utf-8")

    existing_contradictions = {
        r.title for r in query_records(repo_root, record_type="canon-drift", contradiction_only=True)
    }

    issues: list[CanonDriftIssue] = []
    for canon_file, canon_heading, pds_heading, field_key in DRIFT_SECTIONS:
        canon_path = c_root / canon_file
        if not canon_path.exists():
            continue
        canon_text = canon_path.read_text(encoding="utf-8")
        canon_body = _section_body(canon_text, canon_heading)
        pds_body = _extract_pds_section(pds_text, pds_heading)

        if _is_tbd(canon_body) and not _is_tbd(pds_body):
            title = f"canon-drift:{canon_file}:{field_key}"
            if title not in existing_contradictions:
                append_record(
                    repo_root,
                    record_type="canon-drift",
                    title=title,
                    links=[field_key],
                    contradiction=True,
                    payload={
                        "canon_file": canon_file,
                        "section": canon_heading,
                        "message": f"Canon section `{canon_heading}` is TBD but discovery field `{field_key}` has content",
                    },
                )
            issues.append(CanonDriftIssue(
                severity="warning",
                canon_file=canon_file,
                section=canon_heading,
                message=f"Canon `{canon_heading}` is stale: discovery field `{field_key}` has been updated",
                suggestion=f"Run `echel canon --force` to refresh, or update `{canon_heading}` manually",
            ))

    return issues


def canon_drift_report(repo_root: Path, cfg: ProjectConfig) -> str:
    issues = detect_canon_drift(repo_root, cfg)
    lines = ["# Canon Drift Report", ""]
    if not issues:
        lines.append("No canon drift detected. Canon is in sync with discovery.")
    else:
        lines.append(f"## {len(issues)} drift issue(s) found\n")
        for issue in issues:
            lines.append(f"### [{issue.severity}] {issue.canon_file} - {issue.section}")
            lines.append(f"- **Issue:** {issue.message}")
            lines.append(f"- **Action:** {issue.suggestion}")
            lines.append("")
    return "\n".join(lines)


def _populate_canon(canon_text: str, pds_text: str) -> str:
    problem = _compact(_extract_pds_section(pds_text, "02 Problem"))
    users = _compact(_extract_pds_section(pds_text, "03 Users"))
    buyers = _compact(_extract_pds_section(pds_text, "04 Buyers"))
    solution = _compact(_extract_pds_section(pds_text, "08 Proposed Solution"))
    vision = _compact(_extract_pds_section(pds_text, "09 Product Vision"))
    business = _compact(_extract_pds_section(pds_text, "10 Business Model"))
    success = _compact(_extract_pds_section(pds_text, "11 Success Criteria"))
    risks = _compact(_extract_pds_section(pds_text, "17 Risks"))
    competition = _compact(_extract_pds_section(pds_text, "18 Competitive Landscape"))

    if not _is_tbd(problem):
        canon_text = _replace_section(canon_text, "What This Product Is", f"This product solves: {problem}")
        canon_text = _replace_section(canon_text, "Why This Product Exists", problem)
    if not _is_tbd(users):
        canon_text = _replace_section(canon_text, "Who This Product Serves", users)
    if not _is_tbd(solution):
        canon_text = _replace_section(canon_text, "What This Product Is Not", f"This is not: {competition}" if not _is_tbd(competition) else "TBD")
    if not _is_tbd(business):
        canon_text = _replace_section(canon_text, "Why Customers Would Pay or Adopt", business)
    if not _is_tbd(vision):
        canon_text = _replace_section(canon_text, "Why Now", vision)

    return canon_text


def _populate_vision(vision_text: str, pds_text: str) -> str:
    vision = _compact(_extract_pds_section(pds_text, "09 Product Vision"))
    success = _compact(_extract_pds_section(pds_text, "11 Success Criteria"))
    non_goals = _compact(_extract_pds_section(pds_text, "13 Non-Goals"))

    if not _is_tbd(vision):
        vision_text = _replace_section(vision_text, "Vision Statement", vision)
    if not _is_tbd(success):
        vision_text = _replace_section(vision_text, "Business Transformation", success)
    if not _is_tbd(non_goals):
        vision_text = _replace_section(vision_text, "End State", non_goals)

    return vision_text


def _populate_principles(principles_text: str, pds_text: str) -> str:
    constraints = _compact(_extract_pds_section(pds_text, "14 Constraints"))
    assumptions = _compact(_extract_pds_section(pds_text, "15 Assumptions"))

    if not _is_tbd(constraints):
        principles_text = _replace_section(principles_text, "Decision Framework", f"Constraints: {constraints}")
    if not _is_tbd(assumptions):
        principles_text = _replace_section(principles_text, "Principles in Practice", f"Key assumptions: {assumptions}")

    return principles_text


def _populate_non_negotiables(non_neg_text: str, pds_text: str) -> str:
    constraints = _compact(_extract_pds_section(pds_text, "14 Constraints"))
    non_goals = _compact(_extract_pds_section(pds_text, "13 Non-Goals"))

    if not _is_tbd(constraints):
        non_neg_text = _replace_section(non_neg_text, "Hard Constraints", constraints)
    if not _is_tbd(non_goals):
        non_neg_text = _replace_section(non_neg_text, "What We Must NEVER Do", non_goals)

    return non_neg_text


def _extract_pds_section(pds_text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, pds_text, flags=re.DOTALL)
    return m.group(1).strip() if m else ""


def _replace_section(text: str, heading: str, body: str) -> str:
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


def _compact(value: str) -> str:
    cleaned = " ".join(line.strip("- ").strip() for line in value.splitlines() if line.strip())
    if not cleaned or cleaned == "TBD":
        return "TBD"
    return cleaned[:500]


def _count_tbd_sections(text: str) -> int:
    count = 0
    for match in re.finditer(r"## .+\n(.*?)(?=\n## |\Z)", text, flags=re.DOTALL):
        body = match.group(1).strip()
        if body in {"", "TBD", "- TBD"}:
            count += 1
    return count


def _append_log(root: Path, label: str, line: str) -> None:
    log = root.parent / "log.md"
    if not log.exists():
        log.write_text("---\ntype: log\nstatus: active\n---\n# Log\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{_stamp()}] {label} | canon\n- {line}\n")


def _default_canon() -> str:
    return """---
type: product-canon
status: draft
stage: canon
---
# Product Canon

This document is the primary source of product truth. Every downstream artifact must reference and refine canon rather than reinterpret it. When canon changes, all dependent stages must be reevaluated.

## What This Product Is

TBD

## What This Product Is Not

TBD

## Why This Product Exists

TBD

## Who This Product Serves

TBD

## Why Customers Would Pay or Adopt

TBD

## Why Now

TBD

## Product Category

TBD

## Product Identity

| Field | Value |
| --- | --- |
| Category | TBD |
| Type | TBD (tool, platform, service, infrastructure, marketplace) |
| Industry | TBD |
| Stage | TBD |

## Strategic Risks

| ID | Risk | Impact | Mitigation | Statement Type | Confidence |
| --- | --- | --- | --- | --- | --- |
| `R-001` | TBD | TBD | TBD | risk | TBD |

## Execution Risks

| ID | Risk | Impact | Mitigation | Statement Type | Confidence |
| --- | --- | --- | --- | --- | --- |
| `R-002` | TBD | TBD | TBD | risk | TBD |

## Discovery References

This canon is derived from the following discovery artifacts:

| ID | Source | Section |
| --- | --- | --- |
| `P-001` | product-discovery-spec.md | 02 Problem |
| `U-001` | product-discovery-spec.md | 03 Users |
| `B-001` | product-discovery-spec.md | 04 Buyers |
| `S-001` | product-discovery-spec.md | 11 Success Criteria |

## Quality Gate

Before proceeding to Product Strategy, this document must pass:

- [ ] What the product is clearly stated
- [ ] What the product is not clearly stated
- [ ] Why the product exists clearly stated
- [ ] Who the product serves identified
- [ ] Why customers would pay or adopt explained
- [ ] Why now is justified
- [ ] Product category and identity defined
- [ ] Strategic risks identified
- [ ] Execution risks identified
- [ ] Discovery IDs referenced
"""


def _default_vision() -> str:
    return """---
type: product-vision
status: draft
stage: canon
---
# Product Vision

This document defines where the product ends and what business transformation it enables. Vision must be specific, not buzzword-driven.

## Vision Statement

TBD

## Business Transformation

What changes for the customer when this product succeeds?

TBD

## End State

Where does this product journey end?

TBD

## What This Product Is NOT

- Not a TBD
- Not a TBD
- Not a TBD

## Non-Goals

| ID | Non-Goal | Rationale |
| --- | --- | --- |
| `NC-001` | TBD | TBD |

## Discovery References

| ID | Source | Section |
| --- | --- | --- |
| `S-001` | product-discovery-spec.md | 11 Success Criteria |

## Quality Gate

- [ ] Vision is specific and measurable
- [ ] Business transformation is clear
- [ ] End state is defined
- [ ] Non-goals are explicit
- [ ] No fake platform language
"""


def _default_principles() -> str:
    return """---
type: product-principles
status: draft
stage: canon
---
# Product Principles

These are the core principles that guide every product decision. They must not be compromised for短期 convenience.

## Core Principles

| ID | Principle | Statement Type | Confidence |
| --- | --- | --- | --- |
| TBD | TBD | decision | TBD |

## Decision Framework

When principles conflict, use this hierarchy:

1. Customer value over internal convenience
2. Simplicity over feature breadth
3. Evidence over assumption
4. Durability over speed

## Principles in Practice

### How We Say No

TBD

### How We Handle Trade-offs

TBD

### What We Do When Principles Conflict

TBD

## Discovery References

| ID | Source | Section |
| --- | --- | --- |
| `A-001` | product-discovery-spec.md | 15 Assumptions |

## Quality Gate

- [ ] Core principles are defined
- [ ] Principles are specific enough to guide decisions
- [ ] Decision framework is clear
- [ ] Principles are derived from discovery insights
"""


def _default_non_negotiables() -> str:
    return """---
type: product-non-negotiables
status: draft
stage: canon
---
# Non-Negotiables

These are the constraints and requirements that cannot be violated under any circumstances. They override all other considerations.

## Hard Constraints

| ID | Constraint | Category | Statement Type | Confidence |
| --- | --- | --- | --- | --- |
| `C-001` | TBD | TBD | constraint | TBD |

## Legal and Compliance Requirements

| ID | Requirement | Category | Statement Type | Confidence |
| --- | --- | --- | --- | --- |
| TBD | TBD | legal | constraint | TBD |

## Security Requirements

| ID | Requirement | Statement Type | Confidence |
| --- | --- | --- | --- |
| TBD | TBD | constraint | TBD |

## Data Requirements

| ID | Requirement | Statement Type | Confidence |
| --- | --- | --- | --- |
| TBD | TBD | constraint | TBD |

## Performance Requirements

| ID | Requirement | Statement Type | Confidence |
| --- | --- | --- | --- |
| TBD | TBD | constraint | TBD |

## Availability Requirements

| ID | Requirement | Statement Type | Confidence |
| --- | --- | --- | --- |
| TBD | TBD | constraint | TBD |

## What We Must NEVER Do

- TBD
- TBD
- TBD

## Discovery References

| ID | Source | Section |
| --- | --- | --- |
| `C-001` | product-discovery-spec.md | 14 Constraints |

## Quality Gate

- [ ] Hard constraints are explicit
- [ ] Legal and compliance requirements are listed
- [ ] Security requirements are defined
- [ ] Data requirements are defined
- [ ] Performance requirements are defined
- [ ] "Must never do" list is complete
- [ ] All constraints trace back to discovery
"""
