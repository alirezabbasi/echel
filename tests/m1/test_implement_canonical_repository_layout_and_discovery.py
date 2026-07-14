from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from echel.storage import CanonicalRepository, RECORD_COLLECTIONS, RepositoryError


class CanonicalRepositoryLayoutTests(unittest.TestCase):
    def test_create_builds_only_the_canonical_directory_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / ".git").mkdir()
            repository = CanonicalRepository.create(workspace)

            self.assertEqual(workspace.resolve(), repository.workspace)
            self.assertEqual(set(RECORD_COLLECTIONS), {path.name for path in repository.records.iterdir()})
            self.assertTrue((repository.root / "cache").is_dir())
            self.assertFalse((repository.root / "project.json").exists())
            self.assertFalse((repository.root / "artifacts").exists())

    def test_discovery_from_nested_directory_and_file_returns_git_root_store(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / ".git").mkdir()
            created = CanonicalRepository.create(workspace)
            nested = workspace / "src" / "package"
            nested.mkdir(parents=True)
            source = nested / "module.py"
            source.touch()

            self.assertEqual(created, CanonicalRepository.discover(nested))
            self.assertEqual(created, CanonicalRepository.discover(source))

    def test_git_worktree_marker_file_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / ".git").write_text("gitdir: /tmp/example\n")
            created = CanonicalRepository.create(workspace)
            self.assertEqual(created, CanonicalRepository.discover(workspace))

    def test_discovery_never_adopts_echel_state_above_git_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outer = Path(directory)
            (outer / ".echel").mkdir()
            workspace = outer / "product"
            nested = workspace / "src"
            nested.mkdir(parents=True)
            (workspace / ".git").mkdir()

            with self.assertRaises(RepositoryError) as caught:
                CanonicalRepository.discover(nested)
            self.assertEqual("ECHEL-PROJECT-NOT-FOUND", caught.exception.code)
            self.assertEqual(workspace / ".echel", caught.exception.path)

    def test_symlinked_store_or_collection_cannot_escape_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside_dir:
            workspace = Path(directory)
            outside = Path(outside_dir)
            (workspace / ".git").mkdir()
            (workspace / ".echel").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(RepositoryError) as caught:
                CanonicalRepository.discover(workspace)
            self.assertEqual("ECHEL-REPOSITORY-ESCAPE", caught.exception.code)

    def test_missing_or_malformed_repository_has_actionable_error(self) -> None:
        with self.assertRaises(RepositoryError) as caught:
            CanonicalRepository.discover(Path("/echel-no-repository-E2-013"))
        self.assertEqual("ECHEL-REPOSITORY-NOT-FOUND", caught.exception.code)

        with tempfile.TemporaryDirectory() as directory:
            location = Path(directory)
            (location / ".git").mkdir()
            (location / ".echel" / "records").mkdir(parents=True)
            with self.assertRaises(RepositoryError) as caught:
                CanonicalRepository.discover(location)
            self.assertEqual("ECHEL-LAYOUT-INVALID", caught.exception.code)

    def test_create_requires_root_and_rejects_reinitialization(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            nested = workspace / "nested"
            nested.mkdir()
            (workspace / ".git").mkdir()
            with self.assertRaises(RepositoryError) as caught:
                CanonicalRepository.create(nested)
            self.assertEqual("ECHEL-INIT-NOT-ROOT", caught.exception.code)
            CanonicalRepository.create(workspace)
            with self.assertRaises(RepositoryError) as caught:
                CanonicalRepository.create(workspace)
            self.assertEqual("ECHEL-PROJECT-EXISTS", caught.exception.code)

    def test_failed_creation_removes_temporary_layout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / ".git").mkdir()
            with patch.object(Path, "replace", side_effect=OSError("interrupted")):
                with self.assertRaises(RepositoryError) as caught:
                    CanonicalRepository.create(workspace)
            self.assertEqual("ECHEL-LAYOUT-CREATE", caught.exception.code)
            self.assertFalse((workspace / ".echel").exists())
            self.assertEqual([], list(workspace.glob(".echel.tmp-*")))

    def test_collection_lookup_rejects_unknown_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / ".git").mkdir()
            repository = CanonicalRepository.create(workspace)
            with self.assertRaises(RepositoryError) as caught:
                repository.collection("transcripts")
            self.assertEqual("ECHEL-COLLECTION-UNKNOWN", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
