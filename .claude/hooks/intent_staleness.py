#!/usr/bin/env python3
"""cleanvibe UserPromptSubmit hook: say how stale INTENT.md is on loop ticks,
and whether a newer cleanvibe release is out (since 2.0.12).

Only for prompts that start with "[cleanvibe cron]"; anything else gets no
output. What it prints is added to the agent's context. Always exits 0.
"""
import json
import os
import re
import subprocess
import sys
import time


def git(root, *args):
    return subprocess.run(
        ["git", "-C", root, *args], capture_output=True, text=True, timeout=10
    ).stdout.strip()


def _cleanvibe_home():
    return os.environ.get("CLEANVIBE_HOME") or os.path.join(os.path.expanduser("~"), ".cleanvibe")


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=20)


def private_ci_guard(root):
    """Turn GitHub Actions off on this project's repo when it is private
    (since 2.0.14). A written rule was not enough: on 2026-11-23 a project that
    never loaded the queue-driven-workflow skill added CI to a private repo and
    spent the user's Actions minutes. So this runs in code, on every prompt, at
    most once an hour per project. Allowed only when `cleanvibe config
    actions_on_private` is true, or the project's .cleanvibe.json has
    "actions_on_private": true. Any problem (no gh, no GitHub remote, offline)
    means it does nothing."""
    if _load_json(os.path.join(_cleanvibe_home(), "config.json")).get("actions_on_private") is True:
        return
    if _load_json(os.path.join(root, ".cleanvibe.json")).get("actions_on_private") is True:
        return
    gitdir = git(root, "rev-parse", "--absolute-git-dir")
    if not gitdir:
        return
    stamp = os.path.join(gitdir, "cleanvibe-ci-guard")
    try:
        if time.time() - os.path.getmtime(stamp) < 3600:
            return
    except OSError:
        pass
    url = git(root, "remote", "get-url", "origin")
    m = re.search(r"github\.com[:/]([^/\s]+)/([^/\s]+?)(?:\.git)?/?$", url)
    if not m:
        return
    repo = f"{m.group(1)}/{m.group(2)}"
    private = _gh("api", f"repos/{repo}", "-q", ".private")
    if private.returncode != 0:
        return
    try:
        open(stamp, "w").close()
    except OSError:
        pass
    if private.stdout.strip() != "true":
        return
    enabled = _gh("api", f"repos/{repo}/actions/permissions", "-q", ".enabled")
    if enabled.returncode != 0 or enabled.stdout.strip() != "true":
        return
    off = _gh("api", "-X", "PUT", f"repos/{repo}/actions/permissions", "-F", "enabled=false")
    if off.returncode == 0:
        print(
            f"[cleanvibe] {repo} is private, so GitHub Actions has been turned off for it: "
            "private repos must not spend Actions minutes. Run the tests locally before "
            "every push, delete any test workflow under .github/workflows/ and say so in "
            "devlog.md, and never turn Actions back on. Only the user can allow it "
            "(`cleanvibe config actions_on_private true`, or \"actions_on_private\": true "
            "in .cleanvibe.json)."
        )


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    try:
        private_ci_guard(root)
    except Exception:
        pass
    if not str(data.get("prompt", "")).lstrip().startswith("[cleanvibe cron]"):
        return
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
