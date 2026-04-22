#!/usr/bin/env python3
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse
from ursus.config import config
from ursus.linters import Linter, LinterResult
import googlemaps
import json
import logging
import re
import requests
import time


def reverse_geocode(lat: float, lng: float) -> dict:
    """
    Fill the Bezirk, Ortsteil and Kiez information using the Nominatim API.
    """
    response = requests.get(
        "https://nominatim.openstreetmap.org/reverse",
        params={
            "format": "json",
            "lat": lat,
            "lon": lng,
            "addressdetails": 1,
        },
        headers={
            "User-Agent": "AllAboutBerlin (contact@allaboutberlin.com)",
        },
    )
    response.raise_for_status()
    return response.json().get("address", {})


class PlacesLinter(Linter):
    """
    Verify lists of places against the Google Maps API every few months
    """

    verification_frequency = timedelta(days=180)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.google_maps = googlemaps.Client(key=config.google_maps_places_api_key)

    def lint(self, file_path: Path) -> LinterResult:
        if file_path.suffix.lower() != ".json" or not file_path.is_relative_to(Path("places")):
            return

        json_path = config.content_path / file_path
        data = json.loads(json_path.read_text())
        list_modified = False
        to_remove = []

        for i, place in enumerate(data.get("places", [])):
            last_verified = place.get("lastVerified")
            if last_verified and (date.today() - date.fromisoformat(last_verified)) < self.verification_frequency:
                continue

            if not place.get("googlePlaceId"):
                name = place.get("name", f"place #{i + 1}")
                yield None, f"{name}: Place has no place ID", logging.WARNING
                continue

            yield from self.lint_place(place, i)

            if place.get("status") == "CLOSED_PERMANENTLY":
                to_remove.append(i)
            else:
                place["lastVerified"] = date.today().isoformat()

            list_modified = True

        for i in reversed(to_remove):
            data["places"].pop(i)

        if list_modified:
            logging.info(f"Updating {file_path}")
            json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    def lint_place(self, place: dict, index: int) -> LinterResult:
        name = place.get("name", f"place #{index + 1}")

        try:
            google_place = self.google_maps.place(place["googlePlaceId"], language="en")["result"]
        except googlemaps.exceptions.ApiError as e:
            yield None, f"{name}: Place error: {e}", logging.ERROR
            return

        meta_website = urlparse(place.get("website", "")).netloc if place.get("website") else None
        if google_place.get("website") and meta_website != urlparse(google_place.get("website")).netloc:
            yield (
                None,
                f"{name}: Website does not match with Google: {meta_website} -> {google_place.get('website')}",
                logging.WARNING,
            )

        google_address = re.sub(r"(, (\d{5} )?Berlin)?, Germany$", "", google_place["formatted_address"]).strip()
        if place.get("address") != google_address:
            yield (
                None,
                f"{name}: Address does not match with Google: {place.get('address')} -> {google_address}",
                logging.ERROR,
            )
            place["address"] = google_address

        business_status = google_place.get("business_status")
        if business_status and business_status != "OPERATIONAL":
            yield None, f"{name}: Business is {business_status}", logging.ERROR
            place["status"] = business_status
        else:
            place.pop("status", None)

        location_changed = False
        lat = float(place.get("latitude", 0))
        lng = float(place.get("longitude", 0))
        g_lat = round(google_place["geometry"]["location"]["lat"], 6)
        g_lng = round(google_place["geometry"]["location"]["lng"], 6)
        if str(lat) != str(g_lat):
            yield None, f"{name}: Latitude does not match with Google: {lat} -> {g_lat}", logging.ERROR
            place["latitude"] = str(g_lat)
            location_changed = True
        if str(lng) != str(g_lng):
            yield None, f"{name}: Longitude does not match with Google: {lng} -> {g_lng}", logging.ERROR
            place["longitude"] = str(g_lng)
            location_changed = True

        if location_changed or not place.get("borough") or not place.get("suburb"):
            nominatim_address = reverse_geocode(float(place["latitude"]), float(place["longitude"]))
            place["borough"] = nominatim_address.get("borough")
            place["suburb"] = nominatim_address.get("suburb")
            place["quarter"] = nominatim_address.get("quarter")

            city = nominatim_address.get("city")
            if city and city != "Berlin":
                place["city"] = city

            yield None, f"{name}: Missing borough or suburb", logging.ERROR

            time.sleep(1)  # Debounce nominatim requests
