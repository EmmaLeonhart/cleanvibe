"""`cleanvibe new` on an existing non-empty dir prompts (it must not error).

stdlib unittest, no network. The prompt seam `cleanvibe.cli._ask` is
monkeypatched so nothing blocks on real stdin.
"""

import io
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cleanvibe.cli import _suggest_name, main


_GIT_ENV = {
    "GIT_AUTHOR_NAME": "cleanvibe-test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "cleanvibe-test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def _nonempty_dir(root: Path) -> Path:
    d = root / "proj"
    d.mkdir()
    (d / "existing.txt").write_text("hello\n", encoding="utf-8")
    return d


class TestNewPrompt(unittest.TestCase):
    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in _GIT_ENV}
        os.environ.update(_GIT_ENV)

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_yes_converts_in_place_like_convert(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = _nonempty_dir(Path(tmp))
            buf = io.StringIO()
            with patch("cleanvibe.cli._ask", side_effect=["y"]):
                with redirect_stdout(buf):
                    main(["new", str(d), "--no-claude"])
            self.assertTrue((d / ".git").is_dir())
            self.assertTrue((d / "CLAUDE.md").is_file())
            self.assertTrue((d / "existing.txt").is_file())  # original kept
            log = subprocess.run(
                ["git", "log", "--oneline"], cwd=d,
                capture_output=True, text=True,
            ).stdout.strip().splitlines()
            self.assertEqual(len(log), 2, f"expected 2 commits (like convert), got {log}")

    def test_no_creates_under_typed_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = _nonempty_dir(Path(tmp))
            chosen = Path(tmp) / "proj-custom"
            buf = io.StringIO()
            with patch("cleanvibe.cli._ask", side_effect=["n", str(chosen)]):
                with redirect_stdout(buf):
                    main(["new", str(d), "--no-claude"])
            self.assertTrue((chosen / "CLAUDE.md").is_file())
            # The original directory was not converted (no scaffold injected).
            self.assertFalse((d / "CLAUDE.md").exists())

    def test_no_blank_accepts_suggested_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = _nonempty_dir(Path(tmp))
            expected = _suggest_name(d)  # computed BEFORE the dir is created
            self.assertEqual(expected, d.with_name("proj-2"))
            buf = io.StringIO()
            with patch("cleanvibe.cli._ask", side_effect=["n", ""]):
                with redirect_stdout(buf):
                    main(["new", str(d), "--no-claude"])
            self.assertTrue((expected / "CLAUDE.md").is_file())

    def test_dry_run_never_blocks_on_input(self):
        def _boom(prompt):
            raise AssertionError("input() must not be called under --dry-run")

        with tempfile.TemporaryDirectory() as tmp:
            d = _nonempty_dir(Path(tmp))
            buf = io.StringIO()
            with patch("cleanvibe.cli._ask", side_effect=_boom):
                with redirect_stdout(buf):
                    main(["new", str(d), "--dry-run", "--no-claude"])
            out = buf.getvalue()
            self.assertIn("[dry-run]", out)
            self.assertFalse((d / "CLAUDE.md").exists())


if __name__ == "__main__":
    unittest.main()
