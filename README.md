# Website of control-f

The website is the 2026 brand: the pages under [`design-system/patterns/`](design-system/patterns/),
served from the repository root. **Eighteen written pages** — landing page, Expertise,
Über uns, News and a topic and an article, Suche and its empty state, Karriere and a
posting and its empty state, Kontakt and its confirmation, Bewerbung and its
confirmation, Datenschutz, Impressum, 404 — each in two languages, German at the root
and English under `/en/`. Suche answers for real; see below.

**And twenty-five more that are generated from content rather than written**: one
reading page per news post that has text, one Stelle page per opening that has an
advertisement, and one page per topic in use. Those ship into folders — `/blog/`,
`/stellen/` and `/news/thema/`, each mirrored under `/en/` — so the served root holds
the eighteen written pages and nothing else.

The **patterns stay flat**, and that asymmetry is deliberate. 118 check scripts read
`design-system/patterns/` with a non-recursive glob and several name a page by string;
a page moved into a subdirectory there would quietly stop being checked, which is worse
than an untidy directory. So the folder is a property of the address and the prefix is
the property of the source: `patterns/beitrag-wie-stahl-….html` is served at
`/blog/wie-stahl-….html`, and `build-site.py` rewrites every link that points at it.
`scripts/README.md` is the table of what owns what.

The generation before it — nine hand-written pages against `assets/css/main.css` — has
been removed.

## The root is generated

Every `.html` file at the root is written by [`scripts/build-site.py`](scripts/build-site.py)
out of the matching page in `design-system/patterns/`, **and none of it is in git.**
Clone this repository and there is no website in it until you build one:

```bash
sh scripts/build-all.sh                  # the whole chain, in the one order that works
python3 -m http.server 8000              # then it is there
```

Until 2026-08-17 the output was committed beside its sources — the 43 pages here, the
43 under `en/`, the 43 English patterns and the 25 generated pattern pages. 154 files,
four copies of every logical page, 70 % of the tracked HTML lines. A one-word copy
change rewrote four files; `grep` answered four times over and one of the answers was
the source; an hourly Notion import arrived as a ninety-six-file diff nobody read.

What replaced `--check` as the gate:

```bash
sh scripts/build-and-verify.sh           # build, then fail if a TRACKED file moved
python3 scripts/check-tracked-outputs.py # fail if generated output is tracked
```

The first is the one that catches real mistakes now. `en.json`, the fenced regions of
`patterns/news.html` and `patterns/karriere.html`, and the two `content/*/.catalogue.json`
ledgers are written by generators and *are* committed — they are the record of which
strings a build owns, and no build can reconstruct them. Building and then asking git
whether anything moved is what holds those to their sources, and it catches a stale
ledger, which comparing output to source never could.

`--check` still exists on every builder and is still the right thing to run at a desk:
it answers "is the tree in front of me current?". It cannot be the CI gate any more,
because a fresh checkout has no pages for it to compare.

The patterns cannot simply live at the root: 117 `scripts/check-*.py` read them
from `design-system/patterns/`, several keyed on that path by string, and the routines run
against it. So the pattern stays where it is checked and the root holds its shipped form,
which differs by four edits and nothing else — asset paths, the landing page's name, and
the two pieces of preview chrome that never ship. The script's own header lists them.

`design-system.yml` builds first and then runs the checks — it has to, since two of
them read pages — and both deploys build the whole chain before they stage, so there is
no such thing as a forgotten rebuild reaching production.

There is one copy of every stylesheet, script, font and image, in
`design-system/assets/`. The shipped pages and the documentation load the same files.

## So is the English edition

`/en/` is the same pages with the words changed, and it is generated one step
earlier in the same chain by [`scripts/build-i18n.py`](scripts/build-i18n.py):
`design-system/patterns/en/` is built from the German pattern beside it, and
`build-site.py` then ships that directory the way it ships the German one.

Twenty-one written sources go through the catalogue that way. The article and
Stelle pages do not: they arrive already bilingual, because their text is two
halves of one file in `content/` — divided by a `--- en ---` line — and
`build-articles.py` and `build-stellen.py` splice each half into the edition it
belongs to. No article's prose ever enters `en.json`.

```bash
python3 scripts/build-i18n.py            # write design-system/patterns/en/
python3 scripts/build-i18n.py --check    # fail if any page is stale or missing
python3 scripts/build-i18n.py --extract  # print every German string with no entry
```

What is written by hand is one file: [`design-system/i18n/en.json`](design-system/i18n/en.json),
German copy on the left and English on the right. Markup, class names, comments, ids,
page-local `<style>` and `<script>`, the isometric drawings and the act structure are not
duplicated — they come through from the German page byte for byte, so
`diff patterns/kontakt.html patterns/en/kontakt.html` is a list of sentences. Anchors and
ids stay German in both editions on purpose: they are identifiers, and sharing them means
a deep link works in either language.

