/* Was aus dem Kontaktformular ankommen darf, und was der Leser liest, wenn es
   das nicht tut.

   Diese Datei kennt keine Requests und kein HTML. Sie nimmt die Felder, wie
   sie im Formular heißen, und gibt zurück, was falsch ist — damit die Regeln
   an einer Stelle stehen und einzeln lesbar bleiben.

   DIE FEHLERTEXTE sind die des Design Systems: components/forms.html zeigt
   "Bitte geben Sie eine gültige E-Mail-Adresse an." und "Bitte schreiben Sie
   uns, worum es geht." als Beispiele im Specimen. Sie stehen hier wörtlich.
   scripts/check-form-contract.py hält beide Seiten aneinander. */

/* Die fünf Themen aus dem <select> auf patterns/kontakt.html. Ein Wert, der
   nicht darunter ist, kommt nicht aus dem Formular — er wird verworfen und
   nicht etwa gemeldet, denn es gibt nichts, was der Leser daran korrigieren
   könnte. */
export const TOPICS = [
  "Discovery-Workshop",
  "Datenfundament",
  "Predictive Maintenance",
  "Asset Performance",
  "Etwas anderes",
];

/* Obergrenzen. Sie sind großzügig für einen Menschen und eng für ein Skript:
   5 000 Zeichen sind rund zwei Schreibmaschinenseiten. Überschreiten heißt
   melden, nicht abschneiden — eine still gekürzte Nachricht wäre ein
   Datenverlust, den niemand bemerkt. */
export const LIMITS = { name: 120, email: 200, company: 160, message: 5000 };

/* Die Mindestlänge der Nachricht. "Hi" ist keine Anfrage, und der Platzhalter
   im Feld verspricht "ein paar Sätze". */
const MESSAGE_MIN = 10;

/* Absichtlich grob. Eine Adresse endgültig zu prüfen kann nur die Zustellung;
   was hier steht, fängt den Tippfehler ab und lässt alles durch, was
   zustellbar sein könnte. Kein Punkt-Zwang in der Domain, denn Intranet-
   Adressen haben keinen — aber genau ein @, nichts Leeres darum herum und
   keine Leerzeichen. */
const EMAIL = /^[^\s@]+@[^\s@]+$/;

/* Steuerzeichen fliegen raus. Ein \r\n in einem Namen wäre eine
   Header-Injection, sobald der Name in einer Kopfzeile der Mail landet, und
   sonst ist ein Steuerzeichen dort ohnehin nichts. In der Nachricht bleiben
   Zeilenumbrüche erhalten — sie sind dort Inhalt, nicht Syntax. */
const CONTROL = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g;

function clean(value, { keepNewlines = false } = {}) {
  if (typeof value !== "string") return "";
  let out = value.replace(CONTROL, "");
  if (!keepNewlines) out = out.replace(/[\r\n]+/g, " ");
  return out.trim();
}

/* Die Zahlwörter für die Überschrift der Fehlerübersicht. Das Specimen
   schreibt "Bitte prüfen Sie zwei Angaben" — also ein Wort, keine Ziffer. Mehr
   als vier Fehler kann dieses Formular nicht haben: es hat vier Felder, die
   falsch sein können. */
const COUNT_WORDS = ["null", "eine", "zwei", "drei", "vier"];

export function summaryTitle(count) {
  if (count === 1) return "Bitte prüfen Sie eine Angabe";
  return `Bitte prüfen Sie ${COUNT_WORDS[count] || String(count)} Angaben`;
}

/* Nimmt die rohen Formularwerte und gibt beides zurück: die bereinigten Werte,
   mit denen weitergearbeitet wird, und die Liste der Fehler in der Reihenfolge,
   in der die Felder im Formular stehen — die Übersicht liest sich dann wie das
   Formular. */
export function validate(raw) {
  const values = {
    name: clean(raw.name),
    email: clean(raw.email),
    company: clean(raw.company),
    topic: clean(raw.topic),
    message: clean(raw.message, { keepNewlines: true }),
  };

  /* Ein Thema, das nicht aus der Liste stammt, ist kein Fehler des Lesers,
     sondern kein Thema. */
  if (!TOPICS.includes(values.topic)) values.topic = "";

  const errors = [];
  const fail = (field, target, message) => errors.push({ field, target, message });

  if (!values.name) {
    fail("name", "f-name", "Bitte nennen Sie uns Ihren Namen.");
  } else if (values.name.length > LIMITS.name) {
    fail("name", "f-name", `Bitte kürzen Sie Ihren Namen auf ${LIMITS.name} Zeichen.`);
  }

  if (!values.email) {
    fail("email", "f-mail", "Bitte geben Sie eine E-Mail-Adresse an, damit wir antworten können.");
  } else if (values.email.length > LIMITS.email || !EMAIL.test(values.email)) {
    fail("email", "f-mail", "Bitte geben Sie eine gültige E-Mail-Adresse an.");
  }

  if (values.company.length > LIMITS.company) {
    fail("company", "f-firma", `Bitte kürzen Sie den Namen des Unternehmens auf ${LIMITS.company} Zeichen.`);
  }

  if (!values.message) {
    fail("message", "f-msg", "Bitte schreiben Sie uns, worum es geht.");
  } else if (values.message.length < MESSAGE_MIN) {
    fail("message", "f-msg", "Bitte schreiben Sie uns etwas mehr — ein paar Sätze genügen.");
  } else if (values.message.length > LIMITS.message) {
    fail("message", "f-msg",
         `Ihre Nachricht ist länger als ${LIMITS.message.toLocaleString("de-DE")} Zeichen. Bitte kürzen Sie sie.`);
  }

  return { values, errors };
}

/* Die Beschriftung, unter der ein Feld in der Übersicht auftaucht. Sie ist das
   Label aus dem Formular, denn die Übersicht ist ein Index auf das Formular und
   muss dessen Wörter benutzen. */
export const FIELD_LABELS = {
  name: "Name",
  email: "E-Mail",
  company: "Unternehmen",
  message: "Nachricht",
};
