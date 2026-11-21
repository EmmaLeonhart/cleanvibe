---
name: needs-user
description: Use when work cannot go on without the user doing something themselves (a login, a payment, a signature, a command only they can run, a risky or irreversible yes), and when planning a queue. Record it in the project's needs file (NEEDS-USER.md) with .claude/scripts/needs.py instead of asking in prose, sending an AskUserQuestion, or waiting.
---

# Needs the user: record it, don't ask and wait

A session that hits a step only the user can do used to write "waiting" and
stop. The question sat in a reply or a queue item they never read, and the
work behind it went nowhere. Emma (2026-11-20): cleanvibe "just asks and it
just waits", and "I oftentimes don't actually know what's waiting on me."
Instead, write one record per need into the project's needs file
(`NEEDS-USER.md` at the root, or the name in `.cleanvibe.json`'s
`needs_file`). A PC manager, or whatever looks after the user's projects,
reads every project's file and keeps pushing them until each item is done.

## First: is it really theirs?

- **A decision you can make, make it.** Decide, act, and write down the call
  and why. Facts you can look up, things they have already said, and choices
  between internals are never records.
- **A record is for:**
  - an **action** only they can take in the real world: log in somewhere, pay,
    sign, plug something in, run a command themselves, contact a person,
    approve something tied to their accounts;
  - a **decision** that is risky or irreversible, or that only they can know,
    or one they have kept for themselves. It must carry a default.

## Record them up front, when you plan

Don't wait until you reach the step: human work is front-loaded and
predicted in advance. When you write or refill `queue.md`, go through every
item, find each step only the user can do, and record all of them at once,
before you start. Put the record's `NE-<n>` in each queue item it holds up:
the collector ranks records by how many queue items each holds, so the one
that unblocks the most reaches them first.

## How to record it

```
python .claude/scripts/needs.py add --kind action --title "Renew the domain" \
  --do "Log in to the registrar and renew example.com for a year." \
  --blocks "The site going live." --where "any device with a browser"
```

- **title**: a few words, in their terms, not the project's internals.
- **do**: exactly what to do, in one or two sentences, with the command, URL
  or name they need. For a decision: the question and what happens by
  default. One decision per record.
- **blocks**: what is held up, so they can judge urgency.
- **where**: where they have to be (`at the PC`, `phone`, `any device with a
  browser`, `in person`, or a place). People have different contexts; a task
  that needs the desk has to say so early.
- Commit the needs file with the work.

## Then keep working

- **A record holds up only what depends on it.** Leave the blocked item in
  the queue with its `NE-<n>` and go on with everything else. A long queue is
  healthy; a blocker is not a reason to rush or to stop.
- **You write the dependencies, never the user.** Treat queue items as
  independent; where one truly can't start before another, add
  `needs: <start of that item>` to it yourself.
- **Leave the pushing to whatever collects the records.** Don't repeat the
  record in your own replies or status lines.
- **When it's done**, run `python .claude/scripts/needs.py set-status NE-3
  "done YYYY-MM-DD"` (date from the clock) and pick the blocked work back up.
  If they must not hear about it before a date, set `"hold until YYYY-MM-DD"`.
- **They are here and replying, and it is a yes on something risky?** Then
  one short question, a direct reply to their own message, is still fine.
