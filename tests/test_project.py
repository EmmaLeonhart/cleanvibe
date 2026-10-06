"""Tests for cleanvibe.project — the cleanvibe 2 default project.

Stdlib unittest, no network, no Claude launch (launching is mocked).
"""

import io
import os
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

# Never let a launch-path test write the real ~/.claude.json (cleanvibe.trust
# pre-trusts new project folders there). Set before any test runs, whether or
# not tests/__init__.py was imported (`unittest discover -s tests` skips it).
os.environ["CLEANVIBE_CLAUDE_CONFIG"] = os.path.join(
    tempfile.mkdtemp(prefix="cleanvibe-tests-"), ".claude.json"
)


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
                    ".claude/settings.json", ".claude/hooks/save_session_log.py",
                    ".claude/scripts/data_lake_intake.py"):
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
        for needle in ("work from low information", "The chat is the project, from the first message",
                       "INTENT.md", "AskUserQuestion only when the user is clearly here",
                       "Material goes into `data_lake/`", "Thirty-minute intake",
                       "recurring: false", "data_lake_intake.py",
                       "## Chat mode, then work mode", "## Mode check",
                       "An hour has passed since the user's last message",
                       "every new message restarts the hour",
                       "Nothing to go on", "a guess about why the project exists",
                       "No strict instructions is not no work",
                       "the tool or the chat is the subject, it is",
                       "applies only when the\n  user has said nothing at all",
                       "ask one short question before acting",
                       "Stay inside this project", "mean stop now",
                       "queue-driven-workflow", "research-practice", "autonomous-loop",
                       "scratch/", "## Publishing", "With no signal, or signals both ways, it is private.",
                       "sessions/",
                       "Not-done taxonomy"):
            self.assertIn(needle, claude)
        # The default rule names both commands; public only on a signal.
        self.assertIn("--public --source=. --push", claude)
        self.assertIn("(`--private`)", claude)

    def test_gitignore_keeps_scratch_out(self):
        self.assertIn("\nscratch/\n", (_new() / ".gitignore").read_text(encoding="utf-8"))

    def test_launches_first_session_with_remote_control(self):
        proj = project.auto_project_path(Path(tempfile.mkdtemp()))
        with mock.patch.object(project, "_launch_claude") as launch, redirect_stdout(io.StringIO()):
            project.new_project(proj, auto_named=True)
        args, kwargs = launch.call_args
        self.assertEqual(args[1], templates.v2_first_prompt(proj.resolve(), True))
        self.assertTrue(kwargs["remote_control"])
        # Auto-named: a passphrase title, recorded in the marker and the .bat (Emma,
        # 2026-10-01: Claude's own title came from the boilerplate prompt).
        name = kwargs["name"]
        self.assertRegex(name, r"^[a-z]+-[a-z]+-[a-z]+$")
        self.assertEqual(name, proj.name)  # folder and title are the same name
        marker = json.loads((proj / ".cleanvibe.json").read_text(encoding="utf-8"))
        self.assertEqual(marker["session_name"], name)
        if (proj / "!runClaude.bat").exists():
            self.assertIn(f"--name {name} --remote-control {name}",
                          (proj / "!runClaude.bat").read_text(encoding="utf-8"))
        with mock.patch.object(project, "_launch_claude") as launch, redirect_stdout(io.StringIO()):
            project.open_project(proj)
        self.assertEqual(launch.call_args.kwargs["name"], name)  # reopening keeps it

    def test_chosen_name_is_the_session_name(self):
        proj = Path(tempfile.mkdtemp()) / "mental-health-discussion"
        with mock.patch.object(project, "_launch_claude") as launch, redirect_stdout(io.StringIO()):
            project.new_project(proj)
        self.assertEqual(launch.call_args.kwargs["name"], "mental-health-discussion")
        self.assertNotIn("session_name", (proj / ".cleanvibe.json").read_text(encoding="utf-8"))

    def test_passphrase_names_vary_and_are_cmd_safe(self):
        names = {templates.passphrase_name() for _ in range(50)}
        self.assertGreater(len(names), 40)
        for name in names:
            self.assertRegex(name, r"^[a-z]+-[a-z]+-[a-z]+$")

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

    def test_auto_project_path_is_a_fresh_passphrase(self):
        import random
        base = Path(tempfile.mkdtemp())
        first = project.auto_project_path(base, random.Random(1))
        self.assertRegex(first.name, r"^[a-z]+-[a-z]+-[a-z]+$")
        first.mkdir()
        # The same draw again is taken, so it draws another name.
        second = project.auto_project_path(base, random.Random(1))
        self.assertNotEqual(second.name, first.name)
        self.assertFalse(second.exists())

    def test_auto_project_path_numbers_when_every_draw_is_taken(self):
        base = Path(tempfile.mkdtemp())
        (base / "calm-tidy-otter").mkdir()
        with mock.patch.object(templates, "passphrase_name", return_value="calm-tidy-otter"):
            self.assertEqual(project.auto_project_path(base).name, "calm-tidy-otter-2")

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
        # The path carries real information and stays in. What an early session
        # got wrong was turning "this is a practice run" into invented work.
        self.assertIn("at /home/e/oolong", named)
        self.assertIn("I gave it a custom name", named)
        self.assertIn("auto-generated placeholder passphrase", auto)
        self.assertIn("a guess about why the project exists is not a task", named)
        for prompt in (named, auto):
            self.assertIn("starts in chat mode", prompt)
            self.assertIn("GitHub repo with a descriptive name, public or private as CLAUDE.md describes", prompt)
            self.assertIn("does not need my consent to continue", prompt)
        for prompt in (named, auto):
            self.assertIn("low information", prompt)
            self.assertIn("CronCreate", prompt)
            self.assertIn("Thirty-minute intake", prompt)
            self.assertIn("Only use AskUserQuestion if I am clearly here", prompt)
        self.assertIn("without giving a name", auto)

    def test_prompts_are_cmd_safe(self):
        for prompt in (templates.v2_first_prompt("C:\\x\\y", True),
                       templates.v2_resume_prompt("C:\\x\\y")):
            for ch in '"%^&|<>!\n\r':
                self.assertNotIn(ch, prompt)

    def test_path_in_both_prompts_unless_cmd_unsafe(self):
        for prompt in (templates.v2_first_prompt("/tmp/tests/scratch/x", False),
                       templates.v2_resume_prompt("/tmp/tests/scratch/x")):
            self.assertIn("at /tmp/tests/scratch/x", prompt)
        self.assertNotIn("a&b", templates.v2_first_prompt("/tmp/a&b", False))

    def test_bat_names_only_chosen_names(self):
        self.assertIn("--name ai-history --remote-control ai-history",
                      templates.v2_runclaude_bat("/x/ai-history"))
        auto = templates.v2_runclaude_bat("/x/cleanvibe-project-2026-09-26-2104", auto_named=True)
        self.assertNotIn("--name", auto)
        self.assertTrue(auto.rstrip().endswith('" --remote-control'))

    def test_bat_resumes_with_remote_control(self):
        bat = templates.v2_runclaude_bat("/x", auto_named=True)
        self.assertIn(templates.v2_resume_prompt(""), bat)
        # The .bat names no path (%~dp0 is its folder): no dangling " at ".
        self.assertIn("existing cleanvibe project. Catch up", bat)
        self.assertTrue(bat.rstrip().endswith("--remote-control"))


