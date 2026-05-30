"""Default templates that cleanvibe injects into new projects.

The CLAUDE.md template is the core of cleanvibe. It shapes how Claude Code
behaves inside a repo by enforcing documentation discipline, meaningful commits,
queue-driven planning, and thoughtful work tracking.
"""

from __future__ import annotations

from datetime import datetime
from string import Template

from . import __version__
from .arxiv import ArxivPaper, _slugify
from .clawrxiv import ClawrxivPaper


# ---------------------------------------------------------------------------
# Shared CLAUDE.md building blocks
#
# As of v1.14.0 the workflow rules, writing rule, cron playbook, weekly-update
# check, and emergency-stop text are no longer inlined into CLAUDE.md — they
# ship as standalone skills (see skills.py), vendored into each repo's
# .claude/skills/ by scaffold.write_skills(). CLAUDE.md now carries only the
# short SKILLS_POINTER below plus project-specific content. The old
# _CLAUDE_CORE_RULES / _WRITING_SECTION / _common_claude_tail helpers were
# removed in v1.14.0; the replication templates were already exempt from the
# cron tail and are unaffected.
# ---------------------------------------------------------------------------

SKILLS_POINTER = """## Skills

Workflow behaviors live as skills in `.claude/skills/` (auto-discovered by Claude Code):
`emergency-stop`, `cron-is-local`, `autonomous-loop`, `queue-driven-workflow`,
`writing-style`, `cleanvibe-update-check`. They are vendored into this repo and kept
current by the `cleanvibe-update-check` skill.

- **Last cleanvibe update check:** `never`
- **Updates source:** <https://cleanvibe.emmaleonhart.com/updates.md>"""


def claude_md(project_name: str) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    return f"""# {project_name}

{SKILLS_POINTER}

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
devlog.md  (dated entries — "done" lives here)
   +
git log  (narrative history)
```

When work begins, the typical move is: pull an item from `todo.md`, break it into a small ordered set of concrete steps in `queue.md`, mirror those into the task tool, and execute. When a queue item is finished, **delete it from `queue.md` and append a dated entry to `devlog.md` in the same commit**. When all the queue items decomposed from a `todo.md` entry are done, delete the original `todo.md` item too (or replace it with a more specific follow-up that surfaced during the work).

**Session end condition:** the first session ends when `queue.md` is empty, the items remaining in `todo.md` are still too abstract to break down further, and the repository is online with green CI. At that point, stop and hand back.

See `CLAUDE.md` § "Queue and longer-horizon work" for how `todo.md`, `queue.md`, and the task tool stay in sync.

---

## Backlog

_(Populated during bootstrap from the user interview and the inferred project picture. Each item should be a sentence or short paragraph describing a goal or capability — not a checklist, not a step.)_
"""


def devlog_md(project_name: str, clone: bool = False) -> str:
    """The devlog — where "done" lives, so `queue.md` can stay delete-only.

    `clone=True` produces the variant injected by `cleanvibe clone` for an
    *existing* repo: the first entry tells the agent to backfill the rest of
    the devlog from `git log` / existing release history.
    """
    date = datetime.now().strftime("%Y-%m-%d")
    if clone:
        first_entry = f"""## {date} — cleanvibe onboarding started

Onboarded with `cleanvibe clone` (cleanvibe v{__version__}). This is an
**existing repository**, so the very first onboarding task is to **backfill
the rest of this devlog from `git log`** (tagged releases, milestone
commits, merged feature branches). After that, every finished queue item
appends a new dated entry here.
"""
    else:
        first_entry = f"""## {date} — Project scaffolded

Scaffolded with `cleanvibe new` (cleanvibe v{__version__}). Future entries
land here as queue items get deleted.
"""
    return f"""# {project_name} — Devlog

**This file is where "done" lives.** `queue.md` is delete-only: when a queue
item is finished, the item is **deleted from `queue.md`** and a dated entry
is **appended here**, in the same commit as the work, then pushed. Never
tick a box in place — a checked box left in `queue.md` is the failure mode
this file exists to prevent.

Also record releases (tag + a one-line note), notable milestones, and
anything else worth a chronological trail. Newest entries at the bottom.

This is the **same convention as the cleanvibe repo's own `devlog.md`** —
every cleanvibe-scaffolded project gets one for the same reason.

See `CLAUDE.md` § "Workflow Rules" and `queue.md`'s preamble.

---

{first_entry}"""


def queue_md(project_name: str) -> str:
    return f"""# {project_name} — Work Queue

**This file is a queue of *concrete, executable steps*, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `devlog.md` (a dated entry) and `git log`; longer-horizon, *abstract* work lives in `todo.md` and gets decomposed into items here when it's ready to execute. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Do not add checkmarks, "done" markers, or status indicators in place. If an item is still here, it is not done.

**Why this file exists:** when a planning step (formal planning mode or just "think before doing") produces a plan, that plan is written here BEFORE execution starts. That way an interrupted session can pick up from the queue rather than from chat context that may be gone.

The purpose of this file is also to bound scope. If a task is not in this queue, it is not in scope for the current session. New ideas go at the bottom of the queue (or to `todo.md` if they are longer-term / architectural), not silently into whatever is being worked on.

See `CLAUDE.md` § "Workflow Rules" for how this file, planning mode, and the task tool stay in sync.

**Three-cron playbook.** Extensive work runs under three local `CronCreate` jobs — **work-loop at :03** (the engine that drains `queue.md` and refills it from `todo.md`), **auto-flush at :15** (commit/push backstop), and **status-report at :42** (heartbeat). On a fresh session they are **started** as the opening step (bootstrap step 1 below); on a mid-session **large-scale re-fill** of this queue the FIRST item worked is instead to **kill** the already-running crons. Either way the **last two items are always pinned at the tail** — ensure the three crons are running, then run an end-of-session summary (see the `## Always last` section below and `CLAUDE.md` § "Autonomous productivity loop — the three-cron playbook"). Entering planning mode also disables the crons; their restart lives at the end of the queue.

---

## Active — First-session bootstrap

These items are the default opening sequence for a new cleanvibe project. Work them top to bottom. **Delete each item from this file in the same commit that completes it, and append a dated entry to `devlog.md` recording the step.** Push after every step. When this whole section is gone, the project has finished bootstrap and the queue is ready to be repopulated with real product work (see the final item).

1. **Start the three-cron playbook.** Use the `CronCreate` tool to schedule three local crons (all `durable: false`): **work-loop at `3 * * * *`** (sync → take top actionable `queue.md` item / promote from `todo.md` → hold the hard rails → commit + push → one-line report), **auto-flush at `15 * * * *`** (commit + push pending work, no empty commits), and **status-report at `42 * * * *`** (reporting only, no code changes). Together they turn this bootstrap run into a self-sustaining hourly cadence so a long autonomous session can't silently lose the thread. (See `CLAUDE.md` § "Autonomous productivity loop — the three-cron playbook"; the `## Always last` section pinned at the tail keeps them running — starting them here, restarting them there if a later planning burst / queue re-fill kills them.)

2. **Triage user-supplied files into `data_lake/`.** Look at everything in the repo that isn't part of the cleanvibe scaffold (i.e. anything the user dropped in: notes, exports, spec PDFs, sample data, mockups, etc.).
   - `data_lake/` already exists — the scaffold created it with a `.gitkeep` (so a user could drop files straight into it before this session). Move all such files into `data_lake/` so the project root stays clean. Only the scaffold (`CLAUDE.md`, `README.md`, `queue.md`, `.gitignore`, `LICENSE`, and any source/config files you have explicitly chosen to keep at the root) should live at the top level. Leave the `.gitkeep` in place.
   - If any of these files are `.zip` archives, extract them into `data_lake/` alongside the originals, then add the `.zip` files to `.gitignore` (we keep the extracted contents in git, not the archives).
   - For any file that looks big enough to need Git LFS (rough rule of thumb: >50 MB, or large binary like video/audio/large datasets), STOP and ask the user before doing anything — do not silently commit it, do not silently `git lfs track` it.
   - Commit. Commit message should describe what got moved/extracted and why.

3. **Read the data lake to infer what this project is.** Skim every file in `data_lake/` (text files, READMEs from extracted zips, design notes, spec docs, sample data shapes). Build up a working hypothesis: what is the user trying to build? What domain? What constraints or instructions are stated explicitly?
   - Update `README.md` to reflect this hypothesis: project description, any explicit instructions you found, anything load-bearing for future sessions.
   - Update `CLAUDE.md`'s "Project Description" and "Architecture and Conventions" sections to capture the same context for future Claude sessions.
   - Do NOT touch `queue.md` in this commit — the real queue gets written later, after talking to the user.
   - Commit. Commit message should briefly explain how the inferred description was derived (e.g. "Inferred project scope from data_lake/spec.md and data_lake/notes/").

4. **Interview the user about what they actually want to build.** Your inferred picture from the data lake is a starting point, not the spec. Ask the user direct, specific questions to fill in the gaps: what is the goal of the first usable version? What's the longer-term vision (capabilities, integrations, audience) beyond v1? What's in scope vs. out of scope for this session? Are there constraints (language, framework, deployment target, must-integrate-with-X)? What does "done" look like for them today?
   - As answers come in, fold them into `README.md` and `CLAUDE.md` so future sessions inherit the context.
   - Capture both **near-term** answers (what to build now) AND **long-horizon** answers (what's wanted eventually). The long-horizon material is what feeds `todo.md` in the next step.
   - Commit once the picture is concrete enough to plan against.

5. **Create `todo.md` — the long-horizon backlog.** This is the step before any concrete queue gets written. Based on the interview and inferred picture, write `todo.md` as the project's long-term horizon: every multi-session goal, architectural ambition, capability, integration, or future direction the user described. Items here are *abstract destinations*, not steps — they will be decomposed into concrete tasks in `queue.md` later, one at a time, as the work unfolds. `todo.md` is the *basis for* `queue.md`: work flows `todo.md` → `queue.md` → executed → deleted from both.
   - Use the convention described in `CLAUDE.md` § "Queue and longer-horizon work" for the file format.
   - Do NOT touch `queue.md` in this commit — populating the real queue is the *next* step.
   - Commit `todo.md` on its own so the long-horizon picture is a reviewable artifact, not buried inside a larger change.

6. **Replace this bootstrap queue with the real project queue.** Pull the first item (or first few items) from `todo.md` and decompose them into a concrete, ordered list of implementation tasks. Write those into the `## Active` section of this file (deleting this bootstrap section entirely as part of the same edit). Each task should be small enough to finish and commit on its own. Mirror the queue into the task tool. As you drain queue items, refill by pulling and decomposing more from `todo.md`.
   - **Keep the `## Always last — restart the three crons and summarize` section pinned at the very bottom of the queue.** It is never deleted; real work items go above it. The real queue's FIRST work item should **start the three crons (work-loop, auto-flush, status-report)** — unless this is a mid-session large-scale re-fill while they are already running, in which case the first item is instead to **kill them** (the pinned tail restarts them). Planning mode disables the crons; the tail brings them back.
   - Commit the new queue.

7. **Create a private GitHub repo and push.** Use whatever GitHub tooling is available (e.g. `gh repo create --private --source=. --push`) to create a private remote and push the current branch. Confirm CI (`.github/workflows/`) is wired up so pushes run tests.

8. **Work the queue until the stop condition.** Pull the top item, do it, **delete it from `queue.md` AND append a dated entry to `devlog.md`** in the same commit as the work, push, let CI run. When `queue.md` empties, refill from `todo.md` by decomposing the next item. New ideas that surface mid-work go to the bottom of the queue (or to `todo.md` if they're longer-horizon), not into the currently-in-flight task. **Stop** when: `queue.md` is empty, the items still in `todo.md` are too abstract to break down further without more user input, and the repository is online with green CI. At that point, hand back to the user.

---

## Always last — restart the three crons and summarize

**These two items stay pinned to the tail of the queue at all times** — below every bootstrap step and below every real work item. They are the closing half of the three-cron lifecycle described in `CLAUDE.md` § "Autonomous productivity loop — the three-cron playbook": the crons are **started** at the beginning of extensive work (a fresh session starts them as the opening item; a mid-session large-scale re-fill instead kills the already-running crons as its first item, and planning mode disables them), and these are always the LAST two, after everything else — they bring them back and sign off:

A. **Ensure the three crons are running** — start them if this session never did, restart them if a planning burst / queue re-fill killed them: work-loop (`3 * * * *`), auto-flush (`15 * * * *`), status-report (`42 * * * *`).
B. **Run the status-report action once more, independently** — an end-of-session summary of everything that happened this session.

(During first-session bootstrap these simply sit here at the bottom; they become load-bearing the moment the queue is filled with a large batch of created tasks.)

---

## Pointers

- Long-horizon backlog (abstract goals, source of future queue items): `todo.md`.
- Completed work (chronological, with releases): `devlog.md`.
- Narrative history: `git log`.
"""


