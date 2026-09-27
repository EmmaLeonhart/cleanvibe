"""Command-line interface for cleanvibe.

cleanvibe 2 usage:
    cleanvibe                   Open this directory's cleanvibe project as a new
                                session, or (if this directory is not one) create
                                an auto-named project here and open it
    cleanvibe new [NAME]        Create a project (auto-named without NAME) and open it
    cleanvibe replicate REF     Scaffold a replication project: clawRxiv ref, arXiv/alphaxiv ref,
                                a non-arXiv URL, or a drop-in folder
    cleanvibe doctor [PATH]     Read-only audit of a cleanvibe project for drift
    cleanvibe legacy CMD ...    The deprecated cleanvibe 1.x modes:
                                new, research, original, chat, clone, convert
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
from .chat import chat_project, default_chat_path
from .doctor import doctor
from .original import original_project
from .project import auto_project_path, is_cleanvibe_repo, new_project, open_project
from .research import research_project
from .scaffold import clone_project, convert_project, create_project

LEGACY_COMMANDS = ("new", "research", "original", "chat", "clone", "convert")
# 1.x top-level names that now live under `cleanvibe legacy` (`new` is v2 now).
MOVED_COMMANDS = ("research", "original", "chat", "clone", "convert")


def _ask(prompt: str) -> str:
    """Thin wrapper around input() so tests can monkeypatch the prompt seam."""
    return input(prompt)


def _confirm(question: str) -> bool:
    return _ask(f"{question} [y/N] ").strip().lower() in ("y", "yes")


def _looks_like_url(value: str) -> bool:
    """True for a plain http(s) URL (used to route non-arXiv research downloads)."""
    return value.strip().lower().startswith(("http://", "https://"))


def _suggest_name(path: Path) -> Path:
    """Suggest a free sibling name by appending -2, -3, … (never silently used).

    Unlike `replicate`, which auto-numbers because the user supplied no name,
    legacy `new` only ever *suggests* this — the user explicitly chose their
    name, so a silent rename would be surprising.
    """
    n = 2
    while True:
        candidate = path.with_name(f"{path.name}-{n}")
        if not candidate.exists():
            return candidate
        n += 1


# ---------------------------------------------------------------------------
# cleanvibe 2
# ---------------------------------------------------------------------------


def _do_default(args) -> None:
    """`cleanvibe` with no command: open the cwd if it is a cleanvibe project,
    otherwise create an auto-named project in the cwd and open that."""
    here = Path(".")
    if is_cleanvibe_repo(here):
        open_project(here, dry_run=args.dry_run, no_claude=args.no_claude)
        return
    new_project(auto_project_path(here), auto_named=True,
                dry_run=args.dry_run, no_claude=args.no_claude)


def _do_new(args) -> None:
    """`cleanvibe new [NAME]`."""
    if args.name is None:
        new_project(auto_project_path(), auto_named=True,
                    dry_run=args.dry_run, no_claude=args.no_claude)
        return
    path = args.name
    if path.exists() and not path.is_dir():
        print(f"Error: {path} exists and is not a directory.", file=sys.stderr)
        sys.exit(2)
    if path.is_dir() and is_cleanvibe_repo(path):
        print(f"{path} is already a cleanvibe project; opening it.")
        open_project(path, dry_run=args.dry_run, no_claude=args.no_claude)
        return
    if path.is_dir() and any(path.iterdir()):
        print(
            f"Error: {path} already exists and is not empty. Pick another name, "
            f"or adopt it in place with the 1.x `cleanvibe legacy convert {path}`.",
            file=sys.stderr,
        )
        sys.exit(2)
    new_project(path, auto_named=False, dry_run=args.dry_run, no_claude=args.no_claude)


def _do_replicate(args) -> None:
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


# ---------------------------------------------------------------------------
# cleanvibe 1.x, under `cleanvibe legacy` (deprecated)
# ---------------------------------------------------------------------------


def _deprecation_warning(command: str) -> None:
    print(
        f"DEPRECATED: `cleanvibe legacy {command}` runs the cleanvibe 1.x `{command}` "
        f"mode. It still works but is no longer developed. The default "
        f"`cleanvibe new` covers most of what it did: it starts as a conversation, "
        f"works out the purpose with you, and picks up development or research "
        f"practices as skills.",
        file=sys.stderr,
    )


def _do_research(args) -> None:
    """Handler shared by `legacy research PATH` and `legacy new PATH --research`.

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
    """Handler shared by `legacy original PATH` and `legacy new PATH --original`.

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


def _do_chat(args) -> None:
    """`legacy chat [PATH]`: the name is optional (defaults to chat-YYYY-MM-DD).

    With no name the user chose nothing, so a taken default is auto-suffixed,
    like `replicate`. A named but non-empty target gets a free sibling name,
    like `research`.
    """
    path = args.path if args.path is not None else default_chat_path()
    if path.exists() and any(path.iterdir()) and not args.dry_run:
        suggestion = _suggest_name(path)
        print(f"{path} already exists and is not empty; using {suggestion} instead.")
        path = suggestion
    chat_project(path, topic=args.topic, dry_run=args.dry_run, no_claude=args.no_claude)


def _do_legacy_new(args) -> None:
    if args.original:
        # `legacy new PATH --original` is an alias for `legacy original`.
        _do_original(args)
        return
    if args.research:
        # `legacy new PATH --research` is an alias for `legacy research`.
        _do_research(args)
        return
    if args.path.exists() and any(args.path.iterdir()):
        # Existing, non-empty directory: prompt instead of erroring.
        if args.dry_run:
            print(f"[dry-run] {args.path} exists and is not empty.")
            print(f"[dry-run] Would prompt: convert it in place (like "
                  f"`cleanvibe legacy convert`), or create under a different name.")
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


def _do_convert(args) -> None:
    if not args.path.exists():
        print(f"Error: {args.path} does not exist.", file=sys.stderr)
        sys.exit(1)
    if not args.path.is_dir():
        print(f"Error: {args.path} is not a directory.", file=sys.stderr)
        sys.exit(1)
    print(f"Converting existing directory: {args.path}")
    convert_project(args.path, dry_run=args.dry_run, no_claude=args.no_claude)


def _do_clone(args) -> None:
    if args.path is None:
        # Derive directory name from repo URL
        repo_name = args.repo.rstrip("/").rsplit("/", 1)[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        args.path = Path(repo_name)
    print(f"Cloning {args.repo} -> {args.path}")
    clone_project(args.repo, args.path, dry_run=args.dry_run, no_claude=args.no_claude)


_LEGACY_HANDLERS = {
    "new": _do_legacy_new,
    "research": _do_research,
    "original": _do_original,
    "chat": _do_chat,
    "clone": _do_clone,
    "convert": _do_convert,
}


def _add_run_flags(parser, verb: str = "created") -> None:
    parser.add_argument(
        "--dry-run", action="store_true",
        help=f"Show what would be {verb} without writing anything",
    )
    parser.add_argument(
        "--no-claude", action="store_true", help="Don't launch Claude Code afterwards"
    )


def _add_legacy_parsers(subparsers) -> None:
    # legacy new PATH
    new_parser = subparsers.add_parser(
        "new", help="1.x: a new project with the pre-seeded bootstrap queue"
    )
    new_parser.add_argument("path", type=Path, help="Directory to create")
    new_parser.add_argument(
        "--research", action="store_true",
        help="Scaffold an original-research project (same as `legacy research`)",
    )
    new_parser.add_argument(
        "--question", default=None,
        help="(research only) the research question, if you already know it",
    )
    new_parser.add_argument(
        "--original", action="store_true",
        help="Scaffold a research project with an UNCERTAIN topic (same as "
        "`legacy original`)",
    )
    new_parser.add_argument(
        "--area", default=None,
        help="(original only) a focus area / field to seed topic finding",
    )
    _add_run_flags(new_parser)

    # legacy research PATH
    research_parser = subparsers.add_parser(
        "research",
        help="1.x: literature-review-first research project with a GitHub Pages report",
    )
    research_parser.add_argument("path", type=Path, help="Directory to create")
    research_parser.add_argument(
        "--question", default=None,
        help="The research question, if you already know it",
    )
    _add_run_flags(research_parser)

    # legacy original PATH
    original_parser = subparsers.add_parser(
        "original",
        help="1.x: research with an uncertain topic (topic-finding loop first)",
    )
    original_parser.add_argument("path", type=Path, help="Directory to create")
    original_parser.add_argument(
        "--area", default=None,
        help="A focus area / field to seed topic finding",
    )
    _add_run_flags(original_parser)

    # legacy chat [PATH]
    chat_parser = subparsers.add_parser(
        "chat",
        help="1.18: a git-tracked conversation about one topic (the forerunner "
        "of the cleanvibe 2 default)",
    )
    chat_parser.add_argument(
        "path", nargs="?", type=Path, default=None,
        help="Directory to create (defaults to chat-YYYY-MM-DD, auto-suffixed)",
    )
    chat_parser.add_argument(
        "--topic", default=None, help="What the conversation is about",
    )
    _add_run_flags(chat_parser)

    # legacy clone REPO [PATH]
    clone_parser = subparsers.add_parser(
        "clone", help="1.x: clone a repo onto an onboarding branch with scaffolding"
    )
    clone_parser.add_argument("repo", help="Git repository URL to clone")
    clone_parser.add_argument(
        "path", nargs="?", type=Path, default=None, help="Target directory (defaults to repo name)"
    )
    _add_run_flags(clone_parser, "done")

    # legacy convert [PATH]
    convert_parser = subparsers.add_parser(
        "convert", help="1.x: inject missing scaffolding into an existing directory"
    )
    convert_parser.add_argument(
        "path", nargs="?", type=Path, default=Path("."),
        help="Directory to convert (defaults to current directory)"
    )
    _add_run_flags(convert_parser, "done")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cleanvibe",
        description="Start or reopen a Claude Code project that begins as a "
        "conversation. With no command: open this directory's cleanvibe project, "
        "or create an auto-named one here.",
    )
    parser.add_argument(
        "--version", action="version", version=f"cleanvibe {__version__}"
    )
    _add_run_flags(parser)

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    new_parser = subparsers.add_parser(
        "new", help="Create a project (auto-named without NAME) and open a session in it",
    )
    new_parser.add_argument(
        "name", nargs="?", type=Path, default=None,
        help="Directory to create. Omit it to get untitled-cleanvibe-project.",
    )
    _add_run_flags(new_parser)

    replicate_parser = subparsers.add_parser(
        "replicate",
        help="Scaffold a replication project — from a clawRxiv paper, an "
        "arXiv/alphaxiv paper, a URL, or a folder you drop the paper(s) into",
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
    _add_run_flags(replicate_parser)

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Read-only audit of a cleanvibe project for drift. Exits 1 if "
        "anything is found",
    )
    doctor_parser.add_argument(
        "path", nargs="?", type=Path, default=Path("."),
        help="Project to audit (defaults to the current directory)",
    )

    legacy_parser = subparsers.add_parser(
        "legacy",
        help="DEPRECATED: the cleanvibe 1.x modes (new, research, original, "
        "chat, clone, convert)",
    )
    legacy_sub = legacy_parser.add_subparsers(dest="legacy_command", metavar="CMD")
    legacy_sub.required = True
    _add_legacy_parsers(legacy_sub)

    for name in MOVED_COMMANDS:
        moved = subparsers.add_parser(name, add_help=False)
        moved.add_argument("rest", nargs=argparse.REMAINDER)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        _do_default(args)
    elif args.command == "new":
        _do_new(args)
    elif args.command == "replicate":
        _do_replicate(args)
    elif args.command == "doctor":
        sys.exit(doctor(args.path))
    elif args.command == "legacy":
        _deprecation_warning(args.legacy_command)
        _LEGACY_HANDLERS[args.legacy_command](args)
    elif args.command in MOVED_COMMANDS:
        print(
            f"`cleanvibe {args.command}` is a cleanvibe 1.x mode. In cleanvibe 2 "
            f"it is deprecated and runs as `cleanvibe legacy {args.command}`. The "
            f"default `cleanvibe new` now covers most of what it did.",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
