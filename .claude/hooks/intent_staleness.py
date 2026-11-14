#!/usr/bin/env python3
"""cleanvibe UserPromptSubmit hook: say how stale INTENT.md is on loop ticks.

Only for prompts that start with "[cleanvibe cron]"; anything else gets no
output. What it prints is added to the agent's context. Always exits 0.
"""
import json
import os
import subprocess
import sys
import time


def git(root, *args):
    return subprocess.run(
        ["git", "-C", root, *args], capture_output=True, text=True, timeout=10
    ).stdout.strip()


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    if not str(data.get("prompt", "")).lstrip().startswith("[cleanvibe cron]"):
        return
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    if not os.path.isfile(os.path.join(root, "INTENT.md")):
        return
    last = git(root, "log", "-1", "--format=%H %ct", "--", "INTENT.md")
    if not last:
        print("[cleanvibe] INTENT.md has never been committed.")
        return
    sha, ts = last.split()
    hours = (time.time() - int(ts)) / 3600
    commits = git(root, "rev-list", "--count", f"{sha}..HEAD") or "0"
    print(
        f"[cleanvibe] INTENT.md last changed {hours:.1f} hours and {commits} "
        f"commits ago. If what you know about the project has changed since, "
        f"update it this tick."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