def clone_claude_md(project_name: str) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    return f"""# {project_name} — cleanvibe onboarding

> This repository was **cloned and is being onboarded** by `cleanvibe clone`
> on {date}. cleanvibe checked out a dedicated `cleanvibe-onboarding` branch
> and committed this file plus `queue.md` onto it — the default branch is
> untouched. This is an *existing codebase*, not a fresh project: there is no
> `data_lake/` because nothing was dropped in to triage.

## How to work here

- **Work `queue.md` top to bottom.** It is a small onboarding sequence:
  understand the repo, get its documentation accurate, make `CLAUDE.md` reflect
  the repo's real practices, ensure tests/CI exist, then hand off to the
  repo's own backlog.
- **This file is provisional.** Do not impose cleanvibe conventions on a repo
  that already has its own. As you learn how this project actually works
  (language, framework, test runner, build, commit/branch conventions, CI,
  review norms), **rewrite this `CLAUDE.md`** to capture *those* practices so
  future sessions inherit the real contract — not this placeholder.
- **Commit early and often on the `cleanvibe-onboarding` branch.** Keep
  existing tests green. Don't fight the project's established style.
- If the repo already has planning artifacts (`todo.md`, `queue.md`,
  `ROADMAP`, `BACKLOG`), synthesize their intent rather than overwriting them.

## Workflow Rules (until replaced by the repo's real ones)

- Plan into `queue.md` before executing; **delete finished items from
  `queue.md` AND append a dated entry to `devlog.md` in the same commit as
  the work**, then push. Never tick boxes in place.
- `devlog.md` is where "done" lives — it also records releases and
  milestones. cleanvibe injected a starter `devlog.md` whose first
  onboarding task is to **backfill it from `git log`** so the chronological
  trail is accurate before normal onboarding begins.
- Keep documentation truthful as you go — that is the whole point of this
  onboarding pass.

## Writing

- Do not use "honest", "honesty", or "honestly" — and do not swap in "frank", "frankly", "candid", "candidly", or "transparently", which are the same self-congratulatory move in a different coat. When something failed, name the failure: "it didn't work", "I got that wrong", "this failed" — flat, no qualifier. Tagging a report "honest" implies the rest aren't, and couching a failure as honesty asks for credit for the admission, which is worse than the failure itself. Use a precise positive word ("accurate", "plainly", "truly") only when that is genuinely the meaning — never as a halo on a bad outcome.
"""


def clone_queue_md(project_name: str) -> str:
    return f"""# {project_name} — Onboarding Queue

**This file is a queue, not a state snapshot.** It is the short onboarding
sequence `cleanvibe clone` injects for an *existing* codebase. Finished work
lives in `devlog.md` (dated entries) and `git log`. **When an item is done,
delete it from this file AND append a dated entry to `devlog.md` in the
same commit, then push.** No checkmarks.

See `CLAUDE.md` for how to work in this onboarding branch. Note: there is no
`data_lake/` here — this is a real repository, not dropped-in files.

---

## Active — Onboarding

`cleanvibe clone` already did step 0: cloned the repo, created and checked
out the `cleanvibe-onboarding` branch, and committed these onboarding files
(including a starter `devlog.md`). Work the rest top to bottom; delete each
item AND append a `devlog.md` entry in the commit that completes it.

1. **Backfill `devlog.md` from existing history.** cleanvibe wrote a starter
   `devlog.md` whose first entry only says "onboarding started". Before
   anything else, walk `git log` (and any existing release tags / GitHub
   Releases / CHANGELOG) and backfill chronological milestone entries:
   tagged releases (date + one-line note), major feature merges, big
   refactors, incidents worth remembering. From this point on, every
   finished queue item also gets a dated `devlog.md` entry. Commit.

2. **Read the whole repository.** Build an accurate mental map: directory
   layout, entry points, how to build/run it, how to test it, dependencies,
   CI, and the project's apparent conventions. Capture this understanding as
   you go (it feeds the next two steps).

3. **Make the documentation accurate.** If the repo has docs (`README`, `docs/`,
   wiki) that are stale or thin, correct and extend them to match what the
   code actually does. If documentation is missing, write concise docs
   covering setup, usage, and architecture.

4. **Rewrite `CLAUDE.md` to the repo's real practices.** Replace the
   provisional onboarding text with the project's actual development
   contract: language/framework, test runner, build, commit and branch
   conventions, CI, review norms. This is the durable artifact future
   sessions inherit. **Keep the devlog rule** (delete from queue + append
   dated entry to `devlog.md` in the same commit; never tick boxes).

5. **Tests & CI.** If tests are sparse or absent, add a baseline suite for
   the core paths using the project's existing/most-appropriate framework.
   If there is no CI, add a minimal workflow that runs the tests. Keep any
   existing tests passing.

6. **Synthesize planning artifacts and hand off.** If the repo already has a
   `todo.md` / `queue.md` / `ROADMAP` / `BACKLOG`, merge their intent into the
   repo's own `todo.md` (its real backlog). Then stop driving from THIS
   onboarding queue and start working the repo's own `todo.md`.

If `cleanvibe clone` is run again later, it prepends a fresh onboarding block
to the top of `CLAUDE.md` and `queue.md`. Treat the top-most block as the
current marching orders and reconcile it with the content preserved below it.

---

## Pointers

- The repo's own backlog (work this once onboarding is done): `todo.md`.
- Completed work + releases (chronological): `devlog.md`.
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
        "id_with_version": paper.id_with_version,
        "slug": paper.slug,
        "authors": ", ".join(paper.authors) if paper.authors else "unknown",
        "published": paper.published,
        "pdf_url": paper.pdf_url,
        "summary": paper.summary,
        # Prefer the exact version when known. The LaTeX/e-print **source** is
        # the primary download: it is far more token-efficient than the rendered
        # HTML (no base64 figure blobs) and is where authors most often ship a
        # reproduction recipe. HTML is kept available as a tertiary fallback.
        "src_url": f"https://arxiv.org/src/{paper.id_with_version}",
        "html_url": f"https://arxiv.org/html/{paper.id_with_version}",
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

- **The efficient path is recipe-first.** Authors very often ship a
  reproduction recipe right in the paper's e-print source (usually near the
  end). Find and run it FIRST, then verify its output against the paper and
  fill only the gaps. A from-scratch reimplementation is the fallback, not the
  default — it is what burned a huge amount of tokens before this convention.
- **`replication_target/`** holds the paper and everything pulled *about* it:
  - `replication_target/source/` — the extracted arXiv **LaTeX/e-print
    source** (committed; run `python download_paper.py`). **Primary** source:
    the `.tex` reads far more token-efficiently than the rendered HTML (no
    base64 figure blobs) and is where the reproduction recipe usually lives.
  - `replication_target/arxiv-source.tar.gz` — the raw source archive
    (gitignored; the extracted `source/` is what's committed).
  - `replication_target/paper.pdf` — the PDF, as a fallback / complete record
    (gitignored, same downloader). The paper does NOT go in `data_lake/`.
  - the authors' code, if any, cloned as a **git submodule** in here
    (`git submodule add <repo> replication_target/<name>`).
- **`replication_skill.md`** (repo root) — if the source/paper ships a
  reproduction recipe, copy it here and run it first. **`replication/`** — if a
  replication zip is shipped/linked, extract it here (the zip is gitignored,
  its contents committed).
- **`data_lake/`** — other downloaded/supplied material (datasets, notes,
  exports). Same cleanvibe convention as every project. The paper is NOT here.
- **`src/`** — your reimplementation (only the gaps the recipe didn't cover).
  **`scripts/run.py`** — the entry point CI invokes. **`results/`** — metrics
  JSON (gitignored). **`FINDINGS.md`** — the report (reproduced vs. reported,
  what the recipe covered vs. what you filled, gaps, divergences).
- **Go live early.** Create a PUBLIC GitHub repo and push near the start so
  every commit pushes and CI/Pages build as you go — don't leave it local-only.
- **Deliverables are built by GitHub Actions, not committed.**
  `.github/workflows/pages.yml` publishes a **themed** GitHub Pages findings
  site (the shared `report-theme.css` cleanvibe report theme + a color-coded
  replication status badge driven by `paper.json` `status`) + PDF report;
  `.github/workflows/package.yml` builds the downloadable ZIP replication
  package. Just make the repo **public** — `pages.yml` **auto-enables Pages**
  itself (`actions/configure-pages` with `enablement: true`), so there is no
  manual Settings toggle to do.
  Vision for the site shape: http://latent-space.emmaleonhart.com/

## Workflow Rules

- **Commit early and often.** Every meaningful change gets a descriptive commit.
- **Plan into `queue.md` first, then execute.** The replication plan already
  lives in `queue.md` (derived from `SKILL.md`). Work it top to bottom.
- **Finishing a queue item = delete from `queue.md` + append dated entry to
  `devlog.md`**, in the same commit as the work, then push. Never tick
  boxes in place. `devlog.md` is also where you record the replication's
  releases/milestones (source acquired, recipe found/run, environment pinned,
  first reproduced number, FINDINGS published, Pages live).
- **Keep `SKILL.md` truthful.** It is the compounding artifact. If you
  deviated from its plan, edit the plan to match what you actually did.
- **Keep this file and `README.md` current** as the replication takes shape.

## Writing

- Do not use "honest", "honesty", or "honestly" — and do not swap in "frank", "frankly", "candid", "candidly", or "transparently", which are the same self-congratulatory move in a different coat. When something failed, name the failure: "it didn't work", "I got that wrong", "this failed" — flat, no qualifier. Tagging a report "honest" implies the rest aren't, and couching a failure as honesty asks for credit for the admission, which is worse than the failure itself. Use a precise positive word ("accurate", "plainly", "truly") only when that is genuinely the meaning — never as a halo on a bad outcome.
"""
)


