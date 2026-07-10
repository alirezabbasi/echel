from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import health_check


class HealthCheckTests(unittest.TestCase):
    def test_health_check_reports_ok(self):
        self.assertEqual(health_check()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
