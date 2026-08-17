# The routines

Most of the commits on `main` were not written by a person. They were written by
scheduled cloud agents — "routines" — that ran hourly, unattended, and merged
their own pull requests. Twenty-nine of them were pointed at this repository
across five weeks, and **every one of them is switched off.** Verified
2026-08-17 by calling the routines API once per trigger ID: all 29 return
`enabled: false`.

**Their prompts are not in this repository.** They live in the claude.ai
routines API and are edited there, which means the single most consequential
configuration in this project is invisible to anyone reading it. This file is
the repository's record of what they are, what they were told, and — now that
they are paused rather than gone — what re-enabling one would do. It is written
by hand and can drift from the API; where the two disagree, the API is what
actually runs, and `RemoteTrigger {action: "get"}` is how you read it.

## Nothing external is running, and the log shows when it stopped

The pauses came in clusters, each one a scripted sweep rather than a series of
clicks:

| Disabled (UTC) | What was switched off |
|---|---|
| `2026-07-27T13:15Z` | the 7 `Design system —` section lanes |
| `2026-07-28T15:25–18:18Z` | the 4 `Root —` prototype lanes |
| `2026-08-03T06:45Z` (±11 s across 8 triggers) | the 5 `Landing —` lanes and the sweep, the 5 `Pages —` lanes, and `System design & pages` |
| `2026-08-04T06:19Z` (±13 s across 5 triggers) | the 5 browser-compat lanes |
| `2026-08-12T05:06Z` | `Website 4.0 Feedback` |

Commit volume followed. It peaked at roughly **145 commits a day** on
2026-07-27, when the section and landing generations overlapped; it now runs
**3–12 a day**, and those are interactive sessions and the Notion sync.

**What is left is entirely inside the repository.** `news-sync.yml` — display
name *Content from Notion* — holds an hourly cron at `:25`. It imports the news
archive and the vacancy register from Notion into `content/news/` and
`content/jobs/`, runs `sh scripts/build-all.sh`, commits to
`routine/system-pages-notion-YYYYMMDD-HHMM`, pushes, and calls
`routine-merge.yml` as a reusable workflow to gate and land it. Everything else
on `main` arrives as an interactive `claude/*` session pull request. The remote
carries no `routine/*` and no `automation/*` branches at all any more.

The cron's own comment still says it sits *"between the routines' `:11` and
`:39`"*. Both of those neighbours are disabled; the `:25` slot is now simply
where it fires.

## The roster, by generation

This table exists so that the next audit is an API loop over 29 IDs instead of
transcript archaeology. It has to exist, because the API cannot enumerate them:
`GET /v1/code/triggers` returns only the **newest 20** with `has_more: true`,
and the `RemoteTrigger` tool ignores the cursor for `list` — both pages of the
2026-08-17 sweep hashed identically (`7dc4cfd8acff…`). Everything older than the
newest twenty is reachable **only by ID**. Keep the IDs below accurate; they are
the point of the table.

**Seven `Design system —` section lanes, created 2026-07-24.** The first
generation, one lane per chapter of the design system. Their branch suffixes
were never recorded here; all of them push under `routine/`, which matters — see
the queue-clearing hazard below.

| Lane | Fires (UTC) | Trigger ID | Branch prefix | Subject | Disabled |
|---|---|---|---|---|---|
| `Design system — gradients` | `:01` | `trig_0162L71z1q48H9McX4Bf6d8p` | `routine/…` | the gradient family | 2026-07-27 |
| `Design system — illustration` | `:09` | `trig_01JqBFWqYANVMRzSHSVrJBfe` | `routine/…` | illustration form | 2026-07-27 |
| `Design system — harmony` | `:17` | `trig_01Kr8fVoqh7E1fRxmZogZrzW` | `routine/…` | cross-page harmony | 2026-07-27 |
| `Design system — vision` | `:25` | `trig_01P9iMQqT2VpLdYn5ezJLQTE` | `routine/…` | the design vision | 2026-07-27 |
| `Design system — glass` | `:34` | `trig_019Z3FxRtU37rtcoqo8i9VSa` | `routine/…` | Glas surfaces | 2026-07-27 |
| `Design system — grid` | `:43` | `trig_0155VBZFoh86WihZb1mjoSq3` | `routine/…` | the grid | 2026-07-27 |
| `Design system — components` | `:51` | `trig_011qN43SYQeQkF9qg8GfaXNv` | `routine/…` | the component specimens | 2026-07-27 |

