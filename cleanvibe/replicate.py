"""``cleanvibe replicate`` — scaffold a standalone paper-replication project.

Three modes, dispatched on the positional argument:

* **clawRxiv** (``clawrxiv.io/abs/<id>`` or ``clawrxiv:<id>``):
  ``replicate_clawrxiv_project`` fetches the content + abstract + skill recipe
  from the clawRxiv JSON API and writes a skill-first scaffold.
* **arXiv/alphaxiv** (any arXiv ref): ``replicate_project`` fetches metadata and
  writes a source-first, recipe-first scaffold with ``download_paper.py``.
* **manual drop-in** (a folder name): ``replicate_manual_project`` — no fetch;
  the user supplies the paper by hand.

Each lays down the cleanvibe conventions (CLAUDE.md, queue.md, devlog.md,
data_lake/) plus the replication-specific structure (SKILL.md,
replication_target/, GitHub Actions deliverables), then git-inits, makes the
initial commit, and launches Claude Code.

Absorbed from the now-sunset ``replication_skill`` project.
"""

import json
import platform
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from . import __version__, templates
from .arxiv import _read_url, _slugify, fetch_paper
from .clawrxiv import fetch_clawrxiv_paper
from .scaffold import (
    _git_init,
    _launch_claude,
    _write,
    _write_gitkeep,
    _write_if_missing,
)


def _run_extraction_commit(target: Path) -> None:
    """Commit 2 of the arXiv scaffold: download + extract the source, commit it.

    This runs the just-written ``download_paper.py`` (which fetches the arXiv
    e-print source, extracts it to ``replication_target/source/``, and saves the
    PDF) and makes a second commit, **before Claude is launched** — so the agent
    opens onto an already-extracted, already-committed paper source.

    This is *data download + archive extraction by cleanvibe's own stdlib code*,
    NOT execution of third-party code, so it needs no user consent. It is
    best-effort: if the network is unavailable (or arXiv is down), it warns and
    leaves ``download_paper.py`` for the agent to run later (the queue says so).
    """
    dl = target / "download_paper.py"
    if not dl.exists():
        return
    print("  Extracting arXiv source (download_paper.py) for commit 2 ...")
    try:
        result = subprocess.run(
            [sys.executable, "download_paper.py"],
            cwd=target,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except Exception as e:  # network/timeout/python issues — non-fatal
        print(f"  extraction skipped ({e}); the agent will run download_paper.py")
        return
    if result.returncode != 0:
        print("  extraction did not complete; the agent will run download_paper.py")
        return
    subprocess.run(["git", "add", "-A"], cwd=target, capture_output=True)
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=target, capture_output=True, text=True
    )
    if not status.stdout.strip():
        return  # nothing new to commit (e.g. PDF-only, already gitignored)
    subprocess.run(
        [
            "git",
            "commit",
            "-q",
            "-m",
            "Extract arXiv source (download_paper.py)\n\n"
            "Commit 2 of the cleanvibe replicate scaffold: the e-print source is "
            "downloaded and extracted to replication_target/source/ (committed); "
            "the raw archive and PDF are gitignored. Data download + extraction "
            "only — running the authors' recipe/code is gated on user consent "
            "(see queue.md step 1).",
        ],
        cwd=target,
        capture_output=True,
    )
    print("  Committed extracted source (commit 2)")


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


def _slug_from_url(url: str) -> str:
    """Derive a directory slug from a non-arXiv source URL.

    Uses the last path segment (minus a doc extension), falling back to the
    host. ``https://lab.org/papers/cool-thing.pdf`` -> ``cool-thing``;
    ``https://example.com/`` -> ``example-com``.
    """
    parsed = urllib.parse.urlparse(url)
    base = parsed.path.rstrip("/").rsplit("/", 1)[-1]
    base = re.sub(r"\.(pdf|html?|tex|aspx?|php)$", "", base, flags=re.IGNORECASE)
    return _slugify(base or parsed.netloc.replace("www.", ""))


