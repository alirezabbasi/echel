from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from .canon import canon_root
from .config import ProjectConfig, resolve_symbolic_path
from .graph import write_graph
from .strategy import strategy_readiness, strategy_root


REQUIREMENTS_DIR = "requirements"
PRODUCT_FILE = "product-requirements.md"
FUNCTIONAL_FILE = "functional-requirements.md"
NFR_FILE = "non-functional-requirements.md"
MVP_FILE = "mvp-scope.md"
OOS_FILE = "out-of-scope.md"
AC_FILE = "acceptance-criteria.md"

VAGUE_TERMS = {
    "best platform",
    "world-class",
    "easy to use",
    "user-friendly",
    "modern",
    "robust",
    "scalable",
    "powerful",
    "seamless",
    "innovative",
    "next generation",
    "all-in-one",
}


@dataclass(frozen=True)
class RequirementCandidate:
    req_id: str
    title: str
    capability: str
    statement: str
    priority: str
    phase: str
    source_ids: list[str]
    dependencies: str
    risks: str
    acceptance_id: str
    acceptance: str
    validation_method: str


@dataclass(frozen=True)
class NfrCandidate:
    nfr_id: str
    category: str
    requirement: str
    target: str
    priority: str
    phase: str
    source_ids: list[str]
    dependencies: str
    risks: str
    acceptance_id: str
    verification_method: str


@dataclass(frozen=True)
class ScopeExclusion:
    oos_id: str
    item: str
    rationale: str
    source_ids: list[str]
    related_requirements: str
    revisit_trigger: str


def _stamp() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def requirements_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    return wiki / REQUIREMENTS_DIR


def ensure_requirements_files(repo_root: Path, cfg: ProjectConfig) -> Path:
    root = requirements_root(repo_root, cfg)
    root.mkdir(parents=True, exist_ok=True)
    defaults = {
        PRODUCT_FILE: _default_product_requirements(),
        FUNCTIONAL_FILE: _default_functional_requirements(),
        NFR_FILE: _default_non_functional_requirements(),
        MVP_FILE: _default_mvp_scope(),
        OOS_FILE: _default_out_of_scope(),
        AC_FILE: _default_acceptance_criteria(),
    }
    for name, text in defaults.items():
        path = root / name
        if not path.exists():
            path.write_text(text, encoding="utf-8")
    return root


def requirements_status(repo_root: Path, cfg: ProjectConfig) -> str:
    root = requirements_root(repo_root, cfg)
    if not root.exists():
        return "Requirements not initialized. Run `echel requirements` to start."

    files = {
        "product-requirements": root / PRODUCT_FILE,
        "functional-requirements": root / FUNCTIONAL_FILE,
        "non-functional-requirements": root / NFR_FILE,
        "mvp-scope": root / MVP_FILE,
        "out-of-scope": root / OOS_FILE,
        "acceptance-criteria": root / AC_FILE,
    }

    lines = ["# Requirements Status", ""]
    for name, path in files.items():
        if not path.exists():
            lines.append(f"- {name}: MISSING")
            continue
        text = path.read_text(encoding="utf-8")
        generated = len(re.findall(r"\b(?:REQ|NFR|AC|OOS)-1\d\d\b", text))
        vague = _vague_failures(text)
        state = f"{generated} generated ID(s)"
        if vague:
            state += f", {len(vague)} vague phrase(s)"
        lines.append(f"- {name}: {state}")

    graph_nodes = _requirements_graph_node_count(repo_root, cfg)
    lines += ["", f"- Graph requirement nodes: {graph_nodes}"]
    return "\n".join(lines)


