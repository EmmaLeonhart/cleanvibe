"""Fetch paper metadata from the arXiv API.

Stdlib only (``urllib``) — keeps cleanvibe's zero-dependency guarantee.
Ported from the now-absorbed ``replication_skill`` project, which used
``requests``.
"""

from __future__ import annotations

import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Iterable

from . import __version__

ARXIV_API = "http://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
USER_AGENT = f"cleanvibe-replicate/{__version__} (+https://github.com/Immanuelle/cleanvibe)"


@dataclass(frozen=True)
class ArxivPaper:
    arxiv_id: str
    title: str
    authors: tuple
    summary: str
    published: str
    pdf_url: str

    @property
    def slug(self) -> str:
        return _slugify(self.title)


# A bare arXiv id: new-style ``YYMM.NNNNN`` or old-style ``archive/NNNNNNN``
# (optionally with a subject class, e.g. ``cs.LG/0701001``).
_ARXIV_ID = r"\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}"
_IS_ARXIV_URL = re.compile(r"(?:arxiv|alphaxiv)\.org/", re.IGNORECASE)


def parse_arxiv_id(value: str) -> str:
    """Return the bare arXiv id from a bare/versioned id or *any* arxiv.org /
    alphaxiv.org URL.

    The URL path is no longer restricted to ``/abs|pdf|html/``: alphaxiv's
    primary form is ``/overview/<id>`` and arXiv also exposes ``/forum/``,
    versioned ids, trailing slugs, and query strings. For any
    arxiv/alphaxiv URL we extract the first id-shaped token from anywhere in
    it; otherwise we treat the input as a bare id.

    Raises ValueError if the input isn't recognisably arXiv (the caller uses
    this to decide between arXiv mode and folder-drop mode).
    """
    value = value.strip()
    if _IS_ARXIV_URL.search(value):
        m = re.search(_ARXIV_ID, value)
        if m is None:
            raise ValueError(f"no arXiv id found in URL: {value!r}")
        return m.group(0)
    if value.endswith(".pdf"):
        value = value[: -len(".pdf")]
    value = re.sub(r"v\d+$", "", value)
    if not re.fullmatch(_ARXIV_ID, value):
        raise ValueError(f"not a recognisable arXiv id: {value!r}")
    return value


def is_arxiv_ref(value: str) -> bool:
    """True if ``value`` looks like an arXiv/alphaxiv id or URL.

    ``cleanvibe replicate`` uses this to decide whether the positional
    argument is a paper reference (arXiv mode) or a folder name to scaffold
    a manual, drop-the-PDF-in-yourself replication project.
    """
    try:
        parse_arxiv_id(value)
        return True
    except ValueError:
        return False


def fetch_paper(arxiv_id: str, *, timeout: float = 15.0) -> ArxivPaper:
    """Call the arXiv Atom API and return metadata for a single paper."""
    arxiv_id = parse_arxiv_id(arxiv_id)
    query = urllib.parse.urlencode({"id_list": arxiv_id, "max_results": 1})
    req = urllib.request.Request(
        f"{ARXIV_API}?{query}",
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        xml_text = resp.read().decode("utf-8")
    return _parse_atom(xml_text, arxiv_id)


def _parse_atom(xml_text: str, arxiv_id: str) -> ArxivPaper:
    root = ET.fromstring(xml_text)
    entry = root.find("atom:entry", ATOM_NS)
    if entry is None:
        raise LookupError(f"arXiv returned no entry for {arxiv_id}")
    title = _text(entry, "atom:title")
    summary = _text(entry, "atom:summary")
    published = _text(entry, "atom:published")
    authors = tuple(
        _text(a, "atom:name") for a in entry.findall("atom:author", ATOM_NS)
    )
    pdf_url = ""
    for link in entry.findall("atom:link", ATOM_NS):
        if link.get("title") == "pdf" or link.get("type") == "application/pdf":
            pdf_url = link.get("href", "")
            break
    if not pdf_url:
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    return ArxivPaper(
        arxiv_id=arxiv_id,
        title=_collapse(title),
        authors=authors,
        summary=_collapse(summary),
        published=published,
        pdf_url=pdf_url,
    )


def _text(el: ET.Element, path: str) -> str:
    found = el.find(path, ATOM_NS)
    return (found.text or "") if found is not None else ""


def _collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(title: str, *, max_words: int = 8) -> str:
    words = _SLUG_RE.sub(" ", title.lower()).split()
    return "-".join(words[:max_words]).strip("-") or "paper"


def iter_authors(paper: ArxivPaper) -> Iterable[str]:
    yield from paper.authors
