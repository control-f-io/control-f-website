// Build with `wrangler deploy --dry-run --outdir /tmp/cf-worker`, then run:
// node scripts/test-webinar.mjs /tmp/cf-worker/index.js [http://localhost:8787]
// Provider requests are intercepted. For the optional Workerd checks, start
// `wrangler dev --local --var RESEND_API_KEY:` to keep mail disabled there too.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { validate } from "../worker/webinar.js";

const event = JSON.parse(await readFile(new URL("../content/webinar.json", import.meta.url)));
const worker = (await import(pathToFileURL(process.argv[2]).href)).default;
const path = "/blog/webinar-wenn-sie-ihre-daten-nicht-nutzen-laeuft-.html";
const valid = { name: "Erika Muster", email: "erika@example.test", company: "Beispiel GmbH" };
const request = (route, values = valid, method = "POST") => new Request(`https://worker.test${route}`, {
  method,
  ...(method === "POST" ? { body: new URLSearchParams(values) } : {}),
});

assert.deepEqual(validate(valid).errors, []);
assert.deepEqual(validate({ ...valid, company: "" }).errors, []);
assert.deepEqual(validate({}).errors.map(e => e.field), ["name", "email"]);
assert.equal(validate({ ...valid, email: "invalid" }).errors[0].field, "email");
assert.equal(validate({ ...valid, name: "x".repeat(121) }).errors[0].field, "name");
assert.equal(validate({ ...valid, company: "x".repeat(161) }).errors[0].field, "company");
assert.equal(validate({ ...valid, name: " Erika\r\nMuster " }).values.name, "Erika Muster");
assert.match(validate({ email: "invalid" }, "en").errors[1].message, /^Please/);

const realFetch = globalThis.fetch;
const sent = [];
globalThis.fetch = async (url, init) => {
  assert.equal(url, "https://api.resend.com/emails");
  sent.push(JSON.parse(init.body));
  return new Response('{"id":"test-message"}', { status: 200 });
};
const env = {
  RESEND_API_KEY: "test-key",
  CONTACT_FROM: "Form <form@example.test>",
  CONTACT_TO: "contact@example.test",
  WEBINAR_TO: "webinar@example.test",
  SITE_ORIGIN: "https://site.example.test",
  ASSETS: { fetch: async () => new Response("asset") },
};

try {
  for (const locale of ["de", "en"]) {
    const prefix = locale === "en" ? "/en" : "";
    const response = await worker.fetch(request(prefix + path, {
      ...valid, topic: "untrusted event", recipient: "other@example.test",
    }), env, {});
    assert.equal(response.status, 303);
    assert.equal(response.headers.get("location"), `${env.SITE_ORIGIN}${prefix}/webinar-danke.html`);
    assert.equal(response.headers.get("cache-control"), "no-store");
    const message = sent.at(-1);
    assert.deepEqual(message.to, [env.WEBINAR_TO]);
    assert.equal(message.reply_to, valid.email);
    assert.match(message.subject, /^Webinar wurde gebucht:/);
    for (const value of [valid.name, valid.email, valid.company, event.id, event.when.de]) {
      assert.ok(message.text.includes(value));
    }
    assert.ok(!message.text.includes("untrusted event"));
    const count = sent.length;
    const honeypot = await worker.fetch(request(prefix + path, { website: "spam" }), env, {});
    assert.equal(honeypot.status, 303);
    assert.equal(sent.length, count);
  }
  await worker.fetch(request(path, valid), { ...env, WEBINAR_TO: undefined }, {});
  assert.deepEqual(sent.at(-1).to, [env.CONTACT_TO]);
  const limited = await worker.fetch(request(path), {
    ...env, CONTACT_RATE_LIMIT: { limit: async () => ({ success: false }) },
  }, {});
  assert.equal(limited.status, 429);
  assert.equal(limited.headers.get("retry-after"), "60");
  assert.equal((await worker.fetch(request(path, valid, "DELETE"), env, {})).status, 405);
  assert.equal((await worker.fetch(new Request(`https://worker.test${path}`, {
    method: "POST", headers: { "content-type": "application/json" }, body: "{}",
  }), env, {})).status, 400);
} finally {
  globalThis.fetch = realFetch;
}

// Optional actual Workerd checks: errors must retain and escape values in HTML.
if (process.argv[3]) {
  assert.ok(["localhost", "127.0.0.1"].includes(new URL(process.argv[3]).hostname));
  for (const locale of ["de", "en"]) {
    const route = (locale === "en" ? "/en" : "") + path;
    const response = await fetch(process.argv[3] + route, {
      method: "POST", body: new URLSearchParams({ ...valid, name: '"><img src=x onerror=alert(1)>', email: "invalid" }),
      redirect: "manual",
    });
    assert.equal(response.status, 422);
    assert.equal(response.headers.get("cache-control"), "no-store");
    const html = await response.text();
    assert.match(html, /id="fehler"/);
    assert.match(html, /id="f-mail"[^>]*aria-invalid="true"/);
    assert.ok(html.includes('value="invalid"'));
    assert.ok(html.includes('value="&quot;><img src=x onerror=alert(1)>"'));
    assert.ok(!html.includes('value=""><img'));
    assert.ok(html.includes(locale === "de" ? "Bitte geben Sie eine gültige" : "Please enter a valid"));
    // With mail credentials deliberately absent, no success can be reported.
    const unavailable = await fetch(process.argv[3] + route, {
      method: "POST", body: new URLSearchParams(valid), redirect: "manual",
    });
    assert.equal(unavailable.status, 502);
    const failed = await unavailable.text();
    assert.ok(failed.includes(locale === "de" ? "Ihre Anmeldung konnte" : "Your registration could"));
    assert.ok(failed.includes(`value="${valid.email}"`));
  }
}
console.log("Webinar: validation, both editions, notification, redirects, honeypot, rate limit and failure rendering passed.");
