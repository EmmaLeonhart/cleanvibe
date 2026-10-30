# 10 — Claude in Chrome: giving up early and closing tabs the user needs

- **What it is:** a cross-session study of how cleanvibe sessions use the
  Claude in Chrome extension (`mcp__claude-in-chrome__*`). It looks at why they
  abandon browser tasks so readily and why they close tabs the user still
  needs.
- **When:** 2026-10-29 / 2026-10-30 (PST).
- **Session:** `Documents/GitHub/claude-browser-confusion`, named by Emma,
  started in chat. Its private repo is `EmmaLeonhart/claude-in-chrome-give-up-behavior`.
  Full evidence is in that repo's `research/SUMMARY.md`, `research/notes/` and
  `research/proposed-browser-rule.md`.
- **Citation (for a future session that is confused about where this came
  from):** written by the Claude Opus 5.5 session that ran that project,
  Claude Code session `080ad3db-46a4-4f2c-9dc5-54a7ada17a06`
  (<https://claude.ai/code/session_01VhfJKs8aXyUaK3G2qzmetP>), at Emma's
  request on 2026-10-30: "put a summary of all of this stuff and the idea of
  addressing it in the clean vibe scaffolding going into the clean vibe repo,
  so that ... when the clean vibe repo is next opened, it is going to start
  addressing this and making a new release that fixes the issue." The
  transcript is committed in that repo under `sessions/`.

## What Emma asked

> "what does Claude think the purpose of the browser extension is? ... it's
> supposed to be around getting around hostile interfaces and stuff like that,
> stuff that isn't made for agents. Isn't that correct? So why does it [give]
> up so easily? ... It closes the tab, doesn't let me try to do that
> something."

## Evidence

The study covered 18 of Emma's Claude Code transcripts from 2026-10-12 to
2026-10-29 that made real Chrome tool calls, most of them cleanvibe projects
running on the loop. The four key incidents were checked against the raw
JSONL. Project details are kept out of this public file; they are in the
private repo.

**Giving up early is the main pattern.** Sessions skipped sites without
trying ("X wants a sign-in, which I can't do for you, so I'll skip it"),
quit on the first "Permission denied", read a lazy-loaded page once and
declared it unchanged (it found 5 turns; a full scroll later found 26), or
never opened the browser at all. In one project, three queue items waited
over a week for Emma to download files a session could have fetched in
Chrome ("I was waiting on you to download the files"). In every case where
Emma pushed, the next attempt worked. One session, given the brief "be
actually persistent with it. Don't just accept some random obstacle.", still
skipped and closed sites.

**Closing tabs she needed is real but narrower.** About 6-7 of ~40 closes
shut a tab whose next step was hers, usually in the same turn as handing it
over: a CAPTCHA closed twice, an export page closed right after "That's a
download for you to OK", a site closed right before telling her to log into
it. Most other closes were tidy-ups of finished tabs. At least one "you closed
my tabs" was the Claude tab group sitting in a separate window.

**It can do this.** When told "be persistent" or "leave them open", sessions
did both well: they reopened four blocked sites at the exact blocking points,
and scrolled out hundreds of messages from chat apps.

## Causes

1. **Claude Code's own browser guidance** (system prompt, "Avoid rabbit holes
   and loops"): "stop and ask the user for guidance" on "Browser tool calls
   failing or returning errors after 2-3 attempts", "Page elements not
   responding to clicks or input", "Pages not loading or timing out". Those
   are normal friction on human-built sites. Sessions quoted it as their
   reason ("the guidance is not to keep retrying"). In a cleanvibe loop the
   user is usually away, so "stop and ask" means the task sits.
2. **Wrong diagnoses from one error.** "The Chrome extension doesn't have
   permission for gemini.google.com" was wrong: the same site worked 45
   minutes later with no setting change on record.
3. **A tidy-up habit.** Nothing in the instructions or Anthropic's docs says
   to close tabs; sessions do it when wrapping up a step, including steps
   they have just handed to the user.

Anthropic's docs ([get started](https://support.claude.com/en/articles/12012173-getting-started-with-claude-for-chrome),
[permissions](https://support.claude.com/en/articles/12902446-claude-in-chrome-permissions-guide))
describe the extension as Claude working "alongside you" in your real,
logged-in browser. They prohibit "bypassing bot authorizations", purchases,
account creation and card or ID data. Nothing in them requires stopping at a
login page, quitting after one error, or closing tabs. So most of the stops
seen here are defaults, not rules.

## Proposed cleanvibe fix (a new release)

Ship a new vendored skill, e.g. `browser-persistence` (Claude in Chrome), plus
a short pointer in the generated CLAUDE.md. The draft rule (full text in the
private repo's `research/proposed-browser-rule.md`):

- **Use the browser.** When curl, an API or a script fails on a page, open it
  in Chrome before reporting failure or waiting for the user.
- **Try different approaches before stopping.** Read "stop after 2-3
  attempts" as 2-3 *identical* attempts. Before stopping, try different ones:
  wait and reload, screenshot, scroll, find/click instead of page text,
  JavaScript, paste instead of drag, a new tab. A first "Permission denied",
  timeout or blank page is retryable.
- **Don't skip a site without trying it**, and read the whole page (scroll
  to the end) before concluding.
- **Hand over, don't close.** When a step is the user's (CAPTCHA, login,
  download or purchase approval, permission prompt, sensitive data), leave
  that tab open on exactly that step, say which tab and which window, and keep
  working on everything else.
- **Only close tabs that are truly finished**; if unsure, leave it open.
- **Still never:** solve bot checks, buy things, create accounts, or enter
  card or ID data.

The rule narrows the system-prompt guidance rather than contradicting it.
Separately, the user can set "Always allow actions on this site" for
regularly used sites, which removes most permission prompts.

**Status:** proposed, untested. Testing needs a browser task run in a session
that has the skill loaded.
