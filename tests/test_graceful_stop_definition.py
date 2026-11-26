"""v2.0.16: Emma's graceful stop and handoff.md."""
import json
import unittest

from cleanvibe import templates
from cleanvibe.skills import SKILLS


class GracefulStopDefinitionTests(unittest.TestCase):
    def test_rules_give_the_steps_and_handoff(self):
        md = templates.v2_rules_md()
        for text in ("Delete all your crons", "Finish the current task to completion",
                     "every 30 minutes", "Write `handoff.md`", "Commit and push",
                     "stop finished:",
                     "Read `handoff.md` when earlier work comes up",
                     "Work runs with the work loop on",
                     "Search before you say you don't know something about the user"):
            self.assertIn(text, md)

    def test_skill_matches(self):
        body = SKILLS["autonomous-loop"]
        for text in ("handoff.md", "stop finished:", "Work runs with the loop on"):
            self.assertIn(text, body)

    def test_settings_leave_idle_compaction_alone(self):
        # Emma has not decided about idle compaction (2026-11-25): ship no setting.
        self.assertNotIn("idleCompaction", json.loads(templates.v2_settings_json()))


if __name__ == "__main__":
    unittest.main()
