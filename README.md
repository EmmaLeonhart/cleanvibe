# replication-skill

Scaffold an arXiv paper into an agent-executable replication repo.

```
pip install -e .
replicate 1706.03762
```

This creates `replications/<slug>/` containing:

```
README.md          — paper metadata + replication status
SKILL.md           — agent-executable replication plan
paper.json         — frozen arXiv metadata
download_paper.py  — fetches the PDF into paper/ (gitignored)
paper/.gitkeep     — placeholder; the PDF itself is not checked in
.gitignore         — keeps PDFs, checkpoints, and results out of git
```

The philosophy, in one line: every paper you run through this produces a working
replication, a legible findings page, and a **skill file** that teaches an agent
(or a person) how to do that replication. Over time the skill files accumulate
into a library of operationalised research methodology, which is the real
product. See [`notes/replication_framing.md`](notes/replication_framing.md).

## Usage

```
replicate <arxiv-id-or-url> [--dest replications] [--overwrite]
```

Accepts bare ids (`1706.03762`), abs URLs, pdf URLs, and pre-2007 style ids
(`cs.CL/0001001`). The slug is derived from the paper title.

After scaffolding:

```
cd replications/<slug>
python download_paper.py   # pulls the PDF into paper/ (gitignored)
# then follow SKILL.md
```

## Status

`v0.1` — scaffold only. No GitHub repo/Pages/CI autogeneration yet; those are
the next layers once the manual replication loop proves out on a few papers.

## Development

```
pip install -e .[dev]
pytest -q
```
