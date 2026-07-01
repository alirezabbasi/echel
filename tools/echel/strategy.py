from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path
from .discovery import discovery_root, _section_body, _is_tbd


STRATEGY_DIR = "strategy"
STRATEGY_FILES = [
    "icp.md",
    "buyer-user-model.md",
    "market-wedge.md",
    "competitive-analysis.md",
    "positioning.md",
    "pricing-and-packaging.md",
    "pmf-evidence.md",
]


def _stamp() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def strategy_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    return wiki / STRATEGY_DIR


def ensure_strategy_files(repo_root: Path, cfg: ProjectConfig) -> Path:
    root = strategy_root(repo_root, cfg)
    root.mkdir(parents=True, exist_ok=True)

    for name in STRATEGY_FILES:
        path = root / name
        if not path.exists():
            default_fn = _DEFAULTS.get(name)
            if default_fn:
                path.write_text(default_fn(), encoding="utf-8")

    return root


def strategy_status(repo_root: Path, cfg: ProjectConfig) -> str:
    root = strategy_root(repo_root, cfg)
    if not root.exists():
        return "Strategy not initialized. Run `echel strategy` to start."

    lines = ["# Strategy Status", ""]
    all_ready = True
    for name in STRATEGY_FILES:
        path = root / name
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
        lines.append("Strategy is ready for downstream planning.")
    else:
        lines.append("")
        lines.append("Run `echel strategy` to refresh from canon, or `echel strategy --force` to override gaps.")

    return "\n".join(lines)


