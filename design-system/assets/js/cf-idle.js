/* Control-F — a page that is not being read is a page that is not moving.

   OPTIONAL, and it adds nothing to the drawing. Every figure it touches is
   already complete, already animated and already correct without it. All this
   does is stop a perpetual animation from running while the figure carrying it
   is nowhere near the viewport. Delete the tag and the page renders exactly as
   it did, and costs what it cost.

   THE FAULT IT EXISTS FOR. A scroll-driven animation is free when nobody
   scrolls: no scroll, no frame, no work. An animation on the DOCUMENT clock is
   the opposite — `infinite` means for the life of the tab, whether the element
   is on screen, off screen or fifteen thousand pixels away, and whether the
   reader is reading, typing in another window or has walked off.

   patterns/landing-page.html ships 128 of them. 126 are `.sp-stream > b`, the
   six readings each of act 1's twenty-one sensor labels cycle through; two are
   the copy stream's caret. Act 1 is about 2 300 px of a 22 931 px document.

   Measured at 1440 x 900, Chromium 1194, page LOADED AND THEN LEFT ALONE — no
   scrolling, no pointer, no keyboard, five seconds of a still page:

     landing 1440, at the top                1351 ms of style recalc in 5 000
                                             299 recalcs — one per frame, 60 Hz
                                             4.5 ms per frame
                                             2246 ms of total task time  (45 %)
     landing 1440, act 5 on screen and       1395 ms — the figure is 15 000 px
       act 1 fifteen thousand px away          away and costs the same
     landing 1440, with the 126 cancelled      319 ms  (-76 %)
     landing 1440, prefers-reduced-motion        0 ms
     landing  375                                0 ms
     expertise 1440                              0 ms
     kontakt   1440                              0 ms

   Half the main thread, at every frame, forever, for a readout that is not on
   the screen. It is the cost this file removes.

   WHY IT IS NOT THE READOUT'S FAULT, and why the cure is here rather than in
   the keyframes. The property is `opacity`, the cheapest thing to animate in
   the system and the one the motion chapter asks for. Substituting a single
   `transform` animation on one empty 4 x 4 div for all 128 measured 1362 ms of
   recalc in the same 5 s — the same figure. The count barely matters either:
   26 shimmering leaves cost 1375 ms and ONE costs 1150. What costs is that the
   page is producing frames at all; every frame it produces then walks a
   1 623-element document against 840 KB of stylesheet. So there is no cheaper
   keyframe to write, and no smaller number of elements to write it on. The
   only lever is time — the animation has to stop.

   WHAT IT DOES. One IntersectionObserver per marked figure. Off screen, the
   figure gets `data-idle`; acts.css and components.css pause the animations
   under that attribute. On screen it goes away and they run. `rootMargin` is a
   whole viewport in each direction, so the readouts are already ticking well
   before the figure's first pixel arrives and there is nothing to "start".

   PAUSED, NOT STOPPED. `animation-play-state: paused` holds every element at
   the value it had, which for a six-slot ticker is the reading it was showing.
   Nothing re-runs from the top when the reader comes back, no number jumps, and
   the phase offsets that make the twenty-one labels tick out of step are kept.
   The alternative — cancelling the animation — restarts the whole field in
   unison the moment it re-enters, which is the one thing the stagger exists to
   prevent.

   WHAT IT REFUSES. No IntersectionObserver, no work: the page keeps its old
   behaviour rather than getting a worse one. Under prefers-reduced-motion there
   is nothing running to pause — measured 0 ms above, because every one of these
   animations is already inside a no-preference gate — so the observers are
   never even built.

   MARKED, NOT GUESSED. A figure opts in with data-cf-idle, the same way a track
   opts into the copy stream by carrying the class the stream looks for. This
   file has no list of class names in it and nothing to keep in step.

   AND A FIGURE WHOSE BOX CANNOT ANSWER THE QUESTION SAYS SO ON A SECOND
   ATTRIBUTE. data-cf-drawn names, as a selector, the thing inside the figure
   whose ink decides whether there is anything to animate — the fringe's
   twenty-six leaves are held at `scale: 0` for 2 525 px of scroll after their
   box has arrived, and the box is inside a sticky stage, so no margin on the
   attribute above can close over it. The measurement is at callback().

   AND THE MARGIN IS THE FIGURE'S, because one margin was right for one of the
   two things this file gates and wrong for the other.

   A viewport of lead-in is the readouts' requirement: they are TEXT, and a
   ticker that starts while the reader is looking at it is a ticker seen
   starting. The root's fringe has no such requirement — it is a sine on
   stroke-opacity with a per-leaf phase offset, and for the whole first third
   of its own track it is held at `scale: 0` by an animation on the scroll
   timeline. There is nothing to see start, because there is nothing drawn.

   Given one margin, the two shared the readouts' — and the fringe's marked box
   was act 1+2's whole 5 760 px track, whose top edge stands 138 px ABOVE the
   fold at scrollY=0. So the gate was open at the top of the page, and stayed
   open: measured at 1440 x 900, loaded and left alone at the hero,

     as shipped                     2 601 ms of task in 4 000 — 65 % of a core
                                    1 509 ms of it style recalc, 240 recalcs,
                                    one per frame at 60 Hz
     shimmer alone paused               1.0 ms                    0.0 %
     all 26 leaves display:none         0.7 ms                    0.0 %
     at 1280                        2 560 ms                     64 %
     at 768 and at 375                  1.5 ms                    0.0 %

   Two thirds of a core, forever, for twenty-six paths that are `scale: 0`,
   zero pixels wide and 77 px below the fold. The 375 and 768 columns are the
   same page with no fringe in that tier at all, which is what makes the
   attribution exact.

   The value on the attribute is the rootMargin for that figure and nothing
   else; empty keeps the readouts' viewport of lead-in. Figures are grouped by
   margin, so the usual page still builds one observer.

   AND THERE IS A SECOND GATE IN HERE NOW, because geometry cannot answer the
   question on a figure inside a pinned stage: the marked box never leaves the
   viewport, and the readouts it carries have been at opacity 0 for most of
   that time. It is marked `data-cf-paint`, it writes `data-dark`, and it asks
   `checkVisibility({ opacityProperty: true })` rather than an observer. Every
   measurement above is of a STILL page, and on a still page pausing is the
   whole cure. Under a finger it is worth 5 % where taking the animation away
   is worth 74 %, which is why the two gates use different verbs. Measured
   over one rAF-paced pass down the landing page at 390 x 844, CPU throttled
   4x: 378 elements walked per frame before this gate and 105 after, 3 314 ms
   of style recalculation and 1 207. The argument and the rest of the numbers
   are at the foot of this file, where the mechanism is.
   → scripts/check-idle-motion.py, scripts/check-idle-reach.py,
     scripts/check-idle-paint.py */

