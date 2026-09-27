# cleanvibe

**Website · [cleanvibe.emmaleonhart.com](https://cleanvibe.emmaleonhart.com)**

A tiny, zero-dependency Python CLI that starts a Claude Code session in a
git-tracked project and gets out of the way.

**cleanvibe 2** starts every project as an open-ended working session built to
**work from low information**. You might explain exactly what you want, drop a
few files in and say nothing, or not be at the computer at all (a scheduled job
or another agent can start the session). The agent works out what the project is
for from the chat, the files in the folder and the directory name. It writes its
read of the goal into `INTENT.md` and gets on with it. Every session's transcript
is saved into the repository, and sessions start with Remote Control on, so you
can pick them up from the Claude app or web.

## Install

```
pip install cleanvibe
```

### Developer install (working on cleanvibe itself)

```
git clone https://github.com/EmmaLeonhart/cleanvibe
cd cleanvibe
pip install .         # or use !dev-install.bat on Windows
```

**Use `pip install .`, not `pip install -e .`.** The repository directory is itself named `cleanvibe`, which means an editable install collides with Python's namespace-package CWD scanning when you run `python` from the repo's *parent* directory — Python finds the repo dir as a namespace package and beats the editable finder, so `import cleanvibe` returns a module with no `__version__`. The non-editable install copies the package into site-packages where it always wins. After any source edit, run `pip install .` again (or `!dev-install.bat`). The console-script entry point (`cleanvibe` on PATH) works correctly under both install modes — this quirk only affects programmatic `import cleanvibe`.

## Usage

### Start a project

```
cleanvibe                  # in a cleanvibe project: open a new session there
                           # anywhere else: create cleanvibe-YYYY-MM-DD/ here and open it
cleanvibe new              # create an auto-named project and open it
cleanvibe new ai-history   # create ai-history/ and open it
```

A new project gets a git repo on `main` (local and private, with no remote
unless you ask for one) and a Claude Code session in a new window. The session
starts with a first message that tells the agent how cleanvibe works: this is the
first session, the information may be thin, and the user may be away. When the
name was generated, the message says so, so the agent doesn't read meaning into
it.

`cleanvibe new NAME` on an existing cleanvibe project opens it instead of
touching it. On a non-empty folder that isn't a project it refuses (use
`cleanvibe legacy convert` to adopt a folder in place).

### What happens in the first session

1. The agent reads `CLAUDE.md` and **schedules a one-time intake 30 minutes out**
   (`CronCreate`).
2. It looks at what's already in the folder, writes a first read of the purpose
   into `INTENT.md`, and says briefly what it sees. If you're there and talking,
   it follows your lead; `AskUserQuestion` is only for when you are clearly
   present.
