"""Tests for cleanvibe.original — stdlib unittest, no network, no Claude launch.

`cleanvibe original` scaffolds an original-research project whose topic is
UNCERTAIN: like `research` (fresh project, data_lake, literature review,
three-cron playbook, themed report) but with an up-front *topic-finding loop*
that discovers and selects the research question before the literature review.
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
from cleanvibe.original import original_project

IS_WINDOWS = platform.system() == "Windows"


def _make(name="driftprobe", area=None, **kwargs):
    """Scaffold an original project in a temp dir; return (project_path, stdout)."""
    tmp = tempfile.mkdtemp()
    proj = Path(tmp) / name
    buf = io.StringIO()
    with redirect_stdout(buf):
        original_project(proj, area=area, no_claude=True, **kwargs)
    return proj, buf.getvalue()


class TestOriginalScaffold(unittest.TestCase):
    def test_writes_expected_tree(self):
        proj, _ = _make()
        for rel in (
            "CLAUDE.md",
            "README.md",
            "queue.md",
            "devlog.md",
            ".gitignore",
            "data_lake/.gitkeep",
            "topics/.gitkeep",
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

    def test_queue_has_topic_finding_before_literature_review(self):
        # The distinctive original step: a topic-finding loop that comes BEFORE
        # the literature review (which itself comes before building).
        proj, _ = _make()
        queue = (proj / "queue.md").read_text(encoding="utf-8")
        lower = queue.lower()
        self.assertIn("topic-finding loop", lower)
        self.assertIn("topics/", queue)
        self.assertIn("topics.md", lower)
        self.assertIn("candidate research question", lower)
        # Topic finding precedes the literature review precedes the research plan.
        topic_idx = lower.find("topic-finding loop — discover")
        lit_idx = lower.find("literature review (agentic rag)")
        plan_idx = lower.find("create `todo.md`")
        self.assertGreater(topic_idx, 0)
        self.assertGreater(lit_idx, topic_idx,
                           "topic finding must precede the literature review")
        self.assertGreater(plan_idx, lit_idx,
                           "literature review must precede writing the research plan")

    def test_queue_still_has_literature_review(self):
        # original keeps everything research has, including the lit review.
        proj, _ = _make()
        lower = (proj / "queue.md").read_text(encoding="utf-8").lower()
        self.assertIn("literature review", lower)
        self.assertIn("agentic rag", lower)
        self.assertIn("review.md", lower)

    def test_queue_has_three_cron_playbook(self):
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
        proj, _ = _make()
        queue = (proj / "queue.md").read_text(encoding="utf-8")
        self.assertIn("--public", queue)
        self.assertIn("Pages", queue)

    def test_docs_index_is_themed(self):
        proj, _ = _make(name="myoriginal", area="reservoir computing")
        html = (proj / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("--accent: #b8553a", html)
        self.assertIn("prefers-color-scheme: dark", html)
        self.assertIn("#d97757", html)  # dark-mode accent
        self.assertIn("myoriginal", html)
        # No unfilled placeholders leaked through.
        self.assertNotIn("__PROJECT_NAME__", html)
        self.assertNotIn("__QUESTION__", html)
        self.assertNotIn("__DATE__", html)
        self.assertNotIn("__REPORT_CSS__", html)

    def test_docs_index_question_is_topic_finding_placeholder(self):
        # The question is unknown at scaffold time; the topic-finding placeholder
        # stands in until the loop selects one.
        proj, _ = _make()
        html = (proj / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("not yet chosen", html.lower())

    def test_shares_theme_with_research_and_replication(self):
        proj, _ = _make()
        html = (proj / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn(templates.CLEANVIBE_REPORT_CSS, html)
        self.assertIn(".status-badge", templates.CLEANVIBE_REPORT_CSS)

    def test_pages_yml_deploys_docs_and_builds_pdf(self):
        proj, _ = _make()
        yml = (proj / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        self.assertIn("path: docs", yml)
        self.assertIn("deploy-pages", yml)
        self.assertIn("FINDINGS.md", yml)
        self.assertIn("report.pdf", yml)
        self.assertIn("configure-pages", yml)
        self.assertIn("enablement: true", yml)

    def test_claude_md_original_sections(self):
        proj, _ = _make(area="vector symbolic architectures")
        claude = (proj / "CLAUDE.md").read_text(encoding="utf-8")
        lower = claude.lower()
        self.assertIn("original-research project", lower)
        self.assertIn("topic-finding", lower)
        self.assertIn("uncertain topic", lower)
        self.assertIn("topics/", claude)
        self.assertIn("literature review", lower)
        # The focus area is embedded.
        self.assertIn("vector symbolic architectures", claude)
        # v1.14.0: shared workflow/cron blocks live in vendored skills.
        self.assertIn("## Skills", claude)
        self.assertIn("autonomous-loop", claude)
        loop = (proj / ".claude" / "skills" / "autonomous-loop" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("three-cron playbook", loop.lower())

    def test_area_placeholder_when_absent(self):
        proj, _ = _make()  # no area
        claude = (proj / "CLAUDE.md").read_text(encoding="utf-8")
        readme = (proj / "README.md").read_text(encoding="utf-8")
        self.assertIn("open", claude.lower())
        # Question is always a placeholder at scaffold time (uncertain topic).
        self.assertIn("not yet chosen", claude.lower())
        self.assertIn("not yet chosen", readme.lower())

    def test_gitignore_keeps_docs_but_ignores_results(self):
        proj, _ = _make()
        gi = (proj / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("results/", gi)
        self.assertNotIn("\ndocs/", gi)
        self.assertFalse(gi.startswith("docs/"))


class TestOriginalDryRun(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "ghost"
            buf = io.StringIO()
            with redirect_stdout(buf):
                original_project(proj, dry_run=True, no_claude=True)
            self.assertFalse(proj.exists(), "dry-run must not create the directory")
            out = buf.getvalue()
            self.assertIn("[dry-run]", out)
            self.assertIn("topics", out)
            self.assertIn("index.html", out)


class TestOriginalCliDispatch(unittest.TestCase):
    def test_original_subcommand(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["original", str(proj), "--no-claude"])
            self.assertTrue((proj / "docs" / "index.html").is_file())
            self.assertTrue((proj / "topics" / ".gitkeep").is_file())
            self.assertTrue((proj / "literature" / ".gitkeep").is_file())

    def test_new_original_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["new", str(proj), "--original", "--no-claude"])
            # Routed to the original scaffold (has topics/), not plain `new`.
            self.assertTrue((proj / "topics" / ".gitkeep").is_file())
            self.assertTrue((proj / "docs" / "index.html").is_file())

    def test_area_flag_threaded_through(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["original", str(proj), "--area", "tensor network compilers",
                      "--no-claude"])
            readme = (proj / "README.md").read_text(encoding="utf-8")
            claude = (proj / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("tensor network compilers", readme)
            self.assertIn("tensor network compilers", claude)

    def test_plain_new_is_not_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["new", str(proj), "--no-claude"])
            self.assertFalse((proj / "topics").exists())
            self.assertFalse((proj / "docs").exists())


if __name__ == "__main__":
    unittest.main()
