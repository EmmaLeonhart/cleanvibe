"""Picking up a new release by itself (since 2.0.12): the shipped
`.claude/scripts/cleanvibe_upgrade.py` and the loop-tick hook's notice.

Network-free: PyPI is replaced by a local JSON file (CLEANVIBE_PYPI_JSON), the
lock and cache live in a temp CLEANVIBE_HOME, and CLEANVIBE_UPGRADE_DRY makes
the script print its pip and refresh commands instead of running them.
"""

import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from importlib.metadata import version
from pathlib import Path

os.environ.setdefault("CLEANVIBE_CLAUDE_CONFIG", os.path.join(
    tempfile.mkdtemp(prefix="cleanvibe-tests-"), ".claude.json"))

from cleanvibe import doctor, project, templates  # noqa: E402

INSTALLED = version("cleanvibe")


def _new():
    proj = Path(tempfile.mkdtemp()) / "proj"
    with redirect_stdout(io.StringIO()):
        project.new_project(proj, no_claude=True)
    return proj


def _env(latest, **extra):
    home = tempfile.mkdtemp()
    pypi = Path(home) / "pypi.json"
    pypi.write_text(json.dumps({"info": {"version": latest}}), encoding="utf-8")
    env = dict(os.environ, CLEANVIBE_HOME=home, CLEANVIBE_PYPI_JSON=str(pypi),
               CLEANVIBE_UPGRADE_DRY="1")
    env.update(extra)
    return env


def _bump(v):
    parts = [int(p) for p in v.split(".")[:3]]
    parts[-1] += 1
    return ".".join(map(str, parts))


def _script(proj, env, *args):
    return subprocess.run(
        [sys.executable, str(proj / ".claude/scripts/cleanvibe_upgrade.py"), *args],
        capture_output=True, text=True, env=env)


def _hook(proj, env, prompt="[cleanvibe cron] Commit and push"):
    env = dict(env, CLAUDE_PROJECT_DIR=str(proj))
    return subprocess.run(
        [sys.executable, str(proj / ".claude/hooks/intent_staleness.py")],
        input=json.dumps({"prompt": prompt, "cwd": str(proj)}),
        capture_output=True, text=True, env=env)


class TestUpgradeScript(unittest.TestCase):
    def test_scaffold_ships_it_and_doctor_wants_it(self):
        proj = _new()
        self.assertTrue((proj / ".claude/scripts/cleanvibe_upgrade.py").is_file())
        self.assertEqual(doctor.run_checks(proj), [])
        (proj / ".claude/scripts/cleanvibe_upgrade.py").unlink()
        self.assertIn(".claude/scripts/cleanvibe_upgrade.py", project.refresh_project(proj))

    def test_up_to_date_does_nothing(self):
        result = _script(_new(), _env(INSTALLED))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("is the latest", result.stdout)
        self.assertNotIn("pip", result.stdout)

    def test_newer_release_upgrades_then_refreshes(self):
        proj = _new()
        latest = _bump(INSTALLED)
        env = _env(latest)
        result = _script(proj, env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"pip install -q -U cleanvibe=={latest}", result.stdout)
        self.assertIn(f"cleanvibe.cli refresh {proj.resolve()}", result.stdout)
        self.assertFalse((Path(env["CLEANVIBE_HOME"]) / "upgrade.lock").exists())

    def test_check_only_says_and_runs_nothing(self):
        result = _script(_new(), _env(_bump(INSTALLED)), "--check")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Would upgrade", result.stdout)
        self.assertNotIn("$ ", result.stdout)

    def test_a_held_lock_is_waited_for_and_a_stale_one_cleared(self):
        proj = _new()
        env = _env(_bump(INSTALLED))
        lock = Path(env["CLEANVIBE_HOME"]) / "upgrade.lock"
        lock.write_text("1", encoding="utf-8")
        old = time.time() - 16 * 60
        os.utime(lock, (old, old))
        result = _script(proj, env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("pip install", result.stdout)

    def test_unreadable_pypi_fails_softly(self):
        env = _env(INSTALLED, CLEANVIBE_PYPI_JSON=os.path.join(tempfile.mkdtemp(), "missing.json"))
        result = _script(_new(), env)
        self.assertEqual(result.returncode, 1)
        self.assertIn("try again next tick", result.stdout)


class TestHookNotice(unittest.TestCase):
    def test_tick_says_when_a_newer_release_is_out(self):
        proj = _new()
        latest = _bump(INSTALLED)
        result = _hook(proj, _env(latest))
        self.assertEqual(result.returncode, 0)
        self.assertIn(f"cleanvibe {latest} is out (installed: {INSTALLED})", result.stdout)
        self.assertIn("cleanvibe_upgrade.py", result.stdout)

    def test_no_notice_when_current_and_the_answer_is_cached(self):
        proj = _new()
        env = _env(INSTALLED)
        self.assertNotIn("is out", _hook(proj, env).stdout)
        cache = Path(env["CLEANVIBE_HOME"]) / "latest.json"
        self.assertEqual(json.loads(cache.read_text(encoding="utf-8"))["version"], INSTALLED)
        # Within 6 hours the cache answers, not PyPI.
        Path(env["CLEANVIBE_PYPI_JSON"]).write_text(
            json.dumps({"info": {"version": _bump(INSTALLED)}}), encoding="utf-8")
        self.assertNotIn("is out", _hook(proj, env).stdout)

    def test_user_prompts_get_no_notice(self):
        result = _hook(_new(), _env(_bump(INSTALLED)), prompt="hello")
        self.assertEqual(result.stdout, "")

    def test_template_constant_matches_scaffold(self):
        proj = _new()
        self.assertEqual(
            (proj / ".claude/scripts/cleanvibe_upgrade.py").read_text(encoding="utf-8"),
            templates.CLEANVIBE_UPGRADE_PY)


if __name__ == "__main__":
    unittest.main()
