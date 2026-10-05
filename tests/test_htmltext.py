"""Tests for cleanvibe.htmltext (HTML -> Markdown for URL-mode replication).

Network-free: `_download_source` runs against a patched `_read_url`.
"""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cleanvibe import replicate, templates
from cleanvibe.htmltext import html_to_markdown

PAGE = """<html><head><style>body{}</style><script>var x = 1;</script></head>
<body><nav>Home | About</nav>
<h1>A  Paper</h1>
<p>We use <b>bold</b>, <em>emphasis</em>, <code>f(x)</code> and
<a href="https://example.org/code">our code</a> &amp; more.</p>
<p>The state <math alttext="h_{t-1}"><mi>h</mi></math> matters.</p>
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgYGD4DwABBAEAwS2OUAAAAABJRU5ErkJggg==" alt="Figure 1">
<ul><li>one</li><li>two<ol><li>inner</li></ol></li></ul>
<pre>def f():
    return 1</pre>
<table><tr><th>k</th><th>v</th></tr><tr><td>a|b</td><td>2</td></tr><tr><td></td><td></td></tr></table>
<footer>Copyright</footer></body></html>"""


class TestHtmlToMarkdown(unittest.TestCase):
    def setUp(self):
        self.md = html_to_markdown(PAGE)

    def test_drops_scripts_styles_navigation_and_data_uris(self):
        for gone in ("var x", "body{}", "Home | About", "Copyright", "base64", "iVBOR"):
            self.assertNotIn(gone, self.md)

    def test_keeps_structure(self):
        self.assertIn("# A Paper", self.md)
        self.assertIn("**bold**", self.md)
        self.assertIn("*emphasis*", self.md)
        self.assertIn("`f(x)`", self.md)
        self.assertIn("[our code](https://example.org/code) & more.", self.md)
        self.assertIn("[image: Figure 1]", self.md)
        self.assertIn("- one\n- two\n  1. inner", self.md)

    def test_math_from_alttext(self):
        self.assertIn("The state $h_{t-1}$ matters.", self.md)

    def test_pre_keeps_whitespace(self):
        self.assertIn("```\ndef f():\n    return 1\n```", self.md)

    def test_table_with_header_rule_escaped_pipes_and_no_empty_rows(self):
        self.assertIn("| k | v |\n|---|---|\n| a\\|b | 2 |", self.md)
        self.assertNotIn("|  |  |", self.md)


class TestDownloadWritesMarkdown(unittest.TestCase):
    def _download(self, url, body):
        dest = Path(tempfile.mkdtemp()) / "source"
        with patch("cleanvibe.replicate._read_url", return_value=body):
            with redirect_stdout(io.StringIO()):
                saved = replicate._download_source(url, dest)
        return dest, saved

    def test_html_gets_paper_md(self):
        dest, saved = self._download("https://lab.example.org/paper", PAGE.encode())
        self.assertEqual(saved, "paper.html")
        self.assertIn("# A Paper", (dest / "paper.md").read_text(encoding="utf-8"))

    def test_pdf_gets_no_paper_md(self):
        dest, saved = self._download("https://lab.example.org/p.pdf", b"%PDF-1.7 x")
        self.assertEqual(saved, "paper.pdf")
        self.assertFalse((dest / "paper.md").exists())


class TestGeneratedDownloader(unittest.TestCase):
    def test_embeds_the_same_converter(self):
        src = templates.url_download_paper_py("https://lab.example.org/paper")
        ns = {"__name__": "generated", "__file__": "download_paper.py"}
        exec(compile(src, "download_paper.py", "exec"), ns)
        self.assertEqual(ns["html_to_markdown"](PAGE), html_to_markdown(PAGE))
        self.assertEqual(src.count("def main()"), 1)
        self.assertNotRegex(src, r"(?m)^\s*(from|import) (cleanvibe|\.)")


if __name__ == "__main__":
    unittest.main()
