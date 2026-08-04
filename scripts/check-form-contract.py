#!/usr/bin/env python3
"""The contact form and the Worker that answers it agree on every name.

The first check that reads something other than HTML and CSS, because the
contact form is the first thing on this site whose behaviour is not entirely
in the page. patterns/kontakt.html is the form; worker/ is the server that
receives it. Between them run seven agreements, none of which any other check
can see, and every one of which breaks silently:

  1. THE FIELD NAMES. Each .cf-field wrapper in the form carries data-field,
     and its value is the name= of the control inside it. The Worker adds
     cf-field--invalid by that attribute — a wrapper without one is a field
     that can never be marked wrong, and the reader gets a summary pointing at
     a field that looks fine.

  2. THE IDS. render.js maps each field to the id of its control. An id that
     moves takes the per-field message, aria-invalid and the refilled value
     with it, and HTMLRewriter reports nothing when a selector matches nothing.

  3. THE TOPICS. validate.js keeps the five <option> labels so that a value
     from outside the list can be dropped. A sixth option added to the form
     would be silently discarded on every submit.

  4. THE HONEYPOT. index.js reads the field the form calls "website". Rename
     it on one side and the trap is a normal field: every bot passes, and no
     one notices, because nothing about the page changes.

  5. THE ANCHOR. render.js inserts the error summary before form[method=post].
     Exactly one such form is on the page. If it stops matching, the response
     to a failed submit is the plain page — correct, but with nothing telling
     the reader what went wrong.

  6. THE MESSAGES. Two of the strings in validate.js are quoted from
     components/forms.html, which is where the design system writes what an
     error sounds like. They are supposed to be the same words.

  7. THE ROUTES. index.js names the path it answers and the path it redirects
     to on success. Both must be files the build actually ships.

Every one of these photographs as a working page. That is the same shape as
the checks beside this one.

stdlib only, no build step, no dependency — the JavaScript is read as text,
not parsed. The patterns are the source of truth; the Worker follows them.

    python3 scripts/check-form-contract.py       # check, exit 1 on a finding
    python3 scripts/check-form-contract.py -v    # list every agreement audited
"""

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATTERN = ROOT / "design-system" / "patterns" / "kontakt.html"
FORMS_DOC = ROOT / "design-system" / "components" / "forms.html"
WORKER = ROOT / "worker"

COMMENT = re.compile(r"<!--.*?-->", re.S)

# The honeypot's name, written once here and asserted on both sides.
HONEYPOT = "website"

# The two strings validate.js quotes from the component page.
QUOTED = [
    "Bitte geben Sie eine gültige E-Mail-Adresse an.",
    "Bitte schreiben Sie uns, worum es geht.",
]


class FormReader(HTMLParser):
    """Pulls the contact form's shape out of the pattern page.

    Only the first <form method="post"> is read — the page has one, and clause
    5 is what keeps it that way.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.forms = 0
        self.in_form = False
        self.depth = 0
        # data-field value -> {"line": int, "names": [str], "ids": [str]}
        self.wrappers = {}
        self.bare_wrappers = []          # .cf-field without data-field
        self.stack = []                  # open data-field wrappers
        self.names = {}                  # name= -> id=
        self.options = []                # <option> labels, in document order
        self.in_option = False
        self.option_buf = ""
        self.action = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]

        if tag == "form" and (a.get("method") or "").lower() == "post":
            self.forms += 1
            if self.forms == 1:
                self.in_form = True
                self.depth = 0
                self.action = a.get("action")
                return

        if not self.in_form:
            return

        self.depth += 1

        classes = (a.get("class") or "").split()
        if "cf-field" in classes:
            field = a.get("data-field")
            if field is None:
                self.bare_wrappers.append(line)
            else:
                self.wrappers[field] = {"line": line, "names": [], "ids": []}
                self.stack.append((field, self.depth))

        if tag in ("input", "select", "textarea"):
            name, ident = a.get("name"), a.get("id")
            if name:
                self.names[name] = ident
            if self.stack and name:
                self.wrappers[self.stack[-1][0]]["names"].append(name)
                self.wrappers[self.stack[-1][0]]["ids"].append(ident)

        if tag == "option":
            self.in_option = True
            self.option_buf = ""

    def handle_data(self, data):
        if self.in_option:
            self.option_buf += data

    def handle_endtag(self, tag):
        if tag == "option" and self.in_option:
            self.in_option = False
            self.options.append(self.option_buf.strip())
            return

        if not self.in_form:
            return

        if tag == "form":
            self.in_form = False
            return

        if self.stack and self.stack[-1][1] == self.depth:
            self.stack.pop()
        self.depth -= 1


def js_list(text, name):
    """The string literals of an exported array — read as text, not parsed."""
    m = re.search(r"export const %s = \[(.*?)\];" % re.escape(name), text, re.S)
    if not m:
        return None
    return re.findall(r'"([^"]*)"', m.group(1))


def js_fields(text):
    """render.js's FIELDS table: field -> (input selector, wrapper selector)."""
    m = re.search(r"const FIELDS = \{(.*?)\n\};", text, re.S)
    if not m:
        return None
    out = {}
    for row in re.finditer(
        r'(\w+):\s*\{\s*input:\s*"([^"]+)",\s*wrapper:\s*\'([^\']+)\'', m.group(1)
    ):
        out[row.group(1)] = (row.group(2), row.group(3))
    return out


