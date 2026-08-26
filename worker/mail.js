/* Der Versand einer Kontaktanfrage.

   EINE FUNKTION, EIN ANBIETER. Alles, was Resend kennt, steht in sendViaResend()
   — rund zwanzig Zeilen. Ein Wechsel zu Brevo, Mailjet oder Postmark tauscht
   diese Funktion und sonst nichts; sendEnquiry() und der Rest des Workers
   wissen nicht, wer die Mail zustellt.

   ZUR REGION. Resend wählt sie pro Domain, nicht pro Aufruf: eine Domain, die
   im Dashboard auf eu-west-1 angelegt ist, versendet aus Irland, eine auf
   us-east-1 angelegte aus den USA. Es gibt dafür kein Feld in der API, und
   deshalb steht hier keins — die Region ist eine Eigenschaft des Kontos, die
   dieser Code weder setzen noch ablesen kann.

   Sie ist trotzdem eine Aussage, die die Website trifft: datenschutz.html
   nennt den Versandweg beim Namen. Wer die Domain in CONTACT_FROM wechselt
   oder sie in Resend neu anlegt, ändert damit den Satz in der
   Datenschutzerklärung mit — nachsehen lässt sich die Region unter
   https://api.resend.com/domains.

   Unabhängig davon: Kontodaten, Metadaten und Logs — und damit Name, Adresse
   und Text jeder Anfrage — liegen laut Resend in den USA. Das ist eine
   Drittlandsübermittlung und gehört als solche in die Datenschutzerklärung.

   WAS NICHT IN DIE MAIL GEHÖRT. Keine IP, kein User-Agent, kein Zeitstempel
   über das hinaus, was der Mailserver ohnehin setzt. Für die Beantwortung
   einer Anfrage braucht es das nicht, und Art. 5 Abs. 1 lit. c DSGVO sagt,
   dass dann auch nichts davon erhoben wird. */

import { DETAIL_FIELDS, FIELD_LABELS } from "./validate.js";

const RESEND_ENDPOINT = "https://api.resend.com/emails";

/* Der Betreff trägt das Thema, wenn eins gewählt wurde — dann sortiert das
   Postfach von selbst. Ohne Thema bleibt es beim Namen. */
function subjectFor(values) {
  return values.topic
    ? `Kontaktanfrage: ${values.topic} — ${values.name}`
    : `Kontaktanfrage von ${values.name}`;
}

/* Nur-Text, keine HTML-Mail. Die Anfrage ist Fließtext mit einem Kopf aus
   Angaben davor; HTML würde nichts hinzufügen, was ein Postfach nicht schon
   kann, und wäre eine zweite Stelle, an der Nutzereingaben escaped werden
   müssten.

   DER KOPF IST DIE RECHTE SPALTE DER SEITE. Anlage, Anlass, Datenlage und
   Zeitrahmen sind die vier Angaben, nach denen sonst zurückgeschrieben werden
   muss; seit sie auf kontakt.html Felder sind und keine Prosa, kommen sie mit
   und stehen hier über der Nachricht. Jede ist optional, also fehlt jede
   Zeile, die leer geblieben ist — eine Mail mit "Anlage:" und nichts dahinter
   sagt weniger als keine Zeile.

   AUF DEUTSCH, AUCH AUS DER ENGLISCHEN AUSGABE. Die Beschriftungen kommen aus
   FIELD_LABELS.de, weil diese Mail in einem deutschen Postfach gelesen wird und
   nicht von dem, der sie ausgelöst hat. In welcher Sprache geantwortet werden
   will, steht unten in der Adresse der Seite.

   DIE VIER STEHEN NICHT NOCH EINMAL HIER, sondern kommen als DETAIL_FIELDS aus
   validate.js — derselben Liste, aus der das Formular geprüft wird. Eine fünfte
   Angabe wird dort eingetragen und steht damit auch in der Mail; eine Liste an
   zwei Stellen wäre eine Angabe, die geprüft wird und nicht ankommt. */

