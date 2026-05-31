"""Back-fill cleanvibe skills into existing repos and trim their CLAUDE.md.

For each git repo under ``--root`` whose CLAUDE.md contains the old inlined
workflow blocks: sync (fetch + ff-only), write ``.claude/skills/``, trim the
skill-covered sections out of CLAUDE.md (leaving a ``## Skills`` pointer), commit,
and push. Dirty or diverged repos are skipped and reported. ``--dry-run`` (the
default) only reports and touches nothing; ``--apply`` performs the changes.

Single source of truth for the skill bodies is ``cleanvibe/skills.py``.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cleanvibe import skills  # noqa: E402

# A CLAUDE.md is a migration target only if at least two of these appear — they
# are the fingerprints of the old inlined workflow/cron/emergency blocks.
MARKERS = ("Emergency Stop Mode", "three-cron", "LOCAL by default",
           "CronCreate", "Hourly status-report", "## Workflow Rules")

# Section headings whose entire section (heading + body + any nested
# subsections) is removed because the content now lives in a skill.
DROP_HEADINGS = (
    "Emergency Stop Mode",
    "Cron jobs and scheduled work",
    "Cron jobs and scheduled work — LOCAL by default",
    "Autonomous productivity loop",
    "Hourly status-report cron",
    "Check cleanvibe for skill updates",
    "Workflow Rules",
    "Queue and longer-horizon work",
    "Writing",
    "Testing",
)

POINTER = """## Skills

Workflow behaviors live as skills in `.claude/skills/` (auto-discovered by Claude Code):
`emergency-stop`, `cron-is-local`, `autonomous-loop`, `queue-driven-workflow`,
`writing-style`, `cleanvibe-update-check`. They are vendored into this repo and kept
current by the `cleanvibe-update-check` skill.

- **Last cleanvibe update check:** `never`
- **Updates source:** <https://cleanvibe.emmaleonhart.com/updates.md>
"""


def _git(repo: Path, *args, check=False):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                          text=True, check=check)


def _has_markers(claude: Path) -> bool:
    if not claude.exists():
        return False
    text = claude.read_text(encoding="utf-8", errors="replace")
    return sum(m in text for m in MARKERS) >= 2


def _heading_level(line: str):
    """Return (level, title) if line is an ATX heading, else (None, None)."""
    s = line.lstrip()
    if not s.startswith("#"):
        return None, None
    hashes = len(s) - len(s.lstrip("#"))
    return hashes, s.lstrip("#").strip()


def _is_drop(title: str) -> bool:
    return any(title.startswith(h) for h in DROP_HEADINGS)


def _trim_claude(text: str) -> str:
    """Remove the skill-covered sections; prepend the ## Skills pointer once.

    A dropped section runs from its heading until the NEXT heading of any level.
    This is deliberately conservative: it removes the boilerplate block (which is
    always flat — bullets/numbered lists, no internal headings) but PRESERVES any
    project-specific sub-headed content a repo placed under a boilerplate heading
    (e.g. custom `###` rules under `## Workflow Rules`). A run of consecutive
    boilerplate `##` sections is each matched and dropped in turn.
    """
    lines = text.splitlines(keepends=True)
    out = []
    skipping = False
    for ln in lines:
        level, title = _heading_level(ln)
        if level is not None:
            skipping = _is_drop(title)
        if not skipping:
            out.append(ln)
    body = "".join(out)
    # Collapse the runs of blank lines the deletions can leave behind.
    cleaned = []
    blank = 0
    for ln in body.splitlines(keepends=True):
        if ln.strip() == "":
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        cleaned.append(ln)
    body = "".join(cleaned).rstrip() + "\n"
    if "## Skills" not in body:
        if body.startswith("# "):
            nl = body.index("\n") + 1
            body = body[:nl] + "\n" + POINTER + "\n" + body[nl:]
        else:
            body = POINTER + "\n" + body
    return body


def _is_replication(repo: Path) -> bool:
    """cleanvibe replicate projects are a bounded, separately-tuned workflow,
    exempt from the skill set (same principle as the autonomous-loop exemption).
    Detected by the replication scaffold's signature files."""
    return (repo / "replication_target").is_dir() or (repo / "paper.json").is_file()


def find_repos(root: Path):
    for child in sorted(root.iterdir()):
        if not child.is_dir() or not (child / ".git").exists():
            continue
        if _is_replication(child):
            continue
        if _has_markers(child / "CLAUDE.md"):
            yield child


def migrate(repo: Path, apply: bool) -> str:
    name = repo.name
    if not apply:
        return f"WOULD MIGRATE {name}"

    status = _git(repo, "status", "--porcelain").stdout.strip()
    if status:
        return f"SKIP {name}: dirty working tree"

    has_origin = "origin" in _git(repo, "remote").stdout.split()
    if has_origin:
        if _git(repo, "fetch", "origin").returncode != 0:
            return f"SKIP {name}: git fetch failed"
        upstream = _git(repo, "rev-parse", "--abbrev-ref", "@{u}")
        if upstream.returncode == 0:
            counts = _git(repo, "rev-list", "--left-right", "--count",
                          "HEAD...@{u}").stdout.split()
            if len(counts) == 2:
                ahead, behind = counts
                if ahead != "0" and behind != "0":
                    return f"SKIP {name}: diverged from upstream"
                if behind != "0" and _git(repo, "merge", "--ff-only",
                                          "@{u}").returncode != 0:
                    return f"SKIP {name}: not fast-forwardable"

    skills.write_skills(repo)
    claude = repo / "CLAUDE.md"
    claude.write_text(_trim_claude(claude.read_text(encoding="utf-8")),
                      encoding="utf-8")
    _git(repo, "add", "-A")
    commit = _git(repo, "commit", "-m",
                  "chore: vendor cleanvibe skills into .claude/skills; "
                  "trim CLAUDE.md to pointer")
    if commit.returncode != 0:
        return f"FAILED {name}: commit failed ({commit.stderr.strip()[:80]})"
    if not has_origin:
        return f"MIGRATED {name} (no remote; committed locally, not pushed)"
    pushed = _git(repo, "push")
    if pushed.returncode != 0:
        return f"COMMITTED {name} but PUSH FAILED ({pushed.stderr.strip()[:80]})"
    return f"MIGRATED+PUSHED {name}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(Path.home() / "Documents" / "Github"))
    ap.add_argument("--apply", action="store_true",
                    help="perform the migration (default is dry-run)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report only; touch nothing (the default)")
    args = ap.parse_args(argv)
    apply = args.apply and not args.dry_run
    root = Path(args.root)

    results = [migrate(repo, apply) for repo in find_repos(root)]
    print(f"\n=== cleanvibe skill migration ({'APPLY' if apply else 'DRY-RUN'}) "
          f"under {root} ===")
    for r in results:
        print(" ", r)
    print(f"\n{len(results)} repo(s) with the old blocks detected.")
    if not apply and results:
        print("Re-run with --apply to perform the migration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
