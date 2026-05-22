"""Tests for cleanvibe clawRxiv replication mode — stdlib unittest, no network.

fetch_clawrxiv_paper is monkeypatched so nothing hits the clawRxiv API.
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
from cleanvibe.clawrxiv import (
    ClawrxivPaper,
    is_clawrxiv_ref,
    parse_clawrxiv_id,
)
from cleanvibe.replicate import replicate_clawrxiv_project

SLUG = "test-claw-paper"


def _paper(skill_md=None) -> ClawrxivPaper:
    return ClawrxivPaper(
        paper_id="2605.02609",
        title="Test Claw Paper",
        abstract="A short clawRxiv abstract.",
        content="# Test Claw Paper\n\nBody text.\n\n```python\nprint('skill')\n```\n",
        skill_md=skill_md,
        authors=("Dr. A. Author", "OrgOne"),
        claw_name="DNAI-Test-123",
        version="1",
        category="q-bio",
        created_at="2026-05-22 14:06:06",
    )


@contextmanager
def _in_tmp_cwd():
    with tempfile.TemporaryDirectory() as tmp:
        prev = os.getcwd()
        os.chdir(tmp)
        try:
            yield Path(tmp)
        finally:
            os.chdir(prev)


def _run(paper=None, **kwargs):
    buf = io.StringIO()
    paper = paper if paper is not None else _paper()
    with patch("cleanvibe.replicate.fetch_clawrxiv_paper", return_value=paper):
        with redirect_stdout(buf):
            replicate_clawrxiv_project(
                "clawrxiv:2605.02609", no_claude=True, **kwargs
            )
    return buf.getvalue()


class TestClawrxivRef(unittest.TestCase):
    def test_parse_id(self):
        self.assertEqual(parse_clawrxiv_id("clawrxiv:2605.02609"), "2605.02609")
        self.assertEqual(
            parse_clawrxiv_id("https://www.clawrxiv.io/abs/2605.02609"), "2605.02609"
        )
        self.assertEqual(
            parse_clawrxiv_id("https://clawrxiv.io/api/abs/2605.02609v2"), "2605.02609"
        )

    def test_is_clawrxiv_ref_true(self):
        for ref in (
            "https://www.clawrxiv.io/abs/2605.02609",
            "https://clawrxiv.io/abs/2605.02609",
            "clawrxiv.io/abs/2605.02609",
            "clawrxiv:2605.02609",
        ):
            self.assertTrue(is_clawrxiv_ref(ref), ref)

    def test_is_clawrxiv_ref_false(self):
        # Bare arXiv-shaped ids and arXiv URLs are NOT clawRxiv refs.
        for ref in (
            "2605.02609",
            "https://arxiv.org/abs/2605.02609",
            "some-folder-name",
            "https://www.clawrxiv.io/browse",  # references clawrxiv but no id
        ):
            self.assertFalse(is_clawrxiv_ref(ref), ref)

    def test_clawrxiv_ref_is_not_arxiv_ref(self):
        from cleanvibe.arxiv import is_arxiv_ref

        self.assertFalse(is_arxiv_ref("https://www.clawrxiv.io/abs/2605.02609"))
        self.assertFalse(is_arxiv_ref("clawrxiv:2605.02609"))


class TestClawrxivScaffold(unittest.TestCase):
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
                ".gitignore",
                "replication_target/source/paper.md",
                "data_lake/.gitkeep",
                "replication_target/.gitkeep",
                ".github/workflows/pages.yml",
                ".github/workflows/package.yml",
            ):
                self.assertTrue((target / rel).is_file(), f"missing {rel}")
            self.assertTrue((target / ".git").is_dir(), "git repo not initialized")
            # clawRxiv mode has NO download_paper.py (content fetched via API).
            self.assertFalse((target / "download_paper.py").exists())

    def test_content_written_to_source(self):
        with _in_tmp_cwd():
            _run()
            target = Path(f"replicating-{SLUG}")
            body = (target / "replication_target/source/paper.md").read_text(
                encoding="utf-8"
            )
            self.assertEqual(body, _paper().content)

    def test_skill_file_written_when_present(self):
        with _in_tmp_cwd():
            skill = "# SKILL\n\nRun me.\n"
            _run(paper=_paper(skill_md=skill))
            target = Path(f"replicating-{SLUG}")
            self.assertTrue((target / "replication_skill.md").is_file())
            self.assertEqual(
                (target / "replication_skill.md").read_text(encoding="utf-8"), skill
            )
            queue = (target / "queue.md").read_text(encoding="utf-8")
            self.assertIn("already at `replication_skill.md`", queue)

    def test_skill_embedded_when_absent(self):
        with _in_tmp_cwd():
            _run(paper=_paper(skill_md=None))
            target = Path(f"replicating-{SLUG}")
            self.assertFalse((target / "replication_skill.md").exists())
            queue = (target / "queue.md").read_text(encoding="utf-8")
            self.assertIn("embedded in", queue)
            self.assertIn("extract it", queue.lower())

    def test_paper_json_fields(self):
        with _in_tmp_cwd():
            _run()
            target = Path(f"replicating-{SLUG}")
            meta = json.loads((target / "paper.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["source"], "clawrxiv")
            self.assertEqual(meta["paper_id"], "2605.02609")
            self.assertEqual(meta["claw_name"], "DNAI-Test-123")
            self.assertEqual(meta["has_skill_file"], False)
            self.assertEqual(meta["authors"], ["Dr. A. Author", "OrgOne"])

    def test_skill_first_queue(self):
        with _in_tmp_cwd():
            _run()
            target = Path(f"replicating-{SLUG}")
            queue = (target / "queue.md").read_text(encoding="utf-8")
            skill = (target / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Run the skill recipe FIRST", queue)
            self.assertIn("clawRxiv", queue)
            self.assertIn("recipe-first", queue.lower())
            self.assertIn("skill recipe FIRST".lower(), skill.lower())

    def test_dry_run_writes_nothing(self):
        with _in_tmp_cwd():
            out = _run(dry_run=True)
            self.assertFalse(Path(f"replicating-{SLUG}").exists())
            self.assertIn("[dry-run]", out)
            self.assertIn("clawrxiv:2605.02609", out)


class TestClawrxivCliDispatch(unittest.TestCase):
    def test_clawrxiv_url_routes_to_clawrxiv_mode(self):
        with _in_tmp_cwd():
            buf = io.StringIO()
            with patch(
                "cleanvibe.replicate.fetch_clawrxiv_paper", return_value=_paper()
            ):
                with redirect_stdout(buf):
                    cli.main(
                        ["replicate", "https://www.clawrxiv.io/abs/2605.02609",
                         "--no-claude"]
                    )
            target = Path(f"replicating-{SLUG}")
            self.assertTrue((target / "paper.json").is_file())
            meta = json.loads((target / "paper.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["source"], "clawrxiv")
            self.assertFalse((target / "download_paper.py").exists())

    def test_clawrxiv_citation_routes_to_clawrxiv_mode(self):
        with _in_tmp_cwd():
            buf = io.StringIO()
            with patch(
                "cleanvibe.replicate.fetch_clawrxiv_paper", return_value=_paper()
            ):
                with redirect_stdout(buf):
                    cli.main(["replicate", "clawrxiv:2605.02609", "--no-claude"])
            self.assertTrue((Path(f"replicating-{SLUG}") / "paper.json").is_file())


if __name__ == "__main__":
    unittest.main()
