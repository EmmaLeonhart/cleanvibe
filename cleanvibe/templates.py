"""Default templates that cleanvibe injects into new projects.

The CLAUDE.md template is the core of cleanvibe. It shapes how Claude Code
behaves inside a repo by enforcing documentation discipline, meaningful commits,
queue-driven planning, and thoughtful work tracking.
"""

from datetime import datetime
from string import Template

from .arxiv import ArxivPaper


def claude_md(project_name: str) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    return f"""# {project_name}

## Workflow Rules
- **Commit early and often.** Every meaningful change gets a commit with a clear message explaining *why*, not just what.
- **Plan into `queue.md` first, then execute.** When entering planning mode (or doing any non-trivial multi-step work), the FIRST action is to write the plan into `queue.md` as concrete items. Only then begin executing. This means an interrupted session can resume from the queue — the plan does not live only in chat context.
- **Update `queue.md` in the same commit as the work.** When you finish an item, delete it from queue.md in the same commit. A stale queue.md is worse than no queue.md — it lies about what's in flight.
- **Mirror `queue.md` into the task tool.** TaskCreate items as you add them to queue.md; mark `in_progress` when starting; `completed` when done. The two views must not drift.
- **Keep this file up to date.** As the project takes shape, record architectural decisions, conventions, and anything needed to work effectively in this repo.
- **Update README.md regularly.** It should always reflect the current state of the project for human readers.

## Queue and longer-horizon work
- **`queue.md`** — what's being worked on right now. Items get deleted on completion; do not leave checkmarks or status indicators behind. If it's not in `queue.md`, it's not in scope for the current session.
- **`todo.md`** — the **long-term horizon** of the project. Multi-session goals, architectural ambitions, future capabilities, "things we want to do eventually." Items in `todo.md` are *abstract*: they describe a destination, not a step. `todo.md` is the *basis for* `queue.md`: when work begins, an item is pulled from `todo.md`, decomposed into concrete executable steps in `queue.md`, mirrored into the task tool, and executed. As `queue.md` drains, refill it by pulling and decomposing the next `todo.md` item.
- **Flow:** `todo.md` (abstract horizons) → `queue.md` (concrete steps) → task tool (in-flight work) → `git log` (history). Items only ever flow forward; do not leave done items behind in `todo.md` or `queue.md`.
- **Session end condition:** the project's first session ends when `queue.md` is empty, the only items left in `todo.md` are still too abstract to break down further, and the repository is online with green CI. At that point, stop and hand back to the user.

## Testing
- **Write unit tests early.** As soon as there is testable logic, create a test file. Use `pytest` for Python projects or the appropriate test framework for the language in use.
- **Set up CI as soon as tests exist.** Create a `.github/workflows/ci.yml` GitHub Actions workflow that runs the test suite on push and pull request. Keep the workflow simple — install dependencies and run tests.
- **Keep tests passing.** Do not commit code that breaks existing tests. If a change requires updating tests, update them in the same commit.

## Project Description
_TODO: Describe what this project is about._

## Architecture and Conventions
_TODO: Document key decisions, file structure, and patterns as they emerge._

# currentDate
Today's date is {date}.
"""


def readme_md(project_name: str) -> str:
    return f"""# {project_name}

> Scaffolded with [cleanvibe](https://github.com/Immanuelle/cleanvibe).

## About

_TODO: Describe what this project does._

## Getting Started

This project was initialized with `cleanvibe new` and is intended to be developed
with AI-assisted coding via Claude Code.

```
cd {project_name}
claude
```
"""


def todo_md(project_name: str) -> str:
    return f"""# {project_name} — Long-Horizon Backlog

**This file is the long-term horizon of the project, not the current session.** `todo.md` holds multi-session goals, architectural ambitions, future capabilities — things we want to get to *eventually*. Items here are *abstract*: they describe a destination, not a step. Concrete, executable steps live in `queue.md`.

**Flow:**

```
todo.md  (abstract horizons)
   ↓  pick an item, decompose it
queue.md  (concrete executable steps)
   ↓  mirror into task tool, execute
git log  (done)
```

When work begins, the typical move is: pull an item from `todo.md`, break it into a small ordered set of concrete steps in `queue.md`, mirror those into the task tool, and execute. When the queue items are completed, delete the original `todo.md` item too (or replace it with a more specific follow-up that surfaced during the work).

**Session end condition:** the first session ends when `queue.md` is empty, the items remaining in `todo.md` are still too abstract to break down further, and the repository is online with green CI. At that point, stop and hand back.

See `CLAUDE.md` § "Queue and longer-horizon work" for how `todo.md`, `queue.md`, and the task tool stay in sync.

---

## Backlog

_(Populated during bootstrap from the user interview and the inferred project picture. Each item should be a sentence or short paragraph describing a goal or capability — not a checklist, not a step.)_
"""


