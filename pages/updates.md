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

**Scope.** Skills are vendored into every cleanvibe 2 project and every
`legacy` `new`, `convert`, `clone`, `research`, `original` and `chat` project. `cleanvibe replicate` projects are a bounded
paper-replication workflow with their own definition of done and are not
auto-vendored the skill set. The `autonomous-loop` (three-cron) skill is itself
self-exempting for replication-style bounded work.

---

## v2.0.2 (2026-09-27) — one simple work loop; the chat-test proposals

**`autonomous-loop` is replaced (existing repos: copy the text below).** One
cron every half hour (`7,37 * * * *`) with the prompt "commit and push any and
all changes, then continue working on the queue". No separate flush or status
crons. An empty research queue refills from `research/SUMMARY.md` before
idling. If a session is running the old three crons, delete them and create
this one.

cleanvibe 2 projects also get six clarifications in `CLAUDE.md` (from case
study 04): "nothing to go on" means the user has said nothing at all; no
strict instructions is not no work (research the subject); if the user says
the tool or chat is the subject, it is; the intake says the user is "present",
not "steering"; ask one short question when a present user's worry could
point either way.

`.claude/skills/autonomous-loop/SKILL.md`, full text:

````markdown
---
name: autonomous-loop
description: Use when the user wants a long stretch of autonomous work (hours, overnight, or while they are away) — set up one local cron that every half hour commits and pushes everything and keeps working the queue. Also use when deciding whether that cron should keep running.
---

# Autonomous loop — one cron, every half hour

When the user wants you to keep working on your own for a long stretch (hours,
overnight, while they are away), set up **one** local `CronCreate` job:

- **Schedule:** `7,37 * * * *` (every half hour, off the busy :00/:30 marks),
  recurring.
- **Prompt:** `[cleanvibe cron] Commit and push any and all changes, then
  continue working on the queue.`

That's the whole loop. Each time it fires:

1. **Commit and push** everything that has changed, with messages that say what
   and why. Push only if the repo has a remote. No empty commits.
2. **Continue working on the queue.** Take the top item in `queue.md` you can
   do and do it, then the next, for as long as it makes sense. Delete finished
   items from `queue.md` and log them in `devlog.md` in the same commit.
3. **When the queue runs dry, refill it before idling.** In a research project,
   take the top open question in `research/SUMMARY.md`, plan it into
   `queue.md`, and work it. Otherwise take the next `todo.md` item that is
   unblocked, bounded and checkable. If there is truly nothing, the tick is
   **idle**: say so in one line. An idle tick is normal, not a problem to solve.

The job is session-local (`durable: false`): it fires only while this session
runs, so a later session sets it up again if the user still wants autonomous
work.

## The work keeps the project's normal standards
- Claim something works only after running it. Never weaken, skip or delete a
  test to get green; record the defect instead.
- If you don't understand something well enough to do it, write the question
  down (a queue item, or `INTENT.md`) instead of guessing.

These are how the work is done, not reasons to stop the loop.

## Keep it running
- **Do not turn the cron off yourself.** Not because the queue is empty, not
  because a tick failed, not because something looks risky, and not at the
  end of a burst of work. Only the user stops it (directly, or through the
  `emergency-stop` skill).
- If something goes wrong, say so plainly in your next message and carry on
  with whatever is still safe to do.
- In a cleanvibe project, the thirty-minute intake in CLAUDE.md decides when
  the loop starts. Elsewhere, start it when the user asks for autonomous work.

**Why one cron:** earlier versions ran separate hourly work, flush and status
crons. In practice the flushes and status reports weren't useful, and one
item per hour left long idle stretches (case study 05). One half-hourly
"commit, push, keep going" does the work with less ceremony.

Replication projects (`cleanvibe replicate`) are bounded jobs and do not use
the loop.
````

---

## v2.0.0 (2026-09-26) — cleanvibe 2: low-information sessions; skill revisions

cleanvibe 2 changes how new projects start (see the README). For **existing
repos**, what matters here is three skills:

- **`autonomous-loop` — rewritten.** The same three staggered crons (work
  `:03`, flush `:15`, status `:42`) and the same standards, without the
  start / kill-on-refill / restart choreography and the pinned tail items.
  Agents read those as licence to switch the loop off. Now only the user stops
  the crons; an idle tick is normal. If your `queue.md` still has an
  "Always last — restart the cron" section, you can delete it.
- **`research-practice` — new.** Research on any topic (not only CS papers):
  pin the question down (ask only if the user is present; otherwise infer and
  record the assumption), survey wide then deep, `research/SUMMARY.md` as a
  living answer with confidence, `research/sources.md`, claims tied to sources.
- **`queue-driven-workflow` — revised.** Framed as the development practice;
  in a cleanvibe 2 project it creates `queue.md`/`todo.md`/`devlog.md` when the
  work turns into a build; CI once the project has a remote.

Also: AskUserQuestion is for when the user is clearly present and replying;
otherwise decide and write the assumption down. Add `research-practice` to the
skill list in your `CLAUDE.md` `## Skills` section.

`.claude/skills/autonomous-loop/SKILL.md`, full text:

````markdown
---
name: autonomous-loop
description: Use when the user wants a long stretch of autonomous work (hours, overnight, or while they are away) — set up three local hourly crons (work, flush, status) that keep the work moving, committed and readable. Also use when deciding whether those crons should keep running.
---

# Autonomous loop — three hourly crons

When the user wants you to keep working on your own for a long stretch (hours,
overnight, while they are away), set up three local `CronCreate` jobs. They are
session-local (`durable: false`): they fire only while this session runs and end
with it, so a later session sets them up again if the user still wants
autonomous work. Stagger the minutes so the ticks don't collide:

1. **Work, `3 * * * *`.** Each tick:
   - **Sync.** `git fetch`, then fast-forward or rebase. Never force-push, never
     `reset --hard`, never discard work from another machine or session.
   - **Work.** Take the top item in `queue.md` that you can do, and do it. If
     nothing in the queue is doable, take the next `todo.md` item that is
     unblocked, bounded and checkable, plan it into `queue.md`, then do it.
     If there is still nothing, the tick is **idle**: say so in one line and
     stop there. An idle tick is normal, not a problem to solve.
   - **Commit and push**, deleting finished items from `queue.md` and logging
     them in `devlog.md` in the same commit.
   - **Report** in one line: the commits, or `idle: <reason>`.
2. **Flush, `15 * * * *`.** Commit and push anything left uncommitted. No empty
   commits. (Session transcripts are committed by the session-log hook, not by
   this cron.)
3. **Status, `42 * * * *`.** Report only, no changes: what advanced since the
   last report (commits), the queue as it stands, anything blocked (with its
   not-done tag and the specific blocker), and test health.

## The work keeps the project's normal standards
- Claim something works only after running it. Never weaken, skip or delete a
  test to get green; record the defect instead. Check CI, not only local runs.
- If you don't understand something well enough to build it, write the question
  down (a queue item, or `INTENT.md`) instead of guessing.

These are how the work is done, not reasons to stop the loop.

## Keep the crons running
- **Do not turn the crons off yourself.** Not because the queue is empty, not
  because a tick failed, not because something looks risky, and not at the end
  of a burst of work. Only the user stops them (directly, or through the
  `emergency-stop` skill).
- When something goes wrong, the loop is how the user finds out: report it in
  the next status tick and carry on with whatever is still safe to do.
- If the queue is replanned mid-session, leave the crons alone; the next work
  tick picks up the new top item.
- In a cleanvibe project, the thirty-minute intake in CLAUDE.md decides when
  the loop starts. Elsewhere, start it when the user asks for autonomous work.

**Why:** long autonomous stretches usually fail by quietly losing the thread.
The work tick keeps progress steady and committed, the flush makes sure nothing
is lost, and the status tick keeps the thread readable for when the user comes
back.

Replication projects (`cleanvibe replicate`) are bounded jobs and do not use
the loop.
````