_REPLICATION_QUEUE_TMPL = Template(
    """# replicating-$slug - Work Queue

**This file is a queue of concrete, executable steps, not a state snapshot.**
Finished work lives in `devlog.md` (dated entries) and `git log`;
longer-horizon items live in `todo.md`. **When an item is done, delete it
from this file AND append a dated entry to `devlog.md` in the same commit,
then push.** No checkmarks, no status indicators in place.

**Why this file exists:** the replication plan is written here BEFORE
execution so an interrupted session resumes from the queue, not from chat.
The canonical methodology is `SKILL.md`; this queue is its executable form.

---

## Active — Replicate "$title" (arXiv:$arxiv_id)

The scaffold already made commit 1 (the framework) AND commit 2 (the extracted
arXiv source). The efficient path is: read the source, **find and run the
authors' reproduction recipe FIRST**, then verify its output against the paper
and fill only the gaps. From-scratch reimplementation is the fallback, not the
default. Work top to bottom; delete each item in the same commit that completes
it (and append to `devlog.md`).

1. **STOP — get explicit user consent before running ANY external/cloned code.**
   This is the first thing you do, before anything else. Replicating this paper
   means executing code you did not write: the authors' reproduction recipe /
   replication scripts, a cloned repo, a downloaded zip. Per harness safety
   requirements, **ask the user for explicit consent to run such code and wait
   for their answer before executing any of it.** Reading the paper, the
   `source/`, and the recipe text is fine — *running* third-party code is the
   gated action. (Downloading the arXiv source and extracting the tarball is
   plain data handling, already done by the scaffolder, and is not gated.) An
   automated security scan of the code before running is a future enhancement
   (see `todo.md`); for now, only proceed if the user trusts the source.

2. **Read the already-extracted source.** The scaffolder downloaded the arXiv
   **e-print source** ($src_url) and committed it to `replication_target/source/`
   (commit 2) — far cheaper to read than the rendered HTML, which embeds figures
   as huge base64 blobs. Read the paper straight from the `.tex` in `source/` —
   no HTML→markdown step. (If `source/` is empty — e.g. the scaffold ran offline,
   or the paper is PDF-only — run `python download_paper.py` now and commit it;
   that is a plain download, not third-party code, so it is not gated.)

3. **Create the GitHub repo and push — now, not at the end.** Create a PUBLIC
   repo and push: `gh repo create --public --source=. --push` (public is
   required for free GitHub Pages). From here on every commit pushes, so CI and
   Pages build as you go. (This is the step the v1.4.0 flow missed — the
   replication ran entirely locally and never went live.)

4. **Before any deep analysis: find the reproduction recipe in the source.**
   This is the highest-leverage step and it comes before reading the whole
   paper. Authors very often ship a recipe right in the e-print source —
   usually near the end of the paper: a `SKILL.md` / `AGENTS.md`, a
   `reproduce.*` / `replicate.*` / `run.sh` script, a `Makefile` reproduce
   target, a Dockerfile, or a **replication zip** referenced in the text.
   `download_paper.py` prints candidate files; also grep the `.tex` in `source/`
   for "reproduc", "replicat", "skill", "github.com", and asset/zip URLs.
   - Found a **skill/recipe file** → copy it to the repo root as
     `replication_skill.md` and commit.
   - Found a **replication zip** (in the source or linked in the paper) →
     download/extract it into `replication/` (add the zip to `.gitignore`,
     commit the extracted contents).
   - Found the **authors' code repo** → add it as a git submodule under
     `replication_target/` and record the decision in `notes/sources.md`.
   - Found nothing → note that in `notes/sources.md`; the rest of the queue is
     your from-scratch path.

5. **If a recipe exists, RUN IT FIRST and let it drive the rest.** (Only after
   the user's consent from step 1.) Set up just enough environment to execute
   it, run it, and capture its output into
   `results/`. Then read the paper and assess **how much of the headline claims
   the recipe's output actually reproduces** — which numbers/figures it covers
   and which it doesn't. Record this in `notes/sources.md`. With a working
   recipe, most of what follows is *verifying its output against the paper*, not
   reimplementing from scratch. Commit.

6. **Check ALL references — always, recipe or not.** Walk the bibliography and
   confirm the key cited results / datasets / baselines the paper leans on
   actually say what the paper claims. This runs in every replication. Record
   anything load-bearing or surprising in `notes/claims.md`. Commit.

7. **Record `notes/claims.md`** — scoped to whatever the recipe did NOT already
   cover: headline claim(s); datasets (version/hash, where they live);
   models/methods in re-implementable detail; evaluation metrics and the exact
   reported numbers; compute envelope (GPU type, hours, memory — decides if CI
   can auto-run it). If the recipe covered everything, this is a short
   confirmation. Commit.

8. **Reimplement only the uncovered claims** under `src/` (skip anything the
   recipe already reproduced; scope to the headline claim, not every ablation).
   Pin the environment in `requirements.txt` / `environment.yml` to versions
   that work. Commit as you go.

9. **Run the full replication** via `scripts/run.py` (the CI entry point);
   capture metrics as JSON into `results/`. Commit.

10. **Write `FINDINGS.md`:** reproduced vs. reported numbers (table); what the
    recipe covered vs. what you filled; gaps (hyperparameters, preprocessing,
    omitted architecture details) and where/why it diverged. Commit and push.

11. **Publish and finish.** Set the replication verdict in `paper.json`
    `status` — `replicated` / `failed` / `insufficient-hardware` — so the
    report's big status badge turns green / red / amber (it defaults to
    `in-progress`, blue). Confirm `.github/workflows/pages.yml` (themed site +
    PDF report) and `.github/workflows/package.yml` (ZIP) run green; set
    Settings → Pages → Source: GitHub Actions. Keep `SKILL.md` (and
    `replication_skill.md`, if you found one) truthful to what you actually did.
    **Stop / hand back** when `FINDINGS.md` reports at least one headline number
    with its reproduced value, `scripts/run.py` runs end-to-end from a clean
    clone (or documents the un-automatable data step), the repo is public and
    pushed, and the Pages deployment is green.

---

## Pointers

- Methodology / definition of done: `SKILL.md`.
- Long-horizon items: `todo.md`.
- Completed work + replication milestones (chronological): `devlog.md`.
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

If `replication_target/source/` is empty, run `python download_paper.py`
first. It fetches the arXiv **LaTeX/e-print source** ($src_url), extracts it to
`replication_target/source/`, and saves the PDF as a fallback. Read the `.tex`
in `source/` directly — it is far more token-efficient than the rendered HTML
(no base64 figure blobs) and is where the authors' reproduction recipe usually
lives. Fall back to the PDF only for PDF-only submissions.

## Plan

The efficient path: get the source, **find the authors' reproduction recipe
FIRST**, run it, then verify its output against the paper and fill only the
gaps. Reimplementing from scratch is the fallback, not the default.

> **Consent gate (do this before running anything):** replication runs code you
> did not write (the recipe / cloned scripts / a downloaded zip). Per harness
> safety requirements, ask the user for explicit consent before executing ANY
> such code, and wait for their answer. Reading the paper/source/recipe is fine;
> *running* third-party code is gated. (A future automated security scan is in
> `todo.md`.)

1. **Acquire the LaTeX source.** The scaffolder already downloaded + extracted
   the e-print source to `replication_target/source/` (committed) and saved the
   PDF (gitignored) — read the `.tex` directly. (If `source/` is empty, run
   `python download_paper.py`; that is a plain download, not gated.)

2. **Go live early.** Create a PUBLIC GitHub repo and push
   (`gh repo create --public --source=. --push`) so every later commit pushes
   and Pages/CI build as you go — don't leave it local-only.

3. **Find the reproduction recipe in the source — before reading the whole
   paper.** Authors often ship one near the end of the paper: a `SKILL.md` /
   `AGENTS.md`, a `reproduce.*` / `replicate.*` / `run.sh` script, a `Makefile`
   target, a Dockerfile, or a **replication zip**. `download_paper.py` flags
   candidates; also grep the `.tex` for "reproduc"/"replicat"/"skill"/
   "github.com". Copy a recipe file to `replication_skill.md`; extract a
   replication zip into `replication/`; add the authors' code repo as a **git
   submodule** under `replication_target/`. Record findings in
   `notes/sources.md`.

4. **Run the recipe first** (if any): set up just enough to execute it, capture
   output to `results/`, and assess how much of the paper's headline claims it
   reproduces. With a working recipe the rest is verification, not from-scratch
   reimplementation.

5. **Check ALL references** — every run, recipe or not. Confirm the key cited
   results/datasets/baselines the paper relies on say what it claims.

6. **Record `notes/claims.md`** — scoped to what the recipe didn't cover:
   headline claim(s); datasets (version/hash, location); models/methods in
   re-implementable detail; metrics and exact reported numbers; compute envelope
   (decides if CI can auto-run this).

7. **Reimplement only the gaps** under `src/`; pin `requirements.txt` /
   `environment.yml`. Scope to the headline claim, not every ablation.

8. **Run the replication.** `scripts/run.py` so CI can invoke it; metrics →
   `results/`.

9. **Write the findings.** `FINDINGS.md`: reproduced vs. reported (table);
   what the recipe covered vs. what you filled; gaps and divergences.

10. **Publish.** GitHub Pages deploys the findings + a transportable PDF report
    (`.github/workflows/pages.yml`); a ZIP replication package is built
    (`.github/workflows/package.yml`). The repo must be public with Pages set to
    Source: GitHub Actions.

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
- The repo is public and pushed; the GitHub Pages site and the ZIP package
  build green in Actions.
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
the concrete step queue is in [`queue.md`](./queue.md). The efficient path is
**recipe-first**: get the LaTeX source, find and run the authors' reproduction
recipe (often shipped right in the paper), then verify it against the paper and
fill only the gaps.

## What this repo produces

Three compounding artifacts:

1. **The replication** — runnable code under `src/` + `scripts/run.py`.
2. **The legibility layer** — `FINDINGS.md`, published as a GitHub Pages
   site with a transportable PDF report (built by GitHub Actions).
3. **`SKILL.md`** — a reusable, agent-executable replication methodology.

## Layout

- `replication_target/` — the paper and everything pulled about it:
  - `source/` — extracted arXiv LaTeX/e-print source (committed; the primary,
    token-efficient text — read the `.tex` directly). Fetched by
    `python download_paper.py`; the raw archive is gitignored.
  - `paper.pdf` — downloaded PDF (gitignored; fallback / complete record).
  - the authors' code, if any, as a git **submodule**.
- `replication_skill.md` — the authors' recipe, if one is shipped (run first).
- `data_lake/` — other downloaded/supplied material (NOT the paper).
- `src/` — your reimplementation. `scripts/run.py` — CI entry point.
- `results/` — metrics JSON (gitignored). `FINDINGS.md` — the report.
- `paper.json` — frozen metadata pulled from the arXiv API.
- `.github/workflows/` — `pages.yml` (site + PDF), `package.yml` (ZIP).

## Deliverables (GitHub Actions)

To publish, **make this repo public** and set **Settings -> Pages -> Source:
GitHub Actions**. Then `pages.yml` deploys the findings site + PDF report and
`package.yml` builds a downloadable ZIP replication package. Site shape
inspiration: http://latent-space.emmaleonhart.com/
"""
)


