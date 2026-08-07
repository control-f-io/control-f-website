/* Was aus dem Kontaktformular ankommen darf, und was der Leser liest, wenn es
   das nicht tut.

   Diese Datei kennt keine Requests und kein HTML. Sie nimmt die Felder, wie
   sie im Formular heißen, und gibt zurück, was falsch ist — damit die Regeln
   an einer Stelle stehen und einzeln lesbar bleiben.

   ZWEI AUSGABEN, ZWEI SPRACHEN. Es gibt das Formular zweimal: auf
   /kontakt.html und, seit der englischen Ausgabe, auf /en/kontakt.html. Beide
   posten an die eigene Adresse, beide haben dieselben Feldnamen, dieselben ids
   und dieselbe Spamfalle — build-i18n.py ändert nur die Wörter. Also ändern
   sich auch hier nur die Wörter: jede Tabelle in dieser Datei hat einen
   de- und einen en-Zweig, und die Regeln darüber sind einmal geschrieben.

   Ein englischer Leser, der das Feld leer lässt, bekommt einen englischen
   Satz. Alles andere wäre eine deutsche Fehlermeldung auf einer englischen
   Seite — und die Übersicht ist ein Index auf das Formular, sie muss dessen
   Wörter benutzen.

   DIE FEHLERTEXTE der deutschen Ausgabe sind die des Design Systems:
   components/forms.html zeigt "Bitte geben Sie eine gültige E-Mail-Adresse
   an." und "Bitte schreiben Sie uns, worum es geht." als Beispiele im
   Specimen. Sie stehen hier wörtlich. Die englischen haben kein solches
   Specimen — die Komponentenseiten gibt es nur auf Deutsch — und sind hier
   ihre Übersetzung. scripts/check-form-contract.py hält beide Seiten
   aneinander, für beide Ausgaben. */

/* Die Sprache, in der geantwortet wird, wenn ein Pfad keine nennt. */
export const DEFAULT_LOCALE = "de";

/* Die fünf Themen aus dem <select>, je Ausgabe. Ein Wert, der nicht darunter
   ist, kommt nicht aus dem Formular — er wird verworfen und nicht etwa
   gemeldet, denn es gibt nichts, was der Leser daran korrigieren könnte.

   Die beiden Listen stehen in derselben Reihenfolge wie die Optionen auf der
   jeweiligen Seite. Das ist keine Höflichkeit gegenüber dem Leser, sondern
   Voraussetzung: render.js wählt die Option beim Zurückschreiben über ihre
   Position, weil CSS keinen Textvergleich kennt. check-form-contract.py
   vergleicht beide Listen der Reihe nach gegen beide Formulare. */
export const TOPICS = {
  de: [
    "Discovery-Workshop",
    "Datenfundament",
    "Predictive Maintenance",
    "Asset Performance",
    "Etwas anderes",
  ],
  en: [
    "Discovery workshop",
    "Data foundation",
    "Predictive Maintenance",
    "Asset Performance",
    "Something else",
  ],
};

/* Obergrenzen. Sie sind großzügig für einen Menschen und eng für ein Skript:
   5 000 Zeichen sind rund zwei Schreibmaschinenseiten. Überschreiten heißt
   melden, nicht abschneiden — eine still gekürzte Nachricht wäre ein
   Datenverlust, den niemand bemerkt.

   Sie gelten für beide Ausgaben: eine Grenze ist eine Eigenschaft des Feldes,
   nicht der Sprache. */
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
const COUNT_WORDS = {
  de: ["null", "eine", "zwei", "drei", "vier"],
  en: ["no", "one", "two", "three", "four"],
};

export function summaryTitle(count, locale = DEFAULT_LOCALE) {
  const words = COUNT_WORDS[locale] || COUNT_WORDS[DEFAULT_LOCALE];
  const word = words[count] || String(count);
  if (locale === "en") {
    return count === 1 ? "Please check one entry" : `Please check ${word} entries`;
  }
  return count === 1 ? "Bitte prüfen Sie eine Angabe" : `Bitte prüfen Sie ${word} Angaben`;
}

/* Die Meldungen, je Ausgabe. Als Funktionen, weil drei von ihnen eine Zahl
   tragen — und die Zahl in der Sprache gesetzt wird, in der der Satz steht:
   5 000 auf Deutsch, 5,000 auf Englisch. */
const MESSAGES = {
  de: {
    nameMissing: () => "Bitte nennen Sie uns Ihren Namen.",
    nameLong: (n) => `Bitte kürzen Sie Ihren Namen auf ${n} Zeichen.`,
    emailMissing: () => "Bitte geben Sie eine E-Mail-Adresse an, damit wir antworten können.",
    emailInvalid: () => "Bitte geben Sie eine gültige E-Mail-Adresse an.",
    companyLong: (n) => `Bitte kürzen Sie den Namen des Unternehmens auf ${n} Zeichen.`,
    messageMissing: () => "Bitte schreiben Sie uns, worum es geht.",
    messageShort: () => "Bitte schreiben Sie uns etwas mehr — ein paar Sätze genügen.",
    messageLong: (n) =>
      `Ihre Nachricht ist länger als ${n.toLocaleString("de-DE")} Zeichen. Bitte kürzen Sie sie.`,
  },
  en: {
    nameMissing: () => "Please tell us your name.",
    nameLong: (n) => `Please shorten your name to ${n} characters.`,
    emailMissing: () => "Please give us an email address so that we can reply.",
    emailInvalid: () => "Please enter a valid email address.",
    companyLong: (n) => `Please shorten the company name to ${n} characters.`,
    messageMissing: () => "Please tell us what this is about.",
    messageShort: () => "Please write a little more — a few sentences are enough.",
    messageLong: (n) =>
      `Your message is longer than ${n.toLocaleString("en-GB")} characters. Please shorten it.`,
  },
};

