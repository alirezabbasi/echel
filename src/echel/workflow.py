from __future__ import annotations

from dataclasses import replace

from echel.methodology.lifecycle import STAGES, get_stage, next_stage
from echel.model.records import KnowledgeRecord, WorkItem, utc_now
from echel.storage.files import FileStore


class LifecycleBlocked(RuntimeError):
    pass


class WorkflowService:
    def __init__(self, store: FileStore):
        self.store = store

    def status(self) -> dict:
        project = self.store.load_project()
        records = self.store.records()
        current = get_stage(project.current_stage)
        present = {
            record.get("kind")
            for record in records
            if record.get("record_type") == "knowledge"
            and record.get("stage") == current.id
            and record.get("status") in {"accepted", "validated"}
        }
        missing = sorted(set(current.required_kinds) - present)
        return {
            "project": project.to_dict(),
            "stage": current,
            "missing": missing,
            "record_counts": {
                collection: len(self.store.records(collection)) for collection in self.store.DIRECTORIES
            },
        }

    def advance(self, force: bool = False) -> str:
        project = self.store.load_project()
        state = self.status()
        if state["missing"] and not force:
            raise LifecycleBlocked(
                f"{project.current_stage} is not usable; missing accepted knowledge: "
                + ", ".join(state["missing"])
            )
        target = next_stage(project.current_stage)
        if target is None:
            raise LifecycleBlocked("project is already at the final lifecycle stage")
        project = replace(project, current_stage=target.id, updated_at=utc_now())
        self.store.save_project(project)
        return target.id

    def add_knowledge(
        self,
        kind: str,
        statement: str,
        *,
        stage: str | None = None,
        status: str = "proposed",
        confidence: str = "medium",
        sources: list[str] | None = None,
    ) -> KnowledgeRecord:
        current = self.store.load_project().current_stage
        record = KnowledgeRecord(
            id=self.store.next_id("CLM"),
            kind=kind,
            statement=statement,
            stage=stage or current,
            status=status,
            confidence=confidence,
            sources=sources or [],
        )
        self.store.put("knowledge", record.to_dict())
        return record

    def add_work(
        self,
        title: str,
        objective: str,
        relates_to: list[str],
        acceptance: list[str],
        verification: list[str],
    ) -> WorkItem:
        for record_id in relates_to:
            self.store.get(record_id)
        record = WorkItem(
            id=self.store.next_id("WORK"),
            title=title,
            objective=objective,
            stage=self.store.load_project().current_stage,
            relates_to=relates_to,
            acceptance=acceptance,
            verification=verification,
        )
        self.store.put("work", record.to_dict())
        return record


def lifecycle_summary() -> list[dict[str, str]]:
    return [{"id": stage.id, "title": stage.title, "purpose": stage.purpose} for stage in STAGES]