`.claude/skills/research-practice/SKILL.md`, full text:

````markdown
---
name: research-practice
description: Use when the work in a project is research on any topic, not only computer science — pinning down the question, gathering and weighing sources, keeping notes with citations, and maintaining a living summary — whether it is a single question or a long-running inquiry.
---

# Research practice

For research on any subject: history, a technical field, a market, a hobby, a
health question, a policy debate. It suits a single question and a long-running
inquiry that grows over months. (Replicating one specific paper is a different
job; that is `cleanvibe replicate`.)

## Layout (create it when the research starts, not before)
- `research/SUMMARY.md`: the living answer. What is known now, how sure, what
  is contested, what is still open. Rewrite it as understanding changes; it
  should always make sense read on its own.
- `research/sources.md`: one entry per source, with the citation or link, date
  accessed, what kind of source it is (primary data, peer-reviewed, reporting,
  opinion, vendor material), what it contributes, and how far to trust it.
- `research/notes/`: one Markdown file per sub-question, with every claim tied
  to a source.
- Downloads and datasets go in `data_lake/`; throwaway fetches go in `scratch/`.

## How to work
- **Pin the question down.** If the user is here and replying, ask them
  (AskUserQuestion is fine then): what they want to know, why, how deep to go,
  and what would count as an answer. If they are not, infer the question from
  the chat, the material in `data_lake/` and the project name, write it at the
  top of `SUMMARY.md` as a stated assumption, and start.
- **Survey wide, then go deep.** First map the main positions and the key
  sources; then dig into what matters for the user's question.
- **Every claim gets a source.** Keep what a source says separate from your own
  inference, and label the inference.
- **Weigh sources rather than counting them.** Prefer primary and established
  sources, note dates and conflicts of interest, and when sources disagree,
  record both positions and what would settle it instead of averaging them.
- **Say how sure you are**, in `SUMMARY.md` and when you report back: lead with
  the answer, then the confidence, then the evidence.
- **Long-running inquiries** get a dated "What changed" entry in `SUMMARY.md`
  each session, so the user can see how the picture moved.
- **Link, don't copy.** Quote briefly; never commit whole copyrighted texts.
````

`.claude/skills/queue-driven-workflow/SKILL.md`, full text:

````markdown
---
name: queue-driven-workflow
description: Use when the work in a cleanvibe project is software development or any other multi-step build — plan into queue.md first, the todo.md → queue.md → devlog.md flow, delete-don't-check completion, task-tool mirroring, and tests/CI discipline.
---

# Queue-driven workflow (development practice)

In a cleanvibe 2 project nothing is set up for this in advance. When the work
turns into building something over several steps, create `queue.md`, `todo.md`
and `devlog.md` if they don't exist yet, and work this way from then on.

## Workflow Rules
- **Commit early and often.** Every meaningful change gets a commit with a clear message explaining *why*, not just what.
- **Plan into `queue.md` first, then execute.** When entering planning mode (or doing any non-trivial multi-step work), the FIRST action is to write the plan into `queue.md` as concrete items. Only then begin executing. This means an interrupted session can resume from the queue — the plan does not live only in chat context.
- **Finishing an item = delete from `queue.md` + append to `devlog.md`, then commit and push.** When a queue item is done, **delete the item from `queue.md`** and **append a dated entry to `devlog.md`** recording what was completed, in the *same commit as the work*, then push (if the repo has a remote). Never mark an item done in place (no `[x]`, no "✓", no "DONE"). `queue.md` only ever holds not-yet-done work; `devlog.md` is where "done" lives.
- **Mirror `queue.md` into the task tool.** TaskCreate items as you add them to queue.md; mark `in_progress` when starting; `completed` when done. The two views must not drift.
- **Keep CLAUDE.md up to date.** As the project takes shape, record architectural decisions, conventions, and anything needed to work effectively in this repo.
- **Update README.md regularly.** It should always reflect the current state of the project for human readers.

