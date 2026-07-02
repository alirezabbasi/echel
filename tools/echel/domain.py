from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path
from .gates import run_stage_gate
from .graph import write_graph
from .requirements import FUNCTIONAL_FILE, NFR_FILE, PRODUCT_FILE, requirements_root


DOMAIN_DIR = "domain"
DOMAIN_OVERVIEW_FILE = "domain-overview.md"
UBIQUITOUS_LANGUAGE_FILE = "ubiquitous-language.md"
BOUNDED_CONTEXTS_FILE = "bounded-contexts.md"
ENTITIES_FILE = "entities.md"
AGGREGATES_FILE = "aggregates.md"
DOMAIN_EVENTS_FILE = "domain-events.md"
WORKFLOWS_FILE = "workflows.md"
POLICIES_FILE = "policies-and-rules.md"


@dataclass(frozen=True)
class RequirementSource:
    req_id: str
    title: str
    statement: str
    source_ids: str
    phase: str
    kind: str


@dataclass(frozen=True)
class DomainCandidate:
    req_id: str
    requirement_title: str
    concept_id: str
    concept_name: str
    context_id: str
    context_name: str
    aggregate_id: str
    aggregate_name: str
    event_id: str
    event_name: str
    workflow_id: str
    workflow_name: str
    rule_id: str
    rule: str
    phase: str
    source_ids: str
    kind: str


def _stamp() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def domain_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    return wiki / DOMAIN_DIR


def ensure_domain_files(repo_root: Path, cfg: ProjectConfig) -> Path:
    root = domain_root(repo_root, cfg)
    root.mkdir(parents=True, exist_ok=True)
    defaults = {
        DOMAIN_OVERVIEW_FILE: _default_domain_overview(),
        UBIQUITOUS_LANGUAGE_FILE: _default_ubiquitous_language(),
        BOUNDED_CONTEXTS_FILE: _default_bounded_contexts(),
        ENTITIES_FILE: _default_entities(),
        AGGREGATES_FILE: _default_aggregates(),
        DOMAIN_EVENTS_FILE: _default_domain_events(),
        WORKFLOWS_FILE: _default_workflows(),
        POLICIES_FILE: _default_policies(),
    }
    for name, text in defaults.items():
        path = root / name
        if not path.exists():
            path.write_text(text, encoding="utf-8")
    return root


def domain_status(repo_root: Path, cfg: ProjectConfig) -> str:
    root = domain_root(repo_root, cfg)
    if not root.exists():
        return "Domain model not initialized. Run `echel domain` to start."

    files = {
        "domain-overview": root / DOMAIN_OVERVIEW_FILE,
        "ubiquitous-language": root / UBIQUITOUS_LANGUAGE_FILE,
        "bounded-contexts": root / BOUNDED_CONTEXTS_FILE,
        "entities": root / ENTITIES_FILE,
        "aggregates": root / AGGREGATES_FILE,
        "domain-events": root / DOMAIN_EVENTS_FILE,
        "workflows": root / WORKFLOWS_FILE,
        "policies-and-rules": root / POLICIES_FILE,
    }

    lines = ["# Domain Status", ""]
    for name, path in files.items():
        if not path.exists():
            lines.append(f"- {name}: MISSING")
            continue
        text = path.read_text(encoding="utf-8")
        generated = len(re.findall(r"\b(?:DM|BC|AGG|DE|BR)-2\d\d\b|\bWF-DM-2\d\d\b", text))
        lines.append(f"- {name}: {generated} generated ID(s)")
    lines += ["", f"- Graph domain nodes: {_domain_graph_node_count(repo_root, cfg)}"]
    return "\n".join(lines)


def domain_generate(repo_root: Path, cfg: ProjectConfig, force: bool = False) -> list[Path]:
    if not force:
        result = run_stage_gate(repo_root, cfg, "requirements")
        if not result.passed:
            raise ValueError(
                "requirements readiness failed. Domain model cannot be generated until requirements are complete.\n"
                "Use --force to override, or fix requirement gaps first.\n"
                + "\n".join(f"  - {failure}" for failure in result.failures)
            )

    root = ensure_domain_files(repo_root, cfg)
    requirements = _read_requirements(repo_root, cfg)
    if not requirements:
        raise ValueError("no requirements found. Run `echel requirements` or add REQ-###/NFR-### rows first.")

    candidates = _build_candidates(requirements)
    changed = _write_domain_artifacts(root, candidates)
    graph_path = _write_domain_graph(repo_root, cfg, requirements, candidates)
    if graph_path not in changed:
        changed.append(graph_path)
    _append_log(root, "domain", f"Generated or refreshed {len(candidates)} domain concept mappings from requirements.")
    return changed


