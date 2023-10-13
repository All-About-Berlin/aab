from playwright.sync_api import expect
from utils import fill_abmeldung_form_until, fill_person, next_step, previous_step, add_person


def test_data_remembered(page):
    fill_abmeldung_form_until(page, 'addPeople')
    fill_person(page)
    for index in range(1, 4):
        add_person(page)
        fill_person(page, index)

    next_step(page)
    previous_step(page)

    for index in range(0, 4):
        expect(page.get_by_label("Title").nth(index)).to_have_value("Dr.")
        expect(page.get_by_label("Name at birth").nth(index)).to_have_value("Nicole Bouliane")

        expect(page.get_by_text("Male", exact=True).nth(index)).to_be_checked()

        expect(page.get_by_label("Nationality").nth(index)).to_have_value("Canada")
        expect(page.get_by_label("Religion").nth(index)).to_have_value("Sonstiges, nicht kirchensteuerpflichtig")

        expect(page.get_by_title("Day of the month").nth(index)).to_have_value("10")
        expect(page.get_by_title("Month", exact=True).nth(index)).to_have_value("10")
        expect(page.get_by_title("Year").nth(index)).to_have_value("1990")
