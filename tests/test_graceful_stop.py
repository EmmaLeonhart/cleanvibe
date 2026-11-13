"""A graceful stop ends one window, never the work (Emma, 2026-11-10).

A session wrote a graceful stop into its INTENT.md as "resume only on Emma's
say-so"; the generated CLAUDE.md and the autonomous-loop skill now say it is
not a standing order. These tests keep that wording from dropping out.
"""
import unittest

from cleanvibe import templates
from cleanvibe.skills import SKILLS


class GracefulStopTests(unittest.TestCase):
    def test_v2_claude_md_says_graceful_stop_is_one_window(self):
        for auto in (False, True):
            md = templates.v2_claude_md("demo", auto_named=auto)
            self.assertIn("A graceful stop stops this window, not the work", md)
            self.assertIn("Never write it into `INTENT.md`", md)

    def test_autonomous_loop_skill_says_graceful_stop_is_not_standing(self):
        body = SKILLS["autonomous-loop"]
        self.assertIn("A graceful stop ends this window only", body)
        self.assertIn("not a standing order", body)


if __name__ == "__main__":
    unittest.main()