def queue_md(project_name: str) -> str:
    return f"""# {project_name} — Work Queue

**This file is a queue of *concrete, executable steps*, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `git log`; longer-horizon, *abstract* work lives in `todo.md` and gets decomposed into items here when it's ready to execute. When an item is done, delete it — do not add checkmarks, "done" markers, or status indicators. If an item is still here, it is not done.

**Why this file exists:** when a planning step (formal planning mode or just "think before doing") produces a plan, that plan is written here BEFORE execution starts. That way an interrupted session can pick up from the queue rather than from chat context that may be gone.

The purpose of this file is also to bound scope. If a task is not in this queue, it is not in scope for the current session. New ideas go at the bottom of the queue (or to `todo.md` if they are longer-term / architectural), not silently into whatever is being worked on.

See `CLAUDE.md` § "Workflow Rules" for how this file, planning mode, and the task tool stay in sync.

---

## Active — First-session bootstrap

These items are the default opening sequence for a new cleanvibe project. Work them top to bottom. Delete each item from this file in the same commit that completes it. When this whole section is gone, the project has finished bootstrap and the queue is ready to be repopulated with real product work (see the final item).

1. **Triage user-supplied files into `data_lake/`.** Look at everything in the repo that isn't part of the cleanvibe scaffold (i.e. anything the user dropped in: notes, exports, spec PDFs, sample data, mockups, etc.).
   - `data_lake/` already exists — the scaffold created it with a `.gitkeep` (so a user could drop files straight into it before this session). Move all such files into `data_lake/` so the project root stays clean. Only the scaffold (`CLAUDE.md`, `README.md`, `queue.md`, `.gitignore`, `LICENSE`, and any source/config files you have explicitly chosen to keep at the root) should live at the top level. Leave the `.gitkeep` in place.
   - If any of these files are `.zip` archives, extract them into `data_lake/` alongside the originals, then add the `.zip` files to `.gitignore` (we keep the extracted contents in git, not the archives).
   - For any file that looks big enough to need Git LFS (rough rule of thumb: >50 MB, or large binary like video/audio/large datasets), STOP and ask the user before doing anything — do not silently commit it, do not silently `git lfs track` it.
   - Commit. Commit message should describe what got moved/extracted and why.

2. **Read the data lake to infer what this project is.** Skim every file in `data_lake/` (text files, READMEs from extracted zips, design notes, spec docs, sample data shapes). Build up a working hypothesis: what is the user trying to build? What domain? What constraints or instructions are stated explicitly?
   - Update `README.md` to reflect this hypothesis: project description, any explicit instructions you found, anything load-bearing for future sessions.
   - Update `CLAUDE.md`'s "Project Description" and "Architecture and Conventions" sections to capture the same context for future Claude sessions.
   - Do NOT touch `queue.md` in this commit — the real queue gets written later, after talking to the user.
   - Commit. Commit message should briefly explain how the inferred description was derived (e.g. "Inferred project scope from data_lake/spec.md and data_lake/notes/").

3. **Interview the user about what they actually want to build.** Your inferred picture from the data lake is a starting point, not the spec. Ask the user direct, specific questions to fill in the gaps: what is the goal of the first usable version? What's the longer-term vision (capabilities, integrations, audience) beyond v1? What's in scope vs. out of scope for this session? Are there constraints (language, framework, deployment target, must-integrate-with-X)? What does "done" look like for them today?
   - As answers come in, fold them into `README.md` and `CLAUDE.md` so future sessions inherit the context.
   - Capture both **near-term** answers (what to build now) AND **long-horizon** answers (what's wanted eventually). The long-horizon material is what feeds `todo.md` in the next step.
   - Commit once the picture is concrete enough to plan against.

4. **Create `todo.md` — the long-horizon backlog.** This is the step before any concrete queue gets written. Based on the interview and inferred picture, write `todo.md` as the project's long-term horizon: every multi-session goal, architectural ambition, capability, integration, or future direction the user described. Items here are *abstract destinations*, not steps — they will be decomposed into concrete tasks in `queue.md` later, one at a time, as the work unfolds. `todo.md` is the *basis for* `queue.md`: work flows `todo.md` → `queue.md` → executed → deleted from both.
   - Use the convention described in `CLAUDE.md` § "Queue and longer-horizon work" for the file format.
   - Do NOT touch `queue.md` in this commit — populating the real queue is the *next* step.
   - Commit `todo.md` on its own so the long-horizon picture is a reviewable artifact, not buried inside a larger change.

5. **Replace this bootstrap queue with the real project queue.** Pull the first item (or first few items) from `todo.md` and decompose them into a concrete, ordered list of implementation tasks. Write those into the `## Active` section of this file (deleting this bootstrap section entirely as part of the same edit). Each task should be small enough to finish and commit on its own. Mirror the queue into the task tool. As you drain queue items, refill by pulling and decomposing more from `todo.md`.
   - Commit the new queue.

6. **Create a private GitHub repo and push.** Use whatever GitHub tooling is available (e.g. `gh repo create --private --source=. --push`) to create a private remote and push the current branch. Confirm CI (`.github/workflows/`) is wired up so pushes run tests.

7. **Work the queue until the stop condition.** Pull the top item, do it, delete it from `queue.md` in the same commit as the work, push, let CI run. When `queue.md` empties, refill from `todo.md` by decomposing the next item. New ideas that surface mid-work go to the bottom of the queue (or to `todo.md` if they're longer-horizon), not into the currently-in-flight task. **Stop** when: `queue.md` is empty, the items still in `todo.md` are too abstract to break down further without more user input, and the repository is online with green CI. At that point, hand back to the user.

---

## Pointers

- Long-horizon backlog (abstract goals, source of future queue items): `todo.md`.
- Narrative history: `git log`.
"""


