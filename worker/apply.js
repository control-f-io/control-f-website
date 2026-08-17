/* Was aus dem Bewerbungsformular ankommen darf.

   Dieselbe Rolle wie validate.js für das Kontaktformular, und derselbe
   Aufbau: keine Requests, kein HTML, jede Tabelle mit einem de- und einem
   en-Zweig. Was hier anders ist, ist der Anhang — eine Bewerbung bringt
   Dateien mit, und Dateien haben Regeln, die Text nicht hat.

   WAS VERLANGT WIRD, und warum in dieser Aufteilung:

     Lebenslauf     Pflicht. Eine Datei.
     Anschreiben    Pflicht. Eine Datei. Die Karriereseite hat bis 2026-08-07
                    das Gegenteil gesagt ("Brauchen wir ein Anschreiben?
                    Nein."); diese Antwort ist mit diesem Formular umgeschrieben
                    worden, damit Seite und Formular dasselbe verlangen.
     Ein Nachweis   Pflicht, aber nicht welcher: ein Profil (LinkedIn oder
                    irgendeine andere Adresse), ein Portfolio (GitHub, GitLab,
                    eine eigene Seite) oder eine hochgeladene Arbeit. Wer nichts
                    Öffentliches hat — aus der Industrie, aus der Forschung
                    unter NDA — wird von einer einzelnen Pflichtangabe
                    ausgeschlossen, von "irgendeines der drei" nicht.

   WAS NICHT VERLANGT WIRD. Kein Foto, kein Geburtsdatum, kein Familienstand,
   keine Telefonnummer. Die Karriereseite nennt die ersten drei ausdrücklich und
   begründet sie mit dem AGG und mit Datensparsamkeit; die vierte braucht
   niemand, um auf eine Mail zu antworten. Ein Feld, das nicht existiert, ist
   die einzige Form von Datensparsamkeit, die nicht schiefgehen kann.

   DATEIEN LASSEN SICH NICHT ZURÜCKSCHREIBEN. Ein Browser füllt ein
   <input type="file"> aus keinem Server-Response wieder — das darf er nicht,
   sonst könnte eine Seite sich selbst Dateien vom Rechner des Lesers
   zuschicken. Ein Fehler in irgendeinem Feld kostet also die Auswahl der
   Dateien. Deshalb wird hier alles auf einmal geprüft und alles auf einmal
   gemeldet: wer zweimal hintereinander anhängen muss, hat einen Grund,
   aufzuhören. Das Formular sagt das vorher. */

export const DEFAULT_LOCALE = "de";

/* Die offenen Stellen aus dem <select>, je Ausgabe, plus die
   Initiativbewerbung. Wie bei TOPICS in validate.js: gleiche Reihenfolge wie
   die Optionen auf der Seite, weil render.js die Auswahl über ihre Position
   zurückschreibt, und check-form-contract.py vergleicht beide Listen.

   Eine Stelle, die auf karriere.html dazukommt, gehört hier hinein — sonst
   wird sie beim Absenden verworfen und die Bewerbung landet ohne Stelle im
   Postfach. Der Check sagt es, weil er die Optionen des Formulars gegen diese
   Liste hält, und das Formular und karriere.html teilen sich die Namen. */
export const POSITIONS = {
  de: [
    "Data Engineer (m/w/d)",
    "Machine Learning Engineer (m/w/d)",
    "DevOps Engineer (m/w/d)",
    "Werkstudent Frontend (m/w/d)",
    "Initiativbewerbung",
  ],
  en: [
    "Data Engineer (m/f/d)",
    "Machine Learning Engineer (m/f/d)",
    "DevOps Engineer (m/f/d)",
    "Working Student Frontend (m/f/d)",
    "Speculative application",
  ],
};

export const LIMITS = { name: 120, email: 200, url: 400, message: 3000 };

