"""Cross-platform tests for cleanvibe.

Uses stdlib unittest to match the project's zero-dependency philosophy.
All tests pass --no-claude so Claude Code is never launched (no Claude install required in CI).
"""

import io
import platform
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cleanvibe import __version__, templates
from cleanvibe.cli import main
from cleanvibe.scaffold import convert_project, create_project


IS_WINDOWS = platform.system() == "Windows"


class TestVersion(unittest.TestCase):
    def test_version_flag(self):
        with self.assertRaises(SystemExit) as cm:
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(["--version"])
        self.assertEqual(cm.exception.code, 0)


class TestCreateProject(unittest.TestCase):
    def test_creates_core_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            self.assertTrue((proj / "CLAUDE.md").is_file())
            self.assertTrue((proj / "README.md").is_file())
            self.assertTrue((proj / "queue.md").is_file())
            # devlog.md is the canonical home for "done" — every project gets one
            # so queue.md can stay strictly delete-only.
            self.assertTrue((proj / "devlog.md").is_file())
            self.assertTrue((proj / ".gitignore").is_file())
            # data_lake exists from the first commit so users can drop
            # files in before the bootstrap session runs.
            self.assertTrue((proj / "data_lake" / ".gitkeep").is_file())

    def test_queue_md_explains_purpose(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            content = (proj / "queue.md").read_text(encoding="utf-8")
            # The queue.md must explain it is a queue, and reference planning + the task tool
            self.assertIn("not a state snapshot", content)
            self.assertIn("plan", content.lower())

    def test_queue_md_contains_bootstrap_sequence(self):
        # New projects should ship with a default first-session bootstrap queue,
        # not an empty Active section. The bootstrap walks Claude through:
        # data_lake triage -> infer project from files -> interview user ->
        # write the real queue -> create private GitHub repo -> work the queue.
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            content = (proj / "queue.md").read_text(encoding="utf-8")
            lower = content.lower()
            self.assertIn("data_lake", content)
            self.assertIn(".gitkeep", lower)
            self.assertIn(".zip", lower)
            self.assertIn("lfs", lower)
            self.assertIn("readme.md", lower)
            self.assertIn("claude.md", lower)
            self.assertTrue("interview" in lower or "ask the user" in lower)
            self.assertIn("private", lower)
            self.assertIn("github", lower)

    def test_bootstrap_creates_todo_md_before_real_queue(self):
        # The bootstrap sequence must instruct Claude to create todo.md
        # (the long-horizon backlog) BEFORE writing the real concrete queue.
        # Flow: triage -> infer docs -> interview -> todo.md -> real queue -> github -> work.
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            content = (proj / "queue.md").read_text(encoding="utf-8")
            lower = content.lower()
            # The bootstrap explicitly mentions creating todo.md as its own step
            self.assertIn("todo.md", content)
            self.assertIn("long-horizon", lower)
            # The todo.md step comes before the "real queue" replacement step
            todo_idx = lower.find("create `todo.md`")
            real_queue_idx = lower.find("replace this bootstrap queue")
            self.assertGreater(todo_idx, 0, "bootstrap must include a 'Create todo.md' step")
            self.assertGreater(real_queue_idx, todo_idx,
                "Create todo.md must precede 'Replace this bootstrap queue'")

    def test_claude_md_describes_todo_to_queue_flow(self):
        # v1.14.0: the todo.md -> queue.md flow now lives in the
        # queue-driven-workflow skill, vendored into .claude/skills/.
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            skill = (proj / ".claude" / "skills" / "queue-driven-workflow"
                     / "SKILL.md").read_text(encoding="utf-8")
            lower = skill.lower()
            self.assertIn("todo.md", skill)
            self.assertIn("long-term horizon", lower)
            self.assertIn("queue.md", skill)

    def test_devlog_md_template_describes_its_role(self):
        # devlog_md() exists, names the project, and explains the "delete from
        # queue + append dated entry here" rule (the whole point of the file).
        content = templates.devlog_md("myproj")
        self.assertIn("myproj", content)
        lower = content.lower()
        self.assertIn("devlog", lower)
        self.assertIn("queue.md", content)
        self.assertIn("delete", lower)
        # The starter entry mentions scaffolding (so the file has at least one entry).
        self.assertIn("Scaffolded", content)

    def test_devlog_md_clone_variant_says_backfill(self):
        # The clone-style starter must instruct the agent to backfill from git log.
        content = templates.devlog_md("myproj", clone=True)
        lower = content.lower()
        self.assertIn("backfill", lower)
        self.assertIn("git log", lower)

    def test_bootstrap_queue_references_devlog(self):
        # The bootstrap queue's preamble + step instructions must tell the
        # agent that finishing an item = delete from queue + append to devlog.
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            queue_content = (proj / "queue.md").read_text(encoding="utf-8")
            skill = (proj / ".claude" / "skills" / "queue-driven-workflow"
                     / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("devlog.md", queue_content)
            # The CLAUDE.md side of the rule now lives in the workflow skill.
            self.assertIn("devlog.md", skill)

    def test_bootstrap_queue_starts_three_crons(self):
        # v1.11.0: the bootstrap queue's opening step must START the three-cron
        # playbook (work-loop at :03, auto-flush at :15, status-report at :42) —
        # not merely reference killing/restarting them. Earlier templates only
        # wired the status-report cron; v1.11.0 generalizes to the full loop.
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            content = (proj / "queue.md").read_text(encoding="utf-8")
            lower = content.lower()
            self.assertIn("croncreate", lower)
            # All three crons by name + minute mark.
            self.assertIn("work-loop", lower)
            self.assertIn("auto-flush", lower)
            self.assertIn("status-report", lower)
            self.assertIn("3 * * * *", content)
            self.assertIn("15 * * * *", content)
            self.assertIn("42 * * * *", content)
            # An explicit "start the three-cron playbook" step, not only kill/restart.
            self.assertIn("start the three-cron playbook", lower)
            # ... and it is the opening bootstrap step, before triaging files.
            start_idx = lower.find("start the three-cron playbook")
            triage_idx = lower.find("triage user-supplied files")
            self.assertGreater(start_idx, 0)
            self.assertGreater(
                triage_idx, start_idx,
                "starting the crons must be the opening bootstrap step, before triage",
            )

    def test_claude_md_cron_lifecycle_mentions_start(self):
        # v1.14.0: the three-cron lifecycle now lives in the autonomous-loop
        # skill, vendored into .claude/skills/. It must still say to START the
        # crons at the beginning of extensive work — not only kill/restart them.
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            content = (proj / ".claude" / "skills" / "autonomous-loop"
                       / "SKILL.md").read_text(encoding="utf-8")
        lower = content.lower()
        self.assertIn("three-cron playbook", lower)
        self.assertIn("croncreate", lower)
        # All three crons named.
        self.assertIn("work-loop", lower)
        self.assertIn("auto-flush", lower)
        self.assertIn("status-report", lower)
        # Mentions starting at the beginning, not only killing/restarting.
        self.assertIn("start all three crons at the beginning", lower)
        # The lifecycle still covers kill-on-refill and planning-mode disable.
        self.assertIn("kill", lower)
        self.assertIn("planning mode", lower)

    def test_claude_md_has_weekly_update_check_section(self):
        # v1.14.0: every generated CLAUDE.md carries a Skills pointer naming the
        # canonical updates URL + last-check date so long-lived projects can pick
        # up new cleanvibe skills. The detailed weekly check lives in the
        # cleanvibe-update-check skill.
        content = templates.claude_md("myproj")
        lower = content.lower()
        self.assertIn("## skills", lower)
        self.assertIn("https://cleanvibe.emmaleonhart.com/updates.md", content)
        self.assertIn("last cleanvibe update check", lower)
        self.assertIn("cleanvibe-update-check", content)

    def test_todo_md_template_exists_and_describes_flow(self):
        # The todo_md() builder must produce a file that explains its role
        # (long-horizon, abstract) and its relationship to queue.md.
        content = templates.todo_md("myproj")
        self.assertIn("myproj", content)
        lower = content.lower()
        self.assertIn("long-term horizon", lower)
        self.assertIn("queue.md", lower)
        self.assertIn("abstract", lower)

    def test_claude_md_references_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            content = (proj / "CLAUDE.md").read_text(encoding="utf-8")
            # v1.14.0: CLAUDE.md points to the queue-driven-workflow skill, which
            # enforces the queue-first planning rule.
            self.assertIn("queue-driven-workflow", content)
            skill = (proj / ".claude" / "skills" / "queue-driven-workflow"
                     / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("queue.md", skill)
            self.assertIn("planning", skill.lower())

    def test_scaffold_writes_all_six_skills(self):
        # v1.14.0: every scaffolded project gets the six vendored skills under
        # .claude/skills/, and the CLAUDE.md keeps only the ## Skills pointer.
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            for slug in ("emergency-stop", "cron-is-local", "autonomous-loop",
                         "queue-driven-workflow", "writing-style",
                         "cleanvibe-update-check"):
                p = proj / ".claude" / "skills" / slug / "SKILL.md"
                self.assertTrue(p.exists(), f"{slug} skill not written")
                self.assertIn(f"name: {slug}", p.read_text(encoding="utf-8"))
            claude = (proj / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("## Skills", claude)
            # The bulky prose must NOT be inlined into CLAUDE.md anymore.
            self.assertNotIn("Emergency Stop Mode", claude)
            self.assertNotIn("three-cron playbook", claude)

    def test_runclaude_bat_only_on_windows(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            runclaude = proj / "!runClaude.bat"
            if IS_WINDOWS:
                self.assertTrue(runclaude.is_file(), "!runClaude.bat should be created on Windows")
            else:
                self.assertFalse(runclaude.exists(), "!runClaude.bat should NOT be created on Unix")

    def test_initializes_git_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            self.assertTrue((proj / ".git").is_dir(), "git repo should be initialized")

    def test_initial_branch_is_main_not_master(self):
        # cleanvibe must initialize new repos on `main`, regardless of the
        # user's `init.defaultBranch` git config. master causes downstream
        # tooling glitches (default-branch protection, CI assumptions).
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "myproj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=proj, capture_output=True, text=True,
            ).stdout.strip()
            self.assertEqual(branch, "main")

    def test_claude_md_contains_project_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "uniqueprojectname"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, no_claude=True)
            content = (proj / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("uniqueprojectname", content)


class TestDryRun(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "ghost"
            buf = io.StringIO()
            with redirect_stdout(buf):
                create_project(proj, dry_run=True, no_claude=True)
            self.assertFalse(proj.exists(), "dry-run must not create the directory")
            output = buf.getvalue()
            self.assertIn("[dry-run]", output)
            self.assertIn("CLAUDE.md", output)


class TestConvert(unittest.TestCase):
    def test_convert_empty_dir_creates_two_commits(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "existing"
            proj.mkdir()
            (proj / "preexisting.txt").write_text("hello", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                convert_project(proj, no_claude=True)

            self.assertTrue((proj / ".git").is_dir())
            self.assertTrue((proj / "CLAUDE.md").is_file())
            self.assertTrue((proj / "preexisting.txt").is_file())

            # Two commits: original files, then scaffold
            result = subprocess.run(
                ["git", "log", "--oneline"],
                cwd=proj,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0)
            commits = [ln for ln in result.stdout.strip().splitlines() if ln.strip()]
            self.assertEqual(len(commits), 2, f"Expected 2 commits, got: {commits}")

    def test_convert_initial_branch_is_main(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "existing"
            proj.mkdir()
            (proj / "x.txt").write_text("hi", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                convert_project(proj, no_claude=True)
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=proj, capture_output=True, text=True,
            ).stdout.strip()
            self.assertEqual(branch, "main")

    def test_convert_skips_existing_scaffold_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "existing"
            proj.mkdir()
            custom = "# my custom claude.md\n"
            (proj / "CLAUDE.md").write_text(custom, encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                convert_project(proj, no_claude=True)

            # CLAUDE.md must not be overwritten
            self.assertEqual((proj / "CLAUDE.md").read_text(encoding="utf-8"), custom)
            # README, queue.md, devlog.md, and .gitignore should still be injected
            self.assertTrue((proj / "README.md").is_file())
            self.assertTrue((proj / "queue.md").is_file())
            self.assertTrue((proj / "devlog.md").is_file())
            self.assertTrue((proj / ".gitignore").is_file())
            self.assertTrue((proj / "data_lake" / ".gitkeep").is_file())


if __name__ == "__main__":
    unittest.main()