/* Eine Beschriftung auf die Breite der Spalte gebracht: "Anlage:" wird zu
   "Anlage:      ", damit die Werte in einem Nur-Text-Postfach untereinander
   stehen. */
const pad = (label, width) => `${label}:`.padEnd(width);

function bodyFor(values, source) {
  const labels = FIELD_LABELS.de;
  const head = [
    ["name", values.name],
    ["email", values.email],
    ["company", values.company],
    ["topic", values.topic],
    ...DETAIL_FIELDS.map((field) => [field, values[field]]),
  ];
  /* Die Breite der Beschriftungsspalte: das längste Wort, plus Doppelpunkt und
     ein Leerzeichen. "Unternehmen:" ist mit zwölf Zeichen das längste — aber
     die Zahl wird gerechnet und nicht getippt, damit eine Angabe mit einem
     längeren Namen die Spalte nicht schief stellt. */
  const width = Math.max(...head.map(([field]) => labels[field].length + 2));

  /* Name und E-Mail stehen immer — ohne sie wäre die Anfrage nicht durch die
     Prüfung gekommen. Alles danach steht, wenn es ausgefüllt wurde. */
  const lines = head
    .filter(([, value]) => value)
    .map(([field, value]) => `${pad(labels[field], width)}${value}`);

  /* Die Seite, auf der das Formular stand, statt eines festen Domainnamens.
     Sie ist auch dann richtig, wenn der Worker unter workers.dev läuft oder
     die Domain wechselt — und sie sagt, in welcher Sprache geschrieben wurde:
     eine Anfrage von /en/kontakt.html will eine englische Antwort. */
  lines.push("", values.message, "", "--", `Gesendet über das Kontaktformular auf ${source}`);
  return lines.join("\n");
}

/* ---- Anbieter: Resend ---------------------------------------------------
   Die einzige Stelle, die einen Anbieter kennt. Wirft bei jedem Ausgang, der
   keine zugestellte Mail ist — der Aufrufer entscheidet, was der Leser davon
   sieht. */
