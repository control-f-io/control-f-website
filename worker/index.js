/* Die Website, plus die eine Route, die kein Dokument ist.

   Alles unter dieser Adresse ist eine statische Datei und wird von Cloudflares
   Asset-Auslieferung bedient, ohne dass dieser Code läuft — das regelt
   run_worker_first in wrangler.toml, das die Pfade einzeln nennt. Für die
   beiden Kontaktseiten läuft er, und auch dort tut er nur bei POST etwas: ein
   GET reicht er an dieselbe statische Datei weiter, die jede andere Seite auch
   bekommt.

   ZWEIMAL, WEIL ES DIE SEITE ZWEIMAL GIBT. /kontakt.html und /en/kontakt.html
   sind dasselbe Formular mit anderen Wörtern, also muss dieser Worker beide
   beantworten. Er tut es mit demselben Code: was sich unterscheidet, steht in
   FORMS und in den Tabellen von validate.js.

   Ein POST auf einen Pfad, der hier nicht steht, erreicht diesen Code nicht,
   sondern die Asset-Auslieferung, und die beantwortet ihn mit der Seite und
   einem 200 — ein Absenden, das aussieht, als wäre es angekommen, und bei dem
   nie eine Mail entsteht. Genau das war die englische Seite, bevor sie hier
   stand.

   DAS FORMULAR POSTET NICHT MEHR AN DIE EIGENE ADRESSE, und das ist die eine
   Stelle, an der die Übergangslösung sichtbar wird. Die Website steht auf
   GitHub Pages, und GitHub Pages beantwortet einen POST mit 405 — auf einem
   statischen Host gibt es nichts, was ein Formular entgegennähme. Also trägt
   das Formular dort die absolute Adresse dieses Workers, und der Weg führt
   über zwei Origins:

     Erfolg   303 See Other auf die Danke-Seite von SITE_ORIGIN — also zurück
              auf die Seite, von der der Leser kam. Post/Redirect/Get, damit
              ein Neuladen die Nachricht nicht ein zweites Mal sendet.
     Fehler   422 mit derselben Seite, ergänzt um die Übersicht unter
              id="fehler" — dem Fragment, das action trägt. Der Browser landet
              dort von selbst, ohne dass ein Skript läuft. Diese Seite ist die
              Kopie DIESES Workers, unter seiner Adresse: eine Fehlerübersicht
              muss serverseitig in das Dokument geschrieben werden, und das
              kann nur der Server tun, der den POST bekommen hat.

   Der Preis ist also, dass ein Leser mit einem Tippfehler im Formular auf der
   workers.dev-Adresse landet. Das ist kein Fehler dieser Datei, sondern der
   Grund, warum die Umstellung auf eine eigene Domain in wrangler.toml
   vorbereitet steht: sobald sie kommt, sind beide Origins derselbe, SITE_ORIGIN
   entfällt, und das Formular postet wieder an seine eigene Adresse.

   DAZU DIE VERZEICHNIS-INDIZES. wrangler.toml stellt html_handling auf "none",
   damit die Seiten unter ihren eigenen Namen erreichbar bleiben — jeder andere
   Modus beantwortet /kontakt.html mit einem 307 auf /kontakt und würde damit
   jede Adresse der Website ändern und das Formular ganz zerlegen. Der Preis
   ist, dass "/", "/en/" und "/design-system/" dann auf nichts zeigen. Die drei
   Verzeichnisse, die eine index.html haben, bedient dieser Worker.

   Kein Skript ist an diesem Weg beteiligt, auf keiner Seite. */

import * as apply from "./apply.js";
import * as contact from "./validate.js";
import { sendApplication, sendEnquiry } from "./mail.js";
import { renderForm } from "./render.js";

/* Die Kontaktseiten, je Ausgabe: der Pfad, an den sie postet, die Sprache, in
   der ihr geantwortet wird, und die Danke-Seite, auf die ein Erfolg umleitet.
   Ein Eintrag hier ist eine Zeile mehr in run_worker_first — ohne sie läuft
   dieser Worker für den Pfad nicht, und check-form-contract.py sagt es. Der
   Check liest diese Tabelle und prüft für jeden Eintrag, dass beide Dateien
   ausgeliefert werden und dass das Formular auf der Seite dazu passt. */
const FORMS = {
  "/kontakt.html":      { locale: "de", kind: "contact", thanks: "/kontakt-danke.html" },
  "/en/kontakt.html":   { locale: "en", kind: "contact", thanks: "/en/kontakt-danke.html" },
  "/bewerbung.html":    { locale: "de", kind: "apply",   thanks: "/bewerbung-danke.html" },
  "/en/bewerbung.html": { locale: "en", kind: "apply",   thanks: "/en/bewerbung-danke.html" },
};

/* Was ein Formular ausmacht, an einer Stelle je Art. `kind` in FORMS wählt
   eine Zeile hier aus, und alles darunter — Validierung, Beschriftungen,
   Auswahlliste, Versand, Fehlertexte — kommt aus dem Modul, das dazugehört.
   Der Code darunter kennt den Unterschied nicht mehr.

   `fileFields` ist der einzige Eintrag, der beim Kontaktformular leer ist: es
   nimmt keine Dateien an, und ein Feld, das nicht in dieser Liste steht, wird
   aus dem Body nie gelesen. */