def _read_requirements(repo_root: Path, cfg: ProjectConfig) -> list[RequirementSource]:
    root = requirements_root(repo_root, cfg)
    rows = []
    for path, kind in [
        (root / PRODUCT_FILE, "product"),
        (root / FUNCTIONAL_FILE, "functional"),
        (root / NFR_FILE, "non-functional"),
    ]:
        for row in _table_rows(path):
            req_id = row.get("ID", "")
            if not re.fullmatch(r"(?:REQ|NFR)-\d{3}", req_id):
                continue
            title = row.get("Title") or row.get("Capability") or row.get("Category") or req_id
            statement = row.get("Statement") or row.get("Requirement") or title
            rows.append(RequirementSource(
                req_id=req_id,
                title=_clean(title),
                statement=_clean(statement),
                source_ids=_clean(row.get("Source IDs", "")),
                phase=_clean(row.get("Phase", "")),
                kind=kind,
            ))
    deduped: dict[str, RequirementSource] = {}
    for row in rows:
        deduped.setdefault(row.req_id, row)
    return [deduped[key] for key in sorted(deduped)]


def _build_candidates(requirements: list[RequirementSource]) -> list[DomainCandidate]:
    candidates: list[DomainCandidate] = []
    for idx, req in enumerate(requirements, start=201):
        base_name = _domain_name(req)
        context = _context_name(req)
        concept = f"{base_name} Concept"
        candidates.append(DomainCandidate(
            req_id=req.req_id,
            requirement_title=req.title,
            concept_id=f"DM-{idx:03d}",
            concept_name=concept,
            context_id=f"BC-{idx:03d}",
            context_name=context,
            aggregate_id=f"AGG-{idx:03d}",
            aggregate_name=f"{base_name} Aggregate",
            event_id=f"DE-{idx:03d}",
            event_name=f"{base_name} Defined",
            workflow_id=f"WF-DM-{idx:03d}",
            workflow_name=f"{base_name} Review",
            rule_id=f"BR-{idx:03d}",
            rule=f"The domain model must represent `{req.req_id}` as business language before architecture begins.",
            phase=req.phase or "Unassigned",
            source_ids=req.req_id,
            kind=req.kind,
        ))
    return candidates


def _write_domain_artifacts(root: Path, candidates: list[DomainCandidate]) -> list[Path]:
    writers = [
        (root / DOMAIN_OVERVIEW_FILE, _generated_domain_overview(candidates)),
        (root / UBIQUITOUS_LANGUAGE_FILE, _generated_language(candidates)),
        (root / BOUNDED_CONTEXTS_FILE, _generated_contexts(candidates)),
        (root / ENTITIES_FILE, _generated_entities(candidates)),
        (root / AGGREGATES_FILE, _generated_aggregates(candidates)),
        (root / DOMAIN_EVENTS_FILE, _generated_events(candidates)),
        (root / WORKFLOWS_FILE, _generated_workflows(candidates)),
        (root / POLICIES_FILE, _generated_rules(candidates)),
    ]
    changed: list[Path] = []
    for path, section in writers:
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        new = _replace_section(old, "Generated by `echel domain`", section)
        if new != old:
            path.write_text(new, encoding="utf-8")
            changed.append(path)
    return changed


