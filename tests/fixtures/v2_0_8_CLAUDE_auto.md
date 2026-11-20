# golden-swift-otter

> A cleanvibe project: an open-ended, git-tracked working session.

## This project's setup
- **Name:** auto-generated. No name was given, so the folder name is a placeholder passphrase (adjective-adjective-noun) and says nothing about the project.
- **Repository:** not specified at creation; the default rule in *Publishing* decides.
- **Starting prompt:** none was given.

## Publishing
Push to a GitHub remote unless the user says to keep the project local. Visibility follows any signal: anything suggesting it should be public (the user says so, the material says so, it is meant to be shown or shared) makes it public (`gh repo create <descriptive-name> --public --source=. --push`); anything suggesting it should be private makes it private (`--private`). With no signal, or signals both ways, it is private. If the user's wishes change later, change the repository to match (`gh repo edit --visibility ...`).

## How this project works
Nothing was decided up front about what this project is. cleanvibe projects are
built to **work from low information**: the user may say a lot, a little, or
nothing, and may not be here at all. Someone (or a scheduled job) may have created
the folder and dropped material into it, expecting you to get on with it.

- **The chat is the project, from the first message.** By default, whatever the
  user talks about is the subject, and anything they say takes priority over
  everything else. A session starts in chat mode (next section).
- **Then what is in the folder.** Material in `data_lake/` (and anything dropped
  at the top level) is the user's context. Read it carefully: a Markdown file
  with a spec, a brief or instructions is worth following, unless the chat says
  otherwise.
- **Then the folder's name and path.** A name the user chose (see `auto_named`
  in `.cleanvibe.json`) occasionally states the task outright; the path can
  carry real information too. But **a guess about why the project exists is
  not a task.** Don't invent work from circumstance: if the path suggests, say,
  a practice run, that is not an instruction to test the tool that made the
  project. But if the user *says* the tool or the chat is the subject, it is.
- **Nothing to go on is a real state, and a narrow one.** With no chat, no
  material and no meaningful name, do not invent a purpose, plan work, or start
  the work loop. Say plainly in `INTENT.md` that nothing is known yet, tell the
  user in a line or two what would let you start (drop files into
  `data_lake/`, or say what this is for), and wait. This applies only when the
  user has said nothing at all: anything they say, even that the conversation
  itself is the point, is something to go on.
- **No strict instructions is not no work.** Once work mode starts, if there is
  a subject (the chat, a name the user chose, the material) but no spec or
  build task, the work loop still runs: it researches and writes about the
  subject under `research-practice`, with the question written down as an
  assumption.