def _run_intake(proj):
    import sys
    return subprocess.run(
        [sys.executable, str(proj / ".claude/scripts/data_lake_intake.py")],
        capture_output=True, text=True,
    )


def _log(proj, *messages, minutes_ago=None):
    """A transcript in sessions/: cleanvibe's own prompt, then user messages.

    With minutes_ago, the user's messages carry a timestamp that long ago;
    without it they have none (which the intake treats as just now)."""
    from datetime import datetime, timedelta, timezone
    stamp = {}
    if minutes_ago is not None:
        when = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
        stamp = {"timestamp": when.isoformat().replace("+00:00", "Z")}
    entries = [{"type": "user", "message": {"role": "user", "content":
                templates.v2_first_prompt(proj, True)}},
               {"type": "user", "message": {"role": "user", "content":
                "[cleanvibe cron] Thirty-minute intake: follow CLAUDE.md"}}]
    entries += [{"type": "user", "message": {"role": "user", "content": m}, **stamp}
                for m in messages]
    (proj / "sessions" / "2026-09-26_abc.jsonl").write_text(
        "\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")


class TestResearchFixes203(unittest.TestCase):
    """v2.0.3: fixes from the ai-context-research transcript study (case study 06)."""

    def test_prompts_name_the_update_check(self):
        self.assertIn("cleanvibe-update-check", templates.v2_resume_prompt("/home/e/p"))
        self.assertIn("cleanvibe-update-check", templates.v2_first_prompt("/home/e/p", True))

    def test_claude_md_states_the_new_rules(self):
        md = templates.v2_claude_md("p")
        self.assertIn("Times come from the clock", md)                  # M3
        self.assertIn("quote their own words", md)                      # M4
        self.assertIn("~/.claude/projects/.../memory/", md)             # M5: harness memory is outside
        self.assertIn("data_lake/downloads/", md)                       # M5: agrees with research-practice
        self.assertIn("Constraints the user gives in chat", md)         # M7
        self.assertIn("confirm an edit landed", md)                     # M8

    def test_skills_agree_with_claude_md(self):
        self.assertIn("data_lake/downloads/", skills.SKILLS["research-practice"])
        self.assertIn("Check that the parts agree", skills.SKILLS["cleanvibe-update-check"])


