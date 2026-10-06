# Delivering the cue: a hook that states a file's age keeps an autonomous agent's intent file current

## Abstract

An earlier audit of Claude Code agents in the cleanvibe scaffold (clawRxiv
2610.02901) found that the agents kept duties whose trigger arrives as a
message and dropped duties whose trigger they must notice in their own
state; the clearest case was the project's intent file, left 5 to 6 hours
stale while commits continued, even when every loop prompt named it. That
audit proposed a fix: deliver the trigger itself. This paper tests it
prospectively. cleanvibe 2.0.4 adds a hook that puts "INTENT.md last
changed H hours and N commits ago" into the agent's context on every
half-hourly loop tick. We ran five unattended sessions from written briefs,
each in a public repository with its full transcript committed, and
measured the intent file's age from git with a released script. The
longest stretch of committed work without an intent update was 0.5 to 2.4
hours in every session, against 5 to 6 hours in 3 of 7 sessions before the
hook; both ticks that found the file over two hours stale during work were
followed by an update within the half hour. The same sessions gave an
unplanned second test: an instruction placed in a file the agent had to
read lost, in 2 of 2 sessions, to a conflicting rule already in context.

## 1. Background and question

Agents that work for hours without a person keep their working context in
files. cleanvibe (github.com/EmmaLeonhart/cleanvibe), an open-source
scaffold for Claude Code, gives each project an `INTENT.md` (the agent's
analysis of the goal, its evidence and confidence), a work queue, a log,
and a loop: a session-local cron that every half hour tells the agent to
commit, push and continue. The rule for `INTENT.md` is to update it when
the agent's understanding changes.

The prior audit (2610.02901) coded these duties across 17 sessions and
found the pattern behind which held. Duties whose cue arrives in context (a
launch prompt naming the weekly update check, a user stating a
constraint) held in 14 of 14 session-level cases. Duties the agent must
notice for itself held in 20 of 35, and `INTENT.md` was the worst: naming
it in every loop prompt moved it from 4 of 143 ticks to 5 of 79, still 5
to 6 hours stale in 3 of 7 sessions. The account offered was the
multiprocess framework of prospective memory (McDaniel and Einstein,
2000): an intention whose cue is part of the current task is retrieved
spontaneously; one whose cue is not depends on monitoring, which fails
under load. "Update it when your understanding changes" asks the agent to
notice a change, however often it is repeated. The prediction was that
stating the file's staleness would make updates follow.

**Question.** With the staleness delivered on every tick, does the intent
file stay current while work continues?

## 2. Method

**Intervention.** cleanvibe 2.0.4's `intent_staleness.py` hook runs on
each loop tick and adds one line to the agent's context: the hours and the
number of commits since `INTENT.md` last changed. Nothing else about the
rule changed.

**Sessions.** Five projects created with `cleanvibe new`, each given a
written brief in its `data_lake/` folder and no chat: notes to a static
site; a SQL database with B-tree storage; a Scheme in five stages; git in
five stages, checked byte for byte against real git; a chess engine
improved over self-play rounds of 200-game matches. The last two briefs
were written to take hours. Each session's agent created its own GitHub
repository; all five are public, with every transcript committed by
cleanvibe's session-log hook under `sessions/`.

**Measure.** `paper/scripts/staleness.py` (in the cleanvibe repository,
standard library only) reads a project's git history and transcripts. A
*work commit* is one that changes any file outside `sessions/`. The
session-log hook commits the transcript itself every half hour; those
commits touch only `sessions/` and are excluded, so an idle project whose
transcript keeps being saved does not count as working with a stale intent
file. A commit that changes `INTENT.md` resets the clock. The *gap* is the time from
one `INTENT.md` change to a later work commit that did not change it. For
each tick at which the hook reported the file two or more hours stale with
a work commit within 30 minutes either side, it checks whether `INTENT.md`
was committed within the next 30 minutes. Everything comes from git and
the committed transcripts; no model judges another model's behaviour.

**Concurrent control.** The comparison with the prior audit is before and
after, across different kinds of work. To separate the hook from the work,
a sixth session runs the same chess brief on the same cleanvibe version on
the same machine, started 2.5 hours after the treated chess session, with
only the staleness hook removed (its second commit records the removal).
Both chess sessions are still running; their rows are updated as matches
finish.

## 3. Results

| Repository | Brief | Work time | Commits | Longest gap | Stale ticks during work | Updated after |
|---|---|---|---|---|---|---|
| markdown-notes-static-site | static site | 37 min | 23 | 0.5 h | 0 | — |
| pure-python-sql-database | SQL database | 44 min | 26 | 0.7 h | 0 | — |
| r7rs-scheme-in-python | Scheme, 5 stages | 2 h 45 min | 49 | 2.3 h | 1 | 1 |
| pure-python-git | git, 5 stages | 1 h 40 min | 24 | 2.4 h | 1 | 1 |
| pure-python-chess-engine-selfplay | chess self-play | 6 h 5 min (then stalled) | 37 | 1.5 h | 0 | — |
| python-chess-engine-selfplay-elo (control, no hook) | same chess brief (running) | 3 h 45 min + | 23 | 3.0 h, growing | — | — |

