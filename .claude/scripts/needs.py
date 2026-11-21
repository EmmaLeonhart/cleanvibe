"""Add, list and update records in a project's needs file (NEEDS-USER.md).

One record per thing only the user can do (kind, do, blocks, where, raised,
status); see the needs-user skill. Sessions use this tool instead of
hand-editing the file, so every record stays parseable by whatever collects
them (a PC manager). The file sits at the project root; its name comes from
"needs_file" in .cleanvibe.json, default NEEDS-USER.md. Written by cleanvibe
and replaced by `cleanvibe refresh`.

    python .claude/scripts/needs.py add --title T --kind action --do D --blocks B --where W [--default X] [--file F]
    python .claude/scripts/needs.py list [--status open|reported|hold|done|active] [--file F]
    python .claude/scripts/needs.py set-status NE-3 "reported" [--file F]
    python .claude/scripts/needs.py check [--file F]

Exit codes: 0 ok; 2 error (nothing written).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _needs_file_name() -> str:
    try:
        marker = json.loads((PROJECT_ROOT / ".cleanvibe.json").read_text(encoding="utf-8"))
        return marker.get("needs_file") or "NEEDS-USER.md"
    except (OSError, ValueError):
        return "NEEDS-USER.md"


DEFAULT_FILE = str(PROJECT_ROOT / _needs_file_name())
HEADER = "# Needs you\n"
REQUIRED = ["kind", "do", "blocks", "where", "raised", "status"]
OPTIONAL = ["default", "notes"]
KINDS = {"action", "decision", "report"}

HEADING_RE = re.compile(r"^## NE-(\d+): (.+?)\s*$")
FIELD_RE = re.compile(r"^- \*\*([a-z]+):\*\* (.*?)\s*$")
DATE = r"\d{4}-\d{2}-\d{2}"
STATUS_RE = re.compile(rf"^(open|reported|hold until {DATE}|done {DATE})$")


class RecordError(ValueError):
    """The file or a requested change does not follow the format."""


@dataclass
class Record:
    number: int
    title: str
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"NE-{self.number}"

    @property
    def state(self) -> str:
        """The status word alone: open, reported, hold or done."""
        return self.fields["status"].split()[0]

    def render(self) -> str:
        lines = [f"## {self.id}: {self.title}"]
        for name in REQUIRED + OPTIONAL:
            if name in self.fields:
                lines.append(f"- **{name}:** {self.fields[name]}")
        return "\n".join(lines) + "\n"


def validate(rec: Record) -> None:
    missing = [n for n in REQUIRED if not rec.fields.get(n)]
    if missing:
        raise RecordError(f"{rec.id}: missing field(s): {', '.join(missing)}")
    unknown = [n for n in rec.fields if n not in REQUIRED + OPTIONAL]
    if unknown:
        raise RecordError(f"{rec.id}: unknown field(s): {', '.join(unknown)}")
    if rec.fields["kind"] not in KINDS:
        raise RecordError(f"{rec.id}: kind must be action, decision or report, not {rec.fields['kind']!r}")
    if not re.fullmatch(DATE, rec.fields["raised"]):
        raise RecordError(f"{rec.id}: raised must be YYYY-MM-DD, not {rec.fields['raised']!r}")
    if not STATUS_RE.match(rec.fields["status"]):
        raise RecordError(f"{rec.id}: bad status {rec.fields['status']!r}")
    if rec.fields["kind"] == "decision" and not rec.fields.get("default"):
        raise RecordError(f"{rec.id}: a decision needs a default")


def parse(text: str) -> list[Record]:
    """Parse needs-file text into records, validating each one."""
    records: list[Record] = []
    current: Record | None = None
    for lineno, line in enumerate(text.splitlines(), 1):
        m = HEADING_RE.match(line)
        if m:
            current = Record(int(m.group(1)), m.group(2))
            records.append(current)
            continue
        if current is None:
            continue
        f = FIELD_RE.match(line)
        if f:
            name, value = f.groups()
            if name in current.fields:
                raise RecordError(f"line {lineno}: {current.id} repeats field {name!r}")
            current.fields[name] = value
        elif line.startswith("## "):
            raise RecordError(f"line {lineno}: heading is not '## NE-<n>: <title>': {line!r}")
    seen: set[int] = set()
    for rec in records:
        if rec.number in seen:
            raise RecordError(f"{rec.id} appears twice")
        seen.add(rec.number)
        validate(rec)
    return records


def render(records: list[Record]) -> str:
    return HEADER + "".join("\n" + r.render() for r in records)


def load(path: Path) -> list[Record]:
    if not path.exists():
        return []
    return parse(path.read_text(encoding="utf-8"))


def save(path: Path, records: list[Record]) -> None:
    """Write atomically, so a reader never sees half a file."""
    text = render(records)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".needs-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def add(path: Path, *, title: str, kind: str, do: str, blocks: str, where: str,
        default: str | None = None, notes: str | None = None,
        today: dt.date | None = None) -> Record:
    records = load(path)
    number = max((r.number for r in records), default=0) + 1
    fields = {"kind": kind, "do": do, "blocks": blocks, "where": where,
              "raised": (today or dt.date.today()).isoformat(), "status": "open"}
    if default:
        fields["default"] = default
    if notes:
        fields["notes"] = notes
    for name, value in fields.items():
        if "\n" in value:
            raise RecordError(f"{name} must be one line")
    rec = Record(number, title.strip(), fields)
    validate(rec)
    records.append(rec)
    save(path, records)
    return rec


def set_status(path: Path, record_id: str, status: str) -> Record:
    if not STATUS_RE.match(status):
        raise RecordError(f"bad status {status!r}: use open, reported, "
                          "'hold until YYYY-MM-DD' or 'done YYYY-MM-DD'")
    records = load(path)
    for rec in records:
        if rec.id == record_id.upper():
            rec.fields["status"] = status
            save(path, records)
            return rec
    raise RecordError(f"no record {record_id}")


def select(records: list[Record], status: str | None) -> list[Record]:
    """Filter by status word; 'active' means everything not done."""
    if status is None:
        return records
    if status == "active":
        return [r for r in records if r.state != "done"]
    return [r for r in records if r.state == status]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", default=DEFAULT_FILE, help="path to the needs file")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("--title", required=True)
    a.add_argument("--kind", required=True, choices=sorted(KINDS))
    a.add_argument("--do", required=True)
    a.add_argument("--blocks", required=True)
    a.add_argument("--where", required=True)
    a.add_argument("--default")
    a.add_argument("--notes")

    ls = sub.add_parser("list")
    ls.add_argument("--status", choices=["open", "reported", "hold", "done", "active"])

    s = sub.add_parser("set-status")
    s.add_argument("id")
    s.add_argument("status")

    sub.add_parser("check")

    args = ap.parse_args(argv)
    path = Path(args.file)
    try:
        if args.cmd == "add":
            rec = add(path, title=args.title, kind=args.kind, do=args.do,
                      blocks=args.blocks, where=args.where,
                      default=args.default, notes=args.notes)
            print(f"added {rec.id}: {rec.title}")
        elif args.cmd == "list":
            for rec in select(load(path), args.status):
                print(f"{rec.id} [{rec.fields['status']}] {rec.title} ({rec.fields['where']})")
        elif args.cmd == "set-status":
            rec = set_status(path, args.id, args.status)
            print(f"{rec.id} is now {rec.fields['status']}")
        elif args.cmd == "check":
            print(f"{path}: {len(load(path))} record(s), all valid")
    except RecordError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
