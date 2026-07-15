from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from echel.cli.main import main
from echel.initialization import IdeaInitializationService, InitializationError
from echel.storage import CanonicalRecordStore, CanonicalRepository


NOW = datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)


class IdeaInitializationTests(unittest.TestCase):
    def workspace(self, directory: str) -> Path:
        workspace = Path(directory)
        (workspace / ".git").mkdir()
        return workspace

    @staticmethod
    def service() -> IdeaInitializationService:
        return IdeaInitializationService(clock=lambda: NOW)

    def test_preview_explains_exact_minimum_without_filesystem_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = self.workspace(directory)
            plan = self.service().preview(
                workspace,
                "Shift Helper",
                "Help coordinators avoid unfilled shifts.",
                "user:builder",
                "prototype",
                {"locale": "en"},
            )

            explanation = plan.to_dict()
            self.assertEqual("idea-init/v1", explanation["contract"])
            self.assertEqual(["project:shift-helper", "claim:shift-helper-idea"], explanation["records"])
            self.assertEqual("user:builder", explanation["owner"])
            self.assertEqual({"locale": "en"}, explanation["config"])
            self.assertEqual("preview", explanation["mutation"])
            self.assertIn("define the problem", explanation["next_action"])
            self.assertFalse((workspace / ".echel").exists())

    def test_apply_creates_only_project_identity_and_raw_idea_claim(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = self.workspace(directory)
            service = self.service()
            result = service.apply(
                service.preview(
                    workspace,
                    "Shift Helper",
                    "Help coordinators avoid unfilled shifts.",
                    "user:builder",
                    "product",
                    {"locale": "en", "research": "deferred"},
                )
            )

            repository = CanonicalRepository.discover(workspace)
            store = CanonicalRecordStore(repository)
            project = store.load("project", "project:shift-helper").record
            idea = store.load("claim", "claim:shift-helper-idea").record
            metadata = project["extensions"]["dev.echel.initialization"]
            self.assertEqual("idea", project["mode"])
            self.assertEqual("idea", project["maturity"])
            self.assertEqual("product", project["profile"])
            self.assertEqual("user:builder", metadata["owner"])
            self.assertEqual({"locale": "en", "research": "deferred"}, metadata["config"])
            self.assertEqual("raw-idea", idea["kind"])
            self.assertEqual("proposed", idea["status"])
            self.assertEqual("user:builder", idea["provenance"]["actor"])
            self.assertEqual(2, result.to_dict()["records_created"])
            self.assertEqual(
                {"project.json", "records/claims/shift-helper-idea.json"},
                {
                    path.relative_to(repository.root).as_posix()
                    for path in repository.root.rglob("*.json")
                },
            )
            for collection in repository.records.iterdir():
                if collection.name != "claims":
                    self.assertEqual([], list(collection.iterdir()), collection.name)
            for forbidden in ("policy.json", "README.md", "architecture", "roadmap", "tasks"):
                self.assertFalse((repository.root / forbidden).exists())

    def test_all_profiles_are_explicit_but_do_not_change_initial_shape(self) -> None:
        for profile in ("prototype", "product", "production", "regulated"):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as directory:
                workspace = self.workspace(directory)
                service = self.service()
                service.apply(
                    service.preview(workspace, "Demo", "A raw idea", "user:owner", profile)
                )
                store = CanonicalRecordStore(CanonicalRepository.discover(workspace))
                self.assertEqual(profile, store.load("project", "project:demo").record["profile"])
                self.assertEqual(1, len(store.scan("claim")))

    def test_invalid_inputs_secrets_and_config_leave_no_partial_state(self) -> None:
        cases = (
            {"name": "", "idea": "idea", "owner": "user:owner"},
            {"name": "Demo", "idea": "", "owner": "user:owner"},
            {"name": "Demo", "idea": "idea", "owner": "agent:hermes"},
            {"name": "Demo", "idea": "use sk-abcdefghijklmnopqrstuvwxyz", "owner": "user:owner"},
            {"name": "Demo", "idea": "idea", "owner": "user:owner", "config": {"api_key": "x"}},
        )
        for values in cases:
            with self.subTest(values=values), tempfile.TemporaryDirectory() as directory:
                workspace = self.workspace(directory)
                with self.assertRaises(InitializationError):
                    self.service().preview(workspace, **values)
                self.assertFalse((workspace / ".echel").exists())

    def test_publication_interruption_removes_staged_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = self.workspace(directory)
            service = self.service()
            plan = service.preview(workspace, "Demo", "A raw idea", "user:owner")
            real_replace = os.replace

            def interrupt(source, destination):
                if Path(destination) == workspace / ".echel":
                    raise OSError("interrupted before publication")
                return real_replace(source, destination)

            with patch("echel.initialization.os.replace", side_effect=interrupt):
                with self.assertRaises(InitializationError) as caught:
                    service.apply(plan)

            self.assertEqual("ECHEL-INIT-APPLY", caught.exception.code)
            self.assertFalse((workspace / ".echel").exists())
            self.assertEqual([], list(workspace.glob(".echel.init-*.tmp")))

    def test_stale_or_tampered_plan_cannot_replace_an_existing_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = self.workspace(directory)
            service = self.service()
            first = service.preview(workspace, "First", "First idea", "user:owner")
            stale = service.preview(workspace, "Second", "Second idea", "user:owner")
            service.apply(first)
            with self.assertRaises(InitializationError) as exists:
                service.apply(stale)
            self.assertEqual("ECHEL-INIT-EXISTS", exists.exception.code)

        with tempfile.TemporaryDirectory() as directory:
            workspace = self.workspace(directory)
            plan = self.service().preview(workspace, "Demo", "Idea", "user:owner")
            plan.idea["statement"] = "tampered"
            with self.assertRaises(InitializationError) as tampered:
                self.service().apply(plan)
            self.assertEqual("ECHEL-INIT-PLAN-INVALID", tampered.exception.code)
            self.assertFalse((workspace / ".echel").exists())

    def test_cli_json_dry_run_apply_and_structured_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = self.workspace(directory)
            arguments = [
                "--root", str(workspace), "--json", "init", "Demo", "--mode", "idea",
                "--idea", "A raw idea", "--owner", "user:owner", "--config", "locale=en",
            ]
            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main([*arguments, "--dry-run"])
            self.assertEqual(0, code)
            self.assertEqual("preview", json.loads(stdout.getvalue())["mutation"])
            self.assertFalse((workspace / ".echel").exists())

            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(arguments)
            self.assertEqual(0, code)
            self.assertEqual("applied", json.loads(stdout.getvalue())["mutation"])

            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(arguments)
            self.assertEqual(2, code)
            self.assertEqual("ECHEL-INIT-EXISTS", json.loads(stderr.getvalue())["error"]["code"])


if __name__ == "__main__":
    unittest.main()
