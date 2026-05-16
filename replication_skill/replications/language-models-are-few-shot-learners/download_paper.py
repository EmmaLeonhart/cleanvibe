"""Download the PDF for arXiv:2005.14165 into paper/."""

from __future__ import annotations

import sys
from pathlib import Path

import urllib.request

PDF_URL = "https://arxiv.org/pdf/2005.14165v4"
ARXIV_ID = "2005.14165"


def main() -> int:
    out = Path(__file__).parent / "paper" / f"{ARXIV_ID.replace('/', '_')}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 0:
        print(f"already present: {out}")
        return 0
    print(f"downloading {PDF_URL} -> {out}")
    req = urllib.request.Request(PDF_URL, headers={"User-Agent": "replication-skill/0.1"})
    with urllib.request.urlopen(req) as resp, open(out, "wb") as f:
        f.write(resp.read())
    print(f"wrote {out.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