def requirements_generate(repo_root: Path, cfg: ProjectConfig, force: bool = False) -> list[Path]:
    if not force:
        failures = strategy_readiness(repo_root, cfg)
        if failures:
            raise ValueError(
                "strategy readiness failed. Requirements cannot be generated until strategy is complete.\n"
                "Use --force to override, or fix strategy gaps first.\n"
                + "\n".join(f"  - {f}" for f in failures)
            )

    root = ensure_requirements_files(repo_root, cfg)
    sources = _read_sources(repo_root, cfg)
    source_vague = _source_vague_failures(sources)
    if source_vague:
        raise ValueError("requirements source is too vague:\n" + "\n".join(f"  - {f}" for f in source_vague))

    reqs, nfrs, exclusions = _build_candidates(sources)
    if not reqs and not nfrs and not exclusions:
        if force:
            _append_log(root, "requirements", "No meaningful canon or strategy content available for requirement generation.")
            return []
        raise ValueError("no meaningful canon or strategy content available for requirement generation")

    candidate_vague = _candidate_vague_failures(reqs, nfrs)
    if candidate_vague:
        raise ValueError("generated requirements are too vague:\n" + "\n".join(f"  - {f}" for f in candidate_vague))

    changed = _write_requirement_artifacts(root, reqs, nfrs, exclusions)
    graph_path = _write_requirement_graph(repo_root, cfg, reqs, nfrs)
    if graph_path not in changed:
        changed.append(graph_path)
    _append_log(root, "requirements", f"Generated or refreshed {len(reqs)} requirements and {len(nfrs)} non-functional requirements.")
    return changed


def _read_sources(repo_root: Path, cfg: ProjectConfig) -> dict[str, str]:
    c_root = canon_root(repo_root, cfg)
    s_root = strategy_root(repo_root, cfg)
    product = _read(c_root / "product-canon.md")
    vision = _read(c_root / "vision.md")
    principles = _read(c_root / "product-principles.md")
    non_neg = _read(c_root / "non-negotiables.md")
    return {
        "canon_is": _extract_section(product, "What This Product Is"),
        "canon_not": _extract_section(product, "What This Product Is Not"),
        "canon_serves": _extract_section(product, "Who This Product Serves"),
        "canon_adoption": _extract_section(product, "Why Customers Would Pay or Adopt"),
        "vision_transformation": _extract_section(vision, "Business Transformation"),
        "principles": _extract_section(principles, "Principles in Practice"),
        "non_negotiables": _extract_section(non_neg, "Hard Constraints"),
        "icp": _extract_section(_read(s_root / "icp.md"), "Primary ICP"),
        "buyer": _extract_section(_read(s_root / "buyer-user-model.md"), "Economic Buyer"),
        "user": _extract_section(_read(s_root / "buyer-user-model.md"), "User"),
        "operator": _extract_section(_read(s_root / "buyer-user-model.md"), "Operator"),
        "wedge": _extract_section(_read(s_root / "market-wedge.md"), "Wedge Definition"),
        "positioning": _extract_section(_read(s_root / "positioning.md"), "Positioning Statement"),
        "pricing": _extract_section(_read(s_root / "pricing-and-packaging.md"), "Pricing Model"),
        "pmf_continue": _extract_section(_read(s_root / "pmf-evidence.md"), "Continue Criteria"),
        "pmf_stop": _extract_section(_read(s_root / "pmf-evidence.md"), "Stop Criteria"),
    }


