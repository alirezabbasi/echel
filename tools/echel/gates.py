from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Callable

from .coherence import detect_drift
from .config import ProjectConfig, resolve_symbolic_path
from .discovery import DISCOVERY_FIELDS, discovery_root, _section_body, _is_tbd
from .evidence import ensure_registry, validate_links, validate_registry
from .primitives import validate_decisions, validate_gate_ids, validate_tasks
from .requirements import AC_FILE, FUNCTIONAL_FILE, MVP_FILE, NFR_FILE, OOS_FILE, PRODUCT_FILE, requirements_root
from .validation import collect_validation_issues


ARCHITECTURE_FILES = [
    "overview.md",
    "context-map.md",
    "component-architecture.md",
    "data-architecture.md",
    "api-architecture.md",
    "event-architecture.md",
    "workflow-architecture.md",
    "security-architecture.md",
    "observability-architecture.md",
]

DEPLOYMENT_FILES = [
    "deployment-architecture.md",
    "environments.md",
    "release-process.md",
    "rollback-plan.md",
    "secrets-management.md",
    "production-checklist.md",
]

ARCHITECTURE_COMPLEXITY_TERMS = [
    "aws",
    "azure",
    "broker",
    "distributed",
    "external database",
    "gcp",
    "hosted",
    "kafka",
    "kubernetes",
    "message queue",
    "microservice",
    "multi-region",
    "remote orchestration",
    "terraform",
]

DOMAIN_FILES = [
    "domain-overview.md",
    "ubiquitous-language.md",
    "bounded-contexts.md",
    "entities.md",
    "aggregates.md",
    "domain-events.md",
    "workflows.md",
    "policies-and-rules.md",
]

DOMAIN_ID_PATTERNS = {
    "DM": r"DM-\d{3}",
    "BC": r"BC-\d{3}",
    "AGG": r"AGG-\d{3}",
    "DE": r"DE-\d{3}",
    "WF": r"WF-DM-\d{3}",
    "BR": r"BR-\d{3}",
}

TECH_LEAKAGE_TERMS = [
    "api",
    "aws",
    "azure",
    "backend",
    "container",
    "database",
    "django",
    "docker",
    "endpoint",
    "fastapi",
    "frontend",
    "gcp",
    "graphql",
    "grpc",
    "http",
    "json",
    "kafka",
    "kubernetes",
    "lambda",
    "microservice",
    "postgres",
    "postgresql",
    "python",
    "react",
    "redis",
    "rest",
    "s3",
    "server",
    "sqlite",
    "terraform",
    "yaml",
]


@dataclass
class GateResult:
    gate_id: str
    passed: bool
    failures: list[str]


GateFn = Callable[[Path, ProjectConfig], list[str]]


