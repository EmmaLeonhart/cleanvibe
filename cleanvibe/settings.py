"""Machine-level cleanvibe settings, kept in ~/.cleanvibe/config.json.

They hold for every project on this machine, so a choice like "private repos
don't spend GitHub Actions minutes" is made once, not per repo. The folder can
be moved with the CLEANVIBE_HOME environment variable (tests use it).

    cleanvibe config                         # list every setting
    cleanvibe config actions_on_private      # print one
    cleanvibe config actions_on_private true # change one
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# name -> (default, what it does)
SETTINGS = {
    "actions_on_private": (
        False,
        "Let private repos run GitHub Actions CI on push and pull request. "
        "Off: a private repo gets no CI workflow, and its tests run locally "
        "before each push.",
    ),
}

_TRUE = {"true", "yes", "on", "1"}
_FALSE = {"false", "no", "off", "0"}


def home() -> Path:
    env = os.environ.get("CLEANVIBE_HOME")
    return Path(env) if env else Path.home() / ".cleanvibe"


def config_path() -> Path:
    return home() / "config.json"


def _load() -> dict:
    try:
        data = json.loads(config_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def get(name: str):
    if name not in SETTINGS:
        raise KeyError(name)
    value = _load().get(name)
    return SETTINGS[name][0] if value is None else value


def parse(name: str, text: str):
    default = SETTINGS[name][0]
    if isinstance(default, bool):
        low = text.strip().lower()
        if low in _TRUE:
            return True
        if low in _FALSE:
            return False
        raise ValueError(f"{name} takes true or false, not {text!r}")
    return text


def set_value(name: str, text: str):
    if name not in SETTINGS:
        raise KeyError(name)
    value = parse(name, text)
    data = _load()
    data[name] = value
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return value


def _show(value) -> str:
    return str(value).lower() if isinstance(value, bool) else str(value)


def config_cli(name: str | None, value: str | None) -> int:
    """`cleanvibe config [NAME [VALUE]]`. Exit 0 ok, 2 unknown name or bad value."""
    if name is None:
        print(f"Settings for this machine ({config_path()}):")
        for key, (default, doc) in SETTINGS.items():
            print(f"  {key} = {_show(get(key))}  (default {_show(default)})")
            print(f"      {doc}")
        return 0
    if name not in SETTINGS:
        print(f"cleanvibe config: no setting {name!r}. Known: "
              f"{', '.join(SETTINGS)}", file=sys.stderr)
        return 2
    if value is None:
        print(_show(get(name)))
        return 0
    try:
        new = set_value(name, value)
    except ValueError as e:
        print(f"cleanvibe config: {e}", file=sys.stderr)
        return 2
    print(f"{name} = {_show(new)} (saved to {config_path()})")
    return 0
