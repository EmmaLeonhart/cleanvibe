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

### Clone an existing repo

```
cleanvibe clone https://github.com/user/repo
```

This will:
1. `git clone` the repository
2. Check for missing `CLAUDE.md`, `README.md`, `.gitignore`
3. Inject any missing files without overwriting existing ones
4. Launch Claude Code inside the project

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

## License

MIT
