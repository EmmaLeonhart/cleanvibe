"""Fetch paper metadata from the arXiv API.

Stdlib only (``urllib``) — keeps cleanvibe's zero-dependency guarantee.
Ported from the now-absorbed ``replication_skill`` project, which used
``requests``.
"""

from __future__ import annotations

import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Callable, Iterable

from . import __version__

ARXIV_API = "https://export.arxiv.org/api/query"
# arXiv rate-limits aggressively (429, sometimes 503). It asks for ~3s
# between requests; we use that as the base backoff and retry a few times.
_MAX_RETRIES = 4
_BASE_BACKOFF = 3.0
# Socket read timeouts come up as plain ``TimeoutError`` (3.10+) or
# ``socket.timeout`` (3.9) — NEITHER is a subclass of ``urllib.error.URLError``,
# so without this tuple they would bypass the retry loop and surface as a raw
# traceback (the v1.11.0 user report).
_TIMEOUT_ERRORS = (TimeoutError, socket.timeout)
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
    # The resolved version, e.g. ``"1"`` for v1, or ``None`` when the request
    # didn't pin one and the API response carried no version. Kept distinct
    # from ``arxiv_id`` (always the bare id) so naming stays version-agnostic
    # while paper.json / downloads can target the exact version requested.
    version: str | None = None

    @property
    def slug(self) -> str:
        return _slugify(self.title)

    @property
    def id_with_version(self) -> str:
        """The id including ``vN`` when a version is known, else the bare id."""
        return f"{self.arxiv_id}v{self.version}" if self.version else self.arxiv_id


# A bare arXiv id: new-style ``YYMM.NNNNN`` or old-style ``archive/NNNNNNN``
# (optionally with a subject class, e.g. ``cs.LG/0701001``).
_ARXIV_ID = r"\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}"
# Same, but capturing an optional trailing ``vN`` version.
_ARXIV_ID_VER = re.compile(rf"(?P<id>{_ARXIV_ID})(?:v(?P<ver>\d+))?")

# Does this string *reference* arXiv (so we should pull an id out of it)?
# Covers the hosts (arxiv.org / alphaxiv.org, any path: /abs /pdf /html /src
# /overview /audio /forum …), the arXiv DOI prefix used by doi.org links
# (``10.48550/arXiv.<id>``), and the bare ``arXiv:<id>`` citation style.
_REFERENCES_ARXIV = re.compile(
    r"(?:arxiv|alphaxiv)\.org/|10\.48550/arxiv|arxiv:", re.IGNORECASE
)


def split_arxiv_ref(value: str) -> tuple[str, str | None]:
    """Return ``(bare_id, version_or_None)`` for any recognised arXiv reference.

    Accepts every form we have seen in the wild:
      * ``arxiv.org/{abs,pdf,html,src}/<id>[vN]`` (and any other path)
      * ``alphaxiv.org/{abs,overview,audio,forum}/<id>[vN]`` (overview is
        alphaxiv's primary form)
      * ``doi.org/10.48550/arXiv.<id>`` (the arXiv DOI)
      * ``arXiv:<id>[vN]`` citation style
      * a bare ``<id>[vN]`` (new-style ``YYMM.NNNNN`` or old-style
        ``archive/NNNNNNN``), optionally with a ``.pdf`` suffix

    The ``vN`` version is preserved (returned separately) rather than silently
    dropped, so callers can fetch and record the exact version requested.

    Raises ``ValueError`` if no arXiv id can be found — ``replicate`` uses this
    to fall back to folder (manual drop-in) mode.
    """
    value = value.strip()
    if _REFERENCES_ARXIV.search(value):
        # A URL / DOI / citation that references arXiv: pull the first
        # id-shaped token from anywhere in it.
        m = _ARXIV_ID_VER.search(value)
        if m is None:
            raise ValueError(f"no arXiv id found in reference: {value!r}")
        return m.group("id"), m.group("ver")
    # Otherwise treat the whole input as a bare id (optionally ``.pdf``).
    if value.endswith(".pdf"):
        value = value[: -len(".pdf")]
    m = _ARXIV_ID_VER.fullmatch(value)
    if m is None:
        raise ValueError(f"not a recognisable arXiv id: {value!r}")
    return m.group("id"), m.group("ver")


