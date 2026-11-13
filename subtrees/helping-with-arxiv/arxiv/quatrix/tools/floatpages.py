"""List the page of each Fig./Table caption and each section heading in two PDFs."""
import re
import sys

import pymupdf


def marks(pdf):
    out = {}
    for i, page in enumerate(pymupdf.open(pdf)):
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                s = "".join(sp["text"] for sp in l["spans"]).strip()
                m = re.match(r"(Fig\.|Table)\s*(\d+)\.", s)
                if m:
                    out.setdefault(f"{m.group(1)}{m.group(2)}", i + 1)
                m = re.match(r"(\d+(?:\.\d+)?)\s+[A-Z]", s)
                if m and l["spans"][0]["font"].endswith("Bold") and len(s) < 90:
                    out.setdefault(f"§{m.group(1)}", i + 1)
    return out


a, b = marks(sys.argv[1]), marks(sys.argv[2])
for k in sorted(a, key=lambda k: (a[k], k)):
    flag = "" if a[k] == b.get(k) else f"  <-- {b.get(k, 'missing')}"
    print(f"{k:8} orig p{a[k]:<3} new p{b.get(k, '-')}{flag}")
