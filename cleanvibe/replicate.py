"""``cleanvibe replicate`` — scaffold a standalone paper-replication project.

Given an arXiv (or alphaxiv) link, fetch the paper metadata and lay down a
self-contained replication project: the cleanvibe conventions (CLAUDE.md,
queue.md, data_lake/) plus the replication-specific structure (SKILL.md,
download_paper.py, replication_target/, GitHub Actions deliverables). Then
git-init, make the initial commit, and launch Claude Code.

Absorbed from the now-sunset ``replication_skill`` project.
"""

import json
import platform
from pathlib import Path

from . import templates
from .arxiv import fetch_paper
from .scaffold import _git_init, _launch_claude, _write, _write_gitkeep


def _resolve_target(base: Path) -> Path:
    """Return a non-existing directory, auto-suffixing ``-2``, ``-3``, … .

    Replicate never errors on a name collision and never prompts: the user
    supplied no name (it is derived from the paper title), so a silent
    numbered suffix is the least surprising behaviour. This is deliberately
    asymmetric with ``cleanvibe new``, which prompts instead.
    """
    if not base.exists():
        return base
    n = 2
    while True:
        candidate = base.with_name(f"{base.name}-{n}")
        if not candidate.exists():
            return candidate
        n += 1


def _paper_json(paper) -> str:
    return json.dumps(
        {
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "authors": list(paper.authors),
            "published": paper.published,
            "pdf_url": paper.pdf_url,
            "summary": paper.summary,
        },
        indent=2,
        ensure_ascii=False,
    )


def replicate_project(arxiv, path=None, dry_run: bool = False, no_claude: bool = False) -> None:
    """Scaffold a standalone replication project for an arXiv/alphaxiv paper."""
    is_windows = platform.system() == "Windows"
    paper = fetch_paper(arxiv)

    base = Path(path) if path is not None else Path(f"replicating-{paper.slug}")
    target = _resolve_target(base)

    if dry_run:
        print(f"[dry-run] Paper: {paper.title} (arXiv:{paper.arxiv_id})")
        print(f"[dry-run] Would create directory: {target}")
        for rel in (
            "CLAUDE.md",
            "queue.md",
            "README.md",
            "SKILL.md",
            "paper.json",
            "download_paper.py",
            ".gitignore",
            "data_lake/.gitkeep",
            "replication_target/.gitkeep",
            ".github/workflows/pages.yml",
            ".github/workflows/package.yml",
        ):
            print(f"[dry-run] Would write: {target / rel}")
        if is_windows:
            print(f"[dry-run] Would write: {target / 'runclaude.bat'}")
        print(f"[dry-run] Would run: git init")
        print(f"[dry-run] Would run: git add . && git commit")
        if not no_claude:
            print(f"[dry-run] Would launch: claude")
        return

    target.mkdir(parents=True, exist_ok=True)
    print(f"Replicating: {paper.title} (arXiv:{paper.arxiv_id}) -> {target}")

    _write(target / "CLAUDE.md", templates.replication_claude_md(paper))
    _write(target / "queue.md", templates.replication_queue_md(paper))
    _write(target / "README.md", templates.replication_readme_md(paper))
    _write(target / "SKILL.md", templates.replication_skill_md(paper))
    _write(target / "download_paper.py", templates.replication_download_paper_py(paper))
    _write(target / ".gitignore", templates.REPLICATION_GITIGNORE)
    _write(target / "paper.json", _paper_json(paper))

    # The paper itself lives under replication_target/ (gitignored), NEVER in
    # data_lake/. data_lake/ still exists for other downloaded material.
    _write_gitkeep(target / "data_lake")
    _write_gitkeep(target / "replication_target")

    workflows = target / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    _write(workflows / "pages.yml", templates.REPLICATION_PAGES_YML)
    _write(workflows / "package.yml", templates.REPLICATION_PACKAGE_YML)

    if is_windows:
        _write(target / "runclaude.bat", templates.RUNCLAUDE_BAT)

    message = (
        f'Initial commit: replication scaffold for arXiv:{paper.arxiv_id}\n'
        f"\n"
        f'Replicating "{paper.title}"\n'
        f"Scaffolded by `cleanvibe replicate` "
        f"(https://github.com/Immanuelle/cleanvibe).\n"
        f"Paper -> replication_target/paper.pdf (run `python download_paper.py`).\n"
        f"Deliverables (GitHub Pages site + PDF report + ZIP package) build in "
        f"GitHub Actions."
    )
    _git_init(target, message=message)

    if not no_claude:
        _launch_claude(target)
