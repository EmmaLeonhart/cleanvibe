#!/usr/bin/env bash
# Build main.pdf (two passes) and report errors, page count, and float placement vs the original.
cd "$(dirname "$0")/.." || exit 1
export PATH="$LOCALAPPDATA/Programs/MiKTeX/miktex/bin/x64:$PATH"
for _ in 1 2; do pdflatex -interaction=nonstopmode main.tex > build.log 2>&1; done
grep -a -E '^!|Output written|Overfull|undefined' build.log
PYTHONIOENCODING=utf-8 python tools/floatpages.py original.pdf main.pdf 2>/dev/null | grep -E 'Fig|Table' | grep -- '<--'
exit 0
