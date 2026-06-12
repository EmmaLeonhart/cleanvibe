"""Command-line interface for cleanvibe.

Usage:
    cleanvibe new PATH          Create a new scaffolded project
    cleanvibe research PATH     Create an original-research project (literature-review-first + published report)
    cleanvibe original PATH     Create an original-research project with an uncertain topic (adds a topic-finding loop)
    cleanvibe clone REPO [PATH] Clone a repo and inject scaffolding
    cleanvibe convert [PATH]    Convert an existing directory into a cleanvibe project
    cleanvibe replicate REF     Scaffold a replication project: clawRxiv ref, arXiv/alphaxiv ref, a non-arXiv URL, or a drop-in folder
    cleanvibe --version         Show version

Zero dependencies. Just Python stdlib.
"""

from __future__ import annotations  # noqa: I001 - keep at top for 3.9 compat

import argparse
import sys
from pathlib import Path

from . import __version__
from .arxiv import is_arxiv_ref
from .clawrxiv import is_clawrxiv_ref
from .replicate import (
    replicate_clawrxiv_project,
    replicate_manual_project,
    replicate_project,
    replicate_url_project,
)
from .original import original_project
from .research import research_project
from .scaffold import clone_project, convert_project, create_project


def _ask(prompt: str) -> str:
    """Thin wrapper around input() so tests can monkeypatch the prompt seam."""
    return input(prompt)


def _confirm(question: str) -> bool:
    return _ask(f"{question} [y/N] ").strip().lower() in ("y", "yes")


def _looks_like_url(value: str) -> bool:
    """True for a plain http(s) URL (used to route non-arXiv research downloads)."""
    return value.strip().lower().startswith(("http://", "https://"))


def _do_research(args) -> None:
    """Handler shared by `cleanvibe research PATH` and `cleanvibe new PATH --research`.

    Research projects are fresh (like `new`), not in-place conversions — so on a
    non-empty target we just create under a free sibling name rather than
    offering to convert.
    """
    path = args.path
    question = getattr(args, "question", None)
    if path.exists() and any(path.iterdir()) and not args.dry_run:
        suggestion = _suggest_name(path)
        print(f"{path} already exists and is not empty; using {suggestion} instead.")
        path = suggestion
    research_project(
        path, question=question, dry_run=args.dry_run, no_claude=args.no_claude
    )


