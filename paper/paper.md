# Delivering the cue: a hook that states a file's age makes an autonomous agent update its intent file

## Abstract

An earlier audit of Claude Code agents in the cleanvibe scaffold ("Forgotten
duties", clawRxiv post 2901) found that the agents kept duties whose
trigger arrives as a message and dropped duties whose trigger they must
notice in their own state. The clearest case was the project's intent
file: even with every loop prompt reminding the agent to update it, it went
5 to 6 hours stale while commits continued. That audit proposed delivering
the trigger itself. We test this with a hook that adds "INTENT.md last
changed H hours and N commits ago" to the agent's context at each turn of a
half-hourly loop, in six unattended sessions from written briefs, one of
them a concurrent control on the same brief and machine with the hook
removed. All sessions are public repositories with their transcripts
committed, and every number comes from git with a released script. Each
time the hook's line reached the agent with the file two or more hours
old, the next half hour brought an intent update (3 of 3); the control,
with no such line, went 3.5 hours and four work commits without one. The
hook cannot act inside a single long turn, which is where the remaining
stale stretches came from. The sample is small and we report it as a
pilot with its protocol and code, so the counts can be extended.

## 1. Background and question

Agents that work for hours without a person keep their working context in
files. cleanvibe (github.com/EmmaLeonhart/cleanvibe), an open-source
scaffold for Claude Code, gives each project an `INTENT.md` (the agent's
analysis of the goal, its evidence and confidence), a work queue, a log,
and a loop: a session-local cron that every half hour tells the agent to
commit, push and continue. The rule for `INTENT.md` is to update it when
the agent's understanding changes.

The earlier audit coded these duties across 17 sessions. Duties whose cue
arrives in context (a launch prompt naming a weekly check, a user stating
a constraint) held in 14 of 14 session-level cases; duties the agent must
notice for itself held in 20 of 35. For `INTENT.md` the scaffold had
already tried the obvious remedy, a periodic reminder: the loop prompt
said "re-read INTENT.md and update it if your understanding has changed"
at every tick. It moved updates from 4 of 143 ticks to 5 of 79, and the
file was still 5 to 6 hours stale in 3 of 7 sessions. The account offered
was the multiprocess framework of prospective memory (McDaniel and
Einstein, 2000): an intention whose cue is part of the current task is
retrieved spontaneously, while one whose cue is not depends on monitoring,
which fails under load. A reminder repeats the duty but still asks the
agent to notice that its understanding has changed.

**Question.** If the context states how stale the file is, does the agent
update it?

## 2. Method

**Three conditions.** (a) *No reminder*: the scaffold's rule in
`CLAUDE.md` only. (b) *Reminder without the age*: the earlier audit's
cleanvibe 2.0.3 sessions, whose loop prompt names the duty every tick. (c)
*The age*: cleanvibe 2.0.4, whose `intent_staleness.py` hook adds one
line, the hours and commits since `INTENT.md` last changed, whenever a
prompt reaches the agent (a loop tick or a message). The rule's wording is
the same in all three.

**Sessions.** Six projects created with `cleanvibe new`, each with a
written brief and no chat: notes to a static site; a SQL database; a
Scheme in five stages; git in five stages, checked against real git; and a
chess engine improved over self-play rounds of 200-game matches, run twice
on the same machine and brief, once with the hook (condition c) and once,
started 2.5 hours later, with only the hook removed (condition a). The
long briefs were chosen so that work would continue for hours. Every
session's repository is public with its transcripts committed under
`sessions/`. All counts are as of a fixed cutoff; the chess control had
then worked 4 hours 40 minutes.

**Measures**, computed by `paper/scripts/staleness.py` (in the cleanvibe
repository, standard library only) from git and the committed transcripts.
A *work commit* changes any file outside `sessions/` (the transcript hook's
own commits are excluded). The *gap* is the time from an `INTENT.md` change
to a later work commit that did not change it. A *stale cue* is a hook line
reporting two or more hours with a work commit within 30 minutes either
side; it is *followed* if `INTENT.md` is committed within the next 30
minutes. No model judges another model's behaviour.

## 3. Results

| Repository | Condition | Work span | Commits | Longest gap | Stale cues | Followed |
|---|---|---|---|---|---|---|
| markdown-notes-static-site | age | 37 min | 23 | 0.5 h | 0 | — |
| pure-python-sql-database | age | 44 min | 26 | 0.7 h | 0 | — |
| r7rs-scheme-in-python | age | 4 h 35 min | 57 | 2.3 h | 1 | 1 |
| pure-python-git | age | 10 h 10 min | 33 | 3.4 h | 2 | 2 |
| pure-python-chess-engine-selfplay | age | 6 h 5 min | 38 | 1.5 h | 0 | — |
| python-chess-engine-selfplay-elo | none (control) | 4 h 40 min | 25 | 3.5 h, open | — | — |

**When the age arrived, the file was updated.** Three times the hook told
an agent, mid-work, that its intent file was two or more hours old; each
time `INTENT.md` was committed within the half hour (3 of 3). In the Scheme
session the line read "2.1 hours and 12 commits ago", and the next commit
(`029c05f` in r7rs-scheme-in-python) replaced a sentence that had become
false (the R7RS report, described as absent, had just been downloaded) and
added a progress line. The updates carried content, not a refreshed date.

**Without it, the file was not.** The control, on the same brief, machine
and scaffold, received no such line. At the cutoff its intent file had
gone 3.5 hours and four work commits without a change, and the gap was
still open. Its treated twin's longest gap was 1.5 hours; that session
updated the file about hourly, each time because a fact had changed (the
expected match length after the first match; the machine being shared).

**Where the hook cannot reach.** The remaining long gaps with the hook
(2.3 and 3.4 hours) both fell inside single long turns: the hook runs when
a prompt arrives, and a turn in which the agent keeps building receives
none. The git session's 3.4 hours ended when the next tick delivered "3.0
hours and 7 commits ago", and the file was updated. A cue delivered only
at turn boundaries bounds staleness by turn length, not by the clock.

**Compared with a reminder.** Under the reminder without the age
(condition b), the file went 5 to 6 hours stale in 3 of 7 sessions. With
the age, no gap ran on past the next cue.

## 4. Discussion

The duty's wording did not change between conditions; only what the
context said about the file did. A reminder repeats the instruction and
leaves the agent to judge whether it applies now; the age states that it
does. This matches the multiprocess account: the stale file is turned from
something to be noticed into a cue that is part of the current input.
Long-context work points the same way: recall drops when nothing in the
current text matches the stored instruction (Modarressi et al., 2025).

For scaffold builders the rule is to deliver the trigger condition as a
fact rather than restate the duty. It is cheap (one line per prompt), and
at idle ticks agents ignored it correctly: after the short briefs were
done the reported age kept growing and no session invented an update. It
generalizes to other duties that lapsed in the earlier audit, such as the
README ("last changed 9 commits ago") or an empty queue. Its limit is
the turn: a cue that arrives only between turns cannot interrupt a long
one, so a scaffold that wants a bound in hours needs the agent to end
turns, or a cue inside tool results.

One observation, too small to count as a finding: the briefs also asked
for a public repository, against the private default stated in each
project's `CLAUDE.md`. Two agents that met that instruction only in the
brief file created private repositories; one that also had it in its
launch prompt created a public one.

## 5. Limitations

This is a pilot: six sessions, one control, three stale cues, one agent
model, and one author who built the scaffold. The reminder condition comes
from the earlier audit's sessions, which were the author's own projects
rather than written briefs, so only the chess pair compares the hook with
no cue on identical work. The first four sessions ran inside the
cleanvibe repository, so Claude Code also loaded cleanvibe's own
development rules from the parent folder; the chess pair ran outside it.
The treated chess session stopped working after 6 hours when a match was
ended for low memory and it waited for the user; its counts cover the work
before that. Everything can be rechecked from the public repositories with
the released script and extended with the protocol in the accompanying
skill.

## References

- Leonhart, E. Forgotten duties: auditing how coding agents maintain their
  own context in a queue-driven autonomous loop. clawRxiv, post 2901.
- McDaniel, M. A., and Einstein, G. O. (2000). Strategic and automatic
  processes in prospective memory retrieval: a multiprocess framework.
  Applied Cognitive Psychology 14(7), S127–S144.
- Modarressi, A., Deilamsalehy, H., Dernoncourt, F., Bui, T., Rossi, R. A.,
  Yoon, S., and Schütze, H. (2025). NoLiMa: Long-context evaluation beyond
  literal matching. arXiv:2502.05167.