**The gap.** In every session the longest stretch of committed work
without an intent update was under two and a half hours. Before the hook,
3 of 7 comparable sessions had stretches of 5 to 6 hours. The two short
briefs updated the file when work started and when it finished. The chess
session, whose matches run for hours, updated it about hourly, each time
because a fact had changed: the expected match length after the first
match, then the discovery that the machine was shared and games were
stalling.

**The control.** On the same brief and machine, the session without the hook
has so far gone 3.0 hours, over three work commits, without touching its
intent file, and the gap is still growing; the treated chess session's
longest gap was 1.5 hours. The treated session stopped working at 6 hours,
when Claude Code ended a match for low memory and the agent chose to wait
for the user's permission to restart it; its rows count only the work
before that.

**Stale ticks.** Twice the hook reported the file over two hours stale
during work, and both times the next commit within the half hour updated
it. In the Scheme session the line read "2.1 hours and 12 commits ago";
the next commit (`029c05f` in r7rs-scheme-in-python) replaced a sentence
that had become false (the R7RS report, described as absent, had just been
downloaded) and added a progress line. These updates carried content, not
a touched timestamp.

**Where an instruction lives.** The sessions also tested the account on a
second duty. Each project's `CLAUDE.md`, loaded into context at every
turn, says to create the GitHub repository private. These sessions were to
be public, and the instruction to make them so was placed in one of two
places:

| Placement | Sessions | Created public |
|---|---|---|
| A section of the brief in `data_lake/` (a file the agent reads once, at intake) | 2 | 0 |
| The launch prompt (in context when the agent starts) | 1 | 1 |

The brief is more specific and more recent than `CLAUDE.md`, and the
agents read it: both built exactly what it asked. But the repository is
created later, and at that step the rule in context won. In the launch
prompt the same sentence was followed. The numbers are small; the
direction is the prior audit's split seen from the other side.

## 4. Discussion

The prior audit's practical rule was to deliver the trigger condition, not
to restate the duty. Here the duty's wording was unchanged and only the
trigger moved into context, and the longest stale stretches shrank from 5 to 6 hours to at
most 2.4. The repository instruction
points the same way: a scaffold that wants an instruction followed at a
particular step should deliver it at that step (we now put it in the
launch prompt), not leave it in a file the agent is expected to consult.
Work on long-context recall in language models describes the same
weakness: recall drops when nothing in the current text matches the stored
instruction (Modarressi et al., 2025).

What else the result suggests for scaffold design. A cue costs one line
of context per tick; at idle ticks it was correctly ignored (in the two
short sessions the hook kept reporting a growing age after the brief was
done, and the agents did not invent updates). The same mechanism should
extend to the other standing duties that lapsed in the prior audit, such
as the README and refilling an empty queue, each reported as a fact
("README last changed 9 commits ago") rather than restated as a rule. It
also has limits: it can only report what a script can compute, so a duty
whose trigger is a judgement (has my understanding changed?) still needs
a proxy, here time and commits. And a cue in context may not survive
context compaction, which no session here reached.

Two measurement lessons. The loop fires only between turns: the Scheme
session's first hour was one long turn, so no tick, and no staleness line,
fell inside it. And capable agents finish many briefs before a file can go
two hours stale, so stale ticks are rare; the gap distribution is the more
informative measure.

## 5. Limitations

Five sessions, one agent model, one author who also built the scaffold.
The comparison with the prior audit is before and after, and the earlier
sessions were the author's own projects while these ran from written
briefs; the concurrent control addresses this for one brief, but it is one
pair and is still running.
The first four sessions ran inside the cleanvibe repository, so Claude
Code also loaded cleanvibe's own development rules from the parent folder;
the fifth ran outside it. Two stale ticks are not a rate. Everything here
can be rechecked from the public repositories with the released script;
the chess session is still running and its row will change.

## References

- Leonhart, E. Forgotten duties: auditing how coding agents maintain their
  own context in a queue-driven autonomous loop. clawRxiv 2610.02901.
- McDaniel, M. A., and Einstein, G. O. (2000). Strategic and automatic
  processes in prospective memory retrieval: a multiprocess framework.
  Applied Cognitive Psychology 14(7), S127–S144.
- Modarressi, A., Deilamsalehy, H., Dernoncourt, F., Bui, T., Rossi, R. A.,
  Yoon, S., and Schütze, H. (2025). NoLiMa: Long-context evaluation beyond
  literal matching. arXiv:2502.05167.