RUNCLAUDE_BAT = """@echo off
cd /d "%~dp0"
claude
"""


GITIGNORE = """# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
*.egg
.eggs/

# Virtual environments
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
"""


# ---------------------------------------------------------------------------
# Replication project templates (`cleanvibe replicate`)
#
# A replication project is a standalone cleanvibe project dedicated to one
# paper. Structure: the paper itself lives at `replication_target/paper.pdf`
# (gitignored — NOT in data_lake/); `data_lake/` still exists for other
# downloaded material; the authors' code, if any, is cloned as a git
# submodule under `replication_target/`; the deliverables (a GitHub Pages
# site, a transportable PDF report, and a downloadable ZIP replication
# package) are built by GitHub Actions, never committed as directories.
#
# All text templates below are string.Template (stdlib) — no package data,
# no third-party deps. The workflow YAMLs are static constants (they contain
# GitHub `${{ }}` expressions and must NOT pass through Template).
# ---------------------------------------------------------------------------


def _replication_subs(paper: ArxivPaper) -> dict:
    return {
        "title": paper.title,
        "arxiv_id": paper.arxiv_id,
        "slug": paper.slug,
        "authors": ", ".join(paper.authors) if paper.authors else "unknown",
        "published": paper.published,
        "pdf_url": paper.pdf_url,
        "summary": paper.summary,
        "html_url": f"https://arxiv.org/html/{paper.arxiv_id}",
    }


