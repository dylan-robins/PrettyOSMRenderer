#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
#*****************************************************************************#

from __future__ import annotations

import osmnx as ox
import json
from pathlib import Path
import networkx as nx

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
        #G1 = ox.graph_from_place(places, custom_filter='["highway"~"residential"]')
        #G3 = ox.graph_from_place(places, custom_filter='["highway"~"cycleway"]')
        #G5 = ox.graph_from_place(places, custom_filter='["railway"~"rail"]')
        #palette_name = "atelier-sulphurpool",
        #palette = palettes["atelier-sulphurpool"]
        #G5.apply_colour_palette(palette_name, palette)
        #G2 = ox.graph_from_place(places, network_type='drive', retain_all=True)

        #self.graph = nx.compose(G3,G5)
        #self.graph = nx.compose(self.graph,G3)
        #self.graph = nx.compose(self.graph,G2)

        #self.graph = ox.graph_from_place(places, network_type="walk", simplify = True)
        #self.graph = ox.graph_from_place(places, custom_filter='["highway"~"cycleway"]')
        #self.add_layer(places,'["railway"~"rail"]')
        #self.add_layer(places,'["highway"~"residential"]')
    
        places= 45.1891, 5.7227
        self.graph =ox.graph_from_point(
                            places,
                            dist=5000,
                            dist_type="bbox",
                            network_type ="walk",
                            simplify=True,
                            retain_all = False,
                            truncate_by_edge= False,
                            clean_periphery= True,
                            custom_filter= None)
                        

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
                    color = palette["base00"]

                elif item["length"] > 100 and item["length"] <= 200:
                    color = palette["base00"]

                elif item["length"] > 200 and item["length"] <= 400:
                    color = palette["base00"]

                elif item["length"] > 400 and item["length"] <= 800:
                    color = palette["base00"]

                else:
                    color = palette["base00"]
            else:
                color = palette["base00"]

            self.colours.append(color)
    
    def export_image(self, destination: Path, palette_name: str, palette: dict[str, str]):
        self.apply_colour_palette(palette_name, palette)

        print("### Generating image")
        
        ox.plot_graph(
            self.graph,
            node_size=0,
            dpi=300,
            figsize=((33.11,46.81)),
            bgcolor=palette["base07"],
            edge_color=self.colours,
            edge_linewidth=3,
            edge_alpha=1,
            filepath = destination,
            show = True,
            save = True,
            close = True
        )

    def add_layer(self,places,custom_lay):
        G1 = ox.graph_from_place(places, custom_filter=custom_lay)
        self.graph = nx.compose(self.graph,G1)

if __name__ == "__main__":
    places = ["Grenoble, France"]

    #Comment bien construire Map
    map = Map(places)

    EXPORT_DIR.mkdir(exist_ok=True)

    palettes = load_colour_palettes(PALETTE_FILE)

    #print(palettes["macintosh"])
    map.export_image(
            destination = EXPORT_DIR / f"gre_fctlay_macintosh.png",
            palette_name = "macintosh",
            palette = palettes["macintosh"])


