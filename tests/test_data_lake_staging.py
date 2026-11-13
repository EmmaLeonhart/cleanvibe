"""data_lake/ is a staging area (Emma, via the Topaz Wellness queue).

"almost everything is supposed to be moved out of the data lake once it is
done there." The v2 CLAUDE.md says finished material moves out.
"""
import unittest

from cleanvibe import templates


class DataLakeStagingTests(unittest.TestCase):
    def test_v2_claude_md_says_finished_material_moves_out(self):
        md = templates.v2_claude_md("demo")
        self.assertIn("The data lake is a staging area", md)
        self.assertIn("Move, never delete", md)


if __name__ == "__main__":
    unittest.main()
