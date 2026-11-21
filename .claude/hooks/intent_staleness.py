#!/usr/bin/env python3
"""cleanvibe UserPromptSubmit hook: say how stale INTENT.md is on loop ticks,
and whether a newer cleanvibe release is out (since 2.0.12).

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
    release_notice(root)


def _vt(v):
    return tuple(int("".join(c for c in p if c.isdigit()) or 0) for p in str(v).split("."))


def release_notice(root):
    """Say so when PyPI has a newer cleanvibe than the installed one. PyPI is
    asked at most every 6 hours per machine (cached in ~/.cleanvibe/latest.json);
    any problem means no output."""
    try:
        from importlib.metadata import version
        have = version("cleanvibe")
    except Exception:
        return
    home = os.environ.get("CLEANVIBE_HOME") or os.path.join(os.path.expanduser("~"), ".cleanvibe")
    cache = os.path.join(home, "latest.json")
    latest = None
    try:
        with open(cache, encoding="utf-8") as f:
            cached = json.load(f)
        if time.time() - cached["checked"] < 6 * 3600:
            latest = cached["version"]
    except Exception:
        pass
    if latest is None:
        source = os.environ.get("CLEANVIBE_PYPI_JSON")
        if source:
            with open(source, encoding="utf-8") as f:
                latest = json.load(f)["info"]["version"]
        else:
            import urllib.request
            req = urllib.request.Request("https://pypi.org/pypi/cleanvibe/json",
                                         headers={"User-Agent": "cleanvibe-hook"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                latest = json.loads(resp.read().decode("utf-8"))["info"]["version"]
        try:
            os.makedirs(home, exist_ok=True)
            with open(cache, "w", encoding="utf-8") as f:
                json.dump({"checked": time.time(), "version": latest}, f)
        except Exception:
            pass
    if _vt(latest) > _vt(have):
        script = os.path.join(root, ".claude", "scripts", "cleanvibe_upgrade.py")
        if os.path.isfile(script):
            how = "run `python .claude/scripts/cleanvibe_upgrade.py`"
        else:
            how = "run `python -m pip install -U cleanvibe`, then `cleanvibe refresh`"
        print(f"[cleanvibe] cleanvibe {latest} is out (installed: {have}). This tick, "
              f"{how} and commit what it changed.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
