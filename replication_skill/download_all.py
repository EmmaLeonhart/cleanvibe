"""Download every paper in papers.json into its scaffold's gitignored paper/ dir.

The PDFs land under replications/<slug>/paper/<arxiv_id>.pdf. None of them are
committed — .gitignore entries inside each scaffold keep them out. This script
exists so an agent (or a human) can populate every paper/ folder with one
command before starting a replication pass.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

INDEX = Path(__file__).parent / "papers.json"
REPLICATIONS = Path(__file__).parent / "replications"
UA = "replication-skill/0.1 (+https://github.com/EmmaLeonhart/replication_skill)"


def _download(pdf_url: str, dest: Path) -> int:
    """Return bytes written, or 0 if already present and non-empty."""
    if dest.exists() and dest.stat().st_size > 0:
        return 0
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(pdf_url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
        data = resp.read()
        f.write(data)
    return len(data)


def main() -> int:
    if not INDEX.exists():
        print(f"missing {INDEX}", file=sys.stderr)
        return 2
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    papers = index.get("papers", [])
    failures: list[tuple[str, str]] = []
    for entry in papers:
        slug = entry["slug"]
        arxiv_id = entry["arxiv_id"]
        pdf_url = entry["pdf_url"]
        dest = REPLICATIONS / slug / "paper" / f"{arxiv_id.replace('/', '_')}.pdf"
        try:
            written = _download(pdf_url, dest)
            if written == 0:
                print(f"[skip] {arxiv_id}: already present -> {dest}")
            else:
                print(f"[ok]   {arxiv_id}: {written} bytes -> {dest}")
                time.sleep(3)  # polite pause between arXiv hits
        except urllib.error.HTTPError as e:
            print(f"[fail] {arxiv_id}: HTTP {e.code} {e.reason}", file=sys.stderr)
            failures.append((arxiv_id, f"HTTP {e.code}"))
        except Exception as e:  # noqa: BLE001
            print(f"[fail] {arxiv_id}: {e}", file=sys.stderr)
            failures.append((arxiv_id, str(e)))
    if failures:
        print(f"\n{len(failures)} download(s) failed:", file=sys.stderr)
        for aid, why in failures:
            print(f"  {aid}: {why}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
