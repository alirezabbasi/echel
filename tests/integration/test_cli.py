from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from echel.cli.main import main


class CliJourneyTests(unittest.TestCase):
    def invoke(self, *args: str) -> tuple[int, str, str]:
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_idea_initialization_starts_with_only_truthful_minimum(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / ".git").mkdir()
            root = str(workspace)
            code, output, _ = self.invoke(
                "--root", root, "--json", "init", "Example", "--mode", "idea",
                "--idea", "Reduce no-shows", "--owner", "user:builder",
            )
            self.assertEqual(0, code)
            result = json.loads(output)
            self.assertEqual(2, result["records_created"])
            self.assertEqual(
                {"project.json", "records/claims/example-idea.json"},
                {
                    path.relative_to(workspace / ".echel").as_posix()
                    for path in (workspace / ".echel").rglob("*.json")
                },
            )


if __name__ == "__main__":
    unittest.main()
