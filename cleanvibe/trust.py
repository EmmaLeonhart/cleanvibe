"""Pre-trust a folder cleanvibe itself just created, in Claude Code's config.

The first interactive Claude session in a new folder stops at "Is this a
project you created or one you trust?" until someone answers it at the machine.
For an agent-started session that the user means to pick up over Remote
Control, that prompt stalls everything. Emma chose (2026-09-26) to have
cleanvibe mark the folders it creates as trusted.

Scope and care, because this skips a Claude Code safety check:

* Only for a folder ``cleanvibe new`` (or bare ``cleanvibe``) has just created,
  never an existing one, and only when it is about to launch a session there.
* Claude Code's config (``~/.claude.json``, or ``$CLAUDE_CONFIG_DIR/.claude.json``)
  is never created by cleanvibe. If it is missing, unreadable, or not the shape
  expected, it is left untouched and the prompt simply appears as before.
* Only that folder's ``hasTrustDialogAccepted`` is set. A backup of the whole
  file is written next to it first, and the new file replaces the old one
  atomically.
* ``CLEANVIBE_CLAUDE_CONFIG`` overrides the path (the test suite points it at a
  temporary file so tests never touch the real config).

A Claude session that is already running keeps its own copy of the config and
may write it back later, which can drop the flag again. The worst case is the
prompt appearing, as it would have anyway.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

TRUST_FLAG = "hasTrustDialogAccepted"


def claude_config_path() -> Path:
    override = os.environ.get("CLEANVIBE_CLAUDE_CONFIG")
    if override:
        return Path(override)
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    if config_dir:
        return Path(config_dir) / ".claude.json"
    return Path.home() / ".claude.json"


def project_key(path: Path) -> str:
    """How Claude Code keys a project: the absolute path, forward slashes."""
    return str(Path(path).resolve()).replace("\\", "/")


def mark_trusted(path: Path, config: Path | None = None) -> bool:
    """Mark ``path`` trusted in Claude Code's config. True if it is now trusted."""
    config = claude_config_path() if config is None else Path(config)
    try:
        text = config.read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, UnicodeDecodeError, ValueError):
        return False
    if not isinstance(data, dict):
        return False
    projects = data.setdefault("projects", {})
    if not isinstance(projects, dict):
        return False
    key = project_key(path)
    entry = projects.setdefault(key, {})
    if not isinstance(entry, dict):
        return False
    if entry.get(TRUST_FLAG) is True:
        return True
    entry[TRUST_FLAG] = True

    try:
        shutil.copyfile(config, config.with_name(config.name + ".cleanvibe-backup"))
        fd, tmp = tempfile.mkstemp(prefix=".claude.json.", dir=str(config.parent))
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp, config)
    except OSError:
        return False
    return True
