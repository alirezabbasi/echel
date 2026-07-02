from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable

from .coherence import detect_drift
from .config import ProjectConfig, resolve_symbolic_path
from .discovery import DISCOVERY_FIELDS, discovery_root, _section_body, _is_tbd
from .evidence import ensure_registry, validate_links, validate_registry
from .primitives import validate_decisions, validate_gate_ids, validate_tasks


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


CHECKS: dict[str, GateFn] = {
    "schema": _check_schema,
    "coherence": _check_coherence,
    "evidence-links": _check_evidence_links,
    "primitives": _check_primitives,
    "discovery": _check_discovery,
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
