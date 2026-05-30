# CleanVibe Skill Distribution — Design

**Date:** 2026-05-30
**Status:** Approved (pivotal decisions answered in brainstorming)

## Problem

The same reusable workflow prose is duplicated across four places:

1. `cleanvibe/cleanvibe/templates.py` — `_CLAUDE_CORE_RULES`, `_WRITING_SECTION`,
   `_common_claude_tail` — injected into every scaffolded repo's `CLAUDE.md`.
2. The user's global `~/.claude/CLAUDE.md`.
3. The user's auto-memory feedback files (cron-local, emergency-stop, three-cron,
   avoid-honest).
4. Every cleanvibe-scaffolded repo's own `CLAUDE.md` (a frozen copy of #1).

Result: `CLAUDE.md` files are bloated (~120 lines of workflow/cron/emergency prose),
and a change to any rule has to be hand-propagated to ~30 repos. The blocks are all
**trigger-based behaviors**, which is exactly what the Claude Code `SKILL.md` format is
for — a skill's `description` stays in context and the skill fires on its trigger.

## Goal

Convert the reusable blocks into **six standalone skills**, make them:

- usable **globally** (`~/.claude/skills/`), and
- shipped **by default** by cleanvibe into every scaffolded repo (`.claude/skills/`),
  vendored and committed into each repo.

Then **trim** the `CLAUDE.md` files (global, templates, and all existing repos) down to
a short `## Skills` pointer.

## The six skills (one per concern)

| Skill slug | Trigger (`description`) | Source block |
|---|---|---|
| `emergency-stop` | repeated "stop" / explicit halt demand | Emergency Stop Mode |
| `cron-is-local` | user mentions cron / schedule / recurring task | Cron jobs — LOCAL by default |
| `autonomous-loop` | starting extensive / large-scale autonomous work | Three-cron playbook |
| `queue-driven-workflow` | any multi-step work in a cleanvibe project | Workflow Rules + queue/todo/devlog + Testing |
| `writing-style` | writing reports, commits, devlog entries, prose | Writing (no "honest") |
| `cleanvibe-update-check` | session start, weekly | Check cleanvibe for updates (**redefined**) |

`cleanvibe-update-check` is redefined: instead of folding new sections into `CLAUDE.md`,
it now refreshes `.claude/skills/` to the latest cleanvibe-shipped versions (weekly,
opportunistic, via `https://cleanvibe.emmaleonhart.com/updates.md`).

Each `SKILL.md` carries YAML frontmatter:

```yaml
---
name: <slug>
description: Use when <trigger> — <one-line purpose>.
---
```

## Architecture / data flow

```
cleanvibe/cleanvibe/skills.py        ← SINGLE SOURCE OF TRUTH (string constants)
        │   write_skills(dest_root)
        ├──► ~/.claude/skills/<slug>/SKILL.md          (global, personal use)
        └──► <repo>/.claude/skills/<slug>/SKILL.md      (per-repo, vendored + committed)

templates.py   → CLAUDE.md workflow/cron/emergency/writing blocks REPLACED by a
                 short "## Skills" pointer section.
scaffold.py    → new / convert / clone / replicate / research all call write_skills().
```

**Why string constants in `skills.py` (not real package-data files):** mirrors the
established `templates.py` pattern exactly (string constants, zero package-data),
preserving cleanvibe's zero-dependency / flat-layout packaging guarantee. Honors the
project rule "DO NOT innovate with different approaches — follow established patterns."
`write_skills()` is the one function that materializes the constants to disk; both the
global install and the per-repo scaffold go through it, so there is a single code path
and no drift.

## Stages

### Stage A — Author the skills (in cleanvibe)
- New module `cleanvibe/cleanvibe/skills.py`:
  - `SKILLS: dict[str, str]` — slug → full `SKILL.md` text (frontmatter + body),
    ported verbatim from the existing prose (no paraphrase; keep the exact wording the
    repos already rely on).
  - `write_skills(dest_root: Path, *, overwrite: bool = True) -> list[Path]` — writes
    `dest_root/.claude/skills/<slug>/SKILL.md` for each skill; returns paths written.