**Five `Pages —` lanes, created 2026-07-27.** The Patterns section as a whole,
split by kind of fault. Branches `routine/pages-<lane>-YYYYMMDD-HH`; each run
ended with `gh pr merge --squash --delete-branch`.

| Lane | Fires (UTC) | Trigger ID | Branch prefix | Subject | Disabled |
|---|---|---|---|---|---|
| `Pages — links` | `:07` | `trig_01BT5xmLFzS7AwKcPJuKTE9S` | `routine/pages-links-*` | links and navigation (renamed from *Design system — Pages (Patterns) routine*) | 2026-08-03 |
| `Pages — build` | `:19` | `trig_019HDJG4P9RS3yvj4twEk3dj` | `routine/pages-build-*` | build-out of unfinished pages | 2026-08-03 |
| `Pages — style` | `:31` | `trig_019jEGBNZVWLQ4MQVGCLuTCH` | `routine/pages-style-*` | style drift | 2026-08-03 |
| `Pages — responsive` | `:43` | `trig_01Scj3kWZ7Td9AMJq8ijvk5w` | `routine/pages-responsive-*` | the width ladder | 2026-08-03 |
| `Pages — bugs` | `:55` | `trig_01Kr3PASimfxBEsTnL8iLBQV` | `routine/pages-bugs-*` | bugs | 2026-08-03 |

**Five `Landing —` lanes, created 2026-07-27, plus a sweep added 2026-07-29.**
These are the ones this file used to describe as *what is running*. Their sole
subject was `design-system/patterns/landing-page.html`. Branches
`routine/landing-<lane>-YYYYMMDD-HH`.

| Lane | Fires (UTC) | Trigger ID | Branch prefix | Subject | Disabled |
|---|---|---|---|---|---|
| `Landing — seams` | `:03` | `trig_01Cvz78a4PMzB2nRDdX3tCs4` | `routine/landing-seams-*` | overlaps, corners, free line ends, the z-ladder, section seams | 2026-08-03 |
| `Landing — motion` | `:15` | `trig_01KGRKDqW5obbTDtHPMDDEvk` | `routine/landing-motion-*` | scroll choreography, ranges, fill-modes, both directions | 2026-08-03 |
| `Landing — craft` | `:27` | `trig_012SHvkV3yGBdR4SQtxT92R2` | `routine/landing-craft-*` | composition, spacing, type, copy, states, illustration form | 2026-08-03 |
| `Landing — responsive` | `:39` | `trig_01PUX7y3dc55b8Le5qDEYvnn` | `routine/landing-responsive-*` | the width ladder, the pin gate's edges, heights | 2026-08-03 |
| `Landing — quality` | `:51` | `trig_01SdfdR3PmvvGGuijAdTLiRp` | `routine/landing-quality-*` | console, degraded states, keyboard, contrast in situ, weight | 2026-08-03 |
| `Landing — sweep` | `:57` | `trig_014qfZoCJizgu3j29RUuY9py` | `routine/landing-sweep-*` | whole-page sweep (created 2026-07-29) | 2026-08-03 |

**Four `Root —` prototype lanes, created 2026-07-28.** Subject:
`design-system/prototypes/statement-to-process.html`. They lived less than a
day. The verification lane greps `landing-page.html` for
`lp-flow|lp-frame|cf-pin|lp-hold|cf-stmt-collapse` and **reverts any hit** — it
exists to keep prototype work out of the shipping page.

| Lane | Fires (UTC) | Trigger ID | Branch prefix | Subject | Disabled |
|---|---|---|---|---|---|
| `Root — geometry` | `:09` | `trig_017V9xTT8xDW72TqrUB7nNRG` | `routine/root-geometry-*` | the prototype's geometry | 2026-07-28 |
| `Root — hold` | `:21` | `trig_01Kum6aFqP1B5LGstdWZhsNu` | `routine/root-hold-*` | the hold and the pin | 2026-07-28 |
| `Root — clutter` | `:33` | `trig_01LW4C5WFNc5i1nF2ETbfwVB` | `routine/root-clutter-*` | clutter removal | 2026-07-28 |
| `Root — verification` | `:45` | `trig_01F4s7LhY5v7t7SFxkLXVhG8` | `routine/root-verify-*` | reverts prototype classes that reach `landing-page.html` | 2026-07-28 |

