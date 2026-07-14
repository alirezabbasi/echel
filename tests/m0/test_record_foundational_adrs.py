from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
DECISIONS = ROOT / "docs" / "decisions"
INDEX = DECISIONS / "README.md"


class FoundationalAdrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = INDEX.read_text(encoding="utf-8")
        cls.files = sorted(DECISIONS.glob("[0-9][0-9][0-9][0-9]-*.md"))
        cls.documents = {path.name: path.read_text(encoding="utf-8") for path in cls.files}

    def test_exact_foundational_decisions_are_indexed_and_accepted(self):
        expected = {
            "0001-repository-owned-canonical-records.md",
            "0002-disposable-projections-and-indexes.md",
            "0003-runtime-neutral-execution-protocol.md",
            "0004-local-first-core-and-external-authority.md",
            "0005-versioned-isolated-extension-contracts.md",
        }
        self.assertEqual(set(self.documents), expected)
        for filename, text in self.documents.items():
            with self.subTest(adr=filename):
                self.assertIn("- Status: Accepted", text)
                self.assertIn("- Date: 2026-07-15", text)
                self.assertIn(filename, self.index)

    def test_each_adr_records_reasoning_recovery_and_replacement(self):
        for filename, text in self.documents.items():
            with self.subTest(adr=filename):
                for heading in (
                    "## Context",
                    "## Decision",
                    "## Consequences",
                    "## Failure and recovery",
                    "## Alternatives considered",
                    "## Replacement conditions",
                ):
                    self.assertIn(heading, text)

    def test_storage_has_one_repository_owned_source_of_truth(self):
        text = self.documents["0001-repository-owned-canonical-records.md"]
        self.assertIn("one canonical record identity", text)
        self.assertIn("Git owns file and repository history", text)
        self.assertIn("SQLite as the canonical store", text)
        self.assertIn("without a database server or hosted Echel account", text)

    def test_projections_and_indexes_are_disposable(self):
        text = self.documents["0002-disposable-projections-and-indexes.md"]
        self.assertIn("disposable projections", text)
        self.assertIn("never required for canonical recovery", text)
        self.assertIn("rebuilds them deterministically", text)
        self.assertIn("graph view is not", text)

    def test_runtime_protocol_keeps_hermes_out_of_domain(self):
        text = self.documents["0003-runtime-neutral-execution-protocol.md"]
        self.assertIn("runtime-neutral protocol owned by Echel", text)
        self.assertIn("A runtime owns capability discovery", text)
        self.assertIn("Domain and application services never import Hermes", text)
        self.assertIn("fail before side effects", text)

    def test_local_first_preserves_external_authority(self):
        text = self.documents["0004-local-first-core-and-external-authority.md"]
        self.assertIn("local-first and useful offline", text)
        self.assertIn("External integrations are optional adapters", text)
        self.assertIn("remain authoritative for their raw state", text)
        self.assertIn("Network access is denied by default", text)

    def test_extensions_are_typed_isolated_and_non_authoritative(self):
        text = self.documents["0005-versioned-isolated-extension-contracts.md"]
        self.assertIn("capability-specific, versioned contracts", text)
        self.assertIn("deny-by-default permissions", text)
        self.assertIn("write canonical records directly", text)
        self.assertIn("project unreadable when the extension is absent", text)
        self.assertIn("does not promise arbitrary third-party in-process Python plugins", text)

    def test_adr_numbers_titles_and_index_links_are_consistent(self):
        for path in self.files:
            number = path.name[:4]
            first_line = self.documents[path.name].splitlines()[0]
            self.assertRegex(first_line, rf"^# ADR-{re.escape(number)}: .+$")
            self.assertEqual(len(re.findall(rf"\[ADR-{number}\]", self.index)), 1)


if __name__ == "__main__":
    unittest.main()
