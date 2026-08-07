/* Die Antwort auf ein fehlgeschlagenes Absenden.

   patterns/kontakt.html sagt über der Fehlerübersicht: "Serverseitig gerendert:
   sie existiert nur in der Antwort auf ein fehlgeschlagenes Absenden." Das hier
   ist dieser Server. Er baut keine eigene Seite — er nimmt kontakt.html, so wie
   sie ausgeliefert wird, und schreibt vier Dinge hinein:

     1. die Fehlerübersicht, vor dem Formular, mit id="fehler" — das Fragment,
        auf das action zeigt, damit der Browser ohne Skript dort landet
     2. cf-field--invalid auf die betroffenen Feld-Wrapper
     3. die Meldung je Feld, plus aria-invalid und aria-describedby
     4. die Werte, die der Leser schon getippt hat, zurück in die Felder

   HTMLRewriter statt Textersatz: es ist ein Streaming-Parser, kein regulärer
   Ausdruck auf 20 KB HTML. Die Seite wird weitergereicht, während sie
   umgeschrieben wird, und ein Attribut, das umzieht, bricht nichts.

   Die Selektoren sind der Vertrag mit dem Muster. Wenn dort eine id oder ein
   data-field verschwindet, greift der passende Handler still ins Leere — genau
   deshalb hält scripts/check-form-contract.py beide Seiten aneinander, und
   deshalb prüft renderForm() zusätzlich zur Laufzeit, dass die Übersicht
   wirklich eingefügt wurde.

   DIE SELEKTOREN GELTEN FÜR BEIDE AUSGABEN. /en/kontakt.html ist dieselbe
   Seite mit anderen Wörtern — build-i18n.py fasst weder id noch class noch
   data-field an —, also braucht diese Datei keine zweite Tabelle. Was sich
   unterscheidet, sind die Wörter, die sie einsetzt: die Beschriftung in der
   Übersicht und die Themenliste, über deren Position eine Option wieder
   ausgewählt wird. Beide kommen aus validate.js, beide je Ausgabe. */

import { DEFAULT_LOCALE, FIELD_LABELS, TOPICS, summaryTitle } from "./validate.js";

const ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" };
const escapeHtml = (s) => String(s).replace(/[&<>"]/g, (c) => ESCAPES[c]);

/* Welches Eingabefeld zu welchem Feldnamen gehört, und in welchem Wrapper es
   steckt. Eine Tabelle statt fünf Sonderfällen im Code. */
const FIELDS = {
  name:    { input: "#f-name",  wrapper: '[data-field="name"]',    kind: "input" },
  email:   { input: "#f-mail",  wrapper: '[data-field="email"]',   kind: "input" },
  company: { input: "#f-firma", wrapper: '[data-field="company"]', kind: "input" },
  topic:   { input: "#f-topic", wrapper: '[data-field="topic"]',   kind: "select" },
  message: { input: "#f-msg",   wrapper: '[data-field="message"]', kind: "textarea" },
};

function summaryHtml(errors, title, locale) {
  /* Ein Eintrag trägt das Label seines Feldes vorweg — die Übersicht ist ein
     Index auf das Formular. Eine allgemeine Meldung (der Versand ist
     gescheitert) gehört zu keinem Feld und steht deshalb ohne Präfix da. */
  const labels = FIELD_LABELS[locale] || FIELD_LABELS[DEFAULT_LOCALE];
  const items = errors
    .map((e) => {
      const label = e.field ? labels[e.field] : null;
      const text = label ? `${escapeHtml(label)}: ${escapeHtml(e.message)}` : escapeHtml(e.message);
      return `      <li><a href="#${escapeHtml(e.target)}">${text}</a></li>`;
    })
    .join("\n");

  return [
    '    <div class="cf-error-summary" role="alert" tabindex="-1" id="fehler">',
    `      <h3 class="cf-error-summary__title">${escapeHtml(title)}</h3>`,
    '      <ul class="cf-error-summary__list">',
    items,
    "      </ul>",
    "    </div>",
    "",
    "    ",
  ].join("\n");
}

/* Setzt einen einzelnen Wert zurück ins Feld. Ein <input> trägt ihn als
   Attribut, ein <textarea> als Inhalt, ein <select> als selected auf der
   passenden Option — drei Mechanismen, weil HTML drei hat. */
function refill(rewriter, field, value, locale) {
  const spec = FIELDS[field];
  if (!spec || !value) return;

  if (spec.kind === "input") {
    rewriter.on(spec.input, {
      element(el) { el.setAttribute("value", value); },
    });
    return;
  }

  if (spec.kind === "textarea") {
    /* html: false lässt HTMLRewriter escapen — der Text kommt vom Leser. */
    rewriter.on(spec.input, {
      element(el) { el.setInnerContent(value, { html: false }); },
    });
    return;
  }

  /* <select>: die Optionen tragen keinen value-Attribut, ihr Text *ist* der
     Wert. Nach dem Text zu selektieren geht trotzdem nicht — CSS kennt keinen
     Textvergleich, und ein im element-Handler gemerktes Element ist im
     text-Handler bereits ungültig ("content token is no longer valid").

     Also über die Position. TOPICS steht in derselben Reihenfolge wie die
     Optionen im Formular, und check-form-contract.py vergleicht beide Listen
     der Reihe nach — die Position ist damit keine Annahme, sondern geprüft.
     Vor den Themen steht "Bitte wählen", deshalb +2 auf den nullbasierten
     Index: nth-of-type zählt ab 1.

     Die Liste ist die der Ausgabe. Beide haben fünf Themen in derselben
     Reihenfolge, aber gesucht wird der Wert, der angekommen ist, und der ist
     in der Sprache des Formulars, auf dem er ausgewählt wurde. */
  const at = (TOPICS[locale] || TOPICS[DEFAULT_LOCALE]).indexOf(value);
  if (at === -1) return;
  rewriter.on(`${spec.input} option:nth-of-type(${at + 2})`, {
    element(el) { el.setAttribute("selected", ""); },
  });
}

/* Baut die Antwort auf einen POST, der nicht durchging: dieselbe Seite, um die
   Fehler ergänzt, mit dem Status, der sagt warum.

   422 für Eingabefehler, 502 wenn der Mailversand gescheitert ist. Beide sind
   kein 200 — ein Fehlversuch darf nicht als Erfolg im Cache oder im Log
   landen. */
export async function renderForm(assetResponse, { errors = [], values = {}, notice = null, status = 422, locale = DEFAULT_LOCALE }) {
  const title = notice ? notice.title : summaryTitle(errors.length, locale);
  const items = notice ? notice.items : errors;

  let injected = false;
  const rewriter = new HTMLRewriter();

  /* Die Übersicht kommt vor das Formular — dorthin, wo das Muster sie im
     Kommentar ankündigt. */
  rewriter.on("form[method='post']", {
    element(el) {
      el.before(summaryHtml(items, title, locale), { html: true });
      injected = true;
    },
  });

  for (const err of errors) {
    const spec = FIELDS[err.field];
    if (!spec) continue;
    const errorId = `${err.target}-error`;

    rewriter.on(spec.wrapper, {
      element(el) {
        const existing = el.getAttribute("class") || "";
        if (!existing.split(/\s+/).includes("cf-field--invalid")) {
          el.setAttribute("class", `${existing} cf-field--invalid`.trim());
        }
      },
    });

    rewriter.on(spec.input, {
      element(el) {
        el.setAttribute("aria-invalid", "true");
        /* Ein vorhandenes aria-describedby bleibt stehen und bekommt die
           Meldung dazu — es könnte auf einen Hinweistext zeigen. */
        const described = el.getAttribute("aria-describedby");
        el.setAttribute("aria-describedby", described ? `${described} ${errorId}` : errorId);
        el.after(
          `<span class="cf-field__error" id="${escapeHtml(errorId)}">${escapeHtml(err.message)}</span>`,
          { html: true },
        );
      },
    });
  }

  for (const [field, value] of Object.entries(values)) refill(rewriter, field, value, locale);

  const out = rewriter.transform(
    new Response(assetResponse.body, {
      status,
      headers: {
        "content-type": "text/html; charset=utf-8",
        /* Eine Antwort mit den Eingaben des Lesers darin gehört in keinen
           Cache — weder in den des Browsers noch in den von Cloudflare. */
        "cache-control": "no-store",
        "referrer-policy": "same-origin",
      },
    }),
  );

  /* Der Body wird erst beim Lesen durch den Rewriter geschoben, also steht
     `injected` erst danach fest. Der Text wird hier ohnehin gebraucht, um die
     Länge zu kennen — und die Gelegenheit, den Vertrag zu prüfen, kostet damit
     nichts. */
  const html = await out.text();
  if (!injected) {
    /* Kein harter Fehler: der Leser bekommt eine korrekte Seite, nur ohne
       Übersicht. Aber es steht im Log, und der Check fängt es vorher ab. */
    console.error("kontakt: form[method=post] nicht gefunden — Fehlerübersicht nicht eingefügt");
  }

  return new Response(html, { status, headers: out.headers });
}
