#!/usr/bin/env python3
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse
from ursus.config import config
from ursus.linters import Linter, LinterResult
import googlemaps
import logging
import re
import requests
import time
import yaml


def get_google_place(place_id: str) -> dict:
    google_place = googlemaps.Client(key=config.google_maps_places_api_key).place(place_id, language="en")["result"]
    return {
        "name": google_place["name"],
        "address": re.sub(r"(, (\d{5} )?Berlin)?, Germany$", "", google_place["formatted_address"]).strip(),
        "latitude": str(round(google_place["geometry"]["location"]["lat"], 6)),
        "longitude": str(round(google_place["geometry"]["location"]["lng"], 6)),
        "website": google_place.get("website"),
        "business_status": google_place.get("business_status"),
    }


def fill_area_information(place: dict) -> None:
    """
    Fill the Bezirk, Ortsteil and Kiez information using the Nominatim API.
    """
    response = requests.get(
        "https://nominatim.openstreetmap.org/reverse",
        params={
            "format": "json",
            "lat": place["latitude"],
            "lon": place["longitude"],
            "addressdetails": 1,
        },
        headers={
            "User-Agent": "AllAboutBerlin (contact@allaboutberlin.com)",
        },
    )
    response.raise_for_status()
    nominatim_address = response.json()["address"]
    place["borough"] = nominatim_address.get("borough")
    place["suburb"] = nominatim_address.get("suburb")
    place["quarter"] = nominatim_address.get("quarter")

    city = nominatim_address.get("city")
    if city and city != "Berlin":
        place["city"] = city

    time.sleep(1)  # Debounce nominatim requests


class PlacesLinter(Linter):
    """
    Verify lists of places against the Google Maps API every few months
    """

    verification_frequency = timedelta(days=180)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def lint(self, file_path: Path) -> LinterResult:
        if file_path.suffix.lower() != ".yaml" or not file_path.is_relative_to(Path("places")):
            return

        yaml_path = config.content_path / file_path
        places = yaml.safe_load(yaml_path.read_text())
        list_modified = False
        to_remove = []

        for i, place in enumerate(places):
            name = place.get("name", f"place #{i + 1}")

            if not place.get("borough") and not place.get("suburb"):
                fill_area_information(place)
                yield None, f"{name}: Filled borough/suburb from Nominatim", logging.INFO
                list_modified = True

            last_verified = place.get("last_verified")
            if last_verified and (date.today() - last_verified) < self.verification_frequency:
                continue

            if not place.get("google_place_id"):
                yield None, f"{name}: Place has no place ID", logging.WARNING
                continue

            yield from self.lint_place(place, i)

            if place.get("status") == "CLOSED_PERMANENTLY":
                to_remove.append(i)
            else:
                place["last_verified"] = date.today()

            list_modified = True

        for i in reversed(to_remove):
            places.pop(i)

        if list_modified:
            logging.info(f"Updating {file_path}")
            yaml_path.write_text(yaml.dump(places, allow_unicode=True, sort_keys=False, width=120))

    def lint_place(self, place: dict, index: int) -> LinterResult:
        name = place.get("name", f"place #{index + 1}")

        try:
            google_place = get_google_place(place["google_place_id"])
        except googlemaps.exceptions.ApiError as e:
            yield None, f"{name}: Place error: {e}", logging.ERROR
            return

        meta_website = urlparse(place.get("website", "")).netloc if place.get("website") else None
        if google_place["website"] and meta_website != urlparse(google_place["website"]).netloc:
            yield (
                None,
                f"{name}: Website does not match with Google: {meta_website} -> {google_place['website']}",
                logging.WARNING,
            )

        if place.get("address") != google_place["address"]:
            yield (
                None,
                f"{name}: Address does not match with Google: {place.get('address')} -> {google_place['address']}",
                logging.ERROR,
            )
            place["address"] = google_place["address"]

        business_status = google_place["business_status"]
        if business_status and business_status != "OPERATIONAL":
            yield None, f"{name}: Business is {business_status}", logging.ERROR
            place["status"] = business_status
        else:
            place.pop("status", None)

        location_changed = False
        lat = str(float(place.get("latitude", 0)))
        lng = str(float(place.get("longitude", 0)))
        if lat != google_place["latitude"]:
            yield (
                None,
                f"{name}: Latitude does not match with Google: {lat} -> {google_place['latitude']}",
                logging.ERROR,
            )
            place["latitude"] = google_place["latitude"]
            location_changed = True
        if lng != google_place["longitude"]:
            yield (
                None,
                f"{name}: Longitude does not match with Google: {lng} -> {google_place['longitude']}",
                logging.ERROR,
            )
            place["longitude"] = google_place["longitude"]
            location_changed = True

        if location_changed:
            fill_area_information(place)
            yield None, f"{name}: Filled borough/suburb from Nominatim", logging.INFO
