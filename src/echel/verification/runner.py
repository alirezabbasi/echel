from __future__ import annotations

import hashlib
import shlex
import subprocess

from echel.model.records import Evidence
from echel.storage.files import FileStore


class VerificationRunner:
    def __init__(self, store: FileStore):
        self.store = store

    def verify(self, work_id: str) -> list[Evidence]:
        work = self.store.get(work_id)
        results: list[Evidence] = []
        for raw_command in work.get("verification", []):
            command = shlex.split(raw_command)
            completed = subprocess.run(
                command,
                cwd=self.store.workspace,
                text=True,
                capture_output=True,
                check=False,
            )
            output = completed.stdout + completed.stderr
            evidence = Evidence(
                id=self.store.next_id("EVID"),
                subject=work_id,
                kind="verification-command",
                summary=f"{raw_command}: {'passed' if completed.returncode == 0 else 'failed'}",
                command=command,
                exit_code=completed.returncode,
                checksum=hashlib.sha256(output.encode("utf-8")).hexdigest(),
            )
            self.store.put("evidence", evidence.to_dict())
            results.append(evidence)
        return results
