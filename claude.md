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
├── site/                # static GitHub Pages site (index.html/style.css/tabs.js)
├── .github/workflows/
│   ├── ci.yml           # 3-OS x 2-py-version matrix
│   ├── pages.yml        # deploy site/ to GitHub Pages
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
- **`clone` is codebase onboarding, not bootstrapping**: `cleanvibe clone` clones an existing repo, creates a dedicated `cleanvibe-onboarding` branch (default branch untouched), and commits a *small* onboarding `queue.md` + `CLAUDE.md` there — **no `data_lake/`** (nothing was dropped in) and **no README overwrite**. CLAUDE.md/queue.md are *prepended* if they already exist (`_prepend_or_write`, newest-on-top), so re-running just layers a fresh block. The onboarding queue's job is to document the repo, make its docs honest, rewrite the onboarding CLAUDE.md into the repo's *real* practices, add tests/CI if sparse, then hand off to the repo's own `todo.md`. This is intentionally distinct from `new` (fresh project) and `convert` (in-place, missing-only injection).
- **Project website**: a dependency-free static site under `site/` (vanilla HTML/CSS/JS, tabs for what-is / new / clone / replicate) deployed by `.github/workflows/pages.yml`. Pages Source on the repo is set to "GitHub Actions".
- **`cleanvibe replicate` (sibling subcommand)**: `cleanvibe replicate <arxiv-or-alphaxiv-url>` scaffolds a *standalone* replication project for one paper (absorbed from the now-sunset `replication_skill` project). It is a sibling of `new`/`clone`/`convert`. Structure: the paper lives at `replication_target/paper.pdf` (gitignored, **never** in `data_lake/`); `data_lake/` still exists for other downloaded material; the authors' code is cloned as a git submodule under `replication_target/`; the deliverables (a GitHub Pages site, a transportable PDF report, and a downloadable ZIP replication package) are built by GitHub Actions, not committed. The default directory is `replicating-<paper-slug>`, **silently** auto-suffixed `-2`/`-3` on collision (the user supplied no name) — deliberately asymmetric with `cleanvibe new`, which prompts. arXiv access is stdlib `urllib` only (preserves the zero-dependency guarantee); replication templates are inline `string.Template` constants (no package data). Long-horizon replication-infrastructure work is tracked in `todo.md`; the framing/vision lives in `docs/replication_framing.md` with a reference corpus under `docs/replication-examples/`.
- **`devlog.md` — "done" lives here, so `queue.md` can stay delete-only.** Every cleanvibe-scaffolded project (and this repo) ships a `devlog.md`. Finishing a queue item = delete the item from `queue.md` AND append a dated entry to `devlog.md` in the same commit, then push. Never tick boxes in place — a checked box left in `queue.md` is the failure mode this file exists to prevent. Releases (tag + one-line note) and notable milestones also live in `devlog.md`. `cleanvibe new` and `cleanvibe replicate` write a starter entry; `cleanvibe clone` and `cleanvibe convert` inject a "backfill from `git log`" variant whose first onboarding task is to catch the existing repo's devlog up to present before normal work resumes. Flow: `todo.md` (abstract) → `queue.md` (concrete steps) → task tool (in-flight) → `devlog.md` + `git log` (history).
- **PyPI packaging**: `pyproject.toml` declares `[tool.setuptools] packages = ["cleanvibe"]` explicitly. Without this, setuptools' flat-layout auto-discovery also picks up sibling directories like `site/` and `pages/` as candidate "packages" and refuses to build (caused the v1.0.0 PyPI publish to fail; fixed in v1.1.0).

## Workflow Rules
- **Commit early and often.** Every meaningful change gets a descriptive commit.
- **Plan into `queue.md` first, then execute.** Writing the plan into queue.md before doing the work means an interrupted session can resume. Mirror items into the task tool.
- **`todo.md` is the basis for `queue.md`.** Long-horizon items live in `todo.md`; they get decomposed into concrete steps in `queue.md` when work begins on them. Delete from both when done.
- **Finishing a queue item = delete from `queue.md` + append a dated entry to `devlog.md`**, in the same commit as the work, then push. NEVER tick boxes in place. `queue.md` only ever holds not-yet-done work; `devlog.md` is the chronological record of what has been done (and what was released).
- **Keep this file, README.md, and devlog.md up to date** as the project evolves.
