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

## 2026-05-18 — v1.2.1: anti-"honest" writing rule in scaffolded CLAUDE.md

Patch release. Added a `## Writing` section to all three generated
CLAUDE.md templates (`claude_md`, `clone_claude_md`,
`replication_claude_md` in `templates.py`) plus this repo's own
`CLAUDE.md`: *do not use "honest"/"honesty"/"honestly" — aggressively
overused; pick a more precise word.* Also scrubbed the existing literal
"honest" occurrences out of `templates.py` (clone onboarding + clone
queue), `claude.md`, and `README.md` (→ "accurate") so the word stops
propagating into every new project. Version `1.2.0` → `1.2.1`
(`cleanvibe/__init__.py`, `pyproject.toml`); full suite green (36/36);
tagged `v1.2.1` and GitHub release cut.

## 2026-05-19 — v1.2.2: strengthened anti-"honest" Writing rule

Patch release. The scaffolded `## Writing` rule in all three generated
CLAUDE.md templates (`claude_md`, `clone_claude_md`,
`_REPLICATION_CLAUDE_TMPL`) and this repo's own `CLAUDE.md` now uses the
strengthened wording: also bans the substitute coats
("frank"/"frankly", "candid"/"candidly", "transparently") and requires
naming a failure as a failure rather than haloing it. Supersedes the
milder v1.2.1 wording that recommended "frank"/"candid". Version
`1.2.1` -> `1.2.2` (`cleanvibe/__init__.py`, `pyproject.toml`); full
suite green; tagged `v1.2.2` and GitHub release cut (PyPI publish).

## 2026-05-19 — `replicate` arXiv/alphaxiv link parsing made robust

The "arXiv link replication isn't really working" report. Root cause:
`parse_arxiv_id` only accepted `arxiv|alphaxiv.org/(abs|pdf|html)/<id>`.
AlphaXiv's *primary* URL form is `/overview/<id>` (and arXiv also has
`/forum/`, versioned ids, trailing slugs, query strings), all of which
raised `ValueError` — which propagated as a raw traceback, not a usable
error.

- `cleanvibe/arxiv.py`: rewrote `parse_arxiv_id` — if the input is any
  arxiv/alphaxiv URL, extract the first id-shaped token from anywhere in
  it (path view no longer constrained); otherwise the strict bare-id path
  is unchanged. Added `is_arxiv_ref()` so callers can cleanly distinguish a
  paper reference from a folder name (used next by the folder-drop mode).
- `tests/test_arxiv.py`: regression tests for alphaxiv `/overview/`
  (plain + versioned), arXiv `/forum/`, query/fragment, old-style
  `cs.LG/0701001` via abs URL, garbage rejection, and `is_arxiv_ref`
  discriminating folder names from refs. Full suite 38/38 green.

## 2026-05-19 — `cleanvibe replicate` folder-drop (manual) mode

`cleanvibe replicate` now takes *either* an arXiv/alphaxiv reference *or* a
folder name. If the argument doesn't parse as an arXiv ref
(`is_arxiv_ref`), it is treated as a folder and a **manual drop-in**
replication project is scaffolded — no metadata fetch, no
`download_paper.py`, no `paper.json`, no network. The user drops the paper
PDF(s) into `replication_target/` and supporting material into
`data_lake/`; the scaffolded CLAUDE.md / queue.md / SKILL.md / README.md
say this up front, and queue step 1 makes the agent **STOP and ask** if no
PDF is present rather than invent a paper.

- `cleanvibe/templates.py`: `replication_manual_claude_md`,
  `replication_manual_queue_md`, `replication_manual_skill_md`,
  `replication_manual_readme_md` (+ `_manual_name`). Reuses
  `REPLICATION_GITIGNORE` (the dropped PDF stays gitignored — papers are
  copyrighted, local input), the Pages/package workflow constants, and
  `devlog_md`.
- `cleanvibe/scaffold.py`: `_write_if_missing` — non-destructive injection
  so running on a folder that already has the dropped paper / a custom
  README never clobbers it.
- `cleanvibe/replicate.py`: `replicate_manual_project()` — mkdir +
  non-destructive scaffold; commits into an existing git repo or git-inits
  a fresh one; dry-run support.
- `cleanvibe/cli.py`: dual-dispatch on the single positional `target`
  (renamed from `arxiv`); arXiv ref -> `replicate_project`, else
  -> `replicate_manual_project`. Help text + module docstring updated.
- `tests/test_replicate.py`: manual tree (no arXiv artifacts),
  non-destructive injection, gitignored PDF, dry-run, and CLI dispatch
  both ways. Full suite 44/44 green.

## 2026-05-19 — v1.3.0: robust replicate links + folder-drop mode

