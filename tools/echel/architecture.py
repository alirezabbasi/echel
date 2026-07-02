from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from .config import ProjectConfig, resolve_symbolic_path
from .gates import run_stage_gate
from .graph import write_graph


ARCHITECTURE_DIR = "architecture"
OVERVIEW_FILE = "overview.md"
CONTEXT_MAP_FILE = "context-map.md"
COMPONENT_FILE = "component-architecture.md"
DATA_FILE = "data-architecture.md"
API_FILE = "api-architecture.md"
EVENT_FILE = "event-architecture.md"
WORKFLOW_FILE = "workflow-architecture.md"
SECURITY_FILE = "security-architecture.md"
OBSERVABILITY_FILE = "observability-architecture.md"


@dataclass(frozen=True)
class ArchitectureCandidate:
    arch_id: str
    req_id: str
    architecture_choice: str
    responsibility: str
    domain_concept: str
    bounded_context: str
    aggregate: str
    event: str
    rule: str
    rationale: str
    adr_suggestion: str
    source_file: str


def _stamp() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def architecture_root(repo_root: Path, cfg: ProjectConfig) -> Path:
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    return wiki / ARCHITECTURE_DIR


def ensure_architecture_files(repo_root: Path, cfg: ProjectConfig) -> Path:
    root = architecture_root(repo_root, cfg)
    root.mkdir(parents=True, exist_ok=True)
    defaults = {
        OVERVIEW_FILE: _default_overview(),
        CONTEXT_MAP_FILE: _default_context_map(),
        COMPONENT_FILE: _default_component_architecture(),
        DATA_FILE: _default_data_architecture(),
        API_FILE: _default_api_architecture(),
        EVENT_FILE: _default_event_architecture(),
        WORKFLOW_FILE: _default_workflow_architecture(),
        SECURITY_FILE: _default_security_architecture(),
        OBSERVABILITY_FILE: _default_observability_architecture(),
    }
    for name, text in defaults.items():
        path = root / name
        if not path.exists():
            path.write_text(text, encoding="utf-8")
    return root


def architecture_status(repo_root: Path, cfg: ProjectConfig) -> str:
    root = architecture_root(repo_root, cfg)
    if not root.exists():
        return "Architecture model not initialized. Run `echel architecture` to start."

    files = {
        "overview": root / OVERVIEW_FILE,
        "context-map": root / CONTEXT_MAP_FILE,
        "component-architecture": root / COMPONENT_FILE,
        "data-architecture": root / DATA_FILE,
        "api-architecture": root / API_FILE,
        "event-architecture": root / EVENT_FILE,
        "workflow-architecture": root / WORKFLOW_FILE,
        "security-architecture": root / SECURITY_FILE,
        "observability-architecture": root / OBSERVABILITY_FILE,
    }

    lines = ["# Architecture Status", ""]
    for name, path in files.items():
        if not path.exists():
            lines.append(f"- {name}: MISSING")
            continue
        text = path.read_text(encoding="utf-8")
        generated = len(re.findall(r"\bARCH-9\d\d\b", text))
        lines.append(f"- {name}: {generated} generated architecture ID(s)")
    lines += ["", f"- Graph architecture nodes: {_architecture_graph_node_count(repo_root, cfg)}"]
    return "\n".join(lines)


def architecture_generate(repo_root: Path, cfg: ProjectConfig, force: bool = False) -> list[Path]:
    if not force:
        result = run_stage_gate(repo_root, cfg, "domain")
        if not result.passed:
            raise ValueError(
                "domain readiness failed. Architecture cannot be generated until domain language is complete.\n"
                "Use --force to override, or fix domain gaps first.\n"
                + "\n".join(f"  - {failure}" for failure in result.failures)
            )

    root = ensure_architecture_files(repo_root, cfg)
    domain_rows = _read_domain_coverage(repo_root, cfg)
    if not domain_rows:
        raise ValueError("no domain coverage rows found. Run `echel domain` or add requirement-to-domain coverage first.")

    candidates = _build_candidates(domain_rows)
    changed = _write_architecture_artifacts(root, candidates)
    summary = _write_legacy_architecture_summary(repo_root, cfg)
    if summary not in changed:
        changed.append(summary)
    graph_path = _write_architecture_graph(repo_root, cfg, candidates)
    if graph_path not in changed:
        changed.append(graph_path)
    _append_log(root, "architecture", f"Generated or refreshed {len(candidates)} architecture mappings from domain coverage.")
    return changed


