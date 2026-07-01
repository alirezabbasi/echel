from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path


DISCOVERY_DIR = "discovery"
PDS_FILE = "product-discovery-spec.md"
RESEARCH_FILE = "research-plan.md"
ASSUMPTIONS_FILE = "assumptions.md"


@dataclass(frozen=True)
class DiscoveryField:
    key: str
    file: str
    heading: str
    question: str


DISCOVERY_FIELDS = [
    DiscoveryField("problem", PDS_FILE, "02 Problem", "What exact problem are we solving?"),
    DiscoveryField("problem-statement", PDS_FILE, "Problem Statement", "What is the problem statement?"),
    DiscoveryField("current-process", PDS_FILE, "Current Process", "What is the current process?"),
    DiscoveryField("current-pain", PDS_FILE, "Current Pain", "What pain exists today?"),
    DiscoveryField("why-fails", PDS_FILE, "Why Existing Solutions Fail", "Why do existing solutions fail?"),
    DiscoveryField("cost-of-inaction", PDS_FILE, "Cost of Doing Nothing", "What is the cost of doing nothing?"),
    DiscoveryField("urgency", PDS_FILE, "Urgency", "Why does this matter now?"),
    DiscoveryField("users", PDS_FILE, "03 Users", "Who are the primary users?"),
    DiscoveryField("buyers", PDS_FILE, "04 Buyers", "Who are the buyers?"),
    DiscoveryField("operators", PDS_FILE, "05 Operators", "Who operates or supports the product?"),
    DiscoveryField("workflow", PDS_FILE, "06 Current Workflow", "What is the current workflow without the product?"),
    DiscoveryField("pain-points", PDS_FILE, "07 Pain Points", "What are the specific pain points?"),
    DiscoveryField("solution", PDS_FILE, "08 Proposed Solution", "What is the proposed solution concept?"),
    DiscoveryField("vision", PDS_FILE, "09 Product Vision", "What is the product vision?"),
    DiscoveryField("business-model", PDS_FILE, "10 Business Model", "How does money flow?"),
    DiscoveryField("success", PDS_FILE, "11 Success Criteria", "What measurable success criteria exist?"),
    DiscoveryField("scope", PDS_FILE, "12 Scope", "What belongs in the MVP?"),
    DiscoveryField("non-goals", PDS_FILE, "13 Non-Goals", "What is explicitly out of scope?"),
    DiscoveryField("constraints", PDS_FILE, "14 Constraints", "What constraints exist?"),
    DiscoveryField("assumptions", PDS_FILE, "15 Assumptions", "What assumptions are we making?"),
    DiscoveryField("hypotheses", PDS_FILE, "16 Hypotheses", "What hypotheses need testing?"),
    DiscoveryField("risks", PDS_FILE, "17 Risks", "What are the major risks?"),
    DiscoveryField("competition", PDS_FILE, "18 Competitive Landscape", "What are the current alternatives?"),
    DiscoveryField("functional-overview", PDS_FILE, "19 Functional Overview", "What are the high-level capabilities?"),
    DiscoveryField("non-functional", PDS_FILE, "20 Non-Functional Expectations", "What non-functional expectations exist?"),
    DiscoveryField("business-rules", PDS_FILE, "21 Business Rules", "What business rules are known?"),
    DiscoveryField("open-questions", PDS_FILE, "22 Open Questions", "What questions remain unanswered?"),
    DiscoveryField("research", PDS_FILE, "23 Research Plan", "What research is required?"),
]


def _stamp() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def discovery_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    return wiki / DISCOVERY_DIR


def ensure_discovery_files(repo_root: Path, cfg: ProjectConfig, product_name: str = "Product") -> Path:
    root = discovery_root(repo_root, cfg)
    root.mkdir(parents=True, exist_ok=True)

    pds = root / PDS_FILE
    if not pds.exists():
        pds.write_text(_default_pds(product_name), encoding="utf-8")

    research = root / RESEARCH_FILE
    if not research.exists():
        research.write_text(_default_research(), encoding="utf-8")

    assumptions = root / ASSUMPTIONS_FILE
    if not assumptions.exists():
        assumptions.write_text(_default_assumptions(), encoding="utf-8")

    return root