def parse_arxiv_id(value: str) -> str:
    """Return just the bare arXiv id (version stripped) for any reference.

    Thin wrapper over :func:`split_arxiv_ref`; kept for the many callers (and
    the directory-naming path) that only want the version-agnostic id.
    """
    return split_arxiv_ref(value)[0]


def is_arxiv_ref(value: str) -> bool:
    """True if ``value`` looks like an arXiv/alphaxiv id, URL, or DOI.

    ``cleanvibe replicate`` uses this to decide whether the positional
    argument is a paper reference (arXiv mode) or a folder name to scaffold
    a manual, drop-the-PDF-in-yourself replication project.
    """
    try:
        split_arxiv_ref(value)
        return True
    except ValueError:
        return False


def _retry_after_seconds(err: urllib.error.HTTPError) -> float | None:
    """Parse a numeric ``Retry-After`` header (seconds). HTTP-date form -> None."""
    val = err.headers.get("Retry-After") if err.headers else None
    if not val:
        return None
    try:
        return max(0.0, float(val))
    except ValueError:
        return None


def _read_url(
    req: urllib.request.Request,
    *,
    timeout: float,
    retries: int = _MAX_RETRIES,
    sleep: Callable[[float], None] = time.sleep,
) -> bytes:
    """GET ``req`` with retry/backoff for arXiv's rate limiting.

    arXiv returns 429 (and sometimes 503) under load. We honour ``Retry-After``
    when present and otherwise back off exponentially from a ~3s base (arXiv's
    requested politeness interval); transient network errors get the same
    treatment. After the last attempt a rate-limit failure is re-raised as a
    ``RuntimeError`` with a clear message instead of a raw traceback.

    ``sleep`` is injectable so tests exercise the backoff without waiting.
    """
    backoff = _BASE_BACKOFF
    for attempt in range(retries):
        last = attempt == retries - 1
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                if last:
                    raise RuntimeError(
                        f"arXiv is rate-limiting (HTTP {e.code}) after "
                        f"{retries} attempts — wait a minute and retry: "
                        f"{req.full_url}"
                    ) from e
                sleep(_retry_after_seconds(e) or backoff)
                backoff *= 2
                continue
            raise  # other HTTP errors (404 etc.) are not transient
        except (urllib.error.URLError, *_TIMEOUT_ERRORS):
            # URLError covers DNS / refused / SSL; the timeout tuple covers
            # socket-level read timeouts (a separate exception hierarchy).
            if last:
                raise
            sleep(backoff)
            backoff *= 2
    raise AssertionError("unreachable")  # pragma: no cover


def fetch_paper(arxiv_ref: str, *, timeout: float = 30.0) -> ArxivPaper:
    """Call the arXiv Atom API and return metadata for a single paper.

    Accepts any reference :func:`split_arxiv_ref` understands. If a version is
    pinned (e.g. ``2605.20919v1``) the API is queried for that exact version;
    otherwise the latest is returned and its version recorded.
    """
    arxiv_id, version = split_arxiv_ref(arxiv_ref)
    query_id = f"{arxiv_id}v{version}" if version else arxiv_id
    query = urllib.parse.urlencode({"id_list": query_id, "max_results": 1})
    req = urllib.request.Request(
        f"{ARXIV_API}?{query}",
        headers={"User-Agent": USER_AGENT},
    )
    xml_text = _read_url(req, timeout=timeout).decode("utf-8")
    return _parse_atom(xml_text, arxiv_id, version)


def _parse_atom(
    xml_text: str, arxiv_id: str, version: str | None = None
) -> ArxivPaper:
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
    # Resolve the version we didn't pin from the canonical <id>, e.g.
    # ``http://arxiv.org/abs/2605.20919v1`` -> "1".
    if version is None:
        m = re.search(r"v(\d+)\s*$", _text(entry, "atom:id"))
        if m is not None:
            version = m.group(1)
    pdf_url = ""
    for link in entry.findall("atom:link", ATOM_NS):
        if link.get("title") == "pdf" or link.get("type") == "application/pdf":
            pdf_url = link.get("href", "")
            break
    if not pdf_url:
        ver = f"v{version}" if version else ""
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}{ver}.pdf"
    return ArxivPaper(
        arxiv_id=arxiv_id,
        title=_collapse(title),
        authors=authors,
        summary=_collapse(summary),
        published=published,
        pdf_url=pdf_url,
        version=version,
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