def _read_domain_coverage(repo_root: Path, cfg: ProjectConfig) -> list[dict[str, str]]:
    root = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root) / "domain"
    path = root / "domain-overview.md"
    rows: list[dict[str, str]] = []
    for row in _table_rows(path):
        rid = row.get("Requirement ID", "")
        if not re.fullmatch(r"(?:REQ|NFR)-\d{3}", rid):
            continue
        if row.get("Coverage Status", "").lower() != "covered":
            continue
        rows.append(row)
    deduped: dict[str, dict[str, str]] = {}
    for row in rows:
        deduped[row["Requirement ID"]] = row
    return [deduped[key] for key in sorted(deduped)]


def _build_candidates(rows: list[dict[str, str]]) -> list[ArchitectureCandidate]:
    candidates: list[ArchitectureCandidate] = []
    for idx, row in enumerate(rows, start=901):
        req_id = row["Requirement ID"]
        concept = _first_id(row.get("Domain Concept", ""), r"DM-\d{3}") or "DM-UNKNOWN"
        context = _first_id(row.get("Bounded Context", ""), r"BC-\d{3}") or "BC-UNKNOWN"
        aggregate = _first_id(row.get("Aggregate", ""), r"AGG-\d{3}") or "AGG-UNKNOWN"
        event = _first_id(row.get("Event", ""), r"DE-\d{3}") or "DE-UNKNOWN"
        rule = _first_id(row.get("Rule", ""), r"BR-\d{3}") or "BR-UNKNOWN"
        quality = req_id.startswith("NFR-")
        area = "quality architecture" if quality else "product architecture"
        arch_id = f"ARCH-{idx:03d}"
        choice = f"Preserve {req_id} through {context} {area}"
        responsibility = f"Keep `{req_id}` traceable from requirement and domain language into architecture, roadmap, and future task packets."
        rationale = f"`{req_id}` is already covered by {concept}, {context}, {aggregate}, {event}, and {rule}; architecture must preserve that boundary instead of inventing a new one."
        adr = "ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model."
        candidates.append(ArchitectureCandidate(
            arch_id=arch_id,
            req_id=req_id,
            architecture_choice=choice,
            responsibility=responsibility,
            domain_concept=concept,
            bounded_context=context,
            aggregate=aggregate,
            event=event,
            rule=rule,
            rationale=rationale,
            adr_suggestion=adr,
            source_file=OVERVIEW_FILE,
        ))
    return candidates


def _write_architecture_artifacts(root: Path, candidates: list[ArchitectureCandidate]) -> list[Path]:
    writers = [
        (root / OVERVIEW_FILE, _generated_overview(candidates)),
        (root / CONTEXT_MAP_FILE, _generated_context_map(candidates)),
        (root / COMPONENT_FILE, _generated_components(candidates)),
        (root / DATA_FILE, _generated_data(candidates)),
        (root / API_FILE, _generated_api(candidates)),
        (root / EVENT_FILE, _generated_events(candidates)),
        (root / WORKFLOW_FILE, _generated_workflows(candidates)),
        (root / SECURITY_FILE, _generated_security(candidates)),
        (root / OBSERVABILITY_FILE, _generated_observability(candidates)),
    ]
    changed: list[Path] = []
    for path, section in writers:
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        new = _replace_section(old, "Generated by `echel architecture`", section)
        if new != old:
            path.write_text(new, encoding="utf-8")
            changed.append(path)
    return changed


def _write_legacy_architecture_summary(repo_root: Path, cfg: ProjectConfig) -> Path:
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    path = wiki / "architecture.md"
    text = """---
type: product-architecture
status: draft
---
# Product Architecture

## System Shape
Local-first AI-native software engineering operating system with product-owned Markdown memory, deterministic lifecycle commands, product graph, stage gates, work packets, reviews, proof packs, local cockpit, and generated architecture mappings from gated domain language.

## Key Components
- Product wiki
- Product graph
- Agent command surface
- Generated reports
- Lifecycle gate engine
- Work packet generator
- Review and evidence layer
- Local cockpit
- Architecture artifact surface

## Expanded Architecture Model
- [[architecture/overview]]
- [[architecture/context-map]]
- [[architecture/component-architecture]]
- [[architecture/data-architecture]]
- [[architecture/api-architecture]]
- [[architecture/event-architecture]]
- [[architecture/workflow-architecture]]
- [[architecture/security-architecture]]
- [[architecture/observability-architecture]]

## Open Architecture Questions
- How should generated architecture mappings be refined into concrete repository modules in TASK-0024?
- What exact checks belong in the future architecture readiness gate?
- Which architecture choices need new ADRs after architecture generation?
"""
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old != text:
        path.write_text(text, encoding="utf-8")
    return path


