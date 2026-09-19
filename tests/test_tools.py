"""Checks for the grid parser, the machine checks, and the renderer.

    .venv/bin/python -m unittest discover -s tests
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from gridfile import GridError, check, load_palette, parse, parse_background  # noqa: E402
from render import to_image  # noqa: E402

PALETTE = {"outline": (10, 20, 30), "skin_base": (200, 150, 100)}

GOOD = """\
# type: face
# size: 4x3
# light: upper-left
# map: o=outline b=skin_base
oooo
obbo
oooo
"""


def write(text: str) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    handle.write(text)
    handle.close()
    return Path(handle.name)


class ParseTest(unittest.TestCase):
    def test_reads_headers_and_rows(self):
        grid = parse(write(GOOD))
        self.assertEqual(grid.type, "face")
        self.assertEqual((grid.width, grid.height), (4, 3))
        self.assertEqual(grid.charmap, {"o": "outline", "b": "skin_base"})
        self.assertEqual(grid.headers["light"], "upper-left")
        self.assertEqual(len(grid.rows), 3)

    def test_map_may_span_several_lines(self):
        grid = parse(write(GOOD.replace("# map: o=outline b=skin_base", "# map: o=outline\n# map: b=skin_base")))
        self.assertEqual(grid.charmap, {"o": "outline", "b": "skin_base"})

    def test_blank_lines_are_ignored(self):
        grid = parse(write(GOOD.replace("# map:", "\n# map:")))
        self.assertEqual(len(grid.rows), 3)

    def test_missing_required_header(self):
        with self.assertRaisesRegex(GridError, "missing required header"):
            parse(write(GOOD.replace("# size: 4x3\n", "")))

    def test_header_after_rows(self):
        with self.assertRaisesRegex(GridError, "header line after grid rows"):
            parse(write(GOOD + "# light: upper-left\n"))

    def test_background_cannot_be_mapped(self):
        with self.assertRaisesRegex(GridError, "background and cannot be mapped"):
            parse(write(GOOD.replace("o=outline", ".=outline")))

    def test_conflicting_map_entry(self):
        with self.assertRaisesRegex(GridError, "mapped twice"):
            parse(write(GOOD.replace("b=skin_base", "b=skin_base o=skin_base")))

    def test_bad_size(self):
        with self.assertRaisesRegex(GridError, "is not 'WxH'"):
            parse(write(GOOD.replace("4x3", "four")))

    def test_no_rows(self):
        with self.assertRaisesRegex(GridError, "no grid rows"):
            parse(write("# type: face\n# size: 4x3\n# map: o=outline\n"))


class CheckTest(unittest.TestCase):
    def test_clean_grid_has_no_errors(self):
        self.assertEqual(check(parse(write(GOOD)), PALETTE), [])

    def test_row_length(self):
        errors = check(parse(write(GOOD.replace("obbo", "obbbo"))), PALETTE)
        self.assertIn("row 1: length 5, expected 4", errors)

    def test_row_count(self):
        errors = check(parse(write(GOOD + "oooo\n")), PALETTE)
        self.assertIn("height 4, expected 3", errors)

    def test_unknown_character(self):
        errors = check(parse(write(GOOD.replace("obbo", "oxbo"))), PALETTE)
        self.assertIn("row 1: character 'x' is not bound by 'map'", errors)

    def test_colour_outside_master_palette(self):
        errors = check(parse(write(GOOD.replace("b=skin_base", "b=not_a_colour"))), PALETTE)
        self.assertIn("map references 'not_a_colour', which is not in the master palette", errors)

    def test_reports_every_problem_at_once(self):
        broken = GOOD.replace("obbo", "oxbbo")
        self.assertEqual(len(check(parse(write(broken)), PALETTE)), 2)

    def test_max_colors_respected(self):
        self.assertEqual(check(parse(write(GOOD.replace("# map:", "# max_colors: 2\n# map:"))), PALETTE), [])
        errors = check(parse(write(GOOD.replace("# map:", "# max_colors: 1\n# map:"))), PALETTE)
        self.assertIn("uses 2 colours, over the declared max_colors 1", errors)

    def test_max_colors_counts_distinct_rgb_not_entries(self):
        palette = dict(PALETTE, skin_base=PALETTE["outline"])
        grid = parse(write(GOOD.replace("# map:", "# max_colors: 1\n# map:")))
        self.assertEqual(check(grid, palette), [])


class BackgroundTest(unittest.TestCase):
    def test_transparent_is_the_default(self):
        self.assertTrue(parse(write(GOOD)).background.has_alpha)

    def test_solid(self):
        background = parse_background("#102030")
        self.assertEqual(background.color_at(0, 4), (16, 32, 48, 255))
        self.assertEqual(background.color_at(3, 4), (16, 32, 48, 255))

    def test_gradient_interpolates_top_to_bottom(self):
        background = parse_background("gradient:#000000->#0a0a0a")
        self.assertEqual(background.color_at(0, 11), (0, 0, 0, 255))
        self.assertEqual(background.color_at(5, 11), (5, 5, 5, 255))
        self.assertEqual(background.color_at(10, 11), (10, 10, 10, 255))

    def test_unsupported_spec(self):
        with self.assertRaisesRegex(GridError, "unsupported bg"):
            parse_background("rainbow")


class RenderTest(unittest.TestCase):
    def test_pixels_come_from_the_palette(self):
        image = to_image(parse(write(GOOD)), PALETTE)
        self.assertEqual(image.size, (4, 3))
        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.getpixel((0, 0)), (*PALETTE["outline"], 255))
        self.assertEqual(image.getpixel((1, 1)), (*PALETTE["skin_base"], 255))

    def test_background_cells_are_transparent_by_default(self):
        image = to_image(parse(write(GOOD.replace("obbo", "o..o"))), PALETTE)
        self.assertEqual(image.getpixel((1, 1)), (0, 0, 0, 0))

    def test_opaque_background_drops_alpha(self):
        image = to_image(parse(write(GOOD.replace("# map:", "# bg: #102030\n# map:"))), PALETTE)
        self.assertEqual(image.mode, "RGB")

    def test_scale_is_nearest_neighbour(self):
        image = to_image(parse(write(GOOD)), PALETTE, scale=8)
        self.assertEqual(image.size, (32, 24))
        self.assertEqual(image.getpixel((8, 8)), (*PALETTE["skin_base"], 255))


class MasterPaletteTest(unittest.TestCase):
    def test_master_palette_loads(self):
        palette = load_palette()
        self.assertIn("outline", palette)
        self.assertTrue(all(len(rgb) == 3 for rgb in palette.values()))

    def test_face_reference_passes_its_own_checks(self):
        grid = parse(REPO_ROOT / "types" / "face" / "reference" / "knight.txt")
        self.assertEqual(check(grid, load_palette()), [])
        self.assertEqual((grid.width, grid.height), (32, 32))


if __name__ == "__main__":
    unittest.main()