**A German string with no entry in the catalogue fails the build.** That is the part
worth having. The alternative is an English page that quietly ships one German sentence
in the middle of it, which is the failure nobody reviews — and for a month it was five
scheduled routines writing new sentences into the landing pattern every hour, unattended.
Add the copy in German, run `--extract`, translate what it prints, rebuild.

The catch is that the entry is keyed on the German text itself, so **rewording a
sentence fails the build twice**: `UNTRANSLATED` for the new string and `UNUSED` for
the entry the old one left behind. Both are `--extract`-able and both are deliberate;
`scripts/README.md` records it as a known trap rather than a bug.

The two editions point at each other from the nav — the `EN` / `DE` plate at the top
right — and from a `<link rel="alternate" hreflang>` pair in the head. Both are written
by the generator, so they cannot disagree about where the other edition is.

The 117 `scripts/check-*.py` do not read `patterns/en/`. Every fact they keep is
already kept on the German page one directory up, and the English page carries the same
markup, classes, thresholds and glass by construction; asserting it twice would only mean
two tables to edit whenever one page changes. `build-i18n.py --check` is what holds the
mirror to its source.

## Development

```bash
python3 -m http.server 8000    # repo root
```

- Website: <http://localhost:8000/> · English: <http://localhost:8000/en/>
- Design system: <http://localhost:8000/design-system/>

The design system is there in a fresh clone; the website is not. `sh scripts/build-all.sh`
first, or the root is a directory of sources and `/` is a 404.

## Automation

Most commits on `main` **were** written by scheduled cloud agents that merged their own
pull requests, with no human review gate — at peak, 145 in a day. All 29 of them are
switched off as of 2026-08-17, and the only thing still writing to `main` on a schedule
is in this repository: `news-sync.yml`, hourly at `:25`, importing the news archive and
the vacancy register from Notion.

That matters in both directions, and [.github/ROUTINES.md](.github/ROUTINES.md) is the
record: what each routine was, what it was told, the trigger ids to check them by — and
why switching one back on unread is the hazard, since eighteen of the briefs predate the
generated root and would edit a pattern without ever rebuilding the page that ships.

## The search actually searches

`/suche` is the second route whose behaviour is not entirely in the page, and it
is the opposite arrangement to the contact form: no server at all, the answer
computed at build time.

`scripts/build-search-index.py` runs last in `build-all.sh` — after
`build-site.py`, because a search result carries an **address** and a pattern's
address is not the page's — and reads the shipped HTML into one index per
edition, 186 records each: one per page, one per `<h2>` under its `<main>`.
`design-system/assets/js/cf-search.js` fetches the index, matches, ranks and
draws the register the pattern already specifies. The index is generated and is
not tracked, like the pages.

| | |
|---|---|
| `?q=` with hits | the register, every match in `<mark class="cf-mark">`, each link carrying a `#:~:text=` fragment that lights the phrase on the page it opens |
| `?q=` with none | `.cf-error--inline` at `200`, quoting the term back |
| no `?q=` | the field, and nothing claiming to be an answer |
| index unreachable | the same inline block, saying so |
| scripting off | the page as it ships: six real hits for “Telemetrie”, that term in the field |

The match is a **substring**, folded — `Warmepumpe` finds `Wärmepumpe`, and
`Telemetrie` finds `Telemetriedaten`, which is the property that matters in a
language that compounds. Every sentence the script draws lives on the page in a
`<template>`, so `en.json` still owns the copy and `/en/suche` is translated by
the same generator as everything else. `scripts/check-search-contract.py` holds
the three pieces together — the hooks and copy keys are read out of the script,
and every one of the 372 record addresses and anchors is walked.

Search is also the **seventh route in the nav bar**, last before the language
switch, and in the footer where it already was.

## The contact form has a server

Every page is a static file except one route. `design-system/components/forms.html`
says of the error summary "It is rendered by the server, not by a script", and
`patterns/kontakt.html` posts to its own URL so a failed submit lands on that summary
with nothing running. [`worker/`](worker/) is that server — one path, one method:

| | |
|---|---|
| honeypot filled | `303` → `kontakt-danke.html`, discarded silently |
| validation fails | `422`, the same page with the summary, the per-field messages and the values already typed |
| sent | `303` → `kontakt-danke.html` (Post/Redirect/Get, so a reload does not send twice) |

No JavaScript is involved on either path. The form's markup did not change to make
this work — posting to its own address was always the precondition.

