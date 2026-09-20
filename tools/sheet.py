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


def load_frame(path: Path, palette: dict[str, tuple[int, int, int]]) -> Image.Image:
    grid = parse(path)
    errors = check(grid, palette)
    if errors:
        raise GridError(f"{display(path)}: {errors[0]}")
    if grid.width != grid.height:
        raise GridError(f"{display(path)}: {grid.width}x{grid.height} is not square")
    if not grid.background.has_alpha:
        raise GridError(f"{display(path)}: a sheet frame needs 'bg: transparent'")
    return to_image(grid, palette)


def load_frames(
    rows: list[list[str | None]],
    palette: dict[str, tuple[int, int, int]],
    unit_dir: Path,
) -> dict[str, Image.Image]:
    """Every distinct frame the definition names, read once and checked."""
    frames = {
        name: load_frame(unit_dir / f"{name}.txt", palette)
        for row in rows
        for name in row
        if name
    }
    if not frames:
        raise GridError("the sheet definition has no frames in it")
    sizes = {image.size for image in frames.values()}
    if len(sizes) != 1:
        raise GridError(f"frames have mixed sizes: {sorted(sizes)}")
    return frames


def frame_size(frames: dict[str, Image.Image]) -> int:
    return next(iter(frames.values())).width


def compose_sheet(
    rows: list[list[str | None]], frames: dict[str, Image.Image]
) -> Image.Image:
    if not frames:
        raise GridError("the sheet definition has no frames in it")
    frame = frame_size(frames)
    canvas = Image.new("RGBA", (len(rows[0]) * frame, len(rows) * frame))
    for y, row in enumerate(rows):
        for x, name in enumerate(row):
            if name:
                canvas.paste(frames[name], (x * frame, y * frame))
    return canvas


def columns_per_state(rows: list[list[str | None]]) -> dict[str, int]:
    """How many columns each state actually uses, for eyeballing against the
    consumer's JSON. This tool deliberately does not read that JSON."""
    counts: dict[str, int] = {}
    for index, state in enumerate(STATES):
        block = rows[index * len(DIRECTIONS) : (index + 1) * len(DIRECTIONS)]
        used = [x for x in range(len(rows[0])) if any(row[x] for row in block)]
        counts[state] = max(used) + 1 if used else 0
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("definition", type=Path, help="sheet definition file")
    parser.add_argument("--scale", type=int, default=4, help="preview enlargement (default: 4)")
    parser.add_argument("-o", "--outdir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)

    if args.scale < 1:
        raise SystemExit("error: --scale must be 1 or greater")

    try:
        palette = load_palette()
    except GridError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2

    rows = read_sheet(args.definition)
    try:
        frames = load_frames(rows, palette, args.definition.parent)
    except GridError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    canvas = compose_sheet(rows, frames)

    args.outdir.mkdir(parents=True, exist_ok=True)
    name = args.definition.stem.removesuffix(".sheet")
    destination = args.outdir / f"{name}.png"
    canvas.save(destination)
    print(f"ok   {display(destination)}  {canvas.width}x{canvas.height}")
    for state, count in columns_per_state(rows).items():
        print(f"     {state:<7} {count} frame(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
