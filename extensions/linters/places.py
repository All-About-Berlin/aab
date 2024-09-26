#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urlparse
from ursus.config import config
from ursus.linters import Linter
from ursus.utils import get_files_in_path, parse_markdown_head_matter
import googlemaps
import logging
import re


class PlacesLinter(Linter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.google_maps = googlemaps.Client(key=config.google_maps_api_key)

    def lint(self, file_path: Path):
        if file_path.is_relative_to(Path('places')):
            with (config.content_path / file_path).open() as place_file:
                place, field_positions = parse_markdown_head_matter(place_file.readlines())

            if 'Google_Place_ID' not in place:
                yield (0, 0, 3), "Place has no place ID", logging.ERROR
                return

            try:
                google_place = self.google_maps.place(place['Google_Place_ID'], language="en")['result']
            except googlemaps.exceptions.ApiError as e:
                yield (0, 0, 3), "Place error" + str(e), logging.ERROR
                return

            if google_place.get('website') and urlparse(place.get('Website')).netloc != urlparse(google_place.get('website')).netloc:
                yield (
                    field_positions.get('Website'),
                    f"Website does not match with Google: {place.get('Website')} -> {google_place.get('website')}",
                    logging.WARNING
                )

            google_address = re.sub(r"(, (\d{5} )?Berlin)?, Germany$", "", google_place['formatted_address']).strip()
            if place.get('Address') != google_address:
                yield (
                    field_positions.get('Address'),
                    f"Address does not match with Google: {place.get('Address')} -> {google_address}",
                    logging.ERROR
                )

            business_status = google_place.get('business_status')
            if business_status and business_status != 'OPERATIONAL':
                yield None, f"Business is {google_place.get('business_status')}", logging.ERROR

            lat = float(place['Latitude'])
            lng = float(place['Longitude'])
            g_lat = round(google_place['geometry']['location']['lat'], 6)
            g_lng = round(google_place['geometry']['location']['lng'], 6)
            if str(lat) != str(g_lat):
                yield field_positions.get('Latitude'), f"Latitude does not match with Google: {lat} -> {g_lat}", logging.ERROR
            if str(lng) != str(g_lng):
                yield field_positions.get('Longitude'), f"Longitude does not match with Google: {lng} -> {g_lng}", logging.ERROR


class UnusedPlacesLinter(Linter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mentioned_places = set()
        for place_path in get_files_in_path(config.content_path, None, '.md'):
            with (config.content_path / place_path).open() as place_file:
                metadata, _ = parse_markdown_head_matter(place_file.readlines())
                related_places = [
                    value
                    for key, values in metadata.items()
                    for value in values
                    if key.startswith('related_') and value.startswith('places/')
                ]
                self.mentioned_places.update(related_places)

    def lint(self, file_path: Path):
        if file_path.is_relative_to(Path('places')) and str(file_path) not in self.mentioned_places:
            yield None, "Place is not used anywhere", logging.ERROR
