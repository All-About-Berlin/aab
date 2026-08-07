from playwright.sync_api import expect
from . import (
    fill_anmeldung_form_until,
    fill_bei_address,
    next_step,
    previous_step,
    fill_people,
)


def test_data_remembered(page, test_screenshot):
    fill_anmeldung_form_until(page, "beiAddress", people_count=1)
    fill_bei_address(page, people_count=1)

    expect(page.get_by_label("My name is on my mailbox")).not_to_be_checked()
    expect(page.get_by_label("Name on mailbox")).to_have_value("Müller")

    next_step(page)
    previous_step(page)

    expect(page.get_by_label("My name is on my mailbox")).not_to_be_checked()
    expect(page.get_by_label("Name on mailbox")).to_have_value("Müller")

    form = page.get_by_role("group", name="Anmeldung form filler")
    test_screenshot(page, form)


def test_pluralisation(page):
    fill_anmeldung_form_until(page, "addPeople")
    fill_people(page, people_count=2)
    next_step(page)
    expect(page.get_by_label("Our names are on our mailbox")).to_be_checked()
