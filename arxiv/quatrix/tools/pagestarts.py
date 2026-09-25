"""Print the first body-text words of each page in two PDFs, side by side."""
import re
import sys

import pymupdf

FIGFONT = re.compile("TimesNewRoman|DejaVu|STIX|Liberation")


def starts(pdf):
    out = []
    for page in pymupdf.open(pdf):
        first = ""
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                s = "".join(sp["text"] for sp in l["spans"] if not FIGFONT.search(sp["font"])).strip()
                if len(s) > 25:
                    first = s[:45]
                    break
            if first:
                break
        out.append(first)
    return out


a, b = starts(sys.argv[1]), starts(sys.argv[2])
for i in range(max(len(a), len(b))):
    x = a[i] if i < len(a) else ""
    y = b[i] if i < len(b) else ""
    print(f"p{i + 1:<3}{'  ' if x == y else '!='} {x:47}| {y}")
