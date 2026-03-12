from playwright.sync_api import expect
from . import (
    fill_anmeldung_form_until,
    fill_people,
    fill_bei_address,
    fill_documents,
    previous_step,
    next_step,
)
from tests.test_data import people


def test_data_remembered(page, test_screenshot):
    fill_anmeldung_form_until(page, "addPeople")

    fill_people(page, multiple_people=True)
    next_step(page)

    fill_bei_address(page, multiple_people=True)
    next_step(page)

    fill_documents(page, multiple_people=True)

    page.get_by_role("button", name="Finish").click()
    previous_step(page)

    for index in range(0, 5):
        doc = people[index]["id_document"]
        # expect(page.get_by_label(doc['type'][0], exact=True).nth(index)).to_be_checked()
        expect(page.get_by_label("number").nth(index)).to_have_value(doc["number"])
        expect(page.get_by_label("Date issued").nth(index)).to_have_value(doc["issue_date"])
        expect(page.get_by_label("Issuing authority").nth(index)).to_have_value(doc["authority"])
        expect(page.get_by_label("Expiration date").nth(index)).to_have_value(doc["expiration_date"])

    form = page.get_by_role("group", name="Tool to fill the Anmeldung form")
    test_screenshot(page, form)