def _do_original(args) -> None:
    """Handler shared by `cleanvibe original PATH` and `cleanvibe new PATH --original`.

    Like research, original projects are fresh (not in-place conversions) — so on
    a non-empty target we create under a free sibling name rather than converting.
    The seed is an `area` (a field to explore), not a `question`: the question is
    what the topic-finding loop discovers.
    """
    path = args.path
    area = getattr(args, "area", None)
    if path.exists() and any(path.iterdir()) and not args.dry_run:
        suggestion = _suggest_name(path)
        print(f"{path} already exists and is not empty; using {suggestion} instead.")
        path = suggestion
    original_project(
        path, area=area, dry_run=args.dry_run, no_claude=args.no_claude
    )


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
        "--research", action="store_true",
        help="Scaffold an original-research project (same as `cleanvibe research`): "
        "literature-review-first bootstrap + a published, themed report",
    )
    new_parser.add_argument(
        "--question", default=None,
        help="(research only) the research question, if you already know it",
    )
    new_parser.add_argument(
        "--original", action="store_true",
        help="Scaffold an original-research project with an UNCERTAIN topic "
        "(same as `cleanvibe original`): adds a topic-finding loop before the "
        "literature review",
    )
    new_parser.add_argument(
        "--area", default=None,
        help="(original only) a focus area / field to seed topic finding, if you "
        "have a rough direction",
    )
    new_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be created without writing anything"
    )
    new_parser.add_argument(
        "--no-claude", action="store_true", help="Skip launching Claude Code after scaffolding"
    )

    # cleanvibe research PATH
    research_parser = subparsers.add_parser(
        "research",
        help="Create an original-research project: literature-review-first "
        "bootstrap (agentic RAG) and a published, themed GitHub Pages report",
    )
    research_parser.add_argument("path", type=Path, help="Directory to create")
    research_parser.add_argument(
        "--question", default=None,
        help="The research question, if you already know it (otherwise the "
        "bootstrap queue pins it down with you)",
    )
    research_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be created without writing anything"
    )
    research_parser.add_argument(
        "--no-claude", action="store_true", help="Skip launching Claude Code after scaffolding"
    )

    # cleanvibe original PATH
    original_parser = subparsers.add_parser(
        "original",
        help="Create an original-research project with an UNCERTAIN topic: like "
        "`research` but adds a topic-finding loop that discovers and selects the "
        "research question before the literature review",
    )
    original_parser.add_argument("path", type=Path, help="Directory to create")
    original_parser.add_argument(
        "--area", default=None,
        help="A focus area / field to seed topic finding, if you have a rough "
        "direction (otherwise the bootstrap loop explores broadly with you)",
    )
    original_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be created without writing anything"
    )
    original_parser.add_argument(
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

    # cleanvibe replicate (URL | FOLDER) [PATH]
    replicate_parser = subparsers.add_parser(
        "replicate",
        help="Scaffold a replication project — from a clawRxiv paper, an "
        "arXiv/alphaxiv paper, or a folder you drop the paper(s) into yourself",
    )
    replicate_parser.add_argument(
        "target",
        help="A clawRxiv ref (clawrxiv.io/abs/<id> or clawrxiv:<id> — fetches "
        "content + skill recipe), an arXiv/alphaxiv id or URL (fetches "
        "metadata), a plain http(s) URL to non-arXiv research (downloads the "
        "page/PDF as the source), OR a folder name (manual drop-in mode: you "
        "put the paper PDF(s) into replication_target/ and material into "
        "data_lake/ yourself)",
    )
    replicate_parser.add_argument(
        "path", nargs="?", type=Path, default=None,
        help="arXiv mode only: target directory (defaults to "
        "replicating-<paper-slug>, auto-suffixed -2/-3 if it exists). "
        "Ignored in folder mode — there the target IS the folder.",
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

    if args.command == "research":
        _do_research(args)
        return

    if args.command == "original":
        _do_original(args)
        return

    if args.command == "new":
        if args.original:
            # `cleanvibe new PATH --original` is an alias for `cleanvibe original`.
            _do_original(args)
            return
        if args.research:
            # `cleanvibe new PATH --research` is an alias for `cleanvibe research`.
            _do_research(args)
            return
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
        if is_clawrxiv_ref(args.target):
            # Checked before arXiv so clawrxiv.io links / clawrxiv:<id> route to
            # the dedicated clawRxiv mode (the API ships a skill recipe).
            print(f"Scaffolding clawRxiv replication project for: {args.target}")
            replicate_clawrxiv_project(
                args.target, args.path, dry_run=args.dry_run, no_claude=args.no_claude
            )
        elif is_arxiv_ref(args.target):
            print(f"Scaffolding replication project for: {args.target}")
            replicate_project(
                args.target, args.path, dry_run=args.dry_run, no_claude=args.no_claude
            )
        elif _looks_like_url(args.target):
            # A plain http(s) URL that isn't arXiv/clawRxiv -> the research is
            # hosted elsewhere; download the page/PDF as the replication source.
            print(f"Scaffolding replication project from non-arXiv URL: {args.target}")
            replicate_url_project(
                args.target, args.path, dry_run=args.dry_run, no_claude=args.no_claude
            )
        else:
            # Not a paper ref or URL -> treat it as a folder name and
            # scaffold a manual drop-in replication project there.
            if args.path is not None:
                print(
                    f"Note: '{args.path}' ignored — in folder mode the target "
                    f"folder is '{args.target}'.",
                    file=sys.stderr,
                )
            print(f"Scaffolding manual (drop-in) replication project: {args.target}")
            replicate_manual_project(
                args.target, dry_run=args.dry_run, no_claude=args.no_claude
            )


if __name__ == "__main__":
    main()
