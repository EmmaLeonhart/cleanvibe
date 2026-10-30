---
name: browser-persistence
description: Use whenever a task touches a web page — a curl/API/script fetch that fails, a site that needs the browser, or any work with the Claude in Chrome tools (mcp__claude-in-chrome__*) — to keep going through ordinary friction instead of giving up, and to hand steps over without closing the tab.
---

# Browser persistence (Claude in Chrome)

Claude in Chrome exists for pages that were not built for agents: logins, lazy loading, odd widgets, sites that block scripts. It runs in the user's own logged-in Chrome. Friction on those pages is normal, not a reason to stop. In a cleanvibe project the user is often away, so "stop and ask" usually means the task sits for days. (Case study: sessions skipped sites unseen, quit on a first "Permission denied" that worked 45 minutes later, and left queue items waiting a week for downloads Chrome could have done. Every time the user pushed, the next try worked.)

This narrows Claude Code's general browser guidance ("stop and ask after 2-3 failing attempts"); it does not replace it.

- **Use the browser.** When curl, an API or a script fails on a page (403, empty body, JavaScript-only content, a login wall), open it in Chrome before reporting failure or waiting for the user. Don't wait for the user to download something you can fetch there.
- **"2-3 attempts" means 2-3 identical attempts.** Before stopping, try *different* approaches: wait and reload; take a screenshot to see what is really there; scroll; use find/click instead of reading page text; run JavaScript on the page; paste instead of drag; open it in a new tab. A first "Permission denied", timeout or blank page is retryable: try again before concluding anything about permissions.
- **Don't skip a site without trying it.** "It probably needs a sign-in" is not a result. Open it and see. The user is usually already logged in.
- **Read the whole page.** Scroll to the end (lazy-loaded lists keep growing) before saying what a page does or doesn't contain.
- **Hand over, don't close.** When a step is the user's (a CAPTCHA or bot check, a login, approving a download or purchase, a permission prompt, entering sensitive data), leave that tab open on exactly that step. Tell the user which tab and which window it is in (the Claude tab group may be in a separate window), then keep working on everything else.
- **Close only tabs that are truly finished.** If a tab might be needed again, by you or the user, leave it open.
- **Still never:** solve bot checks, buy things, create accounts, or enter card or ID data. Those are the user's steps.
- **When you do stop,** say what you tried (each different approach) and what exactly is blocking, and record it with a not-done tag naming the blocker.