def _build_candidates(sources: dict[str, str]) -> tuple[list[RequirementCandidate], list[NfrCandidate], list[ScopeExclusion]]:
    reqs: list[RequirementCandidate] = []
    nfrs: list[NfrCandidate] = []
    exclusions: list[ScopeExclusion] = []

    if _meaningful(sources["icp"]) or _meaningful(sources["canon_serves"]):
        reqs.append(RequirementCandidate(
            "REQ-101",
            "Serve the primary customer segment",
            "Customer Scope",
            f"The product must support the primary customer segment defined by strategy: {_brief(sources['icp'] or sources['canon_serves'])}.",
            "P0",
            "MVP",
            ["ICP-001", "CANON-001"],
            "None",
            "Building outside the first ICP can dilute MVP focus.",
            "AC-101",
            "A product review can identify the primary customer segment in requirements and MVP scope.",
            "Traceability review against ICP and product canon",
        ))

    if _meaningful(sources["wedge"]):
        reqs.append(RequirementCandidate(
            "REQ-102",
            "Support the first market wedge",
            "Market Wedge",
            f"The product must prioritize the first market wedge before broader expansion: {_brief(sources['wedge'])}.",
            "P0",
            "MVP",
            ["PW-001", "CANON-001"],
            "REQ-101",
            "A broad wedge can cause over-scoped requirements.",
            "AC-102",
            "MVP scope names the wedge and excludes non-wedge work.",
            "Scope review against market-wedge.md",
        ))

    if _meaningful(sources["buyer"]) or _meaningful(sources["user"]) or _meaningful(sources["operator"]):
        reqs.append(RequirementCandidate(
            "REQ-103",
            "Respect buyer, user, and operator separation",
            "Stakeholder Model",
            "The product must preserve separate buyer, user, and operator needs when defining scope and acceptance.",
            "P0",
            "MVP",
            ["B-001", "U-001", "O-001", "CANON-002"],
            "REQ-101",
            "Confusing buyer and user needs can produce invalid product decisions.",
            "AC-103",
            "Requirement review shows buyer, user, and operator impacts are not merged.",
            "Stakeholder traceability review",
        ))

    if _meaningful(sources["pmf_continue"]) or _meaningful(sources["pmf_stop"]):
        reqs.append(RequirementCandidate(
            "REQ-104",
            "Collect product-market-fit decision evidence",
            "PMF Evidence",
            "The product must support explicit continue/stop evidence before scaling beyond MVP.",
            "P1",
            "V1",
            ["PMF-001", "STRAT-001"],
            "REQ-101, REQ-102",
            "Unmeasured PMF can move weak assumptions into execution.",
            "AC-104",
            "PMF continue and stop criteria are linked to validation evidence.",
            "PMF evidence review",
        ))

    if _meaningful(sources["pricing"]):
        reqs.append(RequirementCandidate(
            "REQ-105",
            "Preserve pricing and packaging assumptions",
            "Commercial Model",
            f"The product must keep pricing and packaging assumptions visible during scope decisions: {_brief(sources['pricing'])}.",
            "P1",
            "V1",
            ["STRAT-002", "CANON-003"],
            "REQ-101",
            "Hidden pricing assumptions can distort MVP packaging.",
            "AC-105",
            "Pricing assumptions are visible in requirements and can be validated or rejected.",
            "Commercial assumption review",
        ))

    if _meaningful(sources["non_negotiables"]):
        nfrs.append(NfrCandidate(
            "NFR-101",
            "Non-Negotiables",
            f"The product must comply with canon non-negotiables: {_brief(sources['non_negotiables'])}.",
            "No MVP requirement violates hard constraints.",
            "P0",
            "MVP",
            ["C-001", "CANON-004"],
            "None",
            "Constraint violations can invalidate architecture and delivery planning.",
            "AC-106",
            "Constraint review",
        ))

    if _meaningful(sources["canon_not"]):
        exclusions.append(ScopeExclusion(
            "OOS-101",
            _brief(sources["canon_not"]),
            "Canon explicitly states this is not part of the product identity.",
            ["CANON-005"],
            ", ".join(r.req_id for r in reqs) or "All requirements",
            "Canon changes or explicit product decision",
        ))

    return reqs, nfrs, exclusions