3. **At 30 minutes, the intake runs** (`.claude/scripts/data_lake_intake.py`):
   - commit 1 records the repository exactly as found ("the repository 30
     minutes in, before moving into data_lake/");
   - commit 2 `git mv`s everything that had never been committed (files you
     dropped in, new folders) into `data_lake/`;
   - it reports what moved and how much you've said in the chat.
4. The agent then **studies `data_lake/`** (a spec or brief in there is followed
   unless the chat says otherwise), updates `INTENT.md`, plans the work with the
   matching skill, and **starts the autonomous work loop**. If you said little or
   nothing, it starts right away; if you've been actively steering, it waits
   another hour (90 minutes in).

So you can create a project, drop a brief into it, and walk away.

### What a project contains

| Path | What it is |
|---|---|
| `CLAUDE.md` | How the project works: low-information operation, the data-lake rule, the intake |
| `INTENT.md` | The agent's running read of what you're trying to do, with evidence and confidence |
| `data_lake/` | The material the project works from, committed as part of its history |
| `sessions/` | Every session's transcript, raw `.jsonl` plus readable `.md` |
| `scratch/` | One-off scripts and downloads, gitignored so they don't pile up as crud |
| `.claude/skills/` | Practices the agent picks up when the work takes a shape (below) |
| `.claude/settings.json`, `.claude/hooks/` | The transcript hook |
| `.cleanvibe.json` | Marks the folder as a cleanvibe project |

There is no `queue.md`, `todo.md` or `devlog.md` at the start. The
`queue-driven-workflow` skill adds them if the work turns into building
something.

### Transcripts are kept in git

A hook (not the agent) copies the session transcript into `sessions/` after every
response and commits it at most once an hour and always when the session ends,
so the repository is an audit trail of the whole conversation. The readable
`.md` is what the agent reads to catch up in a later session.

### Sessions are real top-level sessions

A session started by an agent used to inherit that agent's identity
(`CLAUDE_CODE_CHILD_SESSION` and friends) and ran as its child, without its own
transcript. cleanvibe strips that before launching, so a session is its own
session no matter who started it. On Windows it opens in a new console that
outlives the caller; on macOS/Linux without a terminal it opens a new terminal
window. New project folders are marked trusted in Claude Code's config
(`~/.claude.json`, backed up first), so an unattended session doesn't stop at
"Do you trust this folder?".

### Skills

cleanvibe vendors these into every project's `.claude/skills/`:

| Skill | Used for |
|---|---|
| `queue-driven-workflow` | building software: `queue.md` → `devlog.md`, tests, CI |
| `research-practice` | research on any topic: sources, notes with citations, a living summary |
| `autonomous-loop` | long unattended stretches: three hourly crons (work, flush, status) that only you switch off |
| `writing-style` | prose without the "honestly" tic |
| `cron-is-local` | "cron" means a local `CronCreate` job |
| `emergency-stop` | "stop stop stop" halts everything |
| `cleanvibe-update-check` | weekly refresh of these skills from <https://cleanvibe.emmaleonhart.com/updates.md> |

The single source of truth is `cleanvibe/skills.py`. To back-fill them into an
older repo, run `migrate_repos_to_skills.py`.

### Replicate a paper

`cleanvibe replicate` takes a **clawRxiv** reference, an **arXiv/alphaxiv**
reference, a **plain URL** to non-arXiv research, **or** a folder name:

**From a clawRxiv paper (skill-first):**

```
cleanvibe replicate https://www.clawrxiv.io/abs/2605.02609
cleanvibe replicate clawrxiv:2605.02609
```

[clawRxiv](https://www.clawrxiv.io/) publishes papers authored autonomously by
AI agents and exposes a JSON API (`/api/abs/<id>`) that **differentiates the
paper content, abstract, and skill file** (an agent-runnable replication
recipe). That separation is the purest recipe-first case, so clawRxiv gets its
own dedicated mode. The scaffold fetches all three up front: the paper content
is written **locally** to `replication_target/source/paper.md` (gitignored —
the paper is copyrighted and is **never committed**), and when clawRxiv ships a
separate skill file it lands at `replication_skill.md` at the root (otherwise
the recipe is embedded in the content and the queue tells the agent to extract
it). A `download_paper.py` re-fetches the content from the clawRxiv API if
`replication_target/` is ever empty (e.g. a fresh clone). The generated
`queue.md`/`SKILL.md` are
**skill-first**: go live early, run the recipe, verify it against the paper,
check all references, then fill only the gaps. clawRxiv ids look arXiv-shaped,
so a bare id stays arXiv — use a `clawrxiv.io` URL or `clawrxiv:<id>` to select
clawRxiv mode.

**From an arXiv / alphaxiv paper:**

```
cleanvibe replicate https://arxiv.org/abs/1706.03762
cleanvibe replicate https://www.alphaxiv.org/overview/2201.02177
cleanvibe replicate https://doi.org/10.48550/arXiv.1706.03762
cleanvibe replicate 1706.03762v5
```

Any arXiv/alphaxiv id or URL is accepted — `/abs/`, `/pdf/`, `/html/`,
`/src/`, alphaxiv's primary `/overview/`, `/audio/`, `/forum/`, the arXiv
**DOI** form (`doi.org/10.48550/arXiv.<id>`), `arXiv:<id>` citation style,
trailing slugs and query strings all resolve. A pinned `vN` **version** is
preserved (recorded in `paper.json` and used for the download), not silently
dropped. This will:
1. Fetch the paper's metadata from the arXiv API (with **429-aware
   retry/backoff** — arXiv rate-limits, so requests honour `Retry-After`
   and back off rather than crashing)
2. Create `replicating-<paper-slug>/` (silently `-2`/`-3` if it already exists)
3. Scaffold a standalone replication project: cleanvibe conventions
   (`CLAUDE.md`, `queue.md`, `data_lake/`) **plus** the replication structure —
   `SKILL.md` (the agent-executable replication plan), `download_paper.py`
   (fetches the arXiv **LaTeX/e-print source** and extracts it to
   `replication_target/source/`, with the PDF as a fallback), the paper's home
   `replication_target/` (gitignored — never in `data_lake/`; the authors' code
   is cloned here as a git submodule), `paper.json`, and `.github/workflows/`
   that build a GitHub Pages findings site, a transportable PDF report, and a
   downloadable ZIP replication package
4. Initialize a git repo with an initial commit
5. Launch Claude Code inside the project

The generated scaffold is built around the **efficient, recipe-first path**:

- **Source, not HTML.** `download_paper.py` downloads the arXiv **e-print
  source** (`arxiv.org/src/<id>`) and extracts the `.tex` to
  `replication_target/source/`. The `.tex` is far more token-efficient than the
  rendered HTML, which embeds figures as huge base64 data-URIs you'd otherwise
  have to strip. **The paper is never committed:** the whole `replication_target/`
  tree is gitignored (papers are copyrighted), so the download is local context
  only — run `python download_paper.py` to (re)populate it whenever it's empty.
  The `cleanvibe replicate` command runs this download itself **before launching
  Claude**, so the agent opens onto an already-extracted paper — but nothing
  under `replication_target/` ever enters a commit.
- **Consent before running code.** Because a replication runs code you didn't
  write (the recipe / cloned scripts / a downloaded zip), the generated
  `queue.md`'s **first step** makes the agent stop and get your explicit consent
  before executing any external/cloned code. Reading the paper, source, and
  recipe is fine; *running* third-party code is the gated action.
- **Find the recipe FIRST.** Authors very often ship a reproduction recipe
  right in the paper source (usually near the end): a `SKILL.md`/`AGENTS.md`, a
  `reproduce.*`/`replicate.*`/`run.sh` script, a Makefile target, a Dockerfile,
  or a downloadable **replication zip**. The generated `queue.md`/`SKILL.md`
  tell the agent to find it (copying a recipe to `replication_skill.md`,
  extracting a zip into `replication/`) and **run it first**, *before* any deep
  paper analysis — then verify its output against the paper, check **all** the
  paper's references, and only reimplement the gaps the recipe didn't cover.
- **Go live early.** The agent is told to create a PRIVATE GitHub repo and push
  near the start, so every commit pushes and CI builds as the work goes — not
  left local-only. Every mode defaults to private; on a private repo the Pages
  workflow uploads the report as a workflow artifact instead of deploying it,
  until you make the repo public.
- **Themed report with a status badge.** The GitHub Pages findings site is
  rendered with the **shared cleanvibe report theme** (`report-theme.css` — the
  same warm "paper" + dark-mode theme `cleanvibe legacy research` uses) and topped with
  a big color-coded **replication status badge** — 🟢 replicated / 🔴 failed /
  🟠 insufficient hardware / 🔵 in progress — driven by a `status` field in
  `paper.json` (defaults to in-progress). A transportable PDF is built too.

**From a plain URL (research that isn't on arXiv):**

```
cleanvibe replicate https://some-lab.org/papers/cool-thing.pdf
cleanvibe replicate https://openreview.net/forum?id=XXXX
```

When the argument is a plain `http(s)` URL that isn't an arXiv/clawRxiv
reference, cleanvibe **downloads it** as the replication source — the page or
PDF lands **locally** in `replication_target/source/` (`paper.pdf` or
`paper.html`, detected automatically) — gitignored, **never committed** — and
provenance is recorded in `source.json`. A `download_paper.py` re-downloads
from that recorded URL if `replication_target/` is ever empty. Same 429-aware
retry/backoff as arXiv mode. Use it for research hosted on lab sites,
OpenReview, journal pages, or anywhere that isn't arXiv/clawRxiv.

**From a folder you fill yourself (manual drop-in mode):**

```
cleanvibe replicate my-paper-replication
```

When the argument is **not** an arXiv/alphaxiv reference (and not a URL) it is
treated as a folder name and a *manual drop-in* project is scaffolded — no
metadata
fetch, no `download_paper.py`, no `paper.json`, no network. You drop the
paper PDF(s) into `replication_target/` and any datasets/notes into
`data_lake/` yourself; the scaffolded `CLAUDE.md` / `queue.md` / `SKILL.md`
/ `README.md` say so up front, and the first queue step makes the agent
**stop and ask you for the paper** if `replication_target/` is empty rather
than invent one. Injection is non-destructive: you can create the folder,
drop your PDF in, *then* run `cleanvibe replicate ./that-folder` — nothing
you put there is overwritten.

Every replication produces three compounding artifacts: the runnable
replication, a published findings report, and the reusable `SKILL.md`
methodology. See `docs/replication_framing.md` for the full vision.

### Doctor — audit a project for drift

```
cleanvibe doctor            # audit the current directory
cleanvibe doctor path/to/project
```

A **read-only** check of a cleanvibe project for the drift that builds up over
time. It changes nothing, and exits `1` if it finds anything (so it can run in CI):

| Check | Flags |
|---|---|
| `files` | a missing `CLAUDE.md`, `README.md`, `queue.md`, or `devlog.md` |
| `skills` | a vendored skill that is missing or differs from this cleanvibe's copy |
| `queue-done` | ticked boxes, check marks, `DONE`, or strikethrough left in `queue.md` |
| `version` | `queue.md`'s "Current version" not matching `pyproject.toml` |
| `devlog-tags` | a `v*` git tag with no `devlog.md` entry |
| `section-refs` | a reference to a `CLAUDE.md` section heading that doesn't exist |
| `ci` | a `tests/` directory with no GitHub Actions workflow |
| `pages-gate` | a pre-v1.18.0 Pages workflow that fails on a private repo |

### Options

```
cleanvibe --dry-run                       # Preview what bare `cleanvibe` would do here
cleanvibe new NAME --dry-run              # Preview a new project
cleanvibe new NAME --no-claude            # Create it without launching Claude
cleanvibe replicate URL --dry-run         # Preview a replication scaffold
cleanvibe doctor                          # Audit the current project for drift (read-only)
cleanvibe legacy research NAME --dry-run  # Preview a 1.x mode (prints a deprecation warning)
cleanvibe --version                       # Show version
```

## Legacy modes (deprecated)

The cleanvibe 1.x modes still work as `cleanvibe legacy <cmd>`. Each run prints a
`DEPRECATED` warning; they are no longer developed. Their old top-level names
(`cleanvibe research`, …) now just point here. The cleanvibe 2 default covers most
of what they did: it starts from whatever you give it and picks up development or
research practices as skills. All of them create private repos, and their
sessions start with a first message explaining the mode.

### `legacy new` — the 1.x bootstrap project

```
cleanvibe legacy new my-project
```

This will:
1. Create the directory `my-project/`
2. Write `CLAUDE.md` (a short pointer to the skills + project-specific notes)
3. Write `README.md` (starter documentation)
4. Write `queue.md` (active work queue, pre-seeded with a first-session bootstrap sequence that walks Claude through triaging dropped-in files, inferring the project, interviewing the user, creating `todo.md`, populating the real queue, and pushing to a private GitHub repo)
5. Write `devlog.md` (where "done" lives) and `.gitignore` (sensible Python defaults)
6. Create `data_lake/` (drop files in before the first session) and, on Windows, `!runClaude.bat`
7. Vendor `.claude/skills/` (the workflow skills; see Skills above)
8. Initialize a git repo on `main` with an initial commit
9. Launch Claude Code inside the project, with the 1.x `new` starting prompt

### Research a question — your own investigation

```
cleanvibe legacy research reservoiragent
cleanvibe legacy research reservoiragent --question "What is the memory capacity of a reservoir-computing agent?"
cleanvibe legacy new reservoiragent --research      # equivalent alias
```

`research` is for an **original-research project** — *your own* investigation,
not a [replication](#replicate-a-paper) of someone else's paper. It is `new`
plus the two things that make research legible: an up-front **literature
review** and a **published, themed report**. It scaffolds everything `new`
does (`CLAUDE.md`, `README.md`, `queue.md`, `devlog.md`, `.gitignore`,
`data_lake/`, the three-cron playbook) and adds:

- **`literature/`** — the literature review, built *before* any code. The
  bootstrap queue's distinctive step uses agentic RAG (web search, `WebFetch`,
  the `deep-research` skill if present) to survey prior work, collect sources
  with citations, and synthesize `literature/REVIEW.md` (what's known, the
  gaps, what *this* project adds). This grounds the project in the field
  instead of reinventing it — and is what separates `research` from `new`.
- **`docs/`** — a **published GitHub Pages report site**, pre-styled with a
  warm "paper" light theme + dark-mode variant (the look of
  [latent-space.emmaleonhart.com](http://latent-space.emmaleonhart.com/)), plus
  a transportable PDF built from `FINDINGS.md`. `.github/workflows/pages.yml`
  deploys it. The agent edits the content; the theme stays.

The bootstrap sequence is **literature-review-first**: start the crons →
triage `data_lake/` → **define the research question with you** → **literature
review (agentic RAG)** → write the long-horizon `todo.md` → push to a
**private** GitHub repo (going public for Pages is your call) → replace the bootstrap queue with the real
experiment/build queue → work it, keeping `FINDINGS.md` + the `docs/` report
current. Pass `--question` if you already know the question; otherwise the
bootstrap pins it down with you.

### Original research — when you don't have a topic yet

```
cleanvibe legacy original driftprobe
cleanvibe legacy original driftprobe --area "reservoir computing"
cleanvibe legacy new driftprobe --original                          # equivalent alias
```

`original` is `research` for an **uncertain topic**: you don't yet have a fixed
research question. It keeps everything `research` has — `literature/`,
`data_lake/`, the three-cron playbook, the themed `docs/` report — and prepends
one distinctive bootstrap step:

- **`topics/`** — the **topic-finding loop**, run *before* the literature review.
  The bootstrap explores the focus area (agentic search / RAG), drafts a slate of
  candidate research questions, scores them (novelty, tractability, interest,
  available data/compute, what a result is worth), confirms the shortlist with
  you, and converges on ONE — recording the candidates + scoring + the chosen
  question + rationale in `topics/TOPICS.md`. Then it proceeds exactly like
  `research`.

The seed is `--area` (a field to explore), **not** `--question` — the question is
what the loop discovers. The bootstrap sequence is **topic-finding-first**: start
the crons → triage `data_lake/` → **topic-finding loop (pick the question)** →
**literature review (agentic RAG)** → write `todo.md` → push to a **private** repo → replace
the bootstrap queue → work it. Use `original` when you want to investigate *some*
area but haven't settled on the precise question; use [`research`](#research-a-question--your-own-investigation)
when you already know what you're asking.

### Chat — a git-tracked conversation

```
cleanvibe legacy chat                                   # -> chat-YYYY-MM-DD/
cleanvibe legacy chat tea-notes --topic "oolong vs pu-erh"
```

`chat` is for a **conversation about one topic** rather than a software project:
research-heavy, light on code, kept in a **private** git repo so you can resume,
search and share it. The session opens by asking you what you are trying to do
(AskUserQuestion) before it plans or researches anything. Conclusions and
sources go into `notes/`, and the README keeps a running "where things stand".

**Session logs are git-tracked.** The scaffold's `.claude/settings.json` runs a
small stdlib script (`.claude/hooks/save_session_log.py`) after every response
and at session end. It copies the transcript into `sessions/` as raw `.jsonl`
plus a readable `.md`, and commits only `sessions/`. At session end it also
pushes if the repo has a remote. Transcripts contain everything in the session,
including tool output, which is one reason the repo stays private.

**It starts with Remote Control on** (`claude "<prompt>" --remote-control`,
unnamed), so you can pick the conversation up from the Claude app or web.
`!runClaude.bat` does the same. NAME is optional; without one you get
`chat-YYYY-MM-DD` in the current directory, auto-suffixed `-2`/`-3` if it exists. Chat mode has no three-cron
playbook and no Pages report.

### Clone an existing repo — codebase onboarding

```
cleanvibe legacy clone https://github.com/user/repo
```

`clone` is for **onboarding an existing codebase**, not bootstrapping a blank
one. It is deliberately different from `new`:

1. `git clone` the repository
2. Create and check out a dedicated `cleanvibe-onboarding` branch — **the
   default branch is left untouched**
3. *Prepend-or-write* an onboarding `CLAUDE.md` and `queue.md`: if the repo
   already has them, the fresh block goes on top (newest first) and the
   original content is preserved below — re-running just layers another block
4. Inject `.gitignore` only if missing. **No `data_lake/`** (it is a real
   codebase, nothing was dropped in) and **no README overwrite**
5. Commit the onboarding scaffold on the branch
6. Launch Claude Code inside the project

The onboarding `queue.md` is small and focused: read & document the repo,
make existing docs accurate, **rewrite `CLAUDE.md` to the repo's real
development practices**, add tests/CI if sparse, then synthesize any existing
planning artifacts and hand off to the repo's own `todo.md`.

## Why?

Most sessions don't start with a well-defined goal, and a rigid scaffold that
assumes one ends up being fought rather than used. cleanvibe 2 assumes as little
as possible up front and makes the agent do the work of figuring out the goal,
from the chat when you're there and from what's in the folder when you're not.
It keeps two things fixed: everything is committed (including the transcript),
and the agent writes down what it thinks you want (`INTENT.md`), so you can
check and correct it.

## Cross-platform

Works on Windows, Linux, and macOS. Zero dependencies beyond Python 3.9+. On
Windows a session opens in its own console window; on macOS/Linux it takes over
your terminal, or opens a new terminal window when there isn't one (for example
when an agent runs cleanvibe).

## Website

Full walkthrough at the project site (built from `pages/` and deployed by GitHub
Actions): **https://cleanvibe.emmaleonhart.com/**

## Stability

cleanvibe 2.0.0 is a new major version: the default `cleanvibe` / `cleanvibe new`
behavior changed, and the 1.x modes moved under `cleanvibe legacy`. Within 2.x:

- **Commands:** `cleanvibe`, `new`, `replicate`, `doctor` and `legacy` are
  stable. `replicate` behaves exactly as in 1.x. The `legacy` modes keep working
  but are frozen.
- **A new project always has:** `CLAUDE.md`, `README.md`, `INTENT.md`,
  `.cleanvibe.json`, `.gitignore` (with `scratch/`), `sessions/`, `data_lake/`,
  `.claude/settings.json`, `.claude/hooks/save_session_log.py`,
  `.claude/scripts/data_lake_intake.py` and the vendored skills, in a git repo on
  `main` with no remote.
- **Non-destructive:** `new` never overwrites an existing project (it opens it)
  and refuses a non-empty folder that isn't one. `replicate` and the legacy modes
  keep their 1.x guarantees (`clone`/`convert` never overwrite; the replication
  paper is never committed).
- **Template wording** may evolve; the file set and command contracts above are
  what 2.x holds stable.
- **Zero runtime dependencies** remains a hard guarantee.

## License

MIT
