import re
import unittest
from pathlib import Path
import tempfile

from cleanvibe import skills

EXPECTED = {
    "emergency-stop", "cron-is-local", "autonomous-loop",
    "queue-driven-workflow", "research-practice", "writing-style",
    "cleanvibe-update-check", "browser-persistence",
}
FM = re.compile(r"^---\nname: (?P<name>[a-z-]+)\ndescription: (?P<desc>.+?)\n---\n", re.S)


class TestSkills(unittest.TestCase):
    def test_all_present(self):
        self.assertEqual(set(skills.SKILLS), EXPECTED)

    def test_frontmatter_valid_and_matches_slug(self):
        for slug, body in skills.SKILLS.items():
            m = FM.match(body)
            self.assertIsNotNone(m, f"{slug} missing frontmatter")
            self.assertEqual(m.group("name"), slug)
            self.assertTrue(len(m.group("desc")) > 20, f"{slug} description too short")

    def test_write_skills_creates_tree(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            written = skills.write_skills(root)
            self.assertEqual(len(written), len(EXPECTED))
            for slug in EXPECTED:
                p = root / ".claude" / "skills" / slug / "SKILL.md"
                self.assertTrue(p.exists(), f"{p} not written")
                self.assertIn(f"name: {slug}", p.read_text(encoding="utf-8"))

    def test_write_skills_no_overwrite_when_disabled(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / ".claude" / "skills" / "writing-style" / "SKILL.md"
            p.parent.mkdir(parents=True)
            p.write_text("CUSTOM", encoding="utf-8")
            skills.write_skills(root, overwrite=False)
            self.assertEqual(p.read_text(encoding="utf-8"), "CUSTOM")


    def test_browser_persistence_rule(self):
        # Case study 10: sessions gave up on the first browser error and closed
        # tabs the user still needed.
        body = skills.SKILLS["browser-persistence"]
        for phrase in ("Use the browser", "identical attempts", "different",
                       "Don't skip a site", "Hand over, don't close",
                       "which window", "Close only tabs that are truly finished",
                       "solve bot checks"):
            self.assertIn(phrase, body)

    def test_claude_md_points_at_browser_persistence(self):
        from cleanvibe import templates
        self.assertIn("browser-persistence", templates.SKILLS_POINTER)
        self.assertIn("leaving its tab open", templates.SKILLS_POINTER)


if __name__ == "__main__":
    unittest.main()