_REPLICATION_CLAUDE_TMPL = Template(
    """# replicating-$slug

## Project Description

This is a **paper replication** project (scaffolded by `cleanvibe replicate`).
The goal is to reproduce the headline results of:

> **$title**
> arXiv:$arxiv_id - $authors - $published
> PDF: $pdf_url - HTML: $html_url

It produces three compounding artifacts (see `docs/replication_framing.md`
in the cleanvibe repo for the full framing): the runnable replication, a
legibility layer (the published findings report), and `SKILL.md` — the
reusable, agent-executable replication methodology.

## Architecture and Conventions

- **`replication_target/`** holds the paper and everything pulled *about* it:
  - `replication_target/paper.pdf` — the downloaded paper (gitignored; run
    `python download_paper.py`). The paper does NOT go in `data_lake/`.
  - `replication_target/paper.md` — a Markdown extraction of the paper's
    arXiv HTML, for working from structured text. (Extract it during the
    replication; an automated extractor is a cleanvibe horizon, not built yet.)
  - the authors' code, if any, cloned as a **git submodule** in here
    (`git submodule add <repo> replication_target/<name>`).
- **`data_lake/`** — other downloaded/supplied material (datasets, notes,
  exports). Same cleanvibe convention as every project. The paper is NOT here.
- **`src/`** — your reimplementation. **`scripts/run.py`** — the entry point
  CI invokes. **`results/`** — metrics JSON (gitignored). **`FINDINGS.md`** —
  the report (reproduced vs. reported, gaps, divergences).
- **Deliverables are built by GitHub Actions, not committed.**
  `.github/workflows/pages.yml` publishes the GitHub Pages site + PDF report;
  `.github/workflows/package.yml` builds the downloadable ZIP replication
  package. You must make the repo public and enable Pages (Settings -> Pages
  -> Source: GitHub Actions) — the workflows carry TODO markers for this.
  Vision for the site shape: http://sutra.emmaleonhart.com/

## Workflow Rules

- **Commit early and often.** Every meaningful change gets a descriptive commit.
- **Plan into `queue.md` first, then execute.** The replication plan already
  lives in `queue.md` (derived from `SKILL.md`). Work it top to bottom.
- **Update `queue.md` in the same commit as the work.** Delete completed
  items; no checkmarks.
- **Keep `SKILL.md` truthful.** It is the compounding artifact. If you
  deviated from its plan, edit the plan to match what you actually did.
- **Keep this file and `README.md` current** as the replication takes shape.
"""
)


_REPLICATION_QUEUE_TMPL = Template(
    """# replicating-$slug - Work Queue

**This file is a queue of concrete, executable steps, not a state snapshot.**
Finished work lives in `git log`; longer-horizon items live in `todo.md`.
When an item is done, delete it — no checkmarks, no status indicators.

**Why this file exists:** the replication plan is written here BEFORE
execution so an interrupted session resumes from the queue, not from chat.
The canonical methodology is `SKILL.md`; this queue is its executable form.

---

## Active — Replicate "$title" (arXiv:$arxiv_id)

Work top to bottom. Delete each item in the same commit that completes it.

1. **Download the paper.** Run `python download_paper.py` — it writes
   `replication_target/paper.pdf` (gitignored). Do not proceed if it is empty.
   Also save a Markdown extraction of the arXiv HTML ($html_url) to
   `replication_target/paper.md` so later steps work from structured text.

2. **Read the paper; record `notes/claims.md`:** headline claim(s); datasets
   (version/hash, where they live); models/methods in enough detail to
   re-implement; evaluation metrics and the exact reported numbers; compute
   envelope (GPU type, hours, memory) — used to decide if CI can auto-run it.
   Commit.

3. **Find the authors' code.** Check the arXiv "Code" link, paperswithcode,
   GitHub (title + first-author). If official code exists, add it as a git
   submodule under `replication_target/` and record the decision in
   `notes/sources.md` (fork-and-verify vs. independent reimplementation).
   Commit.

4. **Set up the environment.** `requirements.txt` / `environment.yml` pinned
   to versions that work; minimum set needed for the headline claim. Commit.

5. **Reimplement the method** under `src/` — scope to the headline claim,
   not every ablation. Commit as you go.

6. **Run the replication.** Script it as `scripts/run.py` so CI can invoke
   it; capture metrics as JSON into `results/`. Commit.

7. **Write `FINDINGS.md`:** reproduced vs. reported numbers (table); gaps you
   had to fill (hyperparameters, preprocessing, omitted architecture details);
   where and why it diverged. Commit.

8. **Publish the deliverables.** Confirm `.github/workflows/pages.yml` builds
   the GitHub Pages site + PDF report and `.github/workflows/package.yml`
   builds the ZIP replication package. Make the repo public; enable Pages
   (Settings -> Pages -> Source: GitHub Actions). Update `SKILL.md` so it
   reflects how you actually did this. Commit.

9. **Stop / hand back** when `FINDINGS.md` reports at least one headline
   number with its reproduced value, `scripts/run.py` runs end-to-end from a
   clean clone (or documents the un-automatable data step), and the Pages
   deployment is green.

---

## Pointers

- Methodology / definition of done: `SKILL.md`.
- Long-horizon items: `todo.md`.
- Narrative history: `git log`.
"""
)


