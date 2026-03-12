from playwright.sync_api import expect
from tests.test_data import people
from . import fill_tax_id_form_until, fill_people, next_step, previous_step, get_form


def test_data_remembered(page, test_screenshot):
    fill_tax_id_form_until(page, "addPeople")
    fill_people(page, multiple_people=True)

    next_step(page)
    previous_step(page)

    for index in range(0, 5):
        person = people[index]
        expect(page.get_by_title("First name").nth(index)).to_have_value(person["first_name"])
        expect(page.get_by_title("Last name").nth(index)).to_have_value(person["last_name"])
        expect(page.get_by_label("Name at birth").nth(index)).to_have_value(person["birth_name"])
        expect(page.get_by_label("Place of birth").nth(index)).to_have_value(person["birth_place"])
        expect(page.get_by_label("Date of birth").nth(index)).to_have_value(person["birth_date"])

    test_screenshot(page, get_form(page))
