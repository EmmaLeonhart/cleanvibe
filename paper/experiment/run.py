"""Controlled test of the INTENT.md staleness cue, in headless Claude Code sessions.

    python paper/experiment/run.py --trials 10 --out paper/experiment/results.jsonl

Each trial builds a fresh fixture project with the current cleanvibe scaffold
(`cleanvibe.project.new_project`), gives it a backdated history in which
INTENT.md was last written 3.2 hours and 6 work commits ago and contains one
sentence those commits made false, and runs ONE loop tick in a headless
session (`claude -p`). Conditions, interleaved a, b, c, a, b, c, ...:

  a  none      tick prompt without the INTENT sentence; staleness hook removed
  b  reminder  cleanvibe's tick prompt ("Re-read INTENT.md and update it if your
               understanding has changed"); hook removed (as in cleanvibe 2.0.3)
  c  age       the same tick prompt; hook kept, so the context also says
               "INTENT.md last changed 3.2 hours and 6 commits ago" (2.0.4)

Scored from the fixture afterwards (score.py does the same on saved runs):
  updated    INTENT.md differs from the fixture's version (committed or not)
  corrected  the false sentence is gone and the finished features are named
  worked     the queue item was attempted (the code or tests changed)

Fixtures live under --root (default: ../cleanvibe-experiment next to the repo,
outside this repository so its CLAUDE.md is not loaded). Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from cleanvibe.launch import clean_env  # noqa: E402
from cleanvibe.project import new_project  # noqa: E402

TICK_FULL = (
    "[cleanvibe cron] Commit and push any and all changes, then continue working on "
    "the queue (refill it from the open questions if it is empty). Re-read INTENT.md "
    "and update it if your understanding has changed; fill in README.md if the purpose "
    "is now clear. Check the clock before writing any time down."
)
TICK_NONE = (
    "[cleanvibe cron] Commit and push any and all changes, then continue working on "
    "the queue (refill it from the open questions if it is empty). Check the clock "
    "before writing any time down."
)
CONDITIONS = {"a": ("none", TICK_NONE, False), "b": ("reminder", TICK_FULL, False),
              "c": ("age", TICK_FULL, True)}
FALSE_SENTENCE = "Category totals and the monthly report are not started yet."
ALLOWED = ("Read,Edit,Write,Glob,Grep,Bash(git:*),Bash(python:*),Bash(python3:*),"
           "Bash(ls:*),Bash(date:*),Bash(cat:*)")

INTENT_V1 = f"""# What this project is for

_Maintained by Claude: a running read of what the user is trying to do._

## Current understanding

A small command-line tool, `ledger.py`, that reads an expenses CSV
(`date,category,amount`) and prints totals. The user wants it kept to the
standard library.

## Current state

It reads the CSV and prints the grand total. {FALSE_SENTENCE}

## Plan

1. Category totals (`--by-category`).
2. A monthly report (`--monthly`).

## Confidence

High: the brief in `data_lake/brief.md` says exactly this.

## Log

- Work mode started; goal taken from the brief.
"""

LEDGER_V1 = '''"""Total the expenses in a CSV file (date,category,amount)."""
import argparse
import csv


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            yield r["date"], r["category"], float(r["amount"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    args = ap.parse_args(argv)
    print(f"total {sum(a for _, _, a in rows(args.csv)):.2f}")


if __name__ == "__main__":
    main()
'''

LEDGER_V2 = '''"""Total the expenses in a CSV file (date,category,amount)."""
import argparse
import csv
from collections import defaultdict


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            yield r["date"], r["category"], float(r["amount"])


def by_category(items):
    out = defaultdict(float)
    for _, cat, amount in items:
        out[cat] += amount
    return dict(sorted(out.items()))


def monthly(items):
    out = defaultdict(float)
    for date, _, amount in items:
        out[date[:7]] += amount
    return dict(sorted(out.items()))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--by-category", action="store_true")
    ap.add_argument("--monthly", action="store_true")
    args = ap.parse_args(argv)
    items = list(rows(args.csv))
    if args.by_category:
        for k, v in by_category(items).items():
            print(f"{k} {v:.2f}")
    elif args.monthly:
        for k, v in monthly(items).items():
            print(f"{k} {v:.2f}")
    else:
        print(f"total {sum(a for _, _, a in items):.2f}")


if __name__ == "__main__":
    main()
'''

TESTS = '''import unittest

import ledger

ITEMS = [("2026-01-03", "food", 10.0), ("2026-01-20", "rent", 500.0),
         ("2026-02-02", "food", 12.5)]


class TestLedger(unittest.TestCase):
    def test_by_category(self):
        self.assertEqual(ledger.by_category(ITEMS), {"food": 22.5, "rent": 500.0})

    def test_monthly(self):
        self.assertEqual(ledger.monthly(ITEMS), {"2026-01": 510.0, "2026-02": 12.5})


if __name__ == "__main__":
    unittest.main()
'''

QUEUE = """# Queue

