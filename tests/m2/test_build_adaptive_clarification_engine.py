from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from echel.cli.main import main
from echel.initialization import IdeaInitializationService
from echel.methodology.clarification import ClarificationError, ClarificationService
from echel.storage import CanonicalRecordStore, CanonicalRepository, RecordExpectation


NOW = datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)


class AdaptiveClarificationTests(unittest.TestCase):
    def initialized(self, directory: str) -> Path:
        workspace = Path(directory)
        (workspace / ".git").mkdir()
        service = IdeaInitializationService(clock=lambda: NOW)
        service.apply(service.preview(workspace, "Shift Helper", "An app for volunteer shifts", "user:builder"))
        return workspace

    @staticmethod
    def add_claim(workspace: Path, identifier: str, kind: str, status: str = "proposed") -> None:
        store = CanonicalRecordStore(CanonicalRepository.discover(workspace))
        stamp = "2026-07-15T18:00:00Z"
        record = {
                "schema_version": 1,
                "record_type": "claim",
                "id": identifier,
                "revision": 1,
                "created_at": stamp,
                "updated_at": stamp,
                "provenance": {"actor": "user:builder", "origin": "test", "method": "human"},
                "kind": kind,
                "stage": "problem",
                "statement": f"Known {kind}",
                "status": status,
                "confidence": 0.5,
            }
        if status == "rejected":
            record["authority"] = {
                "action": "rejected",
                "actor": "user:builder",
                "actor_kind": "human",
                "capability": "knowledge:decide",
                "rationale": "Not supported by the current understanding.",
                "decided_at": stamp,
                "proposal_revision": 1,
            }
        store.write(
            record,
            RecordExpectation.absent(),
        )

    def test_first_question_targets_the_first_material_gap_and_explains_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = ClarificationService().inspect(self.initialized(directory))
            output = result.to_dict()
            self.assertEqual("clarification/v1", output["contract"])
            self.assertEqual("problem.affected-actor", output["question"]["id"])
            self.assertIn("cannot be evaluated", output["question"]["reason"])
            self.assertEqual(["claim:shift-helper-idea@1"], output["question"]["basis"])
            self.assertEqual("none", output["mutation"])

    def test_existing_knowledge_adapts_selection_and_rejected_claim_does_not_fill_gap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = self.initialized(directory)
            self.add_claim(workspace, "claim:actor", "affected-actor")
            self.add_claim(workspace, "claim:rejected-problem", "problem", "rejected")
            result = ClarificationService().inspect(workspace)
            self.assertEqual("problem.current-problem", result.question.id)
            self.assertNotIn("affected-actor", result.unresolved_kinds)
            self.assertIn("problem", result.unresolved_kinds)

    def test_exclusions_avoid_repetition_without_persisting_session_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = self.initialized(directory)
            first = ClarificationService().inspect(workspace)
            second = ClarificationService().inspect(workspace, [first.question.id])
            recovered = ClarificationService().inspect(workspace)
            self.assertEqual("problem.current-problem", second.question.id)
            self.assertEqual(first.question.id, recovered.question.id)
            self.assertEqual(1, len(CanonicalRecordStore(CanonicalRepository.discover(workspace)).scan("claim")))

    def test_complete_or_fully_deferred_result_has_no_question(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = self.initialized(directory)
            ids = ["problem.affected-actor", "problem.current-problem", "problem.context", "problem.observation"]
            result = ClarificationService().inspect(workspace, ids)
            self.assertIsNone(result.question)
            self.assertEqual(4, len(result.unresolved_kinds))
            self.assertIn("deferred", result.to_dict()["next_action"].lower())

    def test_invalid_project_and_unknown_exclusion_are_actionable_and_non_mutating(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / ".git").mkdir()
            with self.assertRaises(ClarificationError) as missing:
                ClarificationService().inspect(workspace)
            self.assertEqual("ECHEL-CLARIFY-PROJECT-INVALID", missing.exception.code)

        with tempfile.TemporaryDirectory() as directory:
            workspace = self.initialized(directory)
            with self.assertRaises(ClarificationError) as unknown:
                ClarificationService().inspect(workspace, ["invented"])
            self.assertEqual("ECHEL-CLARIFY-QUESTION-UNKNOWN", unknown.exception.code)

    def test_cli_json_contract_and_human_explanation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = self.initialized(directory)
            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(["--root", str(workspace), "--json", "clarify"])
            self.assertEqual(0, code)
            self.assertEqual("problem.affected-actor", json.loads(stdout.getvalue())["question"]["id"])

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(["--root", str(workspace), "clarify"])
            self.assertEqual(0, code)
            self.assertIn("Why:", stdout.getvalue())
            self.assertIn("Question ID:", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
