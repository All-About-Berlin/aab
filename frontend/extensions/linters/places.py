#!/usr/bin/env python3
from pathlib import Path
from typing import Any, List, Tuple
from urllib.parse import urlparse
from ursus.config import config
from ursus.linters import LinterResult
from ursus.linters.markdown import HeadMatterLinter
from ursus.utils import parse_markdown_head_matter
import googlemaps
import logging
import re


class PlacesLinter(HeadMatterLinter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.google_maps = googlemaps.Client(key=config.google_maps_places_api_key)

    def lint_meta(
        self,
        file_path: Path,
        meta: dict[str, List[Any]],
        field_positions: dict[str, Tuple[int, int, int]],
    ) -> LinterResult:
        if file_path.is_relative_to(Path("places")):
            with (config.content_path / file_path).open() as place_file:
                meta, field_positions = parse_markdown_head_matter(place_file.readlines())

            if "google_place_id" not in meta:
                yield (0, 0, 3), "Place has no place ID", logging.ERROR
                return

            try:
                google_place = self.google_maps.place(meta["google_place_id"][0], language="en")["result"]
            except googlemaps.exceptions.ApiError as e:
                yield (0, 0, 3), "Place error" + str(e), logging.ERROR
                return

            meta_website = urlparse(meta.get("website")[0]).netloc if meta.get("website") else None
            if google_place.get("website") and meta_website != urlparse(google_place.get("website")).netloc:
                yield (
                    field_positions.get("website"),
                    f"Website does not match with Google: {meta_website} -> {google_place.get('website')}",
                    logging.WARNING,
                )

            google_address = re.sub(r"(, (\d{5} )?Berlin)?, Germany$", "", google_place["formatted_address"]).strip()
            if meta.get("address")[0] != google_address:
                yield (
                    field_positions.get("address"),
                    f"Address does not match with Google: {meta.get('address')[0]} -> {google_address}",
                    logging.ERROR,
                )

            business_status = google_place.get("business_status")
            if business_status and business_status != "OPERATIONAL":
                yield (
                    None,
                    f"Business is {google_place.get('business_status')}",
                    logging.ERROR,
                )

            lat = float(meta["latitude"][0])
            lng = float(meta["longitude"][0])
            g_lat = round(google_place["geometry"]["location"]["lat"], 6)
            g_lng = round(google_place["geometry"]["location"]["lng"], 6)
            if str(lat) != str(g_lat):
                yield (
                    field_positions.get("latitude"),
                    f"Latitude does not match with Google: {lat} -> {g_lat}",
                    logging.ERROR,
                )
            if str(lng) != str(g_lng):
                yield (
                    field_positions.get("longitude"),
                    f"Longitude does not match with Google: {lng} -> {g_lng}",
                    logging.ERROR,
                )
