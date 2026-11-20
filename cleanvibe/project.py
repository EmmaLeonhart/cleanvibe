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

import os
import platform
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


def projects_home() -> Path:
    """Where projects go when cleanvibe runs from a place no project belongs:
    ``$CLEANVIBE_PROJECTS_DIR`` if set, else ``~/Documents/GitHub``."""
    env = os.environ.get("CLEANVIBE_PROJECTS_DIR")
    return Path(env).expanduser() if env else Path.home() / "Documents" / "GitHub"


def is_bare_location(path: Path) -> bool:
    """True where a bare command prompt opens: a drive or filesystem root, the
    home folder itself, or the Windows system folder (``cmd`` run as admin
    starts in System32). A project is never meant to land there."""
    p = Path(path).resolve()
    if p == Path(p.anchor):
        return True
    if p == Path.home().resolve():
        return True
    system_root = os.environ.get("SystemRoot") or os.environ.get("windir")
    if system_root:
        sr = Path(system_root).resolve()
        if p == sr or sr in p.parents:
            return True
    return False


def default_base(cwd: Path | None = None) -> Path:
    """The folder a new project is created under. Normally the cwd. From a bare
    location (see ``is_bare_location``) it is ``projects_home()`` if that folder
    exists (Emma, 2026-11-20: running ``cleanvibe`` from the root or a bare
    prompt should default to the GitHub directory). If it doesn't exist the cwd
    is kept, so nothing is created somewhere the user never chose."""
    cwd = Path(".") if cwd is None else Path(cwd)
    if is_bare_location(cwd):
        home = projects_home()
        if home.is_dir():
            return home
    return cwd


def auto_project_path(base: Path | None = None, rng=None) -> Path:
    """Where an unnamed project goes under ``base`` (cwd): a fresh passphrase
    name such as ``golden-swift-otter``, used for both the folder and the
    session title (Emma, 2026-10-05: the generated names are good, use them for
    the directory too). Drawn again if taken; after that, a number on the end.
    """
    base = Path(".") if base is None else Path(base)
    for _ in range(20):
        candidate = base / templates.passphrase_name(rng)
        if not candidate.exists():
            return candidate
    stem = templates.passphrase_name(rng)
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
    visibility: str | None = None,
    prompt: str | None = None,
) -> None:
    """Create a cleanvibe 2 project at ``path`` and open its first session.

    ``visibility`` (public/private/local) is the user's explicit choice for the
    GitHub repo; None leaves it to CLAUDE.md's default rule. ``prompt`` is a
    starting prompt from the user, appended to the first-session prompt and
    kept verbatim in the marker."""
    path = Path(path)
    project_name = path.name
    is_windows = platform.system() == "Windows"
    # An auto-named project's folder is a passphrase (auto_project_path); the
    # session title is the same name. Chosen names are used as is.
    session_name = path.name if auto_named else None

    if dry_run:
        print(f"[dry-run] New cleanvibe project: {path}" + (" (auto-named)" if auto_named else ""))
        for rel in (
            "CLAUDE.md", templates.V2_RULES_PATH, "README.md", "INTENT.md", MARKER, ".gitignore",
            "sessions/.gitkeep", "data_lake/.gitkeep",
            ".claude/settings.json (session-log + INTENT staleness hooks)",
            ".claude/hooks/save_session_log.py",
            ".claude/hooks/intent_staleness.py",
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

    _write(path / "CLAUDE.md", templates.v2_claude_md(
        project_name, auto_named, visibility, has_prompt=bool(prompt)))
    rules = path / templates.V2_RULES_PATH
    rules.parent.mkdir(parents=True, exist_ok=True)
    _write(rules, templates.v2_rules_md())
    _write(path / "README.md", templates.v2_readme_md(project_name))
    _write(path / "INTENT.md", templates.v2_intent_md(project_name, auto_named))
    _write(path / MARKER, templates.v2_marker_json(
        project_name, auto_named, session_name, visibility, prompt))
    _write(path / ".gitignore", templates.V2_GITIGNORE)
    _write_gitkeep(path / "sessions")
    _write_gitkeep(path / "data_lake")
    skills.write_skills(path)

    _write(path / ".claude" / "settings.json", templates.v2_settings_json())
    hooks = path / ".claude" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    _write(hooks / "save_session_log.py", templates.CHAT_SAVE_SESSION_LOG_PY)
    _write(hooks / "intent_staleness.py", templates.INTENT_STALENESS_PY)
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
            path, templates.v2_first_prompt(path.resolve(), auto_named, visibility, prompt),
            remote_control=True, name=session_name or path.resolve().name,
        )


