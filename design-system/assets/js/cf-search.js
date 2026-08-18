/* Control-F — search.
   The answer on /suche, computed in the page because there is nobody else to
   compute it. Ships. No dependencies, no build step, ~9 kB unminified.

   WHY THIS FILE EXISTS AT ALL, given that components/search.html's Behaviour
   section opens with "No script." That sentence is about a site with a server:
   the form is a GET, the server renders the answer, the page is a page. This
   site has exactly one route with a server — the contact form's POST, in
   worker/ — and every other address is a static file. Nobody was rendering the
   answer, so /suche drew six results for "Telemetrie" whatever was typed into
   it, for the whole life of the section.

   WHAT IS AND IS NOT MOVED INTO THE SCRIPT. Only the arithmetic. The index is
   built where the pages are (scripts/build-search-index.py, at build time, out
   of the shipped HTML), the copy stays on the page in <template> so the
   catalogue still owns every sentence and build-i18n.py still translates it,
   and the drawing is the same .cf-result the pattern already ships. This file
   matches, ranks, and writes those three things into the page.

   Contract with the page — every hook is an attribute, and check-search-
   contract.py holds the page to it:

     [data-cf-search]           on <main>: this is the live search route
     [data-cf-search-claim]     the header-meta span carrying "N Treffer für …"
     [data-cf-search-counter]   the section header's count
     [data-cf-search-region]    the container the register is drawn into
     [data-cf-search-results]   the <ol> inside it — the specimen, replaced
     [data-cf-search-tpl=copy]  the string table: one [data-key] per string
     [data-cf-search-tpl=empty] the zero-results block, markup and all
     [data-cf-search-tpl=error] the same block for an index that never arrived

   What it writes on <html>, and nothing else:

     data-cf-search="live"      the moment the file runs, before the body
     data-cf-search="ready"     when the register has been drawn

   THE TAG GOES IN THE <head>, and for the same reason cf-nav.js's does. The
   page ships a worked answer — six results for "Telemetrie", which is what
   check-register-count.py holds it to and what a reader with no JavaScript
   gets — and that answer is not the reader's. components.css hides the claim
   and the register while <html> says `live`, so the specimen never reaches the
   glass; written any later, every search would paint six wrong results and
   then replace them. With scripting off the attribute is never written, the
   rule never applies, and the page is the specimen: a real query, its term in
   the field, its six real answers. That is a fallback rather than a lie.

   THE MATCH IS A SUBSTRING, and the empty state says so in as many words:
   "die Suche schneidet nicht an Wortgrenzen ab, Telemetrie findet also auch
   Telemetriedaten". German compounds, so a stemmer that cut at word boundaries
   would answer "Telemetrie" with nothing on a page that says Telemetriedaten
   nine times. Folding is the other half of the same argument — Warmepumpe
   finds Wärmepumpe — and it is done by decomposing to NFD and dropping the
   combining marks, with ß mapped to ss by hand because it has no decomposition.

   CONTOUR HERE, LIGHT THERE. Every match in the register is drawn with
   .cf-mark and never .cf-mark--current: foundations/found.html allows exactly
   one lit match, meaning "the hit you are on", and on a page of candidates the
   reader is on none of them. The light is deferred to the destination — every
   result link carries a #:~:text= fragment quoting its own excerpt, and
   ::target-text draws it there. Which is why the fragment is quoted out of ONE
   run of the index and never across two: a phrase that spans an element
   boundary stops matching, silently, and the reader lands at the top of the
   page with nothing lit and no way to know why.
*/

