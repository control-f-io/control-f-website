/* Die Website, plus die eine Route, die kein Dokument ist.

   Alles unter dieser Adresse ist eine statische Datei und wird von Cloudflares
   Asset-Auslieferung bedient, ohne dass dieser Code läuft — das regelt
   run_worker_first in wrangler.toml, das genau einen Pfad nennt. Für
   /kontakt.html läuft er, und auch dort tut er nur bei POST etwas: ein GET
   reicht er an dieselbe statische Datei weiter, die jede andere Seite auch
   bekommt.

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
   ist, dass "/" und "/design-system/" dann auf nichts zeigen. Die zwei
   Verzeichnisse, die eine index.html haben, bedient dieser Worker.

   Kein Skript ist an diesem Weg beteiligt, auf keiner Seite. */

import { sendEnquiry } from "./mail.js";
import { renderForm } from "./render.js";
import { validate } from "./validate.js";

const FORM_PATH = "/kontakt.html";
const THANKS_PATH = "/kontakt-danke.html";

/* Post/Redirect/Get. 303 und nicht 302: 303 schreibt vor, dass der Browser dem
   Redirect mit GET folgt, und genau darum geht es. */
const seeOther = (location) =>
  new Response(null, { status: 303, headers: { location, "cache-control": "no-store" } });

/* Die Seite, die der Leser bei einem Fehler sieht, ist die Seite selbst — also
   wird sie hier geholt. Ein GET auf den eigenen Pfad, an die Assets gerichtet,
   nicht an den Worker: es entsteht keine Schleife. */
const loadForm = (env, url) => env.ASSETS.fetch(new Request(new URL(FORM_PATH, url), { method: "GET" }));

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

const DIRECTORIES = new Set(["/", "/design-system", "/design-system/"]);

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname !== FORM_PATH) {
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

    return handleSubmit(request, env, ctx, url);
  },
};

async function handleSubmit(request, env, ctx, url) {
  /* Die Bremse. Sie zählt pro IP und pro Minute und steht vor allem anderen,
     damit eine Flut nicht erst geparst und validiert wird. Zehn Absendeversuche
     in einer Minute erreicht kein Mensch, der ein Formular ausfüllt.

     Ohne Binding — etwa in einem lokalen `wrangler dev` ohne Netz — wird nicht
     gebremst statt zu scheitern. */
  const ip = request.headers.get("cf-connecting-ip") || "unbekannt";
  if (env.CONTACT_RATE_LIMIT) {
    const { success } = await env.CONTACT_RATE_LIMIT.limit({ key: ip });
    if (!success) {
      return new Response("Zu viele Anfragen. Bitte versuchen Sie es in einer Minute erneut.", {
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
  if (raw.website.trim() !== "") return seeOther(THANKS_PATH);

  const { values, errors } = validate(raw);

  if (errors.length > 0) {
    return renderForm(await loadForm(env, url), { errors, values, status: 422 });
  }

  try {
    await sendEnquiry(values, env);
  } catch (err) {
    /* Der Grund gehört ins Log, nicht auf die Seite: er kann die
       Mail-Konfiguration verraten, und der Leser kann mit ihm nichts anfangen.
       Was er stattdessen bekommt, ist der Weg, der noch offen ist — die
       Adresse, die auf derselben Seite unter "Direkt" steht. */
    console.error("kontakt: Versand gescheitert", err);
    return renderForm(await loadForm(env, url), {
      values,
      status: 502,
      notice: {
        title: "Ihre Nachricht konnte gerade nicht gesendet werden",
        items: [{
          target: "direkt",
          field: null,
          message: "Bitte versuchen Sie es in einigen Minuten noch einmal — oder schreiben Sie uns direkt an info@control-f.de.",
        }],
      },
    });
  }

  return seeOther(THANKS_PATH);
}