/* Was der Leser sieht, wenn nicht seine Eingabe das Problem war, sondern der
   Versand.

   ES GIBT KEINEN ZWEITEN WEG MEHR, auf den hier verwiesen werden könnte. Diese
   Meldung nannte die Adresse aus der Spalte "Direkt" und zeigte auf deren
   Überschrift; beides ist von der Seite entfernt, weil eine Anfrage über das
   Formular kommen soll. Ein Verweis auf eine id, die es nicht mehr gibt, wäre
   ein Link ins Leere gewesen — der Eintrag zeigt jetzt auf "schreiben", die
   Überschrift über dem Formular selbst, und beide Ausgaben tragen diese id.

   Was der Satz noch verspricht, ist deshalb nur, was er halten kann: dass die
   Eingaben stehen bleiben und ein zweiter Versuch sich lohnt. Das Impressum
   steht in jedem Footer und nennt die Adresse für den Fall, dass es länger
   nicht geht; darauf hier zu zeigen hieße, den Weg wieder aufzumachen, den die
   Seite gerade geschlossen hat. */
export const SEND_FAILED = {
  de: {
    title: "Ihre Nachricht konnte gerade nicht gesendet werden",
    message: "Ihre Angaben stehen noch im Formular. Bitte versuchen Sie es in einigen Minuten noch einmal.",
  },
  en: {
    title: "Your message could not be sent just now",
    message: "Your details are still in the form. Please try again in a few minutes.",
  },
};

/* Die Antwort der Bremse. Kein HTML: sie greift, bevor irgendetwas geparst
   wurde, und ein Mensch bekommt sie praktisch nie zu sehen. */
export const RATE_LIMITED = {
  de: "Zu viele Anfragen. Bitte versuchen Sie es in einer Minute erneut.",
  en: "Too many requests. Please try again in a minute.",
};

/* Nimmt die rohen Formularwerte und gibt beides zurück: die bereinigten Werte,
   mit denen weitergearbeitet wird, und die Liste der Fehler in der Reihenfolge,
   in der die Felder im Formular stehen — die Übersicht liest sich dann wie das
   Formular. */
export function validate(raw, locale = DEFAULT_LOCALE) {
  const say = MESSAGES[locale] || MESSAGES[DEFAULT_LOCALE];
  const topics = TOPICS[locale] || TOPICS[DEFAULT_LOCALE];

  const values = {
    name: clean(raw.name),
    email: clean(raw.email),
    company: clean(raw.company),
    topic: clean(raw.topic),
    message: clean(raw.message, { keepNewlines: true }),
  };

  /* Ein Thema, das nicht aus der Liste stammt, ist kein Fehler des Lesers,
     sondern kein Thema. Geprüft wird gegen die Liste der Ausgabe, auf der das
     Formular stand: "Data foundation" kommt von /en/kontakt.html und von
     nirgends sonst. */
  if (!topics.includes(values.topic)) values.topic = "";

  const errors = [];
  const fail = (field, target, message) => errors.push({ field, target, message });

  if (!values.name) {
    fail("name", "f-name", say.nameMissing());
  } else if (values.name.length > LIMITS.name) {
    fail("name", "f-name", say.nameLong(LIMITS.name));
  }

  if (!values.email) {
    fail("email", "f-mail", say.emailMissing());
  } else if (values.email.length > LIMITS.email || !EMAIL.test(values.email)) {
    fail("email", "f-mail", say.emailInvalid());
  }

  if (values.company.length > LIMITS.company) {
    fail("company", "f-firma", say.companyLong(LIMITS.company));
  }

  if (!values.message) {
    fail("message", "f-msg", say.messageMissing());
  } else if (values.message.length < MESSAGE_MIN) {
    fail("message", "f-msg", say.messageShort());
  } else if (values.message.length > LIMITS.message) {
    fail("message", "f-msg", say.messageLong(LIMITS.message));
  }

  return { values, errors };
}

/* Die Beschriftung, unter der ein Feld in der Übersicht auftaucht. Sie ist das
   Label aus dem Formular, denn die Übersicht ist ein Index auf das Formular und
   muss dessen Wörter benutzen — auf jeder der beiden Seiten die ihren. */
export const FIELD_LABELS = {
  de: {
    name: "Name",
    email: "E-Mail",
    company: "Unternehmen",
    message: "Nachricht",
  },
  en: {
    name: "Name",
    email: "Email",
    company: "Company",
    message: "Message",
  },
};
