"""Tests for cleanvibe.replicate — stdlib unittest, no network.

fetch_paper is monkeypatched so nothing hits the arXiv API.
"""

import io
import json
import os
import tempfile
import unittest
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cleanvibe.arxiv import ArxivPaper
from cleanvibe.replicate import replicate_project


def _paper() -> ArxivPaper:
    return ArxivPaper(
        arxiv_id="1706.03762",
        title="Attention Is All You Need",
        authors=("Ashish Vaswani", "Noam Shazeer"),
        summary="A new simple network architecture called the Transformer.",
        published="2017-06-12T17:57:34Z",
        pdf_url="https://arxiv.org/pdf/1706.03762v5.pdf",
    )


SLUG = "attention-is-all-you-need"


@contextmanager
def _in_tmp_cwd():
    with tempfile.TemporaryDirectory() as tmp:
        prev = os.getcwd()
        os.chdir(tmp)
        try:
            yield Path(tmp)
        finally:
            os.chdir(prev)


def _run(**kwargs):
    """Run replicate_project with fetch_paper patched, stdout captured."""
    buf = io.StringIO()
    with patch("cleanvibe.replicate.fetch_paper", return_value=_paper()):
        with redirect_stdout(buf):
            replicate_project("1706.03762", no_claude=True, **kwargs)
    return buf.getvalue()


class TestReplicateScaffold(unittest.TestCase):
    def test_writes_expected_tree(self):
        with _in_tmp_cwd():
            _run()
            target = Path(f"replicating-{SLUG}")
            self.assertTrue(target.is_dir())
            for rel in (
                "CLAUDE.md",
                "queue.md",
                "README.md",
                "SKILL.md",
                "paper.json",
                "download_paper.py",
                ".gitignore",
                "data_lake/.gitkeep",
                "replication_target/.gitkeep",
                ".github/workflows/pages.yml",
                ".github/workflows/package.yml",
            ):
                self.assertTrue((target / rel).is_file(), f"missing {rel}")
            self.assertTrue((target / ".git").is_dir(), "git repo not initialized")

            meta = json.loads((target / "paper.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["arxiv_id"], "1706.03762")
            self.assertEqual(meta["authors"], ["Ashish Vaswani", "Noam Shazeer"])

            skill = (target / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("arXiv:1706.03762", skill)
            self.assertIn("Attention Is All You Need", skill)

    def test_paper_not_in_data_lake(self):
        with _in_tmp_cwd():
            _run()
            target = Path(f"replicating-{SLUG}")
            # data_lake holds only the placeholder — the paper never goes here.
            self.assertEqual(
                [p.name for p in (target / "data_lake").iterdir()], [".gitkeep"]
            )
            # The paper's home is replication_target/ (gitignored), not data_lake.
            gitignore = (target / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("replication_target/*.pdf", gitignore)
            self.assertFalse((target / "data_lake" / "paper.pdf").exists())

    def test_naming_and_collision_suffix(self):
        with _in_tmp_cwd():
            _run()
            _run()
            _run()
            self.assertTrue(Path(f"replicating-{SLUG}").is_dir())
            self.assertTrue(Path(f"replicating-{SLUG}-2").is_dir())
            self.assertTrue(Path(f"replicating-{SLUG}-3").is_dir())

    def test_explicit_path(self):
        with _in_tmp_cwd():
            _run(path=Path("my-repro"))
            self.assertTrue((Path("my-repro") / "SKILL.md").is_file())

    def test_dry_run_writes_nothing(self):
        with _in_tmp_cwd():
            out = _run(dry_run=True)
            self.assertFalse(
                Path(f"replicating-{SLUG}").exists(),
                "dry-run must not create the directory",
            )
            self.assertIn("[dry-run]", out)
            self.assertIn("1706.03762", out)


if __name__ == "__main__":
    unittest.main()
