# cleanvibe — skill / template update index

This page is the canonical, hand-maintained index of every skill, section, and
convention that cleanvibe currently ships. Every generated `CLAUDE.md` carries
a `## Skills` pointer naming this page; the `cleanvibe-update-check` skill reads
it weekly.

**How to read this page (v1.14.0+).** As of **v1.14.0** the workflow behaviors
ship as standalone **skills** under `.claude/skills/`, not as inlined `CLAUDE.md`
prose. Entries are keyed by the cleanvibe version that introduced or revised a
skill. If a `.claude/skills/<slug>/SKILL.md` is older than what's described here,
update that file to match the wording here; don't paraphrase. Then bump the
*Last cleanvibe update check* date in the repo's `## Skills` section and commit
with a message naming which skills were refreshed.

(Historical: before v1.14.0 these same behaviors were inlined `CLAUDE.md`
sections and the check folded new *sections* into `CLAUDE.md`. The pre-v1.14.0
entries below are kept as a record; their content now lives in the skills.)

**Scope.** Skills are vendored into `cleanvibe new`, `convert`, `clone`, and
`research` projects. `cleanvibe replicate` projects are a bounded
paper-replication workflow with their own definition of done and are not
auto-vendored the skill set. The `autonomous-loop` (three-cron) skill is itself
self-exempting for replication-style bounded work.

---

## v1.14.0 (2026-05-30) — Workflow behaviors become standalone skills

The reusable workflow prose that used to be inlined into every generated
`CLAUDE.md` is now **six standalone skills**, vendored into each repo's
`.claude/skills/` and installable globally at `~/.claude/skills/`. `CLAUDE.md`
keeps only a short `## Skills` pointer plus project-specific content. Single
source of truth: `cleanvibe/skills.py` (`write_skills()`).

The six skills (slug — trigger):

1. **`emergency-stop`** — repeated "stop" / explicit halt demand → kill all
   running processes, background jobs, and this repo's GitHub Actions runs, then
   take no further actions until "emergency stop ended".
2. **`cron-is-local`** — user says "cron"/"schedule" → the in-session
   `CronCreate` tool, local, standing consent; just set it up.
3. **`autonomous-loop`** — starting extensive/large-scale autonomous work → the
   three-cron playbook (work-loop `3 * * * *`, auto-flush `15 * * * *`,
   status-report `42 * * * *`) with its full lifecycle.
4. **`queue-driven-workflow`** — any multi-step/planning work → plan into
   `queue.md` first; the `todo.md` → `queue.md` → `devlog.md` flow;
   delete-don't-check completion; task-tool mirroring; tests/CI discipline.
5. **`writing-style`** — writing any prose → avoid the self-congratulatory
   "honest"/"frank"/"candid"/"transparent" move; name failures flatly.
6. **`cleanvibe-update-check`** — session start, weekly → fetch this page and
   refresh `.claude/skills/` to the latest shipped versions.

**Migrating from v1.13.x and earlier:** delete the inlined Workflow Rules,
Writing, Cron, three-cron, weekly-update-check, and Emergency Stop sections from
your `CLAUDE.md`; add the six skill files under `.claude/skills/` (copy from a
freshly-scaffolded project or from cleanvibe's `skills.py`); replace the removed
prose with the `## Skills` pointer. The `migrate_repos_to_skills.py` script in
the cleanvibe repo automates exactly this.

---

## v1.11.0 (2026-05-26) — Autonomous productivity loop (three-cron playbook) + this update mechanism

### New section: "Autonomous productivity loop — the three-cron playbook"

Replaces the prior "Hourly status-report cron for extensive work" section
(single cron at the top of the hour) with a generalized **three-cron**
playbook that has shown the strongest empirical productivity in the
maintainer's own large-scale autonomous sessions. The three crons stagger
across the hour and play different roles:

1. **Work-loop cron — `3 * * * *` (hourly at :03)** — the engine. Sync remote
   (never force-push or `reset --hard`), take the top actionable `queue.md`
   item or promote one from `todo.md`, hold the hard rails (never fake,
   never weaken / skip / delete a test, never claim "works" without measuring,
   name unbuilt things plainly, verify CI not just local), commit + push,
   one-line report.
2. **Auto-flush cron — `15 * * * *` (hourly at :15)** — the backstop. Commit +
   push pending work; no empty commits.
3. **Status-report cron — `42 * * * *` (hourly at :42)** — the heartbeat,
   reporting only, no code changes.

**Lifecycle:**

- A fresh session **starts all three crons** as the opening queue item.
- A mid-session large-scale queue **re-fill kills the running crons** as its
  first item.
- Entering planning mode **disables** the crons.
- The last two queue items, always pinned at the tail, **ensure the three
  crons are running** and then **run the status-report independently** as an
  end-of-session summary.

Migrating from v1.10.x: delete the old single-cron section and the
single-cron bootstrap-queue references; add the three-cron section using the
wording in `cleanvibe/templates.py` `claude_md()` and `queue_md()`.

### New section: "Check cleanvibe for skill updates (weekly)"

The section you're reading from. Every generated `CLAUDE.md` carries a small
self-update pointer with three fields:

- *Generated by cleanvibe version:* the version that wrote the file.
- *Last cleanvibe update check:* the date the check last ran. **Weekly** —
  if the last-check date is more than 7 days ago, fetch this page and fold
  in any newer entries.
- *Updates source:* `https://cleanvibe.emmaleonhart.com/updates.md`.

The check is opportunistic: if `WebFetch` fails (offline, DNS, page down),
leave the date alone and try next session.

---

## v1.10.0 (earlier) — Bootstrap queue actually starts the cron

The bootstrap queue's opening step actually creates the local cron rather
than only describing the kill/restart lifecycle. (Now generalized to the
three-cron playbook in v1.11.0.)

## v1.9.0 (earlier) — Hourly status-report cron pinned in tail

`## Always last` section pinned at the tail of every generated `queue.md`,
restarting the hourly status cron and running a final status report.
(Generalized to ensure all three crons in v1.11.0.)

## v1.8.0 (earlier) — Cron jobs and scheduled work LOCAL by default

"Cron requests are local and immediate" section. A generic mention of "cron"
means the in-session `CronCreate` tool, run locally while the user is away.

## Earlier — Emergency stop mode + writing rules

Pinned in `claude_md()` since the first templated CLAUDE.md.
