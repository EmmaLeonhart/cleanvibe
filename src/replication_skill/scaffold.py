"""Render a replication directory from an ArxivPaper."""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from string import Template

from replication_skill.arxiv import ArxivPaper


def _template(name: str) -> str:
    return resources.files("replication_skill.templates").joinpath(name).read_text(encoding="utf-8")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_replication(paper: ArxivPaper, dest: Path, *, overwrite: bool = False) -> Path:
    """Create a replication directory for ``paper`` under ``dest``.

    Returns the path to the created directory. If the directory already exists
    and ``overwrite`` is False, raises FileExistsError.
    """
    dest = Path(dest)
    target = dest / paper.slug
    if target.exists() and not overwrite:
        raise FileExistsError(f"{target} already exists (use overwrite=True)")
    target.mkdir(parents=True, exist_ok=True)

    authors = ", ".join(paper.authors) if paper.authors else "unknown"
    subs = {
        "title": paper.title,
        "arxiv_id": paper.arxiv_id,
        "slug": paper.slug,
        "authors": authors,
        "published": paper.published,
        "pdf_url": paper.pdf_url,
        "summary": paper.summary,
    }

    _write(target / "README.md", Template(_template("README.md.tmpl")).substitute(subs))
    _write(target / "SKILL.md", Template(_template("SKILL.md.tmpl")).substitute(subs))
    _write(target / "download_paper.py", Template(_template("download_paper.py.tmpl")).substitute(subs))
    _write(target / ".gitignore", _template("gitignore.tmpl"))
    _write(target / "paper.json", json.dumps(
        {
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "authors": list(paper.authors),
            "published": paper.published,
            "pdf_url": paper.pdf_url,
            "summary": paper.summary,
        },
        indent=2,
        ensure_ascii=False,
    ))
    (target / "paper").mkdir(exist_ok=True)
    _write(target / "paper" / ".gitkeep", "")
    return target
