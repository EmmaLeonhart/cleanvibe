"""Tests for cleanvibe.doctor — the read-only drift audit. Stdlib unittest, no network.

The strongest check is the first class: a freshly scaffolded project of every
mode must come back clean, so the generator never ships drift that doctor would
flag (v1.18.0 found generated queues pointing at CLAUDE.md sections that had
moved into skills in v1.14.0).
"""

import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cleanvibe import doctor as doc
from cleanvibe import skills, templates
from cleanvibe.chat import chat_project
from cleanvibe.cli import main
from cleanvibe.original import original_project
from cleanvibe.project import new_project
from cleanvibe.research import research_project
from cleanvibe.scaffold import create_project


def _scaffold(fn, **kwargs):
    proj = Path(tempfile.mkdtemp()) / "proj"
    with redirect_stdout(io.StringIO()):
        fn(proj, no_claude=True, **kwargs)
    return proj


def _checks(findings):
    return sorted({f.check for f in findings})


class TestFreshScaffoldsAreClean(unittest.TestCase):
    def test_every_mode_scaffolds_without_drift(self):
        for fn in (new_project, create_project, research_project, original_project, chat_project):
            with self.subTest(mode=fn.__name__):
                proj = _scaffold(fn)
                self.assertEqual([str(f) for f in doc.run_checks(proj)], [])

    def test_no_template_points_at_a_moved_claude_md_section(self):
        # These sections moved into skills in v1.14.0.
        source = Path(templates.__file__).read_text(encoding="utf-8")
        for name in ("Workflow Rules", "Queue and longer-horizon work",
                     "Autonomous productivity loop"):
            self.assertNotIn(f'§ "{name}', source)


class TestChecks(unittest.TestCase):
    def setUp(self):
        self.proj = _scaffold(create_project)

    def _write(self, rel, text):
        path = self.proj / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_missing_core_file(self):
        (self.proj / "devlog.md").unlink()
        self.assertIn("devlog.md: missing", [str(f).split("] ")[1] for f in doc.check_files(self.proj)])

    def test_v2_project_needs_intent_and_hook_but_not_queue(self):
        proj = _scaffold(new_project)
        self.assertEqual(doc.check_files(proj), [])  # no queue.md/devlog.md: fine
        (proj / "INTENT.md").unlink()
        (proj / ".claude/hooks/save_session_log.py").unlink()
        self.assertEqual(sorted(f.where for f in doc.check_files(proj)),
                         [".claude/hooks/save_session_log.py", "INTENT.md"])

    def test_missing_and_edited_skills(self):
        slugs = list(skills.SKILLS)
        (self.proj / ".claude/skills" / slugs[0] / "SKILL.md").unlink()
        self._write(f".claude/skills/{slugs[1]}/SKILL.md", "edited")
        messages = [f.message for f in doc.check_skills(self.proj)]
        self.assertEqual(len(messages), 2)
        self.assertIn("missing", messages[0])
        self.assertIn("differs", messages[1])

    def test_done_markers_in_queue(self):
        self._write("queue.md", "\n".join([
            "# Queue",
            "- [x] shipped the thing",
            "1. Fix parser ✓",
            "2. Write docs — DONE",
            "- ~~old idea~~",
            "- [ ] still open",
            "Never tick a box in place.",
        ]))
        findings = doc.check_queue_done(self.proj)
        self.assertEqual([f.where for f in findings],
                         ["queue.md:2", "queue.md:3", "queue.md:4", "queue.md:5"])

    def test_version_pointer_mismatch(self):
        self._write("pyproject.toml", '[project]\nname = "x"\nversion = "2.0.0"\n')
        self._write("queue.md", "Current version: `1.9.0`.\n")
        self.assertEqual(_checks(doc.check_version(self.proj)), ["version"])
        self._write("queue.md", "Current version: `2.0.0`.\n")
        self.assertEqual(doc.check_version(self.proj), [])

    def test_release_tags_missing_from_devlog(self):
        for tag in ("v1.0.0", "v1.1.0", "v1.10.0"):
            subprocess.run(["git", "tag", tag], cwd=self.proj, capture_output=True)
        self._write("devlog.md", "- **v1.0.0** shipped\n- build 1.10.0.1 and v11.1.0 do not count\n")
        missing = sorted(f.message for f in doc.check_devlog_tags(self.proj))
        self.assertEqual(missing, ["no entry for release v1.1.0", "no entry for release v1.10.0"])

    def test_dangling_section_reference(self):
        self._write("todo.md", 'See `CLAUDE.md` § "Nonexistent Section" for details.\n')
        findings = doc.check_section_refs(self.proj)
        self.assertEqual([f.where for f in findings], ["todo.md"])
        self.assertIn("Nonexistent Section", findings[0].message)

    def test_section_reference_never_spans_lines(self):
        # A stray quote must not turn a paragraph into a "section name".
        self._write("todo.md", 'mentions CLAUDE.md § "\nand much later a "quote"\n')
        self.assertEqual(doc.check_section_refs(self.proj), [])

    def test_tests_without_ci(self):
        (self.proj / "tests").mkdir()
        self.assertEqual(_checks(doc.check_ci(self.proj)), ["ci"])
        self._write(".github/workflows/ci.yml", "name: CI\n")
        self.assertEqual(doc.check_ci(self.proj), [])

    def test_pre_1_18_pages_workflow(self):
        old = templates.RESEARCH_PAGES_YML.replace(
            "if: ${{ !github.event.repository.private || vars.CLEANVIBE_PAGES == 'true' }}", "")
        old = old.replace("CLEANVIBE_PAGES", "").replace("github.event.repository.private", "")
        self._write(".github/workflows/pages.yml", old)
        self.assertEqual(_checks(doc.check_pages_gate(self.proj)), ["pages-gate"])
        self._write(".github/workflows/pages.yml", templates.RESEARCH_PAGES_YML)
        self.assertEqual(doc.check_pages_gate(self.proj), [])


class TestDoctorCli(unittest.TestCase):
    def _run(self, path):
        buf = io.StringIO()
        with redirect_stdout(buf), self.assertRaises(SystemExit) as cm:
            main(["doctor", str(path)])
        return cm.exception.code, buf.getvalue()

    def test_clean_project_exits_0(self):
        code, out = self._run(_scaffold(create_project))
        self.assertEqual(code, 0)
        self.assertIn("No drift found", out)

    def test_drift_exits_1_and_changes_nothing(self):
        proj = _scaffold(create_project)
        (proj / "queue.md").write_text("- [x] done ✓\n", encoding="utf-8")
        before = (proj / "queue.md").read_bytes()
        code, out = self._run(proj)
        self.assertEqual(code, 1)
        self.assertIn("queue-done", out)
        self.assertEqual((proj / "queue.md").read_bytes(), before)

    def test_not_a_directory_exits_2(self):
        code, _ = self._run(Path(tempfile.mkdtemp()) / "nope")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
