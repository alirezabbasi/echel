from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from echel.storage.files import FileStore


@dataclass(frozen=True)
class CompiledContext:
    work_item: dict
    knowledge: tuple[dict, ...]
    findings: tuple[dict, ...]

    def as_text(self) -> str:
        lines = [
            f"# Work: {self.work_item['id']} — {self.work_item['title']}",
            "",
            "## Objective",
            self.work_item["objective"],
            "",
            "## Acceptance",
            *[f"- {item}" for item in self.work_item.get("acceptance", [])],
            "",
            "## Verification",
            *[f"- `{item}`" for item in self.work_item.get("verification", [])],
            "",
            "## Relevant product knowledge",
        ]
        for record in self.knowledge:
            lines.append(
                f"- [{record['id']}] ({record['kind']}, {record.get('status', 'unknown')}, "
                f"confidence={record.get('confidence', 'unknown')}): {record['statement']}"
            )
        lines.extend(["", "## Open findings"])
        lines.extend(f"- [{item['id']}] {item['statement']}" for item in self.findings)
        if not self.findings:
            lines.append("- None")
        return "\n".join(lines).rstrip() + "\n"

    def digest(self) -> str:
        return hashlib.sha256(self.as_text().encode("utf-8")).hexdigest()

    def as_json(self) -> str:
        return json.dumps(
            {"work_item": self.work_item, "knowledge": self.knowledge, "findings": self.findings},
            indent=2,
        )


class ContextCompiler:
    """Build the smallest authoritative context reachable from a work item."""

    def __init__(self, store: FileStore):
        self.store = store

    def compile(self, work_id: str) -> CompiledContext:
        work = self.store.get(work_id)
        if work.get("record_type") != "work":
            raise ValueError(f"{work_id} is not a work item")
        related = set(work.get("relates_to", []))
        knowledge = []
        for record in self.store.records("knowledge"):
            if record.get("id") in related:
                knowledge.append(record)
        findings = []
        for finding in self.store.records("findings"):
            if finding.get("status") == "open" and related.intersection(finding.get("affects", [])):
                findings.append(finding)
        return CompiledContext(work, tuple(knowledge), tuple(findings))
