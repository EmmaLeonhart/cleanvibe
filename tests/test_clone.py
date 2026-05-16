"""Tests for the reworked cleanvibe.clone_project — stdlib unittest, no network.

A local temp git repo stands in as the clone source (file path), so no
network is needed. Git identity is forced via env vars so commits work even
where no global git identity is configured.
"""

import io
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cleanvibe.scaffold import CLONE_BRANCH, clone_project


_GIT_ENV = {
    "GIT_AUTHOR_NAME": "cleanvibe-test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "cleanvibe-test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def _git(*args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )


def _make_source_repo(root: Path, extra_files=None) -> Path:
    """Create a tiny git repo with one commit on its default branch."""
    src = root / "source"
    src.mkdir()
    (src / "main.py").write_text("print('hello')\n", encoding="utf-8")
    for name, content in (extra_files or {}).items():
        (src / name).write_text(content, encoding="utf-8")
    _git("init", cwd=src)
    _git("add", "-A", cwd=src)
    _git("commit", "-m", "initial source commit", cwd=src)
    return src


def _clone(src: Path, dest: Path) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        clone_project(str(src), dest, no_claude=True)
    return buf.getvalue()


class TestCloneOnboarding(unittest.TestCase):
    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in _GIT_ENV}
        os.environ.update(_GIT_ENV)

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_onboarding_branch_and_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = _make_source_repo(root)
            dest = root / "cloned"
            _clone(src, dest)

            self.assertTrue((dest / ".git").is_dir())
            branch = _git("rev-parse", "--abbrev-ref", "HEAD", cwd=dest).stdout.strip()
            self.assertEqual(branch, CLONE_BRANCH)

            # Onboarding files present, with onboarding content.
            claude = (dest / "CLAUDE.md").read_text(encoding="utf-8")
            queue = (dest / "queue.md").read_text(encoding="utf-8")
            self.assertIn("cleanvibe-onboarding", claude)
            self.assertIn("Onboarding", queue)

            # No data_lake/, and cleanvibe did NOT inject a README.
            self.assertFalse((dest / "data_lake").exists())
            self.assertFalse((dest / "README.md").exists())

            # Pre-existing repo content preserved.
            self.assertTrue((dest / "main.py").is_file())

            # A commit exists on the onboarding branch.
            log = _git("log", "-1", "--pretty=%s", cwd=dest).stdout
            self.assertIn("cleanvibe onboarding scaffold", log)

    def test_default_branch_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = _make_source_repo(root)
            dest = root / "cloned"
            _clone(src, dest)

            branches = _git(
                "branch", "--format=%(refname:short)", cwd=dest
            ).stdout.split()
            base = next(b for b in branches if b != CLONE_BRANCH)
            # The base branch must not have the injected onboarding CLAUDE.md.
            show = _git("show", f"{base}:CLAUDE.md", cwd=dest)
            self.assertNotEqual(show.returncode, 0, "CLAUDE.md leaked onto base branch")

    def test_prepend_preserves_existing_files(self):
        sentinel = "# Existing project CLAUDE\nORIGINAL_SENTINEL_TEXT\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = _make_source_repo(root, extra_files={"CLAUDE.md": sentinel})
            dest = root / "cloned"
            _clone(src, dest)

            claude = (dest / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("ORIGINAL_SENTINEL_TEXT", claude)  # original kept
            self.assertIn("cleanvibe-onboarding", claude)     # block added
            # Onboarding block is on top (newest first).
            self.assertLess(
                claude.index("cleanvibe-onboarding"),
                claude.index("ORIGINAL_SENTINEL_TEXT"),
            )

    def test_dry_run_clones_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = _make_source_repo(root)
            dest = root / "cloned"
            buf = io.StringIO()
            with redirect_stdout(buf):
                clone_project(str(src), dest, dry_run=True, no_claude=True)
            self.assertFalse(dest.exists())
            out = buf.getvalue()
            self.assertIn("[dry-run]", out)
            self.assertIn(CLONE_BRANCH, out)


if __name__ == "__main__":
    unittest.main()
