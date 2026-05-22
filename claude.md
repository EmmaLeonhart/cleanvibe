# cleanvibe

## Project Description
A pip-installable Python CLI (`cleanvibe`) that scaffolds AI-assisted coding projects and launches Claude Code. Zero dependencies -- just stdlib.

## Architecture
```
cleanvibe/
├── cleanvibe/
│   ├── __init__.py      # Version string
│   ├── cli.py           # argparse-based CLI entry point (new/clone/convert/replicate)
│   ├── scaffold.py      # Core logic: create_project(), clone_project(), convert_project()
│   ├── arxiv.py         # stdlib arXiv/alphaxiv metadata fetch + parsing (zero-dep)
│   ├── replicate.py     # replicate_project(): standalone per-paper replication project
│   └── templates.py     # scaffold + replication-project templates
├── tests/               # stdlib unittest, run by CI on win/mac/linux
├── docs/                # replication_framing.md (vision) + replication-examples/ (reference corpus)
├── pages/                # static GitHub Pages site (index.html/identity.css/CNAME → cleanvibe.emmaleonhart.com)
├── .github/workflows/
│   ├── ci.yml           # 3-OS x 2-py-version matrix
│   ├── pages.yml        # deploy pages/ to GitHub Pages
│   └── publish.yml      # PyPI publish on release
├── pyproject.toml       # Package metadata, [project.scripts] entry point
├── LICENSE              # MIT
├── README.md            # Human-facing docs
├── queue.md             # Active, delete-only work queue
├── todo.md              # Long-horizon backlog (abstract)
└── devlog.md            # Where "done" lives: dated entries + releases
```

