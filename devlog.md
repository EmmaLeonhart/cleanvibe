# cleanvibe — Devlog

**This file is where "done" lives.** `queue.md` is delete-only: when a queue
item is finished, the item is **deleted from `queue.md`** and a dated entry
is **appended here**, in the same commit as the work, then pushed. Never
tick a box in place — a checked box left in `queue.md` is the failure mode
this file exists to prevent.

Releases (tag + a one-line note) and notable milestones also live here, so
this is the chronological narrative of the project, complementary to (but
denser than) `git log`. Newest entries at the bottom.

**Every cleanvibe-scaffolded project gets the same `devlog.md` convention.**
`cleanvibe new` writes one with a starter "project scaffolded" entry;
`cleanvibe convert` and `cleanvibe clone` inject one with a "backfill from
`git log`" instruction so existing repos catch their own devlog up to
present before normal work resumes; `cleanvibe replicate` writes one for
the replication project. This repo's devlog is dogfooding the convention.

See `CLAUDE.md` § "Workflow Rules" and `queue.md`'s preamble.

---

## 2026-02-14 — Bootstrap

`cleanvibe` repo is born. Initial commit (`49f30c5`) drops a bootstrap
`CLAUDE.md`; the package itself (`0382812`) lands the same day — the repo
that bootstrapped itself. `pyproject.toml` build backend is corrected
(`bca9202`) so `pip install -e .` works.

## 2026-02-15 — v0.1.x line: PyPI publishing + Windows fixes

- **v0.1.0** (`c05c038`) — GitHub Actions workflow for PyPI trusted publishing.
- **v0.1.1** (`b53eb5e`) — drop obsolete notes file.
- **v0.1.2** (`1cedec1`) — remove legacy `new-repo.bat` (`cleanvibe` is the
  single entry point now).

## 2026-02-21 — v0.1.3: Windows launch fix

- **v0.1.3** (`e998e25`) — Windows launch uses `cwd=` instead of `cd /d`,
  and opens Explorer on `cleanvibe new` so the user sees their new project
  immediately.

## 2026-03-06 — v0.1.4: Windows `runclaude.bat` + testing guidance

- **v0.1.4** (`b96e463`) — every Windows-scaffolded project gets a
  `runclaude.bat` (double-click to launch Claude in the project), and
  CLAUDE.md template gains testing guidance.

## 2026-03-19 — v0.2.0: `cleanvibe convert`

- New `cleanvibe convert` subcommand turns an existing directory into a
  cleanvibe project in-place (two commits: existing files, then injected
  scaffold). Missing-only injection — never overwrites.
- **v0.2.0** (`10c8275`).

## 2026-04-09 — v0.2.1: planning rule flipped to *pro*-planning

- The CLAUDE.md template originally discouraged elaborate planning; reality
  showed the opposite — agents need a written plan to survive context
  resets. Replaced anti-planning guidance with pro-planning guidance.
- **v0.2.1** (`283cfbb`).

## 2026-04-18 — Replication-skill v0.1 (separate project, soon to be absorbed)

- A sibling project `replication_skill` lands here as Claude-chat artifacts
  and a v0.1 arXiv paper scaffolder (`8e87146`), plus a `papers.json` index
  and bulk downloader (`3945ba1`). This work will later be absorbed into
  cleanvibe as the `replicate` subcommand.

## 2026-05-13 — v0.3.0–v0.4.0: queue.md + bootstrap queue

- **v0.3.0** (`18a12fb`) — `queue.md` ships in the scaffold; CLAUDE.md gains
  the "plan-into-queue first, then execute" workflow rule. CI workflow
  added with cross-platform test matrix (`57ef168`).
- **v0.3.1** (`c37e351`) — informative initial commit message; the repo
  starts dogfooding its own `queue.md`.
- **v0.4.0** (`955f5e9`) — every new project ships with a default
  first-session bootstrap queue (triage data_lake → infer project →
  interview user → write real queue → push to GitHub → work).

## 2026-05-13 — v0.5.0: `todo.md` long-horizon backlog

- **v0.5.0** (`eda1e42`) — inserts a `todo.md` step into the bootstrap
  sequence so the long-horizon picture exists before the concrete queue is
  written. Items flow `todo.md` → `queue.md` → done. Repo dogfoods its own
  `todo.md`.
