import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "save-to-kb" / "scripts" / "find_related.py"


def run(args, kb_root):
    env = dict(os.environ)
    if kb_root is None:
        env.pop("KB_ROOT", None)
    else:
        env["KB_ROOT"] = kb_root
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, env=env,
    )


class TestFindRelated(unittest.TestCase):
    def test_no_match_prints_no_match(self):
        with tempfile.TemporaryDirectory() as d:
            r = run(["zqxnomatch"], d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("NO_MATCH", r.stdout)

    def test_hit_lists_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "AG-01-rag.md").write_text("# RAG workflow\n", encoding="utf-8")
            r = run(["rag"], d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("AG-01-rag.md", r.stdout)

    def test_missing_kb_root_errors(self):
        r = run(["anything"], "")  # KB_ROOT set empty -> treated as unset
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