/* Die Dateigrenzen.

   PRO DATEI 5 MB und ZUSAMMEN 12 MB. Beides ist reichlich für einen
   Lebenslauf als PDF und knapp genug, dass niemand versehentlich ein
   Video anhängt. Die Obergrenze kommt aber nicht von hier, sondern von
   Resend: dort ist bei 40 MB pro Nachricht Schluss, und der Anhang wird für
   den Versand base64-kodiert, was ihn um ein Drittel aufbläht. 12 MB roh sind
   rund 16 MB kodiert — mit Abstand darunter, auch wenn die Mail noch Text
   trägt.

   Überschreiten heißt melden, nicht abschneiden. Eine still verworfene Datei
   wäre eine Bewerbung ohne Lebenslauf, und weder der Absender noch das
   Postfach würde es bemerken. */
export const FILE_LIMITS = { each: 5 * 1024 * 1024, total: 12 * 1024 * 1024 };

/* Was angenommen wird. Die Endung, nicht der content-type: den setzt der
   Browser aus seiner eigenen Tabelle, und für .docx liefern verschiedene
   Browser verschiedene Angaben. Die Endung ist das, was der Absender selbst
   sieht, und damit das, worüber eine Fehlermeldung sprechen kann. */
export const FILE_TYPES = [".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt"];

/* Die drei Dateifelder. `required` ist die Antwort auf die Frage, die das
   Formular stellt; `label` ist, wie das Feld in der Fehlerübersicht heißt. */
export const FILE_FIELDS = ["cv", "letter", "papers"];

const CONTROL = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g;
const EMAIL = /^[^\s@]+@[^\s@]+$/;

/* Absichtlich grob, wie die Adressprüfung. Was ausgeschlossen wird, sind
   Leerzeichen und alles ohne Punkt — also der Tippfehler und das
   hingeschriebene Wort. Ein Schema wird nicht verlangt: "github.com/name" ist
   das, was Menschen schreiben, und mail.js setzt https:// davor, wenn keins
   dasteht. */
const URLISH = /^[^\s]+\.[^\s]+$/;

function clean(value, { keepNewlines = false } = {}) {
  if (typeof value !== "string") return "";
  let out = value.replace(CONTROL, "");
  if (!keepNewlines) out = out.replace(/[\r\n]+/g, " ");
  return out.trim();
}

const COUNT_WORDS = {
  de: ["null", "eine", "zwei", "drei", "vier", "fünf", "sechs", "sieben"],
  en: ["no", "one", "two", "three", "four", "five", "six", "seven"],
};

export function summaryTitle(count, locale = DEFAULT_LOCALE) {
  const words = COUNT_WORDS[locale] || COUNT_WORDS[DEFAULT_LOCALE];
  const word = words[count] || String(count);
  if (locale === "en") {
    return count === 1 ? "Please check one entry" : `Please check ${word} entries`;
  }
  return count === 1 ? "Bitte prüfen Sie eine Angabe" : `Bitte prüfen Sie ${word} Angaben`;
}

const megabytes = (bytes, locale) =>
  `${(bytes / 1024 / 1024).toLocaleString(locale === "en" ? "en-GB" : "de-DE")} MB`;

