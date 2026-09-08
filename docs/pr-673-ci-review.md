# PR #673 CI review

Reviewed 8 September 2026 at PR commit
`d770e06d85282784969754ac704f0c641664ebb8`.

[Pull request](https://github.com/control-f-io/control-f-website/pull/673) ·
[Failed workflow](https://github.com/control-f-io/control-f-website/actions/runs/34230723387)

## What the red checks meant

The failed run had two red jobs. The static job reported 46 failed steps; the
other 130 steps, including setup and the build, succeeded. The runtime job
reported eight browser findings and stopped the five browser checks after it,
so those five were skipped rather than failed.

The findings came from three causes:

1. Real page defects: duplicate IDs, animation and video work despite reduced
   motion, frozen view timelines, keyboard/focus gaps, print overlays, overflow
   risks, and incomplete Open Graph metadata.
2. Checks reading source fragments as complete pages. The footer had moved to
   shared partials, while link, accessibility, job, and footer checks still read
   the unexpanded marker. Fragment files were also being tested as documents.
3. Design registers that still described removed prototype sections or omitted
   new V2 tokens, breakpoints, spacing, motion, gradients, and component classes.

A red check therefore meant that one documented invariant returned exit code 1.
It did not mean the whole site or every test failed. Some diagnostics identified
page behavior; others identified stale test inputs or design-system records.

## Repair

- Kept the translucent grey-black navigation surface at 55% black and added it
  as the live navigation specimen and a registered material in the design
  system. Labels are white and the selected-page marker darkens the backing, so
  both states clear WCAG AA over the brightest possible page frame. At 200% text
  the logo now yields space to the two mobile controls instead of widening the
  document.
- Added one rendered-source path for builds, static checks, browser previews,
  and the development server. It expands the correct German or English footer,
  adds current-section markers, and resolves only routes present in the build
  table. A new regression check covers include count, editions, route aliases,
  clean preview URLs, and preservation of unknown/external URLs.
- Fixed the page-level defects, including the Expertise IDs and timeline crop,
  homepage reduced-motion behavior and metadata, keyboard/focus and print
  states, grid minimums, wrapping, language annotations, and generated news
  filtering classes.
- Moved drawing checks to the prototype that still owns those drawings and
  restored its source-sensor layer. Updated the token and documentation
  registers from the shipping CSS instead of removing their assertions.

## Validation

- `sh scripts/build-and-verify.sh`: the tracked tree matches deterministic
  generator output.
- All workflow static checks pass, including the new rendered-source regression
  check.
- Runtime visits all 39 pattern pages in normal and reduced-motion modes: no
  console or request errors, duplicate IDs, frozen scroll timelines, running
  reduced-motion animation, or fetched reduced-motion video loop.
- Text zoom measures 936 page/viewport/root-size combinations. All 585 gated
  states stay within the viewport; the mobile navigation no longer contributes
  to the remaining legacy census.
- Consent focus return, pinned keyboard traversal, glass contrast sampling, and
  spectrum rendering browser checks pass.

The changes are local on `codex/pr-673-design-system`; the historical GitHub run
remains red until the branch is pushed and CI runs again.
