"""Tests for the per-mode starting prompt (v1.18.0).

Every mode launches Claude with a first message saying the project was started
with cleanvibe, which mode, and what to do first. The prompt travels through
`cmd /k` and a .bat file, so it must stay free of cmd-special characters.
"""

import unittest
from unittest import mock
from pathlib import Path

from cleanvibe import scaffold, templates


class TestStartingPrompt(unittest.TestCase):
    def test_every_mode_names_cleanvibe_and_itself(self):
        for mode in templates._MODE_SUMMARIES:
            prompt = templates.starting_prompt(mode)
            self.assertIn("started with cleanvibe", prompt)
            self.assertIn(f"({mode} mode)", prompt)
            self.assertIn("queue.md", prompt)
            self.assertIn("AskUserQuestion", prompt)

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

    def test_launcher_passes_prompt_windows(self):
        with mock.patch.object(scaffold.platform, "system", return_value="Windows"), \
                mock.patch.object(scaffold.subprocess, "Popen") as popen, \
                mock.patch.object(scaffold.subprocess, "CREATE_NEW_CONSOLE", 16, create=True):
            scaffold._launch_claude(Path("."), "hello there")
        args = popen.call_args_list[-1][0][0]
        self.assertEqual(args, ["cmd", "/k", "claude", "hello there"])

    def test_launcher_passes_prompt_unix(self):
        with mock.patch.object(scaffold.platform, "system", return_value="Linux"), \
                mock.patch.object(scaffold.os, "chdir"), \
                mock.patch.object(scaffold.os, "execlp") as execlp:
            scaffold._launch_claude(Path("."), "hello there")
        execlp.assert_called_once_with("claude", "claude", "hello there")

    def test_launcher_without_prompt(self):
        with mock.patch.object(scaffold.platform, "system", return_value="Linux"), \
                mock.patch.object(scaffold.os, "chdir"), \
                mock.patch.object(scaffold.os, "execlp") as execlp:
            scaffold._launch_claude(Path("."))
        execlp.assert_called_once_with("claude", "claude")


if __name__ == "__main__":
    unittest.main()
