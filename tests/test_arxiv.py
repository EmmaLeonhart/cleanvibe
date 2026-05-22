"""Tests for cleanvibe.arxiv — stdlib unittest, no network.

Ported from replication_skill's pytest suite. Only the pure parsing paths
are exercised (parse_arxiv_id, _parse_atom); fetch_paper hits the network
and is covered indirectly via the monkeypatched replicate tests.
"""

import unittest

from cleanvibe.arxiv import (
    _parse_atom,
    is_arxiv_ref,
    parse_arxiv_id,
    split_arxiv_ref,
)


SAMPLE_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v5</id>
    <title>Attention Is All You Need</title>
    <summary>We propose a new simple network architecture, the Transformer,
    based solely on attention mechanisms.</summary>
    <published>2017-06-12T17:57:34Z</published>
    <author><name>Ashish Vaswani</name></author>
    <author><name>Noam Shazeer</name></author>
    <link title="pdf" href="http://arxiv.org/pdf/1706.03762v5" type="application/pdf"/>
  </entry>
</feed>
"""


class TestParseArxivId(unittest.TestCase):
    def test_accepts_many_forms(self):
        self.assertEqual(parse_arxiv_id("1706.03762"), "1706.03762")
        self.assertEqual(parse_arxiv_id("1706.03762v5"), "1706.03762")
        self.assertEqual(parse_arxiv_id("https://arxiv.org/abs/1706.03762"), "1706.03762")
        self.assertEqual(parse_arxiv_id("https://arxiv.org/pdf/1706.03762v5.pdf"), "1706.03762")
        self.assertEqual(parse_arxiv_id("ARXIV.ORG/abs/1706.03762"), "1706.03762")
        self.assertEqual(parse_arxiv_id("cs.CL/0001001"), "cs.CL/0001001")

    def test_accepts_alphaxiv_links(self):
        self.assertEqual(parse_arxiv_id("https://www.alphaxiv.org/abs/2604.06425"), "2604.06425")
        self.assertEqual(parse_arxiv_id("https://alphaxiv.org/pdf/1706.03762v5.pdf"), "1706.03762")
        self.assertEqual(parse_arxiv_id("ALPHAXIV.ORG/abs/1706.03762"), "1706.03762")

    def test_accepts_non_abs_url_paths(self):
        # The "not really working" bug: alphaxiv's primary URL form is
        # /overview/<id>, plus arXiv /forum/, trailing slug, query string.
        self.assertEqual(
            parse_arxiv_id("https://www.alphaxiv.org/overview/2201.02177"), "2201.02177"
        )
        self.assertEqual(
            parse_arxiv_id("https://www.alphaxiv.org/overview/2201.02177v1"), "2201.02177"
        )
        self.assertEqual(
            parse_arxiv_id("https://arxiv.org/forum/2310.06825"), "2310.06825"
        )
        self.assertEqual(
            parse_arxiv_id("https://arxiv.org/abs/1706.03762?utm=x#sec1"), "1706.03762"
        )
        self.assertEqual(
            parse_arxiv_id("https://arxiv.org/abs/cs.LG/0701001"), "cs.LG/0701001"
        )

    def test_accepts_doi_form(self):
        # The arXiv DOI form (doi.org doesn't contain "arxiv.org/"): the user
        # report's `https://doi.org/10.48550/arXiv.<id>` used to fall through
        # to manual folder mode.
        self.assertEqual(
            parse_arxiv_id("https://doi.org/10.48550/arXiv.2605.20919"),
            "2605.20919",
        )
        self.assertEqual(
            parse_arxiv_id("10.48550/arXiv.1706.03762"), "1706.03762"
        )
        self.assertTrue(is_arxiv_ref("https://doi.org/10.48550/arXiv.2605.20919"))

    def test_accepts_arxiv_citation_style(self):
        self.assertEqual(parse_arxiv_id("arXiv:2605.20919"), "2605.20919")
        self.assertEqual(parse_arxiv_id("arXiv:1706.03762v5"), "1706.03762")

    def test_split_preserves_version(self):
        # parse_arxiv_id stays version-agnostic (used for naming)...
        self.assertEqual(parse_arxiv_id("2605.20919v3"), "2605.20919")
        # ...but split_arxiv_ref hands back the version so it isn't lost.
        self.assertEqual(split_arxiv_ref("2605.20919v3"), ("2605.20919", "3"))
        self.assertEqual(split_arxiv_ref("2605.20919"), ("2605.20919", None))
        self.assertEqual(
            split_arxiv_ref("https://arxiv.org/abs/2605.20919v1"),
            ("2605.20919", "1"),
        )
        self.assertEqual(
            split_arxiv_ref("https://arxiv.org/html/2605.20919v2"),
            ("2605.20919", "2"),
        )
        self.assertEqual(
            split_arxiv_ref("https://www.alphaxiv.org/overview/2605.20919v4"),
            ("2605.20919", "4"),
        )

    def test_accepts_all_reported_url_forms(self):
        # Every form from the user report routes to arXiv mode and yields the id.
        forms = [
            "https://arxiv.org/abs/2605.20919",
            "https://arxiv.org/abs/2605.20919v1",
            "https://doi.org/10.48550/arXiv.2605.20919",
            "https://arxiv.org/pdf/2605.20919",
            "https://arxiv.org/html/2605.20919v1",
            "https://arxiv.org/src/2605.20919",
            "https://www.alphaxiv.org/abs/2605.20919",
            "https://www.alphaxiv.org/overview/2605.20919",
            "https://www.alphaxiv.org/audio/2605.20919",
        ]
        for f in forms:
            self.assertTrue(is_arxiv_ref(f), f)
            self.assertEqual(parse_arxiv_id(f), "2605.20919", f)

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            parse_arxiv_id("not-an-id")
        with self.assertRaises(ValueError):
            parse_arxiv_id("https://arxiv.org/about")

    def test_is_arxiv_ref_discriminates_folders(self):
        # Paper references -> arXiv mode.
        self.assertTrue(is_arxiv_ref("2201.02177"))
        self.assertTrue(is_arxiv_ref("https://www.alphaxiv.org/overview/2201.02177"))
        self.assertTrue(is_arxiv_ref("https://arxiv.org/abs/1706.03762v5"))
        # Folder names -> manual drop-in mode.
        self.assertFalse(is_arxiv_ref("my-paper"))
        self.assertFalse(is_arxiv_ref("./papers/grokking"))
        self.assertFalse(is_arxiv_ref("replicating-some-cool-paper"))
        self.assertFalse(is_arxiv_ref(r"C:\papers\foo"))


class TestParseAtom(unittest.TestCase):
    def test_extracts_fields(self):
        paper = _parse_atom(SAMPLE_ATOM, "1706.03762")
        self.assertEqual(paper.arxiv_id, "1706.03762")
        self.assertEqual(paper.title, "Attention Is All You Need")
        self.assertEqual(paper.authors, ("Ashish Vaswani", "Noam Shazeer"))
        self.assertIn("Transformer", paper.summary)
        self.assertTrue(paper.pdf_url.endswith("1706.03762v5"))
        self.assertEqual(paper.slug, "attention-is-all-you-need")
        # Version resolved from the canonical <id> when not pinned in the request.
        self.assertEqual(paper.version, "5")
        self.assertEqual(paper.id_with_version, "1706.03762v5")


if __name__ == "__main__":
    unittest.main()
