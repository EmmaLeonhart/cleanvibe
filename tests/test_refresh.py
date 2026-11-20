"""`cleanvibe refresh`: shipped files are brought up to this version, and the
project's own files are never touched. Stdlib unittest, no network."""

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
