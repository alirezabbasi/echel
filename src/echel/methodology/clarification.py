from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from echel.storage import CanonicalRecordStore, CanonicalRepository
from echel.storage.layout import RepositoryError


CLARIFICATION_CONTRACT = "clarification/v1"


@dataclass
class ClarificationError(RuntimeError):
    code: str
    field: str
    detail: str
    remedy: str

    def __str__(self) -> str:
        return f"{self.code} at /{self.field}: {self.detail}; remedy: {self.remedy}"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "field": self.field,
            "detail": self.detail,
            "remedy": self.remedy,
        }


@dataclass(frozen=True)
class ClarificationQuestion:
    id: str
    prompt: str
    reason: str
    expected_claim_kind: str
    basis: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "reason": self.reason,
            "expected_claim_kind": self.expected_claim_kind,
            "basis": list(self.basis),
            "can_defer": True,
        }


@dataclass(frozen=True)
class ClarificationResult:
    project_id: str
    stage: str
    question: ClarificationQuestion | None
    unresolved_kinds: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract": CLARIFICATION_CONTRACT,
            "project_id": self.project_id,
            "stage": self.stage,
            "question": self.question.to_dict() if self.question else None,
            "unresolved_kinds": list(self.unresolved_kinds),
            "mutation": "none",
            "next_action": (
                "Answer, defer, or supply evidence for this question."
                if self.question
                else (
                    "Resume a deferred question before assessing problem maturity."
                    if self.unresolved_kinds
                    else "Review the captured problem knowledge before advancing."
                )
            ),
        }


@dataclass(frozen=True)
class _Gap:
    id: str
    claim_kind: str
    prompt: str
    reason: str


PROBLEM_GAPS = (
    _Gap(
        "problem.affected-actor",
        "affected-actor",
        "Who specifically experiences the problem described by this idea?",
        "A product problem cannot be evaluated until the affected actor is explicit.",
    ),
    _Gap(
        "problem.current-problem",
        "problem",
        "What difficulty does that actor experience today, stated without prescribing a solution?",
        "Separating the current difficulty from the proposed solution prevents solution-first planning.",
    ),
    _Gap(
        "problem.context",
        "problem-context",
        "In what situation or workflow does this difficulty occur?",
        "Context bounds the problem and prevents Echel from assuming an overly broad market or workflow.",
    ),
    _Gap(
        "problem.observation",
        "problem-observation",
        "What have you observed that indicates this problem is real or recurring?",
        "An observation distinguishes evidence from an untested product assumption.",
    ),
)


class ClarificationService:
    """Select one material question from canonical knowledge, without mutation."""

    def inspect(
        self, workspace: Path, excluded_question_ids: Iterable[str] = ()
    ) -> ClarificationResult:
        try:
            store = CanonicalRecordStore(CanonicalRepository.discover(workspace))
            project = store.scan("project")
            claims = store.scan("claim")
        except RepositoryError as exc:
            raise ClarificationError(
                "ECHEL-CLARIFY-PROJECT-INVALID",
                "workspace",
                exc.detail,
                "initialize or repair the Echel project, then retry",
            ) from exc
        if len(project) != 1:
            raise ClarificationError(
                "ECHEL-CLARIFY-PROJECT-INVALID",
                "workspace",
                "exactly one canonical project record is required",
                "repair the canonical project record, then retry",
            )

        active = {
            str(item.record["kind"])
            for item in claims
            if item.record["status"] not in {"rejected", "superseded", "stale"}
        }
        raw_ideas = [item for item in claims if item.record["kind"] == "raw-idea"]
        if len(raw_ideas) != 1:
            raise ClarificationError(
                "ECHEL-CLARIFY-IDEA-REQUIRED",
                "claims",
                "exactly one canonical raw-idea claim is required",
                "initialize an idea project or repair duplicate raw-idea claims",
            )

        excluded = set(excluded_question_ids)
        known_ids = {gap.id for gap in PROBLEM_GAPS}
        unknown = sorted(excluded - known_ids)
        if unknown:
            raise ClarificationError(
                "ECHEL-CLARIFY-QUESTION-UNKNOWN",
                "excluded_question_ids",
                f"unknown question identifier {unknown[0]!r}",
                "use an identifier returned by clarification/v1",
            )

        unresolved = tuple(gap.claim_kind for gap in PROBLEM_GAPS if gap.claim_kind not in active)
        selected = next(
            (
                gap
                for gap in PROBLEM_GAPS
                if gap.claim_kind not in active and gap.id not in excluded
            ),
            None,
        )
        idea = raw_ideas[0].record
        question = (
            ClarificationQuestion(
                selected.id,
                selected.prompt,
                selected.reason,
                selected.claim_kind,
                (f"{idea['id']}@{idea['revision']}",),
            )
            if selected
            else None
        )
        return ClarificationResult(str(project[0].record["id"]), "problem", question, unresolved)
