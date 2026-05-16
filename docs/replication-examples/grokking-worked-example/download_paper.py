"""Download the PDF for arXiv:2201.02177 into replication_target/paper.pdf."""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

PDF_URL = "https://arxiv.org/pdf/2201.02177v1"
ARXIV_ID = "2201.02177"


def main() -> int:
    out = Path(__file__).parent / "replication_target" / "paper.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 0:
        print(f"already present: {out}")
        return 0
    print(f"downloading {PDF_URL} -> {out}")
    req = urllib.request.Request(PDF_URL, headers={"User-Agent": "cleanvibe-replicate"})
    with urllib.request.urlopen(req) as resp, open(out, "wb") as f:
        f.write(resp.read())
    print(f"wrote {out.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