(function () {
  'use strict';

  if (!window.IntersectionObserver || !window.matchMedia) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var figures = document.querySelectorAll('[data-cf-idle]');
  if (!figures.length) return;

  /* A whole viewport of margin in each direction, unless the figure names its
     own. The observer fires on the approach rather than on the arrival, so a
     reader scrolling at any speed meets a figure that has been running for at
     least a screen — the tick is never seen starting. A figure with nothing to
     be seen starting says so on its own attribute; see the block header. */
  var DEFAULT_MARGIN = '100% 0px 100% 0px';

  /* AND A SECOND INPUT, FOR THE FIGURE WHOSE BOX CANNOT ANSWER. `data-idle` is
     now the AND of two facts about a figure — near the window, and drawing
     something — and a figure that names no second subject has only the first,
     which is the observer's answer and nothing else. Both writers go through
     apply(), so there is no order between them to get wrong.

     WHY THE FRINGE NEEDED IT, and why no rootMargin does. .sp-root carries
     data-cf-idle="0px" for the twenty-six leaves that shimmer on the document
     clock, and the note over it in patterns/landing-page.html ends on the
     sentence that turns out to be this paragraph's argument rather than that
     one's: lp-frame-draw holds every leaf at `scale: 0` until contain 36 % of
     the track, THOUSANDS OF PIXELS after the box has arrived. The box cannot
     wait, because it is inside a sticky stage. Measured at 1440 x 900,
     .sp-root's rect.top against scrollY:

         scrollY      0    200    400    600    800   1200   2000   2600
         rect.top   927    727    527    327    271    271    271    271

     It sticks at 271 by scrollY 800 and does not move again until the stage
     releases at 6 475. So the gate opened at scrollY 50 — the frame the box
     crossed the fold — and the first leaf did not draw until 2 575. 2 525 px
     of scroll, the first three screens of the front door, with twenty-six
     leaves breathing at 60 Hz on boxes that are 0 x 0. A margin cannot reach
     it: -30 % of the viewport moves the opening from 50 to 300, and every
     value past that closes the gate over leaves that ARE drawn, because the
     box the margin is measured against stopped moving.

     Measured on the shipped page, loaded, scrolled once and then LEFT ALONE,
     5 000 ms per row, Chromium 1194 at 1440 x 900:

                    before            after
       scrollY     recalc    task    recalc  task   what is on screen
          600     200 ms   466 ms      0 ms   2 ms  hero, no leaf drawn
        1 200     201      471         0      2     act 1, no leaf drawn
        1 600     203      473         0      2     act 1, no leaf drawn
        2 000     208      490         0      2     act 1, no leaf drawn
        2 400     883    1 379         3      8     readouts lit, no leaf
        2 600     923    1 496       877  1 571     four leaves drawn
        3 000     230      894       232    890     the fringe, drawn
        4 000     124    2 366       119  2 609     the fringe, drawn

     At 1280 x 800, where the same bands are 2 250 px: 219 / 519 -> 0 / 2 at
     scrollY 600, 208 / 516 -> 0 / 2 at 1 200, 210 / 516 -> 0 / 2 at 1 600.

     Every row where nothing is drawn goes to the 2 ms the top of the page
     already cost, and every row where something is drawn is unchanged. 2 400
     is the interesting one and it is not this gate's doing: the shimmer is the
     only animation in that band Chromium cannot composite, so it is the one
     making the frames the other 126 are then walked in — the claim acts.css
     makes over .lp-flow__leaf, measured here from the other side. The readouts
     keep ticking on the compositor; sampled every 400 ms at scrollY 2 400, the
     six-slot sequence is the same before and after, and 25 screenshots down
     the document at each of 1440 x 900 and 1280 x 800 are byte-identical.

     A BOX WITH NO AREA IS THE THIRD WAY THIS SYSTEM WITHDRAWS A THING, and it
     is the one neither gate in this file could see. The observer answers
     `where`; checkVisibility below answers `display, visibility, opacity,
     content-visibility`. `scale: 0` is none of those: the element is visible
     by every flag that call takes and puts no ink down. So this reads the rect
     and nothing else — it is the cheaper question and it is the one that is
     false here.

     ANY, NOT ALL. The leaves stagger in on --l, so the fringe is drawn from
     the first leaf's arrival to the last leaf's departure and the loop stops
     at the first subject with area. Measured at every viewport the fringe
     ships in, the gate now opens on exactly the scroll position the first leaf
     draws at and closes where it closed before:

       1440x900  50 -> 2 575    1366x768  25 -> 2 175    1280x800  25 -> 2 275
       1280x1024 150 -> 2 925   1152x900  75 -> 2 575    1024x768  25 -> 2 175
       1024x1366 275 -> 3 625   900x700  500 -> 1 150    768x1024 475 -> 1 075
       390x844  400 ->   925

     THE PAUSE IS STILL THE VERB, unchanged: `[data-idle] .lp-flow__leaf` holds
     the shimmer at the value it had, and the per-leaf phase offsets survive.
     Nothing in the stylesheets moves for this — the rule that answers the
     attribute is the one that already answered it.

     AND IT COSTS ONE RECT A FRAME while the figure is dark, on the pages that
     ask for it and no others: the listeners are only attached if some figure
     named a subject. Over a full 300-step pass down the landing page the whole
     document measures 649 and 611 ms of style recalc before against 553, 589
     and 585 after, and 5 246 / 5 270 ms of task against 5 372 / 5 232 / 5 772
     — noise either way, which is the answer to the only cost this adds.
     An unparseable selector leaves the figure with the observer's answer
     alone, for the reason observerFor() falls back to the default margin: a
     gate that is too generous is where this file started, and a page that
     fails to boot is not. */
  var near = [];
  var drawn = [];
  var subjects = [];
  var watched = false;

  function apply(n) {
    if (near[n] && drawn[n]) figures[n].removeAttribute('data-idle');
    else figures[n].setAttribute('data-idle', '');
  }

  function callback(entries) {
    for (var i = 0; i < entries.length; i++) {
      for (var n = 0; n < figures.length; n++) {
        if (figures[n] !== entries[i].target) continue;
        near[n] = entries[i].isIntersecting;
        apply(n);
        break;
      }
    }
  }

  function inked(el) {
    var box = el.getBoundingClientRect();
    return !!(box.width || box.height);
  }

  function reread() {
    for (var n = 0; n < figures.length; n++) {
      if (!subjects[n]) continue;
      var lit = false;
      for (var k = 0; k < subjects[n].length; k++) {
        if (inked(subjects[n][k])) { lit = true; break; }
      }
      if (drawn[n] === lit) continue;
      drawn[n] = lit;
      apply(n);
    }
  }

  /* Coalesced to one rAF, the way act-rail.js and cf-stream.js coalesce
     theirs, and the way the paint gate at the foot of this file does. */
  var ticking = false;
  function schedule() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () { ticking = false; reread(); });
  }

  /* One observer per distinct margin, not one per figure: a page that names no
     margin anywhere builds exactly the single observer this file always built.
     An unparseable value throws from the constructor rather than silently
     observing at some other distance, so it is caught and the figure falls back
     to the default — a gate that is too generous is the behaviour this file
     started from, and a page that fails to boot is not. */
  var observers = {};
  function observerFor(margin) {
    if (!observers[margin]) {
      try {
        observers[margin] = new window.IntersectionObserver(callback, { rootMargin: margin });
      } catch (e) {
        observers[margin] = observers[DEFAULT_MARGIN] ||
          (observers[DEFAULT_MARGIN] =
            new window.IntersectionObserver(callback, { rootMargin: DEFAULT_MARGIN }));
      }
    }
    return observers[margin];
  }

  for (var i = 0; i < figures.length; i++) {
    /* IDLE UNTIL TOLD OTHERWISE, so a figure that is off screen at load has
       been still since its first frame rather than since the first callback.

       AND THE FIRST CALLBACK IS NOT BEFORE PAINT. This line first carried the
       claim that it was, which is wrong and was worth measuring rather than
       asserting: sampling the attribute on every animation frame from
       DOMContentLoaded, over three loads at 1440 x 900 with act 1 on screen,
       `data-idle` was still set on 1, 1 and 2 frames before the observer took
       it off. So the readouts ARE held for a frame or two at load.

       It is kept anyway, because the ticker's own step is 500 ms — each of the
       six readings holds for 16.66 % of a 3 s cycle — and one frame of a still
       reading is indistinguishable from the 30 still frames either side of it.
       The alternative costs the thing this file is for: dropping the pre-set
       lets every figure on the page run from load until the first callback,
       including the ones fifteen thousand pixels away, which is the fault. */
    figures[i].setAttribute('data-idle', '');
    near[i] = false;
    /* DRAWN UNTIL READ, which is the opposite of the line above it and right
       for the same reason: the pre-set must not be the state that lets a
       figure run. `near` is false here, so the AND is false whatever this is,
       and reread() below settles it before the first frame. */
    drawn[i] = true;
    var sel = figures[i].getAttribute('data-cf-drawn');
    var named = null;
    if (sel) {
      try { named = figures[i].querySelectorAll(sel); } catch (e) { named = null; }
    }
    subjects[i] = (named && named.length) ? named : null;
    if (subjects[i]) watched = true;
    observerFor(figures[i].getAttribute('data-cf-idle') || DEFAULT_MARGIN).observe(figures[i]);
  }

  if (watched) {
    reread();
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule, { passive: true });
  }
}());


