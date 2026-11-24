"""Tests for the private-repo Actions guard in the UserPromptSubmit hook (2.0.14).

The hook's source is loaded into a namespace and its `git` and `_gh` helpers
are replaced with fakes, so nothing touches GitHub or a real repo.
"""

import io
import json
import os
import tempfile
import types
import unittest
from contextlib import redirect_stdout

from cleanvibe import templates


def _load_hook():
    mod = types.ModuleType("intent_staleness_hook")
    exec(compile(templates.INTENT_STALENESS_PY, "intent_staleness.py", "exec"), mod.__dict__)
    return mod


class _Result:
    def __init__(self, out="", code=0):
        self.stdout, self.returncode = out, code


class TestPrivateCiGuard(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="cleanvibe-home-")
        self.root = tempfile.mkdtemp(prefix="cleanvibe-proj-")
        self.gitdir = os.path.join(self.root, ".git")
        os.makedirs(self.gitdir)
        self._old_home = os.environ.get("CLEANVIBE_HOME")
        os.environ["CLEANVIBE_HOME"] = self.home
        self.hook = _load_hook()
        self.calls = []
        self.private = "true"
        self.enabled = "true"
        self.url = "https://github.com/someone/thing.git"

        def fake_git(root, *args):
            if args[:1] == ("rev-parse",):
                return self.gitdir
            if args[:2] == ("remote", "get-url"):
                return self.url
            return ""

        def fake_gh(*args):
            self.calls.append(args)
            if args[-2:] == ("-q", ".private"):
                return _Result(self.private)
            if args[-2:] == ("-q", ".enabled"):
                return _Result(self.enabled)
            return _Result("")

        self.hook.git = fake_git
        self.hook._gh = fake_gh

    def tearDown(self):
        if self._old_home is None:
            os.environ.pop("CLEANVIBE_HOME", None)
        else:
            os.environ["CLEANVIBE_HOME"] = self._old_home

    def _run(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.hook.private_ci_guard(self.root)
        return buf.getvalue()

    def _put_calls(self):
        return [c for c in self.calls if "PUT" in c]

    def test_private_repo_with_actions_on_gets_it_turned_off(self):
        out = self._run()
        self.assertEqual(len(self._put_calls()), 1)
        self.assertIn("repos/someone/thing/actions/permissions", self._put_calls()[0])
        self.assertIn("enabled=false", self._put_calls()[0])
        self.assertIn("turned off", out)

    def test_public_repo_is_left_alone(self):
        self.private = "false"
        self.assertEqual(self._run(), "")
        self.assertEqual(self._put_calls(), [])

    def test_actions_already_off_says_nothing(self):
        self.enabled = "false"
        self.assertEqual(self._run(), "")
        self.assertEqual(self._put_calls(), [])

    def test_machine_setting_allows_it(self):
        with open(os.path.join(self.home, "config.json"), "w", encoding="utf-8") as f:
            json.dump({"actions_on_private": True}, f)
        self._run()
        self.assertEqual(self.calls, [])

    def test_project_marker_allows_it(self):
        with open(os.path.join(self.root, ".cleanvibe.json"), "w", encoding="utf-8") as f:
            json.dump({"actions_on_private": True}, f)
        self._run()
        self.assertEqual(self.calls, [])

    def test_non_github_remote_does_nothing(self):
        self.url = "https://gitlab.com/someone/thing.git"
        self._run()
        self.assertEqual(self.calls, [])

    def test_checks_at_most_once_an_hour(self):
        self.private = "false"
        self._run()
        first = len(self.calls)
        self._run()
        self.assertEqual(len(self.calls), first)

    def test_ssh_remote_is_parsed(self):
        self.url = "git@github.com:someone/thing.git"
        self._run()
        self.assertIn("repos/someone/thing/actions/permissions", self._put_calls()[0])


class TestRulesWording(unittest.TestCase):
    def test_rules_do_not_list_ci_as_a_general_practice(self):
        rules = templates.v2_rules_md()
        self.assertNotIn("tests, CI)", rules)
        self.assertIn("No GitHub Actions on private repos", rules)


if __name__ == "__main__":
    unittest.main()