def audit(verbose):
    findings = []
    say = lambda msg: findings.append("  kontakt form: %s" % msg)

    raw = PATTERN.read_text(encoding="utf-8")
    reader = FormReader()
    reader.feed(COMMENT.sub("", raw))

    validate_js = (WORKER / "validate.js").read_text(encoding="utf-8")
    render_js = (WORKER / "render.js").read_text(encoding="utf-8")
    index_js = (WORKER / "index.js").read_text(encoding="utf-8")

    # 5. THE ANCHOR.
    if reader.forms != 1:
        say('render.js inserts the summary before form[method="post"], which '
            "matches %d forms on the page — it must match exactly one"
            % reader.forms)
    if 'rewriter.on("form[method=\'post\']"' not in render_js:
        say("render.js no longer selects form[method='post'] — the error "
            "summary has no anchor")

    # 1. THE FIELD NAMES.
    for line in reader.bare_wrappers:
        say("the .cf-field at line %d carries no data-field, so the Worker "
            "cannot mark it invalid" % line)

    for field, info in sorted(reader.wrappers.items()):
        if len(info["names"]) != 1:
            say("data-field=%r wraps %d named controls; it must wrap exactly "
                "one" % (field, len(info["names"])))
            continue
        if info["names"][0] != field:
            say("data-field=%r at line %d wraps a control named %r — the "
                "attribute must carry the control's own name"
                % (field, info["line"], info["names"][0]))

    # 2. THE IDS.
    fields = js_fields(render_js)
    if fields is None:
        say("render.js has no readable FIELDS table")
    else:
        for field, (selector, wrapper) in sorted(fields.items()):
            info = reader.wrappers.get(field)
            if info is None:
                say("render.js knows a field %r that the form does not have"
                    % field)
                continue
            want = '[data-field="%s"]' % field
            if wrapper != want:
                say("render.js selects the %r wrapper as %s, not %s"
                    % (field, wrapper, want))
            ident = info["ids"][0] if info["ids"] else None
            if selector != "#%s" % ident:
                say("render.js selects the %r control as %s, but the form "
                    "gives it id=%r" % (field, selector, ident))
        for field in sorted(set(reader.wrappers) - set(fields)):
            say("the form has a field %r that render.js does not know — it "
                "can never be marked invalid or refilled" % field)

    # 3. THE TOPICS. The empty first option ("Bitte wählen") is the prompt,
    # not a topic, and is not in the list.
    topics = js_list(validate_js, "TOPICS")
    if topics is None:
        say("validate.js has no readable TOPICS list")
    else:
        in_form = [o for o in reader.options if o and o != "Bitte wählen"]
        if in_form != topics:
            say("validate.js's TOPICS %r do not match the form's options %r — "
                "a topic outside the list is dropped on every submit"
                % (topics, in_form))

    # 4. THE HONEYPOT.
    if HONEYPOT not in reader.names:
        say("the form has no %r field — the honeypot the Worker checks is gone"
            % HONEYPOT)
    if '"%s"' % HONEYPOT not in index_js:
        say("index.js no longer reads a field named %r" % HONEYPOT)

    # 6. THE MESSAGES.
    spec = FORMS_DOC.read_text(encoding="utf-8")
    for quote in QUOTED:
        if quote not in validate_js:
            say("validate.js no longer uses the message %r" % quote)
        elif quote not in spec:
            say("validate.js uses the message %r, which components/forms.html "
                "no longer shows — one of the two moved" % quote)

    # 7. THE ROUTES.
    for const in ("FORM_PATH", "THANKS_PATH"):
        m = re.search(r'const %s = "([^"]+)";' % const, index_js)
        if not m:
            say("index.js has no readable %s" % const)
            continue
        target = ROOT / m.group(1).lstrip("/")
        if not target.exists():
            say("index.js's %s is %s, which the build does not ship"
                % (const, m.group(1)))

    if reader.action != "kontakt.html#fehler":
        say("the form's action is %r — it must post to its own address with "
            "the #fehler fragment, or the Worker cannot answer with this page"
            % reader.action)

    if verbose and not findings:
        print("  wrappers   %s" % ", ".join(sorted(reader.wrappers)))
        print("  topics     %s" % ", ".join(topics or []))
        print("  honeypot   %s" % HONEYPOT)
        print("  action     %s" % reader.action)

    return findings, reader


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every agreement audited")
    args = ap.parse_args()

    findings, reader = audit(args.verbose)

    if findings:
        print("\n".join(findings), file=sys.stderr)
        print("\n%d finding%s between patterns/kontakt.html and worker/."
              % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    print("form contract: %d fields, %d topics and the honeypot agree across "
          "patterns/kontakt.html and worker/; the summary's anchor matches one "
          "form and both routes ship."
          % (len(reader.wrappers), len([o for o in reader.options if o and o != "Bitte wählen"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