def _check_schema(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    failures: list[str] = []
    _ = cfg
    if not (repo_root / "project.echel").exists():
        failures.append("missing project.echel")
    return failures


def _check_coherence(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    _ = cfg
    return [f"{i.category}: {i.message} [{i.source}]" for i in detect_drift(repo_root)]


def _check_evidence_links(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    wiki_root = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    reg_path = repo_root / cfg.evidence_registry
    reg = ensure_registry(reg_path)
    failures = [f"{i.severity}: {i.message}" for i in validate_registry(reg, str(reg_path))]
    link_files = sorted((wiki_root / "work").glob("TASK-*.md")) + sorted((wiki_root / "decisions").glob("ADR-*.md"))
    failures.extend(f"{i.severity}: {i.message} [{i.source}]" for i in validate_links(link_files, reg))
    return failures


def _check_primitives(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    wiki_root = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    fails = []
    t = validate_tasks(sorted((wiki_root / "work").glob("TASK-*.md")))
    d = validate_decisions(sorted((wiki_root / "decisions").glob("ADR-*.md")))
    fails.extend(f"{i.severity}: {i.message} [{i.source}]" for i in t)
    fails.extend(f"{i.severity}: {i.message} [{i.source}]" for i in d)
    return fails


def _check_discovery(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    root = discovery_root(repo_root, cfg)
    pds = root / "product-discovery-spec.md"
    if not pds.exists():
        return ["discovery not initialized: run `echel discover` to start"]
    text = pds.read_text(encoding="utf-8")
    failures: list[str] = []
    required_fields = [
        ("problem", "02 Problem", "Problem must be clearly defined"),
        ("buyers", "04 Buyers", "Buyer must be identified"),
        ("users", "03 Users", "User must be identified"),
        ("operators", "05 Operators", "Operator must be identified"),
        ("workflow", "06 Current Workflow", "Current workflow must be documented"),
        ("business-model", "10 Business Model", "Business value must be measurable"),
        ("success", "11 Success Criteria", "Success criteria must be measurable"),
        ("non-goals", "13 Non-Goals", "Non-goals must be documented"),
        ("constraints", "14 Constraints", "Constraints must be documented"),
        ("risks", "17 Risks", "Risks must be listed"),
        ("assumptions", "15 Assumptions", "Assumptions must be listed"),
        ("open-questions", "22 Open Questions", "Open questions must be listed"),
        ("scope", "12 Scope", "MVP scope must be defined"),
    ]
    for key, heading, message in required_fields:
        body = _section_body(text, heading)
        if _section_incomplete(body):
            failures.append(f"discovery field `{key}` is incomplete: {message}")
    research = root / "research-plan.md"
    if not research.exists():
        failures.append("research plan missing: create wiki/discovery/research-plan.md")
    elif "TBD" in research.read_text(encoding="utf-8"):
        failures.append("research plan is incomplete: add at least one meaningful research item")
    return failures


def _section_incomplete(body: str) -> bool:
    if not body.strip():
        return True
    cleaned = body.strip()
    if cleaned == "TBD" or cleaned == "- TBD":
        return True
    if "TBD" in cleaned:
        return True
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    content_lines = []
    for line in lines:
        if line.startswith("**") or line.startswith("|") or line.startswith("#") or line.startswith("---"):
            continue
        if line in {"TBD", "- TBD", "TBD", "fact or observation", "decision or hypothesis", "decision", "assumption or hypothesis", "hypothesis", "assumption", "question"}:
            continue
        if line.startswith("- ID:") or line.startswith("- Type:") or line.startswith("- Confidence:"):
            continue
        if line.startswith("| `") and "TBD" in line:
            continue
        content_lines.append(line)
    return len(content_lines) == 0


def _check_requirements(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    root = requirements_root(repo_root, cfg)
    if not root.exists():
        return ["requirements not initialized: run `echel requirements` to start"]

    failures: list[str] = []
    required_files = [PRODUCT_FILE, FUNCTIONAL_FILE, NFR_FILE, MVP_FILE, OOS_FILE, AC_FILE]
    missing = [name for name in required_files if not (root / name).exists()]
    if missing:
        return [f"requirements artifact missing: wiki/requirements/{name}" for name in missing]

    product_rows = _requirement_rows(root / PRODUCT_FILE)
    functional_rows = _requirement_rows(root / FUNCTIONAL_FILE)
    nfr_rows = _requirement_rows(root / NFR_FILE)
    mvp_rows = _table_rows(root / MVP_FILE)
    oos_rows = _table_rows(root / OOS_FILE)
    ac_rows = _table_rows(root / AC_FILE)

    req_rows = _dedupe_rows(product_rows + functional_rows, "ID")
    all_requirement_rows = req_rows + _dedupe_rows(nfr_rows, "ID")
    mvp_ids = _mvp_requirement_ids(req_rows, nfr_rows, mvp_rows)
    ac_ids = _valid_ids(ac_rows, "ID", r"AC-\d{3}")
    graph_ids = _requirement_graph_ids(repo_root, cfg)

    if not mvp_ids:
        failures.append("MVP scope is empty: add MVP REQ-### or NFR-### rows to requirements artifacts")

    for row in all_requirement_rows:
        rid = row.get("ID", "")
        if rid not in mvp_ids:
            continue
        if _blank_or_tbd(row.get("Acceptance", "")):
            failures.append(f"{rid} is not testable: acceptance criteria link is missing")
        elif _linked_ids(row.get("Acceptance", ""), r"AC-\d{3}") - ac_ids:
            missing_ac = sorted(_linked_ids(row.get("Acceptance", ""), r"AC-\d{3}") - ac_ids)
            failures.append(f"{rid} references missing acceptance criteria: {', '.join(missing_ac)}")
        if _blank_or_tbd(_validation_method(row)):
            failures.append(f"{rid} is not testable: validation or verification method is missing")
        if _blank_or_tbd(row.get("Dependencies", "")):
            failures.append(f"{rid} has unknown dependencies: use `None` only when there is no dependency")
        if _blank_or_tbd(row.get("Risks", "")):
            failures.append(f"{rid} has no linked risk or risk statement")
        if _blank_or_tbd(row.get("Source IDs", "")):
            failures.append(f"{rid} has no upstream source IDs")

    for rid in sorted(_generated_requirement_ids(all_requirement_rows)):
        if rid not in graph_ids:
            failures.append(f"{rid} is missing from the product graph: rerun `echel requirements` after source updates")

    mvp_nfrs = [row for row in nfr_rows if row.get("ID", "") in mvp_ids or row.get("Phase", "").upper() == "MVP"]
    if not mvp_nfrs:
        failures.append("non-functional requirements are missing for MVP scope")
    for row in mvp_nfrs:
        rid = row.get("ID", "")
        if _blank_or_tbd(row.get("Target", "")):
            failures.append(f"{rid} has no measurable non-functional target")
        if _blank_or_tbd(_validation_method(row)):
            failures.append(f"{rid} has no verification method")

    explicit_oos = [row for row in oos_rows if _valid_id(row.get("ID", ""), r"OOS-\d{3}")]
    if not explicit_oos:
        failures.append("out-of-scope is not explicit: add at least one OOS-### record")
    for row in explicit_oos:
        oid = row.get("ID", "")
        for field in ["Item", "Rationale", "Related Requirements", "Revisit Trigger"]:
            if _blank_or_tbd(row.get(field, "")):
                failures.append(f"{oid} is incomplete: `{field}` must be populated")

    if not ac_ids:
        failures.append("acceptance criteria are missing: add AC-### rows")
    for row in ac_rows:
        aid = row.get("ID", "")
        if not _valid_id(aid, r"AC-\d{3}"):
            continue
        for field in ["Requirement IDs", "Criterion", "Evidence Required", "Validation Method"]:
            if _blank_or_tbd(row.get(field, "")):
                failures.append(f"{aid} is incomplete: `{field}` must be populated")

    return failures


def _requirement_rows(path: Path) -> list[dict[str, str]]:
    return [
        row for row in _table_rows(path)
        if _valid_id(row.get("ID", ""), r"(?:REQ|NFR)-\d{3}")
    ]


def _table_rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []
    lines = text.splitlines()
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
            row = {headers[pos]: values[pos] if pos < len(values) else "" for pos in range(len(headers))}
            rows.append(row)
            idx += 1
        continue
    return rows


def _split_table_line(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def _is_separator_row(line: str) -> bool:
    cells = _split_table_line(line.strip())
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def _dedupe_rows(rows: list[dict[str, str]], key: str) -> list[dict[str, str]]:
    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for row in rows:
        value = row.get(key, "")
        if value in seen:
            continue
        seen.add(value)
        deduped.append(row)
    return deduped


def _mvp_requirement_ids(req_rows: list[dict[str, str]], nfr_rows: list[dict[str, str]], mvp_rows: list[dict[str, str]]) -> set[str]:
    ids = {row.get("ID", "") for row in req_rows + nfr_rows if row.get("Phase", "").upper() == "MVP"}
    ids.update(row.get("Requirement ID", "") for row in mvp_rows)
    return {rid for rid in ids if _valid_id(rid, r"(?:REQ|NFR)-\d{3}")}


def _valid_ids(rows: list[dict[str, str]], key: str, pattern: str) -> set[str]:
    return {row.get(key, "") for row in rows if _valid_id(row.get(key, ""), pattern)}


def _valid_id(value: str, pattern: str) -> bool:
    return re.fullmatch(pattern, value.strip()) is not None


def _linked_ids(value: str, pattern: str) -> set[str]:
    return set(re.findall(pattern, value))


def _generated_requirement_ids(rows: list[dict[str, str]]) -> set[str]:
    return {row.get("ID", "") for row in rows if re.fullmatch(r"(?:REQ|NFR)-1\d\d", row.get("ID", ""))}


def _requirement_graph_ids(repo_root: Path, cfg: ProjectConfig) -> set[str]:
    path = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root) / "graph.manual.json"
    if not path.exists():
        return set()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    nodes = raw.get("nodes", []) if isinstance(raw, dict) else []
    ids: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id", ""))
        match = re.fullmatch(r"requirement:((?:REQ|NFR)-\d{3})", node_id)
        if match:
            ids.add(match.group(1))
    return ids


def _check_domain(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    root = wiki / "domain"
    if not root.exists():
        return ["domain model not initialized: run `echel domain` to start"]

    failures: list[str] = []
    missing = [name for name in DOMAIN_FILES if not (root / name).exists()]
    if missing:
        return [f"domain artifact missing: wiki/domain/{name}" for name in missing]

    requirement_ids = _domain_required_requirement_ids(repo_root, cfg)
    coverage = _domain_requirement_coverage(root / "domain-overview.md")
    for rid in sorted(requirement_ids):
        item = coverage.get(rid)
        if not item:
            failures.append(f"{rid} is not mapped in domain-overview: run `echel domain` or add domain coverage")
            continue
        if item.get("Coverage Status", "").lower() != "covered":
            failures.append(f"{rid} domain coverage is not marked Covered")
        for field, pattern in [
            ("Domain Concept", r"DM-\d{3}"),
            ("Bounded Context", r"BC-\d{3}"),
            ("Rule", r"BR-\d{3}"),
        ]:
            if not _linked_ids(item.get(field, ""), pattern):
                failures.append(f"{rid} domain coverage is missing `{field}`")

    definitions = _domain_defined_ids(root)
    references = _domain_referenced_ids(root)
    for family, refs in references.items():
        missing_refs = sorted(refs - definitions.get(family, set()))
        for ref in missing_refs:
            failures.append(f"{ref} is referenced in domain artifacts but not defined")

    failures.extend(_domain_language_failures(root / "ubiquitous-language.md"))
    failures.extend(_domain_technology_leakage(root))

    graph_ids = _domain_graph_ids(repo_root, cfg)
    generated_ids: set[str] = set()
    for family, ids in definitions.items():
        generated_ids.update(id_ for id_ in ids if re.fullmatch(_domain_pattern(family), id_) and _is_generated_domain_id(id_))
    for did in sorted(generated_ids):
        if did not in graph_ids:
            failures.append(f"{did} is missing from the product graph: rerun `echel domain` after domain updates")

    return failures


def _check_architecture(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    root = wiki / "architecture"
    if not root.exists():
        return ["architecture model not initialized: run `echel architecture` to start"]

    failures: list[str] = []
    missing = [name for name in ARCHITECTURE_FILES if not (root / name).exists()]
    if missing:
        return [f"architecture artifact missing: wiki/architecture/{name}" for name in missing]

    overview_rows = _table_rows(root / "overview.md")
    generated_rows = _generated_architecture_rows(overview_rows)
    generated_ids = {row.get("ID", "") for row in generated_rows}
    requirement_ids = _architecture_required_requirement_ids(repo_root, cfg)

    failures.extend(_architecture_deployment_failures(wiki, root))
    failures.extend(_architecture_table_completeness(root / "data-architecture.md", "data strategy", ["ID", "Store", "Owned Data", "Format", "Source IDs", "Rationale"]))
    failures.extend(_architecture_table_completeness(root / "security-architecture.md", "security model", ["ID", "Boundary", "Assets Protected", "Threats", "Controls", "Source IDs"]))
    failures.extend(_architecture_table_completeness(root / "observability-architecture.md", "observability model", ["ID", "Surface", "Signal", "Producer", "Consumer", "Source IDs"]))
    failures.extend(_architecture_major_decision_adr_failures(overview_rows))

    if not generated_rows:
        failures.append("architecture mappings are missing: run `echel architecture` after domain readiness passes")
    for row in generated_rows:
        aid = row.get("ID", "")
        if not _linked_ids(row.get("Source IDs", ""), r"(?:REQ|NFR)-\d{3}"):
            failures.append(f"{aid} has no requirement or non-functional source ID")
        if not _linked_ids(row.get("Domain Boundaries Preserved", ""), r"(?:DM|BC|AGG|DE|BR)-\d{3}"):
            failures.append(f"{aid} has no preserved domain boundary IDs")
        if _blank_or_tbd(row.get("Rationale", "")):
            failures.append(f"{aid} has no architecture rationale")

    mapped_requirements = set()
    for row in generated_rows:
        mapped_requirements.update(_linked_ids(row.get("Source IDs", ""), r"(?:REQ|NFR)-\d{3}"))
    for rid in sorted(requirement_ids - mapped_requirements):
        failures.append(f"{rid} is not mapped in generated architecture rows")

    graph = _architecture_graph(repo_root, cfg)
    graph_ids = _architecture_graph_ids(graph)
    for aid in sorted(generated_ids):
        if aid not in graph_ids:
            failures.append(f"{aid} is missing from the product graph: rerun `echel architecture` after architecture updates")
    failures.extend(_architecture_graph_edge_failures(graph, generated_rows))
    failures.extend(_architecture_overengineering_failures(root))

    return failures


def _check_release(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    wiki = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root)
    deployment_root = wiki / "deployment"
    failures: list[str] = []

    validation_report = wiki / "validation" / "validation-report.md"
    validation_summary = wiki / "reports" / "validation-summary.md"
    if not validation_report.exists():
        failures.append("validation report missing: run `python3 tools/echel.py validate`")
    if not validation_summary.exists():
        failures.append("validation summary missing: run `python3 tools/echel.py validate`")
    if validation_report.exists():
        _risks, blockers = collect_validation_issues(repo_root, cfg)
        open_blockers = [blocker for blocker in blockers if blocker.status == "open"]
        for blocker in open_blockers:
            failures.append(f"validation blocker is open: {blocker.issue_id} ({blocker.title})")

    missing = [name for name in DEPLOYMENT_FILES if not (deployment_root / name).exists()]
    if missing:
        failures.extend(f"deployment artifact missing: wiki/deployment/{name}" for name in missing)
        return failures

    failures.extend(_deployment_artifact_completeness(deployment_root))
    failures.extend(_rollback_plan_failures(deployment_root / "rollback-plan.md"))
    failures.extend(_production_checklist_failures(deployment_root / "production-checklist.md"))
    failures.extend(_release_evidence_failures(repo_root, cfg))
    failures.extend(_release_risk_failures(wiki / "risks.md"))
    return failures


def _deployment_artifact_completeness(root: Path) -> list[str]:
    failures: list[str] = []
    for name in DEPLOYMENT_FILES:
        path = root / name
        text = path.read_text(encoding="utf-8")
        content_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.startswith("---") and not re.fullmatch(r"\w+:\s*.*", line.strip())
        ]
        if not content_lines or any(line == "TBD" for line in content_lines):
            failures.append(f"deployment artifact is incomplete: wiki/deployment/{name}")
    return failures


def _rollback_plan_failures(path: Path) -> list[str]:
    rows = [
        row for row in _table_rows(path)
        if _valid_id(row.get("ID", ""), r"RB-\d{3}") and row.get("Status", "").lower() != "future"
    ]
    if not rows:
        return ["rollback plan has no active RB-### rollback strategy rows"]
    failures: list[str] = []
    for row in rows:
        rid = row.get("ID", "")
        for field in ["Failure Mode", "Detection Signal", "Rollback Action", "Owner"]:
            if _blank_or_tbd(row.get(field, "")):
                failures.append(f"{rid} rollback row is incomplete: `{field}` must be populated")
    return failures


def _production_checklist_failures(path: Path) -> list[str]:
    rows = [row for row in _table_rows(path) if _valid_id(row.get("ID", ""), r"PROD-\d{3}")]
    if not rows:
        return ["production checklist has no PROD-### rows"]
    failures: list[str] = []
    passing_statuses = {"passed", "accepted", "accepted exception", "deferred"}
    for row in rows:
        cid = row.get("ID", "")
        status = row.get("Status", "").strip().lower()
        if status not in passing_statuses:
            failures.append(f"{cid} production checklist is not passed or accepted: status is `{row.get('Status', '') or 'Missing'}`")
        for field in ["Area", "Check", "Required Evidence", "Owner"]:
            if _blank_or_tbd(row.get(field, "")):
                failures.append(f"{cid} production checklist row is incomplete: `{field}` must be populated")
    return failures


def _release_evidence_failures(repo_root: Path, cfg: ProjectConfig) -> list[str]:
    reg = ensure_registry(repo_root / cfg.evidence_registry)
    issues = [f"{issue.severity}: {issue.message}" for issue in validate_registry(reg, str(repo_root / cfg.evidence_registry))]
    artifacts = reg.get("artifacts", {}) if isinstance(reg, dict) else {}
    if not isinstance(artifacts, dict) or not artifacts:
        issues.append("release evidence is missing: register at least one artifact with `python3 tools/echel.py evidence add`")
        return issues
    release_like = []
    for evid, payload in artifacts.items():
        if not isinstance(payload, dict):
            continue
        joined = " ".join(str(payload.get(field, "")) for field in ["subject", "kind", "summary"]).lower()
        if any(token in joined for token in ["release", "validation", "proof", "deployment"]):
            release_like.append(str(evid))
    if not release_like:
        issues.append("registered evidence does not reference release, validation, proof, or deployment")
    return issues


def _release_risk_failures(path: Path) -> list[str]:
    if not path.exists():
        return ["risk register missing: wiki/risks.md"]
    rows = _table_rows(path)
    failures: list[str] = []
    for row in rows:
        rid = row.get("Risk ID") or row.get("ID") or row.get("Risk")
        if not rid:
            continue
        status = (row.get("Status") or row.get("Risk Status") or "").strip().lower()
        mitigation = row.get("Mitigation") or row.get("Mitigation Plan") or row.get("Accepted By") or row.get("Owner")
        if status in {"open", "unmitigated", "blocking", "blocked"}:
            failures.append(f"{rid} release risk is not accepted or mitigated")
        elif status and status not in {"mitigated", "accepted", "resolved", "closed", "done"}:
            failures.append(f"{rid} release risk has unknown status `{status}`")
        elif not status and _blank_or_tbd(mitigation):
            failures.append(f"{rid} release risk has no mitigation or acceptance record")
    if rows:
        return failures
    text = path.read_text(encoding="utf-8")
    if re.search(r"^##\s+", text, flags=re.MULTILINE) and "Mitigation:" not in text and "Accepted" not in text:
        failures.append("risk register has narrative risks without mitigation or acceptance")
    return failures


def _generated_architecture_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row for row in rows
        if _valid_id(row.get("ID", ""), r"ARCH-9\d\d")
    ]


def _architecture_required_requirement_ids(repo_root: Path, cfg: ProjectConfig) -> set[str]:
    root = requirements_root(repo_root, cfg)
    rows = _dedupe_rows(_requirement_rows(root / PRODUCT_FILE), "ID") + _dedupe_rows(_requirement_rows(root / FUNCTIONAL_FILE), "ID")
    nfr_rows = _dedupe_rows(_requirement_rows(root / NFR_FILE), "ID")
    return {row.get("ID", "") for row in rows + nfr_rows if _valid_id(row.get("ID", ""), r"(?:REQ|NFR)-\d{3}")}


def _architecture_deployment_failures(wiki: Path, root: Path) -> list[str]:
    overview = root / "overview.md"
    legacy = wiki / "architecture.md"
    text = ""
    for path in [overview, legacy]:
        if path.exists():
            text += "\n" + path.read_text(encoding="utf-8")
    lowered = text.lower()
    if "deployment model" in lowered or "local-first" in lowered or "hosted" in lowered:
        return []
    return ["deployment model is missing: state local, hosted, hybrid, or future deployment posture in architecture"]


def _architecture_table_completeness(path: Path, label: str, required_fields: list[str]) -> list[str]:
    rows = [
        row for row in _table_rows(path)
        if _valid_id(row.get("ID", ""), r"ARCH-\d{3}") and row.get("Status", "").lower() not in {"draft", "tbd"}
    ]
    if not rows:
        return [f"{label} is incomplete: add at least one populated ARCH-### row to {path.name}"]
    failures: list[str] = []
    complete_rows = 0
    for row in rows:
        aid = row.get("ID", "")
        missing = [field for field in required_fields if _blank_or_tbd(row.get(field, ""))]
        if missing:
            failures.append(f"{aid} {label} row is incomplete: {', '.join(missing)} must be populated")
        else:
            complete_rows += 1
    if complete_rows == 0:
        failures.append(f"{label} is incomplete: no fully populated architecture row found in {path.name}")
    return failures


def _architecture_major_decision_adr_failures(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    for row in rows:
        aid = row.get("ID", "")
        if _valid_id(aid, r"ARCH-\d{3}") and row.get("Status", "").lower() in {"accepted", "existing"}:
            coverage = row.get("ADR Coverage", "")
            if not _linked_ids(coverage, r"ADR-\d{4}"):
                failures.append(f"{aid} is an accepted architecture choice without ADR coverage")
        decision = row.get("Decision Area", "")
        if decision and row.get("ADR Required", "").lower() == "yes":
            status = row.get("ADR Status", "")
            if not _linked_ids(status, r"ADR-\d{4}"):
                failures.append(f"{decision} requires an ADR but ADR Status is missing an ADR-#### reference")
            if row.get("Rationale Present", "").lower() != "yes":
                failures.append(f"{decision} is missing rationale confirmation")
    return failures


def _architecture_graph(repo_root: Path, cfg: ProjectConfig) -> dict:
    path = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root) / "graph.manual.json"
    if not path.exists():
        return {"nodes": [], "edges": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"nodes": [], "edges": []}
    if not isinstance(raw, dict):
        return {"nodes": [], "edges": []}
    raw.setdefault("nodes", [])
    raw.setdefault("edges", [])
    return raw


def _architecture_graph_ids(graph: dict) -> set[str]:
    ids: set[str] = set()
    for node in graph.get("nodes", []):
        if not isinstance(node, dict):
            continue
        match = re.fullmatch(r"architecture:(ARCH-\d{3})", str(node.get("id", "")))
        if match:
            ids.add(match.group(1))
    return ids


def _architecture_graph_edge_failures(graph: dict, rows: list[dict[str, str]]) -> list[str]:
    edges = graph.get("edges", [])
    failures: list[str] = []
    if not isinstance(edges, list):
        return ["architecture graph edges are invalid: graph.manual.json edges must be a list"]
    edge_pairs = {
        (str(edge.get("from_id", "")), str(edge.get("to_id", "")))
        for edge in edges
        if isinstance(edge, dict)
    }
    for row in rows:
        aid = row.get("ID", "")
        target = f"architecture:{aid}"
        for rid in sorted(_linked_ids(row.get("Source IDs", ""), r"(?:REQ|NFR)-\d{3}")):
            if (f"requirement:{rid}", target) not in edge_pairs:
                failures.append(f"{aid} graph mapping is missing requirement edge from {rid}")
        for did in sorted(_linked_ids(row.get("Domain Boundaries Preserved", ""), r"(?:DM|BC|AGG|DE|BR)-\d{3}")):
            if not any(from_id.endswith(f":{did}") and to_id == target for from_id, to_id in edge_pairs):
                failures.append(f"{aid} graph mapping is missing domain edge from {did}")
    return failures


def _architecture_overengineering_failures(root: Path) -> list[str]:
    failures: list[str] = []
    pattern = re.compile(r"\b(" + "|".join(re.escape(term) for term in ARCHITECTURE_COMPLEXITY_TERMS) + r")\b", re.IGNORECASE)
    for name in ARCHITECTURE_FILES:
        for row in _table_rows(root / name):
            selected_text = _architecture_complexity_text(row)
            if not pattern.search(selected_text) or _architecture_complexity_is_guarded(row):
                continue
            row_id = row.get("ID") or row.get("Decision") or row.get("Decision Area") or "architecture row"
            failures.append(f"{row_id} has unjustified complexity risk: add ADR coverage, explicit rationale, or mark as avoided/future")
    return failures


def _architecture_complexity_text(row: dict[str, str]) -> str:
    selected_fields = [
        "ID",
        "Choice",
        "Architecture Choice",
        "Component",
        "Store",
        "Surface",
        "Boundary",
        "Event",
        "Workflow",
        "Current Interface",
        "Interface",
        "Decision",
    ]
    return " ".join(row.get(field, "") for field in selected_fields)


def _architecture_complexity_is_guarded(row: dict[str, str]) -> bool:
    text = " ".join(row.values()).lower()
    if any(marker in text for marker in ["avoid", "no external", "no public", "future adr", "requires future adr", "planned", "revisit trigger"]):
        return True
    if any("alternative" in key.lower() and not _blank_or_tbd(value) for key, value in row.items()):
        return True
    if row.get("Rationale Present", "").lower() == "yes" and _linked_ids(row.get("ADR Status", ""), r"ADR-\d{4}"):
        return True
    has_adr = bool(_linked_ids(text.upper(), r"ADR-\d{4}"))
    rationale = row.get("Rationale", "") or row.get("Default Position", "") or row.get("Required Evidence", "")
    return has_adr and not _blank_or_tbd(rationale)


def _domain_required_requirement_ids(repo_root: Path, cfg: ProjectConfig) -> set[str]:
    root = requirements_root(repo_root, cfg)
    rows = _dedupe_rows(_requirement_rows(root / PRODUCT_FILE), "ID") + _dedupe_rows(_requirement_rows(root / FUNCTIONAL_FILE), "ID")
    nfr_rows = _dedupe_rows(_requirement_rows(root / NFR_FILE), "ID")
    return {row.get("ID", "") for row in rows + nfr_rows if _valid_id(row.get("ID", ""), r"(?:REQ|NFR)-\d{3}")}


def _domain_requirement_coverage(path: Path) -> dict[str, dict[str, str]]:
    coverage: dict[str, dict[str, str]] = {}
    for row in _table_rows(path):
        rid = row.get("Requirement ID", "")
        if _valid_id(rid, r"(?:REQ|NFR)-\d{3}"):
            coverage[rid] = row
    return coverage


def _domain_defined_ids(root: Path) -> dict[str, set[str]]:
    definitions = {family: set() for family in DOMAIN_ID_PATTERNS}
    file_map = {
        "DM": ["domain-overview.md", "ubiquitous-language.md", "entities.md"],
        "BC": ["bounded-contexts.md"],
        "AGG": ["aggregates.md"],
        "DE": ["domain-events.md"],
        "WF": ["workflows.md"],
        "BR": ["policies-and-rules.md"],
    }
    for family, names in file_map.items():
        pattern = _domain_pattern(family)
        for name in names:
            for row in _table_rows(root / name):
                for key in ["ID", "Context ID"]:
                    value = row.get(key, "")
                    if _valid_id(value, pattern):
                        definitions[family].add(value)
                if family == "DM":
                    definitions[family].update(_linked_ids(row.get("Domain Concept", ""), pattern))
                if family == "BC":
                    definitions[family].update(_linked_ids(row.get("Bounded Context", ""), pattern))
                if family == "AGG":
                    definitions[family].update(_linked_ids(row.get("Aggregate", ""), pattern))
                if family == "DE":
                    definitions[family].update(_linked_ids(row.get("Event", ""), pattern))
                if family == "BR":
                    definitions[family].update(_linked_ids(row.get("Rule", ""), pattern))
    return definitions


def _domain_referenced_ids(root: Path) -> dict[str, set[str]]:
    refs = {family: set() for family in DOMAIN_ID_PATTERNS}
    for name in DOMAIN_FILES:
        for row in _table_rows(root / name):
            text = " ".join(row.values())
            for family, pattern in DOMAIN_ID_PATTERNS.items():
                refs[family].update(_linked_ids(text, pattern))
    return refs


def _domain_language_failures(path: Path) -> list[str]:
    failures: list[str] = []
    terms: dict[str, tuple[str, str]] = {}
    definitions: dict[str, str] = {}
    for row in _table_rows(path):
        did = row.get("ID", "")
        term = row.get("Term", "").strip()
        definition = row.get("Definition", "").strip()
        if not _valid_id(did, r"DM-\d{3}") or _blank_or_tbd(term) or _blank_or_tbd(definition):
            continue
        key = re.sub(r"\s+", " ", term.lower())
        normalized_definition = re.sub(r"\s+", " ", definition.lower())
        if key in terms and terms[key][1] != normalized_definition:
            failures.append(f"{term} has duplicate meanings in ubiquitous language: {terms[key][0]} and {did}")
        terms[key] = (did, normalized_definition)
        if normalized_definition in definitions and definitions[normalized_definition] != did:
            failures.append(f"{did} duplicates the meaning of {definitions[normalized_definition]} in ubiquitous language")
        definitions[normalized_definition] = did
    return failures


def _domain_technology_leakage(root: Path) -> list[str]:
    failures: list[str] = []
    pattern = re.compile(r"\b(" + "|".join(re.escape(term) for term in TECH_LEAKAGE_TERMS) + r")\b", re.IGNORECASE)
    for name in DOMAIN_FILES:
        for row in _table_rows(root / name):
            if _technology_constraint_row(row):
                continue
            text = " ".join(row.values())
            leaked = sorted({match.group(1).lower() for match in pattern.finditer(text)})
            if leaked:
                row_id = row.get("ID") or row.get("Requirement ID") or row.get("Context ID") or "domain row"
                failures.append(f"{row_id} contains technology leakage in domain model: {', '.join(leaked)}")
    return failures


def _technology_constraint_row(row: dict[str, str]) -> bool:
    joined = " ".join(row.values()).lower()
    return "constraint" in joined and not _blank_or_tbd(row.get("Source IDs", ""))


def _domain_graph_ids(repo_root: Path, cfg: ProjectConfig) -> set[str]:
    path = resolve_symbolic_path("$WIKI_ROOT", cfg, repo_root) / "graph.manual.json"
    if not path.exists():
        return set()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    nodes = raw.get("nodes", []) if isinstance(raw, dict) else []
    ids: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id", ""))
        for prefix in ["domain-concept", "bounded-context", "domain-aggregate", "domain-event", "domain-workflow", "business-rule"]:
            if node_id.startswith(f"{prefix}:"):
                ids.add(node_id.split(":", 1)[1])
    return ids


def _domain_pattern(family: str) -> str:
    return DOMAIN_ID_PATTERNS[family]


def _is_generated_domain_id(value: str) -> bool:
    return re.fullmatch(r"(?:DM|BC|AGG|DE|BR)-2\d\d|WF-DM-2\d\d", value) is not None


def _validation_method(row: dict[str, str]) -> str:
    return row.get("Validation Method", "") or row.get("Test Method", "") or row.get("Verification Method", "")


def _blank_or_tbd(value: str) -> bool:
    cleaned = value.strip().strip("`")
    return not cleaned or cleaned.upper() == "TBD" or "TBD" in cleaned.upper()


CHECKS: dict[str, GateFn] = {
    "schema": _check_schema,
    "coherence": _check_coherence,
    "evidence-links": _check_evidence_links,
    "primitives": _check_primitives,
    "discovery": _check_discovery,
    "requirements": _check_requirements,
    "domain": _check_domain,
    "architecture": _check_architecture,
    "release": _check_release,
    "release-deployment": _check_release,
}


def ensure_policy(path: Path) -> dict:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        default = {
            "version": 1,
            "gates": [
                {"id": "GATE-SCHEMA", "checks": ["schema", "primitives"]},
                {"id": "GATE-INTEGRITY", "checks": ["coherence", "evidence-links"]},
                {"id": "GATE-DISCOVERY", "checks": ["discovery"]},
                {"id": "GATE-REQUIREMENTS", "checks": ["requirements"]},
                {"id": "GATE-DOMAIN", "checks": ["domain"]},
                {"id": "GATE-ARCHITECTURE", "checks": ["architecture"]},
                {"id": "GATE-RELEASE", "checks": ["release"]},
            ],
        }
        path.write_text(json.dumps(default, indent=2) + "\n", encoding="utf-8")
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def compile_gates(policy: dict) -> tuple[list[GateResult], list[str]]:
    errors: list[str] = []
    gates = policy.get("gates") if isinstance(policy, dict) else None
    if not isinstance(gates, list):
        return [], ["policy.gates must be a list"]

    gate_ids = []
    for gate in gates:
        if isinstance(gate, dict):
            gate_ids.append(str(gate.get("id", "")))
    for issue in validate_gate_ids(gate_ids, "gate-policy"):
        errors.append(issue.message)

    compiled: list[GateResult] = []
    for gate in gates:
        if not isinstance(gate, dict):
            errors.append("gate entry must be object")
            continue
        gid = gate.get("id")
        checks = gate.get("checks")
        if not isinstance(gid, str) or not isinstance(checks, list):
            errors.append("gate requires string id and list checks")
            continue
        unknown = [chk for chk in checks if chk not in CHECKS]
        if unknown:
            errors.append(f"gate {gid} uses unknown checks: {', '.join(unknown)}")
            continue
        compiled.append(GateResult(gate_id=gid, passed=True, failures=[]))

    return compiled, errors


def run_gates(repo_root: Path, cfg: ProjectConfig) -> tuple[list[GateResult], list[str]]:
    policy_path = repo_root / cfg.gate_policy
    policy = ensure_policy(policy_path)
    compiled, errors = compile_gates(policy)
    if errors:
        return [], errors

    gate_by_id = {g.gate_id: g for g in compiled}
    for gate in policy["gates"]:
        gid = gate["id"]
        for chk in gate["checks"]:
            failures = CHECKS[chk](repo_root, cfg)
            if failures:
                gate_by_id[gid].passed = False
                gate_by_id[gid].failures.extend(f"[{chk}] {failure}" for failure in failures)
    return compiled, []


def run_stage_gate(repo_root: Path, cfg: ProjectConfig, stage: str) -> GateResult:
    check_name = f"discovery" if stage == "discovery" else stage
    if check_name not in CHECKS:
        return GateResult(gate_id=f"GATE-{stage.upper()}", passed=False, failures=[f"unknown stage gate: {stage}"])
    failures = CHECKS[check_name](repo_root, cfg)
    return GateResult(
        gate_id=f"GATE-{stage.upper()}",
        passed=len(failures) == 0,
        failures=failures,
    )
