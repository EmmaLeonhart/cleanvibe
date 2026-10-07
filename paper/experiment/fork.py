"""Experiment 2: the staleness cue in a real long context, by forking a session.

    python paper/experiment/fork.py --trials 10 --out paper/experiment/fork_results.jsonl

The chess control session (no staleness hook) had gone hours without updating
INTENT.md when its 20:48 UTC loop tick, which carried the reminder, again
left it unchanged. Each trial restores that moment and replays one tick:

  repo        a clone of the session's repository at the commit current then
  transcript  the session's transcript up to (not including) that tick, with
              the old project path rewritten to the clone's, resumed with
              `claude -p --resume <id> --fork-session`

Conditions, interleaved: none (tick prompt without the INTENT sentence),
reminder (the tick prompt the session actually got), age (the same prompt
with cleanvibe's staleness hook installed, so the context also says how long
ago INTENT.md changed). Scored: did INTENT.md change. Processes a trial
leaves behind (match runners, engines) are killed after it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cleanvibe import templates  # noqa: E402
from cleanvibe.launch import clean_env  # noqa: E402
from run import ALLOWED, TICK_FULL, TICK_NONE  # noqa: E402

HOME = Path(os.path.expanduser("~"))
SOURCE = REPO.parent / "cleanvibe-practice" / "crisp-golden-badger"
SESSION = "b19c0300-fa3c-42a8-b340-2b9f471463b9"
CUT_LINE = 762            # the 20:48 UTC tick; lines before it are kept
COMMIT = "b5ecc1f790dfacd4a75c35aa201ec5d8f602f10f"
CONDITIONS = {"a": ("none", TICK_NONE, False), "b": ("reminder", TICK_FULL, False),
              "c": ("age", TICK_FULL, True)}


def tick_points():
    """(line index, UTC timestamp, repo commit) of each loop tick in the source
    session between 17:00 and 21:00 UTC: the ticks at which it had gone over an
    hour without changing INTENT.md and left it so (the declines reported)."""
    src = project_dir(SOURCE) / f"{SESSION}.jsonl"
    lines = src.read_text(encoding="utf-8").splitlines()
    ticks = []
    for i, l in enumerate(lines):
        d = json.loads(l)
        c = d.get("message", {}).get("content") if d.get("type") == "user" else None
        t = c if isinstance(c, str) else (c[0].get("text", "") if isinstance(c, list) and c
                                          and c[0].get("type") == "text" else "")
        if t.startswith("[cleanvibe cron] Commit") and "17:00" < d["timestamp"][11:16] < "21:00":
            ticks.append((i, d["timestamp"]))
    out = []
    for i, ts in ticks:
        commit = subprocess.run(["git", "-C", str(SOURCE), "log", "-1", "--format=%H",
                                 f"--until={ts}"], capture_output=True, text=True).stdout.strip()
        out.append((i, ts, commit))
    return out


def project_dir(path: Path) -> Path:
    return HOME / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(path))


def path_forms(p: Path):
    s = str(p)
    return [s.replace("\\", "\\\\"), s, s.replace("\\", "/"),
            re.sub(r"[^A-Za-z0-9]", "-", s)]


def build(dest: Path, keep_hook: bool, cut_line: int = CUT_LINE, commit: str = COMMIT):
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    subprocess.run(["git", "clone", "-q", str(SOURCE), str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "checkout", "-q", "-B", "main", commit], check=True)
    subprocess.run(["git", "-C", str(dest), "remote", "remove", "origin"], check=True)
    if keep_hook:
        hooks = dest / ".claude" / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        (hooks / "intent_staleness.py").write_text(templates.INTENT_STALENESS_PY, encoding="utf-8")
        st = dest / ".claude" / "settings.json"
        cfg = json.loads(st.read_text(encoding="utf-8"))
        cfg["hooks"]["UserPromptSubmit"] = json.loads(templates.v2_settings_json())["hooks"]["UserPromptSubmit"]
        st.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    src = project_dir(SOURCE) / f"{SESSION}.jsonl"
    text = "\n".join(src.read_text(encoding="utf-8").splitlines()[:cut_line]) + "\n"
    for old, new in zip(path_forms(SOURCE), path_forms(dest)):
        text = text.replace(old, new)
    out = project_dir(dest)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{SESSION}.jsonl").write_text(text, encoding="utf-8")


def kill_leftovers(dest: Path):
    pattern = str(dest).replace("\\", "\\\\")
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    f"Get-CimInstance Win32_Process | Where-Object {{ $_.CommandLine -match "
                    f"[regex]::Escape('{dest}') -and $_.Name -ne 'powershell.exe' }} | "
                    f"ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}"],
                   capture_output=True, text=True)


def intent_at_commit(commit: str = COMMIT) -> str:
    return subprocess.run(["git", "-C", str(SOURCE), "show", f"{commit}:INTENT.md"],
                          capture_output=True, text=True, check=True).stdout


def run_trial(root: Path, n: int, cond: str, timeout: int, cut_line: int = CUT_LINE,
              commit: str = COMMIT, tick: str = "20:48") -> dict:
    label, prompt, keep_hook = CONDITIONS[cond]
    dest = root / f"f{n:03d}-{label}"
    build(dest, keep_hook, cut_line, commit)
    before = intent_at_commit(commit)
    t0 = time.time()
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--resume", SESSION, "--fork-session",
             "--output-format", "json", "--allowedTools", ALLOWED],
            cwd=str(dest), env=clean_env(), capture_output=True, text=True, timeout=timeout)
        out = proc.stdout
    except subprocess.TimeoutExpired:
        out = ""
    kill_leftovers(dest)
    try:
        meta = json.loads(out)
    except ValueError:
        meta = {}
    after = (dest / "INTENT.md").read_text(encoding="utf-8")
    return {"trial": n, "condition": label, "tick": tick, "path": str(dest),
            "seconds": round(time.time() - t0),
            "cost_usd": meta.get("total_cost_usd"), "num_turns": meta.get("num_turns"),
            "session_id": meta.get("session_id"), "updated": after != before,
            "result": (meta.get("result") or "")[:300],
            # A run cut off by a usage limit or an error is not a valid trial.
            "finished": bool(meta) and not meta.get("is_error")
                        and "session limit" not in (meta.get("result") or "")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=10, help="per condition")
    ap.add_argument("--out", default=str(REPO / "paper" / "experiment" / "fork_results.jsonl"))
    ap.add_argument("--root", default=str(REPO.parent / "cleanvibe-experiment"))
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--only", default="abc", help="conditions to run, e.g. c for a pilot")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--all-ticks", action="store_true",
                    help="replay each declined tick (17:18-20:48) instead of only 20:48")
    args = ap.parse_args()
    if args.all_ticks:
        n = args.start
        for _ in range(args.trials):
            for line, ts, commit in tick_points():
                for cond in args.only:
                    rec = run_trial(Path(args.root), n, cond, args.timeout, line, commit, ts[11:16])
                    n += 1
                    with open(args.out, "a", encoding="utf-8") as f:
                        f.write(json.dumps(rec) + "\n")
                    print(json.dumps(rec), flush=True)
                    if not rec["finished"] and "session limit" in rec["result"]:
                        print("usage limit reached; stopping", flush=True)
                        return
        return
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    order = [c for _ in range(args.trials) for c in args.only]
    for i, cond in enumerate(order):
        rec = run_trial(root, args.start + i, cond, args.timeout)
        if not rec["finished"] and "session limit" in rec["result"]:
            print("usage limit reached; stopping", flush=True)
            with open(args.out, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
            break
        with open(args.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
