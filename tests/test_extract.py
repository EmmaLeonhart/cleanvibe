"""Tests for clawrxiv_clone.extract.extract_text (no live model)."""

from __future__ import annotations

import pathlib

from clawrxiv_clone.extract import extract_text


def test_md_passthrough(tmp_path: pathlib.Path) -> None:
    p = tmp_path / "paper.md"
    body = "# Title\n\nAbstract here.\n\n## 1 Intro\n\nText.\n"
    p.write_text(body, encoding="utf-8")
    assert extract_text(p) == body


def test_txt_passthrough(tmp_path: pathlib.Path) -> None:
    p = tmp_path / "paper.txt"
    p.write_text("plain text", encoding="utf-8")
    assert extract_text(p) == "plain text"


def test_tex_section_to_heading(tmp_path: pathlib.Path) -> None:
    p = tmp_path / "paper.tex"
    p.write_text(
        "\\documentclass{article}\n"
        "% a comment line\n"
        "\\title{My Paper}\n"
        "\\begin{document}\n"
        "\\section{Introduction}\n"
        "Body text.\n"
        "\\subsection{Details}\n"
        "More.\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    out = extract_text(p)
    assert "# Introduction" in out
    assert "## Details" in out
    # Preamble before \begin{document} (incl. \title and the comment) is dropped.
    assert "documentclass" not in out
    assert "a comment line" not in out
    assert "Body text." in out


def test_unknown_suffix_falls_back_to_text(tmp_path: pathlib.Path) -> None:
    p = tmp_path / "paper.rst"
    p.write_text("rst body", encoding="utf-8")
    assert extract_text(p) == "rst body"
