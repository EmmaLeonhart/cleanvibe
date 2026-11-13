"""Set the placement specifier of figures/tables.

Usage: python tools/setfloat.py SPEC [FILE [LABEL...]]
  SPEC   e.g. H, t, tbp
  FILE   a sections/*.tex file (default: all)
  LABEL  only floats containing \\label{LABEL}, e.g. fig:13
"""
import glob
import re
import sys

spec = sys.argv[1]
files = [sys.argv[2]] if len(sys.argv) > 2 else sorted(glob.glob("sections/*.tex"))
labels = sys.argv[3:]
pat = re.compile(r"\\begin\{(figure|table)\}(\[[^\]]*\])?(.*?\\end\{\1\})", re.S)

for f in files:
    s = open(f, encoding="utf-8").read()
    n = 0

    def repl(m):
        global n
        if labels and not any(rf"\label{{{l}}}" in m.group(3) for l in labels):
            return m.group(0)
        n += 1
        return rf"\begin{{{m.group(1)}}}[{spec}]" + m.group(3)

    s = pat.sub(repl, s)
    open(f, "w", encoding="utf-8").write(s)
    print(f, n)
