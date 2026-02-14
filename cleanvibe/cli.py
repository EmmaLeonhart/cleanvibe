"""Command-line interface for cleanvibe.

Usage:
    cleanvibe new PATH          Create a new scaffolded project
    cleanvibe clone REPO [PATH] Clone a repo and inject scaffolding
    cleanvibe --version         Show version

Zero dependencies. Just Python stdlib.
"""

import argparse
import sys
from pathlib import Path

from . import __version__
from .scaffold import clone_project, create_project


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="cleanvibe",
        description="Scaffold AI-assisted coding projects and launch Claude Code.",
    )
    parser.add_argument(
        "--version", action="version", version=f"cleanvibe {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command")

    # cleanvibe new PATH
    new_parser = subparsers.add_parser(
        "new", help="Create a new project with opinionated scaffolding"
    )
    new_parser.add_argument("path", type=Path, help="Directory to create")
    new_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be created without writing anything"
    )
    new_parser.add_argument(
        "--no-claude", action="store_true", help="Skip launching Claude Code after scaffolding"
    )

    # cleanvibe clone REPO [PATH]
    clone_parser = subparsers.add_parser(
        "clone", help="Clone a repo and inject missing scaffolding"
    )
    clone_parser.add_argument("repo", help="Git repository URL to clone")
    clone_parser.add_argument(
        "path", nargs="?", type=Path, default=None, help="Target directory (defaults to repo name)"
    )
    clone_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without writing anything"
    )
    clone_parser.add_argument(
        "--no-claude", action="store_true", help="Skip launching Claude Code after cloning"
    )

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "new":
        if args.path.exists() and any(args.path.iterdir()):
            print(f"Error: {args.path} already exists and is not empty.", file=sys.stderr)
            sys.exit(1)
        print(f"Creating project: {args.path}")
        create_project(args.path, dry_run=args.dry_run, no_claude=args.no_claude)

    elif args.command == "clone":
        if args.path is None:
            # Derive directory name from repo URL
            repo_name = args.repo.rstrip("/").rsplit("/", 1)[-1]
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]
            args.path = Path(repo_name)
        print(f"Cloning {args.repo} -> {args.path}")
        clone_project(args.repo, args.path, dry_run=args.dry_run, no_claude=args.no_claude)


if __name__ == "__main__":
    main()
