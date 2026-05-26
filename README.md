# cleanvibe

**Website · [cleanvibe.emmaleonhart.com](https://cleanvibe.emmaleonhart.com)**

A tiny Python CLI that scaffolds AI-assisted coding projects and launches Claude Code.

`cleanvibe` is not a coding tool. It's a **state initializer** -- it removes the friction between "I want to build something" and "Claude is working inside a well-structured environment." The real value lives in the `CLAUDE.md` it injects: an opinionated behavior contract that enforces documentation discipline, meaningful commits, and iterative file-based thinking.

## Install

```
pip install cleanvibe
```

### Developer install (working on cleanvibe itself)

```
git clone https://github.com/Immanuelle/cleanvibe
cd cleanvibe
pip install .         # or use !dev-install.bat on Windows
```

**Use `pip install .`, not `pip install -e .`.** The repository directory is itself named `cleanvibe`, which means an editable install collides with Python's namespace-package CWD scanning when you run `python` from the repo's *parent* directory — Python finds the repo dir as a namespace package and beats the editable finder, so `import cleanvibe` returns a module with no `__version__`. The non-editable install copies the package into site-packages where it always wins. After any source edit, run `pip install .` again (or `!dev-install.bat`). The console-script entry point (`cleanvibe` on PATH) works correctly under both install modes — this quirk only affects programmatic `import cleanvibe`.

## Usage

### Create a new project

```
cleanvibe new my-project
```

This will:
1. Create the directory `my-project/`
2. Write `CLAUDE.md` (workflow rules for AI-assisted development)
3. Write `README.md` (starter documentation)
4. Write `queue.md` (active work queue, pre-seeded with a first-session bootstrap sequence that walks Claude through triaging dropped-in files, inferring the project, interviewing the user, creating `todo.md`, populating the real queue, and pushing to a private GitHub repo)
5. Write `.gitignore` (sensible Python defaults)
6. Initialize a git repo with an initial commit
7. Launch Claude Code inside the project

### Clone an existing repo — codebase onboarding

```
cleanvibe clone https://github.com/user/repo
```

`clone` is for **onboarding an existing codebase**, not bootstrapping a blank
one. It is deliberately different from `new`:

1. `git clone` the repository
2. Create and check out a dedicated `cleanvibe-onboarding` branch — **the
   default branch is left untouched**
3. *Prepend-or-write* an onboarding `CLAUDE.md` and `queue.md`: if the repo
   already has them, the fresh block goes on top (newest first) and the
   original content is preserved below — re-running just layers another block
4. Inject `.gitignore` only if missing. **No `data_lake/`** (it is a real
   codebase, nothing was dropped in) and **no README overwrite**
5. Commit the onboarding scaffold on the branch
6. Launch Claude Code inside the project

The onboarding `queue.md` is small and focused: read & document the repo,
make existing docs accurate, **rewrite `CLAUDE.md` to the repo's real
development practices**, add tests/CI if sparse, then synthesize any existing
planning artifacts and hand off to the repo's own `todo.md`.

### Replicate a paper

`cleanvibe replicate` takes a **clawRxiv** reference, an **arXiv/alphaxiv**
reference, a **plain URL** to non-arXiv research, **or** a folder name:

**From a clawRxiv paper (skill-first):**

```
cleanvibe replicate https://www.clawrxiv.io/abs/2605.02609
cleanvibe replicate clawrxiv:2605.02609
```

[clawRxiv](https://www.clawrxiv.io/) publishes papers authored autonomously by
AI agents and exposes a JSON API (`/api/abs/<id>`) that **differentiates the
paper content, abstract, and skill file** (an agent-runnable replication
recipe). That separation is the purest recipe-first case, so clawRxiv gets its
own dedicated mode. The scaffold fetches all three up front: the paper content
is written to `replication_target/source/paper.md` (committed), and when
clawRxiv ships a separate skill file it lands at `replication_skill.md` at the
root (otherwise the recipe is embedded in the content and the queue tells the
agent to extract it). There is **no `download_paper.py`** — the API returns
everything in one call — and the generated `queue.md`/`SKILL.md` are
**skill-first**: go live early, run the recipe, verify it against the paper,
check all references, then fill only the gaps. clawRxiv ids look arXiv-shaped,
so a bare id stays arXiv — use a `clawrxiv.io` URL or `clawrxiv:<id>` to select
clawRxiv mode.

**From an arXiv / alphaxiv paper:**

```
cleanvibe replicate https://arxiv.org/abs/1706.03762
cleanvibe replicate https://www.alphaxiv.org/overview/2201.02177
cleanvibe replicate https://doi.org/10.48550/arXiv.1706.03762
cleanvibe replicate 1706.03762v5
```

Any arXiv/alphaxiv id or URL is accepted — `/abs/`, `/pdf/`, `/html/`,
`/src/`, alphaxiv's primary `/overview/`, `/audio/`, `/forum/`, the arXiv
**DOI** form (`doi.org/10.48550/arXiv.<id>`), `arXiv:<id>` citation style,
trailing slugs and query strings all resolve. A pinned `vN` **version** is
preserved (recorded in `paper.json` and used for the download), not silently
dropped. This will:
1. Fetch the paper's metadata from the arXiv API (with **429-aware
   retry/backoff** — arXiv rate-limits, so requests honour `Retry-After`
   and back off rather than crashing)
2. Create `replicating-<paper-slug>/` (silently `-2`/`-3` if it already exists)
3. Scaffold a standalone replication project: cleanvibe conventions
   (`CLAUDE.md`, `queue.md`, `data_lake/`) **plus** the replication structure —
   `SKILL.md` (the agent-executable replication plan), `download_paper.py`
   (fetches the arXiv **LaTeX/e-print source** and extracts it to
   `replication_target/source/`, with the PDF as a fallback), the paper's home
   `replication_target/` (gitignored — never in `data_lake/`; the authors' code
   is cloned here as a git submodule), `paper.json`, and `.github/workflows/`
   that build a GitHub Pages findings site, a transportable PDF report, and a
   downloadable ZIP replication package
4. Initialize a git repo with an initial commit
5. Launch Claude Code inside the project

The generated scaffold is built around the **efficient, recipe-first path**:

- **Source, not HTML.** `download_paper.py` downloads the arXiv **e-print
  source** (`arxiv.org/src/<id>`) and extracts the `.tex` to
  `replication_target/source/`. The `.tex` is far more token-efficient than the
  rendered HTML, which embeds figures as huge base64 data-URIs you'd otherwise
  have to strip. The raw archive is gitignored; the extracted `source/` is
  committed. The `cleanvibe replicate` command runs this extraction itself as a
  **second commit before launching Claude**, so the agent opens onto an
  already-extracted, already-committed paper.
- **Consent before running code.** Because a replication runs code you didn't
  write (the recipe / cloned scripts / a downloaded zip), the generated
  `queue.md`'s **first step** makes the agent stop and get your explicit consent
  before executing any external/cloned code. Reading the paper, source, and
  recipe is fine; *running* third-party code is the gated action.
- **Find the recipe FIRST.** Authors very often ship a reproduction recipe
  right in the paper source (usually near the end): a `SKILL.md`/`AGENTS.md`, a
  `reproduce.*`/`replicate.*`/`run.sh` script, a Makefile target, a Dockerfile,
  or a downloadable **replication zip**. The generated `queue.md`/`SKILL.md`
  tell the agent to find it (copying a recipe to `replication_skill.md`,
  extracting a zip into `replication/`) and **run it first**, *before* any deep
  paper analysis — then verify its output against the paper, check **all** the
  paper's references, and only reimplement the gaps the recipe didn't cover.
- **Go live early.** The agent is told to create a PUBLIC GitHub repo and push
  near the start, so every commit pushes and Pages/CI build as the work goes —
  not left local-only.

**From a plain URL (research that isn't on arXiv):**

```
cleanvibe replicate https://some-lab.org/papers/cool-thing.pdf
cleanvibe replicate https://openreview.net/forum?id=XXXX
```

When the argument is a plain `http(s)` URL that isn't an arXiv/clawRxiv
reference, cleanvibe **downloads it** as the replication source — the page or
PDF lands in `replication_target/source/` (`paper.pdf` or `paper.html`,
detected automatically), provenance is recorded in `source.json`, and the
scaffold's wording reflects that the source is already present. Same
429-aware retry/backoff as arXiv mode. Use it for research hosted on lab
sites, OpenReview, journal pages, or anywhere that isn't arXiv/clawRxiv.

**From a folder you fill yourself (manual drop-in mode):**

```
cleanvibe replicate my-paper-replication
```

When the argument is **not** an arXiv/alphaxiv reference (and not a URL) it is
treated as a folder name and a *manual drop-in* project is scaffolded — no
metadata
fetch, no `download_paper.py`, no `paper.json`, no network. You drop the
paper PDF(s) into `replication_target/` and any datasets/notes into
`data_lake/` yourself; the scaffolded `CLAUDE.md` / `queue.md` / `SKILL.md`
/ `README.md` say so up front, and the first queue step makes the agent
**stop and ask you for the paper** if `replication_target/` is empty rather
than invent one. Injection is non-destructive: you can create the folder,
drop your PDF in, *then* run `cleanvibe replicate ./that-folder` — nothing
you put there is overwritten.

Every replication produces three compounding artifacts: the runnable
replication, a published findings report, and the reusable `SKILL.md`
methodology. See `docs/replication_framing.md` for the full vision.

### Options

```
cleanvibe new my-project --dry-run        # Preview what would be created
cleanvibe new my-project --no-claude      # Skip launching Claude Code
cleanvibe clone REPO path --dry-run       # Preview what would be done
cleanvibe replicate URL --dry-run         # Preview the arXiv replication scaffold
cleanvibe replicate FOLDER --dry-run      # Preview the manual drop-in scaffold
cleanvibe replicate URL --no-claude       # Scaffold without launching Claude
cleanvibe --version                       # Show version
```

## Why?

Most people struggle with blank repo paralysis, poor commit hygiene, and AI assistants that ramble without producing durable artifacts. `cleanvibe` solves this by injecting a disciplined thinking contract into every project from the start.

The `CLAUDE.md` template enforces:
- Commit early and often with meaningful messages
- No planning-only modes -- all thinking produces files and commits
- Keep documentation up to date as the project evolves
- Use `planning/` directories for exploration instead of internal planning modes

## Cross-platform

Works on Windows, Linux, and macOS. Zero dependencies beyond Python 3.9+.

## Website

Full walkthrough — what cleanvibe is and what each subcommand does — at the
project site (built from `pages/` and deployed by GitHub Actions):
**https://cleanvibe.emmaleonhart.com/**

## Stability

As of **v1.0.0**, cleanvibe commits to the following contract (semantic
versioning from here on):

- **Subcommands** `new`, `clone`, `convert`, and `replicate` are stable. Their
  core behavior will not change incompatibly within the 1.x line.
- **Injected files**: `new` guarantees `CLAUDE.md`, `README.md`, `queue.md`,
  `.gitignore`, and `data_lake/.gitkeep`. `replicate` always guarantees
  `SKILL.md`, `CLAUDE.md`, `queue.md`, and `replication_target/`; in arXiv
  mode it additionally guarantees `paper.json` and `download_paper.py`; in
  clawRxiv mode it guarantees `paper.json` and
  `replication_target/source/paper.md` (and `replication_skill.md` when
  clawRxiv ships a separate skill file) but **no** `download_paper.py` — the
  API returns everything in one call. Both `paper.json` and `download_paper.py`
  are absent by design in manual drop-in mode — there is no metadata to fetch.
- **Non-destructive by contract**: `clone` and `convert` never overwrite
  existing files — `clone` prepends; `convert` only injects what is missing.
  `replicate` in arXiv mode never errors on a name collision (silent
  `-2`/`-3` suffix); in folder mode it injects only what is missing so a
  pre-dropped paper is never clobbered.
- **Template wording** may evolve (improvements to the workflow contract are
  not breaking); the *set* of guaranteed files and the subcommand contracts
  above are what 1.x holds stable.
- **Zero runtime dependencies** remains a hard guarantee for the 1.x line.

## License

MIT
