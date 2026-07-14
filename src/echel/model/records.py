from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, ClassVar


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class Project:
    name: str
    idea: str
    current_stage: str = "idea"
    profile: str = "product"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class KnowledgeRecord:
    id: str
    kind: str
    statement: str
    stage: str
    status: str = "proposed"
    confidence: str = "medium"
    sources: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    record_type: ClassVar[str] = "knowledge"

    def to_dict(self) -> dict[str, Any]:
        return {"record_type": self.record_type, **asdict(self)}


@dataclass
class WorkItem:
    id: str
    title: str
    objective: str
    stage: str
    status: str = "planned"
    priority: str = "normal"
    relates_to: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)
    verification: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    record_type: ClassVar[str] = "work"

    def to_dict(self) -> dict[str, Any]:
        return {"record_type": self.record_type, **asdict(self)}


@dataclass
class Run:
    id: str
    work_item: str
    runtime: str
    model: str = "default"
    status: str = "created"
    context_digest: str = ""
    command: list[str] = field(default_factory=list)
    started_at: str = field(default_factory=utc_now)
    completed_at: str | None = None
    exit_code: int | None = None
    summary: str = ""
    record_type: ClassVar[str] = "run"

    def to_dict(self) -> dict[str, Any]:
        return {"record_type": self.record_type, **asdict(self)}


@dataclass
class Evidence:
    id: str
    subject: str
    kind: str
    summary: str
    command: list[str] = field(default_factory=list)
    exit_code: int | None = None
    artifact: str = ""
    checksum: str = ""
    created_at: str = field(default_factory=utc_now)
    record_type: ClassVar[str] = "evidence"

    def to_dict(self) -> dict[str, Any]:
        return {"record_type": self.record_type, **asdict(self)}


@dataclass
class Finding:
    id: str
    kind: str
    statement: str
    status: str = "open"
    severity: str = "warning"
    affects: list[str] = field(default_factory=list)
    source_run: str = ""
    created_at: str = field(default_factory=utc_now)
    record_type: ClassVar[str] = "finding"

    def to_dict(self) -> dict[str, Any]:
        return {"record_type": self.record_type, **asdict(self)}