_REPLICATION_SKILL_TMPL = Template(
    """---
name: replicate-$slug
description: Replicate the methods of "$title" (arXiv:$arxiv_id) and produce a runnable artifact, a published findings report, and a downloadable replication package.
---

# Replicate: $title

arXiv:$arxiv_id - $authors - $published
PDF: $pdf_url - HTML: $html_url

## Prerequisite

If `replication_target/paper.pdf` is missing, run `python download_paper.py`
first. Don't proceed without the paper. Prefer working from
`replication_target/paper.md` (a Markdown extraction of the arXiv HTML) when
it is present.

## Plan

1. **Acquire the paper.** PDF -> `replication_target/paper.pdf` (gitignored).
   Extract the arXiv HTML to `replication_target/paper.md` for structured text.

2. **Read the paper.** Record in `notes/claims.md`: headline claim(s);
   datasets (version/hash, location); models/methods in re-implementable
   detail; evaluation metrics and the exact reported numbers; compute
   envelope (used to decide if CI can auto-run this).

3. **Find the authors' code.** arXiv "Code" link, paperswithcode, GitHub
   (title + first-author). If official code exists, add it as a **git
   submodule** under `replication_target/` and record in `notes/sources.md`
   whether you fork-and-verify or independently reimplement.

4. **Set up the environment.** `environment.yml` / `requirements.txt` pinned
   to working versions; minimum dependency set for the headline claim.

5. **Reimplement the method.** Code under `src/`. Scope to the headline
   claim, not every ablation.

6. **Run the replication.** `scripts/run.py` so CI can invoke it. Capture
   metrics as JSON into `results/`.

7. **Write the findings.** `FINDINGS.md`: reproduced vs. reported numbers
   (table); gaps you filled; where it diverged and why.

8. **Publish.** GitHub Pages deploys the findings + a transportable PDF
   report (`.github/workflows/pages.yml`); a ZIP replication package is built
   and offered for download (`.github/workflows/package.yml`). The repo must
   be public with Pages enabled.

## Budget guardrails

- If the paper's reported compute is more than ~4 GPU-hours on a single
  consumer GPU, mark this replication **not CI-runnable** in `paper.json` and
  document the reduced-scale variant instead.
- Prefer deterministic seeds and logged hashes so reruns are comparable.

## Definition of done

- `FINDINGS.md` exists and reports at least one headline number from the
  paper, with the reproduced value next to it.
- `scripts/run.py` runs end-to-end from a clean clone (or documents the data
  step that can't be automated).
- The GitHub Pages site and the ZIP package build green in Actions.
- This file still reflects how you actually did it — if you deviated, edit
  the plan above.
"""
)


_REPLICATION_README_TMPL = Template(
    """# Replicating: $title

**arXiv:** [$arxiv_id]($pdf_url) - **HTML:** [$arxiv_id]($html_url)
**Authors:** $authors
**Published:** $published

## Abstract

$summary

## Replication status

Not started. The agent-executable plan is in [`SKILL.md`](./SKILL.md);
the concrete step queue is in [`queue.md`](./queue.md).

## What this repo produces

Three compounding artifacts:

1. **The replication** — runnable code under `src/` + `scripts/run.py`.
2. **The legibility layer** — `FINDINGS.md`, published as a GitHub Pages
   site with a transportable PDF report (built by GitHub Actions).
3. **`SKILL.md`** — a reusable, agent-executable replication methodology.

## Layout

- `replication_target/` — the paper and everything pulled about it:
  - `paper.pdf` — downloaded PDF (gitignored; `python download_paper.py`).
  - `paper.md` — Markdown extraction of the arXiv HTML (for structured text).
  - the authors' code, if any, as a git **submodule**.
- `data_lake/` — other downloaded/supplied material (NOT the paper).
- `src/` — your reimplementation. `scripts/run.py` — CI entry point.
- `results/` — metrics JSON (gitignored). `FINDINGS.md` — the report.
- `paper.json` — frozen metadata pulled from the arXiv API.
- `.github/workflows/` — `pages.yml` (site + PDF), `package.yml` (ZIP).

## Deliverables (GitHub Actions)

To publish, **make this repo public** and set **Settings -> Pages -> Source:
GitHub Actions**. Then `pages.yml` deploys the findings site + PDF report and
`package.yml` builds a downloadable ZIP replication package. Site shape
inspiration: http://sutra.emmaleonhart.com/
"""
)


