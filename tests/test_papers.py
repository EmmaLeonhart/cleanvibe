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


def test_abstract_section_preferred_over_first_block():
    md = ("# Title\n\n**Emma Leonhart** (with Claw)\n\n## Abstract\n\n"
          "We report a defect.\nIt spans two lines.\n\n## 1. Introduction\nBody.")
    p = parse_markdown_paper(md)
    assert p.abstract == "We report a defect.\nIt spans two lines."
    assert "Emma Leonhart" in p.content


def test_abstract_heading_variants_and_end_of_file():
    p = parse_markdown_paper("# T\n\nauthors\n\n### ABSTRACT:\nShort abstract.")
    assert p.abstract == "Short abstract."


def test_empty_abstract_section_falls_back():
    p = parse_markdown_paper("# T\n\nFirst block.\n\n## Abstract\n\n## Intro\nx")
    assert p.abstract == "First block."


def test_word_abstract_in_text_is_not_a_heading():
    p = parse_markdown_paper("# T\n\nThe abstract idea.\n\n## Method\nAbstract thoughts.")
    assert p.abstract == "The abstract idea."
