from __future__ import annotations

import shutil
import subprocess

from .base import RunRequest, RuntimeResult


class HermesRuntime:
    """Thin adapter: Hermes owns the agent loop; Echel owns product truth."""

    name = "hermes"

    def __init__(self, executable: str = "hermes"):
        self.executable = executable

    def available(self) -> bool:
        return shutil.which(self.executable) is not None

    def command(self, request: RunRequest) -> list[str]:
        command = [self.executable, "chat", "--toolsets", ",".join(request.allowed_toolsets), "-q", request.prompt]
        if request.model:
            command[2:2] = ["--model", request.model]
        return command

    def execute(self, request: RunRequest) -> RuntimeResult:
        if not self.available():
            raise RuntimeError("Hermes executable is not installed or not on PATH")
        command = self.command(request)
        completed = subprocess.run(
            command,
            cwd=request.workspace,
            text=True,
            capture_output=True,
            check=False,
        )
        return RuntimeResult(tuple(command), completed.returncode, completed.stdout, completed.stderr)
