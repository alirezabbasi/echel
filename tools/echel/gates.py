from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable

from .coherence import detect_drift
from .config import ProjectConfig, resolve_symbolic_path
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


CHECKS: dict[str, GateFn] = {
    "schema": _check_schema,
    "coherence": _check_coherence,
    "evidence-links": _check_evidence_links,
    "primitives": _check_primitives,
}


def ensure_policy(path: Path) -> dict:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        default = {
            "version": 1,
            "gates": [
                {"id": "GATE-SCHEMA", "checks": ["schema", "primitives"]},
                {"id": "GATE-INTEGRITY", "checks": ["coherence", "evidence-links"]},
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