## Queue and longer-horizon work
- **`queue.md`** — what's being worked on right now. Items get deleted on completion; do not leave checkmarks or status indicators behind. If it's not in `queue.md`, it's not in scope for the current session.
- **`todo.md`** — the **long-term horizon** of the project. Multi-session goals, architectural ambitions, future capabilities. Items in `todo.md` are *abstract*: they describe a destination, not a step. When work begins, an item is pulled from `todo.md`, decomposed into concrete executable steps in `queue.md`, mirrored into the task tool, and executed. As `queue.md` drains, refill it from the next `todo.md` item.
- **`devlog.md`** — where **"done" lives**. Every finished queue item is deleted from `queue.md` and appended as a dated entry here, in the same commit as the work. Releases (tag + one-line note) and notable milestones also go here.
- **Flow:** `todo.md` (abstract horizons) → `queue.md` (concrete steps) → task tool (in-flight work) → `devlog.md` + `git log` (history). Items only ever flow forward.
- **When to stop and hand back:** `queue.md` is empty, what is left in `todo.md` is still too abstract to break down, and tests (and CI, if the project has a remote) pass.

## Testing
- **Write unit tests early.** As soon as there is testable logic, create a test file. Use `pytest` for Python projects or the appropriate test framework for the language in use.
- **Set up CI once the project has a GitHub remote.** A `.github/workflows/ci.yml` that runs the test suite on push and pull request. Keep it simple — install dependencies and run tests.
- **Keep tests passing.** Do not commit code that breaks existing tests. If a change requires updating tests, update them in the same commit.
````

---

## v1.18.0 (2026-09-26) — `cleanvibe chat`, private by default, starting prompts

No skill bodies changed; nothing in `.claude/skills/` needs refreshing.

- **New mode `cleanvibe chat`**: a git-tracked conversation about one topic.
  Existing projects are unaffected.
- **Private by default.** Generated queues and CLAUDE.md now create repos with
  `gh repo create --private`, and the Pages workflows skip the deploy on a
  private repo (uploading the report as a workflow artifact). If this repo's
  `pages.yml` was generated by an older cleanvibe and the repo is private, the
  Pages deploy will fail on every push. Copy the `if:` gate from a fresh
  `cleanvibe research` scaffold, or make the repo public.
- **Starting prompt.** New scaffolds launch Claude with a first message
  describing the mode; `!runClaude.bat` carries the same prompt.
- **Dangling section references (fix in existing repos).** Projects generated
  by `new`, `research` or `original` since v1.14.0 have `queue.md` / `todo.md`
  lines like ``See `CLAUDE.md` § "Workflow Rules"``, pointing at CLAUDE.md
  sections that moved into skills. Replace each one with a pointer to the
  skill: "Workflow Rules" and "Queue and longer-horizon work" →
  `queue-driven-workflow`; "Autonomous productivity loop" → `autonomous-loop`.
  `cleanvibe doctor` lists them (check `section-refs`).

---

## v1.15.0 (2026-06-05) — Copyright fix: replication papers are NEVER committed

`cleanvibe replicate` was committing the paper into the generated repo (the
extracted arXiv LaTeX `source/`, the clawRxiv `paper.md`, the downloaded URL
source), which redistributes a copyrighted work. Fixed: the **entire**
`replication_target/` tree is now gitignored (`replication_target/*` +
`!replication_target/.gitkeep`) and the paper is only ever populated **locally**
by `download_paper.py`. clawRxiv and URL modes gained their own
`download_paper.py` (re-fetch from the API / recorded URL); the arXiv scaffolder
still downloads before launch but commits nothing. Authors' code added as a
submodule now needs `git submodule add -f` (gitignored path; only the gitlink is
committed).

**If you have an older replication repo:** check whether the paper text was
committed (`git ls-files replication_target`). If so, replace your `.gitignore`'s
`replication_target/*.pdf`-style lines with `replication_target/*` +
`!replication_target/.gitkeep`, then `git rm -r --cached replication_target`
(keeping `.gitkeep`) and commit — the paper should never have been in history.

(Replication projects are not auto-vendored the skill set, so this is a
template/behavior change rather than a skill update.)

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
