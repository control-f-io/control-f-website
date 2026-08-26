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

/* Die vier Angaben aus der rechten Spalte teilen sich eine Grenze, weil sie
   sich alles andere auch teilen: einzeilige Felder, alle optional, keins mit
   einer eigenen Regel. 300 Zeichen sind rund drei Zeilen — mehr, als in ein
   <input> sinnvoll hineingeht, und wer mehr zu sagen hat, hat das
   Nachrichtenfeld daneben. */
export const DETAIL_LIMIT = 300;

/* Ihre Namen an einer Stelle. Die Reihenfolge ist die der Spalte, und die
   Fehlerübersicht liest sich in ihr — sie steht unter den vier Pflichtfeldern
   der linken Spalte, so wie die Spalte rechts davon steht. */
export const DETAIL_FIELDS = ["asset", "occasion", "data", "timeframe"];

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
   schreibt "Bitte prüfen Sie zwei Angaben" — also ein Wort, keine Ziffer.

   ACHT, SEIT DIE RECHTE SPALTE FELDER HAT. Hier stand einmal "mehr als vier
   Fehler kann dieses Formular nicht haben", und das stimmte, solange es vier
   Felder gab, die falsch sein konnten. Es sind acht: Name, E-Mail, Unternehmen,
   Nachricht und die vier Angaben aus der Spalte daneben. Das Thema kommt nicht
   dazu — ein Wert außerhalb der Liste wird verworfen und nicht gemeldet.
   Die Liste ist trotzdem kein Zaun: summaryTitle() fällt auf die Ziffer
   zurück, wenn sie zu kurz ist, statt "undefined Angaben" zu schreiben. */
const COUNT_WORDS = {
  de: ["null", "eine", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht"],
  en: ["no", "one", "two", "three", "four", "five", "six", "seven", "eight"],
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
    /* Eine Meldung für alle vier Angaben der rechten Spalte, ohne das Feld zu
       nennen: in der Übersicht steht seine Beschriftung schon davor, und am
       Feld selbst steht sie eine Zeile darüber. Vier fast gleiche Sätze wären
       vier Stellen, an denen dieselbe Zahl gepflegt werden müsste. */
    detailLong: (n) => `Bitte kürzen Sie diese Angabe auf ${n} Zeichen.`,
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
    detailLong: (n) => `Please shorten this entry to ${n} characters.`,
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

  /* Die vier Angaben der rechten Spalte, in einer Schleife statt vierfach
     hingeschrieben: sie werden gleich bereinigt, gleich geprüft und gleich
     gemeldet. Einzeilige Felder, also ohne keepNewlines — ein Zeilenumbruch
     kann hier nur aus einer Zwischenablage kommen und ist dann Formatierung,
     kein Inhalt. */
  for (const field of DETAIL_FIELDS) values[field] = clean(raw[field]);

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

  /* Leer ist bei diesen vieren kein Fehler, sondern die Voreinstellung. Das
     Einzige, was schiefgehen kann, ist Länge — und das Ziel des Eintrags ist
     die id des Feldes, die in FIELDS steht, damit sie nicht ein zweites Mal
     hingeschrieben wird. */
  for (const field of DETAIL_FIELDS) {
    if (values[field].length > DETAIL_LIMIT) {
      fail(field, FIELDS[field].input.slice(1), say.detailLong(DETAIL_LIMIT));
    }
  }

  return { values, errors };
}

/* Welches Eingabefeld zu welchem Feldnamen gehört, und in welchem Wrapper es
   steckt. render.js liest diese Tabelle, statt sie zu besitzen: es gibt zwei
   Formulare auf dieser Website und nur eine Mechanik, die Fehler in eine Seite
   schreibt. Die des Bewerbungsformulars steht in apply.js. */
export const FIELDS = {
  name:      { input: "#f-name",   wrapper: '[data-field="name"]',      kind: "input" },
  email:     { input: "#f-mail",   wrapper: '[data-field="email"]',     kind: "input" },
  company:   { input: "#f-firma",  wrapper: '[data-field="company"]',   kind: "input" },
  topic:     { input: "#f-topic",  wrapper: '[data-field="topic"]',     kind: "select" },
  message:   { input: "#f-msg",    wrapper: '[data-field="message"]',   kind: "textarea" },
  /* Die rechte Spalte. Dieselbe Mechanik wie die fünf darüber — der Worker
     sieht keinen Unterschied zwischen einem Feld links und einem rechts, weil
     es keinen gibt: sie stehen in demselben <form>. */
  asset:     { input: "#f-anlage", wrapper: '[data-field="asset"]',     kind: "input" },
  occasion:  { input: "#f-anlass", wrapper: '[data-field="occasion"]',  kind: "input" },
  data:      { input: "#f-daten",  wrapper: '[data-field="data"]',      kind: "input" },
  timeframe: { input: "#f-zeit",   wrapper: '[data-field="timeframe"]', kind: "input" },
};

/* Die Beschriftung, unter der ein Feld in der Übersicht auftaucht. Sie ist das
   Label aus dem Formular, denn die Übersicht ist ein Index auf das Formular und
   muss dessen Wörter benutzen — auf jeder der beiden Seiten die ihren.

   ZWEI LESER, EINE TABELLE. render.js nimmt sie für die Fehlerübersicht und
   mail.js für den Kopf der Mail, und deshalb steht "Thema" darin, obwohl das
   Thema nie in einer Übersicht auftaucht: ein Wert außerhalb der Auswahlliste
   wird verworfen und nicht gemeldet. In der Mail steht es. Ein Feld, das in
   FIELDS steht und hier nicht, wäre eine Zeile "undefined:" im Postfach. */
export const FIELD_LABELS = {
  de: {
    name: "Name",
    email: "E-Mail",
    company: "Unternehmen",
    topic: "Thema",
    message: "Nachricht",
    asset: "Anlage",
    occasion: "Anlass",
    data: "Datenlage",
    timeframe: "Zeitrahmen",
  },
  en: {
    name: "Name",
    email: "Email",
    company: "Company",
    topic: "Topic",
    message: "Message",
    asset: "Plant",
    occasion: "Reason",
    data: "Data",
    timeframe: "Timing",
  },
};

