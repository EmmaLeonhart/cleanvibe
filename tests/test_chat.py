"""Tests for cleanvibe.chat — stdlib unittest, no network, no Claude launch.

`cleanvibe chat` scaffolds a git-tracked conversation: ask-first CLAUDE.md and
queue, a private repo, and a Stop/SessionEnd hook that saves each session's
transcript into sessions/ and commits it. The hook script is exercised for real
against a fake transcript.
"""

import io
import json
import os
import platform
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from cleanvibe import chat, templates
from cleanvibe.chat import chat_project, default_chat_path
from cleanvibe.cli import main

IS_WINDOWS = platform.system() == "Windows"


def _make(name="tea-chat", topic=None):
    tmp = tempfile.mkdtemp()
    proj = Path(tmp) / name
    with redirect_stdout(io.StringIO()):
        chat_project(proj, topic=topic, no_claude=True)
    return proj


def _git(proj, *args):
    return subprocess.run(
        ["git", *args], cwd=proj, capture_output=True, text=True
    ).stdout


class TestChatScaffold(unittest.TestCase):
    def test_writes_expected_tree(self):
        proj = _make()
        for rel in (
            "CLAUDE.md",
            "README.md",
            "queue.md",
            "devlog.md",
            ".gitignore",
            "notes/.gitkeep",
            "sessions/.gitkeep",
            "data_lake/.gitkeep",
            ".claude/settings.json",
            ".claude/hooks/save_session_log.py",
            ".claude/skills/queue-driven-workflow/SKILL.md",
        ):
            self.assertTrue((proj / rel).is_file(), rel)
        self.assertEqual((proj / "!runClaude.bat").exists(), IS_WINDOWS)

    def test_initial_commit_tracks_hook_and_sessions(self):
        proj = _make()
        tracked = _git(proj, "ls-files").split()
        self.assertIn(".claude/settings.json", tracked)
        self.assertIn(".claude/hooks/save_session_log.py", tracked)
        self.assertIn("sessions/.gitkeep", tracked)
        self.assertEqual(_git(proj, "branch", "--show-current").strip(), "main")

    def test_queue_asks_first_and_goes_private(self):
        queue = (_make() / "queue.md").read_text(encoding="utf-8")
        first = queue.index("1. **Ask the user what they are trying to do.**")
        self.assertLess(first, queue.index("2. **Create the private GitHub repo"))
        self.assertIn("AskUserQuestion", queue)
        self.assertIn("gh repo create --private", queue)
        self.assertNotIn("--public", queue)

    def test_topic_threads_through(self):
        proj = _make(topic="Oolong oxidation levels")
        for rel in ("CLAUDE.md", "README.md", "queue.md"):
            self.assertIn("Oolong oxidation levels", (proj / rel).read_text(encoding="utf-8"))

    def test_no_topic_uses_placeholder(self):
        claude = (_make() / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn(templates._CHAT_TOPIC_PLACEHOLDER, claude)

    def test_claude_md_rules(self):
        claude = (_make() / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("AskUserQuestion", claude)
        self.assertIn("Session logs (git-tracked)", claude)
        self.assertIn("private by default", claude)
        self.assertIn("Not-done taxonomy", claude)

    def test_settings_wire_stop_and_session_end(self):
        settings = json.loads((_make() / ".claude/settings.json").read_text(encoding="utf-8"))
        stop = settings["hooks"]["Stop"][0]["hooks"][0]["command"]
        end = settings["hooks"]["SessionEnd"][0]["hooks"][0]["command"]
        self.assertIn("save_session_log.py", stop)
        self.assertNotIn("--push", stop)
        self.assertIn("--push", end)

    def test_dry_run_writes_nothing(self):
        tmp = tempfile.mkdtemp()
        proj = Path(tmp) / "c"
        with redirect_stdout(io.StringIO()):
            chat_project(proj, dry_run=True)
        self.assertFalse(proj.exists())


class TestDefaultName(unittest.TestCase):
    def test_default_is_dated_and_suffixed(self):
        tmp = Path(tempfile.mkdtemp())
        first = default_chat_path(tmp)
        self.assertRegex(first.name, r"^chat-\d{4}-\d{2}-\d{2}$")
        first.mkdir()
        self.assertEqual(default_chat_path(tmp).name, first.name + "-2")


class TestChatCli(unittest.TestCase):
    def test_cli_dispatch(self):
        tmp = tempfile.mkdtemp()
        proj = Path(tmp) / "mychat"
        with redirect_stdout(io.StringIO()):
            main(["legacy", "chat", str(proj), "--topic", "Tea", "--no-claude"])
        self.assertIn("Tea", (proj / "README.md").read_text(encoding="utf-8"))

    def test_cli_without_name_uses_default(self):
        tmp = Path(tempfile.mkdtemp())
        with mock.patch.object(chat, "default_chat_path", return_value=tmp / "chat-x"), \
                mock.patch("cleanvibe.cli.default_chat_path", return_value=tmp / "chat-x"), \
                redirect_stdout(io.StringIO()):
            main(["legacy", "chat", "--no-claude"])
        self.assertTrue((tmp / "chat-x" / "CLAUDE.md").is_file())


def _transcript(path):
    lines = [
        {"type": "mode", "mode": "normal"},
        {"type": "user", "timestamp": "2026-09-26T10:00:00Z",
         "message": {"role": "user", "content": "What is oolong?<system-reminder>noise</system-reminder>"}},
        {"type": "assistant", "timestamp": "2026-09-26T10:00:05Z",
         "message": {"role": "assistant", "content": [
             {"type": "thinking", "thinking": "private"},
             {"type": "text", "text": "A partly oxidized tea."},
             {"type": "tool_use", "id": "t1", "name": "WebSearch", "input": {"query": "oolong oxidation"}},
             {"type": "tool_use", "id": "t2", "name": "AskUserQuestion",
              "input": {"questions": [{"question": "How deep should I go?"}]}},
         ]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "t1", "content": "search output"},
            {"type": "tool_result", "tool_use_id": "t2", "content": "Deep dive"},
        ]}},
        {"type": "attachment", "attachment": {"type": "queued_command", "prompt": "Also cover pu-erh"}},
        {"type": "user", "isMeta": True, "message": {"role": "user", "content": "meta"}},
    ]
    path.write_text("\n".join(json.dumps(l) for l in lines) + "\nnot json\n", encoding="utf-8")