Mail goes out through **Resend**. Its `eu-west-1` region dispatches from Ireland, but
account data, logs and metadata are stored in the US — a third-country transfer, and
`datenschutz.html` names it as one. `worker/mail.js` is the only file that knows the
provider; swapping it for an EU-domiciled one is about twenty lines and would let that
section shrink.

```bash
npx wrangler dev --local
```

Needs `RESEND_API_KEY` in `.dev.vars` (gitignored). `scripts/check-form-contract.py`
holds the form and the Worker to each other — field names, ids, topics, the honeypot,
the summary's anchor, two error strings and both routes.

## Deployment

Every merge to `main` publishes the website to GitHub Pages via
`.github/workflows/deploy.yml`.

`deploy-worker.yml` publishes the same pages to Cloudflare with the Worker in front of
them. It runs only when the `CLOUDFLARE_ENABLED` variable is set, so it is inert until
someone turns it on, and **both deploys run in parallel** — the cutover is a DNS change,
not a merge. Cloudflare serves `dist/`, which `scripts/stage-site.py` fills with the
86 generated pages and `design-system/` and nothing else in the repository.

**GitHub Pages serves that same directory now.** It used to upload the checkout —
`path: .`, which excludes `.git` and `.github` and nothing else — so the public site
answered 200 for every generator, every check script, the Worker's source,
`wrangler.toml` and the content store. `deploy.yml` stages with
`stage-site.py --surface pages` and uploads `dist/`, so both deploys ship the same
bytes and neither ships the repository.

One difference between the two hosts is configured away: Cloudflare's asset server
answers `/kontakt.html` with a `307` to `/kontakt` by default, which would rewrite every
address on the site and break the form outright. `html_handling = "none"` turns that off,
at the price of the directory indexes — so the Worker serves `/` and `/design-system/`,
and `stage-site.py --check` fails if a third one ever appears without a route.

- Website: https://control-f-io.github.io/control-f-website/
- Design system: https://control-f-io.github.io/control-f-website/design-system/

Because the site is served from a subpath, links and asset references must stay
**relative** (`design-system/assets/css/tokens.css`, `expertise.html`) — a leading `/`
would resolve against `control-f-io.github.io` and 404. `scripts/check-links.py` holds
that rule for the design system; the generator carries it to the root.

## Domain cutover

**The plan, decided 2026-09-02: the site stays on GitHub Pages and takes the domain
there.** The Worker keeps answering the two forms from its workers.dev address, DNS
stays at iwantmyname, and no zone moves to Cloudflare — so nothing about
`info@control-f.io` can break. What that path gives up is written in `wrangler.toml`
above the commented `[[routes]]` block, which is the alternative and stays four lines
away.

**Everything on the site that names its own address reads `SITE_ORIGIN` in
`wrangler.toml`**: `og:image`, `og:url` and the canonical link on every card page, the
sitemap, and the stubs that answer the old Wix addresses. The code side of the move is
therefore one line, and it is the only change in the cutover pull request.

What is already in place:

