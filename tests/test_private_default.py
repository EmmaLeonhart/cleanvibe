"""Repos default to private when nothing says otherwise.

The 1.x modes create a private repo (v1.18.0). A cleanvibe 2 project goes to
GitHub unless the user says local; any signal for public makes it public, any
for private makes it private, and private breaks ties (Emma, 2026-10-06). The
Pages workflows must not fail on a private repo: they skip the Pages deploy
there and upload the report as a plain workflow artifact.
"""

import inspect
import unittest

from cleanvibe import templates

GATE = "${{ !github.event.repository.private || vars.CLEANVIBE_PAGES == 'true' }}"


def _all_template_text():
    """Every string constant and Template in templates.py, concatenated."""
    parts = []
    for name, value in vars(templates).items():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, templates.Template):
            parts.append(value.template)
    return "\n".join(parts) + inspect.getsource(templates)


class TestPrivateByDefault(unittest.TestCase):
    def test_legacy_templates_create_a_private_repo(self):
        text = _all_template_text()
        self.assertNotIn("PUBLIC GitHub repo", text)
        self.assertIn("gh repo create --private", text)

    def test_v2_default_rule_is_remote_with_private_tiebreak(self):
        md = templates.v2_claude_md("p")
        self.assertIn("Push to a GitHub remote unless the user says to keep the project", md)
        self.assertIn("With no signal, or signals both ways, it is private.", md)

    def test_v2_explicit_visibility(self):
        self.assertIn("--public --source=. --push", templates.v2_claude_md("p", visibility="public"))
        self.assertIn("--private --source=. --push", templates.v2_claude_md("p", visibility="private"))
        local = templates.v2_claude_md("p", visibility="local")
        self.assertIn("do not create a remote", local)
        self.assertNotIn("gh repo create <descriptive-name> --p", local)
        self.assertIn("a public GitHub repo", templates.v2_first_prompt("/x", False, "public"))
        self.assertIn("no GitHub repo", templates.v2_first_prompt("/x", False, "local"))

    def test_pages_workflows_gate_deploy_on_visibility(self):
        for yml in (templates.RESEARCH_PAGES_YML, templates.REPLICATION_PAGES_YML):
            # configure-pages, upload-pages-artifact, and the deploy job.
            self.assertEqual(yml.count(GATE), 3)
            # The report is always uploaded, so a private repo still gets it.
            self.assertIn("actions/upload-artifact@v4", yml)
            self.assertIn("name: report", yml)


if __name__ == "__main__":
    unittest.main()