_REPLICATION_DOWNLOAD_TMPL = Template(
    '''"""Fetch arXiv:$id_with_version into replication_target/.

The **primary** download is the arXiv LaTeX / e-print **source**
(arxiv.org/src/...). It is far more token-efficient to read than the rendered
HTML (which embeds figures as huge base64 data-URIs you would otherwise have to
strip) and the .tex files read cleanly. It is also where authors most often
ship a reproduction recipe -- a SKILL.md / AGENTS.md, a reproduce/replicate/
run.sh script, a Makefile target, a Dockerfile, or a link to a replication zip
-- usually near the end of the paper.

This script downloads the source archive, extracts it to
``replication_target/source/`` (committed), saves the PDF as a fallback /
complete record (gitignored), and prints any files that look like a
reproduction recipe so the agent can find and run it FIRST.

arXiv submissions come in a few shapes; all are handled:
  * a gzip-compressed tar (the common case: many files)  -> extracted
  * a single gzip-compressed .tex (single-file paper)    -> source/main.tex
  * a PDF-only submission (no source available)          -> paper.pdf

arXiv rate-limits (HTTP 429/503), so requests retry with backoff that honours
the Retry-After header. Stdlib only.
"""

from __future__ import annotations

import gzip
import io
import socket
import sys
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path

SRC_URL = "$src_url"
PDF_URL = "$pdf_url"
HTML_URL = "$html_url"
ARXIV_ID = "$arxiv_id"

_TARGET = Path(__file__).parent / "replication_target"
_SOURCE = _TARGET / "source"
_MAX_RETRIES = 4
_BASE_BACKOFF = 3.0  # arXiv asks for ~3s between requests
# Socket read timeouts come up as plain TimeoutError (3.10+) or socket.timeout
# (3.9) and are NOT a subclass of urllib.error.URLError, so they need their
# own except-clause to participate in the retry loop.
_TIMEOUT_ERRORS = (TimeoutError, socket.timeout)

# Filenames that suggest a ready-made reproduction recipe / replication asset.
_RECIPE_HINTS = (
    "skill", "agents", "reproduc", "replicat", "run.sh", "makefile",
    "dockerfile", ".zip",
)


def _retry_after(err):
    val = err.headers.get("Retry-After") if err.headers else None
    try:
        return max(0.0, float(val)) if val else None
    except ValueError:
        return None


def _get(url):
    """GET url with retry/backoff for arXiv rate limiting; return bytes."""
    backoff = _BASE_BACKOFF
    for attempt in range(_MAX_RETRIES):
        last = attempt == _MAX_RETRIES - 1
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "cleanvibe-replicate"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and not last:
                wait = _retry_after(e) or backoff
                print(f"  rate-limited (HTTP {e.code}); retrying in {wait:.0f}s")
                time.sleep(wait)
                backoff *= 2
                continue
            raise
        except (urllib.error.URLError, *_TIMEOUT_ERRORS) as e:
            if last:
                raise
            print(f"  transient error ({e!r}); retrying in {backoff:.0f}s")
            time.sleep(backoff)
            backoff *= 2
    raise AssertionError("unreachable")


def _safe_extract(tar, dest):
    """Extract ``tar`` into ``dest``, refusing any member that escapes it."""
    dest = dest.resolve()
    members = tar.getmembers()
    for m in members:
        target = (dest / m.name).resolve()
        if dest != target and dest not in target.parents:
            raise RuntimeError(f"unsafe path in archive: {m.name!r}")
    try:
        # Python 3.12+ : the hardened 'data' filter (also silences the 3.14
        # deprecation warning). Older Pythons don't accept the kwarg.
        tar.extractall(dest, filter="data")
    except TypeError:
        tar.extractall(dest)
    return members


def _extract_source(data):
    """Turn raw /src bytes into files under source/. Returns list of rel paths.

    Handles the three arXiv source shapes (gzip-tar, single gzip-tex, PDF-only).
    """
    # PDF-only submission: no source to extract; let the PDF fetch cover it.
    if data[:5] == b"%PDF-":
        print("  source is a PDF-only submission; no .tex source available")
        return []

    _SOURCE.mkdir(parents=True, exist_ok=True)

    # Most submissions: a (gz/bz2/xz) tar of the project.
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tar:
            members = _safe_extract(tar, _SOURCE)
        names = [m.name for m in members if m.isfile()]
        print(f"  extracted {len(names)} file(s) to {_SOURCE}")
        return names
    except tarfile.ReadError:
        pass

    # Single-file submission: gzip of one .tex (no tar wrapper).
    try:
        tex = gzip.decompress(data)
        out = _SOURCE / "main.tex"
        out.write_bytes(tex)
        print(f"  single-file source -> {out}")
        return ["main.tex"]
    except (OSError, EOFError):
        pass

    # Unknown container: save the raw archive so nothing is lost.
    raw = _TARGET / "arxiv-source.bin"
    raw.write_bytes(data)
    print(f"  could not recognise source container; saved raw -> {raw}")
    return []


def _flag_recipes(names):
    """Print source files whose names hint at a reproduction recipe."""
    hits = [n for n in names if any(h in n.lower() for h in _RECIPE_HINTS)]
    if hits:
        print("\\n  *** candidate reproduction recipe(s) in the source — "
              "look at these FIRST: ***")
        for n in hits:
            print(f"      {n}")
    else:
        print("\\n  no obvious recipe filenames in the source; grep the .tex "
              "for 'reproduc'/'replicat'/'github.com' and check the paper's end")


def _save_binary(url, out, *, optional=False):
    if out.exists() and out.stat().st_size > 0:
        print(f"already present: {out}")
        return True
    print(f"downloading {url} -> {out}")
    try:
        data = _get(url)
    except urllib.error.HTTPError as e:
        if optional:
            print(f"  skipped (HTTP {e.code})")
            return False
        raise
    out.write_bytes(data)
    print(f"  wrote {out.stat().st_size} bytes")
    return data


def main() -> int:
    _TARGET.mkdir(parents=True, exist_ok=True)

    # 1) The LaTeX/e-print source — primary, token-efficient, recipe-bearing.
    if _SOURCE.exists() and any(_SOURCE.iterdir()):
        print(f"source already extracted: {_SOURCE}")
    else:
        print(f"downloading source {SRC_URL}")
        try:
            data = _get(SRC_URL)
            # Keep the raw archive too (gitignored) for provenance.
            (_TARGET / "arxiv-source.tar.gz").write_bytes(data)
            names = _extract_source(data)
            _flag_recipes(names)
        except urllib.error.HTTPError as e:
            print(f"  source unavailable (HTTP {e.code}); relying on the PDF")

    # 2) The PDF — fallback / complete visual record.
    _save_binary(PDF_URL, _TARGET / "paper.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
)


REPLICATION_GITIGNORE = """# The paper itself — downloaded, never committed
replication_target/*.pdf
replication_target/*.html
# The raw arXiv source archive is gitignored; the EXTRACTED
# replication_target/source/ tree IS committed (that is the readable paper text).
replication_target/*.tar.gz
replication_target/*.tar
replication_target/*.tgz
replication_target/arxiv-source.*
# A downloaded replication zip is ignored; its extracted replication/ contents
# are committed.
replication/*.zip
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
# Pages is auto-enabled by the `actions/configure-pages` step below
# (enablement: true), so there is NO manual "Settings -> Pages" toggle to do —
# the only requirement is that the repo is PUBLIC. The first push that runs this
# workflow turns Pages on and deploys.

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
      - name: Configure Pages (auto-enables Pages if not already on)
        uses: actions/configure-pages@v5
        with:
          enablement: true
      - name: Install pandoc
        run: sudo apt-get update && sudo apt-get install -y pandoc
      - name: Build themed findings site + PDF report
        run: |
          mkdir -p site
          # Findings source (falls back to README if FINDINGS.md not written yet)
          SRC=FINDINGS.md
          [ -f "$SRC" ] || SRC=README.md

          # Replication verdict, from paper.json `status` (default in-progress).
          STATUS=in-progress
          if [ -f paper.json ]; then
            STATUS=$(jq -r '.status // "in-progress"' paper.json 2>/dev/null || echo in-progress)
          fi
          case "$STATUS" in
            replicated)            LABEL="Replicated"; CLASS="replicated";;
            failed)                LABEL="Failed to replicate"; CLASS="failed";;
            insufficient-hardware) LABEL="Insufficient hardware to replicate"; CLASS="insufficient";;
            *)                     LABEL="In progress"; CLASS="in-progress";;
          esac

          # Render the findings body (fragment), then wrap it in the shared
          # cleanvibe report theme + the color-coded status badge.
          pandoc "$SRC" -o body.html
          {
            echo '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
            echo '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            echo '<title>Replication report</title><style>'
            [ -f report-theme.css ] && cat report-theme.css
            echo '</style></head><body>'
            echo "<div class=\\"status-badge $CLASS\\">$LABEL</div>"
            cat body.html
            echo '</body></html>'
          } > site/index.html

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


# ---------------------------------------------------------------------------
# Manual / drop-in replication templates (`cleanvibe replicate <folder>`)
#
# When the argument to `cleanvibe replicate` is NOT an arXiv/alphaxiv
# reference, it is treated as a folder name and we scaffold a replication
# project with NO arXiv fetch: no `download_paper.py`, no `paper.json`, no
# network. The user drops the paper PDF(s) into `replication_target/` and any
# supporting material into `data_lake/` by hand. The scaffold's opening
# instructions say this up front. Same downstream structure as the arXiv
# flow (SKILL.md / FINDINGS.md / GitHub Actions deliverables), so the gitignore
# and workflow constants above are reused as-is.
# ---------------------------------------------------------------------------


def _manual_name(folder: str) -> str:
    """Display name for a manual replication project from its folder path."""
    name = folder.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]
    return name or "replication"


def replication_manual_claude_md(folder: str, source_url: str | None = None) -> str:
    name = _manual_name(folder)
    if source_url:
        subtitle = "downloaded source"
        intro_para = (
            "from a **non-arXiv source URL**. The paper was downloaded into\n"
            "`replication_target/source/` at scaffold time (it is not on arXiv\n"
            "or clawRxiv) — see `source.json` for the URL and the saved filename."
        )
        paper_block = (
            "> **The paper source is already here.**\n"
            f"> `cleanvibe replicate` downloaded it from {source_url} into\n"
            "> `replication_target/source/` (committed) and recorded the URL in\n"
            "> `source.json`. You do NOT need to fetch it. Put any extra material\n"
            "> (datasets, the PDF, notes) into `data_lake/`."
        )
        no_meta_bullet = (
            "- **No `download_paper.py`, no arXiv `paper.json`.** The source was\n"
            "  fetched directly from a URL at scaffold time (`source.json` records\n"
            "  it). The agent derives the paper's identity by *reading the\n"
            "  downloaded source* and records it in `notes/claims.md` / `README.md`."
        )
    else:
        subtitle = "manual drop-in"
        intro_para = (
            "in **manual drop-in mode**. Nothing was fetched from arXiv — **you "
            "supply the\npaper(s) and materials by hand.**"
        )
        paper_block = (
            "> **The paper has to be here before anything useful can happen.**\n"
            "> Put the paper PDF(s) into `replication_target/` (name the primary one\n"
            "> `paper.pdf`). Put datasets, supplementary files, author-code exports,\n"
            "> notes, and screenshots into `data_lake/`. If `replication_target/` has no\n"
            "> PDF yet, the first `queue.md` item is to **stop and ask you for it** — the\n"
            "> agent must not invent a paper."
        )
        no_meta_bullet = (
            "- **No `download_paper.py`, no `paper.json`.** This mode has no arXiv\n"
            "  metadata. The agent derives the paper's identity by *reading what you\n"
            "  dropped in* and records it in `notes/claims.md` and `README.md`."
        )
    return f"""# {name} — paper replication ({subtitle})

## Project Description

This is a **paper-replication project** scaffolded by `cleanvibe replicate`
{intro_para}

{paper_block}

The goal is the same as any cleanvibe replication: reproduce the paper's
headline result(s) and produce three compounding artifacts — the runnable
replication, a published findings report, and `SKILL.md` (the reusable,
agent-executable replication methodology). See `docs/replication_framing.md`
in the cleanvibe repo for the full framing.

## Architecture and Conventions

- **The efficient path is recipe-first.** Authors very often ship a
  reproduction recipe in their code repo (a `SKILL.md`/`AGENTS.md`, a
  reproduce/replicate/run.sh script, a Makefile target, a Dockerfile, or a
  replication zip). Find and run it FIRST, then verify its output against the
  paper and fill only the gaps. A from-scratch reimplementation is the
  fallback, not the default.
- **`replication_target/`** holds the paper and everything pulled *about* it:
  - the paper PDF(s) you dropped in — **gitignored**: papers are often
    copyrighted and are your local input, not committed. Convention:
    `replication_target/paper.pdf` for the primary paper.
  - `replication_target/paper.md` — a Markdown extraction of the paper's
    text, made during the replication, so later steps work from structured
    text rather than raw PDF.
  - the authors' code, if any, cloned as a **git submodule** in here
    (`git submodule add <repo> replication_target/<name>`).
- **`replication_skill.md`** (repo root) — the authors' recipe, if one is
  shipped (run first). **`replication/`** — an extracted replication zip (zip
  gitignored, contents committed).
- **`data_lake/`** — other supplied/downloaded material (datasets, notes,
  exports). Standard cleanvibe convention; this *is* committed. The paper is
  NOT here.
{no_meta_bullet}
- **Go live early.** Create a PUBLIC GitHub repo and push near the start so
  every commit pushes and CI/Pages build as you go — don't leave it local-only.
- **`src/`** — your reimplementation. **`scripts/run.py`** — the entry point
  CI invokes. **`results/`** — metrics JSON (gitignored). **`FINDINGS.md`** —
  the report (reproduced vs. reported, gaps, divergences).
- **Deliverables are built by GitHub Actions, not committed.**
  `.github/workflows/pages.yml` publishes a **themed** GitHub Pages findings
  site (the shared `report-theme.css` cleanvibe report theme + a color-coded
  replication status badge driven by `paper.json` `status`) + PDF report;
  `.github/workflows/package.yml` builds the downloadable ZIP replication
  package. Make the repo public and set Settings -> Pages -> Source: GitHub
  Actions. Vision for the site shape: http://latent-space.emmaleonhart.com/

## Workflow Rules

- **Commit early and often.** Every meaningful change gets a descriptive commit.
- **Plan into `queue.md` first, then execute.** The replication plan already
  lives in `queue.md`. Work it top to bottom.
- **Finishing a queue item = delete from `queue.md` + append dated entry to
  `devlog.md`**, in the same commit as the work, then push. Never tick boxes
  in place. `devlog.md` is also where you record the replication's
  releases/milestones (paper identified, environment pinned, first reproduced
  number, FINDINGS published, Pages live).
- **Keep `SKILL.md` truthful.** It is the compounding artifact. If you
  deviated from its plan, edit the plan to match what you actually did.
- **Keep this file and `README.md` current** as the replication takes shape.

## Writing

- Do not use "honest", "honesty", or "honestly" — and do not swap in "frank", "frankly", "candid", "candidly", or "transparently", which are the same self-congratulatory move in a different coat. When something failed, name the failure: "it didn't work", "I got that wrong", "this failed" — flat, no qualifier. Tagging a report "honest" implies the rest aren't, and couching a failure as honesty asks for credit for the admission, which is worse than the failure itself. Use a precise positive word ("accurate", "plainly", "truly") only when that is genuinely the meaning — never as a halo on a bad outcome.
"""


def replication_manual_queue_md(folder: str, source_url: str | None = None) -> str:
    name = _manual_name(folder)
    if source_url:
        preamble = (
            "The paper source was **downloaded from a URL** to "
            "`replication_target/source/`\n(see `source.json`). Supporting "
            "material can be added to `data_lake/`."
        )
        step1 = (
            "1. **Confirm the downloaded source is present, and triage materials.**\n"
            "   The paper source was downloaded from a URL to\n"
            "   `replication_target/source/` (see `source.json`) — you do NOT fetch it.\n"
            "   - Verify `replication_target/source/` holds the downloaded paper\n"
            "     (`paper.html` or `paper.pdf`). If it is empty, the download failed —\n"
            "     STOP and tell the user the URL fetch did not succeed.\n"
            "   - Move any datasets / supplementary / notes the user dropped in into\n"
            "     `data_lake/`.\n"
            "   - Commit. (`data_lake/` material is committed per the cleanvibe convention.)"
        )
    else:
        preamble = (
            "This is **manual drop-in mode** — no paper was downloaded. The paper "
            "PDF(s)\nand supporting material are supplied by the user."
        )
        step1 = (
            "1. **Confirm the paper and materials are present, and triage them.**\n"
            "   Nothing was downloaded — this is manual drop-in mode.\n"
            "   - Look in `replication_target/` for the paper PDF(s), and in the repo\n"
            "     root / `data_lake/` for anything else the user dropped in.\n"
            "   - If the user left the paper at the repo root, move it into\n"
            "     `replication_target/` (name the primary paper `paper.pdf`).\n"
            "   - Move datasets / supplementary / exports / notes into `data_lake/`.\n"
            "   - **If `replication_target/` has no PDF, STOP and ask the user to drop\n"
            "     the paper in before continuing. Do not invent or fetch a paper.**\n"
            "   - Commit. (The dropped paper stays gitignored; `data_lake/` material is\n"
            "     committed per the cleanvibe convention.)"
        )
    return f"""# {name} — Work Queue

**This file is a queue of concrete, executable steps, not a state snapshot.**
Finished work lives in `devlog.md` (dated entries) and `git log`;
longer-horizon items live in `todo.md`. **When an item is done, delete it
from this file AND append a dated entry to `devlog.md` in the same commit,
then push.** No checkmarks, no status indicators in place.

**Why this file exists:** the replication plan is written here BEFORE
execution so an interrupted session resumes from the queue, not from chat.
The canonical methodology is `SKILL.md`; this queue is its executable form.

{preamble}

---

## Active — Manual paper replication

The efficient path is **recipe-first**: identify the paper, find and run the
authors' reproduction recipe (often shipped in their code repo), then verify it
against the paper and fill only the gaps. Reimplementing from scratch is the
fallback. Work top to bottom; delete each item in the same commit that
completes it (and append to `devlog.md`).

> **Consent gate — read before step 4.** This replication will run code you did
> not write (the authors' reproduction recipe / replication scripts / cloned
> repo). Per harness safety requirements, **before executing ANY such code
> (step 4 onward), ask the user for explicit consent and wait for their
> answer.** Reading the paper and the recipe text is fine; *running*
> third-party code is the gated action. An automated security scan of the code
> before running is a future enhancement (see `todo.md`); for now, only proceed
> if the user trusts the source.

{step1}

2. **Identify the paper and go live early.** From the dropped PDF(s) determine
   the title, authors, venue/year, and any arXiv id / DOI; write that into
   `README.md` (replacing the "unknown" placeholders). Save a Markdown
   extraction of the paper to `replication_target/paper.md`. Then create a
   PUBLIC GitHub repo and push (`gh repo create --public --source=. --push`) so
   every later commit pushes and Pages/CI build as you go. Commit.

3. **FIRST, before deep analysis: find the authors' code and an existing
   replication recipe — and follow it first.** This is the highest-leverage
   step. Search the paper, paperswithcode, and GitHub (title + first author).
   Look for a ready-made path the authors (or others) shipped — many recent
   papers have one: a `REPRODUCE*.md` / `reproduce.*` / `replicate.*` /
   `run.sh` script, a `Makefile` reproduce target, a Dockerfile, a Colab
   notebook, a "Reproducing the results" README section, or an **agent recipe**
   (`SKILL.md`, `AGENTS.md`, `.claude/`, `.cursor/`); also check paperswithcode
   and release assets.
   - Found the authors' code → add it as a git submodule under
     `replication_target/` and record the decision in `notes/sources.md`
     (fork-and-verify vs. independent reimplementation).
   - Found a **skill/recipe file** → copy it to the repo root as
     `replication_skill.md`.
   - Found a **replication zip** → extract it into `replication/` (the zip
     gitignored, contents committed).
   Commit what you found either way.

4. **If a recipe exists, RUN IT FIRST.** (Only after the user's consent — see
   the consent gate above.) Set up just enough environment to execute it, run
   it, capture output to `results/`, and assess how much of the paper's headline
   claims it reproduces. With a working recipe the rest is verification, not
   from-scratch reimplementation. Commit.

5. **Check ALL references — always, recipe or not.** Walk the bibliography and
   confirm the key cited results / datasets / baselines the paper relies on say
   what it claims. Record anything load-bearing in `notes/claims.md`. Commit.

6. **Record `notes/claims.md`** — scoped to what the recipe didn't cover:
   the headline claim(s); datasets (version/hash, where they live);
   models/methods in enough detail to re-implement; evaluation metrics and the
   exact reported numbers; the compute envelope (used to decide if CI can
   auto-run it). Commit.

7. **Reimplement only the uncovered claims** under `src/` — scope to the
   headline claim, not every ablation. Pin `requirements.txt` /
   `environment.yml` to versions that work. Commit as you go.

8. **Run the replication.** Script it as `scripts/run.py` so CI can invoke
   it; capture metrics as JSON into `results/`. Commit.

9. **Write `FINDINGS.md`:** reproduced vs. reported numbers (table); what the
   recipe covered vs. what you filled; gaps (hyperparameters, preprocessing,
   omitted architecture details) and where/why it diverged. Commit and push.

10. **Publish and finish.** Record the replication verdict so the report's big
    status badge is right: write a `paper.json` with a `status` field —
    `replicated` / `failed` / `insufficient-hardware` (it defaults to
    `in-progress`, blue, when absent). Confirm `.github/workflows/pages.yml`
    (themed site + PDF) and `.github/workflows/package.yml` (ZIP) run green; set
    Settings → Pages → Source: GitHub Actions. Keep `SKILL.md` (and
    `replication_skill.md`, if found) truthful. **Stop / hand back** when
    `FINDINGS.md` reports at least one headline number with its reproduced
    value, `scripts/run.py` runs end-to-end from a clean clone (or documents the
    un-automatable data step), the repo is public and pushed, and the Pages
    deployment is green.

---

## Pointers

- Methodology / definition of done: `SKILL.md`.
- Long-horizon items: `todo.md`.
- Completed work + replication milestones (chronological): `devlog.md`.
- Narrative history: `git log`.
"""


def replication_manual_skill_md(folder: str, source_url: str | None = None) -> str:
    name = _manual_name(folder)
    slug = _slugify(name)
    if source_url:
        title_suffix = "downloaded source"
        header_note = (
            "No arXiv metadata — the paper source was **downloaded from a URL**\n"
            "into `replication_target/source/` (see `source.json`). Identify the\n"
            "paper by reading the downloaded source."
        )
        prereq = (
            "The paper source is already in `replication_target/source/`\n"
            "(downloaded from a URL). If it is empty the download failed — tell the\n"
            "user. Prefer working from the downloaded source text."
        )
    else:
        title_suffix = "manual drop-in"
        header_note = (
            "No arXiv metadata — the paper(s) are supplied by hand in\n"
            "`replication_target/`. Identify the paper by reading what was dropped in."
        )
        prereq = (
            "If `replication_target/` has no PDF, **stop and ask the user to drop the\n"
            "paper in**. Do not fetch or invent a paper. Once present, prefer working\n"
            "from `replication_target/paper.md` (a Markdown extraction) when available."
        )
    return f"""---
name: replicate-{slug}
description: Replicate a user-supplied paper (dropped into replication_target/) and produce a runnable artifact, a published findings report, and a downloadable replication package.
---

# Replicate ({title_suffix}): {name}

{header_note}

## Prerequisite

{prereq}

## Plan

The efficient path: identify the paper, **find and run the authors'
reproduction recipe FIRST**, then verify it against the paper and fill only the
gaps. Reimplementing from scratch is the fallback.

1. **Triage the drop-in.** Move the paper PDF(s) into
   `replication_target/` (primary -> `paper.pdf`) and any datasets /
   supplementary / notes into `data_lake/`.

2. **Identify the paper + go live early.** Record title/authors/venue/year
   (and arXiv id / DOI if present) in `README.md`; extract the paper text to
   `replication_target/paper.md`. Create a PUBLIC GitHub repo and push
   (`gh repo create --public --source=. --push`) so commits push and Pages/CI
   build as you go.

3. **Find the authors' code and an existing replication recipe — before deep
   analysis.** paperswithcode, GitHub (title + first author). Look for a
   ready-made path: a `REPRODUCE*.md` / `reproduce.*` / `replicate.*` /
   `run.sh` script, a `Makefile` reproduce target, a Dockerfile, a Colab
   notebook, a "Reproducing the results" README section, or an **agent recipe**
   (`SKILL.md`, `AGENTS.md`, `.claude/`, `.cursor/`); also check paperswithcode
   and release assets. Add the authors' code as a **git submodule** under
   `replication_target/`; copy a recipe file to `replication_skill.md`; extract
   a replication zip into `replication/`. Record findings in
   `notes/sources.md`.

4. **Run the recipe first** (if any): execute it, capture output to `results/`,
   and assess how much of the headline claims it reproduces.

5. **Check ALL references** — every run, recipe or not.

6. **Record `notes/claims.md`** — scoped to what the recipe didn't cover:
   headline claim(s); datasets (version/hash, location); models/methods in
   re-implementable detail; evaluation metrics and the exact reported numbers;
   compute envelope.

7. **Reimplement only the gaps** under `src/`; pin `requirements.txt` /
   `environment.yml`. Scope to the headline claim, not every ablation.

8. **Run the replication.** `scripts/run.py` so CI can invoke it. Capture
   metrics as JSON into `results/`.

9. **Write the findings.** `FINDINGS.md`: reproduced vs. reported numbers
   (table); what the recipe covered vs. what you filled; gaps and divergences.

10. **Publish.** GitHub Pages deploys the findings + a transportable PDF
    report (`.github/workflows/pages.yml`); a ZIP replication package is built
    (`.github/workflows/package.yml`). The repo must be public with Pages
    enabled.

## Budget guardrails

- If the paper's reported compute is more than ~4 GPU-hours on a single
  consumer GPU, mark this replication **not CI-runnable** and document the
  reduced-scale variant instead.
- Prefer deterministic seeds and logged hashes so reruns are comparable.

## Definition of done

- `FINDINGS.md` exists and reports at least one headline number from the
  paper, with the reproduced value next to it.
- `scripts/run.py` runs end-to-end from a clean clone (or documents the
  data step that can't be automated).
- The repo is public and pushed; the GitHub Pages site and the ZIP package
  build green in Actions.
- This file still reflects how you actually did it — if you deviated, edit
  the plan above.
"""


def replication_manual_readme_md(folder: str, source_url: str | None = None) -> str:
    name = _manual_name(folder)
    if source_url:
        title = "# Replicating: _(downloaded from a URL — fill this in)_"
        subtitle = (
            "> Scaffolded with [cleanvibe](https://github.com/Immanuelle/cleanvibe)\n"
            f"> `replicate` from a non-arXiv URL ({source_url}). The source was\n"
            "> downloaded into `replication_target/source/` (see `source.json`)."
        )
        paper_line = (
            f"**Paper:** _the source was downloaded from {source_url} into\n"
            "`replication_target/source/`; fill in title / authors / venue / year\n"
            "(and any arXiv id or DOI) after reading it._"
        )
        howto = (
            "1. The paper source is already in `replication_target/source/`.\n"
            "2. Put datasets / supplementary / notes into `data_lake/`.\n"
            "3. Open Claude Code here and work `queue.md` top to bottom."
        )
        nopaper_note = (
            "If `replication_target/source/` is empty, the URL download failed — "
            "the agent will tell you rather than guess."
        )
    else:
        title = "# Replicating: _(paper supplied by hand — fill this in)_"
        subtitle = (
            "> Scaffolded with [cleanvibe](https://github.com/Immanuelle/cleanvibe)\n"
            "> `replicate` in **manual drop-in mode**. No arXiv metadata was fetched."
        )
        paper_line = (
            "**Paper:** _unknown — drop the PDF into `replication_target/`, then fill in\n"
            "title / authors / venue / year (and arXiv id or DOI if it has one) after\n"
            "reading it._"
        )
        howto = (
            "1. Put the paper PDF(s) into `replication_target/` (primary -> `paper.pdf`).\n"
            "2. Put datasets / supplementary / notes into `data_lake/`.\n"
            "3. Open Claude Code here and work `queue.md` top to bottom."
        )
        nopaper_note = (
            "If `replication_target/` has no PDF, the agent will stop and ask you for it\n"
            "rather than guess."
        )
    return f"""{title}

{subtitle}

{paper_line}

## How to start

{howto}

{nopaper_note}

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

- `replication_target/` — the paper and everything about it:
  - the paper PDF(s) you dropped in (gitignored — copyrighted, local input).
  - `paper.md` — Markdown extraction of the paper text (for structured text).
  - the authors' code, if any, as a git **submodule**.
- `data_lake/` — other supplied material (NOT the paper).
- `src/` — your reimplementation. `scripts/run.py` — CI entry point.
- `results/` — metrics JSON (gitignored). `FINDINGS.md` — the report.
- `.github/workflows/` — `pages.yml` (site + PDF), `package.yml` (ZIP).

## Deliverables (GitHub Actions)

To publish, **make this repo public** and set **Settings -> Pages -> Source:
GitHub Actions**. Then `pages.yml` deploys the findings site + PDF report and
`package.yml` builds a downloadable ZIP replication package. Site shape
inspiration: http://latent-space.emmaleonhart.com/
"""


# ---------------------------------------------------------------------------
# clawRxiv replication templates (`cleanvibe replicate <clawrxiv-ref>`)
#
# clawRxiv (clawrxiv.io) publishes papers authored autonomously by AI agents
# and serves them via a JSON API that *differentiates* the paper content, the
# abstract, and a skill file (an agent-runnable replication recipe). The
# scaffolder fetches all three up front: the content is written to
# `replication_target/source/paper.md` (committed) and the skill recipe, when
# clawRxiv ships one separately, to `replication_skill.md` at the root. This is
# the purest recipe-first case, so the queue is **skill-first**: run the recipe
# before any reimplementation. No `download_paper.py` (the API returns
# everything in a single call); the replication gitignore + workflow constants
# above are reused as-is.
# ---------------------------------------------------------------------------


def _clawrxiv_subs(paper: ClawrxivPaper) -> dict:
    if paper.has_skill_file:
        skill_location = (
            "The skill recipe is **already at `replication_skill.md`** "
            "(clawRxiv's `skillMd` field)."
        )
    else:
        skill_location = (
            "clawRxiv shipped no separate skill file for this paper, so the "
            "agent-runnable recipe is **embedded in "
            "`replication_target/source/paper.md`** — extract it into "
            "`replication_skill.md` first, then run it."
        )
    return {
        "title": paper.title,
        "paper_id": paper.paper_id,
        "slug": paper.slug,
        "authors": ", ".join(paper.authors) if paper.authors else "unknown",
        "claw_name": paper.claw_name or "unknown",
        "abstract": paper.abstract or "_(no abstract provided)_",
        "created_at": paper.created_at or "unknown",
        "category": paper.category or "unknown",
        "abs_url": paper.abs_url,
        "api_url": paper.api_url,
        "skill_location": skill_location,
    }


_CLAWRXIV_CLAUDE_TMPL = Template(
    """# replicating-$slug

## Project Description

This is a **paper replication** project (scaffolded by `cleanvibe replicate`
from **clawRxiv**). The goal is to reproduce the headline results of:

> **$title**
> clawrxiv:$paper_id - $authors - $created_at
> Agent author (claw): $claw_name - category: $category
> $abs_url

clawRxiv publishes papers authored autonomously by AI agents and serves each as
three *differentiated* parts — the **content** (body), the **abstract**, and a
**skill file** (an agent-runnable replication recipe). The scaffold already
fetched all three from the API ($api_url).

It produces three compounding artifacts (see `docs/replication_framing.md` in
the cleanvibe repo for the full framing): the runnable replication, a legibility
layer (the published findings report), and `SKILL.md` — the reusable,
agent-executable replication methodology.

## Architecture and Conventions

- **This is the purest recipe-first case — the recipe is already here.**
  $skill_location Run it FIRST, then verify its output against the paper and
  fill only the gaps. A from-scratch reimplementation is the fallback.
- **`replication_target/source/paper.md`** — the clawRxiv paper **content**,
  written at scaffold time (committed; no download step). Read it directly.
- **`replication_skill.md`** (repo root) — the clawRxiv skill recipe, when one
  was shipped separately; otherwise extract it from `paper.md` (see above).
- **`paper.json`** — the frozen clawRxiv metadata (title, authors, claw name,
  version, category, abstract, URLs).
- **`data_lake/`** — other downloaded/supplied material. The paper is NOT here.
- **`src/`** — your reimplementation (only the gaps the recipe didn't cover).
  **`scripts/run.py`** — the entry point CI invokes. **`results/`** — metrics
  JSON (gitignored). **`FINDINGS.md`** — the report (reproduced vs. reported,
  what the recipe covered vs. what you filled, gaps, divergences).
- **Go live early.** Create a PUBLIC GitHub repo and push near the start so
  every commit pushes and CI/Pages build as you go — don't leave it local-only.
- **Deliverables are built by GitHub Actions, not committed.**
  `.github/workflows/pages.yml` publishes a **themed** GitHub Pages findings
  site (the shared `report-theme.css` cleanvibe report theme + a color-coded
  replication status badge driven by `paper.json` `status`) + PDF report;
  `.github/workflows/package.yml` builds the downloadable ZIP replication
  package. Make the repo public and enable Pages (Settings -> Pages -> Source:
  GitHub Actions). Vision for the site shape: http://latent-space.emmaleonhart.com/

## Workflow Rules

- **Commit early and often.** Every meaningful change gets a descriptive commit.
- **Plan into `queue.md` first, then execute.** The replication plan already
  lives in `queue.md` (derived from `SKILL.md`). Work it top to bottom.
- **Finishing a queue item = delete from `queue.md` + append dated entry to
  `devlog.md`**, in the same commit as the work, then push. Never tick boxes in
  place. `devlog.md` is also where you record the replication's
  releases/milestones (skill run, first reproduced number, FINDINGS published,
  Pages live).
- **Keep `SKILL.md` truthful.** It is the compounding artifact. If you deviated
  from its plan, edit the plan to match what you actually did.
- **Keep this file and `README.md` current** as the replication takes shape.

## Writing

- Do not use "honest", "honesty", or "honestly" — and do not swap in "frank", "frankly", "candid", "candidly", or "transparently", which are the same self-congratulatory move in a different coat. When something failed, name the failure: "it didn't work", "I got that wrong", "this failed" — flat, no qualifier. Tagging a report "honest" implies the rest aren't, and couching a failure as honesty asks for credit for the admission, which is worse than the failure itself. Use a precise positive word ("accurate", "plainly", "truly") only when that is genuinely the meaning — never as a halo on a bad outcome.
"""
)


_CLAWRXIV_QUEUE_TMPL = Template(
    """# replicating-$slug - Work Queue

**This file is a queue of concrete, executable steps, not a state snapshot.**
Finished work lives in `devlog.md` (dated entries) and `git log`;
longer-horizon items live in `todo.md`. **When an item is done, delete it
from this file AND append a dated entry to `devlog.md` in the same commit,
then push.** No checkmarks, no status indicators in place.

**Why this file exists:** the replication plan is written here BEFORE
execution so an interrupted session resumes from the queue, not from chat.
The canonical methodology is `SKILL.md`; this queue is its executable form.

This paper comes from **clawRxiv** (papers published autonomously by AI agents).
clawRxiv differentiates the paper **content**, **abstract**, and **skill file**,
and the scaffold already fetched all three: the content is at
`replication_target/source/paper.md` and the skill recipe is handled below. This
is the purest recipe-first case — the recipe is already in the repo.

---

## Active — Replicate "$title" (clawrxiv:$paper_id)

Work top to bottom. Delete each item in the same commit that completes it
(and append to `devlog.md`).

1. **STOP — get explicit user consent before running the skill recipe (or any
   external/cloned code).** This is the first thing you do, before anything
   else. The clawRxiv skill recipe is code you did not write; running it (and
   any cloned scripts it pulls in) is gated. Per harness safety requirements,
   **ask the user for explicit consent to run it and wait for their answer
   before executing anything.** Reading the paper, the recipe text, and the
   `source/` is fine — *running* it is the gated action. An automated security
   scan of the code before running is a future enhancement (see `todo.md`); for
   now, only proceed if the user trusts the source.

2. **Create the GitHub repo and push — PUBLIC, early.** Create a public repo
   and push: `gh repo create --public --source=. --push` (public is required
   for free GitHub Pages). From here on every commit pushes, so CI and Pages
   build as you go.

3. **Run the skill recipe FIRST.** (Only after the user's consent from step 1.)
   $skill_location Set up just enough environment to execute it, run it, and
   capture its output into `results/`. This is the highest-leverage step and it
   comes before any deep analysis — clawRxiv hands you an agent-runnable recipe,
   so use it. Commit.

4. **Verify the skill's output against the paper.** Read
   `replication_target/source/paper.md` and assess **how much of the paper's
   headline claims the recipe actually reproduces** — which results it covers
   and which it doesn't. Record this in `notes/sources.md`. Commit.

5. **Check ALL references — always.** Walk the paper's references and confirm
   the key cited results / datasets / baselines say what the paper claims.
   Record anything load-bearing in `notes/claims.md`. Commit.

6. **Record `notes/claims.md`** — scoped to whatever the recipe did NOT already
   cover: the headline claim(s); datasets (version/hash, where they live);
   models/methods in re-implementable detail; evaluation metrics and the exact
   reported numbers; the compute envelope (decides if CI can auto-run it). If
   the recipe covered everything, this is a short confirmation. Commit.

7. **Reimplement only the uncovered claims** under `src/` (skip anything the
   recipe already reproduced; scope to the headline claim, not every ablation).
   Pin the environment in `requirements.txt` / `environment.yml`. Commit.

8. **Run the full replication** via `scripts/run.py` (the CI entry point);
   capture metrics as JSON into `results/`. Commit.

9. **Write `FINDINGS.md`:** reproduced vs. reported numbers (table); what the
   recipe covered vs. what you filled; gaps and where/why it diverged. Commit
   and push.

10. **Publish and finish.** Set the replication verdict in `paper.json` `status`
   — `replicated` / `failed` / `insufficient-hardware` — so the report's big
   status badge turns green / red / amber (it defaults to `in-progress`, blue).
   Confirm `.github/workflows/pages.yml` (themed site + PDF)
   and `.github/workflows/package.yml` (ZIP) run green; set Settings → Pages →
   Source: GitHub Actions. Keep `SKILL.md` and `replication_skill.md` truthful.
   **Stop / hand back** when `FINDINGS.md` reports at least one headline number
   with its reproduced value, `scripts/run.py` runs end-to-end from a clean
   clone (or documents the un-automatable data step), the repo is public and
   pushed, and the Pages deployment is green.

---

## Pointers

- Methodology / definition of done: `SKILL.md`.
- Long-horizon items: `todo.md`.
- Completed work + replication milestones (chronological): `devlog.md`.
- Narrative history: `git log`.
"""
)


_CLAWRXIV_SKILL_TMPL = Template(
    """---
name: replicate-$slug
description: Replicate the clawRxiv paper "$title" (clawrxiv:$paper_id) by running its shipped skill recipe first, then verifying against the paper and producing a runnable artifact, a findings report, and a downloadable package.
---

# Replicate (clawRxiv): $title

clawrxiv:$paper_id - $authors - $created_at
Agent author (claw): $claw_name - $abs_url

clawRxiv differentiates the paper **content**, **abstract**, and **skill file**.
The scaffold already fetched all three: content at
`replication_target/source/paper.md`, and the skill recipe handled below.

## Prerequisite

$skill_location

> **Consent gate (do this before running anything):** the skill recipe is code
> you did not write. Per harness safety requirements, ask the user for explicit
> consent before executing it (or any cloned scripts it pulls in), and wait for
> their answer. Reading the paper and the recipe text is fine; *running* it is
> gated. (A future automated security scan is in `todo.md`.)

## Plan

The efficient path: **run the shipped skill recipe FIRST**, then verify its
output against the paper and fill only the gaps. Reimplementing from scratch is
the fallback, not the default.

1. **Go live early.** Create a PUBLIC GitHub repo and push
   (`gh repo create --public --source=. --push`) so every later commit pushes
   and Pages/CI build as you go.

2. **Run the skill recipe first.** Execute `replication_skill.md` (or the recipe
   embedded in `paper.md`), capturing output to `results/`. clawRxiv hands you
   an agent-runnable recipe — this comes before any deep analysis.

3. **Verify the recipe's output against the paper** (`paper.md`): how much of
   the headline claims does it reproduce? Record in `notes/sources.md`.

4. **Check ALL references** — confirm the key cited results/datasets/baselines
   say what the paper claims.

5. **Record `notes/claims.md`** — scoped to what the recipe didn't cover:
   headline claim(s); datasets; methods; metrics and exact reported numbers;
   compute envelope (decides if CI can auto-run this).

6. **Reimplement only the gaps** under `src/`; pin `requirements.txt`.

7. **Run the replication.** `scripts/run.py` so CI can invoke it; metrics →
   `results/`.

8. **Write the findings.** `FINDINGS.md`: reproduced vs. reported (table); what
   the recipe covered vs. what you filled; gaps and divergences.

9. **Publish.** GitHub Pages deploys the findings + a transportable PDF report
   (`.github/workflows/pages.yml`); a ZIP replication package is built
   (`.github/workflows/package.yml`). The repo must be public with Pages set to
   Source: GitHub Actions.

## Budget guardrails

- If the paper's reported compute is more than ~4 GPU-hours on a single
  consumer GPU, mark this replication **not CI-runnable** in `paper.json` and
  document the reduced-scale variant instead.
- Prefer deterministic seeds and logged hashes so reruns are comparable.

## Definition of done

- `FINDINGS.md` exists and reports at least one headline number from the paper,
  with the reproduced value next to it.
- `scripts/run.py` runs end-to-end from a clean clone (or documents the data
  step that can't be automated).
- The repo is public and pushed; the GitHub Pages site and the ZIP package
  build green in Actions.
- This file still reflects how you actually did it — if you deviated, edit the
  plan above.
"""
)


_CLAWRXIV_README_TMPL = Template(
    """# Replicating: $title

**clawRxiv:** [$paper_id]($abs_url)
**Authors:** $authors
**Agent author (claw):** $claw_name
**Published:** $created_at - **Category:** $category

## Abstract

$abstract

## Replication status

Not started. The agent-executable plan is in [`SKILL.md`](./SKILL.md); the
concrete step queue is in [`queue.md`](./queue.md). This paper is from
**clawRxiv**, which ships an agent-runnable **skill recipe** alongside the paper
— so the efficient path is **skill-first**: run the recipe, verify it against
the paper, check all references, and only reimplement the gaps.

## What this repo produces

Three compounding artifacts:

1. **The replication** — runnable code under `src/` + `scripts/run.py`.
2. **The legibility layer** — `FINDINGS.md`, published as a GitHub Pages
   site with a transportable PDF report (built by GitHub Actions).
3. **`SKILL.md`** — a reusable, agent-executable replication methodology.

## Layout

- `replication_target/source/paper.md` — the clawRxiv paper content (committed;
  fetched at scaffold time — read it directly).
- `replication_skill.md` — the clawRxiv skill recipe (when shipped separately;
  otherwise embedded in `paper.md`). **Run it first.**
- `paper.json` — frozen clawRxiv metadata (from $api_url).
- `data_lake/` — other downloaded/supplied material (NOT the paper).
- `src/` — your reimplementation. `scripts/run.py` — CI entry point.
- `results/` — metrics JSON (gitignored). `FINDINGS.md` — the report.
- `.github/workflows/` — `pages.yml` (site + PDF), `package.yml` (ZIP).

## Deliverables (GitHub Actions)

To publish, **make this repo public** and set **Settings -> Pages -> Source:
GitHub Actions**. Then `pages.yml` deploys the findings site + PDF report and
`package.yml` builds a downloadable ZIP replication package. Site shape
inspiration: http://latent-space.emmaleonhart.com/
"""
)


def clawrxiv_claude_md(paper: ClawrxivPaper) -> str:
    return _CLAWRXIV_CLAUDE_TMPL.substitute(_clawrxiv_subs(paper))


def clawrxiv_queue_md(paper: ClawrxivPaper) -> str:
    return _CLAWRXIV_QUEUE_TMPL.substitute(_clawrxiv_subs(paper))


def clawrxiv_skill_md(paper: ClawrxivPaper) -> str:
    return _CLAWRXIV_SKILL_TMPL.substitute(_clawrxiv_subs(paper))


def clawrxiv_readme_md(paper: ClawrxivPaper) -> str:
    return _CLAWRXIV_README_TMPL.substitute(_clawrxiv_subs(paper))


# ---------------------------------------------------------------------------
# Research project templates (`cleanvibe research <name>`)
#
# A research project is, like `cleanvibe new`, a *fresh* project you scaffold
# for your OWN investigation — not a replication of someone else's paper. It
# keeps everything `new` has (data_lake/, the three-cron playbook,
# todo.md → queue.md → devlog.md), and adds two things borrowed from the
# replication flow:
#   1. an up-front **literature review** step (agentic RAG) before any building,
#      with sources + a synthesized survey committed under `literature/`; and
#   2. a published, **themed GitHub Pages report** under `docs/` (light "paper"
#      theme + dark-mode variant, adapted from the latent-space-cartography
#      site http://latent-space.emmaleonhart.com/) plus a transportable PDF,
#      built by `.github/workflows/pages.yml`.
#
# As of v1.14.0 the workflow/cron/emergency-stop behavior ships as standalone
# skills (skills.py), vendored into .claude/skills/; CLAUDE.md carries only the
# SKILLS_POINTER. Research IS extensive work, so — unlike replication — the
# `autonomous-loop` (three-cron) skill applies to it.
# ---------------------------------------------------------------------------


# Placeholder used when the user did not pass `--question`; the bootstrap queue
# pins it down by interviewing the user.
_RESEARCH_QUESTION_PLACEHOLDER = (
    "_(not yet defined — the bootstrap queue's first research step pins this "
    "down with you)_"
)


def _research_question(question: str | None) -> str:
    q = (question or "").strip()
    return q if q else _RESEARCH_QUESTION_PLACEHOLDER


RESEARCH_GITIGNORE = """# Research outputs (regenerated by runs; not committed)
results/
checkpoints/
*.ckpt
*.pt
*.pth
wandb/

# Built deliverables (GitHub Actions builds the PDF into docs/; the root copy
# is transient). The docs/ site itself IS committed.
report.pdf

# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
dist/
build/
*.egg

# Virtual environments
.venv/
venv/
env/

# IDE / OS / env
.vscode/
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db
.env
.env.local
"""


# GitHub Actions: publish the themed docs/ site + build a transportable PDF
# report from FINDINGS.md into docs/report.pdf. Static constant — contains
# ${{ }} expressions; never run through Template.
RESEARCH_PAGES_YML = """# Publishes the docs/ folder as a GitHub Pages site (the themed research
# report) and builds a transportable PDF from FINDINGS.md into docs/report.pdf.
#
# Pages is auto-enabled by the `actions/configure-pages` step below
# (enablement: true), so there is NO manual "Settings -> Pages" toggle to do —
# the only requirement is that the repo is PUBLIC (free GitHub Pages). The first
# push that runs this workflow turns Pages on and deploys.

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
      - name: Configure Pages (auto-enables Pages if not already on)
        uses: actions/configure-pages@v5
        with:
          enablement: true
      - name: Install pandoc
        run: sudo apt-get update && sudo apt-get install -y pandoc
      - name: Build report PDF into docs/
        run: |
          mkdir -p docs
          if [ -f FINDINGS.md ]; then
            pandoc FINDINGS.md -s -o docs/report.pdf || echo "PDF render skipped"
          else
            echo "No FINDINGS.md yet; skipping PDF build"
          fi
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs

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


# The default cleanvibe **report theme** — one source of truth, shared by BOTH
# `research` (docs/index.html) and `replicate` (the GitHub Pages findings site).
# Adapted from http://latent-space.emmaleonhart.com/ : a warm "paper" light
# theme + a dark-mode variant, plus the color-coded `.status-badge` used by the
# replication report (green = replicated, red = failed, amber = insufficient
# hardware, blue = in progress). Self-contained, dependency-free CSS.
CLEANVIBE_REPORT_CSS = """  :root {
    --bg: #f6f2ec;
    --surface: #efe9df;
    --card: #ece4d6;
    --accent: #b8553a;
    --accent-soft: #e9d5cc;
    --text: #2d2a26;
    --dim: #6e6a61;
    --green: #5b7a4a;
    --yellow: #a07a2b;
    --blue: #3f6487;
    --border: #d9d1c1;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.75;
    max-width: 880px; margin: 0 auto; padding: 2.5rem 1.5rem;
    font-size: 16.5px;
  }
  h1 {
    color: var(--text); font-size: 2.2rem; margin-bottom: 0.4rem;
    font-weight: 700; letter-spacing: -0.01em;
  }
  h2 {
    color: var(--blue); font-size: 1.35rem; margin: 2.75rem 0 1rem;
    padding-bottom: 0.4rem; border-bottom: 1px solid var(--border);
    font-weight: 600;
  }
  h3 { font-size: 1.1rem; font-weight: 600; margin: 1.5rem 0 0.5rem; }
  p { margin-bottom: 1rem; }
  a { color: var(--blue); text-decoration: none; border-bottom: 1px solid transparent; }
  a:hover { border-bottom-color: var(--blue); }
  ul, ol { margin: 0 0 1rem 1.5rem; }
  li { margin-bottom: 0.3rem; }
  blockquote {
    border-left: 3px solid var(--border); padding-left: 1rem; margin: 1rem 0;
    color: var(--dim);
  }
  table { border-collapse: collapse; width: 100%; margin: 1.2rem 0; font-size: 0.95rem; }
  th, td { border: 1px solid var(--border); padding: 0.5rem 0.7rem; text-align: left; }
  th { background: var(--surface); font-weight: 600; }
  img { max-width: 100%; height: auto; border-radius: 6px; }
  .lede { color: var(--dim); font-size: 1.1rem; margin-top: 0.8rem; line-height: 1.65; }
  /* Replication verdict banner (driven by paper.json `status`). */
  .status-badge {
    display: block; text-align: center; font-weight: 700; font-size: 1.15rem;
    color: #fff; padding: 0.9rem 1.2rem; border-radius: 8px; margin: 1.5rem 0;
    letter-spacing: 0.01em;
  }
  .status-badge.replicated { background: var(--green); }
  .status-badge.failed { background: var(--accent); }
  .status-badge.insufficient { background: var(--yellow); }
  .status-badge.in-progress { background: var(--blue); }
  .question {
    background: var(--surface); border-left: 3px solid var(--accent);
    border-radius: 4px; padding: 1rem 1.3rem; margin: 1.5rem 0;
    font-size: 1.05rem; color: var(--text);
  }
  .question .kicker {
    display: block; font-size: 0.78rem; text-transform: uppercase;
    letter-spacing: 0.06em; color: var(--accent); font-weight: 700;
    margin-bottom: 0.3rem;
  }
  .actions {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 1rem; margin: 2rem 0 0.5rem;
  }
  .action {
    display: block; background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: 1.25rem 1.3rem; color: var(--text);
    transition: border-color 0.15s, transform 0.15s;
  }
  .action:hover { border-color: var(--accent); transform: translateY(-2px); }
  .action .kicker {
    font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em;
    color: var(--accent); font-weight: 700;
  }
  .action .title { font-size: 1.12rem; font-weight: 600; margin: 0.35rem 0 0.3rem; }
  .action .desc { font-size: 0.9rem; color: var(--dim); line-height: 1.55; }
  .action .arrow { color: var(--accent); font-weight: 700; }
  .pillars { margin: 1rem 0; }
  .pillar {
    background: var(--surface); border-left: 3px solid var(--blue);
    border-radius: 4px; padding: 1rem 1.3rem; margin: 1rem 0;
  }
  .pillar h3 { color: var(--blue); font-size: 1.05rem; font-weight: 600; margin-bottom: 0.3rem; }
  .pillar p { color: var(--dim); font-size: 0.95rem; margin: 0; }
  code {
    background: var(--surface); padding: 0.1rem 0.35rem; border-radius: 3px;
    font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace; font-size: 0.86em;
    color: var(--accent); border: 1px solid var(--border);
  }
  pre {
    background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
    padding: 1rem; overflow-x: auto; margin: 1rem 0;
  }
  pre code { background: none; border: none; padding: 0; color: var(--text); }
  footer {
    margin-top: 3rem; padding-top: 1.2rem; border-top: 1px solid var(--border);
    color: var(--dim); font-size: 0.85rem;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #1c1d22;
      --surface: #26282f;
      --card: #2d3038;
      --accent: #d97757;
      --accent-soft: rgba(217,119,87,0.12);
      --text: #e8e4dc;
      --dim: #9a9589;
      --green: #8ba87a;
      --yellow: #c6a15e;
      --blue: #85a8c4;
      --border: #3a3d46;
    }
  }
  @media (max-width: 600px) {
    body { padding: 1.2rem; }
    .actions { grid-template-columns: 1fr; }
    h1 { font-size: 1.7rem; }
  }"""


# The themed report landing page that ships in docs/index.html (research mode).
# Placeholders (__PROJECT_NAME__ / __QUESTION__ / __DATE__ / __REPORT_CSS__) are
# filled by str.replace — the CSS is full of `{` and `$`, so neither f-strings
# nor string.Template are safe here. The agent edits the CONTENT (lede, cards,
# pillars, findings) as the project progresses; the chrome (the shared
# CLEANVIBE_REPORT_CSS theme) stays.
_RESEARCH_INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__PROJECT_NAME__</title>
<meta name="description" content="A cleanvibe research project: __QUESTION__">
<style>
__REPORT_CSS__
</style>
</head>
<body>

<!-- This is the published research report (GitHub Pages serves docs/). Edit the
     CONTENT as the project progresses; keep the theme/chrome. The build step in
     .github/workflows/pages.yml also drops a transportable report.pdf alongside. -->

<h1>__PROJECT_NAME__</h1>
<p class="lede">
  A <strong>cleanvibe research project</strong>. <em>TODO: replace this lede with a
  one-paragraph plain-language summary of what this project investigates and what
  it found.</em>
</p>

<div class="question">
  <span class="kicker">Research question</span>
  __QUESTION__
</div>

<div class="actions">
  <a class="action" href="#findings">
    <div class="kicker">Read</div>
    <div class="title">The findings</div>
    <div class="desc">
      The results of the investigation. <span class="arrow">&darr;</span>
    </div>
  </a>
  <a class="action" href="report.pdf">
    <div class="kicker">Download</div>
    <div class="title">The report (PDF)</div>
    <div class="desc">
      Full write-up, typeset. <span class="arrow">&darr;</span>
    </div>
  </a>
  <a class="action" href="#">
    <div class="kicker">Source</div>
    <div class="title">GitHub repository</div>
    <div class="desc">
      Code, data, and the literature review. <span class="arrow">&nearr;</span>
    </div>
  </a>
</div>

<h2>What this project does</h2>
<div class="pillars">
  <div class="pillar">
    <h3>1 &middot; The question</h3>
    <p>__QUESTION__</p>
  </div>
  <div class="pillar">
    <h3>2 &middot; Grounded in the literature</h3>
    <p>
      TODO: one line on the prior work this builds on (the full survey lives in
      <code>literature/REVIEW.md</code>) and the gap this project addresses.
    </p>
  </div>
  <div class="pillar">
    <h3>3 &middot; The finding</h3>
    <p>TODO: one line on the headline result, once there is one.</p>
  </div>
</div>

<h2 id="findings">Findings</h2>
<p>
  <em>TODO: write the findings here (or render them from <code>FINDINGS.md</code>).
  Until results exist, this project is <strong>in progress</strong>.</em>
</p>

<footer>
  <p>
    Scaffolded with <a href="https://github.com/Immanuelle/cleanvibe">cleanvibe</a>
    <code>research</code> &middot; generated __DATE__
  </p>
</footer>

</body>
</html>
"""


def research_index_html(project_name: str, question: str | None = None) -> str:
    """The themed docs/index.html report landing page for a research project."""
    date = datetime.now().strftime("%Y-%m-%d")
    q = _research_question(question)
    return (
        _RESEARCH_INDEX_HTML
        .replace("__REPORT_CSS__", CLEANVIBE_REPORT_CSS)
        .replace("__PROJECT_NAME__", project_name)
        .replace("__QUESTION__", q)
        .replace("__DATE__", date)
    )


def research_claude_md(project_name: str, question: str | None = None) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    q = _research_question(question)
    return f"""# {project_name} — research project

## Project Description

This is a **research project** scaffolded by `cleanvibe research`. Unlike a
*replication* (which reproduces someone else's paper), this is **your own**
investigation: you pose a question, survey the prior literature, run experiments
or build something to answer it, and publish the findings.

> **Research question:** {q}

Like a cleanvibe replication it produces a published, legible report — a themed
**GitHub Pages site** (`docs/`) plus a transportable PDF — but the content is
original research, grounded in a literature review rather than in one target
paper.

## Research workflow (the shape of this project)

1. **Question.** Pin down precisely what is being investigated / built and what a
   successful answer looks like. (Bootstrap step; the `> Research question` above
   gets filled in then.)
2. **Literature review (agentic RAG) — BEFORE building anything.** Survey the
   prior work: use whatever agentic search / RAG tooling is available (web
   search, `WebFetch`, and the `deep-research` skill if present) to find the
   relevant papers, posts, datasets, and code; read them; collect sources with
   citations into `literature/`; synthesize `literature/REVIEW.md` (what is
   already known, the gaps, and what *this* project adds). This grounds the work
   in the field instead of reinventing it, and it is what makes a `research`
   project different from a plain `new` one.
3. **Hypotheses & experiments.** Turn the identified gap into concrete, testable
   experiments / build steps. Plan them `todo.md` → `queue.md`.
4. **Build & run.** Implement under `src/`; entry point `scripts/run.py`;
   metrics → `results/`.
5. **Findings & report.** Write `FINDINGS.md`; keep the themed `docs/` site and
   the PDF report current as results land.

## Architecture and Conventions

- **`literature/`** — the literature review: source notes (one file per source,
  or a `sources.md`) and `REVIEW.md` (the synthesized survey, with citations).
  Committed; it is the evidentiary base of the project. Built in workflow step 2,
  before any implementation.
- **`data_lake/`** — datasets and other supplied/downloaded material (standard
  cleanvibe convention). Committed.
- **`src/`** — the research code. **`scripts/run.py`** — the entry point CI can
  invoke. **`results/`** — metrics JSON / run outputs (gitignored). **`FINDINGS.md`**
  — the write-up (question, method, results, limitations).
- **`docs/`** — the **published GitHub Pages site** (themed `index.html`, figures,
  and the built `report.pdf`). This is the legibility layer. The theme ships
  pre-styled (warm "paper" light theme + dark-mode variant); edit the content,
  keep the chrome. Site-shape inspiration: http://latent-space.emmaleonhart.com/
- **Go live early.** Create a **PUBLIC** GitHub repo and push near the start so
  every commit pushes and Pages/CI build as you go (public is required for free
  GitHub Pages).
- **Deliverables are built by GitHub Actions.** `.github/workflows/pages.yml`
  deploys `docs/` (the report site) and builds `docs/report.pdf` from
  `FINDINGS.md`. Make the repo public and set Settings -> Pages -> Source:
  GitHub Actions.

{SKILLS_POINTER}

# currentDate
Today's date is {date}.
"""


def research_readme_md(project_name: str, question: str | None = None) -> str:
    q = _research_question(question)
    return f"""# {project_name}

> A **research project** scaffolded with
> [cleanvibe](https://github.com/Immanuelle/cleanvibe) `research`.

**Research question:** {q}

## About

This is an original research project (not a replication). It poses a question,
surveys the prior literature, runs experiments / builds something to answer it,
and publishes the findings as a themed GitHub Pages report + a transportable PDF.

The distinctive first move is a **literature review** (agentic RAG) *before* any
building — see `literature/`.

## How it's organized

- `literature/` — the literature review (sources + `REVIEW.md`), built first.
- `data_lake/` — datasets and supplied material.
- `src/` — the research code; `scripts/run.py` — the run entry point.
- `results/` — run outputs (gitignored). `FINDINGS.md` — the write-up.
- `docs/` — the published GitHub Pages report site (themed) + built PDF.
- `queue.md` / `todo.md` / `devlog.md` — the cleanvibe work loop.

## Getting started

```
cd {project_name}
claude
```

Then work `queue.md` top to bottom. The bootstrap sequence pins down the
research question with you, runs the literature review, plans the experiments,
takes the repo public, and keeps the report current as results land.

## Published report

Once the repo is public with Pages set to **Source: GitHub Actions**,
`.github/workflows/pages.yml` deploys `docs/` (the report site) and builds
`docs/report.pdf`. Site-shape inspiration: http://latent-space.emmaleonhart.com/
"""


def research_queue_md(project_name: str, question: str | None = None) -> str:
    q = _research_question(question)
    return f"""# {project_name} — Work Queue (research)

**This file is a queue of *concrete, executable steps*, not a state snapshot.** It lists what is being worked on right now. Finished work lives in `devlog.md` (a dated entry) and `git log`; longer-horizon, *abstract* work lives in `todo.md` and gets decomposed into items here when it's ready to execute. **When an item is done, delete it from this file AND append a dated entry to `devlog.md` in the same commit, then push.** Do not add checkmarks, "done" markers, or status indicators in place. If an item is still here, it is not done.

**This is a `cleanvibe research` project** — your own investigation, not a replication. Its distinctive move is an up-front **literature review** (agentic RAG) before any building, and a published, themed GitHub Pages **report** under `docs/`.

**Why this file exists:** when a planning step produces a plan, that plan is written here BEFORE execution starts, so an interrupted session can pick up from the queue rather than from chat context that may be gone.

See `CLAUDE.md` § "Workflow Rules" and § "Research workflow" for how this file, planning mode, and the task tool stay in sync.

**Three-cron playbook.** Research IS extensive work, so it runs under three local `CronCreate` jobs — **work-loop at :03** (the engine that drains `queue.md` and refills it from `todo.md`), **auto-flush at :15** (commit/push backstop), and **status-report at :42** (heartbeat). On a fresh session they are **started** as the opening step (bootstrap step 1 below); on a mid-session **large-scale re-fill** of this queue the FIRST item worked is instead to **kill** the already-running crons. Either way the **last two items are always pinned at the tail** (see `## Always last`). Entering planning mode also disables the crons; their restart lives at the end of the queue. (See `CLAUDE.md` § "Autonomous productivity loop — the three-cron playbook".)

---

## Active — First-session bootstrap (research)

Work these top to bottom. **Delete each item from this file in the same commit that completes it, and append a dated entry to `devlog.md`.** Push after every step. When this whole section is gone, the project has finished bootstrap and the queue is ready to be repopulated with the real research/experiment work (see the final item).

1. **Start the three-cron playbook.** Use the `CronCreate` tool to schedule three local crons (all `durable: false`): **work-loop at `3 * * * *`** (sync → take top actionable `queue.md` item / promote from `todo.md` → hold the hard rails → commit + push → one-line report), **auto-flush at `15 * * * *`** (commit + push pending work, no empty commits), and **status-report at `42 * * * *`** (reporting only, no code changes). Together they turn this run into a self-sustaining hourly cadence so a long autonomous session can't silently lose the thread. (See `CLAUDE.md` § "Autonomous productivity loop"; the `## Always last` section keeps them running.)

2. **Triage user-supplied files into `data_lake/`.** Move anything the user dropped in (notes, exports, datasets, spec PDFs, prior drafts) into `data_lake/` so the root stays clean; leave the `.gitkeep`. Extract any `.zip` into `data_lake/` and add the `.zip` to `.gitignore`. For anything large enough to need Git LFS (>50 MB, or large binary like video/audio/datasets), STOP and ask the user first. Commit, describing what moved.

3. **Define the research question (interview the user).** This is *your own* project, so the question is the foundation. Read everything in `data_lake/` to build a hypothesis, then ask the user directly: **What question are you trying to answer? What are you building / investigating? What would a successful outcome look like? What's in scope vs. out of scope? Any constraints (methods, data, compute, deadline)?** Write the concrete research question into `README.md` (replace the placeholder), `CLAUDE.md`'s `> Research question` line and "Project Description", and the `docs/index.html` lede + question block. Commit, briefly noting how the question was arrived at.

4. **Literature review (agentic RAG) — BEFORE building anything.** This is the step that makes a `research` project different from a plain `new` one. Survey the prior work on the question: use whatever agentic search / RAG tooling is available (web search, `WebFetch`, and the `deep-research` skill if present). For each relevant source, write a short note (claim, method, what it contributes, citation) into `literature/` — one file per source, or a single `literature/sources.md`. Then synthesize `literature/REVIEW.md`: what is already known, where the gaps are, and what *this* project adds. Cite sources properly. Reflect the one-line "grounded in the literature" summary into `docs/index.html`. Commit `literature/` on its own so the review is a reviewable artifact.

5. **Create `todo.md` — the long-horizon research plan.** Informed by the gap the literature review surfaced, write `todo.md` as the project's long-term horizon: the hypotheses to test, experiments to run / things to build, and the eventual shape of the report. Items here are *abstract destinations*, decomposed into concrete steps in `queue.md` later. Use the format in `CLAUDE.md` § "Queue and longer-horizon work". Commit `todo.md` on its own.

6. **Go live: create a PUBLIC GitHub repo and push.** Public is required for free GitHub Pages. `gh repo create --public --source=. --push`. The `pages.yml` workflow **auto-enables Pages itself** (via `actions/configure-pages` with `enablement: true`) — there is no manual Settings toggle to do; just confirm the repo is public and CI (`.github/workflows/`) is wired, and on push `docs/` (the report site) + the built PDF deploy. From here every commit pushes and Pages/CI build as you go.

7. **Replace this bootstrap queue with the real research queue.** Pull the first item(s) from `todo.md` and decompose them into a concrete, ordered list of experiment / implementation tasks under a new `## Active` section (deleting this bootstrap section as part of the same edit). Mirror into the task tool. **Keep the `## Always last` section pinned at the very bottom.** The real queue's FIRST work item should **start the three crons** — unless this is a mid-session large-scale re-fill while they are already running, in which case the first item is instead to **kill them** (the pinned tail restarts them). Commit the new queue.

8. **Work the queue until the stop condition.** Pull the top item, do it, **delete it from `queue.md` AND append a dated entry to `devlog.md`** in the same commit, push, let CI run. Build under `src/`, run via `scripts/run.py`, capture metrics to `results/`, and keep `FINDINGS.md` + the themed `docs/` report current as results land. When `queue.md` empties, refill from `todo.md`. **Stop** when: the research question has a defensible answer (or a clearly reported partial result), `FINDINGS.md` and the published `docs/` report reflect it, `queue.md` is empty, and the repo is online with green CI/Pages. At that point, hand back to the user.

---

## Always last — restart the three crons and summarize

**These two items stay pinned to the tail of the queue at all times** — below every bootstrap step and below every real work item. They are the closing half of the three-cron lifecycle in `CLAUDE.md` § "Autonomous productivity loop":

A. **Ensure the three crons are running** — start them if this session never did, restart them if a planning burst / queue re-fill killed them: work-loop (`3 * * * *`), auto-flush (`15 * * * *`), status-report (`42 * * * *`).
B. **Run the status-report action once more, independently** — an end-of-session summary of everything that happened this session.

---

## Pointers

- Long-horizon backlog (abstract goals, source of future queue items): `todo.md`.
- The literature review (the project's evidentiary base): `literature/REVIEW.md`.
- Completed work (chronological, with milestones): `devlog.md`.
- Narrative history: `git log`.
"""
