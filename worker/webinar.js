/* Webinar registrations use the contact form's name, email and company rules.
   The event is chosen by the server; no submitted title or recipient is trusted. */
import { validate as validateContact } from "./validate.js";
export { summaryTitle, RATE_LIMITED } from "./validate.js";

export const FIELDS = {
  name:    { input: "#f-name",  wrapper: '[data-field="name"]',    kind: "input" },
  email:   { input: "#f-mail",  wrapper: '[data-field="email"]',   kind: "input" },
  company: { input: "#f-firma", wrapper: '[data-field="company"]', kind: "input" },
};

export const FIELD_LABELS = {
  de: { name: "Name", email: "E-Mail", company: "Unternehmen" },
  en: { name: "Name", email: "Email", company: "Company" },
};

export const SEND_FAILED = {
  de: {
    title: "Ihre Anmeldung konnte gerade nicht gesendet werden",
    message: "Ihre Angaben stehen noch im Formular. Bitte versuchen Sie es in einigen Minuten noch einmal.",
  },
  en: {
    title: "Your registration could not be sent just now",
    message: "Your details are still in the form. Please try again in a few minutes.",
  },
};

export function validate(raw, locale = "de") {
  const result = validateContact({
    name: raw.name,
    email: raw.email,
    company: raw.company,
    message: "Webinar-Anmeldung",
  }, locale);
  return {
    values: Object.fromEntries(Object.keys(FIELDS).map((field) => [field, result.values[field]])),
    errors: result.errors,
  };
}
