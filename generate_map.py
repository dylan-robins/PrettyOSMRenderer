#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
#*****************************************************************************#

from __future__ import annotations

import osmnx as ox
import json
from pathlib import Path

PALETTE_FILE = Path("base16_schemes.json")
EXPORT_DIR = Path("export")


def load_colour_palettes(palette_file: Path) -> dict[str, dict[str, str]]:
    print("### Loading colour palettes")
    with palette_file.open("r") as colour_scheme_file:
        palettes = json.load(colour_scheme_file)
    return palettes


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
        
    def apply_colour_palette(self, palette_name: str, palette: dict[str, str]):
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
    
    def export_image(self, destination: Path, palette_name: str, palette: dict[str, str]):
        self.apply_colour_palette(palette_name, palette)

        print("### Generating image")
        ox.plot_graph(
            self.graph,
            node_size=0,
            dpi=300,
            figsize=(33.11,46.81),
            bgcolor=palette["base00"],
            edge_color=self.colours,
            edge_linewidth=1,
            edge_alpha=1,
            filepath = destination,
            show = False,
            save = True,
            close = True
        )

if __name__ == "__main__":
    places = ["Grenoble, France"]
    map = Map(places)

    EXPORT_DIR.mkdir(exist_ok=True)

    palettes = load_colour_palettes(PALETTE_FILE)

    for selected_palette_name, selected_palette in palettes.items():
        map.export_image(
            destination = EXPORT_DIR / f"Grenoble_{selected_palette_name}.png",
            palette_name = selected_palette_name,
            palette = selected_palette
        )

