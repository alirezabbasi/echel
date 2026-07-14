from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from echel.context.compiler import ContextCompiler
from echel.model.records import Finding
from echel.runtimes.base import RunRequest
from echel.runtimes.hermes import HermesRuntime
from echel.storage.files import FileStore, StoreError
from echel.workflow import LifecycleBlocked, WorkflowService


class StorageTests(unittest.TestCase):
    def test_initialization_creates_only_minimal_state(self):
        with tempfile.TemporaryDirectory() as directory:
            store = FileStore(Path(directory))
            project = store.initialize("Example", "A raw idea")

            self.assertEqual("idea", project.current_stage)
            self.assertEqual([], store.records())
            self.assertTrue((Path(directory) / ".echel" / "project.json").exists())
            self.assertFalse((Path(directory) / ".echel" / "architecture").exists())

    def test_reinitialization_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = FileStore(Path(directory))
            store.initialize("Example", "A raw idea")
            with self.assertRaises(StoreError):
                store.initialize("Again", "Another idea")


class LifecycleTests(unittest.TestCase):
    def test_knowledge_accumulates_progressively(self):
        with tempfile.TemporaryDirectory() as directory:
            store = FileStore(Path(directory))
            store.initialize("Example", "A raw idea")
            workflow = WorkflowService(store)

            self.assertEqual("problem", workflow.advance())
            with self.assertRaises(LifecycleBlocked):
                workflow.advance()

            workflow.add_knowledge("problem", "Schedulers lose hours to no-shows.", status="accepted")
            workflow.add_knowledge("user", "Small-clinic schedulers.", status="accepted")
            self.assertEqual([], workflow.status()["missing"])
            self.assertEqual("vision", workflow.advance())

    def test_stage_can_be_revisited_without_moving_project_backwards(self):
        with tempfile.TemporaryDirectory() as directory:
            store = FileStore(Path(directory))
            store.initialize("Example", "A raw idea")
            workflow = WorkflowService(store)
            workflow.advance()
            record = workflow.add_knowledge("observation", "New evidence", stage="idea", status="validated")
            self.assertEqual("idea", record.stage)
            self.assertEqual("problem", store.load_project().current_stage)


class ContextTests(unittest.TestCase):
    def test_context_contains_only_explicitly_related_knowledge(self):
        with tempfile.TemporaryDirectory() as directory:
            store = FileStore(Path(directory))
            store.initialize("Example", "A raw idea")
            workflow = WorkflowService(store)
            included = workflow.add_knowledge("requirement", "Users can accept invitations.", status="accepted")
            excluded = workflow.add_knowledge("requirement", "Administrators can export invoices.", status="accepted")
            work = workflow.add_work(
                "Invitation acceptance",
                "Implement acceptance without premature authorization.",
                [included.id],
                ["An invited user remains unauthorized until acceptance."],
                ["python3 -m unittest"],
            )
            finding = Finding(store.next_id("FIND"), "contradiction", "Existing middleware grants access early.", affects=[included.id])
            store.put("findings", finding.to_dict())

            context = ContextCompiler(store).compile(work.id)
            text = context.as_text()

            self.assertIn(included.statement, text)
            self.assertNotIn(excluded.statement, text)
            self.assertIn(finding.statement, text)
            self.assertEqual(64, len(context.digest()))


class HermesAdapterTests(unittest.TestCase):
    def test_adapter_builds_a_provider_independent_request(self):
        runtime = HermesRuntime("hermes-test")
        request = RunRequest("bounded context", Path("/tmp"), "model-x", ("file",))
        self.assertEqual(
            ["hermes-test", "chat", "--model", "model-x", "--toolsets", "file", "-q", "bounded context"],
            runtime.command(request),
        )


if __name__ == "__main__":
    unittest.main()