def _write_domain_graph(repo_root: Path, cfg: ProjectConfig, requirements: list[RequirementSource], candidates: list[DomainCandidate]) -> Path:
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

    for req in requirements:
        upsert_node({
            "id": f"requirement:{req.req_id}",
            "type": "requirement",
            "title": f"{req.req_id} {req.title}",
            "source": "requirements",
            "summary": req.statement,
        })
        upsert_edge({"from_id": "product:root", "to_id": f"requirement:{req.req_id}", "type": "requires"})

    for item in candidates:
        source = "domain/generated"
        domain_nodes = [
            (f"domain-concept:{item.concept_id}", "domain-concept", f"{item.concept_id} {item.concept_name}", DOMAIN_OVERVIEW_FILE),
            (f"bounded-context:{item.context_id}", "bounded-context", f"{item.context_id} {item.context_name}", BOUNDED_CONTEXTS_FILE),
            (f"domain-aggregate:{item.aggregate_id}", "domain-aggregate", f"{item.aggregate_id} {item.aggregate_name}", AGGREGATES_FILE),
            (f"domain-event:{item.event_id}", "domain-event", f"{item.event_id} {item.event_name}", DOMAIN_EVENTS_FILE),
            (f"domain-workflow:{item.workflow_id}", "domain-workflow", f"{item.workflow_id} {item.workflow_name}", WORKFLOWS_FILE),
            (f"business-rule:{item.rule_id}", "business-rule", f"{item.rule_id} {item.rule}", POLICIES_FILE),
        ]
        for node_id, node_type, title, node_source in domain_nodes:
            upsert_node({"id": node_id, "type": node_type, "title": title, "source": f"domain/{node_source}", "summary": source})
            upsert_edge({"from_id": "product:root", "to_id": node_id, "type": "defines"})
            upsert_edge({"from_id": f"requirement:{item.req_id}", "to_id": node_id, "type": "maps_to"})
        upsert_edge({"from_id": f"bounded-context:{item.context_id}", "to_id": f"domain-concept:{item.concept_id}", "type": "owns"})
        upsert_edge({"from_id": f"domain-aggregate:{item.aggregate_id}", "to_id": f"domain-concept:{item.concept_id}", "type": "groups"})
        upsert_edge({"from_id": f"business-rule:{item.rule_id}", "to_id": f"domain-concept:{item.concept_id}", "type": "constrains"})
        upsert_edge({"from_id": f"domain-workflow:{item.workflow_id}", "to_id": f"domain-event:{item.event_id}", "type": "emits"})

    manual["version"] = 1
    path.write_text(json.dumps(manual, indent=2) + "\n", encoding="utf-8")
    write_graph(repo_root, cfg)
    return path


def _generated_domain_overview(candidates: list[DomainCandidate]) -> str:
    lines = [
        "This section is generated from requirement rows. Manual domain judgment should be preserved outside this generated block or upstream in requirements.",
        "",
        "| Requirement ID | Domain Concept | Bounded Context | Aggregate | Event | Rule | Coverage Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.req_id} | {item.concept_id} {item.concept_name} | {item.context_id} {item.context_name} | {item.aggregate_id} {item.aggregate_name} | {item.event_id} {item.event_name} | {item.rule_id} | Covered |")
    return "\n".join(lines)


def _generated_language(candidates: list[DomainCandidate]) -> str:
    lines = [
        "| ID | Term | Definition | Type | Source IDs | Related Terms | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.concept_id} | {item.concept_name} | Domain concept derived from `{item.req_id}`: {_brief(item.requirement_title)}. | Concept | {item.source_ids} | {item.context_id}, {item.rule_id} | Generated |")
    return "\n".join(lines)


def _generated_contexts(candidates: list[DomainCandidate]) -> str:
    lines = [
        "| ID | Context | Responsibility | Owned Concepts | Source IDs | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.context_id} | {item.context_name} | Owns the business language and rules needed to satisfy `{item.req_id}`. | {item.concept_id} | {item.source_ids} | Generated |")
    return "\n".join(lines)


def _generated_entities(candidates: list[DomainCandidate]) -> str:
    lines = [
        "| ID | Entity | Identity | Description | Source IDs | Owner Context | Key Relationships | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.concept_id} | {item.concept_name} | {item.req_id} | Business concept required by `{item.req_id}`. | {item.source_ids} | {item.context_id} | Governed by {item.rule_id}; grouped by {item.aggregate_id} | Generated |")
    return "\n".join(lines)


def _generated_aggregates(candidates: list[DomainCandidate]) -> str:
    lines = [
        "| ID | Aggregate | Root Concept | Included Concepts | Consistency Rule | Source IDs | Owner Context | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.aggregate_id} | {item.aggregate_name} | {item.concept_id} {item.concept_name} | {item.concept_id}, {item.rule_id} | Keep `{item.req_id}` mapped to stable domain language before architecture. | {item.source_ids} | {item.context_id} | Generated |")
    return "\n".join(lines)


def _generated_events(candidates: list[DomainCandidate]) -> str:
    lines = [
        "| ID | Event | Meaning | Trigger | Source IDs | Publisher Context | Consumer Contexts | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.event_id} | {item.event_name} | Domain language for `{item.req_id}` has been defined. | `echel domain` maps requirement to domain model. | {item.source_ids} | {item.context_id} | Architecture, execution planning | Generated |")
    return "\n".join(lines)


def _generated_workflows(candidates: list[DomainCandidate]) -> str:
    lines = [
        "| ID | Workflow | Objective | Source IDs | Participating Contexts | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.workflow_id} | {item.workflow_name} | Review domain coverage for `{item.req_id}` before architecture. | {item.source_ids} | {item.context_id} | Generated |")
    return "\n".join(lines)


