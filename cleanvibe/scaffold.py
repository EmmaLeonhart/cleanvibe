"""Core scaffolding logic for cleanvibe.

Creates project directories, writes template files, initializes git,
and launches Claude Code.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

from . import templates


def create_project(path: Path, dry_run: bool = False, no_claude: bool = False) -> None:
    """Create a new project directory with opinionated scaffolding."""
    project_name = path.name

    if dry_run:
        print(f"[dry-run] Would create directory: {path}")
        print(f"[dry-run] Would write: {path / 'CLAUDE.md'}")
        print(f"[dry-run] Would write: {path / 'README.md'}")
        print(f"[dry-run] Would write: {path / '.gitignore'}")
        print(f"[dry-run] Would run: git init")
        print(f"[dry-run] Would run: git add . && git commit")
        if not no_claude:
            print(f"[dry-run] Would launch: claude")
        return

    path.mkdir(parents=True, exist_ok=True)

    _write(path / "CLAUDE.md", templates.claude_md(project_name))
    _write(path / "README.md", templates.readme_md(project_name))
    _write(path / ".gitignore", templates.GITIGNORE)

    _git_init(path)

    if not no_claude:
        _launch_claude(path)


def clone_project(repo: str, path: Path, dry_run: bool = False, no_claude: bool = False) -> None:
    """Clone a repo and inject scaffolding if missing."""
    if dry_run:
        print(f"[dry-run] Would run: git clone {repo} {path}")
        print(f"[dry-run] Would check for missing CLAUDE.md / README.md / .gitignore")
        print(f"[dry-run] Would inject any missing files")
        if not no_claude:
            print(f"[dry-run] Would launch: claude")
        return

    result = subprocess.run(["git", "clone", repo, str(path)])
    if result.returncode != 0:
        print(f"Error: git clone failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(1)

    project_name = path.name

    # Only inject files that are missing - don't overwrite existing ones
    claude_md = path / "CLAUDE.md"
    if not claude_md.exists():
        _write(claude_md, templates.claude_md(project_name))
        print(f"  Injected CLAUDE.md (was missing)")

    readme = path / "README.md"
    if not readme.exists():
        _write(readme, templates.readme_md(project_name))
        print(f"  Injected README.md (was missing)")

    gitignore = path / ".gitignore"
    if not gitignore.exists():
        _write(gitignore, templates.GITIGNORE)
        print(f"  Injected .gitignore (was missing)")

    if not no_claude:
        _launch_claude(path)


def _write(filepath: Path, content: str) -> None:
    filepath.write_text(content, encoding="utf-8")
    print(f"  Created {filepath.name}")


def _git_init(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit: cleanvibe scaffold"],
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
            subprocess.Popen(
                ["cmd", "/k", f'cd /d "{path}" && claude'],
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
