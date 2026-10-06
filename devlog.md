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

## 2026-05-29 — v1.12.0: `cleanvibe research` (original-research mode)

A fifth project mode alongside `new` / `clone` / `convert` / `replicate`:
`cleanvibe research <name>` (also `cleanvibe new <name> --research [--question Q]`).
It is `new` for *your own* investigation — not a replication of someone else's
paper — so it keeps everything `new` has (`data_lake/`, the three-cron
playbook, `todo.md`->`queue.md`->`devlog.md`) and borrows two things from
`replicate`:

1. **An up-front literature review (agentic RAG)** as the distinctive bootstrap
   step, committed under `literature/` (`REVIEW.md` + sources), done *before*
   any building — what separates `research` from a plain `new` project.
2. **A published, themed GitHub Pages report** under `docs/` — committed
   `index.html` with a warm "paper" light theme + dark-mode variant (adapted
   from latent-space-cartography / http://latent-space.emmaleonhart.com/), plus
   `docs/report.pdf` built from `FINDINGS.md` by `.github/workflows/pages.yml`.

The bootstrap queue is literature-review-first: start crons -> triage
`data_lake/` -> define the research question (interview) -> **literature
review** -> write `todo.md` -> go **public** on GitHub (required for free Pages)
-> replace the bootstrap queue with the real experiment/build queue -> work it,
keeping `FINDINGS.md` + the `docs/` report current. Research is extensive work,
so — unlike replication, which is exempt — it KEEPS the three-cron playbook.

- **`cleanvibe/research.py`** (new): `research_project(path, question, dry_run,
  no_claude)` — mirrors `create_project` but research-flavored (`data_lake/`,
  `literature/`, themed `docs/`, `pages.yml`, git init on `main`, launch Claude).
- **`cleanvibe/templates.py`**: extracted `_CLAUDE_CORE_RULES` /
  `_WRITING_SECTION` / `_common_claude_tail(date)` so `claude_md` (`new`) and
  `research_claude_md` share the workflow/cron/update-check/emergency-stop text
  **without drift**. Added `research_{claude,readme,queue}_md`,
  `research_index_html`, `RESEARCH_GITIGNORE`, `RESEARCH_PAGES_YML`, and the
  themed `_RESEARCH_INDEX_HTML` (filled via `str.replace` of
  `__PROJECT_NAME__`/`__QUESTION__`/`__DATE__` — its CSS is full of `{` and `$`,
  so neither f-strings nor `string.Template` are safe).
- **`cleanvibe/cli.py`**: `research` subcommand (`--question`/`--dry-run`/
  `--no-claude`) + a `--research` flag on `new` that routes to the same handler.
- **`tests/test_research.py`** (new, 17 tests): expected tree, lit-review-before-
  building ordering, research-question step, three-cron playbook, public-repo/
  Pages step, themed `docs/index.html`, `pages.yml` deploys `docs/` + builds PDF,
  CLAUDE.md research sections, `--question` threading, `new`-without-`--research`
  regression. Full suite **96/96** green (was 79).
- Version `1.11.1` -> `1.12.0` (`cleanvibe/__init__.py`, `pyproject.toml`).

## 2026-05-29 — v1.13.0: one shared report theme for research + replication (+ status badge)

Made the v1.12.0 research report theme the **default cleanvibe report theme for
both** `research` and `replicate`, and finished the long-standing "prettier
replication reports with a status badge" queue item in the same pass.

- **`templates.CLEANVIBE_REPORT_CSS`** (new): single source of truth for the
  theme — warm "paper" light theme + dark-mode variant (from
  latent-space-cartography) + color-coded `.status-badge` classes. `research`
  inlines it into `docs/index.html`; `replicate` writes it to a committed
  `report-theme.css`.
- **`REPLICATION_PAGES_YML`** rewritten: was bare `pandoc FINDINGS.md -s`
  (black-and-white, no structure). Now it renders the FINDINGS body with pandoc,
  wraps it in the shared theme + a **big color-coded replication status badge**
  (🟢 replicated / 🔴 failed / 🟠 insufficient-hardware / 🔵 in-progress) in a
  self-contained `site/index.html`, and still builds `report.pdf`. The verdict
  is read (`jq`) from a **`status` field in `paper.json`** (default
  `"in-progress"`), so it can't drift from a stray string.
- **`replicate.py`**: `_paper_json` / `_clawrxiv_paper_json` now emit
  `status: "in-progress"`; all four replicate modes (arXiv / clawRxiv / URL /
  manual) write `report-theme.css`. Replication CLAUDE/README/SKILL/queue
  templates document the `status` field + allowed values + the themed report;
  the site-shape exemplar switched from `sutra` to `latent-space.emmaleonhart.com`.
- **Tests**: +5 (theme shared between modes, `report-theme.css` written, badge +
  status wiring, `paper.json` status default, generated Pages YAML themed). Full
  suite **101/101** green (was 96). Verified both generated Pages workflows parse
  as YAML.
- Version `1.12.0` -> `1.13.0` (`cleanvibe/__init__.py`, `pyproject.toml`).

## 2026-05-29 — v1.13.1: Pages workflows auto-enable GitHub Pages (deploy no longer 404s)

Real-world bug, caught on the first live research project (`reservoiragent`): the
`pages` workflow built + uploaded the artifact fine, but **`actions/deploy-pages`
failed with `HttpError: Not Found (404)` — "Ensure GitHub Pages has been
enabled"**. Root cause: GitHub Pages was never enabled with Source = "GitHub
Actions" for the repo. The old templates only documented that as a manual
one-time `Settings -> Pages` toggle (a TODO comment), so any freshly scaffolded
repo whose owner forgot the toggle had its very first deployment fail.

Fix: both `RESEARCH_PAGES_YML` and `REPLICATION_PAGES_YML` now run
`actions/configure-pages@v5` with `enablement: true` in the build job, which
**turns Pages on via the API automatically** (the `pages: write` permission is
already granted). No manual Settings step anymore — the only requirement is that
the repo is public. Updated the workflow header comments, the research bootstrap
"go live" step, and the replication CLAUDE deliverables note (the stale "TODO
markers / set Settings -> Pages" wording was now inaccurate). Added tests
asserting `configure-pages` + `enablement: true` are wired into both workflows.
Full suite **101/101** green; both generated workflows verified to parse as YAML.

- Version `1.13.0` -> `1.13.1` (`cleanvibe/__init__.py`, `pyproject.toml`).

---

## 2026-05-30 — v1.14.0: Workflow behaviors become standalone skills

The reusable workflow prose that had been inlined into every generated
`CLAUDE.md` (Workflow Rules, Writing, Cron-is-local, the three-cron playbook,
the weekly update check, Emergency Stop) is now **six standalone skills**, the
single source of truth being `cleanvibe/skills.py` (`SKILLS` dict +
`write_skills()`). Slugs: `emergency-stop`, `cron-is-local`, `autonomous-loop`,
`queue-driven-workflow`, `writing-style`, `cleanvibe-update-check`.

- `skills.py` materializes each skill to `.claude/skills/<slug>/SKILL.md`.
  `new` / `convert` / `clone` / `research` all call `write_skills()`; the
  generated `CLAUDE.md` now carries only a short `## Skills` pointer (a fresh
  scaffold's CLAUDE.md dropped from ~120 lines to ~20). Replication modes are
  left as-is (bounded workflow, already exempt from the cron tail).
- `templates.py`: removed the inlined `_CLAUDE_CORE_RULES` / `_WRITING_SECTION` /
  `_common_claude_tail` blocks; added `SKILLS_POINTER`.
- `cleanvibe-update-check` is **redefined**: instead of folding new sections into
  `CLAUDE.md`, it now refreshes `.claude/skills/` to the latest shipped versions.
- `pages/updates.md`: new v1.14.0 entry describing the six skills + the migration
  path; the "how to read" intro now keys on skills, not CLAUDE.md sections.
- New `migrate_repos_to_skills.py`: back-fills the skills into existing repos
  (sync ff-only, write skills, trim CLAUDE.md, commit + push; skips dirty /
  diverged repos). This repo dogfoods its own `.claude/skills/`.
- Tests: `tests/test_skills.py` (skill set, frontmatter, write tree) and
  `tests/test_migrate.py`; scaffold/research tests updated to assert the new
  pointer + vendored skills shape. Full suite green.

- Version `1.13.1` -> `1.14.0` (`cleanvibe/__init__.py`, `pyproject.toml`).

---

## 2026-06-05 — v1.15.0: copyright fix — the paper is NEVER committed

**Bug (serious):** `cleanvibe replicate` was **committing the paper** into the
generated repo. The gitignore only excluded the PDF/HTML/tarball, while the
extracted arXiv LaTeX `source/`, the clawRxiv `paper.md`, and the downloaded
URL source were all committed — and the arXiv scaffolder had a dedicated
"commit 2" (`_run_extraction_commit`) that downloaded, extracted, **and
committed** the e-print source before launch. That redistributes a copyrighted
work in every replication repo. The whole point of `download_paper.py` is the
opposite: deterministically drop the paper into a **gitignored** directory so it
provides local context without ever being committed.

**Fix — the contract is now uniform across all four replicate modes:**
- `REPLICATION_GITIGNORE` ignores the **entire** `replication_target/` tree
  (`replication_target/*` + `!replication_target/.gitkeep` — the `/*` form, not
  bare `replication_target/`, so git can still re-include `.gitkeep`; an
  outright-ignored directory can't have a child re-included).
- `replicate.py`: `_run_extraction_commit` → `_run_extraction` — it still runs
  `download_paper.py` before launch so the agent opens onto an extracted paper,
  but it **commits nothing**. The arXiv initial-commit message and dry-run text
  were corrected (no more "commit 2").
- **clawRxiv and URL modes gained a `download_paper.py`** so an empty
  `replication_target/` is always repopulatable without committing the paper:
  `clawrxiv_download_paper_py` re-fetches `content` from the clawRxiv API;
  `url_download_paper_py` re-downloads from the URL recorded in `source.json`.
- Submodule guidance now uses `git submodule add -f …` (the path is gitignored;
  only the gitlink/.gitmodules are committed — never the paper).
- Every template's prose (CLAUDE/queue/SKILL/README + the `download_paper.py`
  docstrings) flipped from "source/ is committed" to "gitignored, local context
  only; run `download_paper.py` if empty". Manual drop-in mode was already
  correct (paper dropped in by hand, gitignored).

**Tests:** new assertions that nothing under `replication_target/` is
git-tracked after scaffold (`git ls-files` / `git check-ignore`) for arXiv,
clawRxiv, and URL modes; stale `replication_target/*.pdf`-only gitignore
assertions and the clawRxiv `paper.md`-committed assertion updated; the
extraction-helper test renamed to match `_run_extraction`. Full suite green
(109 passed). An offline simulation confirmed end-to-end that a populated
`replication_target/source/paper.md` + `paper.pdf` stays untracked while
`.gitkeep` is tracked. (Live arXiv smoke deferred — arXiv was timing out.)

- Version `1.14.0` -> `1.15.0` (`cleanvibe/__init__.py`, `pyproject.toml`).

## 2026-06-11 — v1.16.0: `cleanvibe original` — research with a topic-finding loop

A sixth mode: **`cleanvibe original <name>`** (also `cleanvibe new <name>
--original [--area FIELD]`). It is `cleanvibe research` for the case where the
**topic is uncertain** — you don't yet have a fixed research question.

- **`cleanvibe/original.py`** (`original_project(path, area, dry_run, no_claude)`)
  mirrors `research_project` and adds a committed `topics/.gitkeep`. It reuses the
  research deliverables wholesale: `RESEARCH_GITIGNORE`, `RESEARCH_PAGES_YML`,
  `CLEANVIBE_REPORT_CSS`, and the `_RESEARCH_INDEX_HTML` shell.
- **The distinctive bootstrap step is a topic-finding loop** (queue step 3, before
  the literature review): explore the focus area with agentic search/RAG, draft a
  slate of candidate research questions, score them (novelty / tractability /
  interest / available data-compute / what a result is worth), confirm the
  shortlist with the user, and converge on ONE — recording candidates + scoring +
  the chosen question + rationale in `topics/TOPICS.md`. Then it proceeds exactly
  like `research` (literature review → experiments → published findings). It keeps
  everything `research` has, including the three-cron playbook (original research
  IS extensive work).
- **The seed is an `--area` (a field), not a `--question`** — the question is what
  the loop discovers. At scaffold time the question is always a placeholder
  (`_ORIGINAL_QUESTION_PLACEHOLDER`, "not yet chosen…"); the area falls back to
  `_ORIGINAL_AREA_PLACEHOLDER` ("open…") when omitted.
- **Templates** (`templates.py`): `original_{claude,readme,queue,index_html}` +
  `_topic_area` helper. **CLI** (`cli.py`): `original` subparser with `--area`, a
  `new --original` alias routed through a shared `_do_original` handler (checked
  before `--research`).
- **Tests:** `tests/test_original.py` (19 tests) — tree incl. `topics/`,
  topic-finding-before-literature-review ordering, three-cron playbook,
  public-for-Pages, themed/shared-theme docs, the topic-finding question
  placeholder, CLI dispatch + `new --original` alias, `--area` threading. Full
  suite green (128 passed).
- Version `1.15.0` -> `1.16.0` (`cleanvibe/__init__.py`).

## 2026-06-11 — v1.16.0 live smoke test

Scaffolded a real `cleanvibe original` project into the gitignored
`tests/scratch/original-smoke` (`--no-claude`): the tree is correct including
the committed `topics/.gitkeep`, and `git ls-files` confirms `topics/` +
`literature/` + `docs/index.html` are tracked. Verified the bootstrap queue
ordering — topic-finding loop (step 3) precedes the literature review (step 4)
precedes `todo.md` (step 5). Then launched Claude into the scaffold to work it
for real.

## 2026-07-01 — v1.17.0: not-done taxonomy + strict-order note in generated CLAUDE.md

_(Backfilled 2026-09-26 from `git log`; the release shipped without a devlog
entry.)_

- `d332abf` — replaced the single-bucket "deliberately not done / blocked on
  Emma" phrasing in the bundled `autonomous-loop` skill (`cleanvibe/skills.py`
  + `.claude/skills/autonomous-loop/SKILL.md`) with six disjoint tags:
  NEEDS-DECISION / BLOCKED-ON-USER-ACTION / BLOCKED-ON-EXTERNAL /
  NEEDS-INVESTIGATION / UNSAFE-TO-GUESS / OUT-OF-SCOPE. The commit message also
  says it appended the strict-order note to this repo's `CLAUDE.md`, but it did
  not touch that file (fixed 2026-09-26, below).
- `7211978` — `templates.py` now emits a "Long command series run in strict
  order" section and the not-done taxonomy in every generated `CLAUDE.md`.
- **v1.17.0** (`de736a3`) — version bump + tag.

## 2026-07-28 — v1.17.1: the scaffolded attribution URL was a 404

Every project cleanvibe scaffolds stamped `https://github.com/Immanuelle/cleanvibe`
into it, and that URL returns **404 with no redirect** — the repo now lives at
`EmmaLeonhart/cleanvibe`. So the attribution link in generated `CLAUDE.md`,
`README.md`, `SKILL.md`, and the generated HTML footer pointed users at nothing,
as did the `Homepage` and `Issues` metadata on the PyPI page and the `git clone`
line in our own README. The `User-Agent` the arxiv and clawrxiv clients send
carried the dead URL too, which is the one place a remote operator would look to
find out who is calling them.

Fixed across 9 files: `pyproject.toml`, `README.md`, and the seven modules that
emit the URL (`arxiv`, `clawrxiv`, `original`, `replicate`, `research`,
`scaffold`, `templates`). 128 tests green.

Deliberately not changed: the `LICENSE` copyright holder and the `pyproject`
author name both read "Immanuelle". Those are a name, not a broken link —
changing a copyright line is Emma's call, not a bug fix. The historical planning
docs under `docs/superpowers/` keep their old local paths, being a record of what
was done at the time.

Version `1.17.0` -> `1.17.1`. Not released — `publish.yml` fires on a published
GitHub release, so cutting one is Emma's call.

## 2026-09-26 — Bookkeeping drift since v1.16.0

The Active queue was empty, and checking it turned up records that no longer
matched the code:

- Backfilled the missing v1.17.0 devlog entry (above, in date order).
- Added the "Long command series run in strict order" and "Not-done taxonomy"
  sections to this repo's `CLAUDE.md`, using the text `templates.py` generates.
  `d332abf` said it had done this and had not.
- `CLAUDE.md`'s live-smoke paragraph still said `replication_target/source/` is
  "(committed)". That has been wrong since v1.15.0, when the whole directory
  became gitignored. It now says local-only.
- `queue.md`'s pointer said version `1.16.0`; now `1.17.1`.

Docs only, no code change.

## 2026-09-26 — Every mode launches Claude with a starting prompt

Emma asked that every mode's session open with a prompt saying it was started
with cleanvibe and what the mode is for. `templates.starting_prompt(mode)` builds
it from a per-mode summary (`new`, `convert`, `clone`, `research`, `original`,
`replicate`, `replicate-manual`, `chat`). Each prompt ends: read CLAUDE.md and
queue.md, work item 1, and ask with AskUserQuestion first if the goal is
unclear. The last clause follows Emma's stated direction that cleanvibe should
lean toward asking the user.

- `scaffold._launch_claude(path, prompt)` passes it as Claude's initial prompt:
  `cmd /k claude "<prompt>"` on Windows, `execlp("claude", "claude", prompt)`
  elsewhere. All nine launch sites pass their mode's prompt.
- The single `RUNCLAUDE_BAT` constant is replaced by `runclaude_bat(mode)`. A
  relaunch from `!runClaude.bat` re-orients the session the same way.
- The prompt goes through cmd.exe and batch, so `starting_prompt` raises if a
  summary contains `" % ^ & | < > !` or a newline.
- Tests: `tests/test_starting_prompt.py` (7), plus a `.bat` content check in
  `test_scaffold.py`. 135 passed.

## 2026-09-26 — Every mode defaults to a private repo

Emma changed her mind on public-by-default. Every mode now assumes a private
GitHub repo.

- About 40 passages in `templates.py` across the replicate (arXiv, clawRxiv,
  URL, manual), research and original templates no longer say "create a PUBLIC
  repo (required for free Pages)". Every `gh repo create` is `--private`.
  `new` was already private.
- Research/original go-live step (bootstrap step 6) now has the agent ask the
  user with AskUserQuestion whether to make the repo public now, later, or
  never, and not change visibility without that answer.
- **Workflow fix this change required.** On the free plan, a Pages deploy from
  a private repo fails, so every push would have gone red. Both Pages workflows
  now gate `configure-pages`, `upload-pages-artifact` and the `deploy` job on
  `!github.event.repository.private || vars.CLEANVIBE_PAGES == 'true'`. They
  always upload the built report as a plain `report` workflow artifact, so a
  private repo still gets its PDF and site. A paid plan turns on Pages for a
  private repo with the repo variable `CLEANVIBE_PAGES=true`.
- Tests: new `tests/test_private_default.py` (no template text may say
  `--public`; both workflows carry the gate 3 times and always upload the
  report). The research/original "goes public" tests were rewritten to assert
  `--private` and the AskUserQuestion step. 137 passed.
- CLAUDE.md Key Decisions + README updated.

Not verified: the workflow gate has not run on a real private repo yet. The
expression and the `report` artifact are checked by unit tests only.

## 2026-09-26 — `cleanvibe chat`: a git-tracked conversation mode

Emma asked for a new mode: a git-tracked, agentic conversation about one topic,
research-heavy and light on code, in a private repo. It should start by asking
what the user is trying to do and keep the session logs in git.
`cleanvibe chat [NAME] [--topic T]` (`cleanvibe/chat.py`).

- **Scaffold:** ask-first `CLAUDE.md`; a `queue.md` whose item 1 is asking the
  user what they are trying to do (AskUserQuestion) and item 2 is creating a
  private repo; `devlog.md`, `notes/`, `sessions/`, `data_lake/`, skills, the
  `chat` starting prompt. NAME is optional and defaults to `chat-YYYY-MM-DD`,
  auto-suffixed.
- **Session logs:** `.claude/settings.json` runs the committed stdlib script
  `.claude/hooks/save_session_log.py` on Stop (after each response) and
  SessionEnd (also pushes if there is an upstream). It saves the raw `.jsonl`
  plus a readable `.md` into `sessions/` and commits only `sessions/`, leaving
  anything else staged alone. It always exits 0.
- The renderer was checked against this session's real transcript first.
  Claude Code stores user messages sent mid-turn as `queued_command`
  attachments, not `user` entries, so the script handles both.
- The strict-order + not-done-taxonomy block is now a shared `BEHAVIOR_RULES`
  constant used by both `new` and `chat`.
- **Tests:** `tests/test_chat.py` (15). This includes running the hook script
  for real against a fake transcript: rendering, commit contents, idempotence,
  push without an upstream, and bad input. 152 passed under `unittest`.
- **Live smoke test (Windows):** scaffolded `tests/scratch/chat-smoke` and ran
  `claude -p "Reply with just the word pong."` in it. The Stop and SessionEnd
  hooks each committed a session log, and the `.md` holds the exchange.

Interpretation calls for Emma to confirm or correct:
- The raw `.jsonl` is committed as well as the `.md`. It is complete but large
  (this session's was 1.3 MB) and holds everything, including tool output and
  environment details. Dropping the raw file is a one-line change.
- Session logs are committed automatically by the hook, not by the agent.
- "Remote control starts, no name needed": read as making NAME optional. No
  remote-control launch flag was added.
- Chat mode has no three-cron playbook (it is conversational, not extensive
  autonomous work) and no Pages report.

## 2026-09-26 — v1.18.0 docs + version

- README: new "Chat — a git-tracked conversation" section, an "Every mode:
  private repo, starting prompt" section, `chat` in Options and Stability
  (plus its guaranteed files).
- `pages/index.html`: a `cleanvibe chat` card; the stability blurb said
  "currently v1.2.0", now v1.18.0. The site still has no `research` or
  `original` cards; left for the wider refresh Emma mentioned.
- `pages/updates.md`: a v1.18.0 entry. No skill bodies changed. It warns that
  an older generated `pages.yml` on a private repo will fail its Pages deploy
  until it gets the new `if:` gate.
- Correction: the chat entry above first said `test_chat.py` has 17 tests; it
  has 15.
- Version `1.17.1` -> `1.18.0` (`cleanvibe/__init__.py`, `pyproject.toml`).
  Not released: `publish.yml` fires on a published GitHub release, so that is
  Emma's call. 152 tests pass.

## 2026-09-26 — CLAUDE.md: the missing "Hourly status-report cron" section

`queue.md`'s header and its pinned "Always last" items pointed at a `CLAUDE.md`
section, "Hourly status-report cron for extensive work", that did not exist.
Emma chose to write it rather than drop the reference. It summarizes the
`autonomous-loop` skill (the source of truth): when the crons apply, the three
staggered crons (work-loop :03, auto-flush :15, status report :42), and the
start / kill / disable / restart lifecycle. It also notes that "the hourly
status-report cron" is this repo's older name for what is now the third of the
three crons.

## 2026-09-26 — Refresh stale claims (site, README, CLAUDE.md, updates page)

Emma picked "refresh stale bits". Each claim was checked against the code, not
reworded; the wider general-purpose rework is later today.

- **Website (`pages/index.html`)**
  - Added the missing `research` and `original` cards.
  - `new` card: it said `new` writes `todo.md`; it doesn't (the first session
    writes it). It now also lists `data_lake/` and the skills.
  - `replicate` card: it said the paper is "the submodule target". The paper is
    downloaded locally and gitignored; the submodule is the authors' code. The
    card now also covers clawRxiv, other URLs, drop-in folders and the consent
    gate.
  - Stability section: it listed four subcommands and included `todo.md` in the
    guaranteed set, contradicting the README. Now all seven, and the set
    matches.
  - "What it is": it said the behavior lives in CLAUDE.md; it has lived in
    skills since v1.14.0. It now also mentions private-by-default and the
    starting prompt.
- **README:** same fix to the intro. The `new` steps list now includes
  `devlog.md`, `data_lake/`, `!runClaude.bat` and the starting prompt. The
  skills paragraph now names `original`/`chat` and says `replicate` doesn't get
  skills.
- **`pages/updates.md`:** the scope line now includes `original` and `chat`.
- **CLAUDE.md:** the website was described as `site/` with tabs; it is `pages/`
  with cards. The `research` decision named `_CLAUDE_CORE_RULES` helpers that
  v1.14.0 removed.

## 2026-09-26 — `cleanvibe doctor`: read-only drift audit

The `todo.md` item, which Emma picked after a session spent fixing drift by
hand. `cleanvibe doctor [PATH]` (`cleanvibe/doctor.py`) runs eight read-only
checks: `files`, `skills`, `queue-done`, `version`, `devlog-tags`,
`section-refs`, `ci`, `pages-gate`. It exits 0 when clean, 1 with findings, 2
on a bad path.

- **It found a generator bug on its first run.** `new`, `research` and
  `original` projects have pointed their `queue.md`/`todo.md` at CLAUDE.md
  sections ("Workflow Rules", "Queue and longer-horizon work", "Autonomous
  productivity loop") since v1.14.0, which moved those sections into skills.
  The 17 references in `templates.py` (and this repo's own `queue.md`/`todo.md`)
  now name the skill. `pages/updates.md` tells existing projects how to fix
  theirs.
- **First run also had false positives, all mine.** Every release tag was
  reported missing, because the pattern rejected `v0.1.0` (the `v` counted as
  a word character before the number). Fixed; the test covers `v1.10.0` vs
  `1.10.0.1` and `v11.1.0`.
- **Dogfooding found one more doctor bug.** Before commit, doctor flagged its
  own documentation: the section-name pattern could span lines, so one stray
  quote swallowed a paragraph. It is now single-line only, with a test.
- No `--fix`: none of the findings has a fix safe to apply without a human
  looking.
- Tests: `tests/test_doctor.py` (14), including "a fresh scaffold of every mode
  audits clean", which is what keeps the generator honest. 166 pass. Doctor on
  this repo: no drift.
- Docs: README section + Options + Stability, a site card, CLAUDE.md
  architecture + Key Decision. Removed from `todo.md`.

## 2026-09-26 — `cleanvibe chat` starts with Remote Control

Asked what "remote control starts, you don't need a name" meant, Emma chose
"launch with Remote Control". So a chat session now starts as
`claude "<prompt>" --remote-control`, unnamed, and chat's `!runClaude.bat` does
the same. Other modes are unchanged (`REMOTE_CONTROL_MODES = {"chat"}`).

- The flag goes after the prompt. `--remote-control [name]` takes an optional
  value, so `claude --remote-control "<prompt>"` would make the prompt the
  session name. Checked against the real CLI (2.1.283):
  `claude -p "Reply with just the word pong." --remote-control` answered
  "pong". That covers argument parsing only; an interactive Remote Control
  session was not opened from here.
- Tests: 4 more in `tests/test_starting_prompt.py` (argv order, chat-only
  `.bat` flag, launcher, `chat_project` passes `remote_control=True`). 170
  pass.

## 2026-09-26 — Released v1.18.0

Emma chose to release. Created GitHub release **v1.18.0** on `c4d59fc` (CI
green on all 6 OS/Python jobs). `publish.yml` succeeded, and PyPI now lists
1.18.0.

It ships everything since v1.17.0: chat mode (with Remote Control),
`cleanvibe doctor`, starting prompts, private-by-default with the gated Pages
workflows, the generated-reference fix, the site/README refresh, and the v1.17.1
attribution-URL fix, which was never released on its own.

Checked the published artifact rather than the checkout: in a fresh venv,
`pip install cleanvibe==1.18.0` → `cleanvibe --version` is 1.18.0,
`cleanvibe chat` scaffolds with `--remote-control` in its `.bat`, and
`cleanvibe doctor` finds that fresh chat project clean.

## 2026-09-26 — cleanvibe 2 — the spec (Emma, voice note)

Recorded here so the design survives outside the chat. Paraphrased from a long
speech-to-text note; the decisions are Emma's.

- **Why.** Sessions often start without a clear goal, and cleanvibe sessions go
  awry as a result. The 1.x modes are limited and constrained, so she ends up
  fighting the project structure. Skills stayed too rigid over time, and
  single-operation scripts pile up as crud.
- **cleanvibe 2.** Every session starts as a conversation that behaves somewhat
  like a chatbot. Assumptions are minimal at the start. The agent asks
  (AskUserQuestion) whenever the user isn't clear about what they want, and in
  the first session it asks a question based on the directory. It actively
  analyzes what the user seems to be trying to accomplish and may write its own
  documentation of that. Development and research practices are separate from
  this core.
- **CLI.** `cleanvibe new NAME` makes the directory and opens Claude in it.
  `cleanvibe new` with no name auto-generates the directory. `cleanvibe` with no
  arguments opens the current directory as a regular session if it is already a
  cleanvibe repo, and otherwise makes a new auto-named project. The 1.x modes run
  as `cleanvibe legacy <cmd>`, deprecated, with a clear flag/warning that saying
  so. `replicate` is **not** deprecated: it is a core, intentionally rigid,
  different use case and runs as before.
- **Starting prompt.** The first session is told the project was started with
  cleanvibe and that this is the first session in this path. It can guess the
  purpose from the path, otherwise it figures it out through conversation. An
  auto-generated name is flagged: the user gave no name, so the project is
  fresh. A resumed session gets a different message.
- **Sessions.** Always a proper session, never a child session, so transcripts
  are saved. (When a Claude session ran cleanvibe, the new session ran as its
  child and did not save its transcript.) Always Remote Control, so an agent can
  start a session and the person can pick it up.
- **Transcripts.** Copied into the repo persistently and always committed,
  roughly hourly, in raw and processed-markdown form. Markdown is easier for the
  agent to reference. Ideally this is done non-agentically, by a background
  process rather than the agent. It lets you audit what went on.
- **Repos.** Private, local git, committed regularly. By default it does not
  even push to GitHub.
- **Cron loop.** Needs updating. It is not split between legacy and v2; if it
  suits legacy modes less well, that is accepted. Agents got anxious and
  switched the hourly loop off, which should not happen.
- **Research.** `cleanvibe research` got used for semi-permanent research on
  topics that were not CS papers. The CS-paper-with-replication shape was too
  specific.
- **Practice.** Track the practice-project directory with a `.gitkeep`. Then
  implement everything as perfectly as possible, make a project, and open a
  session in it for Emma to experiment with.

## 2026-09-26 — v2 item 1: the launcher always starts a real top-level session

The bug Emma described, found in this session's own environment: every
process a Claude session starts inherits `CLAUDE_CODE_CHILD_SESSION=1`, the
session id, `CLAUDECODE`, `CLAUDE_PID`, the messaging socket, and the Remote
Control bridge id (`CLAUDE_CODE_BRIDGE_SESSION_ID`). A `claude` that cleanvibe
started from inside an agent therefore began life as that agent's child.

- New `cleanvibe/launch.py`. `clean_env()` drops those variables by exact name,
  plus any `CLAUDE_CODE_*` variable naming a session, socket, bridge, child,
  parent, entrypoint or execpath. It keeps user configuration such as
  `ANTHROPIC_API_KEY`, `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_GIT_BASH_PATH` and
  `CLAUDE_CODE_USE_BEDROCK`.
- Windows: a new console in a new process group that breaks away from the
  caller's job object, so it outlives the agent's shell call. If breakaway is
  refused, it falls back to a plain new console.
- Unix with a terminal: `execvpe` with the clean environment. Without one (an
  agent's shell), it writes a launch script that `unset`s the parent's session
  variables and opens it in a new macOS Terminal window or the first Linux
  terminal emulator found, otherwise prints the command.
- `scaffold._launch_claude` delegates to it, so every mode (legacy and
  `replicate` included) gets the fix.
- Tests: `tests/test_launch.py` (8); the old launcher tests moved there. 174
  pass. The real end-to-end check is item 9: launching Emma's practice session
  from this agent session.

## 2026-09-26 — v2 item 2: the default project (`cleanvibe/project.py`)

- `new_project(path, auto_named)` writes a minimal scaffold: `CLAUDE.md`,
  `README.md`, `INTENT.md`, the `.cleanvibe.json` marker, `.gitignore` with
  `scratch/`, `sessions/`, `data_lake/`, all skills, the session-log hooks and,
  on Windows, `!runClaude.bat`. It makes a local git repo on `main` with no
  remote and opens the first session with Remote Control on. There is
  deliberately no `queue.md`/`todo.md`/`devlog.md`; `queue-driven-workflow`
  adds them if the work turns into development.
- **CLAUDE.md (v2):** ask with AskUserQuestion when unclear; keep `INTENT.md`
  as a running analysis of what the user is trying to do (not a transcript);
  minimal assumptions; practices come from skills once the work takes a shape
  (`queue-driven-workflow`, `research-practice`, `autonomous-loop`); one-off
  scripts go in the gitignored `scratch/`, so they cannot pile up as crud;
  commit regularly, private, no remote unless asked; transcripts are saved by
  the hook, and the agent reads `sessions/*.md` to catch up.
- **Starting prompts:** `v2_first_prompt` says this is the first session in a
  new cleanvibe project at <path>, that the directory name is the main clue
  (or, when auto-named, that it says nothing because the user gave no name),
  to open by asking a question based on the directory with AskUserQuestion,
  and to keep `INTENT.md` updated. `v2_resume_prompt` says to catch up from
  `INTENT.md`, the newest session log and `queue.md`, then check what this
  session is for. A path containing a character cmd.exe would mangle is left
  out rather than breaking the launch.
- `is_cleanvibe_repo()` recognizes the v2 marker and 1.x projects (a CLAUDE.md
  that mentions cleanvibe, plus `queue.md` or vendored skills).
  `open_project()` resumes without popping an Explorer window.
  `auto_project_path()` gives `cleanvibe-YYYY-MM-DD`, suffixed `-2`, `-3`.
- Caught before commit: the `.bat` resume prompt read "project at . Catch up"
  (empty path). Fixed, with a test.
- Tests: `tests/test_project.py` (16). 190 pass.

## 2026-09-26 — v2 item 3: transcripts committed hourly by the hook, not the agent

Emma wanted transcripts committed roughly every hour, non-agentically, by a
background process rather than the agent. The hooks already run outside the
agent (Claude Code runs them). What changed is the timing:

- **Stop** (after every response): still copies the raw `.jsonl` and
  re-renders the `.md`, so `sessions/` on disk is always current. It commits
  only if the last commit touching `sessions/` is at least an hour old.
  `CLEANVIBE_LOG_COMMIT_SECONDS` overrides the interval.
- **SessionEnd** (`--push`): always commits, then pushes if there is an
  upstream (v2 projects have none by default).
- Anything else the agent commits with `git add -A` in between sweeps
  `sessions/` in too, so nothing is lost; the hook's own commit then has
  nothing left to do.
- Commit message is now `session log <stem>` (was `chat: session log`),
  because every v2 project uses the hook, not only chats.
- Tests: `test_chat.py` hook tests now run with interval 0, plus two new ones.
  Within the hour a Stop refreshes the files but does not commit; SessionEnd
  always commits.

## 2026-09-26 — v2 item 4: the cleanvibe 2 command line

`cleanvibe/cli.py` rewritten around Emma's spec:

- **`cleanvibe`** (no arguments): if the current directory is a cleanvibe
  project (the v2 marker, or a 1.x project), it opens a new session there with
  the resume prompt. Otherwise it creates an auto-named project in the current
  directory (`cleanvibe-YYYY-MM-DD`) and opens its first session. `--dry-run`
  and `--no-claude` work at the top level.
- **`cleanvibe new [NAME]`**: no NAME means auto-named. An existing cleanvibe
  project is opened, never overwritten. A non-empty directory that is not a
  project is refused (exit 2) with a pointer to `cleanvibe legacy convert`
  (no interactive prompt, so an agent calling it gets a clear answer). An
  empty directory is used.
- **`cleanvibe legacy {new,research,original,chat,clone,convert}`**: the 1.x
  modes, unchanged. They print a `DEPRECATED:` warning to stderr on every run.
- **The old top-level names** (`research`, `original`, `chat`, `clone`,
  `convert`) exit 2 with a message naming `cleanvibe legacy <cmd>`; they are
  hidden from `--help`.
- **`replicate` and `doctor` stay top-level and unchanged.**
- Legacy handlers and parsers moved into `_LEGACY_HANDLERS` /
  `_add_legacy_parsers`; `build_parser()` is separate from `main()`.
- Tests: new `tests/test_cli.py` (12). The 1.x CLI tests (research,
  original, chat, legacy-new prompt) now call `cleanvibe legacy ...`. 204 pass.

## 2026-09-26 — v2 item 5: skills — a calmer autonomous loop, a general research practice

- **`autonomous-loop` rewritten.** Emma: agents got anxious and switched the
  hourly loop off. The old text had a start / kill-on-refill /
  disable-in-planning / restart choreography, two items pinned to the queue's
  tail, and "HARD RAILS" / "LOAD-BEARING DEFAULT" language. The new text keeps
  the same three staggered crons (work :03, flush :15, status :42) and the same
  standards. It drops the choreography and says plainly: do not turn the crons
  off yourself (not for an empty queue, a failed tick, a replan or risk); only
  the user stops them; an idle tick is normal; problems go in the next status
  tick. Per Emma it is one loop for everything, legacy included.
- **New `research-practice` skill** for research on any topic, not only CS
  papers (Emma's complaint about `cleanvibe research`). It covers pinning the
  question down with the user, surveying wide then going deep, `research/SUMMARY.md` as
  a living answer with stated confidence and a dated "What changed" log for
  long-running inquiries, `research/sources.md` with source type and trust,
  claims tied to sources, and inference labelled as inference.
- **`queue-driven-workflow`** is now framed as the development practice. In a
  v2 project it creates `queue.md`/`todo.md`/`devlog.md` when the work turns
  into a multi-step build. CI arrives once the project has a remote, since v2
  repos start without one.
- The Skills pointer in every generated CLAUDE.md lists seven skills.
- **This repo:** vendored skills refreshed. The CLAUDE.md cron section is
  rewritten to match. `queue.md` loses its old lifecycle header note and the
  pinned "Always last" items.
- Known and accepted: the frozen 1.x bootstrap queues (`legacy new`,
  `research`, `original`) still describe the old start/kill choreography. Emma
  said the loop is not split for legacy, and legacy may fit it less well.
- Tests: `test_skills` expects seven skills. The cron tests now assert the new
  invariants ("do not turn the crons off yourself", "an idle tick is normal",
  no kill step) instead of the old wording. 204 pass.

## 2026-09-26 — v2 item 6: doctor understands cleanvibe 2 projects

A v2 project is minimal by design (no `queue.md`/`devlog.md` until the work
needs them), so doctor's `files` check would have flagged every fresh one. With
the `.cleanvibe.json` marker present it now requires `CLAUDE.md`, `README.md`,
`INTENT.md`, the marker, `.claude/settings.json` and
`.claude/hooks/save_session_log.py` (without the hook, sessions go
unrecorded). The other checks already skip files that don't exist. 1.x projects
are checked as before. `test_doctor`'s "every fresh scaffold audits clean" now
includes the v2 project; there is a new test for the v2 file set. 205 pass.

## 2026-09-26 — v2 item 7: `tests/scratch/.gitkeep` is tracked

Emma remembered the practice-project directory as "supposed to be git-kept";
it was not. `.gitignore` ignored `tests/scratch/` outright, which also stops
git from tracking a `.gitkeep` inside it. It now ignores
`tests/scratch/*` and re-includes `!tests/scratch/.gitkeep` (the same pattern
as `replication_target/`), so the directory exists in every clone and
everything scaffolded into it stays out of git. CLAUDE.md now describes it as
the sandbox for live runs of any mode, not only `replicate`. (Also corrected
the previous entry's test count: 205, not 206.)

## 2026-09-26 — Practice session hit Claude Code's trust prompt; pre-trust for new folders

**What happened.** `cleanvibe` (bare) in `tests/scratch/` created
`cleanvibe-2026-09-26` and launched its session from this agent session, the
child-session case the launcher fix targets. The launch worked: a new
`claude.exe` (PID 38744) started with the first-session prompt intact through
`cmd /k` (visible in its command line). But the session stopped at Claude
Code's "Is this a project you created or one you trust?" prompt, which blocks
every new folder's first interactive session until someone answers at the
machine (screenshot:
`Documents/claude-screenshots/cleanvibe_2026-09-26/practice-session-console.png`).
Until it is answered there is no transcript and no Remote Control. The earlier
`claude -p` smoke tests never showed this, because `-p` skips the trust prompt.

- Emma chose (AskUserQuestion) to have the prompt answered for her this time.
  `AppActivate`/`SendKeys` failed: there was no foreground window, most
  likely a locked screen. Writing the keypresses into the console input buffer
  was **denied by the auto-mode classifier**, which blocks one session driving
  another's terminal. Not pursued further. **The practice session is waiting
  for Emma to press "Yes, I trust this folder".**
- Emma also chose to have cleanvibe **pre-trust the folders it creates**. New
  `cleanvibe/trust.py`: `mark_trusted(path)` sets
  `projects[<abs path, forward slashes>].hasTrustDialogAccepted = true` in
  Claude Code's config (`~/.claude.json`, `$CLAUDE_CONFIG_DIR/.claude.json`,
  or `CLEANVIBE_CLAUDE_CONFIG`).
  - It only runs from `new_project`, only when about to launch; never on
    `open_project` or legacy modes.
  - It never creates the config file, and leaves it untouched if it is
    unreadable or an unexpected shape.
  - It writes a `.cleanvibe-backup` first, then replaces the file atomically.
  - A Claude session already running holds its own copy of the config and can
    write it back later, dropping the flag. The worst case is that the prompt
    appears as before.
- **Not verified live:** that Claude Code accepts a minimal entry holding only
  the trust flag (real trusted entries have 10+ fields). Deliberately not
  exercised against the real config from this session; it is the practice
  project's job, once Emma unblocks it or runs `cleanvibe new` herself.
- Emma then confirmed in chat: "trust new folders". Committed on that.
- Tests: new `tests/test_trust.py` (10), all on temporary config files. The
  test package points `CLEANVIBE_CLAUDE_CONFIG` at a temp file, and the
  launch-path test modules set it themselves too, because `unittest discover
  -s tests` does not import `tests/__init__.py`. Checked: the real
  `~/.claude.json` hash is identical before and after the full suite. 215
  pass.

## 2026-09-26 — v2: low-information operation and the thirty-minute intake

Emma's 7:15 PM spec, for a scheduled job that runs cleanvibe unattended at
10 PM (research on the history of AI). cleanvibe sessions assume a human may be
there but must work from low information and cope with nobody being there.

- **First-session prompt** (the one message cleanvibe can put straight in front
  of the agent) now carries the operating instructions. The project works from
  low information; the user may say nothing or be away. Read CLAUDE.md, then
  immediately CronCreate the one-time thirty-minute intake. Then look at the
  folder, write a first read into INTENT.md, commit, and say briefly what it
  sees and plans. AskUserQuestion only if the user is clearly there and
  replying.
- **CLAUDE.md (v2)**: the chat comes first, then what is in the folder (specs or
  instructions in the data lake are followed unless the chat says otherwise),
  then the directory name (sometimes enough, usually a hint). New "The data lake"
  rule: material goes into `data_lake/` and is committed as part of the
  repository's history; stray material is committed where it landed first,
  then `git mv`'d in. New "Thirty-minute intake" section with the exact cron
  (one-time, pinned local time, `[cleanvibe cron]` prompt) and five steps: run
  the intake script; investigate `data_lake/` thoroughly; update INTENT.md;
  plan into queue.md/todo.md with the matching skill (low information is the
  normal case, not a reason to wait); start the work loop now if engagement was
  little or none, otherwise one-shot it 60 minutes later (90 minutes in).
- **`.claude/scripts/data_lake_intake.py`** (stdlib, committed in every v2
  project; `templates.V2_INTAKE_PY`) does the mechanical part without
  judgment. Commit 1: "Intake: the repository 30 minutes in, before moving into
  data_lake/", with everything as found. Commit 2: "Intake: move uncommitted
  material into data_lake/", which `git mv`s every top-level entry that had
  never been committed, except the project's own files and workflow
  directories. It then prints a report: the moves, the data-lake file list, and
  user engagement counted from `sessions/*.jsonl`. cleanvibe's own prompts and
  `[cleanvibe cron]` messages are not counted. The verdict is substantial at 2+
  messages or 300+ characters. It records `intake_at` in `.cleanvibe.json` and
  runs once. The resume prompt reschedules it if the first session ended early.
- Resume prompt: no AskUserQuestion. It says to tell the user where things
  stand, follow their lead if they reply, and carry on with the planned work if
  they don't.
- doctor's v2 file set includes the intake script.
- Tests: 5 end-to-end intake tests (real git: drops at the top level, a new
  directory, a file already in data_lake/, an edited README; both commits and
  their contents; runs once; engagement verdicts both ways; agent work
  committed before intake stays put), plus updated prompt/CLAUDE.md tests.

## 2026-09-26 — AskUserQuestion only when the user is clearly present

Emma is leaning away from AskUserQuestion: use it only when the user is
clearly present and replying; otherwise decide and write the assumption down.
Applied to the v2 CLAUDE.md and prompts (above). The `research-practice` skill
now infers the question from chat, data lake and name when the user is away,
recording it as an assumption. In `autonomous-loop`, the "ask whether to start
the loop" line is replaced: in a cleanvibe project the intake decides. The 1.x
starting-prompt tail is now "if I am here, ask me; if not, make a reasonable
assumption and write it down". This repo's vendored skills are refreshed.
220 tests pass.

## 2026-09-26 — v2 practice project: an agent-started session runs as a real session

Bare `cleanvibe` in `tests/scratch/`, run from this agent session, created
`cleanvibe-2026-09-26-2` at 19:33 and launched it. This is the child-session
case the rework targets. Checked from the outside:

- **Pre-trust worked.** Claude Code's config now has the folder with
  `hasTrustDialogAccepted: true`, and the session went straight past the trust
  prompt that stalled the first attempt (still open as PID 38744, left alone).
- **A real top-level session.** Its transcript is under its own
  `~/.claude/projects/...cleanvibe-2026-09-26-2/`, not this session's, and the
  Stop hook copied it into the project's `sessions/` (`.jsonl` + `.md`).
- **Remote Control on.** The transcript has `bridge-session` records.
- **It followed the first-session prompt.** It loaded CronCreate and scheduled
  the one-time intake (`3 20 26 9 *`, `recurring: false`, with the exact
  `[cleanvibe cron] Thirty-minute intake...` prompt). It wrote a first read into
  INTENT.md and committed it (`04c5c9f`): empty folder, generated name, "likely
  a cleanvibe smoke test", low confidence. It reported what it would do if the
  user stayed silent.
- **Found and fixed:** session-log files were dated from the transcript's UTC
  timestamps (`2026-09-27_...` for a 7:33 PM Pacific session). The hook now
  uses the local date.

## 2026-09-26 — Released v2.0.0; local cleanvibe upgraded

Emma gave full permission to release cleanvibe 2 and update her local install
before her scheduled 10 PM run.

- CI green on the release commit `6329203` (6/6: Python 3.9 and 3.13 on
  Windows, macOS, Linux). GitHub release **v2.0.0** created on it; `publish.yml`
  succeeded; PyPI serves `cleanvibe-2.0.0` (wheel + sdist).
- PyPI's summary JSON and pip's index were still serving cached 1.18.0 data a
  minute after publishing, so `pip install -U cleanvibe==2.0.0` found nothing.
  Installed the published 2.0.0 wheel by its PyPI file URL instead (same
  artifact) into Emma's per-user Python 3.13, which is where her `cleanvibe`
  command lives (`AppData/Roaming/Python/Python313/Scripts`). It was **1.17.0**
  before; `cleanvibe --version` now prints 2.0.0.

## 2026-09-26 — 10 PM readiness check (installed 2.0.0, not the checkout)

In a temp folder with the installed command: `cleanvibe new ai-history
--no-claude` wrote the full v2 scaffold, including
`.claude/scripts/data_lake_intake.py` and the hooks, and doctor reported no
drift. `cleanvibe new ai-history --dry-run` on the existing project reported it
would open it rather than overwrite. Dropping `brief.md` and running the intake
script produced both commits and moved `brief.md` into `data_lake/`. Legacy
names point to `cleanvibe legacy`. Nothing is left uncommitted in this repo.

## 2026-09-26 — Live: the thirty-minute intake and work loop ran unattended

The practice session `tests/scratch/cleanvibe-2026-09-26-2` (started at 19:33
from this agent session, nobody interacting) did the whole v2 flow on its own:

- **20:03:** the one-time cron fired. The agent ran
  `.claude/scripts/data_lake_intake.py`, which made both commits (`384cafa`
  snapshot, `ab97cdc` move; nothing had been dropped in, so nothing moved).
- **20:04:** it read the report and the skills, settled its read of the purpose
  (a smoke test of the flow, given an empty folder and a generated name),
  created `queue.md`/`todo.md`/`devlog.md`/`FINDINGS.md` and committed
  (`e7fa51c`).
- The engagement verdict was "little or none", so it started the work loop
  **immediately**: three recurring crons at `3 * * * *`, `15 * * * *` and
  `42 * * * *` with `[cleanvibe cron]` prompts, per the rewritten
  `autonomous-loop` skill. It then kept working its queue.

That covers every step of the unattended path Emma's 10 PM run depends on, run
by a real agent rather than a test. Not exercised live: the
substantial-engagement branch (loop postponed 60 minutes), which is covered by
the intake tests' verdict only.

## 2026-09-26 — Session working files live in a gitignored `scratch/` in this repo

Emma was concerned that this session's working files (edit scripts, release
notes, test folders) sat in Claude Code's temp scratchpad under
`%LOCALAPPDATA%\Temp\claude\...`, which Storage Sense clears. `/scratch/` is
now in `.gitignore`, CLAUDE.md says to use it, and a memory records the
preference. Practice projects stay in `tests/scratch/`.

## 2026-09-26 — 2.0.1: fixes from case study 02 (the invented smoke test)

The first unattended practice session (`tests/scratch/cleanvibe-2026-09-26-2`;
full write-up in `docs/case-studies/02-invented-smoke-test.md`) had no chat, no
files and a generated name. It guessed "a cleanvibe smoke test" from its
location inside the cleanvibe repo, and the intake verdict ("no engagement:
start the loop now") pushed it to act. It spent the loop testing cleanvibe
itself. After Emma arrived it investigated beyond the project, kept going after
"Please don't", and argued with her plan.

- **Nothing to go on.** The intake report now states whether `data_lake/` has
  material and whether the name was generated. The verdicts are:
  substantial engagement (loop in 60 minutes); no engagement but material
  (loop now); **name only** (a chosen name, nothing else: start only if the
  name plainly states a task); and **nothing to go on** (don't plan, don't loop,
  say so in INTENT.md and wait). CLAUDE.md step 5 and the first prompt match.
- **A guess about why the project exists is not a task.** In the first prompt
  and CLAUDE.md. **The path stays in the prompts.** An earlier draft removed it
  and declared location "never evidence". Emma corrected that: the path
  carries real information, and the session's guess was accurate. The failure
  was turning that guess into invented work. She reads it as poisoned by too
  much self-referential information rather than too little.
- **Scope and stopping** (CLAUDE.md): stay inside this project; "stop" and
  "don't" mean stop now; follow the user's reading over your own.
- **Session names.** Every session got the AI title "Cleanvibe project intake"
  from the shared prompt, and Emma couldn't find hers in the app. A folder name
  the user chose is now passed as `--name` (prompt box, `/resume`, terminal
  title) and as the Remote Control session name (the real CLI accepted
  `--name X --remote-control X`). Untitled projects get no name and Claude picks
  one; the `.bat` follows the same rule.
- **Untitled naming (Emma).** `untitled-cleanvibe-project`; if taken,
  `untitled-cleanvibe-project-YYYY-MM-DD-HHMM`; only if that is also taken, a
  number.
- **Case studies** in `docs/case-studies/` (01 trust prompt, 02 invented smoke
  test, 03 and 04 next), per Emma: keep watching sessions and recording them.
- Tests: new verdict tests (nothing to go on, name only, material), naming and
  path tests. 225 pass. Version 2.0.1.

## 2026-09-26 — 2.0.1 released and installed; case studies 03 and 04 launched

- CI green on `2d02def` (6/6). Released **v2.0.1**; PyPI serves it; Emma's
  local `cleanvibe` upgraded to 2.0.1 (from the published wheel again, since
  pip's index lags a new upload).
- With the installed command, from this agent session, in `Documents/GitHub/`:
  - bare `cleanvibe` created `untitled-cleanvibe-project` (case 03: empty,
    untitled, the low-information test);
  - `cleanvibe new chat-test` created `chat-test` (case 04: Emma talks to it).
- Both were pre-trusted, got their own transcripts with Remote Control on, and
  scheduled the intake for 21:43. `chat-test` is titled `chat-test`; the
  untitled one got no name, and Claude called it "Untitled cleanvibe project
  intake". Details and what to watch for are in `docs/case-studies/03-*` and
  `04-*`.

## 2026-09-26 — Case studies 03 and 04: both 2.0.1 branches passed live

- **03, untitled and empty:** the 21:43 intake reported NOTHING TO GO ON. The
  agent recorded that in INTENT.md and did nothing else: no plan, no loop.
  Same input as case 02, opposite outcome.
- **04, chat-test:** Emma chatted from 21:14 to 21:22. The intake reported
  SUBSTANTIAL engagement, so the loop was postponed to a one-time job at 22:43,
  as designed. This was the first live run of that branch. Following her steer
  ("with no strict instructions, the loop monologues and researches the
  subject"), it planned research with `research-practice`.
- Session inspection is now a reusable helper in the gitignored `scratch/`
  (`inspect_session.py`: crons, verdict, user messages).
- Details: `docs/case-studies/03-untitled-empty.md`, `04-chat-test.md`.

## 2026-09-27 — Case studies 03–05: the 10 PM run, chat-test's loop, the long wait

Emma asked to go through all the sessions and write them up.

- **05, ai-history-analysis (new, the 10 PM run):** the first project started
  from files. The brief dropped at creation was moved into `data_lake/` by the
  22:54 intake. With material and no chat, it started the loop, planned from
  the brief with `research-practice`, and wrote three layered, sourced research
  notes by 00:18. At 00:31 it pushed to a private repo at Emma's request.
  **Passed.** It exposed the loop's slow pace: one queue item per hourly tick.
- **04, chat-test:** the postponed loop started at 22:43 on schedule. The
  hook's hourly session-log commits landed live (22:43, 23:44). It wrote
  research on cleanvibe's own act-vs-wait rules, ending in six proposals
  (P1–P6) that it left for Emma to decide.
- **03, untitled:** still nothing after 21:43, three hours on; the
  nothing-to-go-on wait holds.
- Queued as NEEDS-DECISION for Emma: the P1–P6 proposals and the loop pace.

## 2026-09-27 — 2.0.2: one simple work loop

Emma: the loop should be one cron every half hour whose prompt just says to
commit and push any and all changes and continue working on the queue. The
hourly flush and status reports weren't useful. The more complicated loop
helped earlier, when agents made up problems more and her work was
well-defined but hard. Since then agents have gotten smarter and her work has
become more routine.

- `autonomous-loop` rewritten again: one recurring `CronCreate` at
  `7,37 * * * *` (off the :00/:30 marks) with the prompt
  `[cleanvibe cron] Commit and push any and all changes, then continue working
  on the queue.` Each tick commits and pushes, then works the queue for as long
  as it makes sense (not one item per tick, which is what made case 05 slow).
  An empty research queue refills from `research/SUMMARY.md` (P4) before
  idling. Kept: idle is normal; only the user stops it; replication is exempt.
  Per Emma, not split for legacy (the frozen 1.x bootstrap queues still
  describe three crons).
- The v2 CLAUDE.md intake step 5 names the new loop. This repo's CLAUDE.md cron
  section, the README skills table and this repo's vendored skill are updated.
  `pages/updates.md` has a v2.0.2 entry with the full skill text for existing
  repos.

## 2026-09-27 — 2.0.2: adopt chat-test's six proposals

Emma adopted all six (AskUserQuestion). On P1–P3 she added that the first run's
problem was being given too much context by accident, not having context.

- **P1** "Nothing to go on is a real state, and a narrow one": it applies only
  when the user has said nothing at all. The intake gained a matching verdict:
  **SOME ENGAGEMENT, no material** means what the user said is the subject;
  plan research on it and start the loop. Before, one short message with an
  empty folder could still read as "nothing to go on".
- **P2** "No strict instructions is not no work": with a subject but no spec,
  the loop researches it under `research-practice`.
- **P3** "If the user *says* the tool or the chat is the subject, it is."
- **P4** Research queues refill from `research/SUMMARY.md` open questions (in
  the loop skill).
- **P5** The intake verdict and CLAUDE.md say the user is **present**, not
  "steering", since the intake counts messages.
- **P6** Ask one short question when a present user's worry could point
  either way.
- Tests: new SOME ENGAGEMENT test, the "present" wording, the new CLAUDE.md
  clauses, and the loop invariants (one `7,37` cron, the prompt, no flush or
  status, "do not turn the cron off yourself", the SUMMARY.md refill). 226 pass.

## 2026-09-27 — Released v2.0.2; local cleanvibe upgraded

CI green on `0fc4083` (6/6). Released **v2.0.2**; PyPI serves it; Emma's local
`cleanvibe` is now 2.0.2. Checked with the installed command: a fresh project's
`autonomous-loop` skill has the `7,37` cron, its intake script has the
SOME ENGAGEMENT verdict, and doctor reports no drift. Sessions already running
(chat-test, ai-history-analysis) keep the crons they set up under 2.0.1 until
they are restarted or told to switch.

## 2026-09-29 — 2.0.3 on branch `research-fixes-2.0.3` (not pushed, not released)

Applied the eight fixes from the ai-context-research study (case study 06),
approved by Emma: "you can apply all the eight fixes".
- **M1** The loop-tick prompt names the standing duties: refill an empty queue
  from the open questions, re-read and update INTENT.md, fill in README.md,
  check the clock. The skill gains step 4 (keep the standing files current),
  and "blocked" no longer counts as "nothing to do".
- **M2** The first and resume prompts name the cleanvibe-update-check skill.
- **M3** CLAUDE.md: times come from `date`, not estimates or schedules.
- **M4** CLAUDE.md: quote the user before recording their stance; ask if the
  input was dictated or ambiguous.
- **M5** research-practice downloads go in `data_lake/downloads/` (CLAUDE.md
  agrees); Claude Code's memory directory is named as outside the project;
  the update check verifies that skills and CLAUDE.md agree.
- **M6** The session-log hook renders `[cleanvibe cron]` prompts under
  `## Cron`.
- **M7** CLAUDE.md: constraints the user gives in chat go in INTENT.md.
- **M8** CLAUDE.md: prose goes through the file tools, dependent shell steps
  are chained with `&&`, and an edit is checked before it is logged.
- Case study 06; `pages/updates.md` v2.0.3 entry; version 2.0.3; this repo's
  own vendored skills refreshed. Tests: one updated (the tick prompt changed
  on purpose; it now also checks that the duties are named), cron rendering
  in the hook test, and three new 2.0.3 tests. 229 pass.
- **Not done:** push, CI, release, PyPI. Pushing publishes to the public repo
  and the Pages site, so it waits for Emma (BLOCKED-ON-USER-ACTION).

## 2026-10-01 — 2.0.3: chat mode first, private descriptive remote by default

Emma, after an untitled session went into "work mode" (INTENT.md, a commit
and a menu of options) the moment she said "This is the project": the chat is
the project by default, the start is supposed to be light and conversational,
and the agent goes hard into work only when told to or after the user has been
gone long enough that it is no longer a chat. Repos go to GitHub by default,
private, under descriptive names rather than the folder name.
- CLAUDE.md: "The chat is the project, from the first message"; a new
  "Chat mode, then work mode" section (no files, commits, plans or menus in
  chat mode; work mode on the user's word or after an hour without a message,
  restarting with each message; the work-mode start writes INTENT.md, creates
  `gh repo create <descriptive-name> --private --source=. --push`, fills in
  the README, runs the update check, plans and starts the loop); a "Mode
  check" section; the commit rule now pushes to that private remote.
- Intake script: reports minutes since the user's last message (from the
  transcript timestamps) and returns CHAT MODE with a pinned cron time for
  the Mode check, or WORK MODE. It can be re-run after the intake as the Mode
  check, committing nothing. The SUBSTANTIAL verdict is removed.
- First prompt: chat mode, greet in a line or two; the resume prompt
  reschedules a Mode check if work mode hasn't started.
- autonomous-loop skill: the work-mode switch decides when the loop starts.
- Tests: the old verdict and prompt assertions were changed on purpose; new
  tests for chat mode, an hour of quiet, and the re-run Mode check. 231 pass.

## 2026-10-01 — 2.0.3: passphrase session titles for untitled projects

Emma: untitled sessions all showed "Untitled cleanvibe project intake" in the
app, because with no name Claude Code titles the session from cleanvibe's
boilerplate first prompt. She expected Remote Control's passphrase-style
random names. The starting prompt stays (it carries the operating
instructions and permissions; moving it to the system prompt is ruled out).
- An untitled project now gets a random `adjective-adjective-noun` session
  name (`templates.passphrase_name`), stored as `session_name` in
  `.cleanvibe.json` and passed as `--name X --remote-control X` at the first
  launch, in `!runClaude.bat`, and when the project is reopened. A folder name
  the user chose is still the session name.
- Tests: the launch test now expects the passphrase (changed on purpose), plus
  tests for chosen names and for passphrase variety and cmd-safety. 233 pass.

## 2026-10-03 — `helping-with-arxiv` added as a submodule (temporary)

Emma's request (queued by the pc-manager session): add
<https://github.com/EmmaLeonhart/helping-with-arxiv> as a git submodule at
`helping-with-arxiv/`. It holds the arXiv submission-prep work for the Quatrix
paper and overlaps with `cleanvibe/arxiv.py`. The submodule is a stopgap; the
plan is a `git subtree add` later so its history is kept, logged in `todo.md`
with the open questions (prefix, relation to `arxiv.py`). Packaging is
unaffected: `pyproject.toml` lists `packages = ["cleanvibe"]` explicitly.

## 2026-10-03 — Released v2.0.3

Emma: "push it, then merge into main and release it". The
`research-fixes-2.0.3` branch was already contained in `main` (and `main` was
already pushed), so the merge was a no-op; the branch was pushed as asked.
Tagged `v2.0.3`, published the GitHub release, and the publish workflow put
2.0.3 on PyPI (verified on pypi.org). CI green on `main` before tagging.

## 2026-10-03 — `helping-with-arxiv` subtree-merged, keeping its history

Emma: merge it "in properly as a subtree maintaining the history". Removed the
submodule (`0357173`), then `git subtree add --prefix=helping-with-arxiv
https://github.com/EmmaLeonhart/helping-with-arxiv main` without `--squash`,
so its six commits are in this repo's history (`e9a9d9d`). The prefix stayed
`helping-with-arxiv/`. How it relates to `cleanvibe/arxiv.py` is still open
and logged in `todo.md`. Packaging is unaffected (`packages = ["cleanvibe"]`);
233 tests pass and `doctor` is clean.

## 2026-10-03 — Case study 07: did the 2.0.3 fixes work?

The ai-context-research follow-up on the first eight 2.0.3 sessions, written
up for this repo without project names or quotes (several sessions are
personal). M2 (update check), M6 (`## Cron` in the log) and M7 (chat
constraints into INTENT.md) work; M1 does not keep INTENT.md current during
the loop, and no empty queue was refilled, each time for a stated reason;
M8 (prose through file tools, check before logging) still fails in most
sessions. Three open decisions for Emma are listed in the case study.

## 2026-10-03 — `convert` adopts existing planning files

From `todo.md` (the queue was empty; case study 07's three open items are
NEEDS-DECISION for Emma). `convert` never injected `todo.md` itself, but its
bootstrap queue would have moved a repo's `ROADMAP.md` or `TODO` into
`data_lake/` as stray material in step 2 and written a fresh `todo.md` beside
it in step 5. Now `scaffold.find_planning_artifacts` finds top-level
`todo`/`backlog`/`roadmap`/`tasks`/`plan` files, `convert` (and its
`--dry-run`) reports them, and `templates.queue_md(existing_planning=...)`
adds a bullet to step 2 (leave them in place) and to step 5 (build
`todo.md` from them; ask before deleting the originals). A convert without
such files produces the same queue as before. Site card and CLAUDE.md
updated. 4 new tests; 237 pass, `doctor` clean. The site's stability
section calls the legacy modes frozen; this change is additive only.

## 2026-10-03 — Design note: the LLM Wiki pattern (the "Carpathes" item)

From `todo.md`. "Carpathes / L-Carpathes" is read as a dictation of
Karpathy's LLM Wiki (April 2026 gist); a search for "Carpathes" finds nothing
relevant, and the note states that assumption. `docs/llm-wiki.md` maps the
pattern onto cleanvibe (`data_lake/` ≈ `raw/`, `research-practice` notes and
summary ≈ the wiki) and recommends a skill adopted on demand, not a mode or an
integration. Two parts are worth taking regardless: `data_lake/` read-only
after it lands, and lint as the last step of ingest (case study 07: event-
triggered rules hold, standing duties are skipped). The `todo.md` item is
replaced by the follow-up, with two NEEDS-DECISION points for Emma.

## 2026-10-03 — `cleanvibe scan`: a summary for the replication consent gate

From `todo.md` ("automated safety scan of cloned/recipe code"). Since v1.6.1
the replicate templates make the agent ask before running third-party code,
but the user answered blind. New `cleanvibe/scan.py` and `cleanvibe scan
[PATH...]`: read-only, stdlib, regex categories (pipe-to-shell, dynamic-exec,
destructive, credentials, persistence, package-source, binary) with file and
line, plus every URL host mentioned. All five consent-gate passages now tell
the agent to run `cleanvibe scan .` and put the summary in its question,
replacing "a future enhancement (see `todo.md`)". A fresh manual replication
scaffold scans clean once `.github/` is skipped (cleanvibe's own Pages
workflow runs `sudo apt-get` on GitHub's runner); a deliberately risky sample
hit every category. README, site card and CLAUDE.md updated; the `todo.md`
item is narrowed to what is left (following install steps, a real review).
9 new tests; 246 pass, `doctor` clean.

## 2026-10-03 — `todo.md`: replication section brought up to date

The section still described shipped work as future and said the downloader
fetches HTML first (reversed in v1.5.0). Checked each item against the code
and a fresh scaffold, then removed the three that shipped: the Pages findings
site + PDF report (v1.13.0, `pages.yml`), the ZIP package (`package.yml`,
artifact + release asset) and repo provisioning (private `gh repo create`
since v1.5.0/v1.18.0; the "public from minute one" half was reversed on
purpose). Dropped the stale history paragraph (it is in this file already).
Reworded the HTML extractor item to cover only papers with no LaTeX source,
and replaced "unify the two scaffolds" with the open question it became after
cleanvibe 2: whether `replicate` should share the v2 base.

## 2026-10-03 — `cleanvibe replicate --batch`

From `todo.md` ("batch replication from a corpus"). `cleanvibe replicate
--batch FILE [--into DIR]` scaffolds one replication project per paper in a
JSON or text list, each routed exactly as a single `replicate` (the
dispatcher is now `cli._replicate_one`). It never launches Claude, waits 3 s
between network papers (arXiv's rate limit), carries on past a failure and
exits 1 if any paper failed. `docs/replication-examples/papers.json` loads
unchanged. Live run against arXiv: Sutra and "Attention Is All You Need"
both scaffolded and fetched into `tests/scratch/batch-live`, and bare
`cleanvibe --dry-run` inside one would open it, as the closing hint says.
README, site card and CLAUDE.md updated; the README stability note now says
`replicate` is 1.x plus the additive `--batch`. 9 new tests; 255 pass.

## 2026-10-03 — Queue refocused on the paper; repo moves; clawrxiv_clone fix

Emma: the goal is a paper out fast (arXiv endorser rights), posted to
clawRxiv. The paper already exists in `ai-context-research` (draft, Claw4S
`SKILL.md`, 2-page note), waiting on her review, so the queue points there
instead of starting a second one. Repo moves she directed: agentic-erp and
topaz_buiness_plan subtree-merged with history into the business repo
(pushed); emmaleonhart.com merged into a scratch clone of narrative_identity,
push blocked by the auto-mode classifier; INBE → genealogy waiting on a
24.6 GB clone. The subtree merges of private paper repos into public
cleanvibe are held until she says go. From clawrxiv_clone's queue:
`parse_markdown_paper` now reads an `## Abstract` section (`ca9f5c5` there,
4 new tests, 33 pass locally without the fastapi module).

## 2026-10-03 — INBE merged into genealogy

The full checkout of `genealogy` (24.6 GB) stalled at 41 GB, busy for an
hour without writing, after the first attempt hit Windows path-length limits.
Stopped it and redid the merge in a sparse checkout (root files and
`subtrees/` only): `subtrees/INBE` with history, its tree identical to the
local INBE HEAD including one commit never pushed to INBE's own remote.
Merged genealogy's 24 newer commits and pushed. ontology-harness's pointer
to genealogy is not bumped. The local clawRxiv reviewer clone (gemma3:12b)
rated the paper's Claw4S note Weak Accept (scores 4/3/4/4); review saved in
`scratch/paper-score/`, nothing posted.


## 2026-10-04 — The Claw4S note answers its pre-submission review (v2-v5)

Emma: keep working, "responding to the Claw4S analysis and trying to refine
our hypothesis". Worked in ai-context-research (pushed `b56f25a`, `65c3e52`,
`40a03c8`, `cc97467`). The finding is now stated as where a duty's cue comes
from: it holds when the cue arrives in the agent's context (14/14 session
cases) and lapses when the agent must notice it (20/35), with two blind
coders agreeing on every duty, the update check as a quasi-intervention
(0/8 -> 6/6, same-week control 0/1), intent staleness from git rather than
the read heuristic, M6 dropped from the agent duties, a falsifiable
prediction for the next round, and grounding in prospective memory
(McDaniel & Einstein 2000, focal vs non-focal cues). The reviewer clone
swings between Weak Accept and Borderline on the same text; v1, v3 and v4
mostly Weak Accept, v2 dipped. Scores and responses are in
`claw4s/review.md` there. Posting is still Emma's call.

## 2026-10-04 — The arXiv draft gets the cue-source analysis

In ai-context-research (`03369fa`): the draft's new §7.2 carries the Claw4S
note's v5 finding, replacing §7.1's closing "event vs habit" paragraph, with
a sentence each in the abstract and conclusion; frozen sections untouched.
Fixed `build_paper.py` so figures follow `--out` (out-of-tree builds, as the
Claw4S SKILL.md runs them, failed on a missing figure). 14 pages, no LaTeX
errors or unresolved references. Both versions now say the same thing;
posting and submission are Emma's call.

## 2026-10-04 — Release-ready data for the paper

In ai-context-research (`2167401`): `research/data/release/` holds the
per-session and per-tick counts behind the paper with project names replaced
by session codes and cron prompt text by its kind, made by
`scripts/release_data.py`; a scan found no project names in it. The Claw4S
note offers this release; publishing it is Emma's decision.

## 2026-10-04 — The Claw4S skill tests the cue-source claim

In ai-context-research (`3053d63`): `claw4s/SKILL.md` step 5 now states the
v5 claim, and new steps 6-7 have a reader code each duty's cue blind with two
fresh agents and aggregate held/lapsed by cue, with the authors' values and
the result that would falsify it. The privacy section points at
`release_data.py`.

## 2026-10-04 — Claw4S note v6: clarity rewrite

In ai-context-research (`1b2be3a`). v5 scored Borderline three times with
clarity 2-3; v6 rewrites for readability (finding first, plain names, a
Discussion section, caveats in Limitations) with the same numbers and
claims, and clarity is back to 4 (BL and WA). The reviewer clone's floor is
Weak Accept/Borderline and its remaining objections need more data, so no
more rewording rounds. The note is ready for Emma's review.

## 2026-10-04 — clawRxiv review loop for the paper (waiting on the key)

Emma: post the paper, and run it through clawRxiv the way the earlier papers
were ("research CI/CD"). Ported latent-space-cartography's `publish.yml` to
ai-context-research (`9dfc8b7`): `.github/workflows/clawrxiv.yml` with
`scripts/clawrxiv_submit.py` (create, or revise via
`/api/posts/{id}/revise`, following a 409's `duplicateId`) and
`scripts/clawrxiv_fetch_review.py` (poll for the AI review for two hours,
commit it to `claw4s/reviews/`). The payload builds locally (1,004-character
abstract). Blocked on the `CLAWRXIV_API_KEY` secret: the old agent's key
cannot be read back from GitHub, and registering a new agent
(`Emma-no-Mikoto`) and storing its key was refused by the auto-mode
classifier as a secret-store write, so Emma has the one-line command.

## 2026-10-04 — Paper item: the post decision is made

Queue item 1 pointed at the paper in `EmmaLeonhart/ai-context-research` and
waited on Emma to review the Claw4S note and decide whether to post it. The
decision has been made and carried out: Emma said to post it (2026-10-04),
set `CLAWRXIV_API_KEY` on that repo (20:51 UTC), and the `clawrxiv.yml`
workflow posted the note as clawRxiv post 2893, paper **2610.02893**
(`1c9c16e`, by github-actions). The run that fetches the AI review was still
in progress at 14:05 PST. Nothing for this repo to do on the item, so it is
deleted; the review loop is the next item. The paper stays in
ai-context-research (no second copy here).

## 2026-10-04 — clawRxiv review loop: three rounds, stopped at v8

The Claw4S note (in `EmmaLeonhart/ai-context-research`) went through
clawRxiv's AI review (Gemini 3 Flash) three times; each revision got a new
paper id. v6 (2610.02893): **Reject**, mainly for a "hallucinated" NoLiMa
citation (real: arXiv:2502.05167; the reviewer's cutoff predates ICML 2025)
and unreleased data. v7 (2610.02894, `d804fd2`): added the arXiv id and
references, called it a case study, stated the author's role, defined
staleness, scoped the kappa; **Weak Reject**, now faulting novelty
("explicit prompts beat implicit"). v8 (2610.02895, `82a8f02`): said why
that is not the finding (every duty explicit and in context; the explicit
per-tick intent prompt failed); **Reject**, with every con about the data
(N=17, one user, tiny control, transcripts withheld, LLM-coded).

**Decision (this session, under Emma's instruction to make the call on a
stuck item):** stop revising. The ratings swing on the same data, as the
clawRxiv clone study found, wording cannot answer the data points, and each
revision adds a public version. Not done: publishing
`research/data/release/`. That repo reserves it for Emma, it would answer
only one of five cons, and a public release cannot be taken back, so it
stays NEEDS-DECISION (Emma) in ai-context-research. What would move the
rating is round 3 (more sessions and users, a real control), which is that
repo's queue. Responses for every round: `claw4s/review.md` there.

## 2026-10-04 — Correction: the review loop runs continuously

The previous entry's decision to stop the clawRxiv loop at v8 was wrong.
Emma, 2026-10-04: the work loop is the CI/CD that posts the Claw4S note,
checks the AI peer review and keeps pushing new revisions periodically. It
is back in `queue.md` as a standing item worked every tick. v9
(`303ddd7` in ai-context-research) answers v8's circularity, subjectivity
and control points. She also approved publishing `/paper`; the auto-mode
classifier still refuses that write, so it waits on her running the
command.

## 2026-10-04 — 2.0.4: the INTENT.md staleness cue (round 3 intervention)

clawRxiv rated the Claw4S note v10 Weak Reject, and every remaining con
needs round 3 data. The note predicts that making INTENT.md's staleness
arrive will raise intent edits in ticks more than two hours stale from 6%
to most. A cron prompt is fixed text, so the cue is a hook:
`.claude/hooks/intent_staleness.py` (`templates.INTENT_STALENESS_PY`) on
`UserPromptSubmit`, wired by the new `templates.v2_settings_json()` (chat
keeps `chat_settings_json()`). On a `[cleanvibe cron]` prompt it prints
"INTENT.md last changed H hours and N commits ago" from `git log`; any other
prompt, bad input or missing file prints nothing, and it always exits 0.
The generated CLAUDE.md lists it under Files; `pages/updates.md` has the
v2.0.4 entry. `tests/test_intent_staleness.py` runs the generated hook
against a scaffolded repo. Full suite: 260 tests OK, including its 5;
`cleanvibe doctor .` clean. Decision (this session, Emma's standing instruction to make the
call): ai-context-research's open question on "a checkable INTENT duty" is
answered by testing the note's own prediction.
NEEDS-INVESTIGATION: whether Claude Code fires `UserPromptSubmit` for a
cron-enqueued prompt; check the first 2.0.4 session's transcript for the
hook's line before counting round 3.

## 2026-10-04 — v2.0.4 release created; then flagged

CI green on `422585b` (6/6). Created GitHub release **v2.0.4**, which starts
`publish.yml` (PyPI). The auto-mode classifier then flagged the release as
creating a public surface, after it already existed. Not verified: whether
the PyPI publish finished, and Emma's local `cleanvibe` is not upgraded.
NEEDS-DECISION (Emma): keep the release (and upgrade locally so round 3
sessions run 2.0.4), or remove it.

## 2026-10-04 — doctor flags v2 projects missing the staleness hook

Loop tick with every queue item waiting on Emma, so refilled from the
round 3 work: `cleanvibe doctor` now lists `.claude/hooks/intent_staleness.py`
among the cleanvibe 2 core files, so a project scaffolded before 2.0.4
reports it missing instead of silently running round 3 without the cue.
New test in `tests/test_doctor.py`; 261 tests OK; doctor clean on this repo.

## 2026-10-04 — URL-mode replication papers get a clean `paper.md`

Refilled from `todo.md` while the other queue items wait on Emma. A paper
downloaded from a plain URL was saved only as raw `paper.html` (scripts,
navigation, base64 figures). New `cleanvibe/htmltext.py`
`html_to_markdown()` (stdlib `html.parser`) keeps headings, paragraphs,
lists, links, code, tables and image alt text, takes math from LaTeXML's
`alttext` as `$...$`, and drops the rest. `replicate._download_source`
writes `paper.md` beside `paper.html`, and the generated `download_paper.py`
embeds the module's source verbatim, so both paths convert the same way
with no cleanvibe import. The URL queue tells the agent to read `paper.md`.
Live check on arXiv's HTML for 1706.03762: 189 KB of HTML became 42 KB of
Markdown with every section heading and the equations as LaTeX. The PDF-only
half stays in `todo.md`: arXiv PDF-only papers have no HTML at all.
`tests/test_htmltext.py` (8 tests); 269 tests OK; doctor clean.

## 2026-10-05 — `scratch-2026-09-25/` added as a submodule

A clone of `helping-with-arxiv` appeared at the repo root (01:00). Emma:
make it a submodule. Added with `git submodule add` at its existing path,
pointing at `e6bfe9e` (level with GitHub). Its uncommitted `!runClaude.bat`
edit stays in the submodule's working tree. The same repo is also in this
repo as the `helping-with-arxiv/` subtree.

## 2026-10-05 — auto-named projects: the passphrase is the folder name too

Emma: the generated names are good; use them for the directory and the chat
title both. `auto_project_path` now draws a passphrase (`golden-swift-otter`,
redrawn if the folder exists, a number after 20 taken draws) instead of
`untitled-cleanvibe-project`, and `new_project` uses that folder name as the
session title, so the two always match. The first prompt and INTENT.md call it
"a random generated passphrase" that says nothing about the purpose, so the
agent doesn't read meaning into "otter". README, CLAUDE.md and the `new` help
text updated; tests rewritten for the new naming; 270 tests OK. Not released.