const MESSAGES = {
  de: {
    nameMissing: () => "Bitte nennen Sie uns Ihren Namen.",
    nameLong: (n) => `Bitte kürzen Sie Ihren Namen auf ${n} Zeichen.`,
    emailMissing: () => "Bitte geben Sie eine E-Mail-Adresse an, damit wir antworten können.",
    emailInvalid: () => "Bitte geben Sie eine gültige E-Mail-Adresse an.",
    positionMissing: () => "Bitte wählen Sie, worauf Sie sich bewerben.",
    urlInvalid: () => "Das sieht nicht nach einer Adresse aus. Bitte prüfen Sie den Link.",
    urlLong: (n) => `Bitte kürzen Sie den Link auf ${n} Zeichen.`,
    proofMissing: () =>
      "Bitte hinterlassen Sie uns eine Spur Ihrer Arbeit: ein Profil, ein Portfolio oder eine hochgeladene Arbeit — eines davon genügt.",
    cvMissing: () => "Bitte hängen Sie Ihren Lebenslauf an.",
    letterMissing: () => "Bitte hängen Sie Ihr Anschreiben an.",
    fileType: (types) => `Bitte hängen Sie eine Datei in einem dieser Formate an: ${types}.`,
    fileLarge: (size) => `Diese Datei ist größer als ${size}. Bitte hängen Sie eine kleinere an.`,
    filesLarge: (size) => `Ihre Anhänge sind zusammen größer als ${size}. Bitte lassen Sie etwas weg.`,
    messageLong: (n) => `Ihre Nachricht ist länger als ${n.toLocaleString("de-DE")} Zeichen. Bitte kürzen Sie sie.`,
  },
  en: {
    nameMissing: () => "Please tell us your name.",
    nameLong: (n) => `Please shorten your name to ${n} characters.`,
    emailMissing: () => "Please give us an email address so that we can reply.",
    emailInvalid: () => "Please enter a valid email address.",
    positionMissing: () => "Please choose what you are applying for.",
    urlInvalid: () => "That does not look like an address. Please check the link.",
    urlLong: (n) => `Please shorten the link to ${n} characters.`,
    proofMissing: () =>
      "Please leave us a trace of your work: a profile, a portfolio or an uploaded paper — any one of them will do.",
    cvMissing: () => "Please attach your CV.",
    letterMissing: () => "Please attach your cover letter.",
    fileType: (types) => `Please attach a file in one of these formats: ${types}.`,
    fileLarge: (size) => `This file is larger than ${size}. Please attach a smaller one.`,
    filesLarge: (size) => `Your attachments come to more than ${size} together. Please leave something out.`,
    messageLong: (n) => `Your message is longer than ${n.toLocaleString("en-GB")} characters. Please shorten it.`,
  },
};

export const SEND_FAILED = {
  de: {
    title: "Ihre Bewerbung konnte gerade nicht gesendet werden",
    message: "Bitte versuchen Sie es in einigen Minuten noch einmal — oder schicken Sie uns Ihre Unterlagen direkt an info@control-f.io.",
  },
  en: {
    title: "Your application could not be sent just now",
    message: "Please try again in a few minutes — or send your documents directly to info@control-f.io.",
  },
};

export const RATE_LIMITED = {
  de: "Zu viele Anfragen. Bitte versuchen Sie es in einer Minute erneut.",
  en: "Too many requests. Please try again in a minute.",
};

/* Die Felder, wie render.js sie im Dokument findet. Dieselbe Form wie die
   Tabelle des Kontaktformulars; `kind: "file"` ist neu und heißt: nicht
   zurückschreiben, das kann der Browser nicht. */
export const FIELDS = {
  name:      { input: "#b-name",    wrapper: '[data-field="name"]',      kind: "input" },
  email:     { input: "#b-mail",    wrapper: '[data-field="email"]',     kind: "input" },
  position:  { input: "#b-stelle",  wrapper: '[data-field="position"]',  kind: "select" },
  profile:   { input: "#b-profil",  wrapper: '[data-field="profile"]',   kind: "input" },
  portfolio: { input: "#b-portfolio", wrapper: '[data-field="portfolio"]', kind: "input" },
  cv:        { input: "#b-cv",      wrapper: '[data-field="cv"]',        kind: "file" },
  letter:    { input: "#b-anschreiben", wrapper: '[data-field="letter"]', kind: "file" },
  papers:    { input: "#b-arbeiten", wrapper: '[data-field="papers"]',   kind: "file" },
  message:   { input: "#b-msg",     wrapper: '[data-field="message"]',   kind: "textarea" },
};

export const FIELD_LABELS = {
  de: {
    name: "Name",
    email: "E-Mail",
    position: "Stelle",
    profile: "Profil",
    portfolio: "Portfolio",
    cv: "Lebenslauf",
    letter: "Anschreiben",
    papers: "Arbeiten",
    message: "Nachricht",
  },
  en: {
    name: "Name",
    email: "Email",
    position: "Position",
    profile: "Profile",
    portfolio: "Portfolio",
    cv: "CV",
    letter: "Cover letter",
    papers: "Papers",
    message: "Message",
  },
};

