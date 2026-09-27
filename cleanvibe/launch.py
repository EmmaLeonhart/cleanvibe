"""Launch Claude Code as a real, top-level session.

When an agent runs cleanvibe (a Claude session using its shell tool), the
`claude` it starts inherits that session's environment, including
``CLAUDE_CODE_CHILD_SESSION=1``, the parent's session id and message socket,
and its Remote Control bridge id. The new session then starts life as a
*child* of the agent's session: it does not behave as its own conversation,
and its transcript is not saved like a normal one. cleanvibe 2 depends on
every session having its own saved transcript, so :func:`clean_env` removes
the parent session's identity before launching.

The launch itself:

* **Windows**: a new console window (``cmd /k claude ...``), in a new process
  group, breaking away from the caller's job object when the caller allows
  it, so it survives the agent's shell call finishing.
* **Unix with a terminal**: replace this process with ``claude`` (as before).
* **Unix without a terminal** (run by an agent): open a new terminal window
  running a generated launch script (macOS Terminal, or the first Linux
  terminal emulator found). If there is none, print the exact command.
"""

from __future__ import annotations

import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import templates

# The parent Claude session's identity. Exact names, plus a pattern for the
# CLAUDE_CODE_* variables that describe a running session rather than user
# configuration (CLAUDE_CODE_GIT_BASH_PATH, CLAUDE_CODE_USE_BEDROCK and the
# like are configuration and are kept).
SESSION_ENV_VARS = frozenset({
    "CLAUDECODE",
    "AI_AGENT",
    "CLAUDE_PID",
    "CLAUDE_EFFORT",
    "CLAUDE_EXE",
    "CLAUDE_PROJECT_DIR",
    "CLAUDE_ENV_FILE",
})
_SESSION_ENV_PATTERN = re.compile(
    r"^CLAUDE_CODE_\w*(SESSION|SOCKET|BRIDGE|CHILD|PARENT|ENTRYPOINT|EXECPATH|"
    r"SSE_PORT|ATTENDED|REAP)\w*$"
)

# Windows process-creation flags (subprocess only defines some of them).
_CREATE_NEW_CONSOLE = 0x00000010
_CREATE_NEW_PROCESS_GROUP = 0x00000200
_CREATE_BREAKAWAY_FROM_JOB = 0x01000000

_LINUX_TERMINALS = (
    ("x-terminal-emulator", ["-e"]),
    ("gnome-terminal", ["--"]),
    ("konsole", ["-e"]),
    ("xfce4-terminal", ["-x"]),
    ("xterm", ["-e"]),
)


def is_session_var(name: str) -> bool:
    return name in SESSION_ENV_VARS or bool(_SESSION_ENV_PATTERN.match(name))


def clean_env(environ=None) -> dict:
    """A copy of ``environ`` without any parent Claude session's identity."""
    environ = os.environ if environ is None else environ
    return {k: v for k, v in environ.items() if not is_session_var(k)}


def launch(
    path: Path,
    prompt: str | None = None,
    remote_control: bool = False,
    show_folder: bool = True,
    name: str | None = None,
) -> None:
    """Start Claude Code in ``path`` as its own top-level session.

    ``show_folder`` also opens the folder in Explorer (Windows only), as a new
    project always has.
    """
    path = Path(path)
    command = templates.claude_command(prompt, remote_control, name)
    env = clean_env()
    print(f"  Launching Claude Code...")
    try:
        if platform.system() == "Windows":
            _launch_windows(path, command, env, show_folder)
        elif _has_tty():
            os.chdir(path)
            os.execvpe("claude", command, env)
        else:
            _launch_in_new_terminal(path, command)
    except FileNotFoundError:
        print(
            "  Could not launch 'claude'. Make sure Claude Code is installed and on your PATH.",
            file=sys.stderr,
        )


def _has_tty() -> bool:
    """True when a person is at this terminal (not an agent's shell tool)."""
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False


def _launch_windows(path: Path, command: list, env: dict, show_folder: bool = True) -> None:
    if show_folder:
        subprocess.Popen(["explorer", str(path)])
    flags = _CREATE_NEW_CONSOLE | _CREATE_NEW_PROCESS_GROUP
    try:
        subprocess.Popen(
            ["cmd", "/k", *command], cwd=str(path), env=env,
            creationflags=flags | _CREATE_BREAKAWAY_FROM_JOB,
        )
    except PermissionError:
        # The caller's job object forbids breakaway; a plain new console still
        # works, it just may close when the caller's job ends.
        subprocess.Popen(
            ["cmd", "/k", *command], cwd=str(path), env=env, creationflags=flags,
        )


def launch_script(path: Path, command: list) -> str:
    """A POSIX shell script that clears the parent session's identity and
    starts ``command`` in ``path``."""
    unset = sorted(k for k in os.environ if is_session_var(k))
    lines = ["#!/bin/sh"]
    if unset:
        lines.append("unset " + " ".join(unset))
    lines.append(f"cd {shlex.quote(str(path.resolve()))} || exit 1")
    lines.append("exec " + " ".join(shlex.quote(part) for part in command))
    return "\n".join(lines) + "\n"


def _launch_in_new_terminal(path: Path, command: list) -> None:
    fd, script = tempfile.mkstemp(prefix="cleanvibe-", suffix=".command")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(launch_script(path, command))
    os.chmod(script, 0o755)

    if platform.system() == "Darwin":
        subprocess.Popen(["open", "-a", "Terminal", script])
        print(f"  Opened a new Terminal window for the session.")
        return
    for name, flag in _LINUX_TERMINALS:
        if shutil.which(name):
            subprocess.Popen([name, *flag, "sh", script], env=clean_env())
            print(f"  Opened a new {name} window for the session.")
            return
    print("  No terminal to open here. Start the session yourself with:")
    print(f"    sh {shlex.quote(script)}")