def _write_requirement_artifacts(root: Path, reqs: list[RequirementCandidate], nfrs: list[NfrCandidate], exclusions: list[ScopeExclusion]) -> list[Path]:
    changed: list[Path] = []
    writers = [
        (root / PRODUCT_FILE, _generated_product_section(reqs)),
        (root / FUNCTIONAL_FILE, _generated_functional_section(reqs)),
        (root / NFR_FILE, _generated_nfr_section(nfrs)),
        (root / MVP_FILE, _generated_mvp_section(reqs, nfrs)),
        (root / OOS_FILE, _generated_oos_section(exclusions)),
        (root / AC_FILE, _generated_ac_section(reqs, nfrs)),
    ]
    for path, section in writers:
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        new = _replace_section(old, "Generated by `echel requirements`", section)
        if new != old:
            path.write_text(new, encoding="utf-8")
            changed.append(path)
    return changed


def _write_requirement_graph(repo_root: Path, cfg: ProjectConfig, reqs: list[RequirementCandidate], nfrs: list[NfrCandidate]) -> Path:
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    path = wiki / "graph.manual.json"
    manual = _manual_graph(path)
    nodes = manual.setdefault("nodes", [])
    edges = manual.setdefault("edges", [])

    def upsert_node(node: dict) -> None:
        existing = next((n for n in nodes if isinstance(n, dict) and n.get("id") == node["id"]), None)
        if existing:
            existing.update(node)
        else:
            nodes.append(node)

    def upsert_edge(edge: dict) -> None:
        if edge not in edges:
            edges.append(edge)

    for source_id in sorted({sid for req in reqs for sid in req.source_ids} | {sid for nfr in nfrs for sid in nfr.source_ids}):
        upsert_node({"id": f"trace:{source_id}", "type": "trace-source", "title": source_id, "source": "requirements", "summary": "Upstream methodology source ID"})

    for req in reqs:
        node_id = f"requirement:{req.req_id}"
        upsert_node({"id": node_id, "type": "requirement", "title": f"{req.req_id} {req.title}", "source": "requirements/product-requirements.md", "summary": req.statement})
        upsert_edge({"from_id": "product:root", "to_id": node_id, "type": "requires"})
        for source_id in req.source_ids:
            upsert_edge({"from_id": f"trace:{source_id}", "to_id": node_id, "type": "source_for"})

    for nfr in nfrs:
        node_id = f"requirement:{nfr.nfr_id}"
        upsert_node({"id": node_id, "type": "requirement", "title": f"{nfr.nfr_id} {nfr.category}", "source": "requirements/non-functional-requirements.md", "summary": nfr.requirement})
        upsert_edge({"from_id": "product:root", "to_id": node_id, "type": "requires"})
        for source_id in nfr.source_ids:
            upsert_edge({"from_id": f"trace:{source_id}", "to_id": node_id, "type": "source_for"})

    manual["version"] = 1
    path.write_text(json.dumps(manual, indent=2) + "\n", encoding="utf-8")
    write_graph(repo_root, cfg)
    return path


