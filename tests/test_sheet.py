"""Checks for the unit sheet tool.

    .venv/bin/python -m unittest discover -s tests
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import sheet  # noqa: E402

FIXTURES = REPO_ROOT / "tests" / "fixtures"


def write_sheet(text: str) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    handle.write(text)
    handle.close()
    return Path(handle.name)


def definition(rows: list[str]) -> Path:
    return write_sheet("".join(f"{row}\n" for row in rows))


TWELVE = ["sheet_dot sheet_block . ."] * 12


class ReadSheetTest(unittest.TestCase):
    def test_twelve_rows_are_accepted(self):
        rows = sheet.read_sheet(definition(TWELVE))
        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[0], ["sheet_dot", "sheet_block", None, None])

    def test_eleven_rows_are_rejected(self):
        with self.assertRaises(SystemExit):
            sheet.read_sheet(definition(TWELVE[:11]))

    def test_thirteen_rows_are_rejected(self):
        with self.assertRaises(SystemExit):
            sheet.read_sheet(definition(TWELVE + ["sheet_dot . . ."]))

    def test_comments_and_blank_lines_do_not_count_as_rows(self):
        rows = sheet.read_sheet(definition(["# a sheet", ""] + TWELVE))
        self.assertEqual(len(rows), 12)
