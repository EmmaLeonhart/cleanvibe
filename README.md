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
4. Write `.gitignore` (sensible Python defaults)
5. Initialize a git repo with an initial commit
6. Launch Claude Code inside the project

### Clone an existing repo

```
cleanvibe clone https://github.com/user/repo
```

This will:
1. `git clone` the repository
2. Check for missing `CLAUDE.md`, `README.md`, `.gitignore`
3. Inject any missing files without overwriting existing ones
4. Launch Claude Code inside the project

### Options

```
cleanvibe new my-project --dry-run     # Preview what would be created
cleanvibe new my-project --no-claude   # Skip launching Claude Code
cleanvibe clone REPO path --dry-run    # Preview what would be done
cleanvibe --version                    # Show version
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
