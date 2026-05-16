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


def parse_arxiv_id(value: str) -> str:
    """Accept a bare id, abs URL, pdf URL, or versioned id and return the bare id.

    Raises ValueError if the input isn't recognisably arXiv.
    """
    value = value.strip()
    # Accept arxiv.org and alphaxiv.org (which mirrors arXiv ids) abs/pdf/html URLs.
    m = re.search(
        r"(?:arxiv|alphaxiv)\.org/(?:abs|pdf|html)/([^\s?#]+)",
        value,
        flags=re.IGNORECASE,
    )
    if m:
        value = m.group(1)
    if value.endswith(".pdf"):
        value = value[: -len(".pdf")]
    value = re.sub(r"v\d+$", "", value)
    if not re.fullmatch(r"\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}", value):
        raise ValueError(f"not a recognisable arXiv id: {value!r}")
    return value


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
