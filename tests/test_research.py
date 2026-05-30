"""Tests for cleanvibe.research — stdlib unittest, no network, no Claude launch.

`cleanvibe research` scaffolds an original-research project: like `new` (fresh
project, data_lake, three-cron playbook) but with an up-front literature-review
step and a published, themed GitHub Pages report under docs/.
"""

import io
import platform
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cleanvibe import templates
from cleanvibe.cli import main
from cleanvibe.research import research_project

IS_WINDOWS = platform.system() == "Windows"


def _make(name="reservoiragent", question=None, **kwargs):
    """Scaffold a research project in a temp dir; return (tmp_path, project_path)."""
    tmp = tempfile.mkdtemp()
    proj = Path(tmp) / name
    buf = io.StringIO()
    with redirect_stdout(buf):
        research_project(proj, question=question, no_claude=True, **kwargs)
    return proj, buf.getvalue()


class TestResearchScaffold(unittest.TestCase):
    def test_writes_expected_tree(self):
        proj, _ = _make()
        for rel in (
            "CLAUDE.md",
            "README.md",
            "queue.md",
            "devlog.md",
            ".gitignore",
            "data_lake/.gitkeep",
            "literature/.gitkeep",
            "docs/index.html",
            "docs/.nojekyll",
            ".github/workflows/pages.yml",
        ):
            self.assertTrue((proj / rel).is_file(), f"missing {rel}")
        self.assertTrue((proj / ".git").is_dir(), "git repo not initialized")

    def test_initial_branch_is_main(self):
        proj, _ = _make()
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=proj, capture_output=True, text=True,
        ).stdout.strip()
        self.assertEqual(branch, "main")

    def test_runclaude_bat_only_on_windows(self):
        proj, _ = _make()
        runclaude = proj / "!runClaude.bat"
        if IS_WINDOWS:
            self.assertTrue(runclaude.is_file())
        else:
            self.assertFalse(runclaude.exists())

    def test_queue_has_literature_review_before_building(self):
        # The distinctive research step: a literature review (agentic RAG) that
        # comes BEFORE any building.
        proj, _ = _make()
        queue = (proj / "queue.md").read_text(encoding="utf-8")
        lower = queue.lower()
        self.assertIn("literature review", lower)
        self.assertIn("agentic rag", lower)
        self.assertIn("literature/", queue)
        self.assertIn("review.md", lower)
        # It is positioned before the experiment/build step and before the
        # "replace this bootstrap queue" handoff.
        lit_idx = lower.find("literature review (agentic rag)")
        plan_idx = lower.find("create `todo.md`")
        self.assertGreater(lit_idx, 0)
        self.assertGreater(plan_idx, lit_idx,
                           "literature review must precede writing the research plan")

    def test_queue_defines_research_question_step(self):
        proj, _ = _make()
        queue = (proj / "queue.md").read_text(encoding="utf-8")
        lower = queue.lower()
        self.assertIn("define the research question", lower)
        self.assertTrue("interview" in lower or "ask the user" in lower)

    def test_queue_has_three_cron_playbook(self):
        # Research IS extensive work -> keeps the three-cron playbook (unlike
        # replication, which is exempt).
        proj, _ = _make()
        queue = (proj / "queue.md").read_text(encoding="utf-8")
        lower = queue.lower()
        self.assertIn("croncreate", lower)
        self.assertIn("work-loop", lower)
        self.assertIn("auto-flush", lower)
        self.assertIn("status-report", lower)
        self.assertIn("3 * * * *", queue)
        self.assertIn("15 * * * *", queue)
        self.assertIn("42 * * * *", queue)
        self.assertIn("start the three-cron playbook", lower)

    def test_queue_goes_public_for_pages(self):
        # Research publishes a GitHub Pages report, so the repo must be PUBLIC.
        proj, _ = _make()
        queue = (proj / "queue.md").read_text(encoding="utf-8")
        self.assertIn("--public", queue)
        self.assertIn("Pages", queue)

    def test_docs_index_is_themed(self):
        proj, _ = _make(name="myresearch", question="Does X cause Y?")
        html = (proj / "docs" / "index.html").read_text(encoding="utf-8")
        # The warm "paper" theme + dark-mode variant from the reference site.
        self.assertIn("--accent: #b8553a", html)
        self.assertIn("prefers-color-scheme: dark", html)
        self.assertIn("#d97757", html)  # dark-mode accent
        # Project name + question are interpolated into the page.
        self.assertIn("myresearch", html)
        self.assertIn("Does X cause Y?", html)
        # No unfilled placeholders leaked through.
        self.assertNotIn("__PROJECT_NAME__", html)
        self.assertNotIn("__QUESTION__", html)
        self.assertNotIn("__DATE__", html)
        self.assertNotIn("__REPORT_CSS__", html)

    def test_shares_theme_with_replication(self):
        # research and replicate use ONE report theme (CLEANVIBE_REPORT_CSS).
        proj, _ = _make()
        html = (proj / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn(templates.CLEANVIBE_REPORT_CSS, html)
        # The shared theme carries the replication status-badge styles too.
        self.assertIn(".status-badge", templates.CLEANVIBE_REPORT_CSS)

    def test_pages_yml_deploys_docs_and_builds_pdf(self):
        proj, _ = _make()
        yml = (proj / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        self.assertIn("path: docs", yml)
        self.assertIn("deploy-pages", yml)
        self.assertIn("FINDINGS.md", yml)
        self.assertIn("report.pdf", yml)
        # Auto-enables Pages so a fresh public repo doesn't 404 on deploy.
        self.assertIn("configure-pages", yml)
        self.assertIn("enablement: true", yml)

    def test_claude_md_research_sections(self):
        proj, _ = _make(question="What is the capacity of a reservoir agent?")
        claude = (proj / "CLAUDE.md").read_text(encoding="utf-8")
        lower = claude.lower()
        self.assertIn("research project", lower)
        self.assertIn("research workflow", lower)
        self.assertIn("literature review", lower)
        self.assertIn("literature/", claude)
        # The question is embedded.
        self.assertIn("What is the capacity of a reservoir agent?", claude)
        # v1.14.0: the shared workflow/cron/emergency blocks moved to skills.
        # CLAUDE.md carries the Skills pointer; the prose lives in vendored skills.
        self.assertIn("## Skills", claude)
        self.assertIn("autonomous-loop", claude)
        loop = (proj / ".claude" / "skills" / "autonomous-loop" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("three-cron playbook", loop.lower())
        stop = (proj / ".claude" / "skills" / "emergency-stop" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Emergency Stop Mode", stop)

    def test_question_placeholder_when_absent(self):
        proj, _ = _make()  # no question
        claude = (proj / "CLAUDE.md").read_text(encoding="utf-8")
        readme = (proj / "README.md").read_text(encoding="utf-8")
        self.assertIn("not yet defined", claude.lower())
        self.assertIn("not yet defined", readme.lower())

    def test_gitignore_keeps_docs_but_ignores_results(self):
        proj, _ = _make()
        gi = (proj / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("results/", gi)
        # No ignore RULE for docs/ (a rule is a line starting with docs/); the
        # report site is committed. (Comments may still mention "docs/".)
        self.assertNotIn("\ndocs/", gi)
        self.assertFalse(gi.startswith("docs/"))


class TestResearchDryRun(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "ghost"
            buf = io.StringIO()
            with redirect_stdout(buf):
                research_project(proj, dry_run=True, no_claude=True)
            self.assertFalse(proj.exists(), "dry-run must not create the directory")
            out = buf.getvalue()
            self.assertIn("[dry-run]", out)
            # Path separator is OS-specific; just check the themed site is listed.
            self.assertIn("index.html", out)


class TestResearchCliDispatch(unittest.TestCase):
    def test_research_subcommand(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["research", str(proj), "--no-claude"])
            self.assertTrue((proj / "docs" / "index.html").is_file())
            self.assertTrue((proj / "literature" / ".gitkeep").is_file())

    def test_new_research_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["new", str(proj), "--research", "--no-claude"])
            # Routed to the research scaffold (has docs/ + literature/), not the
            # plain `new` one.
            self.assertTrue((proj / "docs" / "index.html").is_file())
            self.assertTrue((proj / "literature" / ".gitkeep").is_file())

    def test_question_flag_threaded_through(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["research", str(proj), "--question", "Why does Z happen?",
                      "--no-claude"])
            readme = (proj / "README.md").read_text(encoding="utf-8")
            html = (proj / "docs" / "index.html").read_text(encoding="utf-8")
            self.assertIn("Why does Z happen?", readme)
            self.assertIn("Why does Z happen?", html)

    def test_plain_new_is_not_research(self):
        # Regression: `cleanvibe new` (no --research) must NOT produce a research
        # scaffold (no docs/ site, no literature/).
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["new", str(proj), "--no-claude"])
            self.assertFalse((proj / "docs").exists())
            self.assertFalse((proj / "literature").exists())


if __name__ == "__main__":
    unittest.main()
