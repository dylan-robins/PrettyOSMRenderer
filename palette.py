#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# *****************************************************************************#

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

Palette = dict[str, str]


def load_colour_palettes(palette_file: Path) -> dict[str, Palette]:
    print("### Loading colour palettes")
    with palette_file.open("r") as colour_scheme_file:
        palettes = json.load(colour_scheme_file)
    return palettes


def generate_swatch(palette: Palette, output_path: Path):
    square_width = 100
    im = Image.new(mode="RGB", size=(len(palette) * square_width, square_width))
    draw = ImageDraw.Draw(im)
    for i, colour in enumerate(palette.values()):
        square_bounding_box = i * square_width, 0, (i + 1) * square_width, square_width
        draw.rectangle(square_bounding_box, fill=colour)
    im.save(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "palette_file", type=Path, help="Path to a json file containing colour palettes"
    )
    parser.add_argument(
        "export_dir",
        type=Path,
        help="Path to a directory in which to place the generated colour swatches",
    )
    args = parser.parse_args()

    if not args.export_dir.is_dir():
        args.export_dir.mkdir()

    palettes = load_colour_palettes(args.palette_file)
    for name, palette in palettes.items():
        print(f"### Generating swatch for palette {name}")
        generate_swatch(palette, args.export_dir / f"{name}.png")