- Unit tests in `tests/` (network-free): assert all six slugs present, every file has
  valid frontmatter with `name`/`description`, `write_skills` creates the expected tree.

### Stage B — Install globally + trim global CLAUDE.md
- Populate `~/.claude/skills/<slug>/SKILL.md` from `skills.py`.
- Trim `~/.claude/CLAUDE.md`: remove the duplicated workflow / cron / emergency / writing
  blocks, replace with a `## Skills` pointer to `~/.claude/skills/`. **Keep** the
  project-specific content (Wikidata tasks, Aelaki API notes, Python interpreter paths,
  Gaiad structure). Leave the auto-memory feedback files untouched (separate mechanism).

### Stage C — Wire cleanvibe + cut a release
- `scaffold.py`: every mode (`new` / `convert` / `clone` / `replicate` / `research`)
  calls `write_skills(project_root)` so each scaffolded repo gets `.claude/skills/`.
  For `convert`/`clone` (non-destructive, missing-only), skills are written if absent.
- `templates.py`: replace the `_CLAUDE_CORE_RULES` / `_WRITING_SECTION` /
  `_common_claude_tail` blocks inside the generated `CLAUDE.md` with the `## Skills`
  pointer. (The shared helpers may shrink or be removed; keep any text still needed
  inline, e.g. the generated-by-version footer if desired.)
- Bump version `1.13.1` → `1.14.0`, document in `pages/updates.md`, `devlog.md`, `README.md`.
- Update tests for the new CLAUDE.md shape + skills presence.

### Stage D — Migrate existing repos
- Migration script `migrate_repos_to_skills.py` (under cleanvibe, or a top-level tool):
  - Discover git repos under `C:\Users\Immanuelle\Documents\Github` whose `CLAUDE.md`
    contains the duplicated blocks (marker strings: `"Emergency Stop Mode"`,
    `"three-cron"`, `"LOCAL by default"`, `"## Writing"`+`honest`).
  - For each matching repo:
    1. `git fetch origin`; verify clean working tree and that the branch can **ff-only**
       fast-forward. Dirty or diverged → **skip and report**, never force / reset.
    2. `write_skills(repo_root)` → `.claude/skills/` (vendored, committed).
    3. Trim its `CLAUDE.md` blocks → `## Skills` pointer.
    4. Commit (clear message) and **push**.
  - `--dry-run` (default) lists planned changes per repo; `--apply` performs them.
  - End-of-run summary: migrated / skipped (with reason) / failed.

## CLAUDE.md pointer block (what replaces the prose)

```markdown
## Skills

Workflow behaviors live as skills in `.claude/skills/` (auto-discovered by Claude Code):
`emergency-stop`, `cron-is-local`, `autonomous-loop`, `queue-driven-workflow`,
`writing-style`, `cleanvibe-update-check`. They are vendored here and kept current by
the `cleanvibe-update-check` skill. The rest of this file is project-specific.
```

## Error handling & safety

- **Marker-gated:** migration only edits a repo that actually contains the blocks.
- **Sync-before-edit:** `git fetch` + ff-only; dirty/diverged repos skipped + reported.
- **Dry-run first:** `--dry-run` is the default; `--apply` is explicit.
- **Per-repo commits:** one focused commit each; failures don't abort the batch.
- **Non-destructive scaffold paths** (`convert`/`clone`) write skills only if missing.

## Testing

- `skills.py`: network-free unit tests (slug set, frontmatter validity, write tree).
- `scaffold`: assert scaffolded projects contain `.claude/skills/<slug>/SKILL.md` and the
  trimmed CLAUDE.md pointer.
- Migration script: a dry-run smoke test against a temp repo fixture (no network/push).

## Out of scope (YAGNI)

- Rewriting the auto-memory feedback files (different mechanism; left intact).
- A general plugin/marketplace packaging of the skills.
- Touching non-cleanvibe repos that never had the blocks.
