#!/usr/bin/env python3
from pathlib import Path
from datetime import date
from extensions.linters.places import get_google_place, fill_area_information
from ursus.config import config
from ursus.utils import import_module_or_path
import difflib
import logging
import os
import requests
import subprocess
import yaml


API_ENDPOINT = "https://allaboutberlin.com/api/forms/place-suggestion"


def format_description(notes: str, languages: str) -> str:
    parts = []
    if notes:
        parts.append(notes if notes.endswith(".") else f"{notes}.")
    if languages:
        parts.append(f"They speak {languages}.")
    return " ".join(parts)


def get_place_suggestions():
    if not config.allaboutberlin_api_username and config.allaboutberlin_api_password:
        raise Exception("config.allaboutberlin_api_username and config.allaboutberlin_api_password must be set")

    url = f"{API_ENDPOINT}?count=10"
    while url:
        response = requests.get(
            url,
            auth=(config.allaboutberlin_api_username, config.allaboutberlin_api_password),
        )
        response.raise_for_status()
        data = response.json()
        yield from data["results"]
        url = data.get("next")


def delete_suggestion(suggestion_id: int):
    if not config.allaboutberlin_api_username and config.allaboutberlin_api_password:
        raise Exception("config.allaboutberlin_api_username and config.allaboutberlin_api_password must be set")

    response = requests.delete(
        f"{API_ENDPOINT}/{suggestion_id}",
        auth=(config.allaboutberlin_api_username, config.allaboutberlin_api_password),
    )
    response.raise_for_status()


def diff_places(old: dict, new: dict) -> str:
    return "".join(
        difflib.unified_diff(
            yaml.dump(old, allow_unicode=True, sort_keys=False).splitlines(keepends=True),
            yaml.dump(new, allow_unicode=True, sort_keys=False).splitlines(keepends=True),
            fromfile="old",
            tofile="new",
        )
    )


def get_full_place_information(suggestion: dict) -> dict:
    google_place = get_google_place(suggestion["google_maps_id"])

    place = {"name": suggestion.get("business_name") or google_place["name"]}

    description = format_description(suggestion.get("notes", ""), suggestion.get("languages", ""))
    if description:
        place["description"] = description

    if google_place["website"]:
        place["website"] = google_place["website"]

    if suggestion.get("is_owner") and suggestion.get("email"):
        place["email"] = suggestion["email"]

    place["address"] = google_place["address"]
    place["latitude"] = google_place["latitude"]
    place["longitude"] = google_place["longitude"]
    place["google_place_id"] = suggestion["google_maps_id"]
    place["last_verified"] = date.today()

    fill_area_information(place)

    return place


def import_place_suggestions(suggestion: dict):
    business_name = suggestion.get("business_name") or "<no name>"
    yaml_path = config.content_path / f"places/{suggestion['category']}.yaml"

    if not yaml_path.exists():
        raise ValueError(f"Skipping {business_name!r}: {yaml_path.name} does not exist")
        return

    places = yaml.safe_load(yaml_path.read_text()) or []
    new_place = get_full_place_information(suggestion)

    places_by_id = {place_id: p for p in places if (place_id := p.get("google_place_id"))}
    new_place_id = suggestion["google_maps_id"]
    if existing_place := places_by_id.get(new_place_id):
        logging.warning(
            f"Duplicate place in {yaml_path.name}: {new_place['name']}\n{diff_places(existing_place, new_place)}"
        )
        return

    logging.info(
        f"\n{new_place['name']} → {yaml_path.relative_to(config.content_path.parent)}\n"
        f"{yaml.dump([new_place], allow_unicode=True, sort_keys=False)}"
    )

    while True:
        choice = input("(a)dd, add and (e)dit, (i)gnore? ").strip().lower()
        if choice in ("a", "e", "i"):
            break

    if choice == "i":
        return

    places.append(new_place)
    yaml_path.write_text(yaml.dump(places, allow_unicode=True, sort_keys=False, width=120))

    if choice == "e":
        editor = os.environ.get("EDITOR") or "vi"
        subprocess.run([editor, str(yaml_path)])

    delete_suggestion(suggestion["id"])
    logging.info(f"Added {new_place['name']} to {yaml_path.name}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    import_module_or_path(Path(__file__).parent.parent / "ursus_config.py")

    for suggestion in get_place_suggestions():
        try:
            import_place_suggestions(suggestion)
        except Exception:
            logging.exception(f"Error processing suggestion #{suggestion.get('id')}")
    else:
        logging.info("No place suggestions found")
