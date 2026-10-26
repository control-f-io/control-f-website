#!/usr/bin/env python3
"""Regression checks for ongoing and dated openings, from Notion to JSON-LD."""

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SYNC = load("sync-jobs-notion")
PAGES = load("build-stellen")
CHECK = load("check-job-posting")
FIXTURE = json.loads((HERE / "data/notion-jobs.sample.json").read_text())["results"][0]
BODY = "Wir suchen Verstärkung.\n\n--- en ---\n\nWe are hiring.\n"


class JobDeadlines(unittest.TestCase):
    def imported(self, deadline):
        row = copy.deepcopy(FIXTURE)
        if deadline == "missing":
            row["properties"].pop("Frist")
        else:
            row["properties"]["Frist"]["date"] = {"start": deadline} if deadline else None
        return SYNC.job_from(row, BODY)

    def job(self, deadline):
        name, source = self.imported(deadline)
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / name).write_text(source, encoding="utf-8")
            with patch.object(PAGES.JOBS, "JOBS", folder):
                return PAGES.JOBS.read_jobs()[0]

    def document(self, job):
        return "\n".join((
            PAGES.ld(job, "de", ""),
            "<h1>" + PAGES.JOBS.title_html(job, "de") + "</h1>",
            PAGES.meta(job, "de", ""),
            PAGES.facts(job, "de", ""),
            "<p>Control-F GmbH · Am Seerhein 6 · 78467 Konstanz · 58.000–72.000 €</p>",
        ))

    def audit(self, source):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "job.html"
            path.write_text(source, encoding="utf-8")
            findings, *_ = CHECK.audit([str(path)])
            return findings

    def test_empty_or_missing_notion_deadline_keeps_full_advertisement(self):
        for deadline in (None, "missing"):
            with self.subTest(deadline=deadline):
                name, source = self.imported(deadline)
                self.assertEqual(name, "data-engineer.md")
                self.assertNotIn("frist:", source)
                self.assertIn(BODY, source)

    def test_removing_deadline_replaces_previously_dated_content(self):
        name, dated = self.imported("2026-09-30")
        _, ongoing = self.imported(None)
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / name).write_text(dated, encoding="utf-8")
            with patch.object(SYNC, "JOBS", folder):
                SYNC.write({name: ongoing}, "write")
            self.assertEqual((folder / name).read_text(), ongoing)

    def test_ongoing_advertisement_gets_a_page_without_expiration_in_both_languages(self):
        job = self.job(None)
        self.assertEqual(PAGES.JOBS.page_name(job), "stelle-data-engineer.html")
        for edition in ("de", "en"):
            with self.subTest(edition=edition):
                self.assertNotIn("validThrough", PAGES.ld(job, edition, ""))
                self.assertNotIn(PAGES.WORDS[edition]["deadline"], PAGES.facts(job, edition, ""))

    def test_explicit_deadline_is_preserved_in_both_languages(self):
        job = self.job("2026-09-30")
        for edition in ("de", "en"):
            with self.subTest(edition=edition):
                posting = json.loads(CHECK.ld_blocks(PAGES.ld(job, edition, ""))[0][1])
                self.assertEqual(posting["validThrough"], "2026-09-30")
                self.assertIn('datetime="2026-09-30"', PAGES.facts(job, edition, ""))

    def test_validator_accepts_ongoing_and_dated_jobs(self):
        for deadline in (None, "2026-09-30"):
            with self.subTest(deadline=deadline):
                self.assertEqual(self.audit(self.document(self.job(deadline))), [])

    def test_validator_still_rejects_deadline_before_publication(self):
        findings = self.audit(self.document(self.job("2020-01-01")))
        self.assertTrue(any("before datePosted" in finding[2] for finding in findings), findings)

    def test_validator_still_rejects_deadline_missing_from_visible_page(self):
        job = self.job("2026-09-30")
        source = self.document(job).replace("30.09.2026", "")
        self.assertTrue(any("validThrough says" in finding[2] for finding in self.audit(source)))


if __name__ == "__main__":
    unittest.main()
