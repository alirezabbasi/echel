from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "product" / "product-contract.md"


class ProductContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CONTRACT.read_text(encoding="utf-8")

    def test_contract_defines_both_entry_modes_and_convergence(self):
        self.assertIn("## Entry mode A — Greenfield product creation", self.text)
        self.assertIn("## Entry mode B — Existing product evolution", self.text)
        self.assertIn("## Shared lifecycle", self.text)
        self.assertIn("same canonical entities", self.text)

    def test_contract_defines_audiences_scope_and_non_goals(self):
        for heading in (
            "## Audiences and jobs",
            "## Echel 2 core scope",
            "## Explicit non-goals for Echel 2",
            "## Initial success criteria",
        ):
            self.assertIn(heading, self.text)

    def test_contract_separates_echel_hermes_and_external_authority(self):
        for heading in (
            "### Echel is authoritative for",
            "### Hermes is authoritative for",
            "### External engineering systems are authoritative for",
        ):
            self.assertIn(heading, self.text)
        self.assertIn("Hermes memory and agent output are not product truth", self.text)

    def test_contract_distinguishes_evidence_from_assumptions(self):
        self.assertIn("### Available evidence", self.text)
        self.assertIn("### Unvalidated assumptions", self.text)
        self.assertIn("must not be presented as market facts", self.text)

    def test_contract_requires_human_approval(self):
        self.assertIn("Status: accepted", self.text)
        self.assertIn("Repository owner | Approved", self.text)
        self.assertIn("Future changes require explicit maintainer review", self.text)


if __name__ == "__main__":
    unittest.main()