- every indexable page carries `<link rel="canonical">` and `og:url` on `SITE_ORIGIN`,
  so the copy a crawler still holds at the old Pages address points at the new one the
  moment the line changes (`scripts/check-open-graph.py` holds both to the page's name);
- `sitemap.xml` on both surfaces, every indexable page with its other edition as an
  hreflang alternate; there is no `robots.txt`, on purpose — the site is meant to be
  read by every crawler, index and script there is;
- `content/redirects.txt`, the 28 addresses the Wix site published and where each now
  lives. GitHub Pages cannot send a 301, so `stage-site.py` writes a meta-refresh stub
  under each old path, canonical to its target — testable today at
  `control-f-io.github.io/control-f-website/post/…` — and a `_redirects` file for the
  Worker surface. Four targets were judgment calls and are explained in that file.

Before the day (all outside this repository):

1. **Lower the TTLs** at iwantmyname on `control-f.io`'s apex A record and the `www`
   CNAME to 300 seconds, a day ahead.
2. **Verify the domain with GitHub**: organisation settings → Pages → *Add a domain* →
   `control-f.io`. GitHub gives a TXT record named
   `_github-pages-challenge-control-f-io.control-f.io`; add it at iwantmyname and click
   *Verify*. Verification covers `www` as well, and it is what stops another GitHub
   user from claiming the domain if Pages is ever switched off.
3. **Search Console**: add a *Domain* property for `control-f.io` (a second TXT at the
   apex). Bing Webmaster Tools can import from it afterwards.
4. **Touch nothing else in the zone.** These records are live and must stay exactly as
   they are: `MX` → Proton, the `v=spf1 include:_spf.protonmail.ch` and
   `protonmail-verification` TXTs, the three `protonmail*._domainkey` CNAMEs, `_dmarc`,
   `resend._domainkey` (the form's DKIM), and `send.control-f.io`'s MX and SPF (the
   form's bounce address). The `MS=…` TXT is an old Microsoft verification and may go.

The day, in this order:

1. **DNS at iwantmyname.** Change `www` from `pointing.wixdns.net` to a CNAME on
   `control-f-io.github.io`. Replace the apex `A 185.230.63.107` (Wix) with GitHub's
   four A records `185.199.108.153`, `185.199.109.153`, `185.199.110.153`,
   `185.199.111.153` and four AAAA records `2606:50c0:8000::153` through
   `2606:50c0:8003::153`. No wildcard records, ever — they defeat the verification.
2. **Tell Pages the domain.** Settings → Pages → *Custom domain* → `www.control-f.io`,
   or, from a checkout with `gh` signed in:

   ```bash
   gh api -X PUT repos/control-f-io/control-f-website/pages -f cname=www.control-f.io
   ```

   From this moment `control-f-io.github.io/control-f-website/…` answers 301 to
   `www.control-f.io/…`, and GitHub redirects the apex to `www` itself. The deploy
   workflow needs no change: with a custom Actions workflow the `CNAME` file is
   ignored and the setting is the whole configuration.
3. **Merge the cutover pull request** — `SITE_ORIGIN = "https://www.control-f.io"`,
   nothing else. Wait for `deploy.yml`; the site now names its own domain everywhere.
4. **HTTPS.** GitHub requests the certificate once DNS resolves; it can take up to a
   day. When Settings → Pages offers *Enforce HTTPS*, turn it on (the repository setting
   is already `https_enforced: true`, but GitHub re-evaluates it for a new domain).
5. **Verify**, from any shell:

   ```bash
   for u in https://www.control-f.io/ https://control-f.io/ https://www.control-f.io/en/ https://www.control-f.io/sitemap.xml https://www.control-f.io/jobs https://www.control-f.io/post/ki-kennzeichnung-was-der-ai-act-jetzt-verlangt https://control-f-io.github.io/control-f-website/expertise.html; do printf '%-90s ' "$u"; curl -sS -o /dev/null -w '%{http_code} %{redirect_url}\n' "$u"; done
   ```

   Then send both forms for real — the German and the English one, an enquiry and an
   application — and confirm the mail arrives at `info@control-f.io` with DKIM passing
   (the Worker's `SITE_ORIGIN` now returns the reader to `www.control-f.io`). Paste the
   landing page into LinkedIn's Post Inspector and check the card names the domain.
6. **Search Console**: submit `https://www.control-f.io/sitemap.xml`. Do not use
   *Change of address* — the property is the same domain.
7. **Only then, Wix.** Cancel the premium plan and disconnect `control-f.io` from the
   Wix site. **`controlf.io` needs a decision first**: its nameservers are Wix's
   (`ns0/ns1.wixdns.net`), it carries the Proton MX for that mailbox, and its 301 to
   `www.control-f.io` is a Wix feature. Move its DNS to iwantmyname (or any host with URL
   forwarding) before the Wix account is touched, and recreate the redirect there.

Cloudflare needs nothing: the Worker keeps its workers.dev address, `_headers` keeps
marking that copy `noindex` — it is still the second copy — and `SITE_ORIGIN` sends the
reader back to the site after a submit, as it does today.

## Fragen

- Answered 2026-08-03: the contact address is `info@control-f.io` and the press
  address `presse@control-f.io`. `jobs@` and `datenschutz@` were not named and
  still write `control-f.de`.
- Answered 2026-08-13: the phone number on Impressum and Datenschutz was
  Simon's personal mobile, not a company line — removed from the pages (and
  from this file, and from git history) rather than replaced.
- host control-f.io or controlf.io or both? — Prepared 2026-09-02: `www.control-f.io`
  is the canonical host, because it is the one the Wix site's sitemap published and the
  one search engines hold. `controlf.io` is a second domain whose DNS is on Wix's
  nameservers and which Wix currently 301s to www.control-f.io; see *Domain cutover*.
- Three of these were about the outgoing homepage and the new design has already
  answered them: the header folds into a menu button below 780 px and is a flat bar
  above it, "Home" is the first item in it, and the map/mail/LinkedIn strip is gone.
  Say so if any of that is wrong.
- Legal placeholders still to be filled by a lawyer: `HRB 000000`, `DE000000000`, the
  Amtsgericht, the photography credit, the log retention, the hosting provider, and
  whether Matomo and the LinkedIn tags are what actually ships.
  → `design-system/README.md`

## TODOs

- SEO optimizations
- optimize for Google Lighthouse
- Redirects for the outgoing URLs (`experten.html`, `dienstleistungen.html`,
  `energie.html`, `maschinenbau.html`, `blog/`) if any of them are linked from outside
