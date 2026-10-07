"""Experiment 3b: replay the declined 20:48 tick in an INTERACTIVE session.

    python paper/experiment/interactive.py --trials 5 --out paper/experiment/interactive_results.jsonl

Headless replays (`claude -p`, fork.py) updated INTENT.md almost every time,
while the live interactive session declined eight ticks running. This arm
removes one difference: each trial resumes the same transcript at the same
tick in a real interactive Claude Code console (a new window, as cleanvibe
launches sessions), with the tick prompt the live session received. The trial
waits until the session has worked on the prompt and gone idle for a minute,
reads INTENT.md, then closes the session and its window. Windows only.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import fork  # noqa: E402
from cleanvibe.launch import clean_env  # noqa: E402
from cleanvibe.trust import mark_trusted  # noqa: E402
from run import TICK_FULL  # noqa: E402

SESSIONS = Path(os.path.expanduser("~")) / ".claude" / "sessions"
NEW_CONSOLE, NEW_GROUP = 0x00000010, 0x00000200


def session_record(dest: Path, since: float):
    for f in glob.glob(str(SESSIONS / "*.json")):
        try:
            r = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if Path(r.get("cwd", "")).resolve() == dest.resolve() and r.get("startedAt", 0) / 1000 >= since - 5:
            return r
    return None


def stop(pid: int):
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    f"$p = Get-CimInstance Win32_Process -Filter 'ProcessId={pid}'; "
                    f"if ($p) {{ $par = $p.ParentProcessId; Stop-Process -Id {pid} -Force; "
                    f"$q = Get-CimInstance Win32_Process -Filter \"ProcessId=$par\"; "
                    f"if ($q.Name -eq 'cmd.exe') {{ Stop-Process -Id $par -Force }} }}"],
                   capture_output=True, text=True)


def run_trial(root: Path, n: int, timeout: int) -> dict:
    dest = root / f"i{n:03d}-reminder"
    fork.build(dest, keep_hook=False)
    mark_trusted(dest)
    before = fork.intent_at_commit()
    t0 = time.time()
    subprocess.Popen(["cmd", "/k", "claude", TICK_FULL, "--resume", fork.SESSION,
                      "--fork-session"], cwd=str(dest), env=clean_env(),
                     creationflags=NEW_CONSOLE | NEW_GROUP)
    rec, was_busy, idle_since, outcome = None, False, None, "timeout"
    while time.time() - t0 < timeout:
        time.sleep(10)
        rec = session_record(dest, t0) or rec
        if not rec:
            continue
        cur = session_record(dest, t0) or rec
        if cur.get("status") == "busy":
            was_busy, idle_since = True, None
        elif was_busy:
            idle_since = idle_since or time.time()
            if time.time() - idle_since > 60:
                outcome = "idle"
                break
    after = (dest / "INTENT.md").read_text(encoding="utf-8")
    if rec:
        stop(rec["pid"])
    fork.kill_leftovers(dest)
    return {"trial": n, "condition": "reminder", "mode": "interactive", "tick": "20:48",
            "path": str(dest), "seconds": round(time.time() - t0), "outcome": outcome,
            "session_id": rec.get("sessionId") if rec else None,
            "finished": outcome == "idle", "updated": after != before}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--out", default=str(HERE / "interactive_results.jsonl"))
    ap.add_argument("--root", default=str(HERE.parents[2] / "cleanvibe-experiment"))
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=1200)
    args = ap.parse_args()
    for i in range(args.trials):
        rec = run_trial(Path(args.root), args.start + i, args.timeout)
        with open(args.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
