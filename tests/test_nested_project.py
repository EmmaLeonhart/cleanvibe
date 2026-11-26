"""`cleanvibe new` warns about CLAUDE.md files above the new project."""
import tempfile
import unittest
from pathlib import Path

from cleanvibe.project import parent_claude_mds


class NestedProjectTests(unittest.TestCase):
    def test_finds_a_claude_md_above(self):
        with tempfile.TemporaryDirectory() as d:
            outer = Path(d) / "outer"
            outer.mkdir()
            (outer / "CLAUDE.md").write_text("@.claude/cleanvibe/RULES.md\n", encoding="utf-8")
            found = parent_claude_mds(outer / "scratch" / "inner")
            self.assertIn((outer / "CLAUDE.md").resolve(), [p.resolve() for p in found])

    def test_nothing_above_a_clean_folder(self):
        with tempfile.TemporaryDirectory() as d:
            inner = Path(d) / "a" / "b"
            found = [p for p in parent_claude_mds(inner) if Path(d).resolve() in p.resolve().parents or p.resolve().parent == Path(d).resolve()]
            self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
