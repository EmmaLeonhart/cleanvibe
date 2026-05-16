# cleanvibe

A tiny Python CLI that scaffolds AI-assisted coding projects and launches Claude Code.

`cleanvibe` is not a coding tool. It's a **state initializer** -- it removes the friction between "I want to build something" and "Claude is working inside a well-structured environment." The real value lives in the `CLAUDE.md` it injects: an opinionated behavior contract that enforces documentation discipline, meaningful commits, and iterative file-based thinking.

## Install

```
pip install cleanvibe
```

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
make existing docs honest, **rewrite `CLAUDE.md` to the repo's real
development practices**, add tests/CI if sparse, then synthesize any existing
planning artifacts and hand off to the repo's own `todo.md`.

### Replicate a paper

```
cleanvibe replicate https://arxiv.org/abs/1706.03762
```

Accepts an arXiv **or alphaxiv** id / abs URL / pdf URL. This will:
1. Fetch the paper's metadata from the arXiv API
2. Create `replicating-<paper-slug>/` (silently `-2`/`-3` if it already exists)
3. Scaffold a standalone replication project: cleanvibe conventions
   (`CLAUDE.md`, `queue.md`, `data_lake/`) **plus** the replication structure —
   `SKILL.md` (the agent-executable replication plan), `download_paper.py`,
   `replication_target/` (the paper itself lives here, gitignored — never in
   `data_lake/`; the authors' code is cloned here as a git submodule),
   `paper.json`, and `.github/workflows/` that build a GitHub Pages findings
   site, a transportable PDF report, and a downloadable ZIP replication package
4. Initialize a git repo with an initial commit
5. Launch Claude Code inside the project

Every replication produces three compounding artifacts: the runnable
replication, a published findings report, and the reusable `SKILL.md`
methodology. See `docs/replication_framing.md` for the full vision.

### Options

```
cleanvibe new my-project --dry-run        # Preview what would be created
cleanvibe new my-project --no-claude      # Skip launching Claude Code
cleanvibe clone REPO path --dry-run       # Preview what would be done
cleanvibe replicate URL --dry-run         # Preview the replication scaffold
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
project site (built from `site/` and deployed by GitHub Actions):
**https://immanuelle.github.io/cleanvibe/**

## Stability

As of **v1.0.0**, cleanvibe commits to the following contract (semantic
versioning from here on):

- **Subcommands** `new`, `clone`, `convert`, and `replicate` are stable. Their
  core behavior will not change incompatibly within the 1.x line.
- **Injected files**: `new` guarantees `CLAUDE.md`, `README.md`, `queue.md`,
  `.gitignore`, and `data_lake/.gitkeep`. `replicate` additionally guarantees
  `SKILL.md`, `paper.json`, `download_paper.py`, and `replication_target/`.
- **Non-destructive by contract**: `clone` and `convert` never overwrite
  existing files — `clone` prepends; `convert` only injects what is missing.
  `replicate` never errors on a name collision (silent `-2`/`-3` suffix).
- **Template wording** may evolve (improvements to the workflow contract are
  not breaking); the *set* of guaranteed files and the subcommand contracts
  above are what 1.x holds stable.
- **Zero runtime dependencies** remains a hard guarantee for the 1.x line.

## License

MIT
