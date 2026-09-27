"""Tests for cleanvibe.trust — pre-trusting a folder cleanvibe just created.

Every test uses its own temporary config file; the real ~/.claude.json is never
read or written.
"""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from cleanvibe import project, trust

os.environ["CLEANVIBE_CLAUDE_CONFIG"] = os.path.join(
    tempfile.mkdtemp(prefix="cleanvibe-tests-"), ".claude.json"
)


def _config(data):
    path = Path(tempfile.mkdtemp()) / ".claude.json"
    path.write_text(data if isinstance(data, str) else json.dumps(data, indent=2), encoding="utf-8")
    return path


class TestMarkTrusted(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp()) / "new-project"
        self.folder.mkdir()
        self.key = trust.project_key(self.folder)

    def test_marks_only_that_folder_and_keeps_everything_else(self):
        other = {"hasTrustDialogAccepted": False, "allowedTools": ["x"]}
        config = _config({"numStartups": 7, "projects": {"C:/elsewhere": other}})
        self.assertTrue(trust.mark_trusted(self.folder, config))
        data = json.loads(config.read_text(encoding="utf-8"))
        self.assertEqual(data["numStartups"], 7)
        self.assertEqual(data["projects"]["C:/elsewhere"], other)
        self.assertIs(data["projects"][self.key]["hasTrustDialogAccepted"], True)

    def test_backs_up_before_writing(self):
        original = json.dumps({"projects": {}}, indent=2)
        config = _config(original)
        trust.mark_trusted(self.folder, config)
        backup = config.with_name(".claude.json.cleanvibe-backup")
        self.assertEqual(backup.read_text(encoding="utf-8"), original)

    def test_already_trusted_is_not_rewritten(self):
        config = _config({"projects": {self.key: {"hasTrustDialogAccepted": True}}})
        before = config.read_bytes()
        self.assertTrue(trust.mark_trusted(self.folder, config))
        self.assertEqual(config.read_bytes(), before)
        self.assertFalse(config.with_name(".claude.json.cleanvibe-backup").exists())

    def test_missing_config_is_never_created(self):
        config = Path(tempfile.mkdtemp()) / ".claude.json"
        self.assertFalse(trust.mark_trusted(self.folder, config))
        self.assertFalse(config.exists())

    def test_unreadable_or_odd_config_is_left_untouched(self):
        for text in ("{not json", "[1, 2]", json.dumps({"projects": []}),
                     json.dumps({"projects": {"KEY": "not a dict"}}).replace("KEY", self.key.replace("\\", "\\\\"))):
            with self.subTest(text=text[:30]):
                config = _config(text)
                self.assertFalse(trust.mark_trusted(self.folder, config))
                self.assertEqual(config.read_text(encoding="utf-8"), text)

    def test_project_key_is_absolute_with_forward_slashes(self):
        key = trust.project_key(self.folder)
        self.assertNotIn("\\", key)
        self.assertTrue(key.endswith("/new-project"))
        self.assertTrue(Path(key).is_absolute())

    def test_config_path_overrides(self):
        with mock.patch.dict(os.environ, {"CLEANVIBE_CLAUDE_CONFIG": "/x/cfg.json"}):
            self.assertEqual(trust.claude_config_path(), Path("/x/cfg.json"))
        env = {k: v for k, v in os.environ.items() if k != "CLEANVIBE_CLAUDE_CONFIG"}
        env["CLAUDE_CONFIG_DIR"] = "/cfgdir"
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(trust.claude_config_path(), Path("/cfgdir") / ".claude.json")


class TestWhenCleanvibeTrusts(unittest.TestCase):
    def _new(self, **kwargs):
        proj = Path(tempfile.mkdtemp()) / "p"
        with mock.patch.object(project, "mark_trusted", return_value=True) as marked, \
                mock.patch.object(project, "_launch_claude"), redirect_stdout(io.StringIO()):
            project.new_project(proj, **kwargs)
        return proj, marked

    def test_new_project_that_launches_is_trusted(self):
        proj, marked = self._new()
        marked.assert_called_once_with(proj)

    def test_no_launch_no_trust(self):
        _, marked = self._new(no_claude=True)
        marked.assert_not_called()

    def test_opening_an_existing_project_never_trusts(self):
        proj, _ = self._new(no_claude=True)
        with mock.patch.object(project, "mark_trusted") as marked, \
                mock.patch.object(project, "_launch_claude"), redirect_stdout(io.StringIO()):
            project.open_project(proj)
        marked.assert_not_called()


if __name__ == "__main__":
    unittest.main()
