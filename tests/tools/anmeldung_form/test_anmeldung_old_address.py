from playwright.sync_api import expect
from tests.test_data import people
from . import (
    fill_anmeldung_form_until,
    fill_old_address,
    next_step,
    previous_step,
)
import re


def test_data_remembered(page, test_screenshot):
    fill_anmeldung_form_until(page, "oldAddress")
    fill_old_address(page)
    next_step(page)
    previous_step(page)

    address = people[0]["local_address_2"]
    expect(page.get_by_label("Country")).to_have_value(address["country_code"])
    expect(page.get_by_label("Street address")).to_have_value(address["street"])
    expect(page.get_by_title("Postal code")).to_have_value(address["post_code"])
    expect(page.get_by_placeholder("Berlin")).to_have_value(address["city"])
    expect(page.get_by_label("Building details")).to_have_value(address["zusatz"])
    expect(page.get_by_label("State")).to_have_value(address["state"][1])

    form = page.get_by_role("group", name="Tool to fill the Anmeldung form")
    test_screenshot(page, form)


def test_data_validity_check(page, test_screenshot):
    fill_anmeldung_form_until(page, "oldAddress")

    page.get_by_label("Country").select_option("Germany")

    expect(page.locator(".anmeldung-form")).not_to_have_class(re.compile(r".*show-errors.*"))
    expect(page.get_by_label("Street address")).to_have_js_property("validity.valid", False)
    expect(page.get_by_title("City")).to_have_js_property("validity.valid", False)
    expect(page.get_by_title("Postal code (Postleitzahl)")).to_have_js_property("validity.valid", False)
    expect(page.get_by_label("Building details")).to_have_js_property("validity.valid", True)
    expect(page.get_by_label("State")).to_have_js_property("validity.valid", False)

    next_step(page)

    expect(page.locator(".anmeldung-form")).to_have_class(re.compile(r".*show-errors.*"))
    expect(page.get_by_label("Street address")).to_have_js_property("validity.valid", False)
    expect(page.get_by_title("City")).to_have_js_property("validity.valid", False)
    expect(page.get_by_title("Postal code (Postleitzahl)")).to_have_js_property("validity.valid", False)
    expect(page.get_by_label("State")).to_have_js_property("validity.valid", False)

    form = page.get_by_role("group", name="Tool to fill the Anmeldung form")
    test_screenshot(page, form)


def test_data_not_germany(page, test_screenshot):
    fill_anmeldung_form_until(page, "oldAddress")

    page.get_by_label("Country").select_option("Canada")
    expect(page.locator(".input-instructions")).to_have_text("You don't need to share your foreign address.")

    next_step(page)

    expect(page.locator(".anmeldung-form")).not_to_have_class(re.compile(r".*show-errors.*"))

    form = page.get_by_role("group", name="Tool to fill the Anmeldung form")
    test_screenshot(page, form)
