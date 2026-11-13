"""Write a test wrapper: main.tex preamble + the given section files.

Usage: python tools/mktest.py NAME [--sec N] [--fig N] [--tab N] SECTION...
"""
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("name")
ap.add_argument("sections", nargs="+")
ap.add_argument("--sec", type=int)
ap.add_argument("--subsec", type=int)
ap.add_argument("--fig", type=int)
ap.add_argument("--tab", type=int)
ap.add_argument("--title", action="store_true")
a = ap.parse_args()

src = open("main.tex", encoding="utf-8").read()
pre = src[: src.index(r"\begin{document}")]
body = [r"\begin{document}"]
if a.title:
    body.append(r"\maketitle")
for k, v in (("section", a.sec), ("subsection", a.subsec), ("figure", a.fig), ("table", a.tab)):
    if v is not None:
        body.append(rf"\setcounter{{{k}}}{{{v}}}")
body += [rf"\input{{sections/{s}}}" for s in a.sections]
body.append(r"\end{document}")
open(f"{a.name}.tex", "w", encoding="utf-8").write(pre + "\n".join(body) + "\n")