**`System design & pages`, created 2026-07-30 from inside a Claude Code
session.** The first that did not fire into `landing-page.html`, and the reason
`.github/workflows/routine-merge.yml` exists.

| Lane | Fires (UTC) | Trigger ID | Branch prefix | Subject | Disabled |
|---|---|---|---|---|---|
| `System design & pages` | `:11` | `trig_019yN4QpyQZFjh1JEKtt2GEL` | `routine/system-pages-*` | `design-system/**` — the chapters, the four stylesheets, the checkers — and every page in `patterns/` except `landing-page.html` | 2026-08-03 |

Its session holds **git and nothing else**: no `gh`, no GitHub API. It reads
`.github/ROUTINES.md` and `design-system/README.md` at the start of every run,
is forbidden to touch `.github/workflows/deploy.yml`, serves the tree with
`python3 -m http.server 8765`, drives Chromium at
`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`, and signs its commits
`Co-Authored-By: Claude Opus 5`.

**`Website 4.0 Feedback`, created 2026-08-03.** Works a queue instead of a
subject area.

| Lane | Fires (UTC) | Trigger ID | Branch prefix | Subject | Disabled |
|---|---|---|---|---|---|
| `Website 4.0 Feedback` | `:35` | `trig_011Hproom5KM5PTmXtew4Apd` | `routine/feedback-<slug>-*` | the Notion feedback queue, data source `collection://3b12e8e3-9877-80a9-87f6-000b5ec2c3d6` | 2026-08-12 |

Draft pull requests only. **It never merges anything**, and it is the only
`routine/*` prompt that knows the site is generated: it runs
`python3 scripts/build-site.py` and its `--check`.

**Five browser-compat lanes, created 2026-08-03.** A second branch-prefix
family — `automation/<engine>-YYYYMMDD-HHMM`, not `routine/*` — which is why
`routine-merge.yml` never sees them.

| Lane | Fires (UTC) | Trigger ID | Branch prefix | Subject | Disabled |
|---|---|---|---|---|---|
| `Browser compat — Chrome` | `:03` | `trig_01VEeqU36XkfNUkJMog5zjBT` | `automation/chrome-*` | Chrome rendering | 2026-08-04 |
| `Browser compat — Firefox` | `:15` | `trig_01AWwhMXzs7KTx4hHqZSnXkd` | `automation/firefox-*` | Firefox rendering | 2026-08-04 |
| `Browser compat — Edge` | `:27` | `trig_012bu9sYyPUUsMdLAS1P111C` | `automation/edge-*` | Edge rendering | 2026-08-04 |
| `Browser compat — Safari` | `:39` | `trig_01QGcBPsiQPsZc5RxTAC25Hu` | `automation/safari-*` | Safari / WebKit rendering | 2026-08-04 |
| `Browser compat — Mobile` | `:51` | `trig_01BxsVfhHs5RAA2NWndhontp` | `automation/mobile-*` | mobile engines | 2026-08-04 |

One roster caveat, stated so nobody mistakes this table for proof: it was
reconstructed from persisted tool output and session transcripts and then
verified ID by ID. A trigger created in the one unobserved window
(2026-08-04 06:19Z → 23:43Z) or from another device would be invisible to that
method. The *PR integrator — audit, de-conflict, merge* routine that
`memory/design-routines-self-merge.md` refers to was never located by ID at all;
memory records it as paused. An eyeball of <https://claude.ai/code/routines> is
the only way to close that gap.

## They cannot be deleted — only paused, or rewritten

`RemoteTrigger` offers `list`, `get`, `create`, `update`, `run`,
`create_webhook_trigger`, `list_runs` and `get_run_log`. **There is no delete
action.** A routine you are finished with can be switched off or have its prompt
replaced, and that is all; the object itself is permanent, and so is the switch
next to it.

`update` does partial updates, which is how the pauses above were made: eight
triggers landing inside eleven seconds, and five inside thirteen, are a script,
not a person working through a list. The same mechanism is available for
retirement — prepending a `HALT: this brief predates the current repository; do
nothing and exit` line to a prompt survives someone toggling `enabled` back on,
which the flag itself does not.

