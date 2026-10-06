# 09 — A five-stage Scheme brief on 2.0.4: the first round 3 case

- **What it is:** the third round 3 practice session, given a staged brief
  so that the work would run long enough for INTENT.md to go over two hours
  stale while commits continued (case study 08 had no such ticks).
- **When:** 2026-10-05 22:15 PDT to 2026-10-06 01:32 PDT (05:15 to 08:32
  UTC, 10-06).
- **Session:** `tests/scratch/silver-jolly-tulip`, auto-named; brief in
  `data_lake/brief.md`: an R7RS-small Scheme in pure Python in five stages
  (interpreter, call/cc and macros, libraries, bytecode VM, conformance
  suite). Launched with the first-session prompt; nobody chatted to it.

## What it did

| | |
|---|---|
| Intake | on time (05:45 UTC), WORK MODE |
| INTENT.md at work start | yes, from the brief |
| Private repo | `r7rs-scheme-in-python` |
| Stages 1-3 | done by 06:40 UTC |
| Stage 4 (bytecode VM) | done 08:00 UTC; nine benchmarks, VM 1.86x faster overall, both engines agree |
| Stage 5 (conformance) | done 08:30 UTC; 1273 tests pass on both engines, 14 expected failures (complex numbers, optional in R7RS); the suite found six real bugs |
| Unit tests | 151 per engine |
| Commits | 34 |
| INTENT.md changes | 05:45 (start), 08:00 (hook), 08:30 and 08:30 (completion, timestamp fix), 08:31 (CI blocked) |
| CI | green on eight jobs at 08:16 UTC, then every job refused by GitHub billing; the agent recorded it as blocked with the unblock signal and checked locally instead |

## Analysis

- **The first round 3 case went the way the paper predicts.** At 08:00 UTC
  the hook line read "INTENT.md last changed 2.1 hours and 12 commits ago".
  The next commit (`029c05f`) updated INTENT.md with substance: it replaced
  a sentence that had become false (the R7RS report was no longer absent;
  it had just been fetched into `data_lake/downloads/`) and added a
  progress line. One case is not a rate, but it is the first time the
  stale-INTENT path has been exercised at all.
- **A long turn produces no ticks.** From the intake (05:45) to 06:47 UTC
  the whole build was one turn. Neither the Stop hook (the committed
  transcript stayed at 05:15) nor the half-hour loop cron (CronCreate jobs
  fire only when the session is idle) ran during it. Round 3 measures
  ticks, so an agent that works without stopping gives it nothing to count
  however stale INTENT.md gets.
- **The session died at about 06:48 UTC** and was resumed at 07:10 with
  `open_project` (the resume prompt). Emma's scheduled job relaunched its
  own sessions at 06:49:57 and this one was not among them; the likely
  cause is that the restart closed it. The resumed session caught up
  from its log and git alone, restarted its loop cron, and ended its turn,
  and from then on work came in ticks. That interruption is what turned the
  build into countable ticks.
- **Blocked CI handled by the not-done taxonomy.** When GitHub refused every
  job for billing, the agent did not retry or work around it: it named the
  blocker, the unblock signal (the next push shows jobs starting), and what
  it verified locally (both engines on Python 3.13 and 3.11, 3.9 syntax).
- **Finished, then the same end as 08:** an empty queue, and INTENT.md says
  complex numbers and further VM speed work are the user's call.

## What it changes

- Round 3 has one case: hook fired at over two hours stale, INTENT.md
  updated with real content. More are needed for a rate.
- The measurement unit needs care: ticks only exist between turns, so a
  session's tick count depends on how often it ends a turn, not only on
  how long it works. Count INTENT.md staleness against commits as well as
  ticks.
- Practice sessions don't survive the scheduled relaunch; they have to be
  resumed by hand (or added to that job).
- GitHub Actions is refused for billing on Emma's account (08:16 UTC
  onward); it affects every repo's CI, not just this one.
