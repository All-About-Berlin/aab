from playwright.sync_api import expect
from tests.test_data import people
from . import fill_tax_id_form_until, fill_address, next_step, previous_step, get_form
import re


def test_data_remembered_no_anmeldung(page, test_screenshot):
    fill_tax_id_form_until(page, "address", purpose="I can't register my address, but I need a tax ID")
    fill_address(page, purpose="I can't register my address, but I need a tax ID")
    next_step(page)
    previous_step(page)

    address = people[0]["local_address"]
    expect(page.get_by_label("Street address")).to_have_value(address["street"])
    expect(page.get_by_title("Postal code")).to_have_value(address["post_code"])
    expect(page.get_by_placeholder("Berlin", exact=True)).to_have_value(address["city"])
    expect(page.get_by_label("State")).to_have_value(address["state"][1])

    test_screenshot(page, get_form(page))


def test_data_remembered_living_abroad(page, test_screenshot):
    fill_tax_id_form_until(page, "address", purpose="I don't live in Germany, but I need a tax ID")
    fill_address(page, purpose="I don't live in Germany, but I need a tax ID")
    next_step(page)
    previous_step(page)

    address = people[0]["foreign_address"]
    expect(page.get_by_label("Street address")).to_have_value(address["street"])
    expect(page.get_by_label("City and post code")).to_have_value(" ".join([address["city"], address["post_code"]]))
    expect(page.get_by_label("Country")).to_have_value(address["country_code"])


def test_data_validity_check(page, test_screenshot):
    fill_tax_id_form_until(page, "address")

    expect(page.locator(".tax-id-form")).not_to_have_class(re.compile(r".*show-errors.*"))
    expect(page.get_by_label("Street address")).to_have_js_property("validity.valid", False)
    expect(page.get_by_title("City")).to_have_js_property("validity.valid", False)
    expect(page.get_by_title("Postal code (Postleitzahl)")).to_have_js_property("validity.valid", False)
    expect(page.get_by_label("State")).to_have_js_property("validity.valid", False)

    next_step(page)

    expect(page.locator(".tax-id-form")).to_have_class(re.compile(r".*show-errors.*"))
    expect(page.get_by_label("Street address")).to_have_js_property("validity.valid", False)
    expect(page.get_by_title("City")).to_have_js_property("validity.valid", False)
    expect(page.get_by_title("Postal code (Postleitzahl)")).to_have_js_property("validity.valid", False)
    expect(page.get_by_label("State")).to_have_js_property("validity.valid", False)

    test_screenshot(page, get_form(page))
