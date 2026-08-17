#!/bin/sh
# Build the website, then fail if building moved anything that is tracked.
#
# WHAT THIS REPLACED, AND WHY THE OLD QUESTION STOPPED MAKING SENSE. CI used to
# run each generator's `--check`, which asks "does the committed output match its
# source?". That was the right question while the output was committed. It is not
# a question at all now that it is not: on a fresh checkout the generated pages do
# not exist, so `--check` would report every one of them MISSING and fail for the
# one reason that is expected.
#
# THE QUESTION THAT SURVIVES is about the files that are still tracked and are
# still partly written by a generator:
#
#   design-system/i18n/en.json          build-news.py and build-jobs.py add the
#                                       archive's and the register's derived
#                                       strings to it, and prune their own
#   design-system/patterns/news.html    five regions inside <!-- news:… --> fences
#   design-system/patterns/karriere.html  two regions inside <!-- jobs:… --> fences
#   content/news/.catalogue.json        which en.json keys build-news.py owns
#   content/jobs/.catalogue.json        which en.json keys build-jobs.py owns
#
# Those cannot be rebuilt from the pages — they are the record of what a build
# owns — so they stay in git, and this is what holds them honest. Build
# everything, then ask git whether any tracked file moved. If one did, the commit
# is missing part of itself: somebody edited inside a fence, or added a German
# sentence without its catalogue entry, or changed a post and committed the
# markdown alone.
#
# It is strictly more than the six `--check` steps asserted. They compared output
# to source and could not see a stale ledger; this compares the whole tracked tree
# to what the generators produce from it.
#
# scripts/check-tracked-outputs.py is the other half of the pair: it fails when
# generated output is tracked. Together they say the tree holds sources, all of
# them, and nothing else.
set -e
cd "$(dirname "$0")/.."

# BEFORE AND AFTER, NOT "IS THE TREE CLEAN". In CI the checkout is pristine, so
# the two are the same assertion; at a desk they are not, and the first version of
# this script failed on the uncommitted edit that was being tested. What is being
# asserted is that *building* moved nothing tracked — so the patch is captured on
# either side and compared. Comparing the whole patch rather than the file list is
# deliberate: a file already modified and then modified again by the build has the
# same name in both lists.
before=$(git diff)

sh scripts/build-all.sh

after=$(git diff)

# Tracked files only. The generated pages are ignored, so they cannot appear here
# however many of them the build just wrote.
if [ "$before" = "$after" ]; then
    echo
    echo "build-and-verify: the tracked tree is what the generators produce from it."
    exit 0
fi

echo
echo "build-and-verify: building moved files that are tracked." >&2
echo >&2
git diff --stat >&2
echo >&2
cat >&2 <<'WHY'
  Each of these is written partly or wholly by a generator and is committed on
  purpose, so a difference here means the commit is missing part of itself:

    design-system/i18n/en.json        a German string was added, reworded or
                                      removed without its English pair. Run
                                      `python3 scripts/build-i18n.py --extract`.
    patterns/news.html                something was edited inside a
    patterns/karriere.html            <!-- news:… --> or <!-- jobs:… --> fence.
                                      Those regions are output; edit content/
                                      instead, or the page outside the fences.
    content/*/.catalogue.json         a post or an opening changed and the
                                      ledger was not committed with it.

  Run `sh scripts/build-all.sh`, review what changed, and commit it.
WHY
exit 1
