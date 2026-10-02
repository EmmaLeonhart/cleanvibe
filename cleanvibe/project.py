"""cleanvibe 2 projects: create one, recognize one, open one.

The default cleanvibe project (``cleanvibe``, ``cleanvibe new [NAME]``) is an
open-ended, git-tracked working conversation. Nothing is assumed up front: the
first session opens by asking the user a question based on the directory, and
the agent keeps ``INTENT.md`` as its running read of what the user is trying
to do. Development and research practices arrive as skills once the work takes
that shape.

A new project gets a minimal scaffold (``CLAUDE.md``, ``README.md``,
``INTENT.md``, the ``.cleanvibe.json`` marker, ``.gitignore`` with ``scratch/``,
``sessions/``, ``data_lake/``, the vendored skills, and the session-log hooks),
a local git repo with no remote, and a Claude session. Sessions are always real
top-level sessions with Remote Control on (see ``launch.py``).
"""

from __future__ import annotations

import platform
from datetime import datetime
from pathlib import Path

from . import __version__, skills, templates
from .scaffold import _git_init, _launch_claude, _write, _write_gitkeep
from .trust import mark_trusted

MARKER = templates.V2_MARKER


def is_cleanvibe_repo(path: Path) -> bool:
    """True for a cleanvibe 2 project, or a project made by cleanvibe 1.x."""
    path = Path(path)
    if (path / MARKER).is_file():
        return True
    claude_md = path / "CLAUDE.md"
    if not claude_md.is_file():
        return False
    try:
        mentions = "cleanvibe" in claude_md.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        return False
    has_workflow = (path / "queue.md").is_file() or (path / ".claude" / "skills").is_dir()
    return mentions and has_workflow


AUTO_NAME = "untitled-cleanvibe-project"


def auto_project_path(base: Path | None = None) -> Path:
    """Where an unnamed project goes under ``base`` (cwd).

    ``untitled-cleanvibe-project`` if it is free; otherwise the same with a
    timestamp (``untitled-cleanvibe-project-YYYY-MM-DD-HHMM``); only if that is
    taken too, a number on the end (``-2``, ``-3``, ...).
    """
    base = Path(".") if base is None else Path(base)
    candidate = base / AUTO_NAME
    if not candidate.exists():
        return candidate
    stem = f"{AUTO_NAME}-{datetime.now().strftime('%Y-%m-%d-%H%M')}"
    candidate = base / stem
    n = 2
    while candidate.exists():
        candidate = base / f"{stem}-{n}"
        n += 1
    return candidate


def new_project(
    path: Path,
    auto_named: bool = False,
    dry_run: bool = False,
    no_claude: bool = False,
) -> None:
    """Create a cleanvibe 2 project at ``path`` and open its first session."""
    path = Path(path)
    project_name = path.name
    is_windows = platform.system() == "Windows"
    # Untitled projects get a passphrase-style session title; chosen names are used as is.
    session_name = templates.passphrase_name() if auto_named else None

    if dry_run:
        print(f"[dry-run] New cleanvibe project: {path}" + (" (auto-named)" if auto_named else ""))
        for rel in (
            "CLAUDE.md", "README.md", "INTENT.md", MARKER, ".gitignore",
            "sessions/.gitkeep", "data_lake/.gitkeep",
            ".claude/settings.json (session-log hooks)",
            ".claude/hooks/save_session_log.py",
            ".claude/scripts/data_lake_intake.py",
            f".claude/skills/ ({len(skills.SKILLS)} skills)",
        ):
            print(f"[dry-run] Would write: {path / rel}")
        if is_windows:
            print(f"[dry-run] Would write: {path / '!runClaude.bat'}")
        print("[dry-run] Would run: git init -b main, then commit (no remote)")
        if not no_claude:
            print("[dry-run] Would launch: claude (first-session prompt, --remote-control)")
        return

    path.mkdir(parents=True, exist_ok=True)
    print(f"Creating cleanvibe project: {path}")

    _write(path / "CLAUDE.md", templates.v2_claude_md(project_name))
    _write(path / "README.md", templates.v2_readme_md(project_name))
    _write(path / "INTENT.md", templates.v2_intent_md(project_name, auto_named))
    _write(path / MARKER, templates.v2_marker_json(project_name, auto_named, session_name))
    _write(path / ".gitignore", templates.V2_GITIGNORE)
    _write_gitkeep(path / "sessions")
    _write_gitkeep(path / "data_lake")
    skills.write_skills(path)

    _write(path / ".claude" / "settings.json", templates.chat_settings_json())
    hooks = path / ".claude" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    _write(hooks / "save_session_log.py", templates.CHAT_SAVE_SESSION_LOG_PY)
    scripts = path / ".claude" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    _write(scripts / "data_lake_intake.py", templates.V2_INTAKE_PY)

    if is_windows:
        _write(path / "!runClaude.bat", templates.v2_runclaude_bat(path, auto_named, session_name))

    _git_init(path, message=(
        f"Initial commit: cleanvibe v{__version__} project\n"
        f"\n"
        f"An open-ended, git-tracked working conversation. Its purpose is worked\n"
        f"out in the first session.\n"
        f"Generated by cleanvibe (https://github.com/EmmaLeonhart/cleanvibe):\n"
        f"- CLAUDE.md (conversation-first rules), INTENT.md (Claude's read of the goal)\n"
        f"- sessions/ + .claude hooks (transcripts saved and committed automatically)\n"
        f"- data_lake/ (files to work with), .gitignore (scratch/ never committed)\n"
        f"- .claude/skills/ (practices: development, research, autonomous loop, ...)"
        + ("\n\nNamed automatically: the user gave no name." if auto_named else "")
    ))

    if not no_claude:
        # A brand-new folder would stop the session at Claude Code's "trust this
        # folder?" prompt; pre-trust it so an agent-started session can be picked
        # up over Remote Control (see trust.py for the safeguards).
        if mark_trusted(path):
            print("  Marked the new folder as trusted in Claude Code's config")
        _launch_claude(
            path, templates.v2_first_prompt(path.resolve(), auto_named),
            remote_control=True, name=session_name or path.resolve().name,
        )


def open_project(path: Path, dry_run: bool = False, no_claude: bool = False) -> None:
    """Open an existing cleanvibe project (2 or 1.x) as a new session."""
    path = Path(path)
    if dry_run:
        print(f"[dry-run] Would open a new session in {path.resolve()} (resume prompt, --remote-control)")
        return
    if no_claude:
        print(f"{path.resolve()} is a cleanvibe project; not launching Claude (--no-claude).")
        return
    print(f"Opening cleanvibe project: {path.resolve()}")
    _launch_claude(
        path, templates.v2_resume_prompt(path.resolve()),
        remote_control=True, show_folder=False,
        name=_session_name(path),
    )


def _session_name(path: Path) -> str | None:
    """The session title for a project: its passphrase if it was auto-named (None
    for an auto-named project from before 2.0.3), otherwise the folder name."""
    import json
    try:
        marker = json.loads((Path(path) / MARKER).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        marker = {}
    if marker.get("auto_named"):
        return marker.get("session_name")
    return Path(path).resolve().name
