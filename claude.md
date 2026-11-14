# cleanvibe

## Project Description
A pip-installable Python CLI (`cleanvibe`) that starts Claude Code sessions in git-tracked projects. **cleanvibe 2** (v2.0.0): every project starts as an open-ended session that works from low information (the user may say little or be away); the agent infers the purpose, keeps `INTENT.md`, and transcripts are committed. This repo is itself a cleanvibe 2 project (since 2026-11-13), except that its transcripts are not committed (it is public). The 1.x modes live under `cleanvibe legacy`. Zero dependencies -- just stdlib.

## Architecture
```
cleanvibe/
├── cleanvibe/
│   ├── __init__.py      # Version string
│   ├── cli.py           # argparse CLI: bare `cleanvibe`, new, replicate, doctor, legacy {new,research,original,chat,clone,convert}
│   ├── project.py       # cleanvibe 2: new_project(), open_project(), is_cleanvibe_repo(), auto_project_path()
│   ├── launch.py        # launch Claude as a real top-level session (strip parent-session env, new console/terminal)
│   ├── trust.py         # pre-trust folders cleanvibe creates in Claude Code's config (~/.claude.json)
│   ├── scaffold.py      # 1.x core: create_project(), clone_project(), convert_project(); shared _write/_git_init/_launch_claude
│   ├── research.py      # research_project(): original-research scaffold (lit-review-first + report)
│   ├── original.py      # original_project(): research scaffold + topic-finding loop (uncertain topic)
│   ├── chat.py          # chat_project(): git-tracked conversation (ask-first, session logs committed by hook)
│   ├── doctor.py        # doctor(): read-only drift audit (run_checks → Finding list)
│   ├── scan.py          # scan(): read-only pattern scan of third-party code before the consent gate
│   ├── arxiv.py         # stdlib arXiv/alphaxiv metadata fetch + parsing (zero-dep)
│   ├── clawrxiv.py      # stdlib clawRxiv (clawrxiv.io) JSON API fetch + parsing (zero-dep)
│   ├── replicate.py     # replicate_{project,clawrxiv_project,manual_project}(): per-paper replication
│   ├── htmltext.py      # stdlib HTML -> Markdown for URL-mode papers (paper.md); embedded in download_paper.py
│   ├── skills.py        # the vendored skills (single source of truth), write_skills()
│   └── templates.py     # all generated text: v2 (v2_*, V2_INTAKE_PY), 1.x modes, replication, the session-log hook script
├── tests/               # stdlib unittest, run by CI on win/mac/linux
├── docs/                # case-studies/, legacy-decisions.md (replicate + 1.x design), replication_framing.md, replication-examples/
├── paper/, paper-replay/ # the clawRxiv papers (CI posts them: .github/workflows/clawrxiv.yml)
├── subtrees/            # merged repos, with history: helping-with-arxiv/ (Quatrix arXiv prep), replication_skill/ (origin of `replicate`), clawrxiv_clone/ (Claw4S/clawRxiv clone)
├── pages/                # static GitHub Pages site (index.html/identity.css/CNAME → cleanvibe.emmaleonhart.com)
├── .github/workflows/
│   ├── ci.yml           # 3-OS x 2-py-version matrix
│   ├── pages.yml        # deploy pages/ to GitHub Pages
│   ├── clawrxiv.yml     # post paper/ or paper-replay/ to clawRxiv and fetch the review
│   └── publish.yml      # PyPI publish on release
├── pyproject.toml       # Package metadata, [project.scripts] entry point
├── INTENT.md            # this repo's own read of its goal (a cleanvibe 2 project since 2026-11-13)
├── .cleanvibe.json      # v2 marker; "session_log": false (public repo: no committed transcripts)
├── LICENSE              # MIT
├── README.md            # Human-facing docs
├── queue.md             # Active, delete-only work queue
├── todo.md              # Long-horizon backlog (abstract)
└── devlog.md            # Where "done" lives: dated entries + releases
```