def _download_source(url: str, dest_dir: Path):
    """Download ``url`` into ``dest_dir`` as paper.pdf/paper.html (sniffed).

    Best-effort and 429-aware (reuses arXiv's ``_read_url`` retry/backoff).
    Returns the saved filename, or ``None`` if the download failed — the
    scaffold still commits and the queue tells the agent to flag the failure.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Downloading source: {url}")
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": f"cleanvibe-replicate/{__version__}"}
        )
        data = _read_url(req, timeout=60)
    except Exception as e:  # network/HTTP/timeout — non-fatal
        print(f"  download failed ({e}); queue.md step 1 says to flag this")
        return None
    path_part = urllib.parse.urlparse(url).path.lower()
    is_pdf = path_part.endswith(".pdf") or data[:5] == b"%PDF-"
    fname = "paper.pdf" if is_pdf else "paper.html"
    (dest_dir / fname).write_bytes(data)
    print(f"  wrote replication_target/source/{fname} ({len(data)} bytes)")
    return fname


def _paper_json(paper) -> str:
    return json.dumps(
        {
            "arxiv_id": paper.arxiv_id,
            "version": paper.version,
            "id_with_version": paper.id_with_version,
            "title": paper.title,
            "authors": list(paper.authors),
            "published": paper.published,
            "pdf_url": paper.pdf_url,
            "summary": paper.summary,
        },
        indent=2,
        ensure_ascii=False,
    )


def _clawrxiv_paper_json(paper) -> str:
    return json.dumps(
        {
            "source": "clawrxiv",
            "paper_id": paper.paper_id,
            "title": paper.title,
            "authors": list(paper.authors),
            "claw_name": paper.claw_name,
            "version": paper.version,
            "category": paper.category,
            "created_at": paper.created_at,
            "abstract": paper.abstract,
            "abs_url": paper.abs_url,
            "api_url": paper.api_url,
            "has_skill_file": paper.has_skill_file,
        },
        indent=2,
        ensure_ascii=False,
    )


def replicate_project(
    arxiv, path=None, dry_run: bool = False, no_claude: bool = False,
    extract: bool = True,
) -> None:
    """Scaffold a standalone replication project for an arXiv/alphaxiv paper.

    After the framework commit (commit 1), unless ``extract=False``, the source
    is downloaded + extracted and committed (commit 2) *before* Claude launches,
    so the agent opens onto an already-extracted paper. ``extract=False`` keeps
    the unit tests network-free.
    """
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
            print(f"[dry-run] Would write: {target / '!runClaude.bat'}")
        print(f"[dry-run] Would run: git init")
        print(f"[dry-run] Would run: git add . && git commit  (commit 1: framework)")
        if extract:
            print(f"[dry-run] Would run: python download_paper.py + git commit  "
                  f"(commit 2: extracted source)")
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
        _write(target / "!runClaude.bat", templates.RUNCLAUDE_BAT)

    message = (
        f'Initial commit: replication scaffold for arXiv:{paper.arxiv_id}\n'
        f"\n"
        f'Replicating "{paper.title}"\n'
        f"Scaffolded by `cleanvibe replicate` "
        f"(https://github.com/Immanuelle/cleanvibe).\n"
        f"Paper source -> replication_target/source/ (commit 2 extracts it).\n"
        f"Deliverables (GitHub Pages site + PDF report + ZIP package) build in "
        f"GitHub Actions."
    )
    _git_init(target, message=message)

    # Commit 2 (before launch): download + extract the source so the agent opens
    # onto an already-extracted, already-committed paper. Best-effort; data
    # download only — running the authors' code stays gated on user consent.
    if extract:
        _run_extraction_commit(target)

    if not no_claude:
        _launch_claude(target)


def replicate_clawrxiv_project(
    ref, path=None, dry_run: bool = False, no_claude: bool = False
) -> None:
    """Scaffold a replication project for a clawRxiv paper.

    clawRxiv (clawrxiv.io) publishes AI-authored papers and serves each as
    three differentiated parts (content / abstract / skill recipe) via its JSON
    API. Unlike arXiv mode there is no ``download_paper.py``: the API returns
    everything in one call, so the paper **content** is written straight to
    ``replication_target/source/paper.md`` and the **skill recipe** (when
    clawRxiv ships one separately) to ``replication_skill.md`` at scaffold time.
    The queue is skill-first.
    """
    is_windows = platform.system() == "Windows"
    paper = fetch_clawrxiv_paper(ref)

    base = Path(path) if path is not None else Path(f"replicating-{paper.slug}")
    target = _resolve_target(base)

    if dry_run:
        print(f"[dry-run] clawRxiv paper: {paper.title} (clawrxiv:{paper.paper_id})")
        print(f"[dry-run] Would create directory: {target}")
        for rel in (
            "CLAUDE.md",
            "queue.md",
            "devlog.md",
            "README.md",
            "SKILL.md",
            "paper.json",
            ".gitignore",
            "replication_target/source/paper.md",
            "data_lake/.gitkeep",
            "replication_target/.gitkeep",
            ".github/workflows/pages.yml",
            ".github/workflows/package.yml",
        ):
            print(f"[dry-run] Would write: {target / rel}")
        if paper.has_skill_file:
            print(f"[dry-run] Would write: {target / 'replication_skill.md'} "
                  f"(clawRxiv skillMd)")
        else:
            print(f"[dry-run] No separate skillMd — recipe is embedded in "
                  f"paper.md (agent extracts it)")
        if is_windows:
            print(f"[dry-run] Would write: {target / '!runClaude.bat'}")
        print(f"[dry-run] NO download_paper.py (content fetched via API)")
        print(f"[dry-run] Would run: git init")
        print(f"[dry-run] Would run: git add . && git commit")
        if not no_claude:
            print(f"[dry-run] Would launch: claude")
        return

    target.mkdir(parents=True, exist_ok=True)
    print(f"Replicating (clawRxiv): {paper.title} (clawrxiv:{paper.paper_id}) -> {target}")

    _write(target / "CLAUDE.md", templates.clawrxiv_claude_md(paper))
    _write(target / "queue.md", templates.clawrxiv_queue_md(paper))
    _write(target / "devlog.md", templates.devlog_md(f"replicating-{paper.slug}"))
    _write(target / "README.md", templates.clawrxiv_readme_md(paper))
    _write(target / "SKILL.md", templates.clawrxiv_skill_md(paper))
    _write(target / ".gitignore", templates.REPLICATION_GITIGNORE)
    _write(target / "paper.json", _clawrxiv_paper_json(paper))

    # The clawRxiv content is the paper text: write it to source/ (committed),
    # mirroring the extracted-arXiv-source convention. The paper is NOT in
    # data_lake/.
    source = target / "replication_target" / "source"
    source.mkdir(parents=True, exist_ok=True)
    _write(source / "paper.md", paper.content)

    # The skill recipe — only when clawRxiv shipped one as a separate field.
    # Otherwise it is embedded in paper.md and the queue tells the agent to
    # extract it.
    if paper.has_skill_file:
        _write(target / "replication_skill.md", paper.skill_md)

    _write_gitkeep(target / "data_lake")
    _write_gitkeep(target / "replication_target")

    workflows = target / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    _write(workflows / "pages.yml", templates.REPLICATION_PAGES_YML)
    _write(workflows / "package.yml", templates.REPLICATION_PACKAGE_YML)

    if is_windows:
        _write(target / "!runClaude.bat", templates.RUNCLAUDE_BAT)

    skill_note = (
        "replication_skill.md (clawRxiv skill recipe)"
        if paper.has_skill_file
        else "skill recipe embedded in paper.md (extract it first)"
    )
    message = (
        f"Initial commit: clawRxiv replication scaffold for clawrxiv:{paper.paper_id}\n"
        f"\n"
        f'Replicating "{paper.title}"\n'
        f"Scaffolded by `cleanvibe replicate` "
        f"(https://github.com/Immanuelle/cleanvibe).\n"
        f"Paper content -> replication_target/source/paper.md; {skill_note}.\n"
        f"Skill-first: run the recipe, then verify against the paper.\n"
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
            print(f"[dry-run] Would write if missing: {target / '!runClaude.bat'}")
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
        _write_if_missing(target / "!runClaude.bat", templates.RUNCLAUDE_BAT)

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


def replicate_url_project(
    url, path=None, dry_run: bool = False, no_claude: bool = False
) -> None:
    """Scaffold a replication project for research that's NOT on arXiv/clawRxiv.

    The positional argument is a plain http(s) URL (a web page or a PDF). The
    source is **downloaded** into ``replication_target/source/`` (``paper.pdf``
    or ``paper.html``, sniffed), provenance is recorded in ``source.json``, and
    the project is scaffolded from the manual templates *parametrized with the
    source URL* — so the wording reflects that the source is already present
    (no "drop it in / stop and ask"). No ``download_paper.py`` / arXiv
    ``paper.json``; everything is committed in one commit.
    """
    is_windows = platform.system() == "Windows"
    slug = _slug_from_url(url)
    base = Path(path) if path is not None else Path(f"replicating-{slug}")
    target = _resolve_target(base)

    if dry_run:
        print(f"[dry-run] Non-arXiv URL replication: {url}")
        print(f"[dry-run] Would create directory: {target}")
        print(
            f"[dry-run] Would download {url} -> "
            f"{target / 'replication_target' / 'source' / 'paper.(pdf|html)'}"
        )
        for rel in (
            "CLAUDE.md",
            "queue.md",
            "devlog.md",
            "README.md",
            "SKILL.md",
            "source.json",
            ".gitignore",
            "data_lake/.gitkeep",
            "replication_target/.gitkeep",
            ".github/workflows/pages.yml",
            ".github/workflows/package.yml",
        ):
            print(f"[dry-run] Would write: {target / rel}")
        if is_windows:
            print(f"[dry-run] Would write: {target / '!runClaude.bat'}")
        print(f"[dry-run] NO download_paper.py / arXiv paper.json (URL mode)")
        print(f"[dry-run] Would run: git init && git add . && git commit")
        if not no_claude:
            print(f"[dry-run] Would launch: claude")
        return

    target.mkdir(parents=True, exist_ok=True)
    name = target.name
    print(f"Replicating from URL (not arXiv/clawRxiv): {url} -> {target}")

    _write(target / "CLAUDE.md", templates.replication_manual_claude_md(name, source_url=url))
    _write(target / "queue.md", templates.replication_manual_queue_md(name, source_url=url))
    _write(target / "devlog.md", templates.devlog_md(name))
    _write(target / "README.md", templates.replication_manual_readme_md(name, source_url=url))
    _write(target / "SKILL.md", templates.replication_manual_skill_md(name, source_url=url))
    _write(target / ".gitignore", templates.REPLICATION_GITIGNORE)

    _write_gitkeep(target / "data_lake")
    _write_gitkeep(target / "replication_target")

    workflows = target / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    _write(workflows / "pages.yml", templates.REPLICATION_PAGES_YML)
    _write(workflows / "package.yml", templates.REPLICATION_PACKAGE_YML)

    if is_windows:
        _write(target / "!runClaude.bat", templates.RUNCLAUDE_BAT)

    # Download the source (best-effort, retry/backoff) and record provenance.
    saved = _download_source(url, target / "replication_target" / "source")
    _write(
        target / "source.json",
        json.dumps(
            {"source": "url", "source_url": url, "saved_as": saved},
            indent=2,
            ensure_ascii=False,
        ),
    )

    message = (
        f"Initial commit: URL replication scaffold for {url}\n"
        f"\n"
        f"Non-arXiv source downloaded to "
        f"replication_target/source/{saved or '(download failed)'} "
        f"(provenance in source.json).\n"
        f"Scaffolded by `cleanvibe replicate` "
        f"(https://github.com/Immanuelle/cleanvibe).\n"
        f"Deliverables (GitHub Pages site + PDF report + ZIP package) build in "
        f"GitHub Actions."
    )
    _git_init(target, message=message)

    if not no_claude:
        _launch_claude(target)
