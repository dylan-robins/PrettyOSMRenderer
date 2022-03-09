#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# *****************************************************************************#

from __future__ import annotations

from pathlib import Path

from geopy.geocoders import Nominatim

from add_text import add_city_name
from generate_map import Map
from palette import load_colour_palettes

PLACES = [
    #{"city": "Hong Kong",     "radius": 5000},
    #{"city": "Bangkok",       "radius": 5000},
    #{"city": "London",        "radius": 5000},
    #{"city": "Macau",         "radius": 5000},
    #{"city": "Singapore",     "radius": 5000},
    #{"city": "Paris",         "radius": 5000},
    {"city": "Dubai",         "radius": 5000},
    #{"city": "New York City", "radius": 5000},
    #{"city": "Kuala Lumpur",  "radius": 5000},
    #{"city": "Istanbul",      "radius": 5000},
]

PALETTES = [
    #"onedark",
    "yesterday-night",
]

palettes = load_colour_palettes(Path("base16_schemes.json"))

for place in PLACES:
    geolocator = Nominatim(user_agent="map_plotter")
    location = geolocator.geocode(place["city"])
    place_metadata = geolocator.reverse(location.point)

    EXPORT_DIR = Path("export") / place["city"]
    EXPORT_DIR.mkdir(exist_ok=True, parents=True)

    map = Map((location.latitude, location.longitude), place["radius"])


    for palette in PALETTES:
        place_cleaned = place["city"].replace(' ', '_').replace(',', '')
        map.export_image(
            destination=EXPORT_DIR / f"{place_cleaned}_{palette}.png",
            palette_name=palette,
            palette=palettes[palette],
        )

        add_city_name(
            input_image = EXPORT_DIR / f"{place_cleaned}_{palette}.png",
            place_name = place["city"],
            output_image = EXPORT_DIR / f"{place_cleaned}_{palette}_named.png",
            palette = palettes[palette],
        )