## Re-enabling one unedited would ship nothing, or merge everything

**Eighteen of the twenty-nine prompts predate the `build-site.py` generation
flip.** The seven section lanes, the five Landing lanes and the sweep, the five
Pages lanes and the four Root lanes were all written when the root HTML was
hand-authored. They assert *"Static site, no build step"*, they instruct the
session to leave the outgoing generation alone and name
`dienstleistungen.html` and `energie.html` among the root files to avoid — both
of which no longer exist — and **not one of them runs
`scripts/build-site.py`**. The root pages are now generated from the very
patterns these lanes edit, so a run would change a pattern, regenerate nothing,
and fail `build-site.py --check` with a brief that contains no instruction
capable of satisfying it. The lane cannot fix what it does not know about.

**Worse, the seven section prompts from 2026-07-24 open with a step called
CLEAR THE QUEUE.** It lists every open pull request, and every one whose branch
starts with `routine/` is *"yours to LAND, not to review"* — checkout, rebase,
`gh pr merge --squash --delete-branch`, after a render sanity check and nothing
else. They predate `design-system.yml` entirely; there was no CI in the
repository when they were written, so their briefs mention no gate. An
accidental re-enable during a restructure would bulk-merge whatever happens to
carry that prefix, including branches these lanes have never heard of.

**If any routine is ever revived, revive only the two youngest generations.**
`Website 4.0 Feedback` runs `build-site.py` and its `--check`, opens draft pull
requests, and never merges. The five browser-compat lanes know the root pages
are generated, run `build-site.py` and `scripts/check-runtime.py`, derive the
check list by grepping `.github/workflows/design-system.yml` for
`python3 scripts/…py( --check)?` instead of hardcoding a count, gate their merge
on the *"Design system checks"* run reaching completed/success, and self-throttle
— two of the last three `automation/<engine>-*` pull requests closed unmerged and
the lane stops. Those five habits are the difference between a prompt that ages
and one that does not. The other twenty-two should be retired with a HALT header
rather than left as they are, since deleting them is not on offer.

## The strings the prompts hardcode

The prompts live outside the repository, so a rename here leaves the old string
alive there, verbatim, one toggle away from running. Anyone renaming something on
this list is renaming half of a contract:

- **Paths.** `design-system/patterns/` and `landing-page.html` — named in the
  briefs and string-keyed inside dozens of checks. Specimen pages under
  `design-system/components/`; rules pages under
  `design-system/foundations/{motion,layout,mobile,materials,colors,geometry,illustration}.html`.
  `design-system/prototypes/statement-to-process.html` for the Root lanes.
- **The four stylesheet names.** `design-system/assets/css/tokens.css`,
  `base.css`, `components.css` are named as what ships; the sweep and
  browser-compat lanes add `acts.css`. `docs.css` and `preview.css` are named as
  what never ships. `tokens.css`'s *THE BREAKPOINT REGISTER* comment is paired
  with `foundations/layout.html` by `check-breakpoints.py`.
- **`scripts/check-*.py` and the wiring convention.** The glob is the merge
  gate, and a new check is expected to be wired into
  `.github/workflows/design-system.yml` as its own step. Named individually in
  prompts: `check-gradient-family.py`, `check-flow-handover.py`,
  `check-void-departure.py`, `check-flow-chain.py`, `check-seam-anchor.py`,
  `check-breakpoints.py`, `check-grid-tracks.py`, `check-contrast.py`,
  `check-glass-budget.py`, `check-iso-motion.py`, `check-overflow-clip.py`,
  `check-figure-fits.py`, `check-flow-label-law.py`, `check-fallback-tier.py`,
  `check-anchor-positioning.py`, `check-anchor-position-cascade.py`,
  `check-rem-floor.py`, `check-scrub-rate.py`, `check-mobile-coverage.py`,
  `check-touch-floor.py`, `check-idle-motion.py`, `check-runtime.py`,
  `gen-stmt-field.py`.
