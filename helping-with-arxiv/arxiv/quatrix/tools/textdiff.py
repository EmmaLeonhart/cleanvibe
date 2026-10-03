"""Word-level diff between the original PDF and a rebuilt PDF.

Normalises ligatures, dashes, math-italic Unicode and line-break hyphenation so
that only real wording/number differences are reported. Text inside the
figures (matplotlib fonts) is ignored because the figures are cropped from the
original verbatim. Blocks that only moved (float placement) are paired up and
reported as moves, not differences.

Usage: python tools/textdiff.py original.pdf main.pdf
"""
import difflib
import re
import sys
import unicodedata

import pymupdf

FIGFONT = re.compile("TimesNewRoman|DejaVu|STIX|Liberation")


def words(pdf):
    out = []
    for page in pymupdf.open(pdf):
        lines = []
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                s = "".join(sp["text"] for sp in l["spans"] if not FIGFONT.search(sp["font"]))
                if s.strip():
                    lines.append(s)
        if lines and re.fullmatch(r"\s*\d+\s*", lines[-1]):
            lines.pop()  # page number
        out.append("\n".join(lines))
    t = unicodedata.normalize("NFKC", "\n".join(out))
    t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)
    for a, b in (("−", "-"), ("–", "-"), ("—", "-"), ("’", "'"),
                 ("‘", "'"), ("“", '"'), ("”", '"')):
        t = t.replace(a, b)
    t = re.sub(r"\s+", " ", t)
    return re.findall(r"[A-Za-z]+|\d+(?:[.,]\d+)*|[^\sA-Za-z\d]", t)


def main():
    wa, wb = words(sys.argv[1]), words(sys.argv[2])
    sm = difflib.SequenceMatcher(None, wa, wb, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    dels = {i: wa[o[1]:o[2]] for i, o in enumerate(ops) if o[0] in ("delete", "replace")}
    ins = {i: wb[o[3]:o[4]] for i, o in enumerate(ops) if o[0] in ("insert", "replace")}
    moved = 0
    for i, d in list(dels.items()):
        for j, n in list(ins.items()):
            if len(d) > 15 and d == n:
                del dels[i], ins[j]
                moved += 1
                break
    print(f"original tokens {len(wa)}, rebuilt tokens {len(wb)}, ratio {sm.ratio():.4f}, moved blocks {moved}")
    count = 0
    for i, o in enumerate(ops):
        d, n = dels.get(i), ins.get(i)
        if not d and not n:
            continue
        count += 1
        pre = " ".join(wa[max(0, o[1] - 6):o[1]])
        print(f"--- ...{pre}")
        if d:
            print(f"   orig: {' '.join(d)[:400]}")
        if n:
            print(f"   new : {' '.join(n)[:400]}")
    print(f"{count} unmatched spans")


if __name__ == "__main__":
    main()
