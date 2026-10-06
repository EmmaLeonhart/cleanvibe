"""INTENT.md staleness in a cleanvibe project, from its git history and transcripts.

Usage: python staleness.py PROJECT_DIR [PROJECT_DIR ...]

For each project prints one JSON line:
- commits: commits in the history;
- stale_commits: work commits (touching anything outside sessions/) that
  did not touch INTENT.md, made while INTENT.md
  had last changed more than 2 hours earlier;
- max_stale_h: the longest gap (hours) between INTENT.md changes while
  commits continued;
- hook_firings: distinct staleness lines the intent_staleness hook put in
  the agent's context (from the committed sessions/*.jsonl);
- stale_firings: those reporting 2 hours or more, with work committed since
  INTENT.md last changed (an idle project's INTENT.md is not out of date);
- stale_firings_updated: stale firings followed by an INTENT.md commit
  within 30 minutes (before the next half-hourly tick);
- active_stale_firings(_updated): the same, counting only firings with a
  work commit within 30 minutes either side (the agent was working, not idle).

Stdlib only. Reads git and sessions/; writes nothing.
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

HOOK = re.compile(r"last changed ([\d.]+) hours and (\d+) commits ago")
STAMP = re.compile(r'"timestamp":"([^"]+)"')
STALE_H = 2.0
WINDOW_S = 30 * 60


def commits(repo):
    out = subprocess.run(
        ["git", "-C", repo, "log", "--reverse", "--format=@%H %at", "--name-only"],
        capture_output=True, text=True, check=True).stdout
    rows, cur = [], None
    for line in out.splitlines():
        if line.startswith("@"):
            sha, ts = line[1:].split()
            cur = {"sha": sha, "t": int(ts), "intent": False, "work": False}
            rows.append(cur)
        elif line.strip() and cur:
            name = line.strip()
            cur["intent"] |= name == "INTENT.md"
            # The session-log hook's own commits touch only sessions/; they are not work.
            cur["work"] |= not name.startswith("sessions/")
    return rows


def firings(repo):
    seen, out = set(), []
    for path in sorted(glob.glob(os.path.join(repo, "sessions", "*.jsonl"))):
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                m = HOOK.search(line)
                s = STAMP.search(line)
                if not (m and s):
                    continue
                key = (os.path.basename(path), m.group(1), m.group(2))
                if key in seen:  # the same reminder is recorded more than once
                    continue
                seen.add(key)
                t = dt.datetime.fromisoformat(s.group(1).replace("Z", "+00:00")).timestamp()
                out.append({"t": t, "hours": float(m.group(1)), "commits": int(m.group(2))})
    return out


def audit(repo):
    cs = commits(repo)
    last_intent, stale, max_gap = None, 0, 0.0
    for c in cs:
        if c["intent"]:
            if last_intent is not None:
                max_gap = max(max_gap, (c["t"] - last_intent) / 3600)
            last_intent = c["t"]
        elif c["work"] and last_intent is not None and (c["t"] - last_intent) / 3600 > STALE_H:
            stale += 1
            max_gap = max(max_gap, (c["t"] - last_intent) / 3600)
    fs = firings(repo)
    intent_times = [c["t"] for c in cs if c["intent"]]

    def worked_since_intent(t):
        last = max((x for x in intent_times if x <= t), default=None)
        return last is not None and any(c["work"] and last < c["t"] <= t for c in cs)

    stale_fs = [f for f in fs if f["hours"] >= STALE_H and worked_since_intent(f["t"])]
    def updated(f):
        return any(f["t"] <= t <= f["t"] + WINDOW_S for t in intent_times)

    active = [f for f in stale_fs
              if any(c["work"] and abs(c["t"] - f["t"]) <= WINDOW_S for c in cs)]
    return {
        "project": os.path.basename(os.path.abspath(repo)),
        "commits": len(cs),
        "stale_commits": stale,
        "max_stale_h": round(max_gap, 2),
        "hook_firings": len(fs),
        "stale_firings": len(stale_fs),
        "stale_firings_updated": sum(map(updated, stale_fs)),
        "active_stale_firings": len(active),
        "active_stale_firings_updated": sum(map(updated, active)),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for repo in sys.argv[1:]:
        print(json.dumps(audit(repo)))