/* ---- THE SECOND GATE: PAINTED, NOT MERELY PRESENT ----

   ITS OWN BLOCK, and that is the shape of the claim above it: two mechanisms
   in one file that share a subject and share nothing else. This one needs no
   IntersectionObserver, observes nothing, and has its own mark; the one above
   needs no checkVisibility and has its own. A browser or a page that can only
   have one gets that one, and neither can take the other down.


     GEOMETRY IS THE WRONG QUESTION FOR A FIGURE INSIDE A PINNED STAGE, and
     acts.css has carried the open fault at length under `.sp-stream` since it
     was found. `data-cf-idle` is on `.sp-track`, which is not sticky and which
     therefore intersects the viewport for the whole of its own scroll — every
     position a reader can be at while still inside act 1 or act 2. The box the
     126 readouts actually live in is `.sp-annots`, which crossfades to opacity
     0 partway through that and stays there. The observer above never sees it
     leave, because the box it is asked about never leaves, and
     IntersectionObserver has no way to report that one box now sits behind
     another that has gone opaque in front of it.

     Measured on the shipped landing page at 390 x 844, consent answered,
     Chromium 1194: the notes are painted over 250 px of scroll and the
     readouts were ticking over 3 100 px of it. Twelve times the scroll a
     reader can see them in, and it is the first half of the document — the
     half a reader meets first.

     AND WHAT IT COSTS IS PAID WHILE SCROLLING, which is the part the rest of
     this file's measurements do not cover and the reason this gate does a
     different thing to the one above. Every number in this file's header is
     from a STILL page: no scroll, no frames of its own, so a perpetual
     animation is the thing making frames happen and pausing it removes the
     frame and everything in it. A page under a finger is producing frames
     anyway. A paused animation is still an animation on the element, and the
     style update that frame — already scheduled by the scroll — still walks
     it. Measured through the acts at 390 x 844 with the CPU throttled 4x, one
     rAF-paced pass of sixty steps, median of three, taken with the readouts'
     resting state as it then was — all six readings `display: block`:

                                   elements/frame   style recalc
       as it stood                      517           2 266 ms
       the same 126 merely PAUSED       491           1 995
       the same 126 with no animation   136             689

     Pausing bought 5 %. Taking the animation away bought 74 %. So this gate
     removes rather than pauses — `[data-dark]` in acts.css sets
     `animation-name: none` — and the gate above keeps `paused` for the case it
     was measured on, where holding each reading at the value it had is worth
     having and costs nothing.

     THE TABLE DOES NOT REPRODUCE ON THE SHIPPED PAGE ANY MORE, and that is
     not the table being wrong. acts.css puts five readings in six back to
     `display: none` under the same attribute, because six readings with no
     animation to show one at a time is a six-deep overprint; that takes 105
     of the 126 animated boxes out of the frame as well, and `paused` and
     `none` then measure 170 and 160 over the same band. The pause did not
     become cheap — the resting state took the elements away. A later edit
     that reads those two numbers and simplifies this back to a play state
     would be reading the wrong pair. scripts/check-idle-paint.py is what
     fails then.

     THE RESTART IS INVISIBLE HERE AND WOULD NOT BE THERE. Dropping these
     animations and re-creating them puts all twenty-one sensors back on their
     slot-0 reading at once — `animation-delay` staggers the six readings
     within a sensor, not the sensors against each other — and acts.css is
     right that this must not happen under the geometric gate, whose edges are
     a viewport of margin around a box that stays put and can therefore flip
     while the reader is looking straight at a lit field. This gate's edges are
     the two instants the figure's opacity passes through zero. There is
     nothing drawn to see restart.

     IT ASKS THE PAGE RATHER THAN CARRYING THE NUMBERS. acts.css states the
     window twice, in contain%, once per tier: 18 % to 82 % below the pin gate
     and 26 % to 44 % above it. A scroll-position gate would have to hold all
     four here, in a second file, with nothing keeping them equal but a third
     check script — and would be wrong in the tiers that have no timeline at
     all. `checkVisibility({ opacityProperty: true })` asks for the one fact
     that actually decides it, so this file has no thresholds in it, needs no
     breakpoint, and works the same in every tier including the ones the
     choreography degrades to.

     ONE CALL PER SCROLL FRAME, on one element per marked figure, coalesced to
     one rAF the way act-rail.js and cf-stream.js coalesce theirs. Measured
     over one rAF-paced pass down the whole document, CPU throttled 4x:

                          elements/frame        style recalc
       390 x 844           378  ->  105        3 314 ms  ->  1 207 ms
       1440 x 844          435  ->  144        4 202     ->  1 981

     Over the acts alone at 390, 513 -> 160 against a floor of 127 with the
     readouts' animation deleted outright — so the gate gives back all but 33
     elements a frame of what deleting the figure would. Every other page in
     patterns/ walks two to six.

     WHAT IT REFUSES, on this file's own terms: no checkVisibility, no work.
     Safari below 17.4 and Firefox below 125 keep the behaviour they have
     rather than a worse one, and the geometric gate above is untouched by any
     of this. → acts.css, under `.sp-stream`;scripts/check-idle-paint.py */

