"""Tests for cleanvibe.launch — starting Claude as a real, top-level session.

The bug this guards against: a `claude` started by an agent (a Claude session
running cleanvibe through its shell tool) inherited the agent's session
identity (CLAUDE_CODE_CHILD_SESSION=1, session id, message socket, Remote
Control bridge id) and ran as a child session. All launching is mocked; no
real process is started.
"""

import io
import os
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from cleanvibe import launch

PARENT_SESSION = {
    "CLAUDECODE": "1",
    "AI_AGENT": "claude-code_2-1-283_agent",
    "CLAUDE_PID": "40648",
    "CLAUDE_EFFORT": "medium",
    "CLAUDE_EXE": "claude",
    "CLAUDE_CODE_CHILD_SESSION": "1",
    "CLAUDE_CODE_SESSION_ID": "84a38fd5",
    "CLAUDE_CODE_MESSAGING_SOCKET": r"\\.\pipe\LOCAL\cc-msg",
    "CLAUDE_CODE_BRIDGE_SESSION_ID": "session_01",
    "CLAUDE_CODE_SESSION_ATTENDED": "1",
    "CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP": "1",
    "CLAUDE_CODE_ENTRYPOINT": "cli",
    "CLAUDE_CODE_EXECPATH": r"C:\claude.exe",
    "CLAUDE_PROJECT_DIR": "/somewhere",
}
USER_CONFIG = {
    "PATH": "/usr/bin",
    "HOME": "/home/emma",
    "ANTHROPIC_API_KEY": "sk-test",
    "CLAUDE_CONFIG_DIR": "/home/emma/.claude",
    "CLAUDE_CODE_GIT_BASH_PATH": r"C:\Git\bin\bash.exe",
    "CLAUDE_CODE_USE_BEDROCK": "1",
}


class TestCleanEnv(unittest.TestCase):
    def test_strips_every_parent_session_var(self):
        env = launch.clean_env({**PARENT_SESSION, **USER_CONFIG})
        for name in PARENT_SESSION:
            self.assertNotIn(name, env)

    def test_keeps_user_configuration(self):
        env = launch.clean_env({**PARENT_SESSION, **USER_CONFIG})
        self.assertEqual(env, USER_CONFIG)


class TestWindowsLaunch(unittest.TestCase):
    def _launch(self, popen_side_effect=None, **kwargs):
        with mock.patch.dict(os.environ, PARENT_SESSION), \
                mock.patch.object(launch.platform, "system", return_value="Windows"), \
                mock.patch.object(launch.subprocess, "Popen", side_effect=popen_side_effect) as popen, \
                redirect_stdout(io.StringIO()):
            launch.launch(Path("."), "hello there", **kwargs)
        return popen

    def test_new_console_breaking_away_with_clean_env(self):
        popen = self._launch(remote_control=True)
        args, kwargs = popen.call_args_list[-1]
        self.assertEqual(args[0], ["cmd", "/k", "claude", "hello there", "--remote-control"])
        self.assertTrue(kwargs["creationflags"] & launch._CREATE_NEW_CONSOLE)
        self.assertTrue(kwargs["creationflags"] & launch._CREATE_BREAKAWAY_FROM_JOB)
        self.assertNotIn("CLAUDE_CODE_CHILD_SESSION", kwargs["env"])
        self.assertNotIn("CLAUDE_CODE_BRIDGE_SESSION_ID", kwargs["env"])

    def test_falls_back_when_breakaway_is_denied(self):
        calls = []

        def popen(argv, **kwargs):
            calls.append(kwargs.get("creationflags", 0))
            if kwargs.get("creationflags", 0) & launch._CREATE_BREAKAWAY_FROM_JOB:
                raise PermissionError("access denied")
            return mock.Mock()

        self._launch(popen_side_effect=popen)
        # explorer, the denied breakaway attempt, then the plain new console.
        self.assertEqual(len(calls), 3)
        self.assertFalse(calls[-1] & launch._CREATE_BREAKAWAY_FROM_JOB)
        self.assertTrue(calls[-1] & launch._CREATE_NEW_CONSOLE)


class TestUnixLaunch(unittest.TestCase):
    def test_with_a_terminal_execs_with_clean_env(self):
        with mock.patch.dict(os.environ, PARENT_SESSION), \
                mock.patch.object(launch.platform, "system", return_value="Linux"), \
                mock.patch.object(launch, "_has_tty", return_value=True), \
                mock.patch.object(launch.os, "chdir"), \
                mock.patch.object(launch.os, "execvpe") as execvpe, \
                redirect_stdout(io.StringIO()):
            launch.launch(Path("."), "hello", remote_control=True)
        name, argv, env = execvpe.call_args[0]
        self.assertEqual(argv, ["claude", "hello", "--remote-control"])
        self.assertNotIn("CLAUDE_CODE_CHILD_SESSION", env)

    def test_without_a_terminal_on_macos_opens_terminal(self):
        with mock.patch.object(launch.platform, "system", return_value="Darwin"), \
                mock.patch.object(launch, "_has_tty", return_value=False), \
                mock.patch.object(launch.subprocess, "Popen") as popen, \
                redirect_stdout(io.StringIO()):
            launch.launch(Path("."), "hello")
        argv = popen.call_args[0][0]
        self.assertEqual(argv[:3], ["open", "-a", "Terminal"])
        self.assertTrue(argv[3].endswith(".command"))
        script = Path(argv[3]).read_text(encoding="utf-8")
        self.assertIn("exec claude hello", script)

    def test_without_a_terminal_or_emulator_prints_the_command(self):
        buf = io.StringIO()
        with mock.patch.object(launch.platform, "system", return_value="Linux"), \
                mock.patch.object(launch, "_has_tty", return_value=False), \
                mock.patch.object(launch.shutil, "which", return_value=None), \
                mock.patch.object(launch.subprocess, "Popen") as popen, \
                redirect_stdout(buf):
            launch.launch(Path("."), "hello")
        popen.assert_not_called()
        self.assertIn("Start the session yourself", buf.getvalue())


class TestLaunchScript(unittest.TestCase):
    def test_unsets_parent_session_and_quotes_everything(self):
        with mock.patch.dict(os.environ, PARENT_SESSION):
            script = launch.launch_script(Path("/tmp/my project"), ["claude", "it's a prompt", "--remote-control"])
        self.assertTrue(script.startswith("#!/bin/sh\n"))
        self.assertIn("CLAUDE_CODE_CHILD_SESSION", script.splitlines()[1])
        self.assertTrue(script.splitlines()[1].startswith("unset "))
        self.assertIn("exec claude 'it'\"'\"'s a prompt' --remote-control", script)


if __name__ == "__main__":
    unittest.main()
