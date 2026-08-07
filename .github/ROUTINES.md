# The routines

Most of the commits on `main` are not written by a person. They are written by
scheduled cloud agents — "routines" — that run hourly, unattended, and merge
their own pull requests. As of this file there are **150 commits in the last
24 hours** and no human review gate on any of them.

**Their prompts are not in this repository.** They live in the claude.ai
routines API and are edited there, which means the single most consequential
configuration in this project is invisible to anyone reading it. This file is
the repository's record of what they are and what they have been told. It is
written by hand and can drift from the API; where the two disagree, the API is
what actually runs, and `RemoteTrigger {action: "get"}` is how you read it.

## What is running

Five routines, all on `claude-opus-5`, all against `design-system/patterns/landing-page.html`
and nothing else. They fire twelve minutes apart so their pushes do not collide.

| Fires (UTC) | Lane | Owns |
|---|---|---|
| `:03` | seams | overlaps, corners, free line ends, the z-ladder, section seams |
| `:15` | motion | scroll choreography, ranges, fill-modes, both scroll directions |
| `:27` | craft | composition, spacing, type, copy, states, illustration form |
| `:39` | responsive | the width ladder, the pin gate's edges, heights |
| `:51` | quality | console, degraded states, keyboard, contrast in situ, weight |

Branches are `routine/landing-<lane>-YYYYMMDD-HH`; each run ends with
`gh pr merge --squash --delete-branch`.

Five sibling routines for the Patterns section as a whole — links, build-out,
style drift, responsive, bugs — exist at `:07/:19/:31/:43/:55` and are currently
**disabled**. Three of them shipped work before they were turned off, and the
nine `scripts/check-*.py` files they wrote are still enforcing.

## System design & pages

One more, added 2026-07-30, and it is the first that does not fire into
`landing-page.html`:

| Fires (UTC) | Lane | Owns |
|---|---|---|
| `:11` | system design & pages | `design-system/**` — the chapters, the four stylesheets, the checkers — and every page in `patterns/` except `landing-page.html`, which has five owners already |

Branches are `routine/system-pages-YYYYMMDD-HH`. `:11` keeps the same four
minutes of clearance from `:07` and `:15` that the existing lanes keep from each
other.

**It cannot merge its own work, and that is why
`.github/workflows/routine-merge.yml` exists.** The five lanes above were
created from the routines UI and their sessions hold a GitHub connector, so `gh`
and the API are theirs. A routine created from inside a Claude Code session
cannot inherit that connector — the create call says so — and its sessions come
up with git and nothing else. Git can push a branch and cannot raise a pull
request, so this one would stop one step short of `main` every hour. The
workflow closes that step from inside the repository, where it needs nobody's
token: a push to `routine/system-pages-**` runs the same forty checks, opens the
PR from the branch's own commit message, and squash-merges it. A failing gate
still opens the PR and then leaves it open.

Two consequences worth knowing. The gate is **run** in that workflow rather than
waited for, because a PR opened with `GITHUB_TOKEN` does not trigger
`design-system.yml` — waiting for a check that will never start would wait
forever. And the routine's **commit message is the PR body**: `gh pr create
--fill` takes both from the commit, so what it measured has to be written there
rather than typed into a PR form it has no way to reach.

If the connector is ever attached to this routine — recreating it from
<https://claude.ai/code/routines> is the way — the workflow becomes redundant
rather than wrong: it would find the PR the session had already opened and merge
that one.

## What every one of them is told

The instructions differ by lane, but these are common and are why the commit log
looks the way it does:

- **A run that ships nothing is a failed run.** "Nothing needed doing" is
  explicitly defined as failure. This is deliberate and it has a cost: it
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
  already shipped twice.
- **Never weaken a check to make a change pass.**
- **The news archive is not markup you edit.** `design-system/patterns/news.html`
  has four regions fenced by `<!-- news:… -->` comments — the cards, the year
  axis, the counters and the pagination — and `scripts/build-news.py` writes
  them from `content/news/`, one file per post. A lane that edits inside those
  fences has its work overwritten by the next build and fails
  `build-news.py --check` in the meantime. Everything outside them, including
  the composition notes and the topic chips, is authored as usual.
- **And neither are the article pages.** `patterns/beitrag-*.html` is one post
  of that archive spliced into `patterns/blog-artikel.html` by
  `scripts/build-articles.py` — one page per post that carries text, in both
  editions. They are generated in full and an edit to one is lost on the next
  build. The specimen is where the reading surface is worked on: everything
  outside its `article:…` fences is shared by every published article, so a
  change made there reaches all of them, and the fenced regions are the parts
  that belong to one particular piece.
- **Copy you write exists in two languages.** Every pattern page ships twice —
  German at the root, English from `design-system/patterns/en/` — and the
  English edition is generated, not written. If a run changes a word a reader
  sees, it adds the German → English pair to `design-system/i18n/en.json`, runs
  `python3 scripts/build-i18n.py`, and commits the regenerated pages with the
  change. `build-i18n.py --extract` prints exactly what is missing. CI fails on
  a German string with no entry, which is the point: the alternative is an
  English page with one German sentence in the middle of it, and no lane reads
  the other edition's screenshots.

## Standing orders

These are corrections from review that outrank the lane briefs. They exist
because the same fault was reported twice.

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
something. The lane now sweeps every stroke's endpoints in page coordinates each
run and reports the nearest-neighbour table.

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

- `main` moves several times an hour. Rebase immediately before you push, and
  expect to do it twice.
- A routine's PR body is usually the best documentation of a change: they are
  required to state what they measured, what they researched and did not act on,
  and what they left for another lane.
- To stop one: <https://claude.ai/code/routines>. Routines cannot be deleted
  through the API that creates them.
