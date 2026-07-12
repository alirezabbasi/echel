from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
import re

from .config import ProjectConfig

EVIDENCE_LINK_PATTERN = re.compile(r"\b(EVID-[A-Z0-9\-]{3,})\b")
EVIDENCE_ID_PATTERN = re.compile(r"^EVID-[A-Z0-9\-]{3,}$")


@dataclass
class EvidenceIssue:
    severity: str
    source: str
    message: str


def ensure_registry(path: Path) -> dict:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"version": 1, "artifacts": {}}
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return data
    return json.loads(path.read_text(encoding="utf-8"))


def register_evidence(
    repo_root: Path,
    cfg: ProjectConfig,
    *,
    evidence_id: str | None,
    subject: str,
    kind: str,
    path: str,
    producer: str,
    summary: str,
    checksum: str | None = None,
) -> tuple[str, dict]:
    """Register one evidence artifact and refresh graph evidence nodes."""
    reg_path = repo_root / cfg.evidence_registry
    registry = ensure_registry(reg_path)
    artifacts = registry.setdefault("artifacts", {})
    if not isinstance(artifacts, dict):
        raise ValueError("evidence registry artifacts must be a mapping")

    evid = evidence_id or _next_evidence_id(artifacts)
    if not EVIDENCE_ID_PATTERN.fullmatch(evid):
        raise ValueError("evidence id must match EVID-[A-Z0-9-]+")

    normalized_path = _normalize_evidence_path(repo_root, path)
    digest = checksum or _sha256(repo_root, normalized_path)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    previous = artifacts.get(evid, {}) if isinstance(artifacts.get(evid), dict) else {}
    record = {
        **previous,
        "subject": subject.strip(),
        "kind": kind.strip(),
        "path": normalized_path,
        "checksum": digest,
        "producer": producer.strip(),
        "summary": summary.strip(),
        "created_at": previous.get("created_at", now),
        "updated_at": now,
    }
    missing = [field for field in ("subject", "kind", "path", "checksum", "producer", "summary") if not record[field]]
    if missing:
        raise ValueError(f"evidence record missing required field(s): {', '.join(missing)}")

    artifacts[evid] = record
    reg_path.parent.mkdir(parents=True, exist_ok=True)
    reg_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    from .graph import write_graph

    write_graph(repo_root, cfg)
    return evid, record


def validate_registry(registry: dict, source: str) -> list[EvidenceIssue]:
    issues: list[EvidenceIssue] = []
    if not isinstance(registry, dict):
        return [EvidenceIssue("critical", source, "evidence registry must be object")]
    if registry.get("version") != 1:
        issues.append(EvidenceIssue("critical", source, "registry version must equal 1"))
    artifacts = registry.get("artifacts")
    if not isinstance(artifacts, dict):
        issues.append(EvidenceIssue("critical", source, "artifacts must be mapping"))
        return issues
    for evid, payload in artifacts.items():
        if not EVIDENCE_LINK_PATTERN.fullmatch(evid):
            issues.append(EvidenceIssue("critical", source, f"invalid evidence id '{evid}'"))
        if not isinstance(payload, dict):
            issues.append(EvidenceIssue("major", source, f"artifact '{evid}' payload must be object"))
            continue
        if "path" not in payload:
            issues.append(EvidenceIssue("major", source, f"artifact '{evid}' missing path"))
        for field in ("subject", "kind", "checksum", "producer", "summary"):
            if field not in payload:
                issues.append(EvidenceIssue("major", source, f"artifact '{evid}' missing {field}"))
    return issues


def extract_evidence_links(text: str) -> set[str]:
    return set(EVIDENCE_LINK_PATTERN.findall(text))


def validate_links(files: list[Path], registry: dict) -> list[EvidenceIssue]:
    artifacts = registry.get("artifacts", {}) if isinstance(registry, dict) else {}
    known = set(artifacts.keys())
    issues: list[EvidenceIssue] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for evid in sorted(extract_evidence_links(text)):
            if evid not in known:
                issues.append(EvidenceIssue("major", str(path), f"references unknown evidence id {evid}"))
    return issues


def _next_evidence_id(artifacts: dict) -> str:
    highest = 0
    for evid in artifacts:
        match = re.fullmatch(r"EVID-(\d+)", str(evid))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"EVID-{highest + 1:03d}"


def _normalize_evidence_path(repo_root: Path, raw_path: str) -> str:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        try:
            return str(candidate.resolve().relative_to(repo_root.resolve()))
        except ValueError:
            return str(candidate)
    return candidate.as_posix()


def _sha256(repo_root: Path, normalized_path: str) -> str:
    evidence_path = Path(normalized_path)
    if not evidence_path.is_absolute():
        evidence_path = repo_root / evidence_path
    if not evidence_path.exists():
        raise FileNotFoundError(f"evidence path not found: {normalized_path}")
    digest = hashlib.sha256()
    with evidence_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"
