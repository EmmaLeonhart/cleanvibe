"""v2.0.16: idle compaction off in shipped settings; Emma's graceful stop; handoff.md."""
import json
import unittest

from cleanvibe import templates
from cleanvibe.project import _merge_settings
from cleanvibe.skills import SKILLS


class IdleCompactionTests(unittest.TestCase):
    def test_shipped_settings_turn_idle_compaction_off(self):
        self.assertIs(json.loads(templates.v2_settings_json())["idleCompaction"], False)

    def test_merge_adds_the_setting_to_an_old_project(self):
        old = json.dumps({"hooks": {}})
        merged = json.loads(_merge_settings(old, templates.v2_settings_json()))
        self.assertIs(merged["idleCompaction"], False)

    def test_merge_keeps_a_projects_own_choice(self):
        own = json.dumps({"idleCompaction": True, "hooks": {}})
        merged = json.loads(_merge_settings(own, templates.v2_settings_json()))
        self.assertIs(merged["idleCompaction"], True)


class GracefulStopDefinitionTests(unittest.TestCase):
    def test_rules_give_the_steps_and_handoff(self):
        md = templates.v2_rules_md()
        for text in ("Delete all your crons", "Finish the current task to completion",
                     "every 30 minutes", "Write `handoff.md`", "Commit and push",
                     "Read `handoff.md` when earlier work comes up",
                     "Work runs with the work loop on"):
            self.assertIn(text, md)

    def test_skill_matches(self):
        body = SKILLS["autonomous-loop"]
        self.assertIn("handoff.md", body)
        self.assertIn("Work runs with the loop on", body)


if __name__ == "__main__":
    unittest.main()
