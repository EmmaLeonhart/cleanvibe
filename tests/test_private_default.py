"""Every mode defaults to a private GitHub repo (v1.18.0).

No generated text may tell the agent to create a public repo, and the Pages
workflows must not fail on a private repo: they skip the Pages deploy there and
upload the report as a plain workflow artifact.
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
    def test_no_template_creates_a_public_repo(self):
        text = _all_template_text()
        self.assertNotIn("--public", text)
        self.assertNotIn("PUBLIC GitHub repo", text)
        self.assertIn("gh repo create --private", text)

    def test_pages_workflows_gate_deploy_on_visibility(self):
        for yml in (templates.RESEARCH_PAGES_YML, templates.REPLICATION_PAGES_YML):
            # configure-pages, upload-pages-artifact, and the deploy job.
            self.assertEqual(yml.count(GATE), 3)
            # The report is always uploaded, so a private repo still gets it.
            self.assertIn("actions/upload-artifact@v4", yml)
            self.assertIn("name: report", yml)


if __name__ == "__main__":
    unittest.main()
