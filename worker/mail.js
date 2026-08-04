/* Der Versand einer Kontaktanfrage.

   EINE FUNKTION, EIN ANBIETER. Alles, was Resend kennt, steht in sendViaResend()
   — rund zwanzig Zeilen. Ein Wechsel zu Brevo, Mailjet oder Postmark tauscht
   diese Funktion und sonst nichts; sendEnquiry() und der Rest des Workers
   wissen nicht, wer die Mail zustellt.

   ZUR REGION. Resend wählt sie pro Domain, nicht pro Aufruf: eine Domain, die
   im Dashboard auf eu-west-1 (Irland) angelegt ist, versendet aus Irland. Es
   gibt dafür kein Feld in der API, und deshalb steht hier keins. Wichtiger,
   und im Code nicht sichtbar: die Region bestimmt nur den Versandweg.
   Kontodaten, Metadaten und Logs — und damit Name, Adresse und Text jeder
   Anfrage — liegen laut Resend in den USA. Das ist eine Drittlandsübermittlung
   und gehört als solche in die Datenschutzerklärung.

   WAS NICHT IN DIE MAIL GEHÖRT. Keine IP, kein User-Agent, kein Zeitstempel
   über das hinaus, was der Mailserver ohnehin setzt. Für die Beantwortung
   einer Anfrage braucht es das nicht, und Art. 5 Abs. 1 lit. c DSGVO sagt,
   dass dann auch nichts davon erhoben wird. */

const RESEND_ENDPOINT = "https://api.resend.com/emails";

/* Der Betreff trägt das Thema, wenn eins gewählt wurde — dann sortiert das
   Postfach von selbst. Ohne Thema bleibt es beim Namen. */
function subjectFor(values) {
  return values.topic
    ? `Kontaktanfrage: ${values.topic} — ${values.name}`
    : `Kontaktanfrage von ${values.name}`;
}

/* Nur-Text, keine HTML-Mail. Die Anfrage ist Fließtext mit vier Angaben davor;
   HTML würde nichts hinzufügen, was ein Postfach nicht schon kann, und wäre
   eine zweite Stelle, an der Nutzereingaben escaped werden müssten. */
function bodyFor(values) {
  const lines = [
    `Name:        ${values.name}`,
    `E-Mail:      ${values.email}`,
  ];
  if (values.company) lines.push(`Unternehmen: ${values.company}`);
  if (values.topic) lines.push(`Thema:       ${values.topic}`);
  lines.push("", values.message, "", "--", "Gesendet über das Kontaktformular auf control-f.de");
  return lines.join("\n");
}

/* ---- Anbieter: Resend ---------------------------------------------------
   Die einzige Stelle, die einen Anbieter kennt. Wirft bei jedem Ausgang, der
   keine zugestellte Mail ist — der Aufrufer entscheidet, was der Leser davon
   sieht. */
async function sendViaResend(env, { from, to, replyTo, subject, text }) {
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

export async function sendEnquiry(values, env) {
  if (!env.RESEND_API_KEY || !env.CONTACT_FROM || !env.CONTACT_TO) {
    throw new Error("Mailversand nicht konfiguriert: RESEND_API_KEY, CONTACT_FROM oder CONTACT_TO fehlt");
  }

  await sendViaResend(env, {
    from: env.CONTACT_FROM,
    to: env.CONTACT_TO,
    replyTo: values.email,
    subject: subjectFor(values),
    text: bodyFor(values),
  });
}
