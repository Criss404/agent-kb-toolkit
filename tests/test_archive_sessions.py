import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "archive-sessions" / "scripts" / "archive_sessions.py"


def load_module():
    spec = importlib.util.spec_from_file_location("archive_sessions", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestArchiveSessions(unittest.TestCase):
    def test_list_registers_adapters(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--list"],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        for name in ("qoder", "claude", "opencode"):
            self.assertIn(name, r.stdout)

    def test_slugify_strips_tags_and_spaces(self):
        m = load_module()
        self.assertEqual(m.slugify("<tag>hello world</tag>"), "hello-world")

    def test_ts_to_str_epoch_is_utc(self):
        m = load_module()
        self.assertTrue(m.ts_to_str(0).startswith("1970-01-01"))


if __name__ == "__main__":
    unittest.main()