def _write_architecture_graph(repo_root: Path, cfg: ProjectConfig, candidates: list[ArchitectureCandidate]) -> Path:
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

    def ensure_node(node: dict) -> None:
        if not any(isinstance(n, dict) and n.get("id") == node["id"] for n in nodes):
            nodes.append(node)

    for item in candidates:
        arch_node = f"architecture:{item.arch_id}"
        ensure_node({"id": f"requirement:{item.req_id}", "type": "requirement", "title": item.req_id, "source": "architecture/generated", "summary": "Requirement referenced by architecture generation."})
        for node_id, node_type, title in [
            (f"domain-concept:{item.domain_concept}", "domain-concept", item.domain_concept),
            (f"bounded-context:{item.bounded_context}", "bounded-context", item.bounded_context),
            (f"domain-aggregate:{item.aggregate}", "domain-aggregate", item.aggregate),
            (f"domain-event:{item.event}", "domain-event", item.event),
            (f"business-rule:{item.rule}", "business-rule", item.rule),
        ]:
            ensure_node({"id": node_id, "type": node_type, "title": title, "source": "architecture/generated", "summary": "Domain item referenced by architecture generation."})
        upsert_node({
            "id": arch_node,
            "type": "architecture",
            "title": f"{item.arch_id} {item.architecture_choice}",
            "source": f"architecture/{item.source_file}",
            "summary": item.rationale,
        })
        upsert_edge({"from_id": "product:root", "to_id": arch_node, "type": "defines"})
        for node_id, edge_type in [
            (f"requirement:{item.req_id}", "maps_to"),
            (f"domain-concept:{item.domain_concept}", "preserved_by"),
            (f"bounded-context:{item.bounded_context}", "preserved_by"),
            (f"domain-aggregate:{item.aggregate}", "preserved_by"),
            (f"domain-event:{item.event}", "informs"),
            (f"business-rule:{item.rule}", "constrains"),
        ]:
            upsert_edge({"from_id": node_id, "to_id": arch_node, "type": edge_type})

    manual["version"] = 1
    path.write_text(json.dumps(manual, indent=2) + "\n", encoding="utf-8")
    write_graph(repo_root, cfg)
    return path


def _generated_overview(candidates: list[ArchitectureCandidate]) -> str:
    lines = [
        "This section is generated from gated domain coverage. Manual architecture judgment should be preserved outside this generated block or recorded as ADRs.",
        "",
        "| ID | Choice | Rationale | Source IDs | Domain Boundaries Preserved | ADR Suggestion | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.arch_id} | {item.architecture_choice} | {item.rationale} | {item.req_id} | {item.domain_concept}, {item.bounded_context}, {item.aggregate}, {item.event}, {item.rule} | {item.adr_suggestion} | Generated |")
    return "\n".join(lines)


def _generated_context_map(candidates: list[ArchitectureCandidate]) -> str:
    lines = [
        "| Domain Context | Architecture Context | Responsibility | Preserved Boundary | Source IDs | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.bounded_context} | {item.arch_id} Architecture Context | {item.responsibility} | Preserve {item.domain_concept}, {item.aggregate}, {item.event}, and {item.rule}. | {item.req_id} | Generated |")
    return "\n".join(lines)


def _generated_components(candidates: list[ArchitectureCandidate]) -> str:
    lines = [
        "| ID | Component | Responsibility | Source IDs | Domain Contexts | Rationale | ADR Coverage | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.arch_id} | {item.architecture_choice} Component | {item.responsibility} | {item.req_id} | {item.bounded_context} | {item.rationale} | ADR required only if this becomes a new independently owned component. | Generated |")
    return "\n".join(lines)


def _generated_data(candidates: list[ArchitectureCandidate]) -> str:
    lines = [
        "| ID | Store | Owned Data | Format | Source IDs | Rationale | Backup Or Recovery | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.arch_id} | {item.req_id} Architecture Trace Store | Requirement, domain, and architecture mapping for {item.req_id}. | Markdown and graph JSON | {item.req_id}, {item.domain_concept}, {item.bounded_context} | Architecture traceability must stay readable and graphable. | Git history and graph rebuild | Generated |")
    return "\n".join(lines)


def _generated_api(candidates: list[ArchitectureCandidate]) -> str:
    lines = [
        "| ID | Surface | Consumer | Contract | Source IDs | Rationale | ADR Coverage | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.arch_id} | {item.req_id} Architecture Handoff | Roadmap, repository factory, task generation | Architecture rows must expose {item.req_id}, {item.bounded_context}, and {item.domain_concept}. | {item.req_id} | Downstream commands need explicit traceable architecture input. | ADR required if exposed as public or remote API. | Generated |")
    return "\n".join(lines)


def _generated_events(candidates: list[ArchitectureCandidate]) -> str:
    lines = [
        "| ID | Event | Meaning | Producer | Consumer | Source IDs | Rationale | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.arch_id} | {item.req_id} Architecture Mapped | Architecture preserves domain coverage for {item.req_id}. | `echel architecture` | Roadmap and architecture gate | {item.req_id}, {item.event} | Domain events should inform architecture without forcing message infrastructure. | Generated |")
    return "\n".join(lines)


