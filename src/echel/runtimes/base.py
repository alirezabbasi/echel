from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class RunRequest:
    prompt: str
    workspace: Path
    model: str | None = None
    allowed_toolsets: tuple[str, ...] = ("terminal", "file")
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeResult:
    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str


class AgentRuntime(Protocol):
    name: str

    def available(self) -> bool: ...
    def execute(self, request: RunRequest) -> RuntimeResult: ...