(function () {
  'use strict';

  if (!window.matchMedia) return;
  /* Nothing to gate: every animation this reaches is already inside a
     no-preference block, which is the measurement in the header above. */
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var painted = document.querySelectorAll('[data-cf-paint]');
  if (!painted.length || !painted[0].checkVisibility) return;

  var dark = [];
  var ticking = false;

  function read() {
    ticking = false;
    for (var i = 0; i < painted.length; i++) {
      /* opacityProperty is the one that answers this file's question; the
         other two are named so that a figure withdrawn by any of the three
         ways this system withdraws things reads the same here. */
      var lit = painted[i].checkVisibility({
        opacityProperty: true,
        visibilityProperty: true,
        contentVisibilityAuto: true
      });
      if (dark[i] === !lit) continue;
      dark[i] = !lit;
      if (dark[i]) painted[i].setAttribute('data-dark', '');
      else painted[i].removeAttribute('data-dark');
    }
  }

  function schedule() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(read);
  }

  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });

  /* DARK UNTIL READ, for the reason the gate above is idle until its first
     callback: a figure that is not painted at load should have been still
     since its first frame. The read is in this same task, so a figure that IS
     painted at load loses nothing by it. */
  for (var d = 0; d < painted.length; d++) {
    painted[d].setAttribute('data-dark', '');
    dark[d] = true;
  }
  read();
}());
