import pytest

from replication_skill.arxiv import _parse_atom, parse_arxiv_id


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


def test_parse_arxiv_id_accepts_many_forms():
    assert parse_arxiv_id("1706.03762") == "1706.03762"
    assert parse_arxiv_id("1706.03762v5") == "1706.03762"
    assert parse_arxiv_id("https://arxiv.org/abs/1706.03762") == "1706.03762"
    assert parse_arxiv_id("https://arxiv.org/pdf/1706.03762v5.pdf") == "1706.03762"
    assert parse_arxiv_id("ARXIV.ORG/abs/1706.03762") == "1706.03762"
    assert parse_arxiv_id("cs.CL/0001001") == "cs.CL/0001001"


def test_parse_arxiv_id_rejects_garbage():
    with pytest.raises(ValueError):
        parse_arxiv_id("not-an-id")


def test_parse_atom_extracts_fields():
    paper = _parse_atom(SAMPLE_ATOM, "1706.03762")
    assert paper.arxiv_id == "1706.03762"
    assert paper.title == "Attention Is All You Need"
    assert paper.authors == ("Ashish Vaswani", "Noam Shazeer")
    assert "Transformer" in paper.summary
    assert paper.pdf_url.endswith("1706.03762v5")
    assert paper.slug == "attention-is-all-you-need"