async function sendViaResend(env, { from, to, replyTo, subject, text, attachments = [] }) {
  const res = await fetch(RESEND_ENDPOINT, {
    method: "POST",
    headers: {
      authorization: `Bearer ${env.RESEND_API_KEY}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      from,
      to: [to],
      /* Antworten geht an den Absender der Anfrage, nicht an das Postfach,
         aus dem die Benachrichtigung kam. Ein Klick auf "Antworten" trifft
         damit den Menschen, der geschrieben hat. */
      reply_to: replyTo,
      subject,
      text,
      /* Weggelassen, wenn es keine gibt: Resend nimmt ein leeres Array zwar
         an, aber eine Kontaktanfrage hat keine Anhänge und soll auch keine
         leere Liste mitschicken. */
      ...(attachments.length ? { attachments } : {}),
    }),
  });

  if (!res.ok) {
    /* Der Text der Fehlerantwort landet im Log, nicht beim Leser: er kann den
       API-Key-Status oder eine Domain-Konfiguration verraten. */
    const detail = await res.text().catch(() => "");
    throw new Error(`Resend ${res.status}: ${detail.slice(0, 500)}`);
  }
}
/* ------------------------------------------------------------------------ */

export async function sendEnquiry(values, env, source) {
  if (!env.RESEND_API_KEY || !env.CONTACT_FROM || !env.CONTACT_TO) {
    throw new Error("Mailversand nicht konfiguriert: RESEND_API_KEY, CONTACT_FROM oder CONTACT_TO fehlt");
  }

  await sendViaResend(env, {
    from: env.CONTACT_FROM,
    to: env.CONTACT_TO,
    replyTo: values.email,
    subject: subjectFor(values),
    text: bodyFor(values, source),
  });
}

/* ---- Bewerbungen ---------------------------------------------------------

   Dieselbe Leitung, ein Anhang mehr. Was eine Bewerbung von einer Anfrage
   unterscheidet, steht in diesem Abschnitt und nirgends sonst; sendViaResend()
   oben weiß nicht, welche von beiden es gerade zustellt. */

/* base64, in Blöcken.

   Der naheliegende Einzeiler — btoa(String.fromCharCode(...bytes)) — geht bei
   einer Datei dieser Größe nicht: das Spread reicht jedes Byte als eigenes
   Argument weiter, und bei einigen zehntausend Argumenten ist der Stack voll.
   Der Wert ist bis dahin plausibel, weshalb es an einer kleinen Testdatei nicht
   auffällt und an einem echten Lebenslauf schon. 0x8000 Bytes pro Block ist die
   übliche sichere Größe. */
function base64(buffer) {
  const bytes = new Uint8Array(buffer);
  const CHUNK = 0x8000;
  let binary = "";
  for (let i = 0; i < bytes.length; i += CHUNK) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + CHUNK));
  }
  return btoa(binary);
}

/* Der Dateiname, wie er im Postfach ankommt: "Nachname, Vorname — Lebenslauf"
   statt "cv_final_v3(2).pdf". Ein Postfach sortiert nach dem, was im Namen
   steht, und der Name, den ein Anhang mitbringt, ist der des Rechners, von dem
   er kam.

   Der Name des Absenders wird auf das reduziert, was in einem Dateinamen nichts
   kaputt macht — kein Schrägstrich, kein Doppelpunkt, kein Steuerzeichen. Die
   Endung bleibt, wie sie war: sie sagt dem Postfach, womit es zu öffnen ist. */
function attachmentName(person, label, original) {
  const dot = original.lastIndexOf(".");
  const ext = dot === -1 ? "" : original.slice(dot).toLowerCase();
  const safe = person.replace(/[^\p{L}\p{N} .-]/gu, "").trim().slice(0, 60) || "Bewerbung";
  return `${safe} — ${label}${ext}`;
}

function applicationSubject(values) {
  return `Bewerbung: ${values.position} — ${values.name}`;
}

/* Der Fließtext. Die Anhänge stehen mit Namen und Größe drin, damit im Postfach
   auf einen Blick zu sehen ist, was mitgekommen sein sollte — eine Mail, der
   ein Anhang unterwegs verloren geht, sieht sonst vollständig aus. */
function applicationBody(values, files, source) {
  const lines = [
    `Name:      ${values.name}`,
    `E-Mail:    ${values.email}`,
    `Stelle:    ${values.position}`,
  ];
  if (values.profile) lines.push(`Profil:    ${withScheme(values.profile)}`);
  if (values.portfolio) lines.push(`Portfolio: ${withScheme(values.portfolio)}`);

  lines.push("", "Anhänge:");
  for (const { label, file } of files) {
    lines.push(`  - ${label}: ${file.name} (${Math.round(file.size / 1024)} kB)`);
  }

  if (values.message) lines.push("", values.message);
  lines.push("", "--", `Gesendet über das Bewerbungsformular auf ${source}`);
  return lines.join("\n");
}

/* Ein Link ohne Schema ist in einer Nur-Text-Mail nicht anklickbar, und
   "github.com/name" ist das, was Menschen in ein Feld schreiben. */
const withScheme = (url) => (/^https?:\/\//i.test(url) ? url : `https://${url}`);

/* files: [{ field, label, file }] — die Datei ist ein File aus formData().
   Sie wird hier erst gelesen, also so spät wie möglich: eine Bewerbung, die an
   der Validierung scheitert, hat nie im Speicher gestanden. */
export async function sendApplication(values, files, env, source) {
  const to = env.APPLY_TO || env.CONTACT_TO;
  if (!env.RESEND_API_KEY || !env.CONTACT_FROM || !to) {
    throw new Error("Mailversand nicht konfiguriert: RESEND_API_KEY, CONTACT_FROM oder APPLY_TO fehlt");
  }

  const attachments = [];
  for (const { label, file } of files) {
    attachments.push({
      filename: attachmentName(values.name, label, file.name),
      content: base64(await file.arrayBuffer()),
    });
  }

  await sendViaResend(env, {
    from: env.CONTACT_FROM,
    to,
    replyTo: values.email,
    subject: applicationSubject(values),
    text: applicationBody(values, files, source),
    attachments,
  });
}