def _generated_rules(candidates: list[DomainCandidate]) -> str:
    lines = [
        "| ID | Rule | Source IDs | Applies To | Enforcement Moment | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.rule_id} | {item.rule} | {item.source_ids} | {item.concept_id}, {item.context_id}, {item.aggregate_id} | Domain generation and future domain gate | Generated |")
    return "\n".join(lines)


def _table_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if not line.startswith("|") or not line.endswith("|"):
            idx += 1
            continue
        headers = _split_table_line(line)
        if idx + 1 >= len(lines) or not _is_separator_row(lines[idx + 1]):
            idx += 1
            continue
        idx += 2
        while idx < len(lines):
            row_line = lines[idx].strip()
            if not row_line.startswith("|") or not row_line.endswith("|"):
                break
            values = _split_table_line(row_line)
            rows.append({headers[pos]: values[pos] if pos < len(values) else "" for pos in range(len(headers))})
            idx += 1
        continue
    return rows


def _split_table_line(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def _is_separator_row(line: str) -> bool:
    cells = _split_table_line(line.strip())
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def _replace_section(text: str, heading: str, body: str) -> str:
    if not text:
        return f"# Domain\n\n## {heading}\n{body.rstrip()}\n"
    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    if re.search(pattern, text, flags=re.DOTALL):
        return re.sub(pattern, lambda m: f"{m.group(1)}{body.rstrip()}\n", text, count=1, flags=re.DOTALL)
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


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


def _domain_graph_node_count(repo_root: Path, cfg: ProjectConfig) -> int:
    path = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root) / "graph.manual.json"
    manual = _manual_graph(path)
    return sum(
        1 for node in manual.get("nodes", [])
        if isinstance(node, dict) and str(node.get("type", "")).startswith("domain")
    )


def _domain_name(req: RequirementSource) -> str:
    title = re.sub(r"\b(Echel|must|should|the|a|an|to|and|or|for|with)\b", " ", req.title, flags=re.IGNORECASE)
    words = [w.capitalize() for w in re.findall(r"[A-Za-z0-9]+", title)[:4]]
    return " ".join(words) or req.req_id


def _context_name(req: RequirementSource) -> str:
    if req.req_id.startswith("NFR-"):
        return f"{_domain_name(req)} Quality Context"
    return f"{_domain_name(req)} Context"


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _brief(value: str, limit: int = 140) -> str:
    cleaned = _clean(value)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def _append_log(root: Path, label: str, line: str) -> None:
    log = root.parent / "log.md"
    if not log.exists():
        log.write_text("---\ntype: log\nstatus: active\n---\n# Log\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{_stamp()}] {label} | domain\n- {line}\n")


def _default_domain_overview() -> str:
    return """---
type: domain-overview
stage: domain
status: draft
owner: product
---
# Domain Overview

## Generated by `echel domain`
| Requirement ID | Domain Concept | Bounded Context | Aggregate | Event | Rule | Coverage Status |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_ubiquitous_language() -> str:
    return """---
type: ubiquitous-language
stage: domain
status: draft
owner: product
---
# Ubiquitous Language

## Generated by `echel domain`
| ID | Term | Definition | Type | Source IDs | Related Terms | Status |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_bounded_contexts() -> str:
    return """---
type: bounded-contexts
stage: domain
status: draft
owner: product
---
# Bounded Contexts

## Generated by `echel domain`
| ID | Context | Responsibility | Owned Concepts | Source IDs | Status |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_entities() -> str:
    return """---
type: domain-entities
stage: domain
status: draft
owner: product
---
# Entities

## Generated by `echel domain`
| ID | Entity | Identity | Description | Source IDs | Owner Context | Key Relationships | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_aggregates() -> str:
    return """---
type: domain-aggregates
stage: domain
status: draft
owner: product
---
# Aggregates

## Generated by `echel domain`
| ID | Aggregate | Root Concept | Included Concepts | Consistency Rule | Source IDs | Owner Context | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_domain_events() -> str:
    return """---
type: domain-events
stage: domain
status: draft
owner: product
---
# Domain Events

## Generated by `echel domain`
| ID | Event | Meaning | Trigger | Source IDs | Publisher Context | Consumer Contexts | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_workflows() -> str:
    return """---
type: domain-workflows
stage: domain
status: draft
owner: product
---
# Domain Workflows

## Generated by `echel domain`
| ID | Workflow | Objective | Source IDs | Participating Contexts | Status |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_policies() -> str:
    return """---
type: domain-policies-and-rules
stage: domain
status: draft
owner: product
---
# Policies And Rules

## Generated by `echel domain`
| ID | Rule | Source IDs | Applies To | Enforcement Moment | Status |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | Draft |
"""
