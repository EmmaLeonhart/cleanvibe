"""Tests for the per-mode starting prompt (v1.18.0).

Every mode launches Claude with a first message saying the project was started
with cleanvibe, which mode, and what to do first. The prompt travels through
`cmd /k` and a .bat file, so it must stay free of cmd-special characters.
"""

import unittest
from unittest import mock
from pathlib import Path

from cleanvibe import templates


class TestStartingPrompt(unittest.TestCase):
    def test_every_mode_names_cleanvibe_and_itself(self):
        for mode in templates._MODE_SUMMARIES:
            prompt = templates.starting_prompt(mode)
            self.assertIn("started with cleanvibe", prompt)
            self.assertIn(f"({mode} mode)", prompt)
            self.assertIn("queue.md", prompt)
            self.assertIn("make a reasonable assumption", prompt)

    def test_prompts_are_cmd_safe_single_line(self):
        for mode in templates._MODE_SUMMARIES:
            prompt = templates.starting_prompt(mode)
            for ch in '"%^&|<>!\n\r':
                self.assertNotIn(ch, prompt, f"{mode!r} prompt contains {ch!r}")

    def test_unsafe_summary_is_rejected(self):
        with mock.patch.dict(templates._MODE_SUMMARIES, {"bad": 'say "hi" & exit'}):
            with self.assertRaises(ValueError):
                templates.starting_prompt("bad")

    def test_bat_passes_the_prompt(self):
        bat = templates.runclaude_bat("research")
        self.assertTrue(bat.startswith("@echo off\n"))
        self.assertIn('cd /d "%~dp0"', bat)
        self.assertIn(f'claude "{templates.starting_prompt("research")}"', bat)

    def test_remote_control_flag_comes_after_prompt(self):
        # `--remote-control [name]` takes an optional value; placed before the
        # prompt it would swallow the prompt as the session name.
        self.assertEqual(templates.claude_command("hi", True),
                         ["claude", "hi", "--remote-control"])
        self.assertEqual(templates.claude_command(None, True),
                         ["claude", "--remote-control"])
        self.assertEqual(templates.claude_command("hi"), ["claude", "hi"])

    def test_only_chat_bat_uses_remote_control(self):
        chat_bat = templates.runclaude_bat("chat")
        self.assertTrue(chat_bat.rstrip().endswith('" --remote-control'))
        for mode in templates._MODE_SUMMARIES:
            if mode != "chat":
                self.assertNotIn("--remote-control", templates.runclaude_bat(mode))

    def test_chat_launches_with_remote_control(self):
        import tempfile
        from contextlib import redirect_stdout
        import io
        from cleanvibe import chat
        proj = Path(tempfile.mkdtemp()) / "c"
        with mock.patch.object(chat, "_launch_claude") as launch, redirect_stdout(io.StringIO()):
            chat.chat_project(proj)
        launch.assert_called_once_with(proj, templates.starting_prompt("chat"), remote_control=True)


if __name__ == "__main__":
    unittest.main()
