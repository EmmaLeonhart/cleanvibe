# replication_skill

## Workflow Rules
- **Commit early and often.** Every meaningful change gets a commit with a clear message explaining *why*, not just what.
- **Do not enter planning-only modes.** All thinking must produce files and commits. If scope is unclear, create a `planning/` directory and write `.md` files there instead of using an internal planning mode.
- **Keep this file up to date.** As the project takes shape, record architectural decisions, conventions, and anything needed to work effectively in this repo.
- **Update README.md regularly.** It should always reflect the current state of the project for human readers.

## Testing
- **Write unit tests early.** As soon as there is testable logic, create a test file. Use `pytest` for Python projects or the appropriate test framework for the language in use.
- **Set up CI as soon as tests exist.** Create a `.github/workflows/ci.yml` GitHub Actions workflow that runs the test suite on push and pull request. Keep the workflow simple — install dependencies and run tests.
- **Keep tests passing.** Do not commit code that breaks existing tests. If a change requires updating tests, update them in the same commit.

## Project Description

`replication-skill` is a CLI + library that scaffolds a directory for
replicating an arXiv paper. The scaffold includes a SKILL.md that encodes the
replication plan so an agent (or human) can execute it end-to-end, a
`download_paper.py` that fetches the PDF into a gitignored `paper/` directory,
and a `paper.json` with frozen metadata. Installable as `replicate` on the PATH.

The three-layer vision (see `notes/replication_framing.md`): every replication
ships working code, a legibility layer (findings page), and a reusable agent
skill file. The skill files are the compounding artifact.

## Architecture and Conventions

- Package layout: `src/replication_skill/` (src layout, hatchling build).
- Templates under `src/replication_skill/templates/` are `string.Template`s;
  substitute with keys matching `ArxivPaper` fields.
- arXiv access: Atom API via `requests`, no auth. Respect the API by keeping
  queries single-paper and sending a descriptive User-Agent.
- Scaffolded paper PDFs are gitignored per-scaffold, never in the library's
  root `.gitignore`. Each replication directory is meant to be split off into
  its own repo eventually.
- Python 3.9+ supported; CI tests 3.10 and 3.12.

# currentDate
Today's date is 2026-04-18.
