/* Die Website, plus die eine Route, die kein Dokument ist.

   Alles unter dieser Adresse ist eine statische Datei und wird von Cloudflares
   Asset-Auslieferung bedient, ohne dass dieser Code läuft — das regelt
   run_worker_first in wrangler.toml, das die Pfade einzeln nennt. Für die
   beiden Kontaktseiten läuft er, und auch dort tut er nur bei POST etwas: ein
   GET reicht er an dieselbe statische Datei weiter, die jede andere Seite auch
   bekommt.

   ZWEIMAL, WEIL ES DIE SEITE ZWEIMAL GIBT. /kontakt.html und /en/kontakt.html
   sind dasselbe Formular mit anderen Wörtern. Jede der beiden postet an die
   eigene Adresse — die englische Seite trägt dasselbe relative
   action="kontakt.html#fehler" und trifft damit /en/kontakt.html —, also muss
   dieser Worker beide beantworten. Er tut es mit demselben Code: was sich
   unterscheidet, steht in FORMS und in den Tabellen von validate.js.

   Ein POST auf einen Pfad, der hier nicht steht, erreicht diesen Code nicht,
   sondern die Asset-Auslieferung, und die beantwortet ihn mit der Seite und
   einem 200 — ein Absenden, das aussieht, als wäre es angekommen, und bei dem
   nie eine Mail entsteht. Genau das war die englische Seite, bevor sie hier
   stand.

   DAS FORMULAR MUSSTE DAFÜR NICHT GEÄNDERT WERDEN. Es steht seit jeher auf
   method="post" action="kontakt.html#fehler" — es postet an die eigene
   Adresse, weil die Antwort auf einen Fehler dieselbe Seite mit der
   Fehlerübersicht ist. Genau das ist hier implementiert.

   DIE ZWEI AUSGÄNGE, beide aus dem Kommentar über dem Formular:

     Erfolg   303 See Other auf kontakt-danke.html. Post/Redirect/Get, damit ein
              Neuladen die Nachricht nicht ein zweites Mal sendet.
     Fehler   422 mit derselben Seite, ergänzt um die Übersicht unter id="fehler"
              — dem Fragment, das action trägt. Der Browser landet dort von
              selbst, ohne dass ein Skript läuft.

   DAZU DIE VERZEICHNIS-INDIZES. wrangler.toml stellt html_handling auf "none",
   damit die Seiten unter ihren eigenen Namen erreichbar bleiben — jeder andere
   Modus beantwortet /kontakt.html mit einem 307 auf /kontakt und würde damit
   jede Adresse der Website ändern und das Formular ganz zerlegen. Der Preis
   ist, dass "/", "/en/" und "/design-system/" dann auf nichts zeigen. Die drei
   Verzeichnisse, die eine index.html haben, bedient dieser Worker.

   Kein Skript ist an diesem Weg beteiligt, auf keiner Seite. */

import { sendEnquiry } from "./mail.js";
import { renderForm } from "./render.js";
import { RATE_LIMITED, SEND_FAILED, validate } from "./validate.js";

/* Die Kontaktseiten, je Ausgabe: der Pfad, an den sie postet, die Sprache, in
   der ihr geantwortet wird, und die Danke-Seite, auf die ein Erfolg umleitet.
   Ein Eintrag hier ist eine Zeile mehr in run_worker_first — ohne sie läuft
   dieser Worker für den Pfad nicht, und check-form-contract.py sagt es. Der
   Check liest diese Tabelle und prüft für jeden Eintrag, dass beide Dateien
   ausgeliefert werden und dass das Formular auf der Seite dazu passt. */
const FORMS = {
  "/kontakt.html":    { locale: "de", thanks: "/kontakt-danke.html" },
  "/en/kontakt.html": { locale: "en", thanks: "/en/kontakt-danke.html" },
};

/* Post/Redirect/Get. 303 und nicht 302: 303 schreibt vor, dass der Browser dem
   Redirect mit GET folgt, und genau darum geht es. */
const seeOther = (location) =>
  new Response(null, { status: 303, headers: { location, "cache-control": "no-store" } });

/* Die Seite, die der Leser bei einem Fehler sieht, ist die Seite selbst — also
   wird sie hier geholt. Ein GET auf den eigenen Pfad, an die Assets gerichtet,
   nicht an den Worker: es entsteht keine Schleife. */
const loadForm = (env, url) => env.ASSETS.fetch(new Request(new URL(url.pathname, url), { method: "GET" }));