def _merge_settings(existing: str | None, shipped: str) -> str:
    """Add cleanvibe's hook entries to a project's settings.json where the same
    command isn't already there. Every other key and entry is left as it was."""
    import json
    data = json.loads(existing) if existing and existing.strip() else {}
    hooks = data.setdefault("hooks", {})
    for event, entries in json.loads(shipped)["hooks"].items():
        have = hooks.setdefault(event, [])
        commands = {h.get("command") for e in have for h in e.get("hooks", [])}
        for entry in entries:
            if not {h["command"] for h in entry["hooks"]} <= commands:
                have.append(entry)
    return json.dumps(data, indent=2) + "\n"


MIGRATION_BACKUP = ".claude/cleanvibe/CLAUDE.pre-split.md"


def _split_sections(text: str) -> tuple:
    """(preamble, [(heading line, body), ...]) on '## ' and '# ' headings."""
    import re
    parts = re.split(r"(?m)^(#{1,2} .*)$", text)
    preamble, rest = parts[0], parts[1:]
    return preamble, [(rest[i], rest[i + 1]) for i in range(0, len(rest), 2)]


# Fingerprints of the rule sections cleanvibe 2.0.8 shipped (from
# tests/fixtures/v2_0_8_CLAUDE_*.md, project name replaced by <PROJECT>), so a
# migration can tell "older cleanvibe wording" from "edited locally" and only
# flags the second. Add the previous release's sections here at each release.
_KNOWN_SHIPPED = {
    "1f06a478d4e5355f", "26b1e8f3e03eb28a", "39e92862b1e62ae7", "56b9e625a55c55c8",
    "6bfcb96e036736c0", "9b7d8c2221752fcc", "a7217c37a7fd57b6", "a84e0248aa3f0411",
    "aadd2296b1d97bf5", "bef9dcb9485fa708", "c635ff87f7554c93", "df9ee3131cc17d3e",
}


def _fingerprint(body: str, project_name: str) -> str:
    import hashlib
    norm = body.strip().replace(project_name, "<PROJECT>") if project_name else body.strip()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


def _shipped_headings() -> dict:
    """Heading -> body of every section the shipped RULES.md has."""
    _, sections = _split_sections(templates.v2_rules_md())
    return {h.strip(): b.strip() for h, b in sections if h.startswith("## ")}


def migrate_claude_md(text: str, project_name: str, auto_named: bool) -> tuple:
    """Turn a pre-split (cleanvibe <= 2.0.8) CLAUDE.md into the split layout.

    Returns (new CLAUDE.md, moved headings, differing headings). Sections whose
    heading is a shipped rule section leave CLAUDE.md (RULES.md replaces them);
    "## Skills" becomes the short form, keeping the update-check date. Every
    other section is the project's own and stays, in order. "differing" lists
    moved sections whose text was not the current shipped text: an older
    cleanvibe's wording or a local edit, which the caller reports, since only
    a person can tell which (the old file is kept as a backup)."""
    import re
    shipped = _shipped_headings()
    old_names = {"## Skills": "## How skills work"}
    preamble, sections = _split_sections(text)
    kept, moved, differing = [], [], []
    date_line = "- **Last cleanvibe update check:** `never`"
    for heading, body in sections:
        h = heading.strip()
        if h == "# currentDate":
            continue  # regenerated below
        if h == "## Skills":
            m = re.search(r"^- \*\*Last cleanvibe update check:\*\*.*$", body, re.M)
            if m:
                date_line = m.group(0).strip()
            moved.append(h)
            continue
        name = old_names.get(h, h)
        if name in shipped:
            moved.append(h)
            if body.strip() != shipped[name] and \
                    _fingerprint(body, project_name) not in _KNOWN_SHIPPED:
                differing.append(h)
            continue
        kept.append(heading + body.rstrip("\n") + "\n")
    has = {s.split("\n", 1)[0].strip() for s in kept}
    out = (preamble.rstrip("\n") + "\n\n" if preamble.strip() else "") + "\n".join(kept)
    if "## Repository name" not in has:
        out += f"\n## Repository name\n{_repo_step_text(project_name, auto_named)}\n"
    if "## This project's own rules" not in has:
        out += ("\n## This project's own rules\n_Rules, conventions and constraints for this "
                f"project only go here, not in\n`{templates.V2_RULES_PATH}`: cleanvibe replaces "
                "that file whole when it updates._\n")
    out += ("\n## The rules cleanvibe ships\nHow every cleanvibe project works, from chat mode "
            "to the work loop. Kept in\ntheir own file so updates never overwrite this one:\n\n"
            f"@{templates.V2_RULES_PATH}\n"
            f"\n## Skills\n{date_line}\n"
            "- **Updates source:** <https://cleanvibe.emmaleonhart.com/updates.md>\n")
    from datetime import datetime
    out += f"\n# currentDate\nToday's date is {datetime.now().strftime('%Y-%m-%d')}.\n"
    return out, moved, differing