Delete-only: a finished item is deleted here and recorded in `devlog.md`.

1. Add a `--since YYYY-MM-DD` option to `--monthly` that skips earlier rows,
   with a test in `test_ledger.py`.
"""


def git(root, *args, when=None):
    env = dict(os.environ)
    if when is not None:
        stamp = f"@{int(when)} +0000"
        env.update(GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    subprocess.run(["git", "-C", str(root), *args], check=True, env=env,
                   capture_output=True, text=True)


def write(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def commit(root, msg, when):
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg, when=when)


def build_fixture(path: Path, keep_hook: bool):
    """A cleanvibe project whose INTENT.md is 3.2 h and 6 work commits stale."""
    now = time.time()
    new_project(path, auto_named=False, no_claude=True)
    git(path, "commit", "--amend", "-q", "--no-edit", when=now - 3.6 * 3600)
    if not keep_hook:
        st = path / ".claude" / "settings.json"
        cfg = json.loads(st.read_text(encoding="utf-8"))
        cfg["hooks"].pop("UserPromptSubmit", None)
        st.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
        (path / ".claude" / "hooks" / "intent_staleness.py").unlink()
    marker = path / ".cleanvibe.json"
    m = json.loads(marker.read_text(encoding="utf-8"))
    m["intake_at"] = "done"
    marker.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")
    h = 3600
    write(path, "data_lake/brief.md",
          "# Brief\n\nA stdlib Python CLI that totals an expenses CSV: grand total, "
          "then totals by category, then a monthly report.\n")
    commit(path, "Intake: the brief into data_lake/", now - 3.4 * h)
    write(path, "INTENT.md", INTENT_V1)
    write(path, "ledger.py", LEDGER_V1)
    write(path, "devlog.md", "# Devlog\n\n- Grand total.\n")
    commit(path, "INTENT.md: work mode from the brief; grand total", now - 3.2 * h)
    steps = [
        ("by_category()", 2.8), ("--by-category flag", 2.3), ("monthly()", 1.7),
        ("--monthly flag", 1.2), ("tests for both", 0.8), ("devlog and queue", 0.4),
    ]
    for i, (what, ago) in enumerate(steps):
        if i == 3:
            write(path, "ledger.py", LEDGER_V2)
        if i == 4:
            write(path, "test_ledger.py", TESTS)
        if i == 5:
            write(path, "queue.md", QUEUE)
            write(path, "devlog.md", "# Devlog\n\n- Grand total.\n- Category totals "
                  "(`--by-category`) done, with tests.\n- Monthly report "
                  "(`--monthly`) done, with tests.\n")
        else:
            write(path, f"notes/step{i}.md", f"{what}\n")
        commit(path, f"ledger: {what}", now - ago * h)


def score(path: Path) -> dict:
    intent = (path / "INTENT.md").read_text(encoding="utf-8")
    ledger = (path / "ledger.py").read_text(encoding="utf-8")
    tests = (path / "test_ledger.py").read_text(encoding="utf-8")
    lower = intent.lower()
    return {
        "updated": intent != INTENT_V1,
        "corrected": FALSE_SENTENCE not in intent and "not started" not in lower
                     and "categor" in lower and "monthly" in lower,
        "worked": "since" in ledger or "since" in tests,
    }


def run_trial(root: Path, n: int, cond: str, timeout: int) -> dict:
    label, prompt, keep_hook = CONDITIONS[cond]
    path = root / f"t{n:03d}-{label}"
    if path.exists():
        shutil.rmtree(path)
    build_fixture(path, keep_hook)
    t0 = time.time()
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json",
             "--allowedTools", ALLOWED],
            cwd=str(path), env=clean_env(), capture_output=True, text=True,
            timeout=timeout)
        out = proc.stdout
    except subprocess.TimeoutExpired:
        out = ""
    meta = {}
    try:
        meta = json.loads(out)
    except ValueError:
        pass
    return {"trial": n, "condition": label, "path": str(path),
            "seconds": round(time.time() - t0), "cost_usd": meta.get("total_cost_usd"),
            "session_id": meta.get("session_id"), "num_turns": meta.get("num_turns"),
            "result": (meta.get("result") or "")[:300],
            # A run cut off by a usage limit or an error is not a valid trial.
            "finished": bool(meta) and not meta.get("is_error")
                        and "session limit" not in (meta.get("result") or ""),
            **score(path)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=10, help="per condition")
    ap.add_argument("--out", default=str(REPO / "paper" / "experiment" / "results.jsonl"))
    ap.add_argument("--root", default=str(REPO.parent / "cleanvibe-experiment"))
    ap.add_argument("--start", type=int, default=1, help="first trial number")
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    order = [c for _ in range(args.trials) for c in "abc"]
    for i, cond in enumerate(order):
        rec = run_trial(root, args.start + i, cond, args.timeout)
        with open(args.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
