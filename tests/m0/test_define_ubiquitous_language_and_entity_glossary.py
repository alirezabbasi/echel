from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
GLOSSARY = ROOT / "docs" / "product" / "ubiquitous-language.md"


class UbiquitousLanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = GLOSSARY.read_text(encoding="utf-8")

    def test_glossary_is_an_accepted_governing_contract(self):
        self.assertIn("Status: accepted", self.text)
        self.assertIn("naming contract for public documentation", self.text)
        self.assertIn("A public term has exactly one meaning", self.text)

    def test_echel_and_hermes_have_distinct_authority(self):
        echel = self._definition("Echel")
        hermes = self._definition("Hermes")
        self.assertIn("does not execute model or tool loops", echel)
        self.assertIn("does not own product truth", hermes)

    def test_knowledge_states_and_derived_data_are_distinct(self):
        for term in (
            "canonical record",
            "provenance",
            "evidence",
            "fact",
            "observation",
            "inference",
            "assumption",
            "hypothesis",
            "decision",
            "finding",
            "proposal",
            "projection",
            "index",
            "runtime memory",
        ):
            self.assertRegex(self.text, rf"\| \*\*{re.escape(term)}\*\* \|")

    def test_both_entry_modes_converge_on_shared_execution_terms(self):
        for term in (
            "greenfield",
            "brownfield",
            "baseline",
            "work item",
            "task specification",
            "context bundle",
            "run",
            "verification",
        ):
            self.assertRegex(self.text, rf"\| \*\*{re.escape(term)}\*\* \|")
        self.assertIn("Both journeys produce the same task specification", self.text)

    def test_overloaded_v1_terms_are_retired_or_mapped(self):
        for old_term in (
            "wiki",
            "product graph",
            "memory kernel",
            "work packet",
            "proof pack",
            "readiness report",
            "cockpit",
            "virtual delivery team",
            "AI-native software engineering OS",
        ):
            self.assertIn(f"`{old_term}", self.text)
        self.assertIn("public v2 output must use the v2 term", self.text)

    def test_glossary_defines_change_governance(self):
        self.assertIn("## Governance", self.text)
        self.assertIn("silently redefining an existing term is prohibited", self.text)
        self.assertIn("conflict with this glossary create a finding", self.text)

    @classmethod
    def _definition(cls, term: str) -> str:
        match = re.search(
            rf"^\| \*\*{re.escape(term)}\*\* \| (.+) \|$",
            cls.text,
            flags=re.MULTILINE,
        )
        if match is None:
            raise AssertionError(f"missing glossary definition for {term}")
        return match.group(1)


if __name__ == "__main__":
    unittest.main()
