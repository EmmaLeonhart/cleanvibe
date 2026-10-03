# helping-with-arxiv

Getting a friend's paper onto arXiv:
**"Quatrix: An Empirical Evaluation of Q-Compass and SAVO on Multimodal
Sequence Modeling"** by Syed Abdur Rehman Ali
([Zenodo 10.5281/zenodo.19839718](https://doi.org/10.5281/zenodo.19839718),
code at [github.com/Abd0r/quatrix](https://github.com/Abd0r/quatrix)).

The paper was only ever published as a PDF, and arXiv will not accept a PDF
that was produced by LaTeX without its source. No source exists publicly, so
this repo rebuilds it from the PDF.

## What's here

- `arxiv/quatrix/quatrix-arxiv.tar.gz` — **the file to upload to arXiv**
  (`main.tex`, `sections/`, `figs/`, `00README.json`). Compiles with pdfLaTeX to
  the same 32 pages as the original.
- `arxiv/quatrix/SUBMISSION.md` — values for the arXiv submission form, and a
  1,754-character metadata abstract (the paper's own is ~2,480; arXiv's limit
  is 1,920) for the author to approve.
- `arxiv/quatrix/main.tex`, `sections/*.tex` — the rebuilt source.
- `arxiv/quatrix/figs/` — the 18 figures, cropped from the original PDF as
  vector PDFs (identical to the original, not redrawn).
- `arxiv/quatrix/original.pdf` — the Zenodo PDF the rebuild is checked against.
- `arxiv/quatrix/tools/` — build and verification scripts.

## Rebuilding and checking

Needs a LaTeX distribution (MiKTeX or TeX Live) and Python with PyMuPDF.

```
bash arxiv/quatrix/tools/build.sh          # build main.pdf, report float pages that differ
cd arxiv/quatrix/tools
python ngramcheck.py ../original.pdf ../main.pdf   # wording check vs the original
cd .. && tar -czf quatrix-arxiv.tar.gz 00README.json main.tex sections figs
```

`ngramcheck.py` reports any run of 8 words that appears in one PDF but not the
other, so the check is independent of where figures and tables land.

## History

Scaffolded as a `cleanvibe research` project (`scratch-2026-09-25`) and
repurposed for this task; `queue.md` / `devlog.md` keep the cleanvibe work log.
