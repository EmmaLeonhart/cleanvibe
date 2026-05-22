"""Tests for cleanvibe.arxiv — stdlib unittest, no network.

Ported from replication_skill's pytest suite. Only the pure parsing paths
are exercised (parse_arxiv_id, _parse_atom); fetch_paper hits the network
and is covered indirectly via the monkeypatched replicate tests.
"""

import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

from cleanvibe.arxiv import (
    _parse_atom,
    _read_url,
    is_arxiv_ref,
    parse_arxiv_id,
    split_arxiv_ref,
)


SAMPLE_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v5</id>
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

    def test_accepts_non_abs_url_paths(self):
        # The "not really working" bug: alphaxiv's primary URL form is
        # /overview/<id>, plus arXiv /forum/, trailing slug, query string.
        self.assertEqual(
            parse_arxiv_id("https://www.alphaxiv.org/overview/2201.02177"), "2201.02177"
        )
        self.assertEqual(
            parse_arxiv_id("https://www.alphaxiv.org/overview/2201.02177v1"), "2201.02177"
        )
        self.assertEqual(
            parse_arxiv_id("https://arxiv.org/forum/2310.06825"), "2310.06825"
        )
        self.assertEqual(
            parse_arxiv_id("https://arxiv.org/abs/1706.03762?utm=x#sec1"), "1706.03762"
        )
        self.assertEqual(
            parse_arxiv_id("https://arxiv.org/abs/cs.LG/0701001"), "cs.LG/0701001"
        )

    def test_accepts_doi_form(self):
        # The arXiv DOI form (doi.org doesn't contain "arxiv.org/"): the user
        # report's `https://doi.org/10.48550/arXiv.<id>` used to fall through
        # to manual folder mode.
        self.assertEqual(
            parse_arxiv_id("https://doi.org/10.48550/arXiv.2605.20919"),
            "2605.20919",
        )
        self.assertEqual(
            parse_arxiv_id("10.48550/arXiv.1706.03762"), "1706.03762"
        )
        self.assertTrue(is_arxiv_ref("https://doi.org/10.48550/arXiv.2605.20919"))

    def test_accepts_arxiv_citation_style(self):
        self.assertEqual(parse_arxiv_id("arXiv:2605.20919"), "2605.20919")
        self.assertEqual(parse_arxiv_id("arXiv:1706.03762v5"), "1706.03762")

    def test_split_preserves_version(self):
        # parse_arxiv_id stays version-agnostic (used for naming)...
        self.assertEqual(parse_arxiv_id("2605.20919v3"), "2605.20919")
        # ...but split_arxiv_ref hands back the version so it isn't lost.
        self.assertEqual(split_arxiv_ref("2605.20919v3"), ("2605.20919", "3"))
        self.assertEqual(split_arxiv_ref("2605.20919"), ("2605.20919", None))
        self.assertEqual(
            split_arxiv_ref("https://arxiv.org/abs/2605.20919v1"),
            ("2605.20919", "1"),
        )
        self.assertEqual(
            split_arxiv_ref("https://arxiv.org/html/2605.20919v2"),
            ("2605.20919", "2"),
        )
        self.assertEqual(
            split_arxiv_ref("https://www.alphaxiv.org/overview/2605.20919v4"),
            ("2605.20919", "4"),
        )

    def test_accepts_all_reported_url_forms(self):
        # Every form from the user report routes to arXiv mode and yields the id.
        forms = [
            "https://arxiv.org/abs/2605.20919",
            "https://arxiv.org/abs/2605.20919v1",
            "https://doi.org/10.48550/arXiv.2605.20919",
            "https://arxiv.org/pdf/2605.20919",
            "https://arxiv.org/html/2605.20919v1",
            "https://arxiv.org/src/2605.20919",
            "https://www.alphaxiv.org/abs/2605.20919",
            "https://www.alphaxiv.org/overview/2605.20919",
            "https://www.alphaxiv.org/audio/2605.20919",
        ]
        for f in forms:
            self.assertTrue(is_arxiv_ref(f), f)
            self.assertEqual(parse_arxiv_id(f), "2605.20919", f)

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            parse_arxiv_id("not-an-id")
        with self.assertRaises(ValueError):
            parse_arxiv_id("https://arxiv.org/about")

    def test_is_arxiv_ref_discriminates_folders(self):
        # Paper references -> arXiv mode.
        self.assertTrue(is_arxiv_ref("2201.02177"))
        self.assertTrue(is_arxiv_ref("https://www.alphaxiv.org/overview/2201.02177"))
        self.assertTrue(is_arxiv_ref("https://arxiv.org/abs/1706.03762v5"))
        # Folder names -> manual drop-in mode.
        self.assertFalse(is_arxiv_ref("my-paper"))
        self.assertFalse(is_arxiv_ref("./papers/grokking"))
        self.assertFalse(is_arxiv_ref("replicating-some-cool-paper"))
        self.assertFalse(is_arxiv_ref(r"C:\papers\foo"))


class TestParseAtom(unittest.TestCase):
    def test_extracts_fields(self):
        paper = _parse_atom(SAMPLE_ATOM, "1706.03762")
        self.assertEqual(paper.arxiv_id, "1706.03762")
        self.assertEqual(paper.title, "Attention Is All You Need")
        self.assertEqual(paper.authors, ("Ashish Vaswani", "Noam Shazeer"))
        self.assertIn("Transformer", paper.summary)
        self.assertTrue(paper.pdf_url.endswith("1706.03762v5"))
        self.assertEqual(paper.slug, "attention-is-all-you-need")
        # Version resolved from the canonical <id> when not pinned in the request.
        self.assertEqual(paper.version, "5")
        self.assertEqual(paper.id_with_version, "1706.03762v5")


class _Resp:
    """Minimal context-manager stand-in for an http response."""

    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


def _http_error(code, retry_after=None):
    hdrs = {"Retry-After": retry_after} if retry_after is not None else {}
    return urllib.error.HTTPError("http://x", code, "err", hdrs, None)


class TestReadUrlRetry(unittest.TestCase):
    """_read_url retries arXiv's 429/503 with backoff — no network, no sleeping."""

    def test_retries_429_then_succeeds(self):
        calls = {"n": 0}
        slept = []

        def fake_urlopen(req, timeout=None):
            calls["n"] += 1
            if calls["n"] < 3:
                raise _http_error(429, retry_after="0")
            return _Resp(b"OK")

        with patch("urllib.request.urlopen", fake_urlopen):
            body = _read_url(
                urllib.request.Request("http://x"), timeout=1, sleep=slept.append
            )
        self.assertEqual(body, b"OK")
        self.assertEqual(calls["n"], 3)
        self.assertEqual(len(slept), 2)  # backed off before each retry

    def test_runtimeerror_after_exhaustion(self):
        def fake_urlopen(req, timeout=None):
            raise _http_error(429)

        with patch("urllib.request.urlopen", fake_urlopen):
            with self.assertRaises(RuntimeError):
                _read_url(
                    urllib.request.Request("http://x"),
                    timeout=1,
                    retries=3,
                    sleep=lambda s: None,
                )

    def test_non_transient_http_error_not_retried(self):
        calls = {"n": 0}

        def fake_urlopen(req, timeout=None):
            calls["n"] += 1
            raise _http_error(404)

        with patch("urllib.request.urlopen", fake_urlopen):
            with self.assertRaises(urllib.error.HTTPError):
                _read_url(
                    urllib.request.Request("http://x"),
                    timeout=1,
                    sleep=lambda s: None,
                )
        self.assertEqual(calls["n"], 1)  # 404 is not transient


if __name__ == "__main__":
    unittest.main()