def discover_status(repo_root: Path, cfg: ProjectConfig) -> str:
    root = discovery_root(repo_root, cfg)
    pds = root / PDS_FILE
    if not pds.exists():
        return "Discovery not initialized. Run `echel discover` to start."

    text = pds.read_text(encoding="utf-8")
    total = len(DISCOVERY_FIELDS)
    answered = 0
    gaps: list[str] = []

    for field in DISCOVERY_FIELDS:
        body = _section_body(text, field.heading)
        if not _is_tbd(body):
            answered += 1
        else:
            gaps.append(f"- `{field.key}`: {field.question}")

    readiness = round((answered / total) * 100) if total else 0

    lines = [
        "# Discovery Status",
        "",
        f"- Readiness: {readiness}% ({answered}/{total} fields answered)",
        f"- PDS: {pds}",
        f"- Research: {root / RESEARCH_FILE}",
        f"- Assumptions: {root / ASSUMPTIONS_FILE}",
        "",
        "## Open Gaps",
    ]
    lines.extend(gaps or ["- None"])
    return "\n".join(lines)


def discover_update(repo_root: Path, cfg: ProjectConfig, field_key: str, value: str) -> Path:
    root = ensure_discovery_files(repo_root, cfg)
    pds = root / PDS_FILE

    field = next((f for f in DISCOVERY_FIELDS if f.key == field_key), None)
    if field is None:
        known = ", ".join(f.key for f in DISCOVERY_FIELDS)
        raise ValueError(f"unknown discovery field '{field_key}'. Known fields: {known}")

    text = pds.read_text(encoding="utf-8")
    text = _replace_section_body(text, field.heading, value)
    pds.write_text(text, encoding="utf-8")

    _append_log(root, "discover", f"Updated `{field_key}` in Product Discovery Specification.")
    return pds