/* Ein Verzeichnis zeigt auf seine index.html — das, was ein gewöhnlicher
   Dateiserver von selbst tut und was html_handling = "none" abschaltet.

   Ohne Schrägstrich am Ende wird erst umgeleitet und dann ausgeliefert, damit
   relative Pfade in der Seite eine Ebene tiefer aufsetzen: /design-system wäre
   sonst die Basis für ../assets/, und die Stylesheets kämen nicht an. */
function directoryIndex(request, env, url) {
  if (!url.pathname.endsWith("/")) {
    return Response.redirect(new URL(`${url.pathname}/${url.search}`, url), 301);
  }
  return env.ASSETS.fetch(new Request(new URL(`${url.pathname}index.html`, url), request));
}

/* Die drei Verzeichnisse mit einer index.html: die Website, die Dokumentation
   und die englische Ausgabe. stage-site.py --check scheitert, wenn in dist/ ein
   viertes auftaucht, das hier nicht steht. */
const DIRECTORIES = new Set(["/", "/design-system", "/design-system/", "/en", "/en/"]);

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const route = FORMS[url.pathname];

    if (!route) {
      if (DIRECTORIES.has(url.pathname)) return directoryIndex(request, env, url);
      return env.ASSETS.fetch(request);
    }

    if (request.method === "GET" || request.method === "HEAD") {
      return env.ASSETS.fetch(request);
    }

    if (request.method !== "POST") {
      return new Response("Method Not Allowed", {
        status: 405,
        headers: { allow: "GET, HEAD, POST" },
      });
    }

    return handleSubmit(request, env, ctx, url, route);
  },
};

async function handleSubmit(request, env, ctx, url, route) {
  const locale = route.locale;
  /* Die Bremse. Sie zählt pro IP und pro Minute und steht vor allem anderen,
     damit eine Flut nicht erst geparst und validiert wird. Zehn Absendeversuche
     in einer Minute erreicht kein Mensch, der ein Formular ausfüllt.

     Ohne Binding — etwa in einem lokalen `wrangler dev` ohne Netz — wird nicht
     gebremst statt zu scheitern. */
  const ip = request.headers.get("cf-connecting-ip") || "unbekannt";
  if (env.CONTACT_RATE_LIMIT) {
    const { success } = await env.CONTACT_RATE_LIMIT.limit({ key: ip });
    if (!success) {
      return new Response(RATE_LIMITED[locale], {
        status: 429,
        headers: { "content-type": "text/plain; charset=utf-8", "retry-after": "60" },
      });
    }
  }

  let form;
  try {
    form = await request.formData();
  } catch {
    /* Kein Formular im Body — das kommt von keinem Browser, der dieses
       Formular abgeschickt hat. */
    return new Response("Bad Request", { status: 400 });
  }

  const raw = Object.fromEntries(
    ["name", "email", "company", "topic", "message", "website"].map((k) => [k, form.get(k) ?? ""]),
  );

  /* Die Spamfalle aus patterns/kontakt.html: ein Feld namens "website" in einem
     hidden-Container, das kein Screenreader liest und keine Tastatur erreicht.
     Ist es ausgefüllt, war es ein Bot.

     Die Antwort ist trotzdem die Danke-Seite. Ein Bot, dem man sagt, dass er
     erkannt wurde, wird angepasst; einer, der ein 303 auf die Danke-Seite
     bekommt, hat keinen Anlass dazu. Es wird still verworfen — genau das Wort,
     das im Kommentar des Formulars steht. */
  if (raw.website.trim() !== "") return seeOther(route.thanks);

  const { values, errors } = validate(raw, locale);

  if (errors.length > 0) {
    return renderForm(await loadForm(env, url), { errors, values, status: 422, locale });
  }

  try {
    /* Die Adresse der Seite, von der die Anfrage kam, geht mit in die Mail —
       an ihr ist zu sehen, in welcher Sprache geantwortet werden will. */
    await sendEnquiry(values, env, `${url.host}${url.pathname}`);
  } catch (err) {
    /* Der Grund gehört ins Log, nicht auf die Seite: er kann die
       Mail-Konfiguration verraten, und der Leser kann mit ihm nichts anfangen.
       Was er stattdessen bekommt, ist der Weg, der noch offen ist — die
       Adresse, die auf derselben Seite unter "Direkt" steht. */
    console.error("kontakt: Versand gescheitert", err);
    return renderForm(await loadForm(env, url), {
      values,
      status: 502,
      locale,
      notice: {
        title: SEND_FAILED[locale].title,
        items: [{
          target: "direkt",
          field: null,
          message: SEND_FAILED[locale].message,
        }],
      },
    });
  }

  return seeOther(route.thanks);
}
