"""Tests for the cleanvibe 2 command line: the no-argument default, `new
[NAME]`, `legacy`, and the moved 1.x names. Launching is mocked or skipped.
"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from cleanvibe import cli, project


class _InTempDir(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.old = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.old)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        with redirect_stdout(out), redirect_stderr(err):
            try:
                cli.main(list(argv))
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()


class TestDefault(_InTempDir):
    def test_outside_a_project_creates_an_auto_named_one(self):
        code, _, _ = self.run_cli("--no-claude")
        self.assertEqual(code, 0)
        made = [p for p in self.tmp.iterdir() if p.is_dir()]
        self.assertEqual(len(made), 1)
        self.assertRegex(made[0].name, r"^cleanvibe-\d{4}-\d{2}-\d{2}$")
        self.assertTrue(project.is_cleanvibe_repo(made[0]))

    def test_inside_a_project_opens_it_instead(self):
        self.run_cli("new", "proj", "--no-claude")
        os.chdir(self.tmp / "proj")
        with mock.patch.object(cli, "open_project") as open_project, \
                mock.patch.object(cli, "new_project") as new_project:
            self.run_cli()
        open_project.assert_called_once()
        new_project.assert_not_called()

    def test_default_launches_the_first_session(self):
        with mock.patch.object(project, "_launch_claude") as launch:
            self.run_cli()
        args, kwargs = launch.call_args
        self.assertIn("first ever session", args[1])
        self.assertIn("without giving a name", args[1])
        self.assertTrue(kwargs["remote_control"])


class TestNew(_InTempDir):
    def test_named(self):
        code, _, _ = self.run_cli("new", "oolong", "--no-claude")
        self.assertEqual(code, 0)
        self.assertTrue((self.tmp / "oolong" / ".cleanvibe.json").is_file())

    def test_unnamed_is_auto_named(self):
        self.run_cli("new", "--no-claude")
        auto = next(self.tmp.glob("cleanvibe-*"))
        self.assertIn("created without a name", (auto / "INTENT.md").read_text(encoding="utf-8"))

    def test_existing_project_is_opened_not_overwritten(self):
        self.run_cli("new", "oolong", "--no-claude")
        intent = self.tmp / "oolong" / "INTENT.md"
        intent.write_text("edited", encoding="utf-8")
        code, out, _ = self.run_cli("new", "oolong", "--no-claude")
        self.assertEqual(code, 0)
        self.assertIn("already a cleanvibe project", out)
        self.assertEqual(intent.read_text(encoding="utf-8"), "edited")

    def test_non_empty_non_project_is_refused(self):
        (self.tmp / "stuff").mkdir()
        (self.tmp / "stuff" / "notes.txt").write_text("mine", encoding="utf-8")
        code, _, err = self.run_cli("new", "stuff", "--no-claude")
        self.assertEqual(code, 2)
        self.assertIn("legacy convert", err)
        self.assertEqual(sorted(p.name for p in (self.tmp / "stuff").iterdir()), ["notes.txt"])

    def test_empty_existing_dir_is_used(self):
        (self.tmp / "empty").mkdir()
        self.run_cli("new", "empty", "--no-claude")
        self.assertTrue((self.tmp / "empty" / "CLAUDE.md").is_file())


class TestLegacy(_InTempDir):
    def test_legacy_runs_with_a_deprecation_warning(self):
        code, _, err = self.run_cli("legacy", "research", "study", "--no-claude")
        self.assertEqual(code, 0)
        self.assertIn("DEPRECATED", err)
        self.assertTrue((self.tmp / "study" / "literature").is_dir())

    def test_moved_names_point_at_legacy(self):
        for name in cli.MOVED_COMMANDS:
            with self.subTest(name=name):
                code, _, err = self.run_cli(name, "x")
                self.assertEqual(code, 2)
                self.assertIn(f"cleanvibe legacy {name}", err)
                self.assertFalse((self.tmp / "x").exists())

    def test_legacy_requires_a_command(self):
        code, _, _ = self.run_cli("legacy")
        self.assertEqual(code, 2)

    def test_replicate_is_not_legacy(self):
        code, _, err = self.run_cli("replicate", "some-paper", "--no-claude")
        self.assertEqual(code, 0)
        self.assertNotIn("DEPRECATED", err)
        self.assertTrue((self.tmp / "some-paper" / "replication_target").is_dir())


if __name__ == "__main__":
    unittest.main()