def _generated_product_section(reqs: list[RequirementCandidate]) -> str:
    lines = [
        "This section is generated from canon and strategy. Manual edits should happen in the source artifacts or be intentionally preserved outside this generated block.",
        "",
        "| ID | Title | Type | Priority | Phase | Source IDs | Dependencies | Risks | Acceptance | Validation Method | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for req in reqs:
        lines.append(f"| {req.req_id} | {req.title} | Product | {req.priority} | {req.phase} | {_join(req.source_ids)} | {req.dependencies} | {req.risks} | {req.acceptance_id} | {req.validation_method} | Generated |")
    if not reqs:
        lines.append("| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |")
    return "\n".join(lines)


def _generated_functional_section(reqs: list[RequirementCandidate]) -> str:
    lines = [
        "| ID | Capability | Statement | Priority | Phase | Source IDs | Dependencies | Risks | Acceptance | Test Method | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for req in reqs:
        lines.append(f"| {req.req_id} | {req.capability} | {req.statement} | {req.priority} | {req.phase} | {_join(req.source_ids)} | {req.dependencies} | {req.risks} | {req.acceptance_id} | {req.validation_method} | Generated |")
    if not reqs:
        lines.append("| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |")
    return "\n".join(lines)


def _generated_nfr_section(nfrs: list[NfrCandidate]) -> str:
    lines = [
        "| ID | Category | Requirement | Target | Priority | Phase | Source IDs | Dependencies | Risks | Acceptance | Verification Method | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for nfr in nfrs:
        lines.append(f"| {nfr.nfr_id} | {nfr.category} | {nfr.requirement} | {nfr.target} | {nfr.priority} | {nfr.phase} | {_join(nfr.source_ids)} | {nfr.dependencies} | {nfr.risks} | {nfr.acceptance_id} | {nfr.verification_method} | Generated |")
    if not nfrs:
        lines.append("| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |")
    return "\n".join(lines)


def _generated_mvp_section(reqs: list[RequirementCandidate], nfrs: list[NfrCandidate]) -> str:
    lines = [
        "| Requirement ID | Title | Why Included | Source IDs | Dependencies | Acceptance | Exit Evidence |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for req in [r for r in reqs if r.phase == "MVP"]:
        lines.append(f"| {req.req_id} | {req.title} | Required to satisfy canon and strategy before downstream domain work | {_join(req.source_ids)} | {req.dependencies} | {req.acceptance_id} | {req.validation_method} |")
    for nfr in [n for n in nfrs if n.phase == "MVP"]:
        lines.append(f"| {nfr.nfr_id} | {nfr.category} | Required to preserve non-functional constraints before architecture | {_join(nfr.source_ids)} | {nfr.dependencies} | {nfr.acceptance_id} | {nfr.verification_method} |")
    if len(lines) == 2:
        lines.append("| TBD | TBD | TBD | TBD | TBD | TBD | TBD |")
    return "\n".join(lines)


def _generated_oos_section(exclusions: list[ScopeExclusion]) -> str:
    lines = [
        "| ID | Item | Current Phase | Rationale | Source IDs | Related Requirements | Revisit Trigger | Decision Owner | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in exclusions:
        lines.append(f"| {item.oos_id} | {item.item} | MVP | {item.rationale} | {_join(item.source_ids)} | {item.related_requirements} | {item.revisit_trigger} | Product | Generated |")
    if not exclusions:
        lines.append("| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |")
    return "\n".join(lines)


def _generated_ac_section(reqs: list[RequirementCandidate], nfrs: list[NfrCandidate]) -> str:
    lines = [
        "| ID | Requirement IDs | Criterion | Evidence Required | Validation Method | Source IDs | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for req in reqs:
        lines.append(f"| {req.acceptance_id} | {req.req_id} | {req.acceptance} | Requirement and scope rows show the expected source links | {req.validation_method} | {_join(req.source_ids)} | Generated |")
    for nfr in nfrs:
        lines.append(f"| {nfr.acceptance_id} | {nfr.nfr_id} | {nfr.target} | NFR row and constraint review evidence | {nfr.verification_method} | {_join(nfr.source_ids)} | Generated |")
    if len(lines) == 2:
        lines.append("| TBD | TBD | TBD | TBD | TBD | TBD | Draft |")
    return "\n".join(lines)


def _source_vague_failures(sources: dict[str, str]) -> list[str]:
    failures = []
    for key, value in sources.items():
        meaningful = _meaningful(value)
        if meaningful:
            for term in sorted(VAGUE_TERMS):
                if term in value.lower():
                    failures.append(f"{key} contains vague phrase `{term}`")
    return failures


def _candidate_vague_failures(reqs: list[RequirementCandidate], nfrs: list[NfrCandidate]) -> list[str]:
    failures = []
    for req in reqs:
        if _is_vague(req.statement):
            failures.append(f"{req.req_id} is vague: {req.statement}")
    for nfr in nfrs:
        if _is_vague(nfr.requirement):
            failures.append(f"{nfr.nfr_id} is vague: {nfr.requirement}")
    return failures


def _vague_failures(text: str) -> list[str]:
    lowered = text.lower()
    return [term for term in sorted(VAGUE_TERMS) if term in lowered]


def _is_vague(value: str) -> bool:
    lowered = value.lower()
    if any(term in lowered for term in VAGUE_TERMS):
        return True
    words = re.findall(r"[A-Za-z0-9]+", value)
    return len(words) < 8


def _requirements_graph_node_count(repo_root: Path, cfg: ProjectConfig) -> int:
    path = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root) / "graph.manual.json"
    manual = _manual_graph(path)
    return sum(1 for n in manual.get("nodes", []) if isinstance(n, dict) and str(n.get("id", "")).startswith("requirement:REQ-"))


def _manual_graph(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "nodes": [], "edges": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "nodes": [], "edges": []}
    if not isinstance(raw, dict):
        return {"version": 1, "nodes": [], "edges": []}
    raw.setdefault("version", 1)
    raw.setdefault("nodes", [])
    raw.setdefault("edges", [])
    return raw


def _replace_section(text: str, heading: str, body: str) -> str:
    if not text:
        return f"# Requirements\n\n## {heading}\n{body.rstrip()}\n"
    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    if re.search(pattern, text, flags=re.DOTALL):
        return re.sub(pattern, lambda m: f"{m.group(1)}{body.rstrip()}\n", text, count=1, flags=re.DOTALL)
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


def _extract_section(text: str, heading: str) -> str:
    match = re.search(rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)", text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _meaningful(value: str) -> bool:
    cleaned = value.strip()
    return bool(cleaned) and cleaned not in {"TBD", "- TBD"} and "TBD" not in cleaned


def _brief(value: str, limit: int = 180) -> str:
    cleaned = " ".join(line.strip("- ").strip() for line in value.splitlines() if line.strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def _join(values: list[str]) -> str:
    return ", ".join(values)


def _append_log(root: Path, label: str, line: str) -> None:
    log = root.parent / "log.md"
    if not log.exists():
        log.write_text("---\ntype: log\nstatus: active\n---\n# Log\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{_stamp()}] {label} | requirements\n- {line}\n")


def _default_product_requirements() -> str:
    return """---
type: requirements
stage: requirements
status: draft
owner: product
---
# Product Requirements

## Generated by `echel requirements`
| ID | Title | Type | Priority | Phase | Source IDs | Dependencies | Risks | Acceptance | Validation Method | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_functional_requirements() -> str:
    return """---
type: functional-requirements
stage: requirements
status: draft
owner: product
---
# Functional Requirements

## Generated by `echel requirements`
| ID | Capability | Statement | Priority | Phase | Source IDs | Dependencies | Risks | Acceptance | Test Method | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_non_functional_requirements() -> str:
    return """---
type: non-functional-requirements
stage: requirements
status: draft
owner: product
---
# Non-Functional Requirements

## Generated by `echel requirements`
| ID | Category | Requirement | Target | Priority | Phase | Source IDs | Dependencies | Risks | Acceptance | Verification Method | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_mvp_scope() -> str:
    return """---
type: mvp-scope
stage: requirements
status: draft
owner: product
---
# MVP Scope

## Generated by `echel requirements`
| Requirement ID | Title | Why Included | Source IDs | Dependencies | Acceptance | Exit Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD |
"""


def _default_out_of_scope() -> str:
    return """---
type: out-of-scope
stage: requirements
status: draft
owner: product
---
# Out of Scope

## Generated by `echel requirements`
| ID | Item | Current Phase | Rationale | Source IDs | Related Requirements | Revisit Trigger | Decision Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_acceptance_criteria() -> str:
    return """---
type: acceptance-criteria
stage: requirements
status: draft
owner: product
---
# Acceptance Criteria

## Generated by `echel requirements`
| ID | Requirement IDs | Criterion | Evidence Required | Validation Method | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""