(function () {
  'use strict';

  /* Before the body is parsed — see the header. */
  document.documentElement.setAttribute('data-cf-search', 'live');

  /* THE REGISTER IS CAPPED, AND THE PAGE SAYS SO WHEN IT BITES.
     components/pagination.html's rule is that pagination joins above about
     four screens; thirty results is around that, and a cap the reader is told
     about is honest where a silently truncated list is not. A query broad
     enough to pass thirty is a query to narrow, and the capped line says that
     rather than offering a page 2 of a ranking nobody should be reading down. */
  var MAX = 30;

  /* Where the index is. Derived from this file's own address rather than from
     the page's, because the two are at different depths — a root page loads
     `design-system/assets/js/`, the pattern preview loads `../assets/js/` —
     and the index sits beside this script either way. The same base resolves
     every result link, so a result found from the design system's copy of the
     page opens the shipped page rather than the pattern. */
  var HERE = 'design-system/assets/js/';
  var src = (document.currentScript && document.currentScript.src) || '';
  var BASE = src.indexOf(HERE) >= 0 ? src.slice(0, src.indexOf(HERE)) : '';
  var LANG = (document.documentElement.getAttribute('lang') || 'de').slice(0, 2);

  /* Started here in the head, so the fetch and the rest of the parse run
     together. Two hundred milliseconds of index is two hundred milliseconds of
     markup the browser was going to spend anyway. */
  var index = fetch(BASE + 'design-system/assets/search/index-' + LANG + '.json')
    .then(function (r) {
      if (!r.ok) throw new Error('index ' + r.status);
      return r.json();
    });

  /* ---------------------------------------------------------------- folding */

  function fold(text) {
    return text
      .toLowerCase()
      .replace(/ß/g, 'ss')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  /* The query as terms. Quotes are not a syntax here and are not pretended to
     be: two words mean both words, in any order, anywhere in the record. */
  function terms(query) {
    return fold(query).split(/\s+/).filter(function (t) { return t.length > 1; });
  }

  /* Every occurrence of every term inside one folded string, merged where two
     terms overlap so a mark is never opened inside a mark. */
  function hits(folded, ts) {
    var found = [];
    for (var i = 0; i < ts.length; i++) {
      var from = 0, at;
      while ((at = folded.indexOf(ts[i], from)) !== -1) {
        found.push([at, at + ts[i].length]);
        from = at + ts[i].length;
      }
    }
    found.sort(function (a, b) { return a[0] - b[0]; });
    var merged = [];
    for (var j = 0; j < found.length; j++) {
      var last = merged[merged.length - 1];
      if (last && found[j][0] <= last[1]) last[1] = Math.max(last[1], found[j][1]);
      else merged.push([found[j][0], found[j][1]]);
    }
    return merged;
  }

  /* ----------------------------------------------------------------- ranking */

  /* A record scores on where the terms are, not how often. A term in the title
     is the reader's word being the page's subject; the same term four times in
     a paragraph is a paragraph about it, which is worth less and worth it once.
     Every term must appear somewhere or the record is not an answer at all —
     two words typed together are a narrowing, and OR would widen instead. */
  function score(doc, ts) {
    var title = fold(doc.title);
    var body = doc.foldedRuns;
    var total = 0;
    for (var i = 0; i < ts.length; i++) {
      var inTitle = title.indexOf(ts[i]) !== -1;
      var inBody = false;
      for (var j = 0; j < body.length && !inBody; j++) {
        inBody = body[j].indexOf(ts[i]) !== -1;
      }
      if (!inTitle && !inBody) return 0;
      total += (inTitle ? 8 : 0) + (inBody ? 2 : 0);
    }
    /* A WHOLE PAGE OUTRANKS ITS OWN SECTIONS, and the bonus has to be larger
       than a body match to do it. Every section inherits the page's title —
       "Data Engineer (m/w/d) — Eckdaten" — so the title term scores identically
       on all of them and the body term is the only thing left to separate a
       page from a piece of itself. Measured on ?q=Data+Engineer before this
       was 3 rather than 1: the winner was `/stellen/data-engineer#weitere`,
       the cross-link list at the foot of the page, because it happens to
       repeat the other openings' titles in its body. The page itself came
       fifth. Three per term clears a body match (two) with one to spare, so
       the page leads and the reader who wanted the section still finds it two
       lines down under the same heading. */
    if (doc.kind !== 'section') total += 3 * ts.length;
    return total;
  }

  /* ---------------------------------------------------------------- excerpts */

  /* The run to quote: the first one carrying the most of the query. First
     rather than longest, because a page's own order is an argument — the lead
     paragraph says what the page is and the eleventh says what it also covers. */
  function pick(doc, ts) {
    var best = null;
    for (var i = 0; i < doc.runs.length; i++) {
      var spans = hits(doc.foldedRuns[i], ts);
      if (!spans.length) continue;
      var distinct = 0;
      for (var t = 0; t < ts.length; t++) {
        if (doc.foldedRuns[i].indexOf(ts[t]) !== -1) distinct++;
      }
      if (!best || distinct > best.distinct) best = {
        text: doc.runs[i], spans: spans, distinct: distinct
      };
      if (best.distinct === ts.length) break;
    }
    return best;
  }

  /* A window of about two lines around the first match, cut at spaces so no
     word is halved, with an ellipsis on the side that was cut. */
  var WINDOW = 190;

  function excerpt(run) {
    var start = Math.max(0, run.spans[0][0] - 60);
    var end = Math.min(run.text.length, start + WINDOW);
    if (start > 0) {
      var space = run.text.indexOf(' ', start);
      start = space === -1 || space > run.spans[0][0] ? start : space + 1;
    }
    if (end < run.text.length) {
      var back = run.text.lastIndexOf(' ', end);
      end = back > run.spans[0][0] ? back : end;
    }
    return {
      text: (start > 0 ? '… ' : '') + run.text.slice(start, end) +
            (end < run.text.length ? ' …' : ''),
      offset: start - (start > 0 ? 2 : 0)
    };
  }

  /* ---------------------------------------------------------------- fragment */

  /* The phrase the destination lights up. Four to six words is the band
     components/search.html measured: shorter repeats on the page and sends the
     reader to the wrong occurrence, longer spans an element boundary the
     editor will one day change. Taken from inside a single run, so it cannot
     span one today either. */
  function fragment(url, run) {
    var text = run.text, span = run.spans[0];
    var start = span[0], end = span[1];

    /* OUT TO WHOLE WORDS FIRST. The match is a substring and in German it is
       usually a substring of a compound: "Telemetrie" inside "Telemetriedaten".
       Quoting the match alone would send `Telemetrie daten` — the phrase cut
       mid-word and put back with a space in it, which matches nothing on the
       page it came from. The phrase is a SLICE of the run from here on, never
       a rejoin, so what is quoted is what is written. */
    while (start > 0 && !/\s/.test(text.charAt(start - 1))) start--;
    while (end < text.length && !/\s/.test(text.charAt(end))) end++;

    /* Two words back and three on: four to six words in all, which is the band
       components/search.html measured. Shorter repeats on the target page and
       lands the reader on the wrong occurrence; longer spans an element
       boundary an editor will one day move. */
    for (var i = 0; i < 2; i++) {
      var prev = start > 1 ? text.lastIndexOf(' ', start - 2) : -1;
      if (prev === -1) { start = 0; break; }
      start = prev + 1;
    }
    for (var j = 0; j < 3; j++) {
      var next = text.indexOf(' ', end + 1);
      if (next === -1) { end = text.length; break; }
      end = next;
    }

    /* encodeURIComponent leaves the hyphen alone, and the hyphen is this
       syntax's own delimiter — `prefix-,start,end,-suffix`. A literal one left
       raw makes the browser read half the phrase as a prefix and match
       nothing, silently. */
    var phrase = encodeURIComponent(text.slice(start, end).trim())
      .replace(/-/g, '%2D');
    /* `:~:` opens the fragment DIRECTIVE, and it opens it inside whatever
       fragment the record already carries. A section record's address ends in
       #faq, and a second `#` there would be a malformed URL rather than two
       instructions — the anchor puts the reader in the right section, the
       directive lights the phrase inside it. */
    return url + (url.indexOf('#') === -1 ? '#' : '') + ':~:text=' + phrase;
  }

  /* ------------------------------------------------------------------ drawing */

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }

  /* The excerpt with its matches marked. Built out of text nodes and <mark>
     elements rather than assembled as a string: the index holds page copy, and
     page copy put through innerHTML is the one injection this component could
     ever have. */
  function marked(text, ts) {
    var frag = document.createDocumentFragment();
    var spans = hits(fold(text), ts);
    var at = 0;
    for (var i = 0; i < spans.length; i++) {
      if (spans[i][0] > at) {
        frag.appendChild(document.createTextNode(text.slice(at, spans[i][0])));
      }
      frag.appendChild(el('mark', 'cf-mark', text.slice(spans[i][0], spans[i][1])));
      at = spans[i][1];
    }
    if (at < text.length) frag.appendChild(document.createTextNode(text.slice(at)));
    return frag;
  }

  function result(doc, ts, ordinal, copy) {
    var li = el('li', 'cf-result');

    var kind = copy('kind-' + doc.kind) || copy('kind-page');
    var meta = el('p', 'cf-result__meta');
    var num = el('span', null, ordinal < 10 ? '0' + ordinal : String(ordinal));
    num.setAttribute('aria-hidden', 'true');
    meta.appendChild(num);
    meta.appendChild(el('span', null, doc.date ? kind + ' · ' + doc.date : kind));
    li.appendChild(meta);

    var run = pick(doc, ts);
    var link = el('a', 'cf-result__link');
    link.href = run ? fragment(BASE + doc.url, run) : BASE + doc.url;
    link.appendChild(marked(doc.title, ts));
    var title = el('h3', 'cf-result__title');
    title.appendChild(link);
    li.appendChild(title);

    /* A record whose only match is in its title still gets an excerpt, and it
       is the record's opening line: the reader asked what this page is, the
       title answered, and the sentence under it is the page saying the same
       thing at length. Nothing in it is marked, because nothing in it matched
       — a mark on a word the reader did not type is the component lying about
       where the answer is. */
    var body = run ? excerpt(run).text : doc.runs[0];
    if (body) {
      var p = el('p', 'cf-result__excerpt');
      p.appendChild(marked(body, ts));
      li.appendChild(p);
    }

    li.appendChild(el('p', 'cf-result__path', doc.path));
    return li;
  }

  /* --------------------------------------------------------------- the page */

  function run() {
    var main = document.querySelector('[data-cf-search]');
    if (!main) return;

    var field = main.querySelector('.cf-search .cf-field__input');
    var claim = main.querySelector('[data-cf-search-claim]');
    var counter = main.querySelector('[data-cf-search-counter]');
    var region = main.querySelector('[data-cf-search-region]');
    var section = region && region.closest('.section');
    var strings = main.querySelector('[data-cf-search-tpl="copy"]');
    if (!field || !claim || !region || !strings) return;

    /* Every sentence this file draws comes from the page, so the catalogue
       still owns it and patterns/en/ still gets it translated. The short ones
       are a table of [data-key] spans; the two block states are whole markup,
       because a heading and a route out are structure the page should keep. */
    function copy(key) {
      var node = strings.content.querySelector('[data-key="' + key + '"]');
      return node ? node.textContent.trim() : '';
    }
    function fill(text, values) {
      return text.replace(/\{(\w+)\}/g, function (whole, name) {
        return name in values ? values[name] : whole;
      });
    }
    /* The reader's own words go back into the page as a text node and never as
       markup — the one place in this component where that could go wrong. */
    function fillTree(root, values) {
      var walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      var node;
      while ((node = walk.nextNode())) {
        if (node.nodeValue.indexOf('{') !== -1) {
          node.nodeValue = fill(node.nodeValue, values);
        }
      }
      return root;
    }

    var query = '';
    try {
      query = (new URL(window.location.href).searchParams.get('q') || '').trim();
    } catch (e) { /* no URL support: the page stays the specimen */ }

    field.value = query;

    /* THE ORDER HERE IS THE LIVE REGION'S, not tidiness. The claim carries
       role="status", and while <html> says `live` it is `visibility: hidden` —
       which takes it out of the accessibility tree, where a change is not a
       status message, it is nothing. So the register is drawn, then the page is
       handed over, and only then is the number written: into a region that is
       by that point visible and being watched. Same task, same frame, so
       nothing about the drawing changes. */
    function done() {
      document.documentElement.setAttribute('data-cf-search', 'ready');
    }

    /* No question asked. The register is not empty, it is not yet — so it is
       not drawn at all, and the page is the field it opens with. */
    if (!query) {
      if (section) section.hidden = true;
      document.title = copy('page-title');
      done();
      claim.textContent = copy('claim-idle');
      return;
    }

    document.title = query + ' — ' + copy('page-title');

    /* Zero results, or an index that never arrived. Two templates and one
       drawing: both are "no answer here" and the reader's next step is the
       same either way — .cf-error--inline at 200, a sentence naming what
       happened, and a route out. What differs is whose fault it is, and that
       is the whole of what the two blocks say differently. */
    function state(name) {
      var tpl = main.querySelector('[data-cf-search-tpl="' + name + '"]');
      if (!tpl) return;
      region.replaceChildren(
        fillTree(tpl.content.cloneNode(true), { q: query }));
    }

    index.then(function (data) {
      var ts = terms(query);
      var docs = data.docs;
      var found = [];
      for (var i = 0; i < docs.length; i++) {
        docs[i].foldedRuns = docs[i].runs.map(fold);
        var s = ts.length ? score(docs[i], ts) : 0;
        if (s) found.push({ doc: docs[i], score: s });
      }
      found.sort(function (a, b) {
        return b.score - a.score || a.doc.url.localeCompare(b.doc.url);
      });

      var n = found.length;
      var line = fill(copy(n === 1 ? 'claim-one' : 'claim'),
                      { n: String(n), q: query });

      if (!n) {
        state('empty');
      } else {
        var list = el('ol', 'cf-results');
        list.setAttribute('role', 'list');
        var shown = Math.min(n, MAX);
        for (var k = 0; k < shown; k++) {
          list.appendChild(result(found[k].doc, ts, k + 1, copy));
        }
        region.replaceChildren(list);
        if (n > shown) {
          region.appendChild(el('p', 'cf-result__path',
                                fill(copy('capped'), { m: String(shown) })));
        }
      }

      if (section) section.hidden = false;
      if (counter) counter.textContent = String(n);
      document.title = line + ' — ' + copy('page-title');
      done();
      claim.textContent = line;
    }).catch(function () {
      state('error');
      if (counter) counter.textContent = '0';
      done();
      claim.textContent = fill(copy('claim'), { n: '0', q: query });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