- **Branch prefixes.** `routine/system-pages-**` is a **three-way contract** —
  `routine-merge.yml`'s push filter (line 43), `news-sync.yml`'s branch naming
  and its `workflow_call` handoff, and the `:11` prompt's own
  `routine/system-pages-$(date -u +%Y%m%d-%H)`. All three move together or none
  of them do; a miss strands branches silently, which is exactly the 2026-08-07
  incident recorded below. Then `routine/landing-<lane>-*`,
  `routine/pages-<lane>-*`, `routine/root-<lane>-*`,
  `routine/feedback-<slug>-*`, and the second family `automation/<engine>-*`.
- **Workflow display names, not filenames.** *"Deploy to GitHub Pages"* is
  dispatched by name and named in the older prompts as the publish mechanism;
  *"Design system checks"* is the literal merge gate of the browser-compat
  lanes; *"Content from Notion"* is named in prompts and watchdogs. Renaming a
  `name:` breaks these — fail-closed for the merge gate, fail-stale for the
  publish claim.
- **Content directories.** `content/news/` and `content/jobs/`, which the Notion
  sync owns and the generated regions are built from.
- **Environment facts.** Chromium at
  `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`;
  `/usr/local/bin/python3.12` (some Root prompts hardcode it, because
  `check-seam-anchor.py` needs 3.12); `python3 -m http.server` on 8000, 8765 and
  8899; `npm i playwright@1.62.0`; the Notion data source
  `collection://3b12e8e3-9877-80a9-87f6-000b5ec2c3d6`. And the repository itself,
  `control-f-io/control-f-website`, with `main` as the base.

**Every count in every prompt is stale.** The check totals they quote range from
*"the existing nine checks"* (the Pages lanes) through 64, 66, 73 and ~75 to
*"~109 gate scripts"* (the browser lanes), against 117 files today. Only the
browser lanes derive the list rather than quoting a number, which is the pattern
any surviving prompt should adopt.

## A token holds no events, and two incidents proved it

**`GITHUB_TOKEN` raises no events.** A push or a pull request made with the
workflow token starts no other workflow. It is a single rule with a wide blast
radius, and the current design routes around it in three hand-built ways.

**That is why `.github/workflows/routine-merge.yml` exists.** The five Landing
lanes were created from the routines UI and their sessions hold a GitHub
connector, so `gh` and the API were theirs. A routine created from inside a
Claude Code session cannot inherit that connector — the create call says so —
and its sessions come up with git and nothing else. Git can push a branch and
cannot raise a pull request, so `:11` would have stopped one step short of
`main` every hour. The workflow closes that step from inside the repository,
where it needs nobody's token: a push to `routine/system-pages-**`, or a
`workflow_call` naming the branch, runs the gate and squash-merges into `main`
with the branch's own commit message. A failing gate merges nothing and leaves
the branch standing, with the reason in the job summary and on the pull request
if there is one.

**The gate is run there rather than waited for**, because a pull request opened
with `GITHUB_TOKEN` never starts `design-system.yml` — waiting for a check that
will not start waits forever. It runs every `scripts/check-*.py` by glob, so a
check written later is enforced by existing, and **it now also runs the six
builders' `--check`** in `build-all.sh` order: `build-news`, `build-jobs`,
`build-i18n`, `build-articles`, `build-stellen`, `build-site`. That second part
is new, and it was bought with a deploy. While those six lived only in
`design-system.yml`, a branch that changed German copy without adding the pair
to `design-system/i18n/en.json` passed this gate, self-merged, and only then
went red — on `main`, and again in `deploy.yml`, which runs `build-i18n.py` in
write mode before it uploads and exits 1 on the missing entry. The site stops
deploying, both editions, every page, until the catalogue is repaired by hand.
An unattended merge has to assert what the deploy will assert.

**It merges with git and not with `gh`.** `gh pr create` answered *"GitHub
Actions is not permitted to create or approve pull requests"* on the run that
imported the Stellen register, so the merge is git's and the pull request is
attempted and skipped when refused. What is lost is the pull request as a
record; the commit message carries it instead, which is also why a routine's
**commit message is its PR body** — `gh pr create --fill` takes both from the
commit, so what a run measured has to be written there.

*Note on that setting:* it now reads **on**. The API reports
`can_approve_pull_request_reviews: true` for this repository as of 2026-08-17,
so the rationale in `routine-merge.yml`'s comment block — "it is off here" — is
stale. No bot-authored pull request has ever actually succeeded here, so nothing
has been re-tested; the step still tries and carries on, and the day it starts
working the only change is that the record comes back.

