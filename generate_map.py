#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# *****************************************************************************#

from __future__ import annotations

import argparse
from email.policy import default
from pathlib import Path

import osmnx as ox

from palette import Palette, load_colour_palettes


class Map:
    def __init__(self, places) -> None:
        print("### Loading data from OpenStreetMap")
        self.graph = ox.graph_from_place(places)
        self.data = []
        self.colours = []
        self.unpack_data()

    def unpack_data(self):
        for uu, vv, kkey, ddata in self.graph.edges(keys=True, data=True):
            self.data.append(ddata)

    def apply_colour_palette(self, palette_name: str, palette: Palette):
        print(f"### Applying palette {palette_name} to data")

        # The length is in meters
        for item in self.data:
            if "length" in item.keys():

                if item["length"] <= 100:
                    color = palette["base08"]

                elif item["length"] > 100 and item["length"] <= 200:
                    color = palette["base09"]

                elif item["length"] > 200 and item["length"] <= 400:
                    color = palette["base0A"]

                elif item["length"] > 400 and item["length"] <= 800:
                    color = palette["base0B"]

                else:
                    color = palette["base05"]
            else:
                color = palette["base05"]

            self.colours.append(color)

    def export_image(self, destination: Path, palette_name: str, palette: Palette):
        self.apply_colour_palette(palette_name, palette)

        print("### Generating image")
        ox.plot_graph(
            self.graph,
            node_size=0,
            dpi=300,
            figsize=(9, 12),
            bgcolor=palette["base00"],
            edge_color=self.colours,
            edge_linewidth=1,
            edge_alpha=1,
            filepath=destination,
            show=False,
            save=True,
            close=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--places",
        type=str,
        nargs="+",
        help="The place to generate the map for",
        default="Grenoble, France",
    )
    parser.add_argument(
        "--palette_file",
        type=Path,
        help="Path to a json file containing colour palettes",
        default=Path("base16_schemes.json"),
    )
    parser.add_argument(
        "--palette_names",
        type=str,
        nargs="+",
        help="Names of the palettes to load from the palette_file",
        default=["onedark", "github", "grayscale", "shapeshifter"],
    )
    parser.add_argument(
        "--export_dir",
        type=Path,
        help="Path to a directory in which to place the generated maps",
        default=Path("export"),
    )
    args = parser.parse_args()

    map = Map(args.places)

    args.export_dir.mkdir(exist_ok=True)

    palettes = load_colour_palettes(args.palette_file)

    for palette_name in args.palette_names:
        map.export_image(
            destination=args.export_dir / f"Grenoble_{palette_name}.png",
            palette_name=palette_name,
            palette=palettes[palette_name],
        )
