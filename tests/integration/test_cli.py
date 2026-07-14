from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
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

    def test_idea_to_verified_work_journey(self):
        with tempfile.TemporaryDirectory() as directory:
            root = str(Path(directory))
            code, _, _ = self.invoke("--root", root, "init", "Example", "--idea", "Reduce no-shows")
            self.assertEqual(0, code)
            self.assertEqual(0, self.invoke("--root", root, "advance")[0])
            self.assertEqual(0, self.invoke("--root", root, "add", "problem", "Clinics lose time", "--status", "accepted")[0])
            self.assertEqual(0, self.invoke("--root", root, "add", "user", "Clinic schedulers", "--status", "accepted")[0])
            self.assertEqual(0, self.invoke("--root", root, "advance")[0])

            code, output, _ = self.invoke(
                "--root", root, "work", "Test reminder", "--objective", "Run the smallest experiment",
                "--relates-to", "CLM-001", "--accept", "Experiment reports a result", "--verify", "python3 --version",
            )
            self.assertEqual(0, code)
            self.assertIn("WORK-001", output)

            code, output, _ = self.invoke("--root", root, "context", "WORK-001")
            self.assertEqual(0, code)
            self.assertIn("Clinics lose time", output)
            self.assertNotIn("Clinic schedulers", output)

            code, output, _ = self.invoke("--root", root, "run", "WORK-001")
            self.assertEqual(0, code)
            self.assertIn("hermes", output)
            self.assertTrue((Path(directory) / ".echel" / "runs" / "RUN-001.json").exists())

            code, output, _ = self.invoke("--root", root, "verify", "WORK-001")
            self.assertEqual(0, code)
            self.assertIn('"exit_code": 0', output)
            self.assertTrue((Path(directory) / ".echel" / "evidence" / "EVID-001.json").exists())


if __name__ == "__main__":
    unittest.main()