**And it dispatches both deploys by name**, which is also new. The merge is
pushed with `GITHUB_TOKEN`, so no push event follows it and neither deploy would
start on its own. `workflow_dispatch` is one of the two event kinds the token
may raise, so the loop names *"Deploy to GitHub Pages"* and *"Deploy the
Worker"*. Before it named the second one, the Cloudflare copy sat at the
previous user-credential push after every merge that came through here —
measured on the three Notion syncs of 2026-08-13: stale for 42 minutes, 2 hours
38 minutes, and 16 minutes, until an unrelated human merge raised a push event
and carried the content over by accident. Pages is the serving origin today, so
the cost was invisible; the day the DNS cutover makes the Worker the site, an
hourly import that never reaches it is the whole pipeline failing quietly.

**The other incident is the same rule on a push.** `news-sync.yml` pushes with
`github.token`, so its branches raise nothing. Measured on 2026-08-07:
`routine/system-pages-news-20260807-2155` was pushed at 21:55 with ninety-six
files of imported archive on it, zero runs started against that ref, and it sat
on the remote until a person opened the pull request by hand. `news-sync.yml`
therefore **calls** the gate as a reusable workflow and hands it the branch
name; `routine-merge.yml` reads `inputs.branch` when it is called and the pushed
ref when it is not, so both entrances gate identically.

Any new automation that pushes or merges has to copy one of those three
patterns, or it will silently do nothing downstream.

## What every one of them was told

The instructions differ by lane, but these are common, and they are why the
commit log reads the way it does. They are also still the live text of 29
prompts, so this is a description of what would resume, not only of what
happened:

- **A run that ships nothing is a failed run.** "Nothing needed doing" is
  explicitly defined as failure. This was deliberate and it had a cost: it
  guarantees motion, not that every change is worth making.
- **Look, do not only measure.** Every lane must render with Playwright and
  *read the screenshots*. The faults that prompted these routines — overlaps,
  broken corners, an animation that had finished before the reader arrived —
  were all found by eye and were all invisible to a DOM sweep.
- **Stay in your lane.** Out-of-lane findings go in the PR's audit section for
  another lane to pick up, rather than being fixed in passing.
- **The commit subject is a full sentence stating the finding**, not a label.
  `git log` is the design system's changelog and reads as one.
- **Write the invariant into CI.** When a lane finds a rule that is true
  everywhere, stated nowhere, and countable in a file, it writes a
  `scripts/check-*.py`, wires it into `design-system.yml`, and proves it fails
  on a reintroduction. Every check in that directory started as a bug that had
  already shipped twice. There are 117 of them now, and they are still
  enforcing with every lane switched off — that is the durable half of this
  whole arrangement.
- **Never weaken a check to make a change pass.**
- **The news archive is not markup you edit.** `design-system/patterns/news.html`
  has four regions fenced by `<!-- news:… -->` comments — the cards, the year
  axis, the counters and the pagination — and `scripts/build-news.py` writes
  them from `content/news/`, one file per post. A lane that edits inside those
  fences has its work overwritten by the next build and fails
  `build-news.py --check` in the meantime. Everything outside them, including
  the composition notes and the topic chips, is authored as usual.
- **Nor is the vacancy register.** `patterns/karriere.html` has two regions
  fenced by `<!-- jobs:… -->` — the entries and the count in the page header —
  and `scripts/build-jobs.py` writes them from `content/jobs/`, one file per
  opening. `patterns/karriere-stelle.html` is the template the job pages are
  spliced from and carries a *Musterausschreibung* rather than a real opening:
  two pages with one JobPosting is the duplicate `check-job-posting.py` exists
  to stop.
- **And neither are the article pages.** `patterns/beitrag-*.html` is one post
  of that archive spliced into `patterns/blog-artikel.html` by
  `scripts/build-articles.py` — one page per post that carries text, in both
  editions. They are generated in full and an edit to one is lost on the next
  build. The specimen is where the reading surface is worked on: everything
  outside its `article:…` fences is shared by every published article, so a
  change made there reaches all of them, and the fenced regions are the parts
  that belong to one particular piece. `patterns/stelle-*.html` is the same
  arrangement for the vacancy register, from `karriere-stelle.html`.