def discover_questions(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    root = discovery_root(repo_root, cfg)
    pds = root / PDS_FILE
    if not pds.exists():
        return [f"{f.key}: {f.question}" for f in DISCOVERY_FIELDS]

    text = pds.read_text(encoding="utf-8")
    gaps: list[str] = []
    for field in DISCOVERY_FIELDS:
        body = _section_body(text, field.heading)
        if _is_tbd(body):
            gaps.append(f"{field.key}: {field.question}")
    return gaps


def _section_body(text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, text, flags=re.DOTALL)
    return m.group(1).strip() if m else ""


def _replace_section_body(text: str, heading: str, body: str) -> str:
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


def _is_tbd(value: str) -> bool:
    cleaned = value.strip()
    return cleaned in {"", "TBD", "- TBD"}


def _append_log(root: Path, label: str, line: str) -> None:
    log = root.parent / "log.md"
    if not log.exists():
        log.write_text("---\ntype: log\nstatus: active\n---\n# Log\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{_stamp()}] {label} | discovery\n- {line}\n")


def _default_pds(product_name: str) -> str:
    return f"""---
type: product-discovery-spec
status: draft
stage: discovery
---
# Product Discovery Specification

This document is the founder/platform contract. It captures everything the platform needs to know before any downstream work begins. Every statement must be classified by type and confidence. Important entries must carry a traceability ID.

## Statement Types

Every statement in this document must be tagged with one of:

| Type | Meaning |
| --- | --- |
| fact | Verified information |
| observation | Directly observed |
| assumption | Believed but unverified |
| hypothesis | Needs testing |
| decision | Explicitly chosen |
| constraint | Cannot be changed |
| risk | Possible negative outcome |
| question | Still unresolved |

## Confidence Levels

Important entries must include a confidence level:

- `high`: strong evidence or owner certainty.
- `medium`: plausible but needs validation.
- `low`: weakly supported or exploratory.

AI agents must never treat assumptions or hypotheses as facts.

---

## 01 Executive Summary

| Field | Value |
| --- | --- |
| Product Name | {product_name} |
| One-sentence description | TBD |
| Category | TBD |
| Target industry | TBD |
| Current stage | Discovery |
| Author | TBD |
| Date | TBD |
| Revision | TBD |

---

## 02 Problem

**Statement type:** fact or observation
**Confidence:** TBD

### Problem Statement {{#P-001}}

- ID: `P-001`
- Type: TBD
- Confidence: TBD

TBD

### Current Process

TBD

### Current Pain

TBD

### Why Existing Solutions Fail

TBD

### Cost of Doing Nothing

TBD

### Evidence

TBD

### Urgency

TBD

### Who Experiences It

TBD

### Frequency

TBD

### Severity

TBD

---

## 03 Users

### Primary Users {{#U-001}}

| ID | Role | Description | Statement Type | Confidence |
| --- | --- | --- | --- | --- |
| `U-001` | TBD | TBD | TBD | TBD |

### User Goals

TBD

### User Constraints

TBD

---

## 04 Buyers

### Buyer Model {{#B-001}}

| ID | Role | Description | Statement Type | Confidence |
| --- | --- | --- | --- | --- |
| `B-001` | TBD | TBD | TBD | TBD |

### Economic Buyer

- Who signs the contract? TBD
- Who pays? TBD
- Who approves? TBD
- Who blocks? TBD
- Who influences? TBD

---

## 05 Operators

### Operator Model {{#O-001}}

| ID | Role | Description | Statement Type | Confidence |
| --- | --- | --- | --- | --- |
| `O-001` | TBD | TBD | TBD | TBD |

---

## 06 Current Workflow

### Workflow {{#WF-001}}

- ID: `WF-001`
- Type: TBD
- Confidence: TBD

Describe the current process step by step without the proposed product.

TBD

### Workflow Steps

1. TBD
2. TBD
3. TBD

---

## 07 Pain Points

### Pain Point {{#PP-001}}

| ID | Description | Frequency | Business Cost | Operational Cost | Workaround | Root Cause | Importance | Statement Type | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `PP-001` | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

---

## 08 Proposed Solution

**Statement type:** decision or hypothesis
**Confidence:** TBD

### Solution Concept

TBD

### Core Capabilities

- TBD

### Differentiation

TBD

---

## 09 Product Vision

**Statement type:** decision
**Confidence:** TBD

Where does this product end? What business transformation happens?

TBD

---

## 10 Business Model

**Statement type:** assumption or hypothesis
**Confidence:** TBD

How does money flow?

- License: TBD
- SaaS: TBD
- Subscription: TBD
- Marketplace: TBD
- Professional Services: TBD
- Support: TBD
- Training: TBD
- Usage: TBD
- Revenue Share: TBD

---

## 11 Success Criteria

### Business Success {{#S-001}}

| ID | Criterion | Type | Confidence |
| --- | --- | --- | --- |
| `S-001` | TBD | TBD | TBD |

### Technical Success

| ID | Criterion | Type | Confidence |
| --- | --- | --- | --- |
| `S-002` | TBD | TBD | TBD |

### Operational Success

| ID | Criterion | Type | Confidence |
| --- | --- | --- | --- |
| `S-003` | TBD | TBD | TBD |

### Customer Success

| ID | Criterion | Type | Confidence |
| --- | --- | --- | --- |
| `S-004` | TBD | TBD | TBD |

### Financial Success

| ID | Criterion | Type | Confidence |
| --- | --- | --- | --- |
| `S-005` | TBD | TBD | TBD |

---

## 12 Scope

### MVP

- TBD

### Version 1

- TBD

### Version 2

- TBD

### Future

- TBD

---

## 13 Non-Goals

**Statement type:** decision

| ID | Non-Goal | Rationale |
| --- | --- | --- |
| `NC-001` | TBD | TBD |

Without explicit non-goals, scope expands forever.

---

## 14 Constraints

| ID | Constraint | Category | Statement Type | Confidence |
| --- | --- | --- | --- | --- |
| `C-001` | TBD | budget | TBD | TBD |
| `C-002` | TBD | time | TBD | TBD |
| `C-003` | TBD | people | TBD | TBD |
| `C-004` | TBD | technology | TBD | TBD |
| `C-005` | TBD | legal | TBD | TBD |
| `C-006` | TBD | compliance | TBD | TBD |

---

## 15 Assumptions

**Statement type:** assumption

| ID | Assumption | Confidence | Impact if Wrong | Validation Method |
| --- | --- | --- | --- | --- |
| `A-001` | TBD | TBD | TBD | TBD |

---

## 16 Hypotheses

**Statement type:** hypothesis

| ID | Hypothesis | Confidence | Test Method | Success Signal | Failure Signal |
| --- | --- | --- | --- | --- | --- |
| `H-001` | TBD | TBD | TBD | TBD | TBD |

---

## 17 Risks

| ID | Risk | Category | Impact | Likelihood | Mitigation | Statement Type | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `R-001` | TBD | business | TBD | TBD | TBD | TBD | TBD |
| `R-002` | TBD | technical | TBD | TBD | TBD | TBD | TBD |
| `R-003` | TBD | operational | TBD | TBD | TBD | TBD | TBD |
| `R-004` | TBD | financial | TBD | TBD | TBD | TBD | TBD |
| `R-005` | TBD | market | TBD | TBD | TBD | TBD | TBD |
| `R-006` | TBD | execution | TBD | TBD | TBD | TBD | TBD |
| `R-007` | TBD | legal | TBD | TBD | TBD | TBD | TBD |
| `R-008` | TBD | vendor | TBD | TBD | TBD | TBD | TBD |

---

## 18 Competitive Landscape

| ID | Alternative | Type | Strength | Weakness | Switching Cost |
| --- | --- | --- | --- | --- | --- |
| `CMP-001` | TBD | TBD | TBD | TBD | TBD |

Current alternatives include not only software but also Excel, email, phone, consultants, legacy systems, custom software, and doing nothing.

---

## 19 Functional Overview

High level capabilities. No architecture.

- TBD

---

## 20 Non-Functional Expectations

| Category | Expectation | Statement Type | Confidence |
| --- | --- | --- | --- |
| Availability | TBD | TBD | TBD |
| Performance | TBD | TBD | TBD |
| Scalability | TBD | TBD | TBD |
| Security | TBD | TBD | TBD |
| Compliance | TBD | TBD | TBD |
| Observability | TBD | TBD | TBD |
| Maintainability | TBD | TBD | TBD |

---

## 21 Business Rules

| ID | Rule | Statement Type | Confidence |
| --- | --- | --- | --- |
| `BR-001` | TBD | TBD | TBD |

Business rules are business truth, not database design.

---

## 22 Open Questions

| ID | Question | Owner | Priority | Due Date | Statement Type |
| --- | --- | --- | --- | --- | --- |
| `Q-001` | TBD | TBD | TBD | TBD | question |

Do not hide unknowns.

---

## 23 Research Plan

| ID | Topic | Method | Owner | Due Date | Status |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | not started |

Research areas:
- Market
- Technology
- Legal
- Domain
- Competition

---

## 24 References

- Papers: TBD
- Products: TBD
- Links: TBD
- Standards: TBD
- Specifications: TBD

---

## 25 Appendix

Sketches, whiteboard notes, screenshots, raw ideas.

TBD

---

## Quality Gate

Before proceeding to Product Canon, this document must pass:

- [ ] Problem clearly defined
- [ ] Buyer identified
- [ ] User identified
- [ ] Operator identified
- [ ] Current workflow documented
- [ ] Business value measurable
- [ ] Non-goals documented
- [ ] Constraints documented
- [ ] Success criteria measurable
- [ ] Major risks identified
- [ ] Assumptions listed with confidence
- [ ] Open questions documented
- [ ] Research plan exists
- [ ] MVP scope defined

If one fails, do not proceed.

---

## Traceability

This document originates the following ID families:

- `P-###`: problem and pain points
- `U-###`: users
- `B-###`: buyers
- `O-###`: operators
- `WF-###`: workflows
- `PP-###`: pain points
- `A-###`: assumptions
- `H-###`: hypotheses
- `R-###`: risks
- `S-###`: success criteria
- `Q-###`: open questions
- `C-###`: constraints
- `NC-###`: non-goals
- `BR-###`: business rules

Downstream artifacts must reference these IDs rather than reinterpreting the content.
"""


def _default_research() -> str:
    return """---
type: discovery-research-plan
status: draft
stage: discovery
---
# Research Plan

This document tracks research activities required before later lifecycle stages can proceed. Research findings must be recorded with statement type and confidence.

## Research Areas

### Market Research

| ID | Topic | Method | Owner | Due Date | Status | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | not started | TBD |

### Technology Research

| ID | Topic | Method | Owner | Due Date | Status | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | not started | TBD |

### Legal Research

| ID | Topic | Method | Owner | Due Date | Status | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | not started | TBD |

### Domain Research

| ID | Topic | Method | Owner | Due Date | Status | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | not started | TBD |

### Competition Research

| ID | Topic | Method | Owner | Due Date | Status | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | not started | TBD |

## Research Rules

- Every research finding must be tagged with statement type (`fact`, `observation`, `assumption`, `hypothesis`).
- Every research finding must include confidence level.
- Research that invalidates upstream assumptions must trigger a contradiction record and propagate the change.
- Research results feed into the Product Discovery Specification, Product Canon, and Product Strategy.

## Research Completion Criteria

Research is complete when:

- [ ] Market size and wedge are validated or explicitly marked as hypothesis.
- [ ] Technology constraints are confirmed.
- [ ] Legal and compliance requirements are identified.
- [ ] Domain terminology is stable.
- [ ] Competitive landscape is mapped.
- [ ] All high-priority open questions from the PDS are answered or accepted.
"""


def _default_assumptions() -> str:
    return """---
type: discovery-assumptions
status: draft
stage: discovery
---
# Assumptions

This document tracks all assumptions, hypotheses, and open questions for the product. Every entry must include a traceability ID, statement type, confidence level, and validation method.

## Active Assumptions

| ID | Assumption | Confidence | Impact if Wrong | Validation Method | Status | Resolved By |
| --- | --- | --- | --- | --- | --- | --- |
| `A-001` | TBD | TBD | TBD | TBD | active | TBD |

## Active Hypotheses

| ID | Hypothesis | Confidence | Test Method | Success Signal | Failure Signal | Status | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `H-001` | TBD | TBD | TBD | TBD | TBD | active | TBD |

## Open Questions

| ID | Question | Owner | Priority | Due Date | Status | Answer |
| --- | --- | --- | --- | --- | --- | --- |
| `Q-001` | TBD | TBD | TBD | TBD | open | TBD |

## Resolved Items

| ID | Original Type | Statement | Resolution | Resolved Date | Changed Downstream |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD |

## Assumption Tracking Rules

- Every assumption must be validated or explicitly accepted before the discovery gate passes.
- Low-confidence assumptions that affect scope, architecture, or release readiness must remain visible until resolved.
- When an assumption is validated, update its status to `validated` and record the evidence.
- When an assumption is invalidated, record the contradiction and propagate the change to all downstream artifacts that referenced it.
- Hypotheses must be tested with explicit success and failure signals before they can be promoted to facts.
- Open questions must have an owner and a due date.

## Confidence Validation Rules

| Confidence | Required Action |
| --- | --- |
| high | Evidence must exist or owner must explicitly accept responsibility. |
| medium | Validation plan must exist within current lifecycle stage. |
| low | Must not block downstream stages. Must be escalated or resolved before release. |
"""
