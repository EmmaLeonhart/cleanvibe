"""`cleanvibe refresh --migrate`: a pre-split (<= 2.0.8) CLAUDE.md is split into
the project's own CLAUDE.md plus the shipped RULES.md. Nothing is lost: the old
file is kept, project sections stay, and real local edits are flagged.
Fixtures are the 2.0.8 generator's own output for a demo project."""

import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

os.environ.setdefault("CLEANVIBE_CLAUDE_CONFIG", os.path.join(
    tempfile.mkdtemp(), "claude.json"))

from cleanvibe import doctor, project, templates  # noqa: E402
from cleanvibe.cli import main  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _old_project(fixture="v2_0_8_CLAUDE_chosen.md", name="demo-project", auto=False):
    """A fresh project whose CLAUDE.md is replaced by the 2.0.8 one."""
    proj = Path(tempfile.mkdtemp()) / name
    with redirect_stdout(io.StringIO()):
        project.new_project(proj, auto_named=auto, no_claude=True)
    shutil.copyfile(FIXTURES / fixture, proj / "CLAUDE.md")
    (proj / templates.V2_RULES_PATH).unlink()
    return proj


class TestMigrate(unittest.TestCase):
    def test_untouched_2_0_8_project_migrates_with_nothing_flagged(self):
        for fixture, name, auto in (("v2_0_8_CLAUDE_chosen.md", "demo-project", False),
                                    ("v2_0_8_CLAUDE_auto.md", "golden-swift-otter", True)):
            with self.subTest(fixture=fixture):
                proj = _old_project(fixture, name, auto)
                old = (proj / "CLAUDE.md").read_text(encoding="utf-8")
                result = project.migrate_project(proj)
                self.assertEqual(result["differing"], [])
                self.assertEqual(len(result["moved"]), 10)
                new = (proj / "CLAUDE.md").read_text(encoding="utf-8")
                fresh = templates.v2_claude_md(name, auto_named=auto)
                strip_date = lambda t: t.split("# currentDate")[0]
                self.assertEqual(strip_date(new), strip_date(fresh))
                self.assertEqual((proj / project.MIGRATION_BACKUP).read_text(encoding="utf-8"), old)
                self.assertEqual(doctor.run_checks(proj), [])

    def test_project_sections_and_check_date_are_kept(self):
        proj = _old_project()
        claude = proj / "CLAUDE.md"
        text = claude.read_text(encoding="utf-8")
        text = text.replace("- **Last cleanvibe update check:** `never`",
                            "- **Last cleanvibe update check:** `2026-11-01`")
        text = text.replace("## Publishing", "## This project's conventions\n- Use tabs.\n\n## Publishing")
        claude.write_text(text, encoding="utf-8")
        project.migrate_project(proj)
        new = claude.read_text(encoding="utf-8")
        self.assertIn("## This project's conventions\n- Use tabs.", new)
        self.assertIn("`2026-11-01`", new)
        self.assertNotIn("## Mode check", new)

    def test_a_locally_edited_rule_section_is_flagged(self):
        proj = _old_project()
        claude = proj / "CLAUDE.md"
        claude.write_text(claude.read_text(encoding="utf-8").replace(
            "## Mode check\n", "## Mode check\nAlso ping the team channel.\n"), encoding="utf-8")
        result = project.migrate_project(proj)
        self.assertEqual(result["differing"], ["## Mode check"])
        self.assertIn("Also ping the team channel.",
                      (proj / project.MIGRATION_BACKUP).read_text(encoding="utf-8"))

    def test_already_split_project_is_left_alone(self):
        proj = _old_project()
        project.migrate_project(proj)
        before = (proj / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertTrue(project.migrate_project(proj)["already"])
        self.assertEqual((proj / "CLAUDE.md").read_text(encoding="utf-8"), before)

    def test_cli_dry_run_writes_nothing_then_migrates(self):
        proj = _old_project()
        old = (proj / "CLAUDE.md").read_text(encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit) as e:
            main(["refresh", str(proj), "--migrate", "--dry-run"])
        self.assertEqual(e.exception.code, 0)
        self.assertIn("Would update CLAUDE.md: 10 shipped section(s) moved", out.getvalue())
        self.assertEqual((proj / "CLAUDE.md").read_text(encoding="utf-8"), old)
        self.assertFalse((proj / templates.V2_RULES_PATH).exists())
        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            main(["refresh", str(proj), "--migrate"])
        self.assertTrue((proj / templates.V2_RULES_PATH).exists())
        self.assertEqual(doctor.run_checks(proj), [])


if __name__ == "__main__":
    unittest.main()
