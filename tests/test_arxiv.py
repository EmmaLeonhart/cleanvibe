"""Tests for cleanvibe.arxiv — stdlib unittest, no network.

Ported from replication_skill's pytest suite. Only the pure parsing paths
are exercised (parse_arxiv_id, _parse_atom); fetch_paper hits the network
and is covered indirectly via the monkeypatched replicate tests.
"""

import unittest

from cleanvibe.arxiv import _parse_atom, parse_arxiv_id


SAMPLE_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
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

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            parse_arxiv_id("not-an-id")


class TestParseAtom(unittest.TestCase):
    def test_extracts_fields(self):
        paper = _parse_atom(SAMPLE_ATOM, "1706.03762")
        self.assertEqual(paper.arxiv_id, "1706.03762")
        self.assertEqual(paper.title, "Attention Is All You Need")
        self.assertEqual(paper.authors, ("Ashish Vaswani", "Noam Shazeer"))
        self.assertIn("Transformer", paper.summary)
        self.assertTrue(paper.pdf_url.endswith("1706.03762v5"))
        self.assertEqual(paper.slug, "attention-is-all-you-need")


if __name__ == "__main__":
    unittest.main()
