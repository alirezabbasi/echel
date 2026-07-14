from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from echel.model.records import Project


class StoreError(RuntimeError):
    pass


class FileStore:
    """Git-friendly canonical storage. Derived indexes must live elsewhere."""

    DIRECTORIES = ("knowledge", "work", "runs", "evidence", "findings")

    def __init__(self, root: Path):
        self.workspace = root.resolve()
        self.root = self.workspace / ".echel"

    def initialize(self, name: str, idea: str, profile: str = "product") -> Project:
        if self.root.exists():
            raise StoreError(f"project already initialized: {self.root}")
        self.root.mkdir(parents=True)
        for directory in self.DIRECTORIES:
            (self.root / directory).mkdir()
        project = Project(name=name.strip(), idea=idea.strip(), profile=profile)
        self._write_json(self.root / "project.json", project.to_dict())
        self._write_json(
            self.root / "policy.json",
            {"version": 1, "knowledge_writes": "approval-required", "runtime": "hermes"},
        )
        return project

    def load_project(self) -> Project:
        payload = self._read_json(self.root / "project.json")
        return Project(**payload)

    def save_project(self, project: Project) -> None:
        self._write_json(self.root / "project.json", project.to_dict())

    def put(self, collection: str, record: dict[str, Any]) -> Path:
        if collection not in self.DIRECTORIES:
            raise StoreError(f"unknown collection: {collection}")
        record_id = str(record.get("id", ""))
        if not re.fullmatch(r"[A-Z]+-[0-9]{3,}", record_id):
            raise StoreError(f"invalid record id: {record_id}")
        path = self.root / collection / f"{record_id}.json"
        self._write_json(path, record)
        return path

    def get(self, record_id: str) -> dict[str, Any]:
        for collection in self.DIRECTORIES:
            path = self.root / collection / f"{record_id}.json"
            if path.exists():
                return self._read_json(path)
        raise StoreError(f"record not found: {record_id}")

    def records(self, collection: str | None = None) -> list[dict[str, Any]]:
        collections = (collection,) if collection else self.DIRECTORIES
        records: list[dict[str, Any]] = []
        for name in collections:
            if name not in self.DIRECTORIES:
                raise StoreError(f"unknown collection: {name}")
            directory = self.root / name
            if directory.exists():
                records.extend(self._read_json(path) for path in sorted(directory.glob("*.json")))
        return records

    def next_id(self, prefix: str) -> str:
        maximum = 0
        pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
        for record in self.records():
            match = pattern.match(str(record.get("id", "")))
            if match:
                maximum = max(maximum, int(match.group(1)))
        return f"{prefix}-{maximum + 1:03d}"

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise StoreError(f"missing Echel file: {path}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise StoreError(f"cannot read {path}: {exc}") from exc
        if not isinstance(payload, dict):
            raise StoreError(f"expected JSON object: {path}")
        return payload

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(path)