## Key Decisions
- **cleanvibe 2 (v2.0.0) — the general-purpose rework.** Emma's spec is recorded in `devlog.md` (2026-09-26, "cleanvibe 2 — the spec", plus the 7:15 PM low-information addendum). The essentials:
  - **Creation options (2026-10-06, Emma):** `--visibility public|private|local` and `--prompt TEXT` on bare `cleanvibe` and `new`. The default publishing rule in the generated CLAUDE.md: always push to a GitHub remote unless told local; any signal for public makes it public, any for private makes it private, private breaks ties (it used to insist on private). `--prompt` is appended to the end of the first prompt as the user's own words (`templates.cmd_safe` swaps cmd-unsafe characters) and kept verbatim in the marker (`starting_prompt`); Emma's reason: Claude weighs what comes from the user most, and cleanvibe's job is to get the context in front of the agent as the user's. CLAUDE.md's "This project's setup" records the name kind (custom vs auto-generated placeholder), visibility and prompt. "Keep going without asking": planned work needs no consent to continue; an unanswered decision gets made and recorded (a practice session stalled waiting on an absent user to restart a job).
  - **CLI:** bare `cleanvibe` opens the cwd's project (v2 marker `.cleanvibe.json` or a 1.x project) with the resume prompt, else creates an auto-named project in the cwd: a random passphrase (`golden-swift-otter`, `templates.passphrase_name`) that is both the folder and the session title (Emma, 2026-10-05; until then the folder was `untitled-cleanvibe-project` and only the title was a passphrase). `new [NAME]` creates one (auto-named without NAME; an existing project is opened; a non-empty non-project folder is refused). `replicate` and `doctor` are unchanged top-level commands. The 1.x modes run as `cleanvibe legacy <cmd>` with a DEPRECATED warning; their old top-level names exit 2 pointing there.
  - **Low information is the design point.** The user may say nothing or be away (Emma runs cleanvibe from a scheduled job). Priority: chat > what is in the folder (`data_lake/`; specs/instructions there are followed) > the directory name. The agent keeps `INTENT.md` (its analysis of the goal, evidence, confidence) and writes assumptions down instead of stopping to ask. **AskUserQuestion only when the user is clearly present and replying.**
  - **The first-session prompt carries the operating instructions** (it is the one message cleanvibe can put directly in front of the agent): low information, read CLAUDE.md, CronCreate the one-time **thirty-minute intake**, write a first read into INTENT.md. The resume prompt reschedules the intake if it never ran.
  - **Thirty-minute intake:** `.claude/scripts/data_lake_intake.py` (`templates.V2_INTAKE_PY`) commits the repo as found, `git mv`s never-committed top-level material into `data_lake/` and commits that, then reports user engagement from `sessions/*.jsonl` (cleanvibe's own `[cleanvibe cron]`/starting prompts excluded; substantial = 2+ messages or 300+ chars). The agent then studies the data lake, updates INTENT.md, plans with the matching skill, and starts the autonomous loop: immediately with little/no engagement, or via a one-shot 60 minutes later with substantial engagement. Runs once (`intake_at` in the marker).
  - **Data-lake rule:** material goes into `data_lake/` and is committed as part of the repository's history (stray material: commit where it landed, then `git mv`).
  - **Minimal scaffold:** CLAUDE.md, README.md, INTENT.md, marker, `.gitignore` (+`scratch/` for one-off crud), `sessions/`, `data_lake/`, skills, hooks, intake script. No queue/todo/devlog until `queue-driven-workflow` adds them. Local git on `main`; since 2.0.3 work mode creates a private GitHub repo under a descriptive name and pushes.
  - **Sessions are real top-level sessions with Remote Control** (`launch.clean_env` strips `CLAUDE_CODE_CHILD_SESSION`, the parent session id/socket/bridge id, etc.; `claude "<prompt>" --remote-control`, flag after the prompt because it takes an optional name). New folders are **pre-trusted** in Claude Code's config (`trust.mark_trusted`: only folders `new_project` just created and is launching; backup + atomic write; never creates or repairs the config) so an unattended session doesn't stall at the trust prompt. Emma approved this explicitly.
  - **Transcripts:** the Stop hook refreshes `sessions/<local date>_<id>.{jsonl,md}` after every response and commits them at most hourly; SessionEnd always commits (and pushes if there is an upstream).
  - **Skills:** `autonomous-loop` rewritten without the start/kill/restart choreography (only the user stops the crons; idle ticks are normal) and not split for legacy; new general `research-practice`; `queue-driven-workflow` is the development practice a v2 project adopts on demand.
  - **2.0.1, from case study 02** (`docs/case-studies/`): the intake verdict has a **nothing to go on** state (no material + no engagement + generated name → don't plan, don't loop, say so and wait) and a **name only** state. CLAUDE.md and the first prompt say **a guess about why the project exists is not a task**, stay inside the project, and "stop"/"don't" means stop. The **path stays in the prompts**: Emma corrected an attempt to drop it; it carries real information, and the failure was inventing work from a correct guess, not the path. **Session names:** a user-chosen folder name is passed as `--name` and the Remote Control name; auto-named projects use their passphrase folder name for both (since 2.0.3 for the title, 2026-10-05 for the folder); the prompts say a generated name carries no meaning.
- **Case studies** (`docs/case-studies/`): every practice or real session gets a write-up: input, what it did, analysis, the fix it led to. Keep watching and adding to them.
- **Tests** never write the real `~/.claude.json`: launch-path test modules point `CLEANVIBE_CLAUDE_CONFIG` at a temp file (`unittest discover -s tests` does not import `tests/__init__.py`, so it is set per module too).
- **Zero dependencies**: Uses only stdlib (argparse, pathlib, subprocess, platform). No click, no typer. Keeps install fast and reduces supply chain risk.
- **Cross-platform launch** (`launch.py`): Windows opens a new console (`cmd /k`, new process group, breaking away from the caller's job object when allowed). Unix with a terminal `execvpe`s `claude`; without one (run by an agent) it opens a new terminal window from a generated script, or prints the command.
- **`--dry-run` flag**: Shows what would happen without writing anything. Builds trust.
- **`cleanvibe doctor` — read-only drift audit (v1.18.0).** `cleanvibe/doctor.py`. Eight checks, each a `check_*(root) -> list[Finding]` in the `CHECKS` tuple: `files`, `skills` (vendored copy vs `skills.SKILLS`), `queue-done` (ticked boxes / check marks / DONE / strikethrough in `queue.md`), `version` (queue pointer vs `pyproject.toml`), `devlog-tags` (every `v*` tag mentioned in `devlog.md`), `section-refs` (every CLAUDE.md section reference must name a real heading), `ci`, `pages-gate` (pre-v1.18.0 Pages workflow on a private repo). It never writes; exit 0 clean, 1 findings, 2 bad path. Output goes through `_say`, so a Windows console can't crash on a quoted ✓. There is **no `--fix`** yet: none of the findings has a fix safe enough to apply blind. **`tests/test_doctor.py` asserts a fresh scaffold of every mode audits clean.** That test is what caught the generator pointing `queue.md`/`todo.md` at CLAUDE.md sections that had moved into skills in v1.14.0; they now name the skills. Run `python -m cleanvibe.cli doctor .` on this repo before a release.
- **`cleanvibe scan` — read-only pattern scan of third-party code (2026-10-03).** `cleanvibe/scan.py`. Feeds the replicate consent gate: every gate passage tells the agent to run `cleanvibe scan .` and put the summary in its question, so the user's consent is informed rather than blind (`tests/test_scan.py` checks the templates say so). Categories are regex lists in `CATEGORIES` (pipe-to-shell, dynamic-exec, destructive, credentials, persistence, package-source) plus `binary` by suffix; it also lists every URL host mentioned. It skips `.git/`, `.github/` (CI runs on GitHub's runners, and cleanvibe's own Pages workflow uses `sudo apt-get`), `.claude/`, and the cleanvibe docs at the project root; the same names deeper down are the authors' files and are scanned. Exit 0 nothing matched, 1 matches, 2 no path exists. It says on every run that it is a pattern match, not a security review; keep that line.
- **Project website**: a dependency-free static site under `pages/` (vanilla HTML/CSS/JS: a what-it-is section, one searchable card per subcommand, the stability contract; `updates.md` is the skill update index that scaffolded repos read weekly) deployed by `.github/workflows/pages.yml`. When a subcommand is added or changed, update its card. Pages Source on the repo is set to "GitHub Actions".
- **`devlog.md` — "done" lives here, so `queue.md` can stay delete-only.** Every cleanvibe-scaffolded project (and this repo) ships a `devlog.md`. Finishing a queue item = delete the item from `queue.md` AND append a dated entry to `devlog.md` in the same commit, then push. Never tick boxes in place — a checked box left in `queue.md` is the failure mode this file exists to prevent. Releases (tag + one-line note) and notable milestones also live in `devlog.md`. `cleanvibe new` and `cleanvibe replicate` write a starter entry; `cleanvibe clone` and `cleanvibe convert` inject a "backfill from `git log`" variant whose first onboarding task is to catch the existing repo's devlog up to present before normal work resumes. Flow: `todo.md` (abstract) → `queue.md` (concrete steps) → task tool (in-flight) → `devlog.md` + `git log` (history).
- **PyPI packaging**: `pyproject.toml` declares `[tool.setuptools] packages = ["cleanvibe"]` explicitly. Without this, setuptools' flat-layout auto-discovery also picks up sibling directories like `site/` and `pages/` as candidate "packages" and refuses to build (caused the v1.0.0 PyPI publish to fail; fixed in v1.1.0).
- **Default branch is `main`, not `master`**: every cleanvibe-init'd repo (`new` / `convert` / `replicate`) passes `git init -b main` so the initial branch is `main` regardless of the user's `init.defaultBranch` config. Requires git ≥ 2.28 (mid-2020). Fixed in v1.1.1; older cleanvibe-scaffolded repos may need a one-time `git branch -m master main`.
- **Python 3.9 compat**: any module that uses PEP 604 unions (`X | None`) or PEP 585 generics (`list[str]`) in annotations must include `from __future__ import annotations` at the top — otherwise it fails at import on 3.9 (CI matrix target). `cli.py`, `arxiv.py`, and `templates.py` all carry the future import.
- **`replicate` and the 1.x modes (`legacy new/research/original/chat/clone/convert`)**: their design decisions (replication architecture, consent gate, copyright rule, clawRxiv, report theme, research/original/chat modes, clone/convert, the 1.x scaffold and defaults) are in `docs/legacy-decisions.md`, moved there verbatim on 2026-11-13 to keep this file to what is current. Read it before changing any of those.

## Skills

cleanvibe dogfoods its own skills: the workflow behaviors live as skills in
`.claude/skills/` (auto-discovered by Claude Code) — `emergency-stop`,
`cron-is-local`, `autonomous-loop`, `queue-driven-workflow`, `research-practice`,
`writing-style`, `cleanvibe-update-check`, `browser-persistence`. They are the single-source-of-truth bodies from
`cleanvibe/skills.py`, materialized by `write_skills()`. The short version of the
workflow contract: commit early with *why*; plan into `queue.md` first and mirror
into the task tool; `todo.md` is the long-horizon basis for `queue.md`; finishing
an item = delete from `queue.md` + append a dated `devlog.md` entry in the same
commit, then push (never tick a box in place); keep this file, README.md, and
devlog.md current.

- **Last cleanvibe update check:** `never`
- **Updates source:** <https://cleanvibe.emmaleonhart.com/updates.md>

## Session start: turn the loop on first
**The very first action of every session in this repo is to start the
`autonomous-loop` cron** (one `CronCreate`, `7,37 * * * *`, the prompt from the
skill), without asking and before anything else. Emma, 2026-11-09: this was the
only repo that didn't, because nothing here said so.

## Hourly status-report cron for extensive work
(Heading kept for old links; the loop is no longer hourly or a status report.)
The source of truth is the `autonomous-loop` skill (`.claude/skills/autonomous-loop/SKILL.md`,
from `cleanvibe/skills.py`). Since v2.0.2 it is **one** session-local `CronCreate`
job, `7,37 * * * *` (every half hour), whose prompt is just "commit and push any
and all changes, then continue working on the queue". There are no separate
flush or status crons: Emma found the reports and flushes weren't useful. An
empty research queue refills from `research/SUMMARY.md`; an idle tick is
normal; only the user turns the cron off. Use it when the user wants a long
stretch of autonomous work. The history (the three-cron playbook, the
kill/restart choreography, and why each was dropped) is in `devlog.md`.

## Long command series run in strict order
When the user gives a long series of commands, treat it as a long series of commands to be
executed in relatively STRICT ORDER, one after another, EVEN IF the order seems not to make
sense or seems inefficient. The sequencing is intentional — the user organizes the steps so
states change in the order they want. Do not reorder, merge, or skip steps.

## Not-done taxonomy (never "deliberately deferred")
When work is NOT done, tag it with exactly ONE of: **NEEDS-DECISION** (name the decision +
who decides), **BLOCKED-ON-USER-ACTION** (a real-world action only the user can take — name
it), **BLOCKED-ON-EXTERNAL** (CI / a remote / a third party / another session's unpushed
commit — name it + the unblock signal), **NEEDS-INVESTIGATION** (not understood yet — a
to-do for the next tick, never a resting place), **UNSAFE-TO-GUESS** (could cause damage —
name the risk + what makes it safe), or **OUT-OF-SCOPE** (another repo's job — name it).
LOAD-BEARING DEFAULT: if it fits none of these with a specifically-named blocker, it is NOT
deferred — DO IT NOW. Bare "deliberately not done" / "blocked on <person>" is banned.

## Default replication target & live smoke tests
- **The default paper for `cleanvibe replicate` is arXiv:2605.20919 — "Sutra: Tensor-Op RNNs as a Compilation Target for Vector Symbolic Architectures"** (the maintainer's own paper). Use it whenever you need to exercise the `replicate` pipeline end-to-end against a real paper.
- **`scratch/` (repo root, gitignored) holds a session's working files** (one-off edit scripts, drafts, release notes). Use it instead of Claude Code's temp scratchpad under `%LOCALAPPDATA%\Temp\claude\`, which Storage Sense deletes on its own schedule. Never commit it.
- **`tests/scratch/` is the practice sandbox for live runs of any mode** (`cleanvibe new` practice projects, `replicate` smoke tests). Its contents are gitignored (`tests/scratch/*`); only `tests/scratch/.gitkeep` is tracked, so the directory always exists. Never commit anything else in it. Each run scaffolds a full project (with its own nested git repo) in there.
- The committed unit tests in `tests/` are network-free (they monkeypatch `fetch_paper`). A **live** smoke test actually hits arXiv, e.g.:
  ```
  python -m cleanvibe.cli replicate https://arxiv.org/abs/2605.20919 tests/scratch/replicating-sutra
  ```
  It launches a Claude session (there is no `--no-claude` since 2.0.8: projects created without their first session ended up unusable); use an explicit path under `tests/scratch/`. To exercise the full source-first path, then run the generated downloader (`cd` into the scratch project and `python download_paper.py`): it fetches `arxiv.org/src/<id>`, extracts the `.tex` to `replication_target/source/` — local context only; the whole `replication_target/` is gitignored since v1.15.0 (the paper is copyrighted) — and prints any candidate recipe files.
- The full set of arXiv link forms the parser must accept (regression set): `https://arxiv.org/abs/<id>[vN]`, `/pdf/`, `/html/`, `/src/`, `https://doi.org/10.48550/arXiv.<id>`, `https://www.alphaxiv.org/{abs,overview,audio}/<id>`, bare `<id>[vN]`, and `arXiv:<id>`.
- **clawRxiv** (`cleanvibe/clawrxiv.py`): forms the parser must accept are `https://[www.]clawrxiv.io/abs/<id>`, `/api/abs/<id>`, and `clawrxiv:<id>`. A bare `<id>` is **not** clawRxiv (stays arXiv) — clawRxiv needs an explicit signal. Default clawRxiv smoke paper: `clawrxiv:2605.02609` (ROMO-CV). Live smoke: `python -m cleanvibe.cli replicate https://www.clawrxiv.io/abs/2605.02609 tests/scratch/replicating-clawrxiv` — confirm `replication_target/source/paper.md` (content) and `paper.json` (`source: clawrxiv`) land.
- **`replicate --batch FILE [--into DIR]` (2026-10-03).** `replicate.load_batch` reads JSON (a list or `{"papers": [...]}`, entries a ref string or an object with `ref`/`arxiv_id`/`url` + optional `path`; `docs/replication-examples/papers.json` loads as is) or text (one ref per line, `#` comments only at line start or after whitespace so URL fragments survive). `cli._do_replicate_batch` runs `cli._replicate_one` (the single-target dispatcher) for each entry with `os.chdir(DIR)` so default names and relative paths land there, always `no_claude=True`, `BATCH_DELAY_SECONDS = 3` between network refs (tests set it to 0), and catches `Exception`/`SystemExit` per paper so one failure doesn't stop the batch (exit 1 if any failed). Live smoke: a text file with `2605.20919` and `https://arxiv.org/abs/1706.03762`, run with `--into tests/scratch/batch-live`.
