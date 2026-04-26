from pathlib import Path
from playwright.sync_api import expect
import json
import pytest

test_data_dir = Path(__file__).parent


def mock_places_json(page, body):
    page.route(
        "**/places/test-places.json",
        lambda route: route.fulfill(status=200, content_type="application/json", body=body),
    )


@pytest.fixture
def places_map(page):
    mock_places_json(page, (test_data_dir / "test-places.json").read_text())
    page.goto("/tests/tools/places-map")
    return page.get_by_label("Map with list of places")


@pytest.fixture
def places_map_no_insurance(page):
    data = json.loads((test_data_dir / "test-places.json").read_text())
    for place in data["places"]:
        place.pop("acceptsPublicHealthInsurance", None)
    mock_places_json(page, json.dumps(data))
    page.goto("/tests/tools/places-map")
    return page.get_by_label("Map with list of places")


def test_places_list_shows_all_places(page, places_map, test_screenshot):
    test_screenshot(page, places_map)
    items = places_map.locator("ol > li")
    expect(items).to_have_count(5)
    expect(items.nth(0)).to_contain_text("Test Place Alpha")
    expect(items.nth(0).locator("h4 a")).to_have_attribute("href", "https://example.com/alpha")
    expect(items.nth(0)).to_contain_text("Speaks English and German")
    expect(items.nth(0).locator("address")).to_contain_text("Mitte")

    expect(items.nth(1)).to_contain_text("Test Place Beta")
    expect(items.nth(1).locator("address")).to_contain_text("Charlottenburg")
    expect(items.nth(2)).to_contain_text("Test Place Gamma")
    expect(items.nth(2)).to_contain_text("Open on weekends")
    expect(items.nth(3)).to_contain_text("Test Place Delta")
    expect(items.nth(4)).to_contain_text("Test Place Epsilon")


def test_recommended_badge(page, places_map):
    expect(places_map.locator("ol > li").nth(0).locator(".recommended")).to_be_visible()
    expect(places_map.locator("ol > li").nth(1).locator(".recommended")).to_have_count(0)


def test_health_insurance_pill(page, places_map):
    expect(places_map.locator("ol > li").nth(1).locator(".pill")).to_have_count(0)

    pill = places_map.locator("ol > li").nth(0).locator(".pill.yes")
    expect(pill).to_be_visible()
    expect(pill).to_contain_text("Public health insurance")


def test_health_insurance_filter_visible(page, places_map):
    places_map.locator("details summary").click()
    expect(places_map.locator("select").nth(1)).to_be_visible()


def test_health_insurance_filter_not_visible(page, places_map_no_insurance):
    places_map_no_insurance.locator("details summary").click()
    expect(places_map_no_insurance.locator("select")).to_have_count(1)


def test_filter_by_borough(page, places_map):
    places_map.locator("details summary").click()
    places_map.locator("select").first.select_option("borough-Neukölln")

    items = places_map.locator("ol > li")
    expect(items).to_have_count(2)
    expect(items.nth(0)).to_contain_text("Test Place Gamma")
    expect(items.nth(1)).to_contain_text("Test Place Epsilon")


def test_filter_by_suburb(page, places_map):
    places_map.locator("details summary").click()
    places_map.locator("select").first.select_option("suburb-Prenzlauer Berg")

    items = places_map.locator("ol > li")
    expect(items).to_have_count(1)
    expect(items.nth(0)).to_contain_text("Test Place Delta")


def test_filter_by_health_insurance(page, places_map):
    places_map.locator("details summary").click()
    places_map.locator("select").nth(1).select_option(label="Public health insurance")

    # Pills should not be shown when the filter is active (redundant info)
    expect(places_map.locator("ol .pill")).to_have_count(0)

    items = places_map.locator("ol > li")
    expect(items).to_have_count(2)
    expect(items.nth(0)).to_contain_text("Test Place Alpha")
    expect(items.nth(1)).to_contain_text("Test Place Gamma")


def test_filter_no_results(page, places_map):
    places_map.locator("details summary").click()
    places_map.locator("select").first.select_option("suburb-Charlottenburg")
    places_map.locator("select").nth(1).select_option(label="Public health insurance")

    items = places_map.locator("ol > li")
    expect(items).to_have_count(1)
    expect(items.first).to_contain_text("No places match your criteria")


def test_filter_reset(page, places_map):
    places_map.locator("details summary").click()
    places_map.locator("select").first.select_option("borough-Neukölln")
    expect(places_map.locator("ol > li")).to_have_count(2)

    places_map.locator("select").first.select_option(label="Anywhere")
    expect(places_map.locator("ol > li")).to_have_count(5)


def test_add_place(page, places_map):
    places_map.locator("button.add").click()
    expect(places_map.locator(".place-suggestion-form")).to_be_visible()
    expect(places_map.locator("ol")).not_to_be_visible()


def test_add_place_cancel(page, places_map):
    places_map.locator("button.add").click()
    expect(places_map.locator(".place-suggestion-form")).to_be_visible()

    places_map.locator(".place-suggestion-form button", has_text="Go back").click()
    expect(places_map.locator("ol")).to_be_visible()
    expect(places_map.locator(".place-suggestion-form")).not_to_be_visible()
