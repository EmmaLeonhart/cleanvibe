"""Render pages of a PDF to PNG under the permanent screenshots folder.

Usage: python tools/render.py PDF PREFIX [PAGES...]   (pages 1-based; default all)
"""
import os
import sys

import pymupdf

OUT = os.path.join(os.path.expanduser("~"), "Documents", "claude-screenshots",
                   "scratch-2026-09-25_2026-09-25", "rebuild")
os.makedirs(OUT, exist_ok=True)
pdf, prefix, *pages = sys.argv[1:]
d = pymupdf.open(pdf)
idx = [int(p) - 1 for p in pages] or range(len(d))
for i in idx:
    path = os.path.join(OUT, f"{prefix}_p{i + 1:02d}.png")
    d[i].get_pixmap(dpi=110).save(path)
    print(path)