## Key Decisions
- **Zero dependencies**: Uses only stdlib (argparse, pathlib, subprocess, platform). No click, no typer. Keeps install fast and reduces supply chain risk.
- **Cross-platform**: Windows launches claude in a new cmd window via `subprocess.Popen`. Unix uses `os.execlp` to replace the process.
- **Non-destructive cloning**: `cleanvibe clone` only injects files that are missing. Never overwrites.
- **`--dry-run` flag**: Shows what would happen without writing anything. Builds trust.
- **queue.md is part of the scaffold**: Every project gets a `queue.md` and a CLAUDE.md that enforces planning into queue.md before executing, mirroring it into the task tool, and updating it in the same commit as the work. See the reference repos at `../Sutra/`, `../SutraDB/`, `../shintowiki-scripts/` for the established convention.
- **todo.md as long-horizon backlog**: `todo.md` holds the project's abstract long-term horizons; `queue.md` holds the concrete executable steps. Items flow `todo.md` → `queue.md` → done. The bootstrap sequence creates `todo.md` between "write documentation" and "write the real queue" so the long-horizon picture exists *before* anything concrete is queued.
- **`data_lake/.gitkeep`**: The Python scaffold creates `data_lake/.gitkeep` eagerly (in `create_project` and clone/convert injection) so the directory exists from the first commit — a user can drop files straight into it before the bootstrap session ever runs. The bootstrap queue step 1 then just moves user-supplied files into the already-existing `data_lake/`.
- **`clone` is codebase onboarding, not bootstrapping**: `cleanvibe clone` clones an existing repo, creates a dedicated `cleanvibe-onboarding` branch (default branch untouched), and commits a *small* onboarding `queue.md` + `CLAUDE.md` there — **no `data_lake/`** (nothing was dropped in) and **no README overwrite**. CLAUDE.md/queue.md are *prepended* if they already exist (`_prepend_or_write`, newest-on-top), so re-running just layers a fresh block. The onboarding queue's job is to document the repo, make its docs accurate, rewrite the onboarding CLAUDE.md into the repo's *real* practices, add tests/CI if sparse, then hand off to the repo's own `todo.md`. This is intentionally distinct from `new` (fresh project) and `convert` (in-place, missing-only injection).
- **Project website**: a dependency-free static site under `site/` (vanilla HTML/CSS/JS, tabs for what-is / new / clone / replicate) deployed by `.github/workflows/pages.yml`. Pages Source on the repo is set to "GitHub Actions".
- **`cleanvibe replicate` (sibling subcommand, dual-mode)**: `cleanvibe replicate <ref-or-folder>` scaffolds a *standalone* replication project for one paper (absorbed from the now-sunset `replication_skill` project). It is a sibling of `new`/`clone`/`convert`. The single positional argument dual-dispatches via `arxiv.is_arxiv_ref()`:
  - **arXiv mode** (arg parses as an arXiv/alphaxiv id or URL): fetch metadata, scaffold `replicating-<paper-slug>/` (default dir **silently** auto-suffixed `-2`/`-3` on collision — the user supplied no name, deliberately asymmetric with `cleanvibe new` which prompts), write `paper.json` + `download_paper.py`. `arxiv.parse_arxiv_id` accepts **any** arxiv/alphaxiv URL path (not just `abs|pdf|html` — alphaxiv's primary form is `/overview/<id>`, plus `/forum/`, versioned ids, trailing slug/query): for any arxiv/alphaxiv URL it extracts the first id-shaped token from anywhere in the string; the strict bare-id path is unchanged. (Before v1.3.0 only `/(abs|pdf|html)/` worked and the `ValueError` surfaced as a raw traceback — that was the "arXiv link replication not really working" bug.)
  - **manual drop-in mode** (arg is anything else → a folder name): NO metadata fetch, NO `download_paper.py`, NO `paper.json`, NO network. The user drops the paper PDF(s) into `replication_target/` and supporting material into `data_lake/` by hand; the manual templates (`replication_manual_{claude,queue,skill,readme}_md` in `templates.py`) say this up front and queue step 1 makes the agent STOP and ask for the paper rather than invent one. Injection is **non-destructive** (`scaffold._write_if_missing`) so running on a folder that already holds the dropped paper / a user README never clobbers it; it commits into an existing git repo or git-inits a fresh one.
  - Shared structure (both modes): the paper lives under `replication_target/` (gitignored — copyrighted/local input, **never** in `data_lake/`); `data_lake/` exists for other material; the authors' code is cloned as a git submodule under `replication_target/`; deliverables (GitHub Pages site + transportable PDF report + downloadable ZIP package) are built by GitHub Actions, not committed. arXiv access is stdlib `urllib` only (zero-dep guarantee); arXiv-mode replication templates are inline `string.Template` constants, manual-mode templates are plain f-string functions (both no package data). Long-horizon replication-infrastructure work is in `todo.md`; framing/vision in `docs/replication_framing.md` with a reference corpus under `docs/replication-examples/`.
- **`devlog.md` — "done" lives here, so `queue.md` can stay delete-only.** Every cleanvibe-scaffolded project (and this repo) ships a `devlog.md`. Finishing a queue item = delete the item from `queue.md` AND append a dated entry to `devlog.md` in the same commit, then push. Never tick boxes in place — a checked box left in `queue.md` is the failure mode this file exists to prevent. Releases (tag + one-line note) and notable milestones also live in `devlog.md`. `cleanvibe new` and `cleanvibe replicate` write a starter entry; `cleanvibe clone` and `cleanvibe convert` inject a "backfill from `git log`" variant whose first onboarding task is to catch the existing repo's devlog up to present before normal work resumes. Flow: `todo.md` (abstract) → `queue.md` (concrete steps) → task tool (in-flight) → `devlog.md` + `git log` (history).
- **PyPI packaging**: `pyproject.toml` declares `[tool.setuptools] packages = ["cleanvibe"]` explicitly. Without this, setuptools' flat-layout auto-discovery also picks up sibling directories like `site/` and `pages/` as candidate "packages" and refuses to build (caused the v1.0.0 PyPI publish to fail; fixed in v1.1.0).
- **Default branch is `main`, not `master`**: every cleanvibe-init'd repo (`new` / `convert` / `replicate`) passes `git init -b main` so the initial branch is `main` regardless of the user's `init.defaultBranch` config. Requires git ≥ 2.28 (mid-2020). Fixed in v1.1.1; older cleanvibe-scaffolded repos may need a one-time `git branch -m master main`.
- **Python 3.9 compat**: any module that uses PEP 604 unions (`X | None`) or PEP 585 generics (`list[str]`) in annotations must include `from __future__ import annotations` at the top — otherwise it fails at import on 3.9 (CI matrix target). `cli.py`, `arxiv.py`, and `templates.py` all carry the future import.

## Workflow Rules
- **Commit early and often.** Every meaningful change gets a descriptive commit.
- **Plan into `queue.md` first, then execute.** Writing the plan into queue.md before doing the work means an interrupted session can resume. Mirror items into the task tool.
- **`todo.md` is the basis for `queue.md`.** Long-horizon items live in `todo.md`; they get decomposed into concrete steps in `queue.md` when work begins on them. Delete from both when done.
- **Finishing a queue item = delete from `queue.md` + append a dated entry to `devlog.md`**, in the same commit as the work, then push. NEVER tick boxes in place. `queue.md` only ever holds not-yet-done work; `devlog.md` is the chronological record of what has been done (and what was released).
- **Keep this file, README.md, and devlog.md up to date** as the project evolves.

## Default replication target & live smoke tests
- **The default paper for `cleanvibe replicate` is arXiv:2605.20919 — "Sutra: Tensor-Op RNNs as a Compilation Target for Vector Symbolic Architectures"** (the maintainer's own paper). Use it whenever you need to exercise the `replicate` pipeline end-to-end against a real paper.
- **`tests/scratch/` is a gitignored sandbox for live `replicate` runs.** It is in `.gitignore`; never commit its contents. Each run scaffolds a full replication project (which git-inits its own nested repo) in there.
- The committed unit tests in `tests/` are network-free (they monkeypatch `fetch_paper`). A **live** smoke test actually hits arXiv, e.g.:
  ```
  python -m cleanvibe.cli replicate https://arxiv.org/abs/2605.20919 tests/scratch/replicating-sutra --no-claude
  ```
  Use `--no-claude` so it doesn't launch a Claude window, and an explicit path under `tests/scratch/`.
- The full set of link forms the parser must accept (regression set): `https://arxiv.org/abs/<id>[vN]`, `/pdf/`, `/html/`, `/src/`, `https://doi.org/10.48550/arXiv.<id>`, `https://www.alphaxiv.org/{abs,overview,audio}/<id>`, bare `<id>[vN]`, and `arXiv:<id>`.

## Writing
- Do not use "honest", "honesty", or "honestly" — and do not swap in "frank", "frankly", "candid", "candidly", or "transparently", which are the same self-congratulatory move in a different coat. When something failed, name the failure: "it didn't work", "I got that wrong", "this failed" — flat, no qualifier. Tagging a report "honest" implies the rest aren't, and couching a failure as honesty asks for credit for the admission, which is worse than the failure itself. Use a precise positive word ("accurate", "plainly", "truly") only when that is genuinely the meaning — never as a halo on a bad outcome.
