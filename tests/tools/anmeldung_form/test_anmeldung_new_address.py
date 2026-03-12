from playwright.sync_api import expect
from tests.test_data import people
from . import (
    fill_anmeldung_form_until,
    fill_new_address,
    next_step,
    previous_step,
)
import re


def test_data_remembered(page, test_screenshot):
    fill_anmeldung_form_until(page, "newAddress")
    fill_new_address(page)
    next_step(page)
    previous_step(page)

    address = people[0]["local_address"]
    expect(page.get_by_label("Street address")).to_have_value(address["street"])
    expect(page.get_by_label("Post code")).to_have_value(address["post_code"])
    expect(page.get_by_label("Building details")).to_have_value(address["zusatz"])
    expect(page.get_by_label("Move-in date")).to_have_value(people[0]["move_out_date"])

    form = page.get_by_role("group", name="Tool to fill the Anmeldung form")
    test_screenshot(page, form)


def test_data_validity_check(page, test_screenshot):
    fill_anmeldung_form_until(page, "newAddress")

    expect(page.locator(".anmeldung-form")).not_to_have_class(re.compile(r".*show-errors.*"))
    expect(page.get_by_label("Street address")).to_have_js_property("validity.valid", False)
    expect(page.get_by_label("Post code")).to_have_js_property("validity.valid", False)
    expect(page.get_by_label("Building details")).to_have_js_property("validity.valid", True)

    next_step(page)

    expect(page.locator(".anmeldung-form")).to_have_class(re.compile(r".*show-errors.*"))
    expect(page.get_by_label("Street address")).to_have_js_property("validity.valid", False)
    expect(page.get_by_label("Post code")).to_have_js_property("validity.valid", False)

    form = page.get_by_role("group", name="Tool to fill the Anmeldung form")
    test_screenshot(page, form)
