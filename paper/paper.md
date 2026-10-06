# Cues that arrive and cues that must be noticed: how coding agents keep their own context files in an autonomous loop

## Abstract

Agents that work for hours without a person keep their context in files: a
statement of intent, a work queue, a log. We study how Claude Code agents
keep those files in cleanvibe, an open-source scaffold that starts
git-tracked projects with a half-hourly autonomous loop, across three
rounds of sessions and two rounds of fixes. Duties whose trigger arrives as
a message (a launch prompt, a user's remark) held: a weekly update check
went from 0 of 9 sessions to 6 of 6 once the launch prompt named it, and
constraints stated in chat were recorded in 8 of 8. Duties whose trigger
the agent must notice in its own state did not: the intent file went 3 to
6 hours stale while commits continued, and naming it in every loop prompt
moved it from 4 of 143 ticks to 5 of 79. We read this through the
multiprocess account of human prospective memory and predicted that
delivering the staleness itself ("INTENT.md last changed H hours and N
commits ago") would make updates follow. In five sessions run to test this, in public repositories with every
transcript committed, the longest stretch of committed work without an
intent update fell from 5 to 6 hours (3 of 7 round 2 sessions) to 0.5 to
2.4 hours, and both ticks that found the file over two hours stale during
work were followed by an update. We give the audit script and the protocol
so the count can grow.

## 1. Problem

A long autonomous session stays on course only if its working files stay
true. cleanvibe (github.com/EmmaLeonhart/cleanvibe) gives every project an
`INTENT.md` (the agent's analysis of the goal, its evidence and its
confidence), a `queue.md` of concrete next steps, a `devlog.md` where
finished work is recorded, and a loop: one session-local cron that every
half hour tells the agent to commit, push and keep working the queue. The
rules for keeping these files are written in the project's `CLAUDE.md` and
in skills the agent loads. They stay in context the whole session. The
question is which of them the agent actually follows when no one is
watching, and what changes that.

## 2. Method

Each cleanvibe session's transcript is committed to its repository
(`sessions/*.jsonl`) by a hook, with the project's git history alongside.
From these we count, per loop tick, which files the agent read and changed,
and per session, whether each standing duty held. Rounds 1 and 2 (published
as case studies 06 and 07 in the cleanvibe repository) coded 20 workflow
rules per session, once by the analysing agent and once blind by a fresh
agent that saw only the transcripts (Cohen's kappa 0.69). For round 3 the
measure is mechanical: `paper/scripts/staleness.py` reads a project's git
log and transcripts and reports, for each time the staleness hook fired,
how stale the intent file was, whether work was being committed around
that tick, and whether the intent file was committed within the next 30
minutes. Commits made by the transcript hook itself, which touch only
`sessions/`, are not counted as work.

## 3. Results

**Round 1** (four sessions, cleanvibe 2.0.2). Rules tied to a clear event
held everywhere: the one-time intake at 30 minutes, following its verdict,
commit cadence, staying inside the project. The standing duties did not. No
session ran the weekly update check. The intent file went 3 to 5.5 hours
stale while commits kept landing, and 0 of 22 loop ticks read it; the ticks
did what the tick prompt named and nothing else.

**Fixes (2.0.3).** The tick prompt named the duties (refresh INTENT.md and
the README, refill an empty queue, read the clock); the launch prompt named
the update check; constraints the user states in chat go into INTENT.md.

**Round 2** (eight sessions on 2.0.3, two on 2.0.2 the same week as a
control).

| Duty | Trigger | Before | After |
|---|---|---|---|
| Weekly update check | arrives (launch prompt) | 0 of 9 sessions | 6 of 6 first sessions |
| Record constraints from chat | arrives (user message) | — | 8 of 8 sessions |
| Cron prompts shown in the log | arrives (cron fire) | none | every fire |
| Refresh INTENT.md | must be noticed | 4 of 143 ticks | 5 of 79 ticks; 5–6 h stale in 3 sessions |
| Prose through the file tools | must be noticed | — | 2 of 8 sessions |
| Check an edit before logging it | must be noticed | — | 4 of 8 sessions |

The control sessions did not run the update check, which rules out a change
in the agent model that week. Empty queues were not refilled (0 of 55
ticks), but every idle tick gave a reason, most often that the remaining
ideas went beyond what the user had asked for; we do not count that as a
lapse.

**The pattern.** Every duty was stated explicitly and stayed in context.
What separated those that held is where the event that makes the duty due
comes from: a message entering the context (a prompt, a user's remark, a
cron firing), or a change the agent would have to detect in its own state
(its understanding has moved on, it is about to write prose with a shell
command). Naming the intent file in every tick prompt made the instruction
arrive, but not the cue: "update it if your understanding has changed"
still asks the agent to notice the change.

**Round 3** (cleanvibe 2.0.4). The fix that follows is to deliver the
staleness. A hook adds "INTENT.md last changed H hours and N commits ago"
to the agent's context at every loop tick. We predicted that in ticks where
the file is over two hours stale while work continues, most would update
it. Practice sessions were started from written briefs with no chat, each
in a public repository:

| Session (repository) | Brief | Commits | Longest gap while working | Stale firings, active work | Followed by an update |
|---|---|---|---|---|---|
| markdown-notes-static-site | notes to a static site | 23 | 0.5 h | 0 | — |
| pure-python-sql-database | SQL database with B-tree storage | 26 | 0.7 h | 0 | — |
| r7rs-scheme-in-python | Scheme in five stages | 49 | 2.3 h | 1 | 1 |
| pure-python-git | git in five stages | 24 | 2.4 h | 1 | 1 |
| pure-python-chess-engine-selfplay | chess engine, self-play rounds (running) | 22 | 1.0 h | 0 | — |

Both firings with the file over two hours stale during active work were
followed by an update within the half hour (2 of 2). In the Scheme session
the next commit (`029c05f` in github.com/EmmaLeonhart/r7rs-scheme-in-python)
replaced a sentence that had become false and added a progress line. The
stronger result is the gap itself: across five round 3 sessions the
longest stretch of committed work without an intent update was 0.5 to 2.4
hours, against 5 to 6 hours in 3 of 7 round 2 sessions. The hook states
the file's age on every tick, not only past two hours, and the chess
session, whose matches run for hours, updated the file about hourly when
a fact changed (the expected match length, the machine being shared).

The same sessions gave an unplanned test of the cue account. Each brief, a
file in `data_lake/`, said to create the GitHub repository public; the
project's `CLAUDE.md`, loaded in context, says private. Both sessions that
reached that step after the brief carried the instruction created it
private. An instruction in a file the agent has to go and read lost to one
already in context.

## 4. Discussion

The split matches the multiprocess framework of prospective memory
(McDaniel and Einstein, 2000): an intention whose cue is part of the
current task is retrieved spontaneously, while one whose cue is not needs
monitoring, which fails under load. A launch prompt is the first kind of
cue; a file quietly going stale is the second. Work on long-context recall
points the same way: recall drops when nothing in the current text matches
the stored instruction (Modarressi et al., 2025). The practical rule for
people building agent scaffolds is to deliver the trigger condition, not to
restate the duty more forcefully.

Round 3 also showed two limits of measuring by ticks. First, the loop only
fires between turns: the Scheme session's first hour of building was a
single turn, so no tick, and no staleness line, fell inside it. Second,
short briefs never produce the case the prediction is about. A test of the
prediction needs sessions that commit for hours.

## 5. Limitations

One author, who built the scaffold and is its only user; one agent model;
rounds 1 and 2 have 4 and 10 sessions. The cue distinction was drawn after
round 2, so round 3 is its first prospective test, with five sessions and
two qualifying ticks. Round 3 sessions ran from written briefs while round
2 were the author's own projects, which may account for part of the
difference. The first four round 3 sessions ran inside the cleanvibe
repository, so Claude Code also loaded cleanvibe's own development rules
from the parent folder; the fifth ran outside it. Rounds 1 and 2 are personal sessions; their
transcripts are not released, and the counts above come from the case
studies published in the cleanvibe repository. Round 3's transcripts are
public in full. No session reached context compaction, so the risk the
literature stresses most is untested.

## References

- McDaniel, M. A., and Einstein, G. O. (2000). Strategic and automatic
  processes in prospective memory retrieval: a multiprocess framework.
  Applied Cognitive Psychology 14(7), S127–S144.
- Modarressi, A., Deilamsalehy, H., Dernoncourt, F., Bui, T., Rossi, R. A.,
  Yoon, S., and Schütze, H. (2025). NoLiMa: Long-context evaluation beyond
  literal matching. arXiv:2502.05167.
