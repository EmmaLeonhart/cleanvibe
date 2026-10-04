"""Tests for the cleanvibe 2 INTENT.md staleness hook (round 3 intervention).

Runs the generated `.claude/hooks/intent_staleness.py` against a freshly
scaffolded project, the way Claude Code's UserPromptSubmit hook would.
"""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cleanvibe import project, templates

os.environ["CLEANVIBE_CLAUDE_CONFIG"] = os.path.join(
    tempfile.mkdtemp(prefix="cleanvibe-tests-"), ".claude.json"
)


def _new():
    proj = Path(tempfile.mkdtemp()) / "tea-notes"
    with redirect_stdout(io.StringIO()):
        project.new_project(proj, no_claude=True)
    return proj


def _run_hook(proj, prompt):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(proj))
    result = subprocess.run(
        [sys.executable, str(proj / ".claude/hooks/intent_staleness.py")],
        input=json.dumps({"prompt": prompt, "cwd": str(proj)}),
        capture_output=True, text=True, env=env,
    )
    return result


def _commit(proj, name):
    (proj / name).write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", name], cwd=proj, check=True, capture_output=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-m", name], cwd=proj, check=True, capture_output=True)


class TestIntentStaleness(unittest.TestCase):
    def test_scaffold_writes_and_wires_the_hook(self):
        proj = _new()
        self.assertTrue((proj / ".claude/hooks/intent_staleness.py").is_file())
        settings = json.loads((proj / ".claude/settings.json").read_text(encoding="utf-8"))
        hooks = settings["hooks"]
        self.assertIn("intent_staleness.py", hooks["UserPromptSubmit"][0]["hooks"][0]["command"])
        self.assertIn("save_session_log.py", hooks["Stop"][0]["hooks"][0]["command"])
        self.assertIn("--push", hooks["SessionEnd"][0]["hooks"][0]["command"])

    def test_chat_settings_are_unchanged(self):
        self.assertNotIn("UserPromptSubmit", templates.chat_settings_json())

    def test_cron_tick_gets_hours_and_commits(self):
        proj = _new()
        _commit(proj, "a.txt")
        _commit(proj, "b.txt")
        result = _run_hook(proj, "[cleanvibe cron] Commit and push any and all changes")
        self.assertEqual(result.returncode, 0)
        self.assertRegex(result.stdout,
                         r"INTENT\.md last changed \d+\.\d hours and 2 commits ago")

    def test_user_prompt_gets_nothing(self):
        proj = _new()
        result = _run_hook(proj, "what is this project for?")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_bad_input_exits_zero_silently(self):
        proj = _new()
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(proj))
        result = subprocess.run(
            [sys.executable, str(proj / ".claude/hooks/intent_staleness.py")],
            input="not json", capture_output=True, text=True, env=env,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
