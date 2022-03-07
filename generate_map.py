#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# *****************************************************************************#

from __future__ import annotations

import argparse
from email.policy import default
from pathlib import Path

import geopandas as gpd
import osmnx as ox
from geopy.geocoders import Nominatim

from palette import Palette, load_colour_palettes


class Map:
    def __init__(self, point: tuple[float, float], radius: int) -> None:
        print("### Loading data from OpenStreetMap")
        self.streets = ox.graph_from_point(
            point,
            dist=radius,
            retain_all=True,
            truncate_by_edge=True,
            clean_periphery=False,
        )
        self.street_data = self.unpack_data()
        if "geometry" not in self.street_data:
            raise KeyError("geometries not found in street data!")

        self.water = ox.geometries_from_point(
            point, tags={"water": "river"}, dist=radius,
        )

    def unpack_data(self) -> gpd.GeoDataFrame:
        data = []
        for _, _, _, ddata in self.streets.edges(keys=True, data=True):
            data.append(ddata)
        df = gpd.GeoDataFrame(data)
        df.to_csv("streets.csv")
        return df

    def apply_colour_palette(self, palette_name: str, palette: Palette):
        print(f"### Applying palette {palette_name} to data")

        def _map_highway_type_to_colour(row: gpd.GeoSeries) -> str:
            if isinstance(row.highway, str):
                comparer = lambda way, ref: way in ref
            else:
                comparer = lambda way, ref: any(i in ref for i in way)

            if comparer(row.highway, ["motorway"]):
                return palette["base05"]
            elif comparer(row.highway, ["trunk"]):
                return palette["base05"]
            elif comparer(
                row.highway,
                ["primary", "secondary", "tertiary", "unclassified", "residential"],
            ):
                return palette["base05"]
            elif comparer(row.highway, ["path"]):
                return palette["base03"]
            else:
                return palette["base02"]

        def _map_highway_type_to_width(row: gpd.GeoSeries) -> int:
            if isinstance(row.highway, str):
                comparer = lambda way, ref: way in ref
            else:
                comparer = lambda way, ref: any(i in ref for i in way)

            if comparer(row.highway, ["motorway", "trunk"]):
                return 2
            else:
                return 1

        self.street_data["colour"] = self.street_data.apply(
            _map_highway_type_to_colour, axis=1
        )
        self.street_data["line_width"] = self.street_data.apply(
            _map_highway_type_to_width, axis=1
        )

    @property
    def streets_bbox(self) -> tuple[float, float, float, float]:
        minx, miny, maxx, maxy = self.street_data.geometry.total_bounds
        return (maxy, miny, maxx, minx)

    def export_image(self, destination: Path, palette_name: str, palette: Palette):
        self.apply_colour_palette(palette_name, palette)

        print("### Generating image")
        fig, ax = ox.plot_graph(
            self.streets,
            node_size=0,
            figsize=(20, 20),
            bgcolor=palette["base00"],
            edge_color=self.street_data["colour"].to_list(),
            edge_linewidth=1,
            edge_alpha=1,
            show=False,
            save=False,
            close=True,
        )

        ox.plot_footprints(
            self.water,
            color=palette["base01"],
            bbox=self.streets_bbox,
            ax=ax,
            dpi=600,
            save=True,
            show=False,
            close=False,
            filepath=destination,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--place",
        type=str,
        help="The place to generate the map for",
        default="Grenoble, France",
    )
    parser.add_argument(
        "--radius", type=int, help="Radius around the point to generate", default=3000,
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

    geolocator = Nominatim(user_agent="map_plotter")
    location = geolocator.geocode(args.place)

    map = Map((location.latitude, location.longitude), args.radius,)

    args.export_dir.mkdir(exist_ok=True)

    palettes = load_colour_palettes(args.palette_file)

    for palette_name in args.palette_names:
        map.export_image(
            destination=args.export_dir / f"Grenoble_{palette_name}.png",
            palette_name=palette_name,
            palette=palettes[palette_name],
        )