def _generated_workflows(candidates: list[ArchitectureCandidate]) -> str:
    lines = [
        "| ID | Workflow | Entry Condition | Steps | Exit Condition | Source IDs | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.arch_id} | {item.req_id} Architecture Handoff | Domain gate passes for {item.req_id}. | Map requirement, domain concept, context, rule, and event into architecture. | Architecture row can feed roadmap and future task generation. | {item.req_id}, {item.bounded_context} | Generated |")
    return "\n".join(lines)


def _generated_security(candidates: list[ArchitectureCandidate]) -> str:
    lines = [
        "| ID | Boundary | Assets Protected | Threats | Controls | Source IDs | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.arch_id} | {item.req_id} Architecture Boundary | Source IDs, domain IDs, and architecture mapping for {item.req_id}. | Silent intent loss or boundary drift. | Stage gates, ADR suggestions, generated graph edges. | {item.req_id}, {item.rule} | Generated |")
    return "\n".join(lines)


def _generated_observability(candidates: list[ArchitectureCandidate]) -> str:
    lines = [
        "| ID | Surface | Signal | Producer | Consumer | Source IDs | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(f"| {item.arch_id} | {item.req_id} Architecture Trace | Requirement-to-domain-to-architecture mapping is present. | `echel architecture` | Architecture gate, roadmap, product graph | {item.req_id}, {item.bounded_context} | Generated |")
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
        return f"# Architecture\n\n## {heading}\n{body.rstrip()}\n"
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


def _architecture_graph_node_count(repo_root: Path, cfg: ProjectConfig) -> int:
    path = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root) / "graph.manual.json"
    manual = _manual_graph(path)
    return sum(1 for node in manual.get("nodes", []) if isinstance(node, dict) and str(node.get("id", "")).startswith("architecture:ARCH-"))


def _first_id(value: str, pattern: str) -> str | None:
    match = re.search(pattern, value)
    return match.group(0) if match else None


def _append_log(root: Path, label: str, line: str) -> None:
    log = root.parent / "log.md"
    if not log.exists():
        log.write_text("---\ntype: log\nstatus: active\n---\n# Log\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{_stamp()}] {label} | architecture\n- {line}\n")


def _default_overview() -> str:
    return """---
type: architecture-overview
stage: architecture
status: draft
owner: architecture
---
# Architecture Overview

## Generated by `echel architecture`
| ID | Choice | Rationale | Source IDs | Domain Boundaries Preserved | ADR Suggestion | Status |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_context_map() -> str:
    return """---
type: architecture-context-map
stage: architecture
status: draft
owner: architecture
---
# Context Map

## Generated by `echel architecture`
| Domain Context | Architecture Context | Responsibility | Preserved Boundary | Source IDs | Status |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_component_architecture() -> str:
    return """---
type: component-architecture
stage: architecture
status: draft
owner: architecture
---
# Component Architecture

## Generated by `echel architecture`
| ID | Component | Responsibility | Source IDs | Domain Contexts | Rationale | ADR Coverage | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_data_architecture() -> str:
    return """---
type: data-architecture
stage: architecture
status: draft
owner: architecture
---
# Data Architecture

## Generated by `echel architecture`
| ID | Store | Owned Data | Format | Source IDs | Rationale | Backup Or Recovery | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_api_architecture() -> str:
    return """---
type: api-architecture
stage: architecture
status: draft
owner: architecture
---
# API Architecture

## Generated by `echel architecture`
| ID | Surface | Consumer | Contract | Source IDs | Rationale | ADR Coverage | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_event_architecture() -> str:
    return """---
type: event-architecture
stage: architecture
status: draft
owner: architecture
---
# Event Architecture

## Generated by `echel architecture`
| ID | Event | Meaning | Producer | Consumer | Source IDs | Rationale | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_workflow_architecture() -> str:
    return """---
type: workflow-architecture
stage: architecture
status: draft
owner: architecture
---
# Workflow Architecture

## Generated by `echel architecture`
| ID | Workflow | Entry Condition | Steps | Exit Condition | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_security_architecture() -> str:
    return """---
type: security-architecture
stage: architecture
status: draft
owner: architecture
---
# Security Architecture

## Generated by `echel architecture`
| ID | Boundary | Assets Protected | Threats | Controls | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""


def _default_observability_architecture() -> str:
    return """---
type: observability-architecture
stage: architecture
status: draft
owner: architecture
---
# Observability Architecture

## Generated by `echel architecture`
| ID | Surface | Signal | Producer | Consumer | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | Draft |
"""
