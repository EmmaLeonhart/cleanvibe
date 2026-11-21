"""`cleanvibe refresh`: shipped files are brought up to this version, and the
project's own files are never touched, except the old default Publishing rule. Stdlib unittest, no network."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

os.environ.setdefault("CLEANVIBE_CLAUDE_CONFIG", os.path.join(
    tempfile.mkdtemp(), "claude.json"))

from cleanvibe import project, skills, templates  # noqa: E402
from cleanvibe.cli import main  # noqa: E402


def _new():
    proj = Path(tempfile.mkdtemp()) / "proj"
    with redirect_stdout(io.StringIO()):
        project.new_project(proj, no_claude=True)
    return proj


class TestRefresh(unittest.TestCase):
    def test_fresh_project_needs_nothing(self):
        self.assertEqual(project.refresh_project(_new()), [])

    def test_restores_shipped_files_and_leaves_the_project_alone(self):
        proj = _new()
        rules = proj / templates.V2_RULES_PATH
        rules.write_text("old rules\n", encoding="utf-8")
        slug = next(iter(skills.SKILLS))
        (proj / f".claude/skills/{slug}/SKILL.md").unlink()
        (proj / ".claude/hooks/intent_staleness.py").write_text("old\n", encoding="utf-8")
        claude = proj / "CLAUDE.md"
        claude.write_text(claude.read_text(encoding="utf-8") + "\n- my own rule\n", encoding="utf-8")
        intent_before = (proj / "INTENT.md").read_text(encoding="utf-8")
        claude_before = claude.read_text(encoding="utf-8")

        changed = project.refresh_project(proj)
        self.assertEqual(sorted(changed), sorted([
            templates.V2_RULES_PATH, f".claude/skills/{slug}/SKILL.md",
            ".claude/hooks/intent_staleness.py"]))
        self.assertEqual(rules.read_text(encoding="utf-8"), templates.v2_rules_md())
        self.assertEqual(claude.read_text(encoding="utf-8"), claude_before)
        self.assertEqual((proj / "INTENT.md").read_text(encoding="utf-8"), intent_before)
        self.assertEqual(project.refresh_project(proj), [])

    def test_settings_keep_the_projects_own_entries(self):
        proj = _new()
        settings = proj / ".claude/settings.json"
        data = {"permissions": {"allow": ["Bash(npm test)"]},
                "hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "mine.py"}]}]}}
        settings.write_text(json.dumps(data), encoding="utf-8")
        self.assertIn(".claude/settings.json", project.refresh_project(proj))
        merged = json.loads(settings.read_text(encoding="utf-8"))
        self.assertEqual(merged["permissions"], data["permissions"])
        self.assertEqual(merged["hooks"]["PreToolUse"], data["hooks"]["PreToolUse"])
        shipped = json.loads(templates.v2_settings_json())["hooks"]
        for event in shipped:
            self.assertIn(shipped[event][0], merged["hooks"][event])
        self.assertEqual(project.refresh_project(proj), [])  # no duplicates on a re-run

    def test_rules_only_when_imported(self):
        proj = _new()
        claude = proj / "CLAUDE.md"
        claude.write_text("# old-style project\n", encoding="utf-8")
        (proj / templates.V2_RULES_PATH).unlink()
        self.assertNotIn(templates.V2_RULES_PATH, project.refresh_project(proj))
        self.assertFalse((proj / templates.V2_RULES_PATH).exists())

    def test_a_mention_of_the_import_is_not_an_import(self):
        # cleanvibe's own CLAUDE.md names the import line in prose; refresh
        # wrote a RULES.md there until this was fixed (2026-11-20).
        proj = _new()
        (proj / "CLAUDE.md").write_text(
            "# p\n\nCLAUDE.md imports it (`@.claude/cleanvibe/RULES.md`).\n", encoding="utf-8")
        (proj / templates.V2_RULES_PATH).unlink()
        self.assertNotIn(templates.V2_RULES_PATH, project.refresh_project(proj))
        self.assertFalse((proj / templates.V2_RULES_PATH).exists())
        self.assertFalse(project.migrate_project(proj)["already"])

    def test_needs_script_is_shipped_and_works(self):
        import subprocess, sys
        proj = _new()
        script = proj / ".claude/scripts/needs.py"
        self.assertEqual(script.read_text(encoding="utf-8"), templates.NEEDS_PY)
        r = subprocess.run([sys.executable, str(script), "add", "--kind", "action",
                            "--title", "Sign it", "--do", "Sign the form.", "--blocks", "b",
                            "--where", "in person"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        text = (proj / "NEEDS-USER.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# Needs you\n"))
        self.assertIn("## NE-1: Sign it", text)
        script.unlink()
        self.assertIn(".claude/scripts/needs.py", project.refresh_project(proj))

    def test_session_log_opt_out_is_respected(self):
        proj = _new()
        marker = proj / ".cleanvibe.json"
        m = json.loads(marker.read_text(encoding="utf-8"))
        m["session_log"] = False
        marker.write_text(json.dumps(m), encoding="utf-8")
        (proj / ".claude/hooks/save_session_log.py").unlink()
        (proj / ".claude/settings.json").write_text("{}", encoding="utf-8")
        project.refresh_project(proj)
        self.assertFalse((proj / ".claude/hooks/save_session_log.py").exists())
        hooks = json.loads((proj / ".claude/settings.json").read_text(encoding="utf-8"))["hooks"]
        self.assertNotIn("Stop", hooks)
        self.assertIn("UserPromptSubmit", hooks)

    def test_dry_run_and_cli(self):
        proj = _new()
        (proj / templates.V2_RULES_PATH).write_text("old\n", encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit) as e:
            main(["refresh", str(proj), "--dry-run"])
        self.assertEqual(e.exception.code, 0)
        self.assertIn("Would update " + templates.V2_RULES_PATH, out.getvalue())
        self.assertEqual((proj / templates.V2_RULES_PATH).read_text(encoding="utf-8"), "old\n")
        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as e:
            main(["refresh", str(proj)])
        self.assertEqual(e.exception.code, 0)
        self.assertEqual((proj / templates.V2_RULES_PATH).read_text(encoding="utf-8"),
                         templates.v2_rules_md())

    def test_refuses_a_non_project(self):
        err = io.StringIO()
        with redirect_stderr(err), self.assertRaises(SystemExit) as e:
            main(["refresh", tempfile.mkdtemp()])
        self.assertEqual(e.exception.code, 2)
        self.assertIn("not a cleanvibe 2 project", err.getvalue())


if __name__ == "__main__":
    unittest.main()


class TestPublishingUpgrade(unittest.TestCase):
    """The old "any signal for public" default is replaced by "private unless
    the user says public" (2026-11-18); any other Publishing text is kept."""

    def _with_old_rule(self):
        proj = _new()
        claude = proj / "CLAUDE.md"
        text = claude.read_text(encoding="utf-8")
        current = templates._publishing_section(None, "proj", False)
        current = current.split("\n", 1)[1].split(" If the user's wishes change later", 1)[0]
        old = project._old_default_publishing("proj")
        self.assertIn(current, text)
        claude.write_text(text.replace(current, old), encoding="utf-8")
        return proj, text

    def test_old_default_rule_is_replaced(self):
        proj, fresh = self._with_old_rule()
        self.assertIn("CLAUDE.md", project.refresh_project(proj))
        self.assertEqual((proj / "CLAUDE.md").read_text(encoding="utf-8"), fresh)
        self.assertEqual(project.refresh_project(proj), [])

    def test_dry_run_reports_without_writing(self):
        proj, _ = self._with_old_rule()
        before = (proj / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("CLAUDE.md", project.refresh_project(proj, dry_run=True))
        self.assertEqual((proj / "CLAUDE.md").read_text(encoding="utf-8"), before)

    def test_chosen_or_edited_publishing_is_left_alone(self):
        for vis in ("public", "private", "local"):
            with self.subTest(visibility=vis):
                proj = Path(tempfile.mkdtemp()) / "proj"
                with redirect_stdout(io.StringIO()):
                    project.new_project(proj, no_claude=True, visibility=vis)
                self.assertNotIn("CLAUDE.md", project.refresh_project(proj))
        proj = _new()
        claude = proj / "CLAUDE.md"
        edited = claude.read_text(encoding="utf-8").replace(
            "## Publishing\n", "## Publishing\nThis one is public: the user said so.\n")
        claude.write_text(edited, encoding="utf-8")
        self.assertNotIn("CLAUDE.md", project.refresh_project(proj))
