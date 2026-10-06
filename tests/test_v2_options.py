"""cleanvibe 2 creation options: --visibility, --prompt, and the name record."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("CLEANVIBE_CLAUDE_CONFIG", os.path.join(tempfile.gettempdir(), "cv-test-claude.json"))

from cleanvibe import cli, templates  # noqa: E402
from cleanvibe.project import new_project  # noqa: E402

PROMPT = 'Build a "todo" app & keep it 100% simple!\nThanks'


class TestCmdSafe(unittest.TestCase):
    def test_every_unsafe_character_is_replaced(self):
        out = templates.cmd_safe(PROMPT)
        self.assertFalse(templates._PROMPT_UNSAFE.intersection(out))
        self.assertEqual(out, "Build a 'todo' app and keep it 100 percent simple. Thanks")


class TestFirstPrompt(unittest.TestCase):
    def test_starting_prompt_is_appended_last(self):
        p = templates.v2_first_prompt("/x/p", False, None, PROMPT)
        self.assertTrue(p.endswith(templates.cmd_safe(PROMPT)))
        self.assertIn("was also given this starting prompt, from me:", p)

    def test_no_prompt_no_tail(self):
        self.assertNotIn("starting prompt", templates.v2_first_prompt("/x/p", False))


class TestProjectFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def make(self, name, **kw):
        path = Path(self.tmp.name) / name
        with mock.patch("cleanvibe.project._git_init"):
            new_project(path, no_claude=True, **kw)
        return path

    def test_marker_and_claude_md_record_the_options(self):
        path = self.make("tea", visibility="public", prompt=PROMPT)
        marker = json.loads((path / ".cleanvibe.json").read_text(encoding="utf-8"))
        self.assertEqual(marker["visibility"], "public")
        self.assertEqual(marker["starting_prompt"], PROMPT)
        md = (path / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("**Name:** custom", md)
        self.assertIn("**Repository:** `public`", md)
        self.assertIn("**Starting prompt:** the user gave one", md)

    def test_auto_named_without_options(self):
        path = self.make("golden-swift-otter", auto_named=True)
        marker = json.loads((path / ".cleanvibe.json").read_text(encoding="utf-8"))
        self.assertNotIn("visibility", marker)
        self.assertNotIn("starting_prompt", marker)
        md = (path / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("**Name:** auto-generated", md)
        self.assertIn("placeholder passphrase", md)
        self.assertIn("**Starting prompt:** none was given.", md)

    def test_keep_going_rule(self):
        md = (self.make("p") / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("**Keep going without asking.**", md)


class TestCli(unittest.TestCase):
    def test_new_accepts_the_options(self):
        args = cli.build_parser().parse_args(
            ["new", "x", "--visibility", "local", "--prompt", "hello"])
        self.assertEqual(cli._create_opts(args), {"visibility": "local", "prompt": "hello"})

    def test_bare_cleanvibe_accepts_the_options(self):
        args = cli.build_parser().parse_args(["--visibility", "public"])
        self.assertEqual(cli._create_opts(args)["visibility"], "public")

    def test_bad_visibility_is_refused(self):
        with self.assertRaises(SystemExit):
            cli.build_parser().parse_args(["new", "x", "--visibility", "shared"])


if __name__ == "__main__":
    unittest.main()
