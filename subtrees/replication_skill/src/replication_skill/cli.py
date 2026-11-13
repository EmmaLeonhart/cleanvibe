"""``replicate`` CLI entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from replication_skill.arxiv import fetch_paper
from replication_skill.scaffold import scaffold_replication


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="replicate",
        description="Scaffold a replication directory for an arXiv paper.",
    )
    parser.add_argument("arxiv", help="arXiv id, abs URL, or pdf URL")
    parser.add_argument(
        "--dest",
        default="replications",
        help="directory under which the replication folder is created (default: replications/)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace an existing replication directory",
    )
    args = parser.parse_args(argv)

    paper = fetch_paper(args.arxiv)
    target = scaffold_replication(paper, Path(args.dest), overwrite=args.overwrite)
    print(f"scaffolded {paper.arxiv_id} -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
