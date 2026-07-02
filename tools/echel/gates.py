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
