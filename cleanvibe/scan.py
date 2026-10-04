"""``cleanvibe scan`` — read-only pattern scan of code you did not write.

A replication runs third-party code: the authors' recipe, a cloned repo, a
downloaded zip. The replicate templates make the agent ask the user before
running any of it. This scan gives that question something to go on: what the
code would touch, grouped by kind, with the lines that matched and the hosts
it mentions.

It is a pattern match, not a security review. It reads files and changes
nothing; finding nothing does not mean the code is safe. Exit code 0 when
nothing matched, 1 when something did, 2 when no given path exists.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# (category, what it means for the user, patterns). Order is report order.
CATEGORIES = (
    ("pipe-to-shell", "downloads something and runs it unseen", (
        r"\b(?:curl|wget)\b[^|\n]*\|\s*(?:sudo\s+)?(?:ba|z|da)?sh\b",
        r"\bInvoke-Expression\b|\biex\b\s*\(",
        r"DownloadString\s*\(",
    )),
    ("dynamic-exec", "runs code built or decoded at run time", (
        r"(?<![\w.])eval\s*\(",
        r"(?<![\w.])exec\s*\(",
        r"\bbase64\s+(?:-d|--decode)\b",
        r"\bb64decode\s*\(",
        r"\bmarshal\.loads?\s*\(",
        r"\bpickle\.loads?\s*\(",
        r"\bFunction\s*\(\s*['\"]",
    )),
    ("destructive", "deletes or overwrites outside its own files", (
        r"\brm\s+-[a-zA-Z]*(?:rf|fr)[a-zA-Z]*\b",
        r"\bshutil\.rmtree\s*\(",
        r"\bmkfs(?:\.\w+)?\b",
        r"\bdd\s+if=",
        r"\bgit\s+push\s+(?:-f|--force)\b",
        r"\bchmod\s+(?:-R\s+)?777\b",
        r"\bRemove-Item\b.*-Recurse",
        r"\bformat\s+[a-zA-Z]:",
    )),
    ("credentials", "reads keys, tokens or credential stores", (
        r"[~/\\]\.ssh\b",
        r"[~/\\]\.aws\b",
        r"\.netrc\b",
        r"\bid_(?:rsa|ed25519|ecdsa)\b",
        r"\.config/gcloud\b",
        r"\b(?:GITHUB|GH|AWS_SECRET|OPENAI_API|ANTHROPIC_API|HF)_?(?:TOKEN|KEY|ACCESS_KEY)\w*",
        r"\bkeyring\.get_password\b",
        r"\bsecurity\s+find-(?:generic|internet)-password\b",
    )),
    ("persistence", "changes the system or survives the run", (
        r"\bcrontab\b",
        r"[~/\\]\.(?:bashrc|zshrc|bash_profile|profile)\b",
        r"\bsystemctl\s+(?:enable|start)\b",
        r"\bsudo\b",
        r"\bschtasks\b",
        r"\bHKEY_|\breg\s+add\b",
        r"\blaunchctl\s+load\b",
    )),
    ("package-source", "installs from an unusual source", (
        r"--(?:extra-)?index-url\b",
        r"\bpip3?\s+install\b[^\n]*\bgit\+",
        r"\bnpm\s+install\b[^\n]*\bhttps?://",
    )),
)

_COMPILED = tuple(
    (name, meaning, tuple(re.compile(p) for p in patterns))
    for name, meaning, patterns in CATEGORIES
)
_URL_HOST = re.compile(r"\bhttps?://([A-Za-z0-9.-]+\.[A-Za-z]{2,})")

# Files nobody can read before running: flagged as their own category.
BINARY_SUFFIXES = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".pyc", ".pyd", ".o", ".a",
    ".jar", ".class", ".whl", ".msi", ".app", ".deb", ".rpm",
}
# Never scanned: version control, Claude Code config, CI workflows (they run on
# GitHub's runners, not on this machine), and the docs cleanvibe itself wrote
# at the project root (they quote commands as instructions).
SKIP_DIRS = {
    ".git", ".github", ".claude", "__pycache__", "node_modules", ".venv", "venv",
}
SKIP_ROOT_FILES = {
    "CLAUDE.md", "README.md", "queue.md", "todo.md", "devlog.md", "INTENT.md",
}
MAX_BYTES = 2_000_000
EXAMPLES_PER_CATEGORY = 8


@dataclass
class Hit:
    category: str
    where: str
    line: str

    def __str__(self) -> str:
        return f"{self.where}: {self.line}"


@dataclass
class Report:
    hits: list
    hosts: list
    files_scanned: int


def _iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        if not path.is_file():
            continue
        if len(rel.parts) == 1 and path.name in SKIP_ROOT_FILES:
            continue
        yield path


def _read_text(path: Path):
    try:
        if path.stat().st_size > MAX_BYTES:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


def scan(paths) -> Report:
    """Scan files and directories; return every hit and the hosts mentioned."""
    hits, hosts, scanned = [], set(), 0
    for root in paths:
        root = Path(root)
        if not root.exists():
            continue
        base = root.parent if root.is_file() else root
        for path in _iter_files(root):
            where = path.relative_to(base).as_posix()
            if path.suffix.lower() in BINARY_SUFFIXES:
                hits.append(Hit("binary", where, "compiled or packaged file"))
                continue
            text = _read_text(path)
            if text is None:
                continue
            scanned += 1
            for lineno, line in enumerate(text.splitlines(), 1):
                hosts.update(h.lower() for h in _URL_HOST.findall(line))
                for name, _, patterns in _COMPILED:
                    if any(p.search(line) for p in patterns):
                        snippet = line.strip()
                        if len(snippet) > 120:
                            snippet = snippet[:117] + "..."
                        hits.append(Hit(name, f"{where}:{lineno}", snippet))
    return Report(hits=hits, hosts=sorted(hosts), files_scanned=scanned)


def _say(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "ascii"
        print(text.encode(enc, errors="replace").decode(enc))


def scan_cli(paths) -> int:
    paths = [Path(p) for p in (paths or ["."])]
    existing = [p for p in paths if p.exists()]
    for p in paths:
        if not p.exists():
            _say(f"cleanvibe scan: {p} does not exist (skipped)")
    if not existing:
        return 2

    report = scan(existing)
    _say(f"cleanvibe scan: {', '.join(str(p) for p in existing)} "
         f"({report.files_scanned} text files)")
    meanings = {name: meaning for name, meaning, _ in CATEGORIES}
    meanings["binary"] = "cannot be read before it runs"
    order = [name for name, _, _ in CATEGORIES] + ["binary"]
    for name in order:
        found = [h for h in report.hits if h.category == name]
        if not found:
            continue
        _say(f"\n[{name}] {len(found)}: {meanings[name]}")
        for hit in found[:EXAMPLES_PER_CATEGORY]:
            _say(f"  {hit}")
        if len(found) > EXAMPLES_PER_CATEGORY:
            _say(f"  ... and {len(found) - EXAMPLES_PER_CATEGORY} more")
    if report.hosts:
        _say(f"\nHosts mentioned ({len(report.hosts)}): {', '.join(report.hosts)}")
    if not report.hits:
        _say("\nNo risky patterns matched.")
    _say("\nThis is a pattern match, not a security review: "
         "no match does not mean the code is safe.")
    return 1 if report.hits else 0