Minor release bundling the two changes above (the user report: "the
arXiv link replication thing is not really working, and the pipeline
should also work from just a folder you dump PDFs into"):

- **Fix:** `parse_arxiv_id` accepts any arxiv/alphaxiv URL path
  (alphaxiv's primary `/overview/`, `/forum/`, versioned, slug/query) —
  previously only `abs|pdf|html`, and the failure surfaced as a raw
  traceback.
- **Feature:** `cleanvibe replicate <folder>` manual drop-in mode — no
  fetch, no `download_paper.py`/`paper.json`, non-destructive; the user
  supplies the paper(s) by hand and the scaffold says so up front.
- Docs updated: `README.md` (both replicate modes + corrected Stability
  contract — `paper.json`/`download_paper.py` are arXiv-mode-only),
  `CLAUDE.md` (dual-mode architecture decision), `todo.md` (landed note).
- Version `1.2.2` -> `1.3.0` (`cleanvibe/__init__.py`,
  `pyproject.toml`); full suite 44/44 green; tagged `v1.3.0` and GitHub
  release cut (PyPI publish runs on release).

## 2026-05-22 — replicate arXiv parsing: DOI form + version preservation

User report: `cleanvibe replicate https://arxiv.org/abs/2605.20919` (their
own paper, "Sutra") threw errors, and several link forms should work —
including `doi.org/10.48550/arXiv.<id>`, `arxiv.org/{pdf,html,src}/...`,
alphaxiv `/abs|overview|audio/...`, and versioned ids.

- `cleanvibe/arxiv.py`: new `split_arxiv_ref()` returns `(bare_id,
  version)`. Detection broadened from "host is arxiv/alphaxiv.org" to also
  cover the arXiv DOI prefix (`10.48550/arXiv.<id>`, which `doi.org` links
  use — they contain no `arxiv.org/`) and `arXiv:<id>` citation style. The
  DOI form previously raised `ValueError` and was mis-routed to manual
  folder mode. The `vN` version is no longer silently dropped: `ArxivPaper`
  gains a `version` field and an `id_with_version` property; `fetch_paper`
  queries the pinned version when given one and otherwise resolves it from
  the response's canonical `<id>`. `parse_arxiv_id` stays version-agnostic
  (still used for directory naming).
- `cleanvibe/replicate.py`: `paper.json` now records `version` and
  `id_with_version`.
- `cleanvibe/templates.py`: replication `html_url` uses the exact version
  (`arxiv.org/html/<id>vN`).
- `tests/test_arxiv.py`: regression tests for the DOI form, `arXiv:`
  style, every URL form from the report, version preservation via
  `split_arxiv_ref`, and version resolved from the atom `<id>`. Suite green.

## 2026-05-22 — replicate: arXiv 429 retry/backoff + HTML-first download

The recurring failure in the user report: arXiv returns 429 (sometimes
503) under load and `fetch_paper` did a single `urlopen` with no retry, so
the user got raw tracebacks ("constant 429 errors").

- `cleanvibe/arxiv.py`: `_read_url()` retries 429/503 with exponential
  backoff from a ~3s base, honouring a numeric `Retry-After` header; it
  also retries transient `URLError`s and, after exhausting retries on a
  rate-limit, raises a clear `RuntimeError` instead of a traceback. The
  `sleep` callable is injectable so tests don't wait. API base switched
  `http://` -> `https://export.arxiv.org/api/query`.
- `cleanvibe/templates.py`: the generated `download_paper.py` now fetches
  the arXiv **HTML** first (`arxiv.org/html/<id>vN` ->
  `replication_target/paper.html`) because it reads far better than the PDF
  for structured-text work (per user preference), with the PDF kept as a
  fallback/complete record. Both gitignored. Same Retry-After backoff; the
  HTML fetch is optional (not every paper has HTML — a 404 is tolerated).
- `tests/test_arxiv.py`: network-free `_read_url` tests — retries 429 then
  succeeds (asserting it backed off), raises `RuntimeError` after
  exhaustion, and does not retry a non-transient 404. Suite green.
- Verified live: the DOI form now fetches over https (Sutra v1), and the
  rendered `download_paper.py` compiles with an HTML-first plan.

## 2026-05-22 — replicate templates: "follow the authors' recipe first" step

User ask: many recent papers ship a reproduction script or agent skill, so
the replicate queue should look for and follow that *before* reimplementing.

- `cleanvibe/templates.py`: added a prominent step 4 ("Check for an existing
  replication recipe — and follow it first") to both the arXiv
  (`_REPLICATION_QUEUE_TMPL`, `_REPLICATION_SKILL_TMPL`) and manual
  (`replication_manual_queue_md`, `replication_manual_skill_md`) templates,
  right after "find the authors' code". It enumerates what to look for —
  `REPRODUCE*.md` / `reproduce.*` / `replicate.*` / `run.sh`, a Makefile
  reproduce target, Dockerfile, Colab, a "Reproducing the results" README
  section, and agent recipes (`SKILL.md` / `AGENTS.md` / `.claude/` /
  `.cursor/`), plus paperswithcode / release assets — and says to run it
  first and only fall through to independent reimplementation if there's no
  recipe or it fails. Remaining steps renumbered; the reimplement step now
  reads "reimplement (or adapt the authors' code from step 4)".
- HTML-first folded into the templates too: queue/SKILL acquire-the-paper
  steps now fetch `paper.html` (preferred) + `paper.pdf` and work from a
  `paper.md` extraction; the arXiv CLAUDE.md architecture lists
  `paper.html` as the preferred source.
- `tests/test_replicate.py`: assert the recipe-first step and the HTML
  preference appear in the generated queue/SKILL/download_paper.py (both
  modes). Full suite 53/53 green.

## 2026-05-22 — default replication target + gitignored live-scratch dir

- **arXiv:2605.20919 ("Sutra", the maintainer's own paper) is now the
  documented default paper** for exercising `cleanvibe replicate`
  end-to-end. Recorded in `CLAUDE.md` along with the full regression set of
  link forms the parser must accept.
- **`tests/scratch/` is a gitignored sandbox** for live `replicate` runs
  (added to `.gitignore`). The committed unit tests stay network-free
  (they monkeypatch `fetch_paper`); live runs that actually hit arXiv land
  in `tests/scratch/` and are never committed. `CLAUDE.md` documents the
  exact `python -m cleanvibe.cli replicate … tests/scratch/… --no-claude`
  invocation.

## 2026-05-22 — live smoke test: `replicate` on Sutra, end-to-end

Ran `python -m cleanvibe.cli replicate https://arxiv.org/abs/2605.20919
tests/scratch/replicating-sutra --no-claude` against the real arXiv API.

- Scaffolded a clean replication project; `paper.json` recorded
  `version: 1` and `id_with_version: 2605.20919v1`; the generated `queue.md`
  carries the recipe-first step 4.
- Ran the generated `download_paper.py`: it fetched the arXiv **HTML**
  first (`paper.html`, 359 KB) and then the **PDF** (`paper.pdf`, 515 KB)
  into `replication_target/` — the HTML-first behaviour and live download
  both work, no rate-limit hit this run.
- Confirmed all reported link forms (DOI `10.48550/arXiv.<id>`, versioned
  `…v1`, alphaxiv `/overview/`) route to arXiv mode, not folder mode.

## 2026-05-22 — v1.4.0: robust replicate link parsing, 429 resilience, recipe-first

Bundles the day's work (user report: `cleanvibe replicate
https://arxiv.org/abs/2605.20919` threw errors, the DOI/versioned forms
should work, the HTML is better than the PDF, the queue should follow an
authors' replication recipe first, and arXiv was returning constant 429s):

- **Parsing:** `split_arxiv_ref` handles every form — `arxiv.org/{abs,pdf,
  html,src}/<id>[vN]`, `alphaxiv.org/{abs,overview,audio,forum}/<id>[vN]`,
  the arXiv DOI (`doi.org/10.48550/arXiv.<id>`), `arXiv:<id>`, and bare ids.
  The `vN` version is preserved (`ArxivPaper.version` / `id_with_version`,
  `paper.json`).
- **429 resilience:** `fetch_paper`'s requests go through `_read_url`, which
  retries 429/503 with `Retry-After`-aware exponential backoff and raises a
  clear error instead of a traceback. API base now `https`.
- **HTML-first:** the generated `download_paper.py` fetches the arXiv HTML
  (preferred for structured text) before the PDF, with the same backoff.
- **Recipe-first:** both arXiv and manual replicate queue/SKILL templates
  gained a step to find and follow an existing reproduction recipe before
  reimplementing.
- **Default paper + sandbox:** arXiv:2605.20919 ("Sutra") documented as the
  default replication target; `tests/scratch/` gitignored for live runs.
- Version `1.3.0` -> `1.4.0` (`cleanvibe/__init__.py`, `pyproject.toml`);
  full suite 53/53 green; live smoke test passed. Merged to `main`
  (`6f0523c`), tagged `v1.4.0`, and GitHub release cut
  (https://github.com/EmmaLeonhart/cleanvibe/releases/tag/v1.4.0) — the
  Publish-to-PyPI workflow runs on release.

## 2026-05-22 — replicate: source-first downloader + recipe-first scaffold

The v1.4.0 live Sutra replication *worked but was wasteful* (user report): it
downloaded the HTML and had to hand-strip base64 figure blobs, reimplemented
all five claims from scratch, only noticed the paper's own reproduction recipe
late, and never pushed to a remote. Restructured the generated arXiv scaffold so
the efficient path is the default.

- **`cleanvibe/templates.py` `download_paper.py` template rewritten** to fetch
  the arXiv **LaTeX/e-print source** (`arxiv.org/src/<id>`) instead of the HTML.
  It saves the raw archive (`replication_target/arxiv-source.tar.gz`,
  gitignored), extracts the `.tex` to `replication_target/source/` (committed),
  and saves the PDF as a fallback. Handles all three arXiv source shapes
  (gzip-tar / single-gzip-tex / PDF-only) with stdlib `tarfile`/`gzip`, a
  path-traversal-safe `_safe_extract` (uses `filter="data"` on Python 3.12+,
  falls back on older), and prints candidate reproduction-recipe filenames.
  `_replication_subs` gained `src_url`; `REPLICATION_GITIGNORE` ignores the
  source archive + a downloaded `replication/*.zip` while keeping the extracted
  trees committed.
- **arXiv-mode queue/SKILL/CLAUDE/README templates restructured to recipe-first.**
  The highest-leverage step — find and run the authors' reproduction recipe
  (usually shipped right in the paper source, near the end) — now comes FIRST,
  before any deep paper analysis. A found recipe file is copied to
  `replication_skill.md`; a referenced replication zip is extracted into
  `replication/`. Then verify the recipe's output against the paper, **check
  ALL references in every run**, record `notes/claims.md` scoped to the gaps,
  and reimplement only what the recipe didn't cover. New early step: create a
  PUBLIC GitHub repo and push (`gh repo create --public --source=. --push`) so
  commits push and Pages/CI build as you go — the v1.4.0 run stayed local-only.
- **Manual drop-in templates** got the same principles (recipe-first framing,
  check ALL references, go-live-early, `replication_skill.md`/`replication/`).
- **`tests/test_replicate.py`**: `test_recipe_first_and_html_preference` ->
  `test_recipe_first_and_source_preference` (asserts source, not HTML, in the
  queue + downloader; recipe → `replication_skill.md`); new
  `test_download_paper_compiles_and_targets_source` (the generated downloader
  parses as valid Python and is source-first); manual recipe-first assertion
  loosened to the contiguous "replication recipe". Full suite **54/54** green.
- **Live smoke test** (Sutra, arXiv:2605.20919): the generated `download_paper.py`
  fetched and extracted the source (4 files; `paper.tex.body` 93 KB of clean
  LaTeX vs the old 359 KB base64 HTML), gitignored the tarball + PDF, committed
  `source/`, and was idempotent on rerun. Grepping the extracted `.tex`
  immediately surfaces the Reproducibility section: the authors' repo, a
  downloadable `sutra-replication-package.zip`, and a shipped `SKILL.md` — the
  exact recipe-first signal the new flow is built to catch up front.

## 2026-05-22 — v1.5.0: source-first + recipe-first replication

Minor release bundling the architecture work above. Version `1.4.0` -> `1.5.0`
(`cleanvibe/__init__.py`, `pyproject.toml`); full suite 54/54 green; live Sutra
smoke test passed. Pushed to `main` (`d545a91`), tagged `v1.5.0`, and GitHub
release cut (https://github.com/EmmaLeonhart/cleanvibe/releases/tag/v1.5.0) —
the Publish-to-PyPI workflow runs on release.

## 2026-05-22 — clawRxiv as a first-class replication source

User pointed at clawRxiv (clawrxiv.io) — a preprint repo for papers authored
autonomously by AI agents — noting it "differentiates the paper content,
abstract, and skill file" and "should have its own thing for a URL to it."
Confirmed via the live API (`/api/abs/<id>`): the JSON has separate `content`,
`abstract`, and `skillMd` fields. That separation is the purest recipe-first
case, so clawRxiv got its own `replicate` mode.

- **`cleanvibe/clawrxiv.py`** (new): `ClawrxivPaper` dataclass +
  `is_clawrxiv_ref` / `parse_clawrxiv_id` / `fetch_clawrxiv_paper` (stdlib
  `urllib`+`json`, light 429/503 retry — preserves the zero-dep guarantee).
  Accepts `clawrxiv.io/{abs,api/abs}/<id>` (with/without `www.`) and
  `clawrxiv:<id>`. clawRxiv ids are arXiv-shaped, so a **bare id stays arXiv**
  — clawRxiv needs an explicit signal.
- **`cleanvibe/templates.py`**: `clawrxiv_{claude,queue,skill,readme}_md` +
  `_clawrxiv_subs`. The queue is **skill-first**: go live early, run the skill
  recipe FIRST, verify it against the paper, check ALL references, fill only the
  gaps. Reuses the replication gitignore + workflow constants.
- **`cleanvibe/replicate.py`** `replicate_clawrxiv_project`: writes the paper
  content to `replication_target/source/paper.md` (committed) and, when
  clawRxiv ships a separate `skillMd`, the recipe to `replication_skill.md` at
  the root (otherwise the queue tells the agent to extract the recipe embedded
  in `paper.md`). `paper.json` records `source: "clawrxiv"` + `has_skill_file`.
  **No `download_paper.py`** — the API returns everything in one call.
- **`cleanvibe/cli.py`**: dispatch checks `is_clawrxiv_ref` **before**
  `is_arxiv_ref`, then manual. Help text + module docstring updated.
- **`tests/test_clawrxiv.py`** (new, network-free — monkeypatch
  `fetch_clawrxiv_paper`): id parsing, ref discrimination (clawRxiv vs arXiv vs
  folder), tree written, content→source/paper.md, skill present→
  `replication_skill.md` / absent→embedded, paper.json fields, skill-first
  queue, CLI dispatch both ref forms. Full suite **67/67** green.
- **Live smoke test**: `cleanvibe replicate https://www.clawrxiv.io/abs/2605.02609`
  scaffolded ROMO-CV — `paper.json` (`source: clawrxiv`, claw `DNAI-RomoCV-…`),
  content (19 KB) committed to `source/paper.md`; `skillMd` was null so the
  embedded-recipe path was exercised (no `replication_skill.md`, queue says
  extract).

## 2026-05-22 — Windows launcher renamed `runclaude.bat` → `!runClaude.bat`

User request: the Windows launcher should be `!runClaude.bat` — the `!` floats
it to the top of the file listing (easy to find) and camelCase reads cleanly.
(They wrote `.md`; confirmed it stays an executable `.bat` so double-click still
launches Claude — a `.md` can't.) Renamed at every write site in `scaffold.py`
(new/convert/clone) and `replicate.py` (arXiv/clawRxiv/manual) and in
`tests/test_scaffold.py`. Historical devlog entries keep the old name as a
record. Verified live: `cleanvibe new` writes `!runClaude.bat` with the correct
`@echo off / cd /d "%~dp0" / claude` body.

## 2026-05-22 — v1.6.0: clawRxiv source + `!runClaude.bat`

Minor release bundling the two changes above. Version `1.5.0` -> `1.6.0`
(`cleanvibe/__init__.py`, `pyproject.toml`); full suite 67/67 green; both live
smoke tests passed. Pushed to `main`, tagged `v1.6.0`, and GitHub release cut —
the Publish-to-PyPI workflow runs on release.

## 2026-05-22 — consent gate + scaffolder-side source extraction (commit 2)

User clarification on the replication flow: (1) the scaffolder's job isn't just
the framework commit — it should also do the source extraction as a **second
commit before launching Claude**, so the agent opens onto an already-extracted
paper; and (2) because replication **runs code the user didn't write**, the
generated `queue.md` must, as its first step, make the agent stop and get
**explicit user consent** before executing any cloned/recipe code.

- **`cleanvibe/replicate.py`**: `_run_extraction_commit(target)` runs the
  just-written `download_paper.py` and commits the extracted source as commit 2,
  **before** `_launch_claude`. Best-effort (network/arXiv failure → warns and
  leaves it for the agent), gated by a new `extract` param on `replicate_project`
  (`True` from the CLI; tests pass `False` to stay network-free). It's data
  download + tarball extraction by our own stdlib code — not third-party
  execution — so it is NOT consent-gated. The initial-commit message now points
  at `replication_target/source/`.
- **`cleanvibe/templates.py`**: a **consent gate** is now queue step 1 in both
  the arXiv (`_REPLICATION_QUEUE_TMPL`) and clawRxiv (`_CLAWRXIV_QUEUE_TMPL`)
  templates, and a prominent callout in the manual queue: STOP and get explicit
  user consent before running ANY external/cloned code; reading the
  paper/source/recipe is fine, *running* third-party code is gated. Reinforced
  in both SKILL plans. The arXiv queue's source step now says the scaffolder
  already extracted + committed it (with an offline fallback to
  `download_paper.py`); steps renumbered.
- **`todo.md`**: logged the future "automated safety scan of cloned/recipe code
  before running" enhancement (the consent gate is the interim measure).
- **Tests**: `_run` defaults `extract=False`; new tests assert the consent gate
  is queue step 1 (arXiv + clawRxiv) and that `extract=True/False`
  invokes/skips `_run_extraction_commit`; the arXiv dispatch test patches the
  extractor so the CLI default doesn't hit the network. Full suite **70/70**
  green.
- **Live**: `cleanvibe replicate <Sutra>` now produces two commits ("Initial
  commit: replication scaffold" + "Extract arXiv source (download_paper.py)")
  with `replication_target/source/` committed, before launch.

## 2026-05-22 — v1.6.1: consent gate + commit-2 source extraction

Patch release bundling the two changes above (user framed it explicitly as a
small v1.6.1, not a big release). Version `1.6.0` -> `1.6.1`
(`cleanvibe/__init__.py`, `pyproject.toml`); full suite 70/70 green; live smoke
test passed. Pushed to `main`, tagged `v1.6.1`, and GitHub release cut — the
Publish-to-PyPI workflow runs on release.

## 2026-05-22 — replicate from a non-arXiv URL (download a web page / PDF)

User ask: `cleanvibe replicate` should handle research that's **not** on
arXiv/clawRxiv — give it a plain URL and it downloads the page or PDF as the
replication source. Also fixed the stale editable install (`pip install -e .`)
so code run outside the repo uses this repo, not the old site-packages copy.

- `cleanvibe/cli.py`: a 4th `replicate` dispatch branch — after clawRxiv and
  arXiv, before folder mode — routes a plain `http(s)` URL
  (`_looks_like_url`) to the new `replicate_url_project`.
- `cleanvibe/replicate.py`: `replicate_url_project` downloads the URL into
  `replication_target/source/` (`paper.pdf` or `paper.html`, sniffed by
  extension/magic bytes via `_download_source`), records provenance in
  `source.json`, and scaffolds from the manual templates **parametrized with
  the source URL**. Reuses arXiv's 429-aware `_read_url` (retry/backoff).
  Download is best-effort: a failure still commits, and the queue tells the
  agent to flag it. `_slug_from_url` derives the directory name.
- `cleanvibe/templates.py`: the four `replication_manual_*` templates gained
  an optional `source_url` param. With it, the wording flips from "drop the
  paper in yourself / STOP and ask" to "the source was downloaded from
  <url> into `replication_target/source/`". Without it (folder mode) the
  output is byte-stable, so existing manual tests pass unchanged.
- `tests/test_replicate.py`: `TestReplicateUrl` (tree + `source.json`,
  URL-vs-manual wording, dry-run, `_slug_from_url`) and a CLI routing test —
  all network-free (`_download_source` mocked). Full suite 75/75 green.
- Live smoke test: `replicate https://example.com/` downloaded the page to
  `replication_target/source/paper.html` (528 B) and committed cleanly.

## 2026-05-22 — v1.6.2: replicate from a non-arXiv URL

Patch release for the change above (user: "tiny update so just up the last
number"). `cleanvibe replicate <http(s)-url>` now downloads non-arXiv
research (web page or PDF) into `replication_target/source/` and scaffolds
around it. Version `1.6.1` -> `1.6.2` (`cleanvibe/__init__.py`,
`pyproject.toml`); README documents the new URL form; full suite 75/75
green; live smoke test passed. Pushed to `main`, tagged `v1.6.2`, GitHub
release cut — Publish-to-PyPI runs on release.

## 2026-05-23 — v1.7.0: Emergency Stop Mode in the generated CLAUDE.md

Added an "Emergency Stop Mode" section to the CLAUDE.md template that
`cleanvibe` injects into every scaffolded project (`claude_md()` in
`cleanvibe/templates.py`), and to this repo's own CLAUDE.md. On a
continuous series of "stop" messages (or an explicit stop), Claude
force-kills all repo/session processes and GitHub Actions runs, does NOT
investigate or reverse anything, ignores repetitive messages for ~15-30
min, answers only direct questions from context (looking anything up counts
as a forbidden action), and resumes only when the user says "emergency stop
ended." Version 1.6.2 -> 1.7.0 (`cleanvibe/__init__.py`,
`pyproject.toml`). Tagged v1.7.0, GitHub release cut announcing it.

## 2026-05-23 — v1.8.0: "cron means local CronCreate" in the generated CLAUDE.md

Added a "Cron jobs and scheduled work — LOCAL by default" section to the
CLAUDE.md template (`claude_md()` in `cleanvibe/templates.py`) and to
this repo's own CLAUDE.md. It makes explicit that when the user says
"cron"/"cron job"/"schedule" generically they mean the in-session
`CronCreate` tool running locally on their machine while they are away
from the house -- NOT an OS crontab, CI `schedule:`, or cloud scheduler --
and that their absence is never a reason to delay or ask for confirmation
(standing consent; just set it up). Version 1.7.0 -> 1.8.0
(`cleanvibe/__init__.py`, `pyproject.toml`). Tagged v1.8.0, release cut.

## 2026-05-24 — v1.9.0: hourly status-report cron for extensive work

Added an "Hourly status-report cron for extensive work" section to the
CLAUDE.md template (`claude_md()` in `cleanvibe/templates.py`) and to this
repo's own CLAUDE.md. The default for any session involving relatively
extensive work — above all, a large-scale population of `queue.md` with
created tasks — is to run a local `CronCreate` job that fires every hour on
the hour with a status report, so an autonomous run can't silently lose the
thread of what it is doing. Lifecycle: the FIRST queue item kills the hourly
cron; the LAST TWO queue items, pinned at the tail, restart it and then run
an independent end-of-session summary. Entering planning mode also disables
the cron (its restart lives at the end of the queue).

Also wired the lifecycle into the bootstrap `queue_md()` template: a preamble
note, a bullet in the "replace this bootstrap queue" step about keeping the
tail section pinned, and a new headed `## Always last — restart the hourly
cron and summarize` section that stays pinned at the bottom of every queue.
This same section was rolled out across the top-level project CLAUDE.md files
in the Github workspace. Version 1.8.0 -> 1.9.0 (`cleanvibe/__init__.py`,
`pyproject.toml`). Full suite green; tagged v1.9.0, release cut.

## 2026-05-24 — v1.9.1: fix Python 3.9 import (templates.py)

`cleanvibe/templates.py` was missing `from __future__ import annotations`, so
the `str | None` parameter annotations on the manual-replication template
functions (`replication_manual_{claude,queue,skill,readme}_md`) were evaluated
at import time and raised `TypeError: unsupported operand type(s) for |` on
Python 3.9 — breaking `import cleanvibe.templates` (and therefore `cli.py`)
entirely on 3.9, despite `requires-python = ">=3.9"`. This had been red in CI
on the 3.9 matrix legs since the manual templates landed (v1.7.0/v1.8.0 CI was
already failing on 3.9; the v1.9.0 release inherited it). Added the future
import (deferring all annotations to strings), matching the convention already
documented in CLAUDE.md and already present in `cli.py`/`arxiv.py`. Version
1.9.0 -> 1.9.1 (`cleanvibe/__init__.py`, `pyproject.toml`). Tagged v1.9.1,
release cut.

## 2026-05-24 — v1.10.0: generated projects actually START the hourly cron

v1.9.0 shipped the hourly-status-report *vision* into the generated templates
but never wired the cron to fire: a freshly scaffolded project's bootstrap
sequence had no step that creates the `CronCreate` job, and the pinned tail
said "**restart** the hourly cron" when nothing had ever started one. So on a
real `cleanvibe new` run the hourly reports never happened. v1.10.0 makes the
vision real and reconciles the lifecycle so "start" and "kill-first" stop
contradicting:

- **`cleanvibe/templates.py` `queue_md()`** — new bootstrap **step 1**: *"Start
  the hourly status-report cron"* (`CronCreate`, every hour on the hour); the
  existing steps 1–7 renumbered down to 2–8. The preamble note and the pinned
  `## Always last` section reworded so a fresh session **starts** the cron up
  front and the tail **ensures it is still running** + summarizes, while a
  mid-session re-fill **kills** it up front and the tail **restarts** it. Item A
  of `## Always last` changed from "Restart the hourly updates cron job" to
  "Ensure the hourly status-report cron is running — start it if this session
  never did, restart it if a planning burst / queue re-fill killed it." The
  "Replace this bootstrap queue" step now tells the agent the real queue's FIRST
  item should start the cron (or kill it on a re-fill) with the tail pinned.
- **`claude_md()`** § "Hourly status-report cron for extensive work" — replaced
  the one-line "the FIRST queue item is always: kill the cron" sequencing (which
  is nonsensical on a fresh session with no cron yet) with an explicit (a)–(d)
  lifecycle: (a) START at the beginning of extensive work; (b) a mid-session
  large-scale re-fill kills the already-running cron first, tail restarts;
  (c) planning mode disables it; (d) the last two pinned items ensure-running +
  summarize.
- **This repo's own `CLAUDE.md`** got the same (a)–(d) lifecycle correction
  (dogfooding).
- **`tests/test_scaffold.py`** — two new tests: the bootstrap queue's opening
  step starts the hourly cron (before triage), and `claude_md()` mentions
  *starting* the cron at the beginning, not only killing/restarting. Full suite
  **77/77** green (was 75).
- This session dogfooded the lifecycle: a `CronCreate` hourly status-report cron
  was started up front, the seven queue items worked top to bottom, and the
  pinned `## Always last` items close it out.

Version `1.9.1` -> `1.10.0` (`cleanvibe/__init__.py`, `pyproject.toml`); tagged
`v1.10.0`, GitHub release cut (Publish-to-PyPI runs on release).

## 2026-05-24 — v1.10.1: queue the replication-report status badge; cron is new-mode-only

Queued (in `queue.md` `## Active`, pinned above the `## Always last` heartbeat)
the work to make the `cleanvibe replicate` GitHub Pages findings report
legible: a big color-coded status badge — green "Replicated" / red "Failed to
replicate" / amber "Insufficient hardware to replicate" / blue "In progress"
(default in-progress, driven by a `status` field in `paper.json`) — plus a
structured, styled (non-black-and-white) theme, replacing today's bare
`pandoc FINDINGS.md` output.

Also codified in `CLAUDE.md` § "Hourly status-report cron for extensive work"
that the hourly cron is **`new`/general work only** — the `cleanvibe replicate`
templates deliberately omit it (a replication is a bounded, single-purpose
workflow). Already true in the templates; the note prevents a future session
from adding it back. This is a planning/docs release — the report feature
itself is spec'd in the queue, to be implemented next. Version `1.10.0` ->
`1.10.1` (`cleanvibe/__init__.py`, `pyproject.toml`); tagged `v1.10.1`,
release cut.
## 2026-05-26 — v1.11.0: three-cron playbook + self-update mechanism

Generalized the productivity loop in the generated `CLAUDE.md` / `queue.md`
templates, and added a self-update pointer so existing cleanvibe-scaffolded
projects can pick up new sections without being re-scaffolded.

- **`claude_md()`** — replaced the single "Hourly status-report cron for
  extensive work" section with **"Autonomous productivity loop — the
  three-cron playbook"**: work-loop at :03 (sync, take top `queue.md` item or
  promote from `todo.md`, hard rails, commit + push, one-line report),
  auto-flush at :15 (commit + push pending work, no empty commits),
  status-report at :42 (heartbeat, reporting only). Lifecycle (fresh-session
  start, mid-session re-fill kill, planning-mode disable, pinned-tail
  restart) carries over verbatim, just generalized from one cron to three.
  This was already empirically the most productive shape in Yantra; v1.11.0
  promotes it into the default.

- **`claude_md()`** — added **"Check cleanvibe for skill updates (weekly)"**.
  Every generated `CLAUDE.md` now carries three fields: the cleanvibe version
  that generated it, the date of the last update check, and the canonical
  updates URL (`https://cleanvibe.emmaleonhart.com/updates.md`). The
  instruction: weekly, `WebFetch` the updates page; fold in any sections
  introduced after the generating version; bump the version + date.
  Opportunistic — fetch failures silently roll over.

- **`queue_md()`** — bootstrap step 1 now starts the three-cron set (not just
  the status-report cron); preamble references the playbook; `## Always last`
  pinned-tail items ensure all three crons are running.

- **`pages/updates.md`** — new file, deployed at
  `cleanvibe.emmaleonhart.com/updates.md` via the existing `pages.yml`
  workflow. Hand-maintained index of every section / skill keyed by the
  cleanvibe version that introduced it. The canonical source the CLAUDE.md
  self-update mechanism fetches.

- **`tests/test_scaffold.py`** — `test_bootstrap_queue_starts_hourly_cron`
  renamed to `test_bootstrap_queue_starts_three_crons` and expanded to
  assert all three crons are named in the bootstrap queue with their cron
  strings (`3 * * * *`, `15 * * * *`, `42 * * * *`). New test
  `test_claude_md_has_weekly_update_check_section` asserts the self-update
  section is in every generated CLAUDE.md.

- **Replication templates remain exempt** (v1.10.1 codification); replication
  CLAUDE.md still uses the single, simpler structure.

Companion changes outside cleanvibe (same dated work, separate repos): the
new `claude_md()` sections were propagated by hand into the existing CLAUDE.md
of Yantra (added the update-check section; the three-cron playbook was
already there in Yantra-specific form), Sutra (upgraded from single
status-report cron to the three-cron playbook, added the update-check
section), and TradingThing (same upgrade as Sutra).

Version `1.10.1` -> `1.11.0` (`cleanvibe/__init__.py`, `pyproject.toml`).

## 2026-05-26 — v1.11.0 follow-up: dev-install convenience + namespace-shadowing note

While verifying the v1.11.0 ship I confirmed an existing quirk:
`pip install -e .` from this repo lands `cleanvibe` in the editable
finder, but the finder gets registered AFTER `PathFinder` in
`sys.meta_path`. When Python is invoked from this repo's *parent*
directory (e.g. `C:\Users\…\Documents\Github`), `PathFinder` scans
CWD (sys.path[0] = `''`), finds the repo directory `Github/cleanvibe/`
as a candidate, treats it as a **namespace** package (no `__init__.py`
at the repo root), and never reaches the editable finder. Result:
`import cleanvibe` succeeds but the module has no `__version__`,
no `__file__`, and the package code never loads.

The CLI (`cleanvibe.exe`, the console-script entry point) is unaffected
because the launcher resolves through the entry-point dispatch, not
through arbitrary-CWD `import`. The bug only bites programmatic
`import cleanvibe` from one specific parent directory.

The root cause is structural — the repo dir name equals the package
name, which is a recipe for CWD-shadowing under editable installs.
Fixing it properly would mean renaming either the repo or the package.
Both are too invasive for what is, in practice, a "don't use `-e .`"
issue.

What landed today:

- **README.md "Developer install" section** — tells contributors to use
  `pip install .` (or `!dev-install.bat`), not `pip install -e .`, and
  explains why in one paragraph.
- **`!dev-install.bat`** — a one-line convenience that runs
  `python -m pip install .` from the repo root. `!` floats it to the
  top of the file listing (same prefix convention as `!runClaude.bat`).
- No code change. The fix is documentation + a clearer dev workflow,
  not a setuptools or templates change.

Independently verified during this session: the v1.11.0 wheel installs
clean (`pip install .` from `cleanvibe/`), `cleanvibe --version` prints
`1.11.0` from every tested CWD (including the previously-broken
`Documents/Github` parent), and `python -c "import cleanvibe"` from
that parent CWD now resolves to the site-packages copy with
`__version__ == '1.11.0'`.

## 2026-05-28 — v1.11.1: retry socket read timeouts in arXiv / clawRxiv fetch

User report: `cleanvibe replicate https://arxiv.org/abs/2605.20919` died with
a raw `TimeoutError` traceback from `ssl.py` -> `socket.recv_into` partway
through the arXiv API call. The retry loop in `cleanvibe/arxiv.py` (and
`clawrxiv.py`, and the generated `download_paper.py` template) caught
`urllib.error.HTTPError` for 429/503 and `urllib.error.URLError` for transient
connection errors — but socket-level read timeouts surface as plain
`TimeoutError` (3.10+) or `socket.timeout` (3.9), **neither of which is a
subclass of `URLError`**. So the timeout bypassed the retry loop entirely and
the user got a traceback instead of a retry. (HTTP 429s were already covered
in v1.4.0; this is the missing parallel case for read timeouts.)

- **`cleanvibe/arxiv.py` `_read_url`** and **`cleanvibe/clawrxiv.py`
  `_read_url`**: added `(TimeoutError, socket.timeout)` (module-level
  `_TIMEOUT_ERRORS`) to the transient-error except clause alongside
  `URLError`. Bumped the default `timeout` from 15s to 30s — arXiv's
  Atom endpoint can be slow under load, and the v1.4.0 retry/backoff
  only helps if the first attempt actually returns *something* rather
  than hanging out the whole timeout window.
- **`cleanvibe/templates.py`** `download_paper.py` template: same fix
  in the generated `_get()`, so every freshly scaffolded replication
  project picks up the retry. Logs the retry reason (`transient error
  (...); retrying in Ns`) so a user staring at a slow download knows
  why it's pausing.
- **`tests/test_arxiv.py`**: `test_retries_socket_timeout` exercises
  both `TimeoutError` and `socket.timeout` via `subTest`, asserting the
  call is retried instead of propagating. Full suite **79/79** green
  (was 77).
- Version `1.11.0` -> `1.11.1` (`cleanvibe/__init__.py`,
  `pyproject.toml`).
