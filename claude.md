# cleanvibe

## Project Description
A pip-installable Python CLI (`cleanvibe`) that scaffolds AI-assisted coding projects and launches Claude Code. Zero dependencies -- just stdlib.

## Architecture
```
cleanvibe/
├── cleanvibe/
│   ├── __init__.py      # Version string
│   ├── cli.py           # argparse-based CLI entry point
│   ├── scaffold.py      # Core logic: create_project(), clone_project()
│   └── templates.py     # CLAUDE.md, README.md, .gitignore templates
├── pyproject.toml       # Package metadata, [project.scripts] entry point
├── LICENSE              # MIT
└── README.md            # Human-facing docs
```

## Key Decisions
- **Zero dependencies**: Uses only stdlib (argparse, pathlib, subprocess, platform). No click, no typer. Keeps install fast and reduces supply chain risk.
- **Cross-platform**: Windows launches claude in a new cmd window via `subprocess.Popen`. Unix uses `os.execlp` to replace the process.
- **Non-destructive cloning**: `cleanvibe clone` only injects files that are missing. Never overwrites.
- **`--dry-run` flag**: Shows what would happen without writing anything. Builds trust.

## Workflow Guidelines
- **Commit early and often.** Every meaningful change gets a descriptive commit.
- **Do not enter planning-only modes.** All thinking produces files and commits.
- **Keep this file and README.md up to date** as the project evolves.