def _repo_step_text(project_name: str, auto_named: bool) -> str:
    return templates._repo_step(project_name, auto_named)


def migrate_project(path: Path, dry_run: bool = False) -> dict:
    """`cleanvibe refresh --migrate`: split a pre-2.0.9 project's CLAUDE.md.
    Backs the old file up to MIGRATION_BACKUP, rewrites CLAUDE.md, writes
    RULES.md. Does nothing to a project that already imports RULES.md."""
    import json
    path = Path(path)
    if not (path / MARKER).is_file():
        raise ValueError(f"{path} is not a cleanvibe 2 project (no {MARKER})")
    claude_path = path / "CLAUDE.md"
    text = claude_path.read_text(encoding="utf-8")
    if ("@" + templates.V2_RULES_PATH) in text:
        return {"already": True, "moved": [], "differing": []}
    marker = json.loads((path / MARKER).read_text(encoding="utf-8"))
    name = marker.get("name") or path.resolve().name
    auto = bool(marker.get("auto_named", False))
    new_text, moved, differing = migrate_claude_md(text, name, auto)
    if not dry_run:
        backup = path / MIGRATION_BACKUP
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(text, encoding="utf-8")
        claude_path.write_text(new_text, encoding="utf-8")
        (path / templates.V2_RULES_PATH).write_text(templates.v2_rules_md(), encoding="utf-8")
    return {"already": False, "moved": moved, "differing": differing}


def refresh_project(path: Path, dry_run: bool = False) -> list:
    """`cleanvibe refresh`: bring the files cleanvibe ships up to this version.

    Rewrites every skill, `.claude/cleanvibe/RULES.md` (only when CLAUDE.md
    imports it), the hooks and the intake script, and adds cleanvibe's hook
    entries to `.claude/settings.json` without touching anything else there.
    Never touches CLAUDE.md, INTENT.md or any other project file. Returns the
    relative paths that changed (or would change, with ``dry_run``).
    """
    import json
    path = Path(path)
    marker = path / MARKER
    if not marker.is_file():
        raise ValueError(f"{path} is not a cleanvibe 2 project (no {MARKER})")
    try:
        opted_out = json.loads(marker.read_text(encoding="utf-8")).get("session_log") is False
    except ValueError:
        opted_out = False

    wanted = {f".claude/skills/{slug}/SKILL.md": body for slug, body in skills.SKILLS.items()}
    claude = (path / "CLAUDE.md").read_text(encoding="utf-8") if (path / "CLAUDE.md").is_file() else ""
    if ("@" + templates.V2_RULES_PATH) in claude:
        wanted[templates.V2_RULES_PATH] = templates.v2_rules_md()
    wanted[".claude/hooks/intent_staleness.py"] = templates.INTENT_STALENESS_PY
    wanted[".claude/scripts/data_lake_intake.py"] = templates.V2_INTAKE_PY
    if not opted_out:
        wanted[".claude/hooks/save_session_log.py"] = templates.CHAT_SAVE_SESSION_LOG_PY

    settings_path = path / ".claude" / "settings.json"
    old_settings = settings_path.read_text(encoding="utf-8") if settings_path.is_file() else None
    shipped = templates.v2_settings_json()
    if opted_out:
        shipped_data = json.loads(shipped)
        for event in ("Stop", "SessionEnd"):
            shipped_data["hooks"].pop(event, None)
        shipped = json.dumps(shipped_data)
    new_settings = _merge_settings(old_settings, shipped)
    if old_settings is None or json.loads(old_settings or "{}") != json.loads(new_settings):
        wanted[".claude/settings.json"] = new_settings

    changed = []
    for rel, text in wanted.items():
        target = path / rel
        current = target.read_text(encoding="utf-8") if target.is_file() else None
        if current is not None and current.replace("\r\n", "\n") == text.replace("\r\n", "\n"):
            continue
        changed.append(rel)
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
    return changed


def open_project(path: Path, dry_run: bool = False, no_claude: bool = False) -> None:
    """Open an existing cleanvibe project (2 or 1.x) as a new session."""
    path = Path(path)
    if dry_run:
        print(f"[dry-run] Would open a new session in {path.resolve()} (resume prompt, --remote-control)")
        return
    if no_claude:
        print(f"{path.resolve()} is a cleanvibe project; not launching Claude.")
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
