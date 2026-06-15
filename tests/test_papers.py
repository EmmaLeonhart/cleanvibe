"""Markdown paper parser (shared by the review/submit CLIs)."""

from clawrxiv_clone.papers import parse_markdown_paper


def test_parse_markdown_paper():
    md = "# My Title\n\nThe abstract paragraph.\n\n## Method\nDetails here."
    p = parse_markdown_paper(md)
    assert p.title == "My Title"
    assert p.abstract == "The abstract paragraph."
    assert "## Method" in p.content


def test_parse_no_h1():
    p = parse_markdown_paper("Just some text.\n\nMore body.")
    assert p.title == "Untitled"
    assert p.abstract == "Just some text."