_REPLICATION_DOWNLOAD_TMPL = Template(
    '''"""Download the PDF for arXiv:$arxiv_id into replication_target/paper.pdf."""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

PDF_URL = "$pdf_url"
ARXIV_ID = "$arxiv_id"


def main() -> int:
    out = Path(__file__).parent / "replication_target" / "paper.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 0:
        print(f"already present: {out}")
        return 0
    print(f"downloading {PDF_URL} -> {out}")
    req = urllib.request.Request(PDF_URL, headers={"User-Agent": "cleanvibe-replicate"})
    with urllib.request.urlopen(req) as resp, open(out, "wb") as f:
        f.write(resp.read())
    print(f"wrote {out.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
)


REPLICATION_GITIGNORE = """# The paper itself — downloaded, never committed
replication_target/*.pdf
replication_target/*.html
!replication_target/.gitkeep

# Replication outputs
results/
checkpoints/
*.ckpt
*.pt
*.pth
wandb/

# Build / deliverables (produced by GitHub Actions, not committed)
site/
*.zip
report.pdf

# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
dist/
build/

# Virtual environments
.venv/
venv/
env/

# IDE / OS / env
.vscode/
.idea/
*.swp
.DS_Store
Thumbs.db
.env
.env.local
"""


# GitHub Actions: build the findings Pages site + transportable PDF report.
# Static constant — contains ${{ }} expressions; never run through Template.
REPLICATION_PAGES_YML = """# Publishes FINDINGS.md as a GitHub Pages site + a transportable PDF report.
#
# TODO (one-time, by the repo owner):
#   1. Make this repository public.
#   2. Settings -> Pages -> Source: "GitHub Actions".
# Until then this workflow will run but the deploy step has nothing to serve.

name: pages

on:
  push:
    branches: [main, master]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - name: Install pandoc
        run: sudo apt-get update && sudo apt-get install -y pandoc
      - name: Build site + PDF report
        run: |
          mkdir -p site
          # Findings page (falls back to README if FINDINGS.md not written yet)
          SRC=FINDINGS.md
          [ -f "$SRC" ] || SRC=README.md
          pandoc "$SRC" -s -o site/index.html --metadata title="Replication report"
          pandoc "$SRC" -o site/report.pdf || echo "PDF render skipped"
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
"""


# GitHub Actions: assemble the downloadable ZIP replication package.
# Static constant — contains ${{ }} expressions; never run through Template.
REPLICATION_PACKAGE_YML = """# Builds a downloadable ZIP "replication package": the replication code plus
# the necessary code from the paper's repo (the submodule), excluding the
# gitignored paper binary and git internals. Uploaded as a build artifact and,
# on a published release, attached as a release asset.

name: package

on:
  workflow_dispatch:
  release:
    types: [published]

permissions:
  contents: write

jobs:
  package:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - name: Build replication package zip
        run: |
          NAME="replication-package"
          git ls-files --recurse-submodules > /tmp/files.txt
          # Drop the (gitignored anyway) paper binaries if present
          grep -v -E 'replication_target/.*\\.(pdf|html)$' /tmp/files.txt > /tmp/keep.txt
          zip -q "$NAME.zip" -@ < /tmp/keep.txt
          echo "built $NAME.zip ($(du -h "$NAME.zip" | cut -f1))"
      - uses: actions/upload-artifact@v4
        with:
          name: replication-package
          path: replication-package.zip
      - name: Attach to release
        if: github.event_name == 'release'
        uses: softprops/action-gh-release@v2
        with:
          files: replication-package.zip
"""


def replication_claude_md(paper: ArxivPaper) -> str:
    return _REPLICATION_CLAUDE_TMPL.substitute(_replication_subs(paper))


def replication_queue_md(paper: ArxivPaper) -> str:
    return _REPLICATION_QUEUE_TMPL.substitute(_replication_subs(paper))


def replication_skill_md(paper: ArxivPaper) -> str:
    return _REPLICATION_SKILL_TMPL.substitute(_replication_subs(paper))


def replication_readme_md(paper: ArxivPaper) -> str:
    return _REPLICATION_README_TMPL.substitute(_replication_subs(paper))


def replication_download_paper_py(paper: ArxivPaper) -> str:
    return _REPLICATION_DOWNLOAD_TMPL.substitute(_replication_subs(paper))