class TestSessionLogHook(unittest.TestCase):
    def _run_hook(self, proj, transcript, *args, interval="0"):
        # interval=None leaves the default hourly throttle in place.
        payload = json.dumps({"session_id": "abcdef123456", "transcript_path": str(transcript)})
        env = dict(os.environ)
        env.pop("CLEANVIBE_LOG_COMMIT_SECONDS", None)
        if interval is not None:
            env["CLEANVIBE_LOG_COMMIT_SECONDS"] = interval
        return subprocess.run(
            [sys.executable, str(proj / ".claude/hooks/save_session_log.py"), *args],
            input=payload, capture_output=True, text=True, env=env,
        )

    def test_saves_renders_and_commits_only_sessions(self):
        proj = _make()
        transcript = Path(tempfile.mkdtemp()) / "t.jsonl"
        _transcript(transcript)
        # Something else staged must NOT be swept into the session-log commit.
        (proj / "notes" / "draft.md").write_text("wip", encoding="utf-8")
        _git(proj, "add", "notes/draft.md")

        result = self._run_hook(proj, transcript)
        self.assertEqual(result.returncode, 0, result.stderr)

        raw = proj / "sessions" / "2026-09-26_abcdef12.jsonl"
        md = proj / "sessions" / "2026-09-26_abcdef12.md"
        self.assertEqual(raw.read_text(encoding="utf-8"), transcript.read_text(encoding="utf-8"))
        text = md.read_text(encoding="utf-8")
        self.assertIn("What is oolong?", text)
        self.assertNotIn("noise", text)          # system reminders stripped
        self.assertNotIn("private", text)        # thinking not rendered
        self.assertNotIn("meta", text)           # isMeta skipped
        self.assertIn("A partly oxidized tea.", text)
        self.assertIn("*WebSearch*: oolong oxidation", text)
        self.assertNotIn("search output", text)  # ordinary tool output skipped
        self.assertIn("How deep should I go?", text)
        self.assertIn("**Answered:** Deep dive", text)
        self.assertIn("Also cover pu-erh", text)  # mid-turn message

        self.assertIn("session log 2026-09-26_abcdef12", _git(proj, "log", "-1", "--format=%s"))
        committed = _git(proj, "show", "--name-only", "--format=", "HEAD").split()
        self.assertEqual(sorted(committed), [
            "sessions/2026-09-26_abcdef12.jsonl", "sessions/2026-09-26_abcdef12.md"])
        self.assertIn("notes/draft.md", _git(proj, "diff", "--cached", "--name-only"))

    def test_unchanged_transcript_makes_no_new_commit(self):
        proj = _make()
        transcript = Path(tempfile.mkdtemp()) / "t.jsonl"
        _transcript(transcript)
        self._run_hook(proj, transcript)
        before = _git(proj, "rev-parse", "HEAD")
        self._run_hook(proj, transcript)
        self.assertEqual(_git(proj, "rev-parse", "HEAD"), before)

    def test_stop_commits_at_most_hourly(self):
        # Fresh project: its initial commit just touched sessions/, so a Stop
        # within the hour refreshes the files but does not commit them.
        proj = _make()
        transcript = Path(tempfile.mkdtemp()) / "t.jsonl"
        _transcript(transcript)
        before = _git(proj, "rev-parse", "HEAD")
        result = self._run_hook(proj, transcript, interval=None)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((proj / "sessions" / "2026-09-26_abcdef12.md").is_file())
        self.assertEqual(_git(proj, "rev-parse", "HEAD"), before)
        self.assertIn("sessions/", _git(proj, "status", "--porcelain"))

    def test_session_end_always_commits(self):
        proj = _make()
        transcript = Path(tempfile.mkdtemp()) / "t.jsonl"
        _transcript(transcript)
        before = _git(proj, "rev-parse", "HEAD")
        self._run_hook(proj, transcript, "--push", interval=None)
        self.assertNotEqual(_git(proj, "rev-parse", "HEAD"), before)
        self.assertEqual(_git(proj, "status", "--porcelain", "--", "sessions"), "")

    def test_push_without_upstream_is_harmless(self):
        proj = _make()
        transcript = Path(tempfile.mkdtemp()) / "t.jsonl"
        _transcript(transcript)
        result = self._run_hook(proj, transcript, "--push")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_bad_input_never_fails_the_hook(self):
        proj = _make()
        result = self._run_hook(proj, Path(tempfile.mkdtemp()) / "missing.jsonl")
        self.assertEqual(result.returncode, 0)
        self.assertIn("save_session_log", result.stderr)


if __name__ == "__main__":
    unittest.main()
