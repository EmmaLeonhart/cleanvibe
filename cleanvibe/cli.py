"""Command-line interface for cleanvibe.

Usage:
    cleanvibe new PATH          Create a new scaffolded project
    cleanvibe clone REPO [PATH] Clone a repo and inject scaffolding
    cleanvibe convert [PATH]    Convert an existing directory into a cleanvibe project
    cleanvibe replicate URL     Scaffold a replication project for an arXiv/alphaxiv paper
    cleanvibe --version         Show version

Zero dependencies. Just Python stdlib.
"""

from __future__ import annotations  # noqa: I001 - keep at top for 3.9 compat

import argparse
import sys
from pathlib import Path

from . import __version__
from .replicate import replicate_project
from .scaffold import clone_project, convert_project, create_project


def _ask(prompt: str) -> str:
    """Thin wrapper around input() so tests can monkeypatch the prompt seam."""
    return input(prompt)


def _confirm(question: str) -> bool:
    return _ask(f"{question} [y/N] ").strip().lower() in ("y", "yes")


def _suggest_name(path: Path) -> Path:
    """Suggest a free sibling name by appending -2, -3, … (never silently used).

    Unlike `replicate`, which auto-numbers because the user supplied no name,
    `new` only ever *suggests* this — the user explicitly chose their name, so
    a silent rename would be surprising.
    """
    n = 2
    while True:
        candidate = path.with_name(f"{path.name}-{n}")
        if not candidate.exists():
            return candidate
        n += 1


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

    # cleanvibe convert [PATH]
    convert_parser = subparsers.add_parser(
        "convert", help="Convert an existing directory into a cleanvibe project"
    )
    convert_parser.add_argument(
        "path", nargs="?", type=Path, default=Path("."),
        help="Directory to convert (defaults to current directory)"
    )
    convert_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without writing anything"
    )
    convert_parser.add_argument(
        "--no-claude", action="store_true", help="Skip launching Claude Code after converting"
    )

    # cleanvibe replicate URL [PATH]
    replicate_parser = subparsers.add_parser(
        "replicate",
        help="Scaffold a standalone replication project for an arXiv/alphaxiv paper",
    )
    replicate_parser.add_argument(
        "arxiv", help="arXiv or alphaxiv id / abs URL / pdf URL"
    )
    replicate_parser.add_argument(
        "path", nargs="?", type=Path, default=None,
        help="Target directory (defaults to replicating-<paper-slug>, "
        "auto-suffixed -2/-3 if it exists)",
    )
    replicate_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be created without writing anything"
    )
    replicate_parser.add_argument(
        "--no-claude", action="store_true", help="Skip launching Claude Code after scaffolding"
    )

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "new":
        if args.path.exists() and any(args.path.iterdir()):
            # Existing, non-empty directory: prompt instead of erroring.
            if args.dry_run:
                print(f"[dry-run] {args.path} exists and is not empty.")
                print(f"[dry-run] Would prompt: convert it in place (like "
                      f"`cleanvibe convert`), or create under a different name.")
                print(f"[dry-run] In-place (convert) preview:")
                convert_project(args.path, dry_run=True, no_claude=args.no_claude)
                return
            print(f"{args.path} already exists and is not empty.")
            if _confirm("Turn this existing directory into a git repo with "
                        "cleanvibe scaffolding and start work?"):
                print(f"Converting existing directory in place: {args.path}")
                convert_project(args.path, no_claude=args.no_claude)
                return
            # NO: offer a different name (suggest one; user may type their own).
            suggestion = _suggest_name(args.path)
            typed = _ask(
                f"Create under a different name instead? "
                f"[{suggestion}] (enter a name, or blank to accept): "
            ).strip()
            target = Path(typed) if typed else suggestion
            if target.exists() and any(target.iterdir()):
                fallback = _suggest_name(target)
                print(f"{target} is also non-empty; using {fallback} instead.")
                target = fallback
            print(f"Creating project: {target}")
            create_project(target, dry_run=args.dry_run, no_claude=args.no_claude)
            return
        print(f"Creating project: {args.path}")
        create_project(args.path, dry_run=args.dry_run, no_claude=args.no_claude)

    elif args.command == "convert":
        if not args.path.exists():
            print(f"Error: {args.path} does not exist.", file=sys.stderr)
            sys.exit(1)
        if not args.path.is_dir():
            print(f"Error: {args.path} is not a directory.", file=sys.stderr)
            sys.exit(1)
        print(f"Converting existing directory: {args.path}")
        convert_project(args.path, dry_run=args.dry_run, no_claude=args.no_claude)

    elif args.command == "clone":
        if args.path is None:
            # Derive directory name from repo URL
            repo_name = args.repo.rstrip("/").rsplit("/", 1)[-1]
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]
            args.path = Path(repo_name)
        print(f"Cloning {args.repo} -> {args.path}")
        clone_project(args.repo, args.path, dry_run=args.dry_run, no_claude=args.no_claude)

    elif args.command == "replicate":
        print(f"Scaffolding replication project for: {args.arxiv}")
        replicate_project(
            args.arxiv, args.path, dry_run=args.dry_run, no_claude=args.no_claude
        )


if __name__ == "__main__":
    main()