/* Eine hochgeladene Datei, so weit geprüft, wie es ohne ihren Inhalt geht.
   Gibt {file, error} zurück: die Datei, wenn sie zählt, und die Meldung, wenn
   sie nicht durchgeht. Beides kann leer sein — ein leeres optionales Feld ist
   weder das eine noch das andere. */
function checkFile(entry, say, locale) {
  /* formData() liefert für ein leeres <input type="file"> je nach Browser
     nichts oder eine Datei mit dem Namen "" und der Größe 0. Beides heißt:
     nicht ausgefüllt. */
  if (!entry || typeof entry === "string" || !entry.name || entry.size === 0) {
    return { file: null, error: null };
  }
  const dot = entry.name.lastIndexOf(".");
  const ext = dot === -1 ? "" : entry.name.slice(dot).toLowerCase();
  if (!FILE_TYPES.includes(ext)) {
    return { file: null, error: say.fileType(FILE_TYPES.join(", ")) };
  }
  if (entry.size > FILE_LIMITS.each) {
    return { file: null, error: say.fileLarge(megabytes(FILE_LIMITS.each, locale)) };
  }
  return { file: entry, error: null };
}

/* Nimmt die rohen Werte und die drei Dateien und gibt zurück, was falsch ist —
   in der Reihenfolge, in der die Felder im Formular stehen. */
export function validate(raw, uploads, locale = DEFAULT_LOCALE) {
  const say = MESSAGES[locale] || MESSAGES[DEFAULT_LOCALE];
  const positions = POSITIONS[locale] || POSITIONS[DEFAULT_LOCALE];

  const values = {
    name: clean(raw.name),
    email: clean(raw.email),
    position: clean(raw.position),
    profile: clean(raw.profile),
    portfolio: clean(raw.portfolio),
    message: clean(raw.message, { keepNewlines: true }),
  };

  if (!positions.includes(values.position)) values.position = "";

  const errors = [];
  const fail = (field, target, message) => errors.push({ field, target, message });

  if (!values.name) {
    fail("name", "b-name", say.nameMissing());
  } else if (values.name.length > LIMITS.name) {
    fail("name", "b-name", say.nameLong(LIMITS.name));
  }

  if (!values.email) {
    fail("email", "b-mail", say.emailMissing());
  } else if (values.email.length > LIMITS.email || !EMAIL.test(values.email)) {
    fail("email", "b-mail", say.emailInvalid());
  }

  if (!values.position) fail("position", "b-stelle", say.positionMissing());

  for (const [field, target] of [["profile", "b-profil"], ["portfolio", "b-portfolio"]]) {
    if (!values[field]) continue;
    if (values[field].length > LIMITS.url) {
      fail(field, target, say.urlLong(LIMITS.url));
    } else if (!URLISH.test(values[field])) {
      fail(field, target, say.urlInvalid());
    }
  }

  const files = {};
  for (const field of FILE_FIELDS) {
    const { file, error } = checkFile(uploads[field], say, locale);
    if (error) fail(field, FIELDS[field].input.slice(1), error);
    if (file) files[field] = file;
  }

  if (!files.cv && !errors.some((e) => e.field === "cv")) {
    fail("cv", "b-cv", say.cvMissing());
  }
  if (!files.letter && !errors.some((e) => e.field === "letter")) {
    fail("letter", "b-anschreiben", say.letterMissing());
  }

  /* Irgendein Nachweis. Die Meldung hängt am Profilfeld, weil das das erste
     der drei ist — die Übersicht ist ein Index auf das Formular und muss
     irgendwohin zeigen; der Satz nennt alle drei Wege. */
  if (!values.profile && !values.portfolio && !files.papers) {
    fail("profile", "b-profil", say.proofMissing());
  }

  const total = Object.values(files).reduce((sum, f) => sum + f.size, 0);
  if (total > FILE_LIMITS.total) {
    fail("cv", "b-cv", say.filesLarge(megabytes(FILE_LIMITS.total, locale)));
  }

  if (values.message.length > LIMITS.message) {
    fail("message", "b-msg", say.messageLong(LIMITS.message));
  }

  return { values, files, errors };
}