def strategy_readiness(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    root = strategy_root(repo_root, cfg)
    failures: list[str] = []

    icp_path = root / "icp.md"
    if icp_path.exists():
        text = icp_path.read_text(encoding="utf-8")
        if _section_incomplete(_extract_section(text, "Primary ICP")):
            failures.append("strategy field `icp` is incomplete: ICP must be defined")
    else:
        failures.append("strategy file missing: wiki/strategy/icp.md")

    buyer_path = root / "buyer-user-model.md"
    if buyer_path.exists():
        text = buyer_path.read_text(encoding="utf-8")
        if _section_incomplete(_extract_section(text, "Economic Buyer")):
            failures.append("strategy field `buyer` is incomplete: Economic buyer must be identified")
    else:
        failures.append("strategy file missing: wiki/strategy/buyer-user-model.md")

    wedge_path = root / "market-wedge.md"
    if wedge_path.exists():
        text = wedge_path.read_text(encoding="utf-8")
        if _section_incomplete(_extract_section(text, "Wedge Definition")):
            failures.append("strategy field `wedge` is incomplete: Market wedge must be defined")
    else:
        failures.append("strategy file missing: wiki/strategy/market-wedge.md")

    pmf_path = root / "pmf-evidence.md"
    if pmf_path.exists():
        text = pmf_path.read_text(encoding="utf-8")
        continue_section = _extract_section(text, "Continue Criteria")
        stop_section = _extract_section(text, "Stop Criteria")
        if _section_incomplete(continue_section) or _section_incomplete(stop_section):
            failures.append("strategy field `pmf` is incomplete: PMF evidence must have continue/stop criteria")
    else:
        failures.append("strategy file missing: wiki/strategy/pmf-evidence.md")

    pricing_path = root / "pricing-and-packaging.md"
    if pricing_path.exists():
        text = pricing_path.read_text(encoding="utf-8")
        if _section_incomplete(_extract_section(text, "Pricing Model")):
            failures.append("strategy field `pricing` is incomplete: Pricing model must be defined")
    else:
        failures.append("strategy file missing: wiki/strategy/pricing-and-packaging.md")

    return failures


def strategy_generate(repo_root: Path, cfg: ProjectConfig, force: bool = False) -> list[Path]:
    from .gates import run_stage_gate

    if not force:
        result = run_stage_gate(repo_root, cfg, "discovery")
        if not result.passed:
            raise ValueError(
                "discovery gate failed. Strategy cannot be generated until discovery is complete.\n"
                "Use --force to override, or fix discovery gaps first.\n"
                + "\n".join(f"  - {f}" for f in result.failures)
            )

    root = ensure_strategy_files(repo_root, cfg)
    d_root = discovery_root(repo_root, cfg)
    pds = d_root / "product-discovery-spec.md"
    pds_text = pds.read_text(encoding="utf-8") if pds.exists() else ""

    changed: list[Path] = []

    icp_path = root / "icp.md"
    icp_text = icp_path.read_text(encoding="utf-8")
    new_icp = _populate_icp(icp_text, pds_text)
    if new_icp != icp_text:
        icp_path.write_text(new_icp, encoding="utf-8")
        changed.append(icp_path)

    buyer_path = root / "buyer-user-model.md"
    buyer_text = buyer_path.read_text(encoding="utf-8")
    new_buyer = _populate_buyer(buyer_text, pds_text)
    if new_buyer != buyer_text:
        buyer_path.write_text(new_buyer, encoding="utf-8")
        changed.append(buyer_path)

    wedge_path = root / "market-wedge.md"
    wedge_text = wedge_path.read_text(encoding="utf-8")
    new_wedge = _populate_wedge(wedge_text, pds_text)
    if new_wedge != wedge_text:
        wedge_path.write_text(new_wedge, encoding="utf-8")
        changed.append(wedge_path)

    comp_path = root / "competitive-analysis.md"
    comp_text = comp_path.read_text(encoding="utf-8")
    new_comp = _populate_competitive(comp_text, pds_text)
    if new_comp != comp_text:
        comp_path.write_text(new_comp, encoding="utf-8")
        changed.append(comp_path)

    pos_path = root / "positioning.md"
    pos_text = pos_path.read_text(encoding="utf-8")
    new_pos = _populate_positioning(pos_text, pds_text)
    if new_pos != pos_text:
        pos_path.write_text(new_pos, encoding="utf-8")
        changed.append(pos_path)

    pricing_path = root / "pricing-and-packaging.md"
    pricing_text = pricing_path.read_text(encoding="utf-8")
    new_pricing = _populate_pricing(pricing_text, pds_text)
    if new_pricing != pricing_text:
        pricing_path.write_text(new_pricing, encoding="utf-8")
        changed.append(pricing_path)

    pmf_path = root / "pmf-evidence.md"
    pmf_text = pmf_path.read_text(encoding="utf-8")
    new_pmf = _populate_pmf(pmf_text, pds_text)
    if new_pmf != pmf_text:
        pmf_path.write_text(new_pmf, encoding="utf-8")
        changed.append(pmf_path)

    _append_log(root, "strategy", "Generated or refreshed Product Strategy from canon.")
    return changed


def _populate_icp(icp_text: str, pds_text: str) -> str:
    users = _compact(_extract_pds_section(pds_text, "03 Users"))
    buyers = _compact(_extract_pds_section(pds_text, "04 Buyers"))
    competition = _compact(_extract_pds_section(pds_text, "18 Competitive Landscape"))

    if not _is_tbd(users):
        icp_text = _replace_section(icp_text, "Primary ICP", f"Target users: {users}")
    if not _is_tbd(buyers):
        icp_text = _replace_section(icp_text, "Secondary ICP", f"Target buyers: {buyers}")
    if not _is_tbd(competition):
        icp_text = _replace_section(icp_text, "Anti-ICP", f"Alternatives: {competition}")

    return icp_text


def _populate_buyer(buyer_text: str, pds_text: str) -> str:
    users = _compact(_extract_pds_section(pds_text, "03 Users"))
    buyers = _compact(_extract_pds_section(pds_text, "04 Buyers"))
    operators = _compact(_extract_pds_section(pds_text, "05 Operators"))

    if not _is_tbd(buyers):
        buyer_text = _replace_section(buyer_text, "Economic Buyer", buyers)
    if not _is_tbd(users):
        buyer_text = _replace_section(buyer_text, "User", users)
    if not _is_tbd(operators):
        buyer_text = _replace_section(buyer_text, "Operator", operators)

    return buyer_text


def _populate_wedge(wedge_text: str, pds_text: str) -> str:
    problem = _compact(_extract_pds_section(pds_text, "02 Problem"))
    pain = _compact(_extract_pds_section(pds_text, "07 Pain Points"))
    competition = _compact(_extract_pds_section(pds_text, "18 Competitive Landscape"))

    if not _is_tbd(problem):
        wedge_text = _replace_section(wedge_text, "The Problem We Solve", problem)
    if not _is_tbd(pain):
        wedge_text = _replace_section(wedge_text, "What They Do Today", pain)
    if not _is_tbd(competition):
        wedge_text = _replace_section(wedge_text, "Why That Is Broken", f"Current alternatives: {competition}")

    return wedge_text


def _populate_competitive(comp_text: str, pds_text: str) -> str:
    competition = _compact(_extract_pds_section(pds_text, "18 Competitive Landscape"))
    problem = _compact(_extract_pds_section(pds_text, "02 Problem"))

    if not _is_tbd(competition):
        comp_text = _replace_section(comp_text, "Direct Competitors", competition)
    if not _is_tbd(problem):
        comp_text = _replace_section(comp_text, "Do Nothing", f"Cost of doing nothing: {problem}")

    return comp_text


def _populate_positioning(pos_text: str, pds_text: str) -> str:
    solution = _compact(_extract_pds_section(pds_text, "08 Proposed Solution"))
    vision = _compact(_extract_pds_section(pds_text, "09 Product Vision"))
    success = _compact(_extract_pds_section(pds_text, "11 Success Criteria"))

    if not _is_tbd(solution):
        pos_text = _replace_section(pos_text, "Key Benefit", solution)
    if not _is_tbd(vision):
        pos_text = _replace_section(pos_text, "Differentiator", vision)
    if not _is_tbd(success):
        pos_text = _replace_section(pos_text, "Proof Points", f"Success metrics: {success}")

    return pos_text


def _populate_pricing(pricing_text: str, pds_text: str) -> str:
    business = _compact(_extract_pds_section(pds_text, "10 Business Model"))
    constraints = _compact(_extract_pds_section(pds_text, "14 Constraints"))
    success = _compact(_extract_pds_section(pds_text, "11 Success Criteria"))

    if not _is_tbd(business):
        pricing_text = _replace_section(pricing_text, "Pricing Model", f"Business model: {business}")
    if not _is_tbd(constraints):
        pricing_text = _replace_section(pricing_text, "Revenue Projections", f"Constraints: {constraints}")
    if not _is_tbd(success):
        pricing_text = _replace_section(pricing_text, "Pricing Validation", f"Success criteria: {success}")

    return pricing_text


def _populate_pmf(pmf_text: str, pds_text: str) -> str:
    success = _compact(_extract_pds_section(pds_text, "11 Success Criteria"))
    assumptions = _compact(_extract_pds_section(pds_text, "15 Assumptions"))
    risks = _compact(_extract_pds_section(pds_text, "17 Risks"))

    if not _is_tbd(success):
        pmf_text = _replace_section(pmf_text, "Continue Criteria", f"Success signals: {success}")
    if not _is_tbd(assumptions):
        pmf_text = _replace_section(pmf_text, "Stop Criteria", f"If assumptions fail: {assumptions}")
    if not _is_tbd(risks):
        pmf_text = _replace_section(pmf_text, "Decision Framework", f"Risk signals: {risks}")

    return pmf_text


def _extract_pds_section(pds_text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, pds_text, flags=re.DOTALL)
    return m.group(1).strip() if m else ""


def _extract_section(text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, text, flags=re.DOTALL)
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


def _section_incomplete(body: str) -> bool:
    if not body.strip():
        return True
    cleaned = body.strip()
    if cleaned == "TBD" or cleaned == "- TBD":
        return True
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    content_lines = []
    for line in lines:
        if line.startswith("**") or line.startswith("|") or line.startswith("#") or line.startswith("---"):
            continue
        if line in {"TBD", "- TBD", "TBD"}:
            continue
        if line.startswith("- ID:") or line.startswith("- Type:") or line.startswith("- Confidence:"):
            continue
        if line.startswith("| `") and "TBD" in line:
            continue
        content_lines.append(line)
    return len(content_lines) == 0


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
        f.write(f"\n## [{_stamp()}] {label} | strategy\n- {line}\n")


def _default_icp() -> str:
    return """---
type: strategy-icp
status: draft
stage: strategy
---
# Ideal Customer Profile

This document defines the specific customer segment we serve first. The ICP must be concrete enough that a sales or marketing team could identify and reach these customers.

## Primary ICP

| Field | Value |
| --- | --- |
| Segment Name | TBD |
| Industry | TBD |
| Company Size | TBD |
| Role | TBD |
| Pain Level | TBD |
| Budget | TBD |
| Decision Speed | TBD |

## ICP Characteristics

### Demographics

- Industry: TBD
- Company size: TBD
- Geography: TBD
- Revenue range: TBD
- Technology stack: TBD

### Behavioral Signals

- Currently using: TBD
- Trigger event: TBD
- Buying process: TBD
- Timeline to purchase: TBD

### Pain Indicators

- Primary pain: TBD
- Frequency of pain: TBD
- Cost of pain: TBD
- Current workaround: TBD

## Secondary ICP

| Field | Value |
| --- | --- |
| Segment Name | TBD |
| Industry | TBD |
| Company Size | TBD |
| Role | TBD |

## Anti-ICP

Who we explicitly do NOT serve:

- TBD
- TBD
- TBD

## Discovery References

| ID | Source | Section |
| --- | --- | --- |
| `U-001` | product-discovery-spec.md | 03 Users |
| `B-001` | product-discovery-spec.md | 04 Buyers |
| `ICP-001` | product-discovery-spec.md | 18 Competitive Landscape |

## Quality Gate

- [ ] ICP is specific enough to identify real customers
- [ ] Industry and company size are defined
- [ ] Role and pain indicators are clear
- [ ] Anti-ICP is explicit
- [ ] ICP traces back to discovery users and buyers
"""


def _default_buyer() -> str:
    return """---
type: strategy-buyer-user-model
status: draft
stage: strategy
---
# Buyer and User Model

This document separates every stakeholder role. Confusing buyer with user is one of the most common product strategy mistakes.

## Stakeholder Roles

### Economic Buyer

The person who signs the contract and controls the budget.

| Field | Value |
| --- | --- |
| Role Title | TBD |
| Department | TBD |
| Reporting Line | TBD |
| Budget Authority | TBD |
| Primary Concern | TBD |
| Success Metric | TBD |

### User

The person who uses the product daily.

| Field | Value |
| --- | --- |
| Role Title | TBD |
| Department | TBD |
| Daily Tasks | TBD |
| Pain Points | TBD |
| Success Metric | TBD |

### Approver

The person who must approve the purchase.

| Field | Value |
| --- | --- |
| Role Title | TBD |
| Department | TBD |
| Approval Criteria | TBD |
| Concerns | TBD |

### Influencer

The person who recommends or evaluates the product.

| Field | Value |
| --- | --- |
| Role Title | TBD |
| Department | TBD |
| Influence Type | TBD |
| Evaluation Criteria | TBD |

### Blocker

The person who can stop the deal.

| Field | Value |
| --- | --- |
| Role Title | TBD |
| Department | TBD |
| Blocking Reason | TBD |
| Mitigation | TBD |

### Operator

The person who operates or supports the product.

| Field | Value |
| --- | --- |
| Role Title | TBD |
| Department | TBD |
| Operational Tasks | TBD |
| Success Metric | TBD |

## Stakeholder Matrix

| Role | Title | Concern | Success Metric |
| --- | --- | --- | --- |
| Economic Buyer | TBD | TBD | TBD |
| User | TBD | TBD | TBD |
| Approver | TBD | TBD | TBD |
| Influencer | TBD | TBD | TBD |
| Blocker | TBD | TBD | TBD |
| Operator | TBD | TBD | TBD |

## Discovery References

| ID | Source | Section |
| --- | --- | --- |
| `U-001` | product-discovery-spec.md | 03 Users |
| `B-001` | product-discovery-spec.md | 04 Buyers |
| `O-001` | product-discovery-spec.md | 05 Operators |

## Quality Gate

- [ ] Economic buyer is identified and separated from user
- [ ] User role is clearly defined
- [ ] Approver is identified
- [ ] Influencer is identified
- [ ] Blocker is identified
- [ ] Operator is identified
- [ ] Each role has distinct concerns and success metrics
"""


def _default_wedge() -> str:
    return """---
type: strategy-market-wedge
status: draft
stage: strategy
---
# Market Wedge

This document defines the specific market entry point. A wedge is the smallest, most painful use case we can win first.

## Wedge Definition

| Field | Value |
| --- | --- |
| Wedge Name | TBD |
| Target Segment | TBD |
| Primary Pain | TBD |
| Current Alternative | TBD |
| Why We Win | TBD |

## First Use Case

### The Problem We Solve

TBD

### Who Experiences It

TBD

### How Often

TBD

### What They Do Today

TBD

### Why That Is Broken

TBD

### What Changes When We Win

TBD

## Wedge Strength

### Pain Intensity

- Rating: TBD (1-10)
- Evidence: TBD

### Urgency

- Rating: TBD (1-10)
- Evidence: TBD

### Willingness to Pay

- Rating: TBD (1-10)
- Evidence: TBD

### Switching Cost

- Rating: TBD (1-10)
- Evidence: TBD

## Adoption Barriers

| Barrier | Severity | Mitigation |
| --- | --- | --- |
| TBD | TBD | TBD |

## Wedge Expansion

After winning the wedge, we expand to:

1. TBD
2. TBD
3. TBD

## Discovery References

| ID | Source | Section |
| --- | --- | --- |
| `P-001` | product-discovery-spec.md | 02 Problem |
| `PP-001` | product-discovery-spec.md | 07 Pain Points |
| `CMP-001` | product-discovery-spec.md | 18 Competitive Landscape |

## Quality Gate

- [ ] Wedge is specific and narrow enough to win
- [ ] Pain intensity is rated with evidence
- [ ] Urgency is rated with evidence
- [ ] Willingness to pay is rated with evidence
- [ ] Switching cost is rated with evidence
- [ ] Adoption barriers are identified
- [ ] Expansion path is defined
"""


def _default_competitive() -> str:
    return """---
type: strategy-competitive-analysis
status: draft
stage: strategy
---
# Competitive Analysis

This document maps all alternatives customers use today, not only direct competitors. The biggest competitor is often "do nothing."

## Direct Competitors

| ID | Name | Strength | Weakness | Pricing | Market Share |
| --- | --- | --- | --- | --- | --- |
| `CMP-001` | TBD | TBD | TBD | TBD | TBD |

## Indirect Competitors

| ID | Name | Type | Strength | Weakness |
| --- | --- | --- | --- | --- |
| `CMP-002` | TBD | TBD | TBD | TBD |

## Non-Software Alternatives

| ID | Alternative | Why Customers Use It | Limitation |
| --- | --- | --- | --- |
| `CMP-003` | TBD | TBD | TBD |

## Do Nothing

| Field | Value |
| --- | --- |
| Why customers do nothing | TBD |
| Cost of doing nothing | TBD |
| Trigger to change | TBD |

## Competitive Positioning

### Our Advantage

TBD

### Our Disadvantage

TBD

### Differentiation

TBD

## Win/Loss Analysis

### When We Win

- TBD
- TBD

### When We Lose

- TBD
- TBD

## Competitive Response Plan

| Competitor | Their Likely Response | Our Counter |
| --- | --- | --- |
| TBD | TBD | TBD |

## Discovery References

| ID | Source | Section |
| --- | --- | --- |
| `CMP-001` | product-discovery-spec.md | 18 Competitive Landscape |
| `P-001` | product-discovery-spec.md | 02 Problem |

## Quality Gate

- [ ] Direct competitors are identified
- [ ] Indirect competitors are identified
- [ ] Non-software alternatives are listed
- [ ] "Do nothing" alternative is analyzed
- [ ] Win/loss patterns are documented
- [ ] Competitive response plan exists
"""


def _default_positioning() -> str:
    return """---
type: strategy-positioning
status: draft
stage: strategy
---
# Positioning

This document defines how we want customers to understand and remember our product. Positioning is not marketing copy; it is the strategic choice of where we compete.

## Positioning Statement

For [target customer] who [need], [product name] is a [category] that [key benefit]. Unlike [alternative], we [differentiator].

## Positioning Elements

### Target Customer

TBD

### Category

TBD

### Key Benefit

TBD

### Differentiator

TBD

### Alternative

TBD

## Category Design

### Existing Category

- Category name: TBD
- Our position: TBD
- Our advantage: TBD

### New Category

- Category name: TBD
- Why new: TBD
- How we define it: TBD

## Messaging Framework

### Primary Message

TBD

### Supporting Messages

1. TBD
2. TBD
3. TBD

### Proof Points

| Message | Proof |
| --- | --- |
| TBD | TBD |

## Brand Personality

| Trait | Description |
| --- | --- |
| Voice | TBD |
| Tone | TBD |
| Style | TBD |

## Positioning Validation

### Customer Perception

- How customers describe us: TBD
- How customers describe competitors: TBD
- Gap to close: TBD

### Market Readiness

- Category awareness: TBD
- Buyer readiness: TBD
- Timing: TBD

## Discovery References

| ID | Source | Section |
| --- | --- | --- |
| `S-001` | product-discovery-spec.md | 11 Success Criteria |
| `CMP-001` | product-discovery-spec.md | 18 Competitive Landscape |

## Quality Gate

- [ ] Positioning statement is clear
- [ ] Category choice is deliberate
- [ ] Key benefit is specific
- [ ] Differentiator is defensible
- [ ] Messaging framework is defined
- [ ] Positioning is validated against customer perception
"""


def _default_pricing() -> str:
    return """---
type: strategy-pricing-packaging
status: draft
stage: strategy
---
# Pricing and Packaging

This document defines how we monetize. All pricing is hypothesis-level unless explicitly validated.

## Pricing Model

| Field | Value |
| --- | --- |
| Model Type | TBD (subscription, usage, license, freemium, marketplace) |
| Billing Unit | TBD |
| Billing Frequency | TBD |
| Statement Type | hypothesis |
| Confidence | TBD |

## Pricing Tiers

### Free / Trial

| Field | Value |
| --- | --- |
| Purpose | TBD |
| Limits | TBD |
| Conversion Goal | TBD |

### Tier 1

| Field | Value |
| --- | --- |
| Name | TBD |
| Price | TBD |
| Includes | TBD |
| Target Segment | TBD |

### Tier 2

| Field | Value |
| --- | --- |
| Name | TBD |
| Price | TBD |
| Includes | TBD |
| Target Segment | TBD |

### Enterprise

| Field | Value |
| --- | --- |
| Name | TBD |
| Price | TBD |
| Includes | TBD |
| Target Segment | TBD |

## Packaging Strategy

### What Goes in Each Tier

| Feature | Free | Tier 1 | Tier 2 | Enterprise |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |

### Upsell Triggers

- TBD
- TBD

## Pricing Validation

### Price Sensitivity

- Method: TBD
- Results: TBD
- Confidence: TBD

### Willingness to Pay

- Method: TBD
- Results: TBD
- Confidence: TBD

### Competitive Benchmarking

| Competitor | Their Price | Our Price | Justification |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

## Revenue Projections

| Metric | Value | Confidence |
| --- | --- | --- |
| ARPU | TBD | hypothesis |
| LTV | TBD | hypothesis |
| CAC | TBD | hypothesis |
| Payback Period | TBD | hypothesis |

## Discovery References

| ID | Source | Section |
| --- | --- | --- |
| `S-001` | product-discovery-spec.md | 11 Success Criteria |
| `C-001` | product-discovery-spec.md | 14 Constraints |

## Quality Gate

- [ ] Pricing model is defined
- [ ] All pricing is marked as hypothesis unless validated
- [ ] Pricing tiers are clear
- [ ] Packaging strategy is defined
- [ ] Price sensitivity has been tested
- [ ] Revenue projections are documented with confidence levels
"""


def _default_pmf() -> str:
    return """---
type: strategy-pmf-evidence
status: draft
stage: strategy
---
# PMF Evidence

This document defines what evidence we need to prove or disprove product-market fit. Every piece of evidence must have continue and stop criteria.

## PMF Definition

What does PMF mean for this product?

TBD

## Evidence Plan

### Continue Criteria

These signals tell us to keep going:

| ID | Signal | Metric | Target | Current | Status |
| --- | --- | --- | --- | --- | --- |
| `PMF-001` | TBD | TBD | TBD | TBD | not measured |

### Stop Criteria

These signals tell us to pivot or stop:

| ID | Signal | Metric | Threshold | Current | Status |
| --- | --- | --- | --- | --- | --- |
| `PMF-002` | TBD | TBD | TBD | TBD | not measured |

## Evidence Types

### Customer Evidence

| ID | Evidence Type | Method | Target | Status |
| --- | --- | --- | --- | --- |
| `PMF-003` | TBD | TBD | TBD | not started |

### Market Evidence

| ID | Evidence Type | Method | Target | Status |
| --- | --- | --- | --- | --- |
| `PMF-004` | TBD | TBD | TBD | not started |

### Product Evidence

| ID | Evidence Type | Method | Target | Status |
| --- | --- | --- | --- | --- |
| `PMF-005` | TBD | TBD | TBD | not started |

### Financial Evidence

| ID | Evidence Type | Method | Target | Status |
| --- | --- | --- | --- | --- |
| `PMF-006` | TBD | TBD | TBD | not started |

## Evidence Collection Plan

### Phase 1: Validation

- TBD
- TBD

### Phase 2: Early Traction

- TBD
- TBD

### Phase 3: Scale

- TBD
- TBD

## PMF Scorecard

| Metric | Target | Current | Status |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

## Decision Framework

### When to Continue

- TBD
- TBD

### When to Pivot

- TBD
- TBD

### When to Stop

- TBD
- TBD

## Discovery References

| ID | Source | Section |
| --- | --- | --- |
| `S-001` | product-discovery-spec.md | 11 Success Criteria |
| `H-001` | product-discovery-spec.md | 16 Hypotheses |
| `R-001` | product-discovery-spec.md | 17 Risks |

## Quality Gate

- [ ] PMF definition is clear
- [ ] Continue criteria are defined with measurable metrics
- [ ] Stop criteria are defined with measurable thresholds
- [ ] Evidence types cover customer, market, product, and financial signals
- [ ] Evidence collection plan has phases
- [ ] Decision framework is explicit
"""


_DEFAULTS = {
    "icp.md": _default_icp,
    "buyer-user-model.md": _default_buyer,
    "market-wedge.md": _default_wedge,
    "competitive-analysis.md": _default_competitive,
    "positioning.md": _default_positioning,
    "pricing-and-packaging.md": _default_pricing,
    "pmf-evidence.md": _default_pmf,
}