- **Copy you write exists in two languages.** Every pattern page ships twice —
  German at the root, English from `design-system/patterns/en/` — and the
  English edition is generated, not written. If a run changes a word a reader
  sees, it adds the German → English pair to `design-system/i18n/en.json`, runs
  `python3 scripts/build-i18n.py`, and commits the regenerated pages with the
  change. `build-i18n.py --extract` prints exactly what is missing. CI fails on
  a German string with no entry, which is the point: the alternative is an
  English page with one German sentence in the middle of it, and no lane reads
  the other edition's screenshots.
- **And the root pages are generated too — which eighteen of these prompts do
  not know.** `scripts/build-site.py` writes the root and `en/` HTML from
  `design-system/patterns/`. Only `Website 4.0 Feedback` and the five
  browser-compat lanes run it. See the re-enablement hazard above; this is the
  single largest gap between what the prompts say and what the repository is.

## Standing orders

These are corrections from review that outranked the lane briefs. They exist
because the same fault was reported twice, and they are kept here with the lanes
switched off because they are design decisions about the page, not instructions
to an agent. Whoever works on the landing page next inherits them.

### The build-up must not be over before the reader arrives — motion, 2026-07-27

A `cover` range starts the moment an element's first pixel crosses the viewport
bottom, so an assembly can run to completion below where anyone is looking. The
statement figure did exactly that: scrolled to at reading pace, it was a still
drawing.

The rule is that a build happens where the eye is — still visibly running when
its figure sits in the middle third of the viewport. The acceptance test is to
centre the figure and sample the **rendered** state, not the fraction of the
range spent: these animations carry `--ease-out`, so the visual state runs ahead
of the linear position, and a retime that looked correct by range arithmetic
still measured 78 % built at the centred position. Baseline after the fix:
statement **24 %**, flow **54 %**.

### No line may end in mid-air — seams, 2026-07-28

Measured at 1440×900: the flow's seven drops land within **5 px** of the frame's
rail, but the left run ends **320 px** above it and the right run **32 px**,
each finishing at a node with a stub after it. Every endpoint must arrive at
something. The lane swept every stroke's endpoints in page coordinates each run
and reported the nearest-neighbour table.

One subtlety recorded with it: once the stage pins, `.lp-flow` scrolls while
`.lp-frame` sticks, so any join between them must be made and read *before* the
pin.

### The colour leads and the black follows — motion, 2026-07-28

Two strokes per route: a 2 px light carrying the lime → Glas → CF-Grau ramp,
and the 1 px `--border-strong` contour a few points behind it, so the colour is
a travelling head rather than a tint. On `.lp-flow`, not on the frame — colour
was removed from the border deliberately. The light must be gone before card
01's lime arrives at `contain 11.5 %`, because `--accent` is one lit element per
screen (`design-system/foundations/colors.html#one-per-screen`).

### The statement-to-process illustration — craft, 2026-07-28

To be preferred over other sections until it is good: make the flow a **growing
abstract fractal root** rather than a bus with one split — recursive, self-similar,
thinning, every segment still on one of the four brand angles. Connect its ends.
Carry **numbers and data** on the routes so it reads as data moving, without
breaking the rule that text does not go inside an illustration. And find a good
home for a section title.

## If you are a person reading this

- `main` is quiet now — 3–12 commits a day, not several an hour. The one thing
  that can land under you unannounced is the Notion sync at `:25`, and it only
  touches `content/news/`, `content/jobs/` and what the builders generate from
  them. Rebase before you push anyway; it costs nothing.
- A routine's PR body is usually the best documentation of a change: they were
  required to state what they measured, what they researched and did not act on,
  and what they left for another lane. `git log` on `main` is where those
  subjects live now.
- **Do not switch a lane back on to see what it does.** Eighteen of the
  twenty-nine briefs are older than the way this repository builds, and seven of
  those will try to merge every open `routine/*` pull request in their first
  step. Read the prompt in the UI first, against this file.
- To inspect or change one: <https://claude.ai/code/routines>, or
  `RemoteTrigger {action: "get"}` with an ID from the roster above. Routines
  cannot be deleted through the API that creates them — only disabled, or
  rewritten.
