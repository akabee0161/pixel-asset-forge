#!/usr/bin/env python3
"""Assemble a unit sprite sheet from grid files.

    tools/sheet.py assets/unit/roran/roran.sheet.txt

A sheet definition is whitespace-separated frame names, one sheet row per line,
exactly 12 rows (3 states x 4 directions). `.` leaves a cell transparent. It is
the same shape as a `layouts/*.txt` file on purpose.

    down_base  down_breathe  .  .
    up_base    up_breathe    .  .

Rows 0-3 are idle, 4-7 walk, 8-11 attack; within each block the order is
down, up, left, right. The consumer (character-tactics) reads the sheet by
`row = state_index * 4 + direction_index`, so the order is not ours to change.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gridfile import REPO_ROOT, GridError, check, display, load_palette, parse

from render import to_image
from tilemap import read_layout

OUTPUT_DIR = REPO_ROOT / "build" / "sheets"

ROWS = 12
STATES = ("idle", "walk", "attack")
DIRECTIONS = ("down", "up", "left", "right")

# The frame row the feet are supposed to sit on. Declared in
# docs/2026-09-20-unit-sprite-sheet-spec.md section 3.
FOOT_Y = 30


def read_sheet(path: Path) -> list[list[str | None]]:
    rows = read_layout(path)
    if len(rows) != ROWS:
        raise SystemExit(
            f"error: {path}: {len(rows)} rows, expected {ROWS} "
            f"({len(STATES)} states x {len(DIRECTIONS)} directions)"
        )
    return rows
