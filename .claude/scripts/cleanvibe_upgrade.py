"""Pick up a new cleanvibe release: upgrade the installed cleanvibe, then refresh this project.

Shipped by cleanvibe (since 2.0.12) as .claude/scripts/cleanvibe_upgrade.py; `cleanvibe
refresh` replaces it whole. The loop-tick hook says when a newer release is out; run this then.

    python .claude/scripts/cleanvibe_upgrade.py           # upgrade if newer, then refresh
    python .claude/scripts/cleanvibe_upgrade.py --check   # only say what would happen

It installs into the Python that runs it (the one `cleanvibe` should be installed in). Several
sessions on one machine may run it at the same tick, so the install takes a lock
(~/.cleanvibe/upgrade.lock, stale after 15 minutes) and re-checks the version once it holds it.
Exit 0 when up to date or upgraded, 1 when something failed (the message says what).
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PYPI = "https://pypi.org/pypi/cleanvibe/json"
LOCK_STALE = 15 * 60


def _version_tuple(v):
    out = []
    for part in str(v).strip().split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        out.append(int(digits) if digits else 0)
    return tuple(out)


def installed_version():
    try:
        from importlib.metadata import version, PackageNotFoundError
    except ImportError:  # Python < 3.8
        return None
    try:
        return version("cleanvibe")
    except PackageNotFoundError:
        return None


def latest_version(timeout=10):
    source = os.environ.get("CLEANVIBE_PYPI_JSON")  # tests: a local file instead of PyPI
    if source:
        data = json.loads(Path(source).read_text(encoding="utf-8"))
    else:
        req = urllib.request.Request(PYPI, headers={"User-Agent": "cleanvibe-upgrade"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    return data["info"]["version"]


def lock_path():
    base = os.environ.get("CLEANVIBE_HOME") or os.path.join(os.path.expanduser("~"), ".cleanvibe")
    return Path(base) / "upgrade.lock"


def take_lock(path, wait=120):
    """Create the lock file exclusively; wait up to `wait` seconds for another holder."""
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + wait
    while True:
        try:
            fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        except FileExistsError:
            try:
                if time.time() - path.stat().st_mtime > LOCK_STALE:
                    path.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.time() > deadline:
                return False
            time.sleep(3)


def run(cmd, dry):
    print("$ " + " ".join(cmd))
    if dry:
        return 0
    return subprocess.run(cmd).returncode


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    check_only = "--check" in argv
    dry = check_only or bool(os.environ.get("CLEANVIBE_UPGRADE_DRY"))
    root = Path(__file__).resolve().parents[2]
    have = installed_version()
    if have is None:
        print(f"cleanvibe is not installed in this Python ({sys.executable}); nothing to upgrade.")
        return 1
    try:
        latest = latest_version()
    except Exception as exc:
        print(f"Could not read the latest cleanvibe version ({exc}); try again next tick.")
        return 1
    if _version_tuple(latest) <= _version_tuple(have):
        print(f"cleanvibe {have} is the latest; nothing to do.")
        return 0
    print(f"cleanvibe {latest} is out (installed: {have}).")
    if check_only:
        print("Would upgrade it, then run `cleanvibe refresh` on this project.")
        return 0
    lock = lock_path()
    if not take_lock(lock):
        print(f"Another session holds {lock}; try again next tick.")
        return 1
    try:
        have = installed_version() or have
        if _version_tuple(latest) > _version_tuple(have):
            if run([sys.executable, "-m", "pip", "install", "-q", "-U", f"cleanvibe=={latest}"], dry):
                print("The upgrade failed; the output above says why.")
                return 1
        else:
            print(f"Another session already installed {have}.")
    finally:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass
    if run([sys.executable, "-m", "cleanvibe.cli", "refresh", str(root)], dry):
        print("`cleanvibe refresh` failed; the output above says why.")
        return 1
    print("Done. Commit what refresh changed, saying which cleanvibe version it came from.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