- First PR merged (`46ffd47`, #1).

## 2026-05-16 — v0.6.0: `data_lake/.gitkeep` from commit 1

- **v0.6.0** (`293733f`) — the scaffold eagerly creates `data_lake/.gitkeep`
  (in `create_project` and convert/clone injection) so the directory exists
  from the first commit. A user can drop files into `data_lake/` *before*
  the bootstrap session ever runs.

## 2026-05-16 — Subtree-merge `replication_skill` into cleanvibe

- `replication_skill` is sunset as a standalone project and subtree-merged
  into cleanvibe (`df3979d`) so the replication work and the scaffold work
  share a codebase.

## 2026-05-16 — v0.7.0: `cleanvibe replicate` subcommand

- arXiv fetch ported into `cleanvibe/arxiv.py` using stdlib `urllib` only
  (`0af851e`) — preserves the zero-dependency guarantee.
- Accepts `alphaxiv.org` links too (`9e7dee5`).
- Replication-project templates land as inline `string.Template` constants
  (`7f9014b`); no package data.
- `cleanvibe/replicate.py` (`5b8d549`) + CLI wiring (`4240b41`); tests
  (`e451b59`) monkeypatch `fetch_paper` so no network is needed.
- Disposition note kept (`54199c9`): absorb replication_skill into
  cleanvibe; keep the reference corpus under `docs/replication-examples/`.
- **v0.7.0** (`82eba7e`) — documents `cleanvibe replicate`; finishes the
  replication integration.

## 2026-05-16 — v1.0.0: clone reworked, GitHub Pages site, Stability contract

- `cleanvibe clone` is reworked into *codebase onboarding* (`008275c`):
  dedicated `cleanvibe-onboarding` branch, default branch untouched,
  clone-specific templates (`6c59ad5`), CLAUDE.md/queue.md *prepended*
  (never overwritten), no `data_lake/`, no README injection.
- Tests cover clone end-to-end with a local-temp-repo source — no network
  (`8244b80`).
- Static GitHub Pages site lands under `site/` with an Actions deploy
  workflow (`15dec28`).
- **v1.0.0** (`fd8fd48`) — clone onboarding docs, Stability contract, site
  link. First 1.x release.

## 2026-05-16 — Grokking worked example + apex landing page

- The first end-to-end replication worked example: Grokking (arXiv:2201.02177)
  is locked as the target (`7269199`) and a real replication is produced
  via `cleanvibe replicate` (`e903f9a`). The site links the Grokking
  example from the Replicate tab (`646fdbc`).
- `cleanvibe.emmaleonhart.com` subdomain site added (`0b31c39`), sharing
  the visual identity used across the constellation of projects.

## 2026-05-16 — devlog.md feature planned

- Failure mode observed: agents kept *ticking off* `queue.md` items in
  place (`[x]`, "DONE") instead of deleting them, so the queue rotted into
  a half state-snapshot. Fix specced into `queue.md`: introduce `devlog.md`
  as the canonical home for completed work. Finishing a queue item =
  delete from `queue.md` + append a dated entry to `devlog.md` + commit +
  push. Spec lands as `c57c79f` and is then made fully resumable with
  explicit DONE/TODO markers (`273b46c`) so a fresh session can pick it up
  with no chat context.

## 2026-05-16 — v1.1.0: devlog.md ships across all scaffolds + PyPI build fix

- `devlog_md()` template added (`cleanvibe/templates.py`); `queue_md`,
  `claude_md`, `todo_md`, the clone templates, and the replication
  templates all reference the devlog rule.
- `create_project`, `_inject_scaffold` (convert), `clone_project`, and
  `replicate_project` now all write `devlog.md` (clone/convert get the
  "backfill from git log" variant; new/replicate get the fresh starter
  entry).
- Tests extended in `test_scaffold.py`, `test_clone.py`, `test_replicate.py`
  — devlog presence, content, and the "backfill" instruction for the
  existing-repo variant. 30/30 green locally.
- **PyPI publish build fix**: the v1.0.0 release's Publish-to-PyPI job
  failed at "Build package". Reproduced locally — setuptools flat-layout
  auto-discovery was picking up sibling directories `site/` and `pages/`
  as candidate packages, refusing to build with "Multiple top-level
  packages discovered". Fixed in `pyproject.toml` with an explicit
  `[tool.setuptools] packages = ["cleanvibe"]`. Local
  `python -m build` now produces both sdist and wheel cleanly. This unblocks
  v1.1.0 reaching PyPI.
- This repo's own `devlog.md` (this file) backfilled from `git log` —
  dogfooding the same convention every scaffolded project now ships with.
- **v1.1.0** tagged and pushed (`c0a57e9`).

## 2026-05-16 — v1.1.1: default branch is `main`, Python 3.9 CI fixed

Two follow-on bugs surfaced immediately after v1.1.0:

- **CI was red on Python 3.9** (all three OSes; 3.13 green). Root cause:
  `cleanvibe/cli.py` used `argv: list[str] | None` at function definition
  time without `from __future__ import annotations`. PEP 604 union (`X | None`)
  and PEP 585 generics (`list[str]`) are evaluated immediately on 3.9.
  Fix: add `from __future__ import annotations` to cli.py so annotations
  become strings. (`templates.py` and `arxiv.py` already had it.)
- **Scaffolded repos came up on `master`** because `git init` honours the
  user's `init.defaultBranch` config, which is still `master` on many
  installs. This was breaking downstream tooling that assumed `main`.
  Fix: `_git_init` and `convert_project`'s git-init call now pass
  `-b main` explicitly (requires git ≥ 2.28). New tests assert the
  initial branch is `main` for both `cleanvibe new` and `cleanvibe convert`.
- 32/32 tests green locally. v1.1.0 tag stays in place (immutable); this
  ships as **v1.1.1**.

## 2026-05-16 — Consolidated the GitHub Pages site (removed stale `site/`)

- The repo briefly had two site directories: a stale top-level `site/`
  (`index.html`/`style.css`/`tabs.js`, the original draft) and the canonical
  `pages/` (`index.html`/`identity.css`/`CNAME` → cleanvibe.emmaleonhart.com,
  the only one `.github/workflows/pages.yml` deploys, carrying the shared
  visual identity). Removed the stale `site/` so there is exactly one clear,
  good Pages site.
- Fixed the root `CLAUDE.md` architecture block, which still pointed at the
  old `site/` path, to reference `pages/`.
- Left intentional: the `site/` references inside the *replication* templates
  and the Grokking worked-example workflow — that is the per-replication
  project's own site, a different context.

## 2026-05-16 — `cleanvibe new` on a non-empty dir prompts (no longer errors)

- Was: `cleanvibe new PATH` printed an error and `sys.exit(1)` if the target
  existed and was non-empty. Now it prompts.
- `cleanvibe/cli.py`: added a testable prompt seam — `_ask()` (wraps
  `input()`), `_confirm()`, `_suggest_name()` (append `-2`, `-3`, … until
  free, only ever *suggested*). The `new` handler, on a non-empty existing
  dir: under `--dry-run` it never calls `input()` (prints the prompt it
  would show + a `convert_project(dry_run=True)` preview); otherwise it asks
  yes/no — **yes** = `convert_project()` in place (reuses convert: commit 1
  existing files, commit 2 scaffold, then launch), **no** = ask for a
  different name (suggested, blank accepts; falls back if the chosen name is
  also non-empty), then `create_project()`.
- Preserved the deliberate asymmetry: `replicate` silently auto-numbers
  (user supplied no name); `new` only ever *prompts* (the user chose the
  name on purpose) — it never silently renames.
- `tests/test_cli_new_prompt.py` added: yes→2 commits like convert,
  no→typed name, no+blank→suggested `-2`, and `--dry-run` provably never
  blocks on input. 36/36 tests green locally.

## 2026-05-16 — v1.2.0: `cleanvibe new` non-empty-dir prompt

Minor release bundling the prompt feature above. Version bumped
`1.1.1` → `1.2.0` (`cleanvibe/__init__.py`, `pyproject.toml`); full suite
green (36/36); pushed to `origin/master`. No tag/release here — release
cutting is handled by the separate scheduled job.

## 2026-05-16 — CI/CD repointed from `master` to `main`

GitHub's default branch was switched to `main` (via `gh repo edit
--default-branch main`; `origin/main` == old `origin/master`). The repo's
workflows still triggered on `master`, so nothing would run on `main`:

- `.github/workflows/ci.yml` — `push.branches` and `pull_request.branches`
  `[master]` → `[main]`.
- `.github/workflows/pages.yml` — `push.branches` `[master]` → `[main]`
  (Pages deploy of `pages/` → cleanvibe.emmaleonhart.com).
- `.github/workflows/publish.yml` — untouched: `on: release: [published]`,
  no branch dependency, already correct.
- Left intentionally: generated workflow templates (`templates.py`, the
  Grokking example) already use `[main, master]` — they fire on `main`;
  `master` is a harmless fallback for downstream scaffolded projects.
  Historical/explanatory `master` mentions in `devlog.md`, `CLAUDE.md`, and
  test names are records, not operational — left as-is.

All three workflow YAMLs validate; suite green. `master` is now used for
nothing in this repo's CI/CD.
