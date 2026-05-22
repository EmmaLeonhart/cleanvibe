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

from cleanvibe import cli
from cleanvibe.arxiv import ArxivPaper
from cleanvibe.replicate import replicate_manual_project, replicate_project


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
                "devlog.md",
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
            # devlog.md and queue.md both reference the devlog workflow
            devlog = (target / "devlog.md").read_text(encoding="utf-8")
            self.assertIn(f"replicating-{SLUG}", devlog)
            self.assertIn("queue.md", devlog)
            self.assertIn("devlog.md", (target / "queue.md").read_text(encoding="utf-8"))

            meta = json.loads((target / "paper.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["arxiv_id"], "1706.03762")
            self.assertEqual(meta["authors"], ["Ashish Vaswani", "Noam Shazeer"])

            skill = (target / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("arXiv:1706.03762", skill)
            self.assertIn("Attention Is All You Need", skill)

    def test_recipe_first_and_html_preference(self):
        with _in_tmp_cwd():
            _run()
            target = Path(f"replicating-{SLUG}")
            queue = (target / "queue.md").read_text(encoding="utf-8")
            skill = (target / "SKILL.md").read_text(encoding="utf-8")
            # The recipe-first step is present in both the queue and the skill.
            self.assertIn("existing replication recipe", queue)
            self.assertIn("follow it first", queue.lower())
            self.assertIn("existing replication recipe", skill)
            # HTML is preferred over the PDF for the downloaded source.
            self.assertIn("paper.html", queue)
            download = (target / "download_paper.py").read_text(encoding="utf-8")
            self.assertIn("paper.html", download)

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


def _run_manual(folder="my-paper", **kwargs):
    buf = io.StringIO()
    with redirect_stdout(buf):
        replicate_manual_project(folder, no_claude=True, **kwargs)
    return buf.getvalue()


class TestReplicateManual(unittest.TestCase):
    def test_writes_expected_tree_without_arxiv_artifacts(self):
        with _in_tmp_cwd():
            _run_manual("my-paper")
            target = Path("my-paper")
            self.assertTrue(target.is_dir())
            for rel in (
                "CLAUDE.md",
                "queue.md",
                "devlog.md",
                "README.md",
                "SKILL.md",
                ".gitignore",
                "data_lake/.gitkeep",
                "replication_target/.gitkeep",
                ".github/workflows/pages.yml",
                ".github/workflows/package.yml",
            ):
                self.assertTrue((target / rel).is_file(), f"missing {rel}")
            self.assertTrue((target / ".git").is_dir(), "git repo not initialized")
            # Manual mode has NO arXiv fetch artifacts.
            self.assertFalse((target / "download_paper.py").exists())
            self.assertFalse((target / "paper.json").exists())
            # The scaffold says, up front, that the user supplies the paper.
            claude = (target / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("manual drop-in", claude.lower())
            self.assertIn("replication_target/", claude)
            queue = (target / "queue.md").read_text(encoding="utf-8")
            self.assertIn("STOP and ask the user", queue)
            skill = (target / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("name: replicate-my-paper", skill)

    def test_recipe_first_step_present(self):
        with _in_tmp_cwd():
            _run_manual("my-paper")
            target = Path("my-paper")
            queue = (target / "queue.md").read_text(encoding="utf-8")
            skill = (target / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("existing replication recipe", queue)
            self.assertIn("existing replication recipe", skill)

    def test_non_destructive_injection(self):
        """A pre-existing folder with a dropped paper / custom file is kept."""
        with _in_tmp_cwd():
            target = Path("dropped")
            (target / "replication_target").mkdir(parents=True)
            (target / "replication_target" / "paper.pdf").write_bytes(b"%PDF-1.7 fake")
            (target / "README.md").write_text("MY OWN README", encoding="utf-8")
            _run_manual("dropped")
            # The dropped paper survives.
            self.assertEqual(
                (target / "replication_target" / "paper.pdf").read_bytes(),
                b"%PDF-1.7 fake",
            )
            # The user's own README is not overwritten.
            self.assertEqual(
                (target / "README.md").read_text(encoding="utf-8"), "MY OWN README"
            )
            # But the rest of the scaffold is still injected.
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertTrue((target / "CLAUDE.md").is_file())

    def test_paper_pattern_gitignored(self):
        with _in_tmp_cwd():
            _run_manual("p")
            gi = (Path("p") / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("replication_target/*.pdf", gi)

    def test_dry_run_writes_nothing(self):
        with _in_tmp_cwd():
            out = _run_manual("ghost", dry_run=True)
            self.assertFalse(Path("ghost").exists())
            self.assertIn("[dry-run]", out)
            self.assertIn("manual", out.lower())


class TestReplicateCliDispatch(unittest.TestCase):
    """The single positional arg routes to arXiv mode or folder mode."""

    def test_folder_name_routes_to_manual(self):
        with _in_tmp_cwd():
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.main(["replicate", "some-cool-paper", "--no-claude"])
            self.assertTrue((Path("some-cool-paper") / "SKILL.md").is_file())
            self.assertFalse((Path("some-cool-paper") / "paper.json").exists())

    def test_arxiv_ref_routes_to_arxiv_mode(self):
        with _in_tmp_cwd():
            buf = io.StringIO()
            with patch("cleanvibe.replicate.fetch_paper", return_value=_paper()):
                with redirect_stdout(buf):
                    cli.main(
                        ["replicate", "https://www.alphaxiv.org/overview/1706.03762",
                         "--no-claude"]
                    )
            target = Path(f"replicating-{SLUG}")
            self.assertTrue((target / "paper.json").is_file())
            self.assertTrue((target / "download_paper.py").is_file())


if __name__ == "__main__":
    unittest.main()
