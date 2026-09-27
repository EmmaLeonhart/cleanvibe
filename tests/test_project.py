"""Tests for cleanvibe.project — the cleanvibe 2 default project.

Stdlib unittest, no network, no Claude launch (launching is mocked).
"""

import io
import json
import platform
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from cleanvibe import project, skills, templates
from cleanvibe.scaffold import create_project

IS_WINDOWS = platform.system() == "Windows"


def _new(name="tea-notes", auto_named=False):
    proj = Path(tempfile.mkdtemp()) / name
    with redirect_stdout(io.StringIO()):
        project.new_project(proj, auto_named=auto_named, no_claude=True)
    return proj


def _git(proj, *args):
    return subprocess.run(["git", *args], cwd=proj, capture_output=True, text=True).stdout


class TestNewProject(unittest.TestCase):
    def test_minimal_tree(self):
        proj = _new()
        for rel in ("CLAUDE.md", "README.md", "INTENT.md", ".cleanvibe.json",
                    ".gitignore", "sessions/.gitkeep", "data_lake/.gitkeep",
                    ".claude/settings.json", ".claude/hooks/save_session_log.py"):
            self.assertTrue((proj / rel).is_file(), rel)
        for slug in skills.SKILLS:
            self.assertTrue((proj / ".claude/skills" / slug / "SKILL.md").is_file(), slug)
        self.assertEqual((proj / "!runClaude.bat").exists(), IS_WINDOWS)
        # Minimal assumptions: no queue/todo/devlog until the work needs them.
        for rel in ("queue.md", "todo.md", "devlog.md"):
            self.assertFalse((proj / rel).exists(), rel)

    def test_private_local_git_with_everything_committed(self):
        proj = _new()
        self.assertEqual(_git(proj, "branch", "--show-current").strip(), "main")
        self.assertEqual(_git(proj, "remote").strip(), "")
        self.assertEqual(_git(proj, "status", "--porcelain").strip(), "")
        tracked = _git(proj, "ls-files").split()
        for rel in (".cleanvibe.json", "INTENT.md", ".claude/settings.json",
                    ".claude/hooks/save_session_log.py", "sessions/.gitkeep"):
            self.assertIn(rel, tracked)

    def test_marker(self):
        marker = json.loads((_new("abc") / ".cleanvibe.json").read_text(encoding="utf-8"))
        self.assertEqual(marker["name"], "abc")
        self.assertFalse(marker["auto_named"])
        self.assertRegex(marker["created"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertIn("cleanvibe", marker)

    def test_auto_named_is_recorded_everywhere(self):
        proj = _new("cleanvibe-2026-09-26", auto_named=True)
        self.assertTrue(json.loads((proj / ".cleanvibe.json").read_text(encoding="utf-8"))["auto_named"])
        self.assertIn("created without a name", (proj / "INTENT.md").read_text(encoding="utf-8"))
        self.assertIn("the user gave no name", _git(proj, "log", "-1", "--format=%B"))

    def test_named_intent_points_at_the_name(self):
        intent = (_new("oolong-research") / "INTENT.md").read_text(encoding="utf-8")
        self.assertIn("directory name, `oolong-research`", intent)

    def test_claude_md_rules(self):
        claude = (_new() / "CLAUDE.md").read_text(encoding="utf-8")
        for needle in ("AskUserQuestion", "INTENT.md", "Minimal assumptions",
                       "queue-driven-workflow", "research-practice", "autonomous-loop",
                       "scratch/", "gh repo create --private", "sessions/",
                       "Not-done taxonomy"):
            self.assertIn(needle, claude)
        self.assertNotIn("--public", claude)

    def test_gitignore_keeps_scratch_out(self):
        self.assertIn("\nscratch/\n", (_new() / ".gitignore").read_text(encoding="utf-8"))

    def test_launches_first_session_with_remote_control(self):
        proj = Path(tempfile.mkdtemp()) / "p"
        with mock.patch.object(project, "_launch_claude") as launch, redirect_stdout(io.StringIO()):
            project.new_project(proj, auto_named=True)
        args, kwargs = launch.call_args
        self.assertEqual(args[1], templates.v2_first_prompt(proj.resolve(), True))
        self.assertTrue(kwargs["remote_control"])

    def test_dry_run_writes_nothing(self):
        proj = Path(tempfile.mkdtemp()) / "p"
        with redirect_stdout(io.StringIO()):
            project.new_project(proj, dry_run=True)
        self.assertFalse(proj.exists())


class TestRecognizeAndOpen(unittest.TestCase):
    def test_is_cleanvibe_repo(self):
        self.assertTrue(project.is_cleanvibe_repo(_new()))
        legacy = Path(tempfile.mkdtemp()) / "legacy"
        with redirect_stdout(io.StringIO()):
            create_project(legacy, no_claude=True)
        self.assertTrue(project.is_cleanvibe_repo(legacy))
        plain = Path(tempfile.mkdtemp())
        self.assertFalse(project.is_cleanvibe_repo(plain))
        (plain / "CLAUDE.md").write_text("# some other project\n", encoding="utf-8")
        (plain / "queue.md").write_text("x\n", encoding="utf-8")
        self.assertFalse(project.is_cleanvibe_repo(plain))

    def test_auto_project_path_suffixes(self):
        base = Path(tempfile.mkdtemp())
        first = project.auto_project_path(base)
        self.assertRegex(first.name, r"^cleanvibe-\d{4}-\d{2}-\d{2}$")
        first.mkdir()
        self.assertEqual(project.auto_project_path(base).name, first.name + "-2")

    def test_open_uses_resume_prompt_without_explorer(self):
        proj = _new()
        with mock.patch.object(project, "_launch_claude") as launch, redirect_stdout(io.StringIO()):
            project.open_project(proj)
        args, kwargs = launch.call_args
        self.assertEqual(args[1], templates.v2_resume_prompt(proj.resolve()))
        self.assertTrue(kwargs["remote_control"])
        self.assertFalse(kwargs["show_folder"])


class TestV2Prompts(unittest.TestCase):
    def test_first_prompt_content(self):
        named = templates.v2_first_prompt("/home/e/oolong", False)
        auto = templates.v2_first_prompt("/home/e/cleanvibe-2026-09-26", True)
        for prompt in (named, auto):
            self.assertIn("first ever session", prompt)
            self.assertIn("AskUserQuestion", prompt)
            self.assertIn("INTENT.md", prompt)
        self.assertIn("at /home/e/oolong", named)
        self.assertIn("directory name is the main clue", named)
        self.assertIn("without giving a name", auto)

    def test_prompts_are_cmd_safe(self):
        for prompt in (templates.v2_first_prompt("C:\\x\\y", True),
                       templates.v2_resume_prompt("C:\\x\\y")):
            for ch in '"%^&|<>!\n\r':
                self.assertNotIn(ch, prompt)

    def test_unsafe_path_is_left_out(self):
        prompt = templates.v2_first_prompt("/tmp/a&b", False)
        self.assertNotIn("a&b", prompt)
        self.assertIn("started with cleanvibe.", prompt)

    def test_bat_resumes_with_remote_control(self):
        bat = templates.v2_runclaude_bat("/x")
        self.assertIn(templates.v2_resume_prompt(""), bat)
        # The .bat names no path (%~dp0 is its folder): no dangling " at ".
        self.assertIn("existing cleanvibe project. Catch up", bat)
        self.assertTrue(bat.rstrip().endswith("--remote-control"))


if __name__ == "__main__":
    unittest.main()
