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
import subprocess
from pathlib import Path

from . import __version__, templates
from .arxiv import fetch_paper
from .scaffold import (
    _git_init,
    _launch_claude,
    _write,
    _write_gitkeep,
    _write_if_missing,
)


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
            "devlog.md",
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
    _write(target / "devlog.md", templates.devlog_md(f"replicating-{paper.slug}"))
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


def replicate_manual_project(folder, dry_run: bool = False, no_claude: bool = False) -> None:
    """Scaffold a replication project for a paper the user supplies by hand.

    Used when the ``cleanvibe replicate`` argument is a folder name rather
    than an arXiv/alphaxiv reference: no metadata fetch, no
    ``download_paper.py``, no ``paper.json``, no network. The user drops the
    paper PDF(s) into ``replication_target/`` and supporting material into
    ``data_lake/``; the scaffold's opening instructions say so up front.

    Injection is **non-destructive** (the folder may already exist with the
    user's dropped-in paper): scaffold files are written only if missing, and
    the dropped paper itself is left untouched (and stays gitignored).
    """
    is_windows = platform.system() == "Windows"
    target = Path(folder)
    name = target.name or "replication"
    is_git_repo = (target / ".git").is_dir()

    files = (
        "CLAUDE.md",
        "queue.md",
        "devlog.md",
        "README.md",
        "SKILL.md",
        ".gitignore",
        "data_lake/.gitkeep",
        "replication_target/.gitkeep",
        ".github/workflows/pages.yml",
        ".github/workflows/package.yml",
    )

    if dry_run:
        print(f"[dry-run] Manual (drop-in) replication - no arXiv fetch")
        print(f"[dry-run] Target directory: {target}"
              f"{' (exists)' if target.exists() else ''}")
        for rel in files:
            print(f"[dry-run] Would write if missing: {target / rel}")
        if is_windows:
            print(f"[dry-run] Would write if missing: {target / 'runclaude.bat'}")
        print(f"[dry-run] NO download_paper.py / paper.json (manual mode)")
        if is_git_repo:
            print(f"[dry-run] Existing git repo: would commit injected scaffold")
        else:
            print(f"[dry-run] Would run: git init && git add . && git commit")
        if not no_claude:
            print(f"[dry-run] Would launch: claude")
        print(f"[dry-run] Drop the paper PDF(s) into "
              f"{target / 'replication_target'} before working the queue.")
        return

    target.mkdir(parents=True, exist_ok=True)
    print(f"Manual replication scaffold (drop the paper in yourself) -> {target}")

    _write_if_missing(target / "CLAUDE.md", templates.replication_manual_claude_md(name))
    _write_if_missing(target / "queue.md", templates.replication_manual_queue_md(name))
    _write_if_missing(target / "devlog.md", templates.devlog_md(name))
    _write_if_missing(target / "README.md", templates.replication_manual_readme_md(name))
    _write_if_missing(target / "SKILL.md", templates.replication_manual_skill_md(name))
    _write_if_missing(target / ".gitignore", templates.REPLICATION_GITIGNORE)

    # The paper goes here (gitignored); data_lake/ is for other material.
    _write_gitkeep(target / "data_lake")
    _write_gitkeep(target / "replication_target")

    _write_if_missing(
        target / ".github" / "workflows" / "pages.yml", templates.REPLICATION_PAGES_YML
    )
    _write_if_missing(
        target / ".github" / "workflows" / "package.yml",
        templates.REPLICATION_PACKAGE_YML,
    )

    if is_windows:
        _write_if_missing(target / "runclaude.bat", templates.RUNCLAUDE_BAT)

    message = (
        f"Add cleanvibe manual replication scaffold (cleanvibe v{__version__})\n"
        f"\n"
        f"`cleanvibe replicate {folder}` — manual drop-in mode (no arXiv "
        f"fetch). Drop the paper PDF(s) into replication_target/ and "
        f"supporting material into data_lake/, then work queue.md.\n"
        f"Scaffolded by cleanvibe (https://github.com/Immanuelle/cleanvibe)."
    )
    if is_git_repo:
        subprocess.run(["git", "add", "-A"], cwd=target, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], cwd=target, capture_output=True)
        print(f"  Committed scaffold into existing git repo")
    else:
        _git_init(target, message=message)

    print(
        f"  Next: drop the paper PDF(s) into {target / 'replication_target'} "
        f"(and other material into {target / 'data_lake'}), then work queue.md."
    )

    if not no_claude:
        _launch_claude(target)
