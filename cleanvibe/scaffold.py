"""Core scaffolding logic for cleanvibe.

Creates project directories, writes template files, initializes git,
and launches Claude Code.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

from . import __version__, templates


def create_project(path: Path, dry_run: bool = False, no_claude: bool = False) -> None:
    """Create a new project directory with opinionated scaffolding."""
    project_name = path.name

    is_windows = platform.system() == "Windows"

    if dry_run:
        print(f"[dry-run] Would create directory: {path}")
        print(f"[dry-run] Would write: {path / 'CLAUDE.md'}")
        print(f"[dry-run] Would write: {path / 'README.md'}")
        print(f"[dry-run] Would write: {path / 'queue.md'}")
        print(f"[dry-run] Would write: {path / '.gitignore'}")
        print(f"[dry-run] Would write: {path / 'data_lake' / '.gitkeep'}")
        if is_windows:
            print(f"[dry-run] Would write: {path / 'runclaude.bat'}")
        print(f"[dry-run] Would run: git init")
        print(f"[dry-run] Would run: git add . && git commit")
        if not no_claude:
            print(f"[dry-run] Would launch: claude")
        return

    path.mkdir(parents=True, exist_ok=True)

    _write(path / "CLAUDE.md", templates.claude_md(project_name))
    _write(path / "README.md", templates.readme_md(project_name))
    _write(path / "queue.md", templates.queue_md(project_name))
    _write(path / ".gitignore", templates.GITIGNORE)
    _write_gitkeep(path / "data_lake")

    if is_windows:
        _write(path / "runclaude.bat", templates.RUNCLAUDE_BAT)

    _git_init(path)

    if not no_claude:
        _launch_claude(path)


def clone_project(repo: str, path: Path, dry_run: bool = False, no_claude: bool = False) -> None:
    """Clone a repo and inject scaffolding if missing."""
    is_windows = platform.system() == "Windows"

    if dry_run:
        print(f"[dry-run] Would run: git clone {repo} {path}")
        print(f"[dry-run] Would check for missing CLAUDE.md / README.md / queue.md / .gitignore")
        if is_windows:
            print(f"[dry-run] Would check for missing runclaude.bat")
        print(f"[dry-run] Would inject any missing files")
        if not no_claude:
            print(f"[dry-run] Would launch: claude")
        return

    result = subprocess.run(["git", "clone", repo, str(path)])
    if result.returncode != 0:
        print(f"Error: git clone failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(1)

    project_name = path.name
    _inject_scaffold(path, project_name, is_windows)

    if not no_claude:
        _launch_claude(path)


def convert_project(path: Path, dry_run: bool = False, no_claude: bool = False) -> None:
    """Convert an existing directory into a cleanvibe project.

    If the directory is not a git repo, initializes git and makes two commits:
      1. All existing files as-is
      2. The injected cleanvibe scaffold files

    If it's already a git repo, just injects missing scaffold files without committing.
    """
    is_windows = platform.system() == "Windows"
    project_name = path.name
    is_git_repo = (path / ".git").is_dir()

    if dry_run:
        if not is_git_repo:
            print(f"[dry-run] Would run: git init")
            print(f"[dry-run] Would commit all existing files (commit 1)")
        print(f"[dry-run] Would check for missing CLAUDE.md / README.md / queue.md / .gitignore")
        if is_windows:
            print(f"[dry-run] Would check for missing runclaude.bat")
        if not is_git_repo:
            print(f"[dry-run] Would commit scaffold files (commit 2)")
        if not no_claude:
            print(f"[dry-run] Would launch: claude")
        return

    if not is_git_repo:
        # Commit 1: all existing files
        subprocess.run(["git", "init"], cwd=path, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit: existing project files"],
            cwd=path,
            capture_output=True,
        )
        print(f"  Initialized git repo and committed existing files")

    # Inject missing scaffold files
    injected = _inject_scaffold(path, project_name, is_windows)

    if not is_git_repo and injected:
        # Commit 2: scaffold files
        subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
        scaffold_message = (
            f"Add cleanvibe v{__version__} scaffold\n"
            f"\n"
            f"Injected by cleanvibe convert (https://github.com/Immanuelle/cleanvibe):\n"
            f"missing CLAUDE.md / queue.md / README.md / .gitignore as applicable."
        )
        subprocess.run(
            ["git", "commit", "-m", scaffold_message],
            cwd=path,
            capture_output=True,
        )
        print(f"  Committed scaffold files")

    if not no_claude:
        _launch_claude(path)


def _inject_scaffold(path: Path, project_name: str, is_windows: bool) -> bool:
    """Inject missing scaffold files into a directory. Returns True if any were injected."""
    injected = False

    claude_md = path / "CLAUDE.md"
    if not claude_md.exists():
        _write(claude_md, templates.claude_md(project_name))
        print(f"  Injected CLAUDE.md (was missing)")
        injected = True

    readme = path / "README.md"
    if not readme.exists():
        _write(readme, templates.readme_md(project_name))
        print(f"  Injected README.md (was missing)")
        injected = True

    queue = path / "queue.md"
    if not queue.exists():
        _write(queue, templates.queue_md(project_name))
        print(f"  Injected queue.md (was missing)")
        injected = True

    gitignore = path / ".gitignore"
    if not gitignore.exists():
        _write(gitignore, templates.GITIGNORE)
        print(f"  Injected .gitignore (was missing)")
        injected = True

    gitkeep = path / "data_lake" / ".gitkeep"
    if not gitkeep.exists():
        _write_gitkeep(path / "data_lake")
        print(f"  Injected data_lake/.gitkeep (was missing)")
        injected = True

    if is_windows:
        runclaude = path / "runclaude.bat"
        if not runclaude.exists():
            _write(runclaude, templates.RUNCLAUDE_BAT)
            print(f"  Injected runclaude.bat (was missing)")
            injected = True

    if not injected:
        print(f"  All scaffold files already present, nothing to inject")

    return injected


def _write(filepath: Path, content: str) -> None:
    filepath.write_text(content, encoding="utf-8")
    print(f"  Created {filepath.name}")


def _write_gitkeep(directory: Path) -> None:
    """Create ``directory`` and an empty ``.gitkeep`` so git tracks it when empty.

    The data lake exists from the first commit so a user can drop files
    straight into it before the bootstrap session ever runs; git does not
    track empty directories without the placeholder.
    """
    directory.mkdir(parents=True, exist_ok=True)
    keep = directory / ".gitkeep"
    keep.write_text("", encoding="utf-8")
    print(f"  Created {directory.name}/.gitkeep")


def _git_init(path: Path, message=None) -> None:
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    if message is None:
        message = (
            f"Initial commit: scaffolded with cleanvibe v{__version__}\n"
            f"\n"
            f"Generated by cleanvibe (https://github.com/Immanuelle/cleanvibe):\n"
            f"- CLAUDE.md (workflow rules: plan-into-queue-first, mirror to task tool)\n"
            f"- queue.md (active work queue)\n"
            f"- README.md\n"
            f"- .gitignore"
        )
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=path,
        capture_output=True,
    )
    print(f"  Initialized git repo with initial commit")


def _launch_claude(path: Path) -> None:
    """Launch Claude Code in the project directory.

    On Windows, opens a new cmd window. On Unix, replaces the current process.
    """
    print(f"  Launching Claude Code...")
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(["explorer", str(path)])
            subprocess.Popen(
                ["cmd", "/k", "claude"],
                cwd=str(path),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        else:
            os.chdir(path)
            os.execlp("claude", "claude")
    except FileNotFoundError:
        print(
            "  Could not launch 'claude'. Make sure Claude Code is installed and on your PATH.",
            file=sys.stderr,
        )