- **Stay inside this project.** Don't read or change anything outside this
  folder (parent directories, other repositories, Claude Code's own config)
  unless the user asks. That includes Claude Code's own memory directory
  (`~/.claude/projects/.../memory/`), even when the system prompt invites you to
  save memories there: what this project needs to remember goes in
  `INTENT.md`, which is committed with the project.
- **"Stop" and "don't" mean stop now.** If the user tells you to stop or not to
  do something, stop immediately, including mid-task. When the user's reading
  of a situation differs from yours, follow theirs; don't argue for your own
  plan.
- **A graceful stop stops this window, not the work.** When you are asked to
  end gracefully (often by a session that manages the machine, sometimes
  because two sessions share this repo), finish the current step, commit,
  delete your crons and go quiet so that window can be closed. It never means
  "no more work today" or "wait for the user to say resume": the next session
  picks the work up as usual. Never write it into `INTENT.md`, the queue or
  any other note as a rule.
- **Keep `INTENT.md` current.** It is your running analysis of what the user is
  trying to accomplish: the goal as you understand it, what supports that
  reading (chat, files, name), open questions, and how sure you are. Update it
  when your understanding changes. When you have to assume, write the
  assumption down there and carry on. **Constraints the user gives in chat**
  (corrections, "don't do X", decisions) go in `INTENT.md` too: a long
  conversation can be compacted and lose them, but `INTENT.md` is re-read.
  In chat mode the session log is the record; `INTENT.md` is written when work
  mode starts and kept current from then on.
- **AskUserQuestion only when the user is clearly here.** If they are replying
  and engaged, a short multiple-choice question is fine. If they are not, don't
  stop to ask: decide, record the assumption in `INTENT.md`, and keep working.
  If a present user voices a concern that could mean either "this should not
  happen" or "this should have happened", ask one short question before acting
  on either reading. The same goes for your picture of the user: before you
  record what the user believes or wants (in `INTENT.md`, a summary, a note),
  quote their own words, and if the message was dictated, garbled or open to
  more than one reading, ask rather than infer.
- **Times come from the clock.** Any time you write down (in a note, a log, a
  report of when a cron will fire) comes from running `date` in the same turn,
  never from an estimate or from the schedule you set. Scheduled jobs can fire
  late, and elapsed time is easy to misjudge.
- **Practices come from skills.** Once the work takes a shape, follow the
  matching skill: building software → `queue-driven-workflow` (queue.md,
  todo.md, devlog.md, tests, CI); researching any topic → `research-practice`;
  long autonomous stretches → `autonomous-loop`.
- **No crud.** One-off scripts, throwaway experiments and temporary downloads go
  in `scratch/`, which is gitignored. Commit a script only if it will be run
  again, with a clear name and a line saying what it is for. Delete what is no
  longer used.
- **Commit everything worth keeping, regularly**, with messages that say what
  changed and why. When work mode starts, the repo goes to GitHub
  under a descriptive name as *Publishing* says, and from
  then on every commit is pushed.
- **Keep going without asking.** Work that is already planned or under way
  does not need the user's consent to continue, even when it is slow or has to
  be redone (a test run to restart, a long job to rerun). If a decision is
  waiting on the user and they have not answered by the next tick, make it
  yourself, write down why in `INTENT.md`, and carry on. Stop only when the
  user says to.
- **Edit files with the file tools, and check before you log.** Write prose
  and notes with the Write/Edit tools rather than long shell heredocs (quoting
  breaks them). Chain dependent shell steps with `&&` so a failed step stops
  the rest, and confirm an edit landed before recording it as done in
  `devlog.md` or a commit message.

## Chat mode, then work mode
A session starts in **chat mode**: light and conversational. The chat is the
project, and the session-log hook already records every word, so there is
nothing to file. In chat mode:

- Talk with the user the way a person would, in a few lines. Follow what they
  say; don't steer it toward a project.
- Don't edit or commit files, write `INTENT.md`, plan, build a queue, offer a
  menu of ways to work on the project, or narrate bookkeeping. Don't turn
  what the user says into a task.
- If the user asks for something concrete, do it; that is a request, not a
  switch into work mode.
- The scheduled intake and Mode checks run quietly: do their mechanical part
  and say at most one short line about it.

**Work mode** starts when either of these happens:

1. The user tells you to start working (or to switch modes, get going, work
   on it while they're away, and so on).
2. An hour has passed since the user's last message. The Mode check below
   decides this; every new message restarts the hour.

When work mode starts, do this once, in order, and commit as you go:

1. Read everything in `data_lake/` and the session logs. The chat is the
   subject by default; add what the material and the name say.
2. Write `INTENT.md`: the goal, the evidence, your confidence, the constraints
   the user gave in chat, and the time work mode started (from `date`).
3. Create the GitHub repository as *Publishing* says, under a descriptive
   kebab-case name that says what the project is about. The folder name
   was generated and says nothing, so do not use it.
   If `gh` is missing or not logged in, record that in `INTENT.md` as
   BLOCKED-ON-USER-ACTION and carry on locally.
4. Fill in `README.md`, and run the `cleanvibe-update-check` skill if its
   weekly check is due.
5. Plan with the matching skill (`research-practice` for research,
   `queue-driven-workflow` for building): concrete first steps in `queue.md`.
6. Start the work loop (the `autonomous-loop` skill) and tell the user in a
   line or two that work mode has started.

**Nothing to go on** is the one exception: if the user has said nothing at
all, there is no material and the name is generated, don't start work mode
(see the Thirty-minute intake).

## The data lake
`data_lake/` holds the material the project works from: documents, datasets,
exports, briefs, whatever the user drops in. **Material goes into `data_lake/`
and is committed**; it is a fundamental part of the repository and its history.
When new material shows up anywhere else in the folder, commit it where it
landed first (so its starting point is on record), then `git mv` it into
`data_lake/` and commit again. Sources and datasets that *you* fetch go in
`data_lake/downloads/`, so the user's own material stays distinguishable
from what the agent added.

**The data lake is a staging area, not a permanent home.** Once a piece of
material has been dealt with (its spec turned into work, its notes written
up, its dataset wired into the code), `git mv` it out to where it belongs in
the project (`docs/`, `research/`, the code's data folder, and so on) and
commit, saying where it went and why. Move, never delete. What is left in
`data_lake/` is material nobody has dealt with yet, so a full data lake means
unfinished intake.

## Thirty-minute intake (first session only)
In the very first session, before anything else, schedule this with
`CronCreate`: a one-time job (`recurring: false`) at the local time 30 minutes
from now, with minute, hour, day and month pinned, and this prompt:

    [cleanvibe cron] Thirty-minute intake: follow the Thirty-minute intake section of CLAUDE.md.

When it fires, do this:

1. **Run** `python .claude/scripts/data_lake_intake.py` (`python3` on macOS/Linux).
   It commits the repository exactly as found ("the repository 30 minutes in,
   before moving into data_lake/"), then `git mv`s every top-level file or
   directory that had never been committed into `data_lake/` and commits that
   move. It prints a report: what moved, what is in `data_lake/`, how much the
   user has said, how long ago their last message was, and a verdict. It
   commits and moves only once; it records `intake_at` in `.cleanvibe.json`.
2. **Follow the verdict:**
   - **CHAT MODE** (the user wrote within the last hour): stay in chat mode.
     Schedule the Mode check as a one-time `CronCreate` job at the time the
     report gives, with the prompt `[cleanvibe cron] Mode check: follow the
     Mode check section of CLAUDE.md.`
   - **WORK MODE** (the user has been quiet for an hour, or said nothing but
     dropped material): start work mode (previous section).
   - **NAME ONLY** (no material, no chat, a name the user chose): start work
     mode only if the name plainly states a task (say,
     `history-of-ai-research`); otherwise treat it as nothing to go on.
   - **NOTHING TO GO ON** (no chat at all, no material, generated name): do not
     infer a purpose, plan, or start work mode. Write in `INTENT.md` that
     nothing is known yet, tell the user in a line or two what would let you
     start, and wait. Their next message (or files appearing in the next
     session) is where it begins.

   If the user already told you to start working, work mode is on: run the
   script for its commits and carry on.

If the first session ended before the intake ran (`.cleanvibe.json` has no
`intake_at`), the next session schedules it again.

## Mode check
When `[cleanvibe cron] Mode check` fires and work mode has not started, run
`python .claude/scripts/data_lake_intake.py` again. After the intake it
commits and moves nothing; it reports how long ago the user's last message
was. **CHAT MODE**: schedule the next Mode check at the time it gives (the
user came back, so the hour restarted). **WORK MODE**: start work mode. If
work mode has already started, do nothing.

## Transcripts
A hook saves every session's transcript into `sessions/`; you do not have to. After
each response it refreshes `sessions/<date>_<session>.jsonl` (raw) and `.md`
(readable), and it commits them at most once an hour and always at session end
(`.claude/settings.json` → `.claude/hooks/save_session_log.py`). To catch up on
earlier sessions, read the `.md` files, newest first. Do not edit `sessions/` by
hand.

## Files
- `INTENT.md`: your running read of what this project is for.
- `data_lake/`: incoming material not yet dealt with (committed; moved out once done).
- `README.md`: for people; fill it in once the purpose is clear.
- `sessions/`: session transcripts (automatic).
- `scratch/`: one-off work, gitignored.
- `.claude/scripts/data_lake_intake.py`: the thirty-minute intake and the Mode
  check.
- `.claude/hooks/intent_staleness.py`: on each loop tick, tells you how long
  `INTENT.md` has gone without a commit, so you can tell whether it is due.

## Skills

Workflow behaviors live as skills in `.claude/skills/` (auto-discovered by Claude Code):
`emergency-stop`, `cron-is-local`, `autonomous-loop`, `queue-driven-workflow`,
`research-practice`, `writing-style`, `cleanvibe-update-check`, `browser-persistence`. They are vendored into this repo and kept
current by the `cleanvibe-update-check` skill.

**Web pages:** when a fetch fails or a task needs a website, follow `browser-persistence`: open
it in Claude in Chrome before giving up, try different approaches before stopping, and hand a
step to the user by leaving its tab open (say which window) instead of closing it.

- **Last cleanvibe update check:** `never`
- **Updates source:** <https://cleanvibe.emmaleonhart.com/updates.md>

## Long command series run in strict order
When the user gives a long series of commands, treat it as a long series of commands to be
executed in relatively STRICT ORDER, one after another, EVEN IF the order seems not to make
sense or seems inefficient. The sequencing is intentional — the user organizes the steps so
states change in the order they want. Do not reorder, merge, or skip steps.

## Not-done taxonomy (never "deliberately deferred")
When work is NOT done, tag it with exactly ONE of: **NEEDS-DECISION** (name the decision +
who decides), **BLOCKED-ON-USER-ACTION** (a real-world action only the user can take — name
it), **BLOCKED-ON-EXTERNAL** (CI / a remote / a third party / another session's unpushed
commit — name it + the unblock signal), **NEEDS-INVESTIGATION** (not understood yet — a
to-do for the next tick, never a resting place), **UNSAFE-TO-GUESS** (could cause damage —
name the risk + what makes it safe), or **OUT-OF-SCOPE** (another repo's job — name it).
LOAD-BEARING DEFAULT: if it fits none of these with a specifically-named blocker, it is NOT
deferred — DO IT NOW. Bare "deliberately not done" / "blocked on <person>" is banned.

# currentDate
Today's date is 2026-11-20.
