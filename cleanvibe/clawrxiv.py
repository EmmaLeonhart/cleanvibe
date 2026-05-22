"""Fetch paper + skill metadata from clawRxiv (clawrxiv.io).

clawRxiv publishes papers authored autonomously by AI agents. Its JSON API
(``/api/abs/<id>``) returns the paper as three *differentiated* parts — the
``content`` (full markdown body), the ``abstract``, and ``skillMd`` (an
agent-runnable replication recipe) — which is exactly the recipe-first model
cleanvibe replication is built around. So clawRxiv gets its own ``replicate``
mode, distinct from arXiv/alphaxiv.

Stdlib only (``urllib`` + ``json``) — keeps cleanvibe's zero-dependency
guarantee. Mirrors the shape of ``cleanvibe.arxiv``.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable

from . import __version__
from .arxiv import _slugify  # reuse the shared slugifier

CLAWRXIV_API = "https://www.clawrxiv.io/api/abs/"
USER_AGENT = f"cleanvibe-replicate/{__version__} (+https://github.com/Immanuelle/cleanvibe)"
_MAX_RETRIES = 4
_BASE_BACKOFF = 2.0

# clawRxiv ids look arXiv-like: ``YYMM.NNNNN``.
_CLAWRXIV_ID_RE = re.compile(r"\d{4}\.\d{4,5}")
# Does this string *reference* clawRxiv? A clawrxiv.io URL (any path, with or
# without ``www.``) or a ``clawrxiv:<id>`` citation. A bare arXiv-shaped id is
# deliberately NOT a clawRxiv reference — clawRxiv needs an explicit signal, so
# bare ids stay arXiv.
_REFERENCES_CLAWRXIV = re.compile(r"clawrxiv\.io/|clawrxiv:", re.IGNORECASE)


@dataclass(frozen=True)
class ClawrxivPaper:
    paper_id: str
    title: str
    abstract: str
    content: str
    skill_md: str | None
    authors: tuple
    claw_name: str
    version: str | None
    category: str
    created_at: str

    @property
    def slug(self) -> str:
        return _slugify(self.title)

    @property
    def abs_url(self) -> str:
        return f"https://www.clawrxiv.io/abs/{self.paper_id}"

    @property
    def api_url(self) -> str:
        return f"{CLAWRXIV_API}{self.paper_id}"

    @property
    def has_skill_file(self) -> bool:
        """True when clawRxiv shipped a *separate* skill file (``skillMd``).

        When False, the agent-runnable recipe is embedded in ``content``
        instead and must be extracted from the paper body.
        """
        return bool(self.skill_md and self.skill_md.strip())


def parse_clawrxiv_id(value: str) -> str:
    """Return the bare clawRxiv id (``YYMM.NNNNN``) from any clawRxiv reference.

    Raises ``ValueError`` if no id-shaped token is present.
    """
    m = _CLAWRXIV_ID_RE.search(value.strip())
    if m is None:
        raise ValueError(f"no clawRxiv id found in: {value!r}")
    return m.group(0)


def is_clawrxiv_ref(value: str) -> bool:
    """True if ``value`` is a clawrxiv.io URL or ``clawrxiv:<id>`` citation.

    ``cleanvibe replicate`` checks this *before* the arXiv check so clawRxiv
    links route to the dedicated clawRxiv mode.
    """
    if not _REFERENCES_CLAWRXIV.search(value):
        return False
    try:
        parse_clawrxiv_id(value)
        return True
    except ValueError:
        return False


def _read_url(
    url: str,
    *,
    timeout: float,
    retries: int = _MAX_RETRIES,
    sleep: Callable[[float], None] = time.sleep,
) -> bytes:
    """GET ``url`` with light retry/backoff for 429/503 and transient errors.

    ``sleep`` is injectable so tests exercise the backoff without waiting.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
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
                        f"clawRxiv is rate-limiting (HTTP {e.code}) after "
                        f"{retries} attempts — wait a minute and retry: {url}"
                    ) from e
                sleep(backoff)
                backoff *= 2
                continue
            raise  # other HTTP errors (404 etc.) are not transient
        except urllib.error.URLError:
            if last:
                raise
            sleep(backoff)
            backoff *= 2
    raise AssertionError("unreachable")  # pragma: no cover


def fetch_clawrxiv_paper(ref: str, *, timeout: float = 15.0) -> ClawrxivPaper:
    """Call the clawRxiv JSON API and return metadata + content + skill."""
    paper_id = parse_clawrxiv_id(ref)
    raw = _read_url(f"{CLAWRXIV_API}{paper_id}", timeout=timeout)
    return _parse_clawrxiv(json.loads(raw.decode("utf-8")), paper_id)


def _parse_clawrxiv(obj: dict, paper_id: str) -> ClawrxivPaper:
    title = (obj.get("title") or "").strip()
    if not title:
        raise LookupError(f"clawRxiv returned no paper for {paper_id}")
    version = obj.get("version")
    return ClawrxivPaper(
        paper_id=obj.get("paperId") or paper_id,
        title=_collapse(title),
        abstract=_collapse(obj.get("abstract") or ""),
        content=obj.get("content") or "",  # markdown body — keep newlines
        skill_md=obj.get("skillMd"),
        authors=tuple(obj.get("humanNames") or ()),
        claw_name=obj.get("clawName") or "",
        version=str(version) if version is not None else None,
        category=obj.get("category") or "",
        created_at=obj.get("createdAt") or "",
    )


def _collapse(s: str) -> str:
    """Collapse runs of whitespace — for title/abstract only, NOT content."""
    return re.sub(r"\s+", " ", s).strip()
