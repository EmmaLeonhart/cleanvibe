"""``cleanvibe doctor`` — read-only audit of a cleanvibe project for drift.

Checks the conventions cleanvibe scaffolds, and that drift in practice:

* ``files``        — the core files exist. 1.x: CLAUDE.md, README.md, queue.md,
                      devlog.md. cleanvibe 2 (``.cleanvibe.json``): CLAUDE.md,
                      README.md, INTENT.md, the marker, and the transcript hook.
* ``skills``       — every vendored skill is present and matches this cleanvibe's copy.
* ``queue-done``   — "done" markers left in queue.md (ticked boxes, ✓, DONE, strikethrough).
                      queue.md is delete-only; done lives in devlog.md.
* ``version``      — queue.md's "Current version" pointer matches pyproject.toml.
* ``devlog-tags``  — every ``v*`` git tag is mentioned in devlog.md.
* ``section-refs`` — every ``CLAUDE.md § "X"`` reference points at a real heading.
* ``ci``           — a GitHub Actions workflow exists when there are tests.
* ``pages-gate``   — a Pages workflow skips the deploy on a private repo (v1.18.0+);
                      an older one fails on every push once the repo is private.

It changes nothing. Exit code 0 when clean, 1 when anything was found.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from . import skills

CORE_FILES = ("CLAUDE.md", "README.md", "queue.md", "devlog.md")
# cleanvibe 2 projects start minimal: no queue.md/devlog.md until the work needs
# them, but the transcript hook must be there or sessions go unrecorded.
V2_MARKER = ".cleanvibe.json"
V2_CORE_FILES = (
    "CLAUDE.md", "README.md", "INTENT.md", V2_MARKER,
    ".claude/settings.json", ".claude/hooks/save_session_log.py",
)

_DONE_MARKERS = (
    (re.compile(r"^\s*[-*]\s*\[[xX]\]"), "ticked checkbox"),
    (re.compile(r"[✓✔✅]"), "check mark"),
    (re.compile(r"^\s*(?:[-*]|\d+\.)\s.*\bDONE\b"), "DONE marker"),
    (re.compile(r"^\s*(?:[-*]|\d+\.)\s*~~.+~~"), "struck-through item"),
)
_VERSION_POINTER = re.compile(r"Current version:\s*`?v?([0-9][0-9A-Za-z.+-]*)`?")
_PYPROJECT_VERSION = re.compile(r'^version\s*=\s*"([^"]+)"', re.M)
# The section name is quoted on one line; never let a stray quote match across lines.
_SECTION_REF = re.compile(r'CLAUDE\.md`?[ \t]*§[ \t]*"([^"\n]+)"')


@dataclass
class Finding:
    check: str
    where: str
    message: str

    def __str__(self) -> str:
        return f"[{self.check}] {self.where}: {self.message}"


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def check_files(root: Path) -> list:
    required = V2_CORE_FILES if (root / V2_MARKER).is_file() else CORE_FILES
    return [
        Finding("files", name, "missing")
        for name in required
        if not (root / name).is_file()
    ]


def check_skills(root: Path) -> list:
    found = []
    for slug, body in skills.SKILLS.items():
        rel = f".claude/skills/{slug}/SKILL.md"
        text = _read(root / rel)
        if text is None:
            found.append(Finding("skills", rel, "missing"))
        elif text.replace("\r\n", "\n") != body.replace("\r\n", "\n"):
            found.append(Finding(
                "skills", rel,
                "differs from this cleanvibe's copy (outdated, or edited locally)",
            ))
    return found


def check_queue_done(root: Path) -> list:
    text = _read(root / "queue.md")
    if text is None:
        return []
    found = []
    for n, line in enumerate(text.splitlines(), 1):
        for pattern, label in _DONE_MARKERS:
            if pattern.search(line):
                snippet = line.strip()
                snippet = snippet if len(snippet) <= 70 else snippet[:67] + "..."
                found.append(Finding(
                    "queue-done", f"queue.md:{n}",
                    f"{label} left in place: {snippet!r} (delete it; log it in devlog.md)",
                ))
                break
    return found


def check_version(root: Path) -> list:
    queue = _read(root / "queue.md")
    pyproject = _read(root / "pyproject.toml")
    if queue is None or pyproject is None:
        return []
    pointer = _VERSION_POINTER.search(queue)
    actual = _PYPROJECT_VERSION.search(pyproject)
    if pointer and actual and pointer.group(1) != actual.group(1):
        return [Finding(
            "version", "queue.md",
            f"says current version {pointer.group(1)}, pyproject.toml says {actual.group(1)}",
        )]
    return []


def _git_tags(root: Path) -> list:
    try:
        out = subprocess.run(
            ["git", "tag", "--list", "v*"], cwd=root,
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    return out.stdout.split() if out.returncode == 0 else []


def check_devlog_tags(root: Path) -> list:
    devlog = _read(root / "devlog.md")
    if devlog is None:
        return []
    found = []
    for tag in _git_tags(root):
        bare = re.escape(tag[1:])
        # "v1.2.0" or "1.2.0", not as part of "1.2.0.1" or "11.2.0".
        if not re.search(rf"(?<![\w.])v?{bare}(?![\w]|\.\d)", devlog):
            found.append(Finding("devlog-tags", "devlog.md", f"no entry for release {tag}"))
    return found


def check_section_refs(root: Path) -> list:
    claude = _read(root / "CLAUDE.md")
    if claude is None:
        return []
    headings = {
        m.group(1).strip().lower()
        for m in re.finditer(r"^#{1,6}\s+(.+?)\s*$", claude, re.M)
    }
    found = []
    for name in ("CLAUDE.md", "queue.md", "README.md", "todo.md"):
        text = _read(root / name)
        if text is None:
            continue
        for ref in sorted(set(_SECTION_REF.findall(text))):
            if ref.strip().lower() not in headings:
                found.append(Finding(
                    "section-refs", name,
                    f'refers to CLAUDE.md section "{ref}", which has no such heading',
                ))
    return found


def check_ci(root: Path) -> list:
    workflows = root / ".github" / "workflows"
    has_workflow = workflows.is_dir() and any(
        p.suffix in (".yml", ".yaml") for p in workflows.iterdir()
    )
    if not has_workflow and (root / "tests").is_dir():
        return [Finding("ci", ".github/workflows/", "tests/ exists but no CI workflow runs it")]
    return []


def check_pages_gate(root: Path) -> list:
    workflows = root / ".github" / "workflows"
    if not workflows.is_dir():
        return []
    found = []
    for wf in sorted(workflows.glob("*.y*ml")):
        text = _read(wf) or ""
        if "configure-pages" in text and "CLEANVIBE_PAGES" in text:
            continue
        if "actions/deploy-pages" in text and "upload-pages-artifact" in text and \
                "report" in text and "github.event.repository.private" not in text:
            found.append(Finding(
                "pages-gate", f".github/workflows/{wf.name}",
                "cleanvibe report workflow predates v1.18.0: its Pages deploy fails on a "
                "private repo. Copy the `if:` gate from a fresh `cleanvibe research` scaffold",
            ))
    return found


CHECKS = (
    check_files,
    check_skills,
    check_queue_done,
    check_version,
    check_devlog_tags,
    check_section_refs,
    check_ci,
    check_pages_gate,
)


def run_checks(root: Path) -> list:
    root = Path(root)
    found = []
    for check in CHECKS:
        found.extend(check(root))
    return found


def _say(text: str) -> None:
    # Findings quote queue.md lines (check marks etc.); never crash a console
    # whose encoding (e.g. Windows cp1252) cannot print them.
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    print(text.encode(encoding, "replace").decode(encoding, "replace"))


def doctor(root: Path) -> int:
    """Print the audit for ``root``; return the process exit code."""
    root = Path(root)
    if not root.is_dir():
        _say(f"Error: {root} is not a directory.")
        return 2
    findings = run_checks(root)
    _say(f"cleanvibe doctor: {root.resolve()}")
    if not findings:
        _say(f"  No drift found ({len(CHECKS)} checks).")
        return 0
    for finding in findings:
        _say(f"  {finding}")
    _say(f"  {len(findings)} finding(s). doctor is read-only; nothing was changed.")
    return 1
