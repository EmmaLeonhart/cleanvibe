"""Cross-platform tests for cleanvibe.

Uses stdlib unittest to match the project's zero-dependency philosophy.
All tests pass --no-claude so Claude Code is never launched (no Claude install required in CI).
"""

import io
import platform
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cleanvibe import __version__
from cleanvibe.cli import main
from cleanvibe.scaffold import convert_project, create_project


IS_WINDOWS = platform.system() == "Windows"


class TestVersion(unittest.TestCase):
    def test_version_flag(self):
        with self.assertRaises(SystemExit) as cm:
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["--version"])
        self.assertEqual(cm.exception.code, 0)


class TestCreateProject(unittest.TestCase):
    def test_creates_core_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            self.assertTrue((proj / "CLAUDE.md").is_file())
            self.assertTrue((proj / "README.md").is_file())
            self.assertTrue((proj / ".gitignore").is_file())

    def test_runclaude_bat_only_on_windows(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            runclaude = proj / "runclaude.bat"
            if IS_WINDOWS:
                self.assertTrue(runclaude.is_file(), "runclaude.bat should be created on Windows")
            else:
                self.assertFalse(runclaude.exists(), "runclaude.bat should NOT be created on Unix")

    def test_initializes_git_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            self.assertTrue((proj / ".git").is_dir(), "git repo should be initialized")

    def test_claude_md_contains_project_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "uniqueprojectname"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            content = (proj / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("uniqueprojectname", content)


class TestDryRun(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "ghost"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, dry_run=True, no_claude=True)
            self.assertFalse(proj.exists(), "dry-run must not create the directory")
            output = buf.getvalue()
            self.assertIn("[dry-run]", output)
            self.assertIn("CLAUDE.md", output)


class TestConvert(unittest.TestCase):
    def test_convert_empty_dir_creates_two_commits(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "existing"
            proj.mkdir()
            (proj / "preexisting.txt").write_text("hello", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                convert_project(proj, no_claude=True)

            self.assertTrue((proj / ".git").is_dir())
            self.assertTrue((proj / "CLAUDE.md").is_file())
            self.assertTrue((proj / "preexisting.txt").is_file())

            # Two commits: original files, then scaffold
            result = subprocess.run(
                ["git", "log", "--oneline"],
                cwd=proj,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0)
            commits = [ln for ln in result.stdout.strip().splitlines() if ln.strip()]
            self.assertEqual(len(commits), 2, f"Expected 2 commits, got: {commits}")

    def test_convert_skips_existing_scaffold_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "existing"
            proj.mkdir()
            custom = "# my custom claude.md\n"
            (proj / "CLAUDE.md").write_text(custom, encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                convert_project(proj, no_claude=True)

            # CLAUDE.md must not be overwritten
            self.assertEqual((proj / "CLAUDE.md").read_text(encoding="utf-8"), custom)
            # README and .gitignore should still be injected
            self.assertTrue((proj / "README.md").is_file())
            self.assertTrue((proj / ".gitignore").is_file())


if __name__ == "__main__":
    unittest.main()
