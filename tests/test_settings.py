import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from cleanvibe import settings, skills, templates
from cleanvibe.cli import main


class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = os.environ.get("CLEANVIBE_HOME")
        os.environ["CLEANVIBE_HOME"] = self.tmp.name

    def tearDown(self):
        if self.old is None:
            os.environ.pop("CLEANVIBE_HOME", None)
        else:
            os.environ["CLEANVIBE_HOME"] = self.old
        self.tmp.cleanup()

    def test_private_actions_off_by_default(self):
        self.assertIs(settings.get("actions_on_private"), False)

    def test_set_and_read_back(self):
        settings.set_value("actions_on_private", "yes")
        self.assertIs(settings.get("actions_on_private"), True)
        saved = json.loads(Path(self.tmp.name, "config.json").read_text())
        self.assertEqual(saved, {"actions_on_private": True})

    def test_bad_value_and_unknown_name(self):
        with self.assertRaises(ValueError):
            settings.set_value("actions_on_private", "maybe")
        with self.assertRaises(KeyError):
            settings.get("nope")
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as cm:
            main(["config", "nope"])
        self.assertEqual(cm.exception.code, 2)

    def test_cli_prints_and_sets(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as cm:
            main(["config", "actions_on_private"])
        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().strip(), "false")
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            main(["config", "actions_on_private", "true"])
        self.assertIs(settings.get("actions_on_private"), True)

    def test_corrupt_file_falls_back_to_defaults(self):
        Path(self.tmp.name, "config.json").write_text("{not json")
        self.assertIs(settings.get("actions_on_private"), False)


class PrivateReposSpendNoMinutesTest(unittest.TestCase):
    def test_skill_gates_ci_on_the_setting(self):
        body = skills.SKILLS["queue-driven-workflow"]
        self.assertIn("cleanvibe config actions_on_private", body)
        self.assertIn("A **private** repo gets no CI workflow", body)

    def test_pages_build_skips_private_pushes(self):
        yml = templates.REPLICATION_PAGES_YML
        build = yml[yml.index("  build:"):yml.index("    steps:")]
        self.assertIn("!github.event.repository.private", build)
        self.assertIn("workflow_dispatch", build)


if __name__ == "__main__":
    unittest.main()