class TestThirtyMinuteIntake(unittest.TestCase):
    def setUp(self):
        self.proj = _new("ai-history")
        # The user drops material in: a loose brief, a new folder, a file
        # straight into data_lake/, and an edit to a tracked file.
        (self.proj / "brief.md").write_text("# Research the history of AI\n", encoding="utf-8")
        (self.proj / "papers").mkdir()
        (self.proj / "papers" / "turing-1950.txt").write_text("computing machinery", encoding="utf-8")
        (self.proj / "data_lake" / "notes.txt").write_text("already here", encoding="utf-8")
        with open(self.proj / "README.md", "a", encoding="utf-8") as fh:
            fh.write("\nedited by the user\n")

    def test_snapshot_then_move_then_report(self):
        before = _git(self.proj, "rev-parse", "HEAD").strip()
        result = _run_intake(self.proj)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        subjects = _git(self.proj, "log", "--format=%s", f"{before}..HEAD").splitlines()
        self.assertEqual(subjects, [
            "Intake: move uncommitted material into data_lake/",
            "Intake: the repository 30 minutes in, before moving into data_lake/",
        ])
        # The snapshot commit holds every file where it was found.
        snap = _git(self.proj, "show", "--name-only", "--format=", "HEAD~1").split()
        for path in ("brief.md", "papers/turing-1950.txt", "data_lake/notes.txt", "README.md"):
            self.assertIn(path, snap)
        # The move commit moved only the never-committed top-level entries.
        tracked = _git(self.proj, "ls-files").split()
        for path in ("data_lake/brief.md", "data_lake/papers/turing-1950.txt", "data_lake/notes.txt"):
            self.assertIn(path, tracked)
        for path in ("brief.md", "papers/turing-1950.txt"):
            self.assertNotIn(path, tracked)
        for path in ("README.md", "CLAUDE.md", "INTENT.md", ".cleanvibe.json"):
            self.assertIn(path, tracked)
        self.assertEqual(_git(self.proj, "status", "--porcelain").strip(), "")
        self.assertIn("data_lake/papers/turing-1950.txt", result.stdout)
        self.assertIn("intake_at", (self.proj / ".cleanvibe.json").read_text(encoding="utf-8"))

    def test_runs_only_once(self):
        _run_intake(self.proj)
        head = _git(self.proj, "rev-parse", "HEAD")
        again = _run_intake(self.proj)
        self.assertEqual(again.returncode, 0)
        self.assertIn("already done", again.stdout)
        self.assertEqual(_git(self.proj, "rev-parse", "HEAD"), head)

    def test_no_chat_with_material_starts_work_mode(self):
        _log(self.proj)  # only cleanvibe's own prompts
        out = _run_intake(self.proj).stdout
        self.assertIn("0 message(s)", out)
        self.assertIn("WORK MODE", out)
        self.assertIn("said nothing, but there is material", out)

    def test_recent_chat_stays_in_chat_mode(self):
        # 2.0.3: the start is conversational; work waits for an hour of quiet.
        _log(self.proj, "This is about the history of AI.", "Focus on Dartmouth.", minutes_ago=10)
        out = _run_intake(self.proj).stdout
        self.assertIn("2 message(s)", out)
        self.assertIn("last message: 10 minute(s) ago", out)
        self.assertIn("CHAT MODE", out)
        self.assertIn("Schedule the Mode check", out)
        self.assertRegex(out, r"cron `\d+ \d+ \d+ \d+ \*`, recurring: false")
        self.assertNotIn("WORK MODE", out)

    def test_an_hour_of_quiet_starts_work_mode(self):
        _log(self.proj, "This is about the history of AI.", minutes_ago=75)
        out = _run_intake(self.proj).stdout
        self.assertIn("WORK MODE", out)
        self.assertIn("quiet for 60+ minutes", out)

    def test_mode_check_reruns_without_committing(self):
        _log(self.proj, "hello", minutes_ago=5)
        self.assertIn("CHAT MODE", _run_intake(self.proj).stdout)
        head = _git(self.proj, "rev-parse", "HEAD")
        _log(self.proj, "hello", minutes_ago=70)  # the user went quiet
        out = _run_intake(self.proj).stdout
        self.assertIn("# Mode check", out)
        self.assertIn("WORK MODE", out)
        self.assertEqual(_git(self.proj, "rev-parse", "HEAD"), head)

    def test_empty_folder_generated_name_is_nothing_to_go_on(self):
        proj = _new("cleanvibe-2026-09-26", auto_named=True)  # nothing dropped in
        out = _run_intake(proj).stdout
        self.assertIn("Material in data_lake/: none", out)
        self.assertIn("NOTHING TO GO ON", out)
        self.assertNotIn("start work mode now", out)

    def test_something_said_without_material_is_the_subject(self):
        # P1: anything the user says is something to go on.
        proj = _new("cleanvibe-2026-09-26", auto_named=True)
        _log(proj, "the history of chess engines")
        out = _run_intake(proj).stdout
        self.assertIn("CHAT MODE", out)  # no timestamp counts as just now
        self.assertNotIn("NOTHING TO GO ON", out)

    def test_empty_folder_chosen_name_is_name_only(self):
        out = _run_intake(_new("history-of-ai-research")).stdout
        self.assertIn("NAME ONLY", out)

    def test_material_without_engagement_starts_now(self):
        out = _run_intake(self.proj).stdout  # setUp dropped files in
        self.assertIn("but there is material", out)
        self.assertIn("start work mode now", out)

    def test_agent_work_already_committed_stays_put(self):
        (self.proj / "research").mkdir()
        (self.proj / "research" / "SUMMARY.md").write_text("x", encoding="utf-8")
        (self.proj / "notes-by-agent").mkdir()
        (self.proj / "notes-by-agent" / "a.md").write_text("x", encoding="utf-8")
        _git(self.proj, "add", "notes-by-agent")
        _git(self.proj, "commit", "-q", "-m", "agent notes")
        _run_intake(self.proj)
        tracked = _git(self.proj, "ls-files").split()
        self.assertIn("research/SUMMARY.md", tracked)          # a workflow directory
        self.assertIn("notes-by-agent/a.md", tracked)          # committed before intake


if __name__ == "__main__":
    unittest.main()