const KINDS = {
  contact: {
    module: contact,
    /* Neun, seit die zweite Spalte der Seite Felder trägt und keine Prosa
       mehr. Ein Feld, das hier nicht steht, wird aus dem Body nie gelesen —
       es käme im Browser an, im Worker nicht, und niemand sähe etwas davon.
       Die Reihenfolge ist die der Seite: erst die linke Spalte, dann die
       rechte. */
    textFields: ["name", "email", "company", "topic", "message",
                 ...contact.DETAIL_FIELDS],
    fileFields: [],
    options: (locale) => contact.TOPICS[locale],
    /* Der Eintrag der Übersicht, wenn kein Feld schuld ist: die Überschrift
       des Abschnitts, in dem das Formular steht. */
    failTarget: "schreiben",
    send: (values, files, env, source) => sendEnquiry(values, env, source),
  },
  apply: {
    module: apply,
    textFields: ["name", "email", "position", "profile", "portfolio", "message"],
    fileFields: apply.FILE_FIELDS,
    options: (locale) => apply.POSITIONS[locale],
    failTarget: "bewerben",
    send: sendApplication,
  },
};

/* Post/Redirect/Get. 303 und nicht 302: 303 schreibt vor, dass der Browser dem
   Redirect mit GET folgt, und genau darum geht es. */
const seeOther = (location) =>
  new Response(null, { status: 303, headers: { location, "cache-control": "no-store" } });

/* Wohin ein Erfolg zurückführt.

   Solange die Website auf GitHub Pages steht, kommt das Formular von dort und
   nicht von hier: SITE_ORIGIN in wrangler.toml nennt diese Adresse samt
   Unterverzeichnis, und der Leser landet nach dem Absenden wieder auf ihr. Ohne
   SITE_ORIGIN bleibt der Pfad relativ, und dann ist die Danke-Seite die dieses
   Workers — was nach der Umstellung auf eine eigene Domain das Richtige ist. */
const thanksFor = (env, route) =>
  env.SITE_ORIGIN ? `${env.SITE_ORIGIN}${route.thanks}` : route.thanks;

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
  const kind = KINDS[route.kind];
  const mod = kind.module;

  /* Die Bremse. Sie zählt pro IP und pro Minute und steht vor allem anderen,
     damit eine Flut nicht erst geparst und validiert wird. Zehn Absendeversuche
     in einer Minute erreicht kein Mensch, der ein Formular ausfüllt.

     Sie steht bei einer Bewerbung noch aus einem zweiten Grund ganz vorn: erst
     danach wird der Body gelesen, und der bringt hier bis zu zwölf Megabyte
     mit. Was abgewiesen wird, wird nicht hochgeladen.

     Ohne Binding — etwa in einem lokalen `wrangler dev` ohne Netz — wird nicht
     gebremst statt zu scheitern. */
  const ip = request.headers.get("cf-connecting-ip") || "unbekannt";
  if (env.CONTACT_RATE_LIMIT) {
    const { success } = await env.CONTACT_RATE_LIMIT.limit({ key: ip });
    if (!success) {
      return new Response(mod.RATE_LIMITED[locale], {
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
       Formular abgeschickt hat. Bei einer Bewerbung ist es auch die Antwort
       auf einen Upload, den Cloudflare wegen seiner Größe abgeschnitten hat. */
    return new Response("Bad Request", { status: 400 });
  }

  const raw = Object.fromEntries(
    [...kind.textFields, "website"].map((k) => [k, form.get(k) ?? ""]),
  );

  /* Die Spamfalle: ein Feld namens "website" in einem hidden-Container, das
     kein Screenreader liest und keine Tastatur erreicht. Ist es ausgefüllt, war
     es ein Bot. Beide Formulare tragen dieselbe.

     Die Antwort ist trotzdem die Danke-Seite. Ein Bot, dem man sagt, dass er
     erkannt wurde, wird angepasst; einer, der ein 303 auf die Danke-Seite
     bekommt, hat keinen Anlass dazu. Es wird still verworfen — genau das Wort,
     das im Kommentar des Formulars steht. */
  if (String(raw.website).trim() !== "") return seeOther(thanksFor(env, route));

  /* Die Dateien, sofern dieses Formular welche kennt. form.get() liefert für
     ein <input type="file"> ein File und für alles andere einen String; was
     davon brauchbar ist, entscheidet apply.js. */
  const uploads = {};
  for (const field of kind.fileFields) uploads[field] = form.get(field);

  const { values, files = {}, errors } = kind.fileFields.length
    ? mod.validate(raw, uploads, locale)
    : mod.validate(raw, locale);

  /* Alles, was renderForm() über dieses Formular wissen muss. Einmal gebaut,
     weil beide Fehlerwege es brauchen. */
  const page = {
    fields: mod.FIELDS,
    labels: mod.FIELD_LABELS[locale],
    options: kind.options(locale),
    values,
  };

  if (errors.length > 0) {
    return renderForm(await loadForm(env, url), {
      ...page,
      errors,
      title: mod.summaryTitle(errors.length, locale),
      status: 422,
    });
  }

  try {
    /* Die Adresse der Seite, von der es kam, geht mit in die Mail — an ihr ist
       zu sehen, in welcher Sprache geantwortet werden will. */
    const attachments = kind.fileFields
      .filter((field) => files[field])
      .map((field) => ({ field, label: mod.FIELD_LABELS.de[field], file: files[field] }));
    await kind.send(values, attachments, env, `${url.host}${url.pathname}`);
  } catch (err) {
    /* Der Grund gehört ins Log, nicht auf die Seite: er kann die
       Mail-Konfiguration verraten, und der Leser kann mit ihm nichts anfangen.
       Was er stattdessen bekommt, ist der Weg, der noch offen ist. */
    console.error(`${route.kind}: Versand gescheitert`, err);
    return renderForm(await loadForm(env, url), {
      ...page,
      status: 502,
      title: mod.SEND_FAILED[locale].title,
      notice: {
        title: mod.SEND_FAILED[locale].title,
        items: [{
          target: kind.failTarget,
          field: null,
          message: mod.SEND_FAILED[locale].message,
        }],
      },
    });
  }

  return seeOther(thanksFor(env, route));
}
