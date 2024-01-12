from playwright.sync_api import expect
from ..anmeldung_form import fill_anmeldung_form_until, fill_people, fill_bei_address, fill_documents, previous_step, \
    next_step
from ..test_data import people


def test_data_remembered(page):
    fill_anmeldung_form_until(page, 'addPeople')

    fill_people(page, multiple_people=True)
    next_step(page)

    fill_bei_address(page, multiple_people=True)
    next_step(page)

    fill_documents(page, multiple_people=True)

    page.get_by_role("button", name="Finish").click()
    previous_step(page)

    for index in range(0, 5):
        doc = people[index]['id_document']
        expect(page.get_by_label(doc['type'][0], exact=True).nth(index)).to_be_checked()
        expect(page.get_by_label('number').nth(index)).to_have_value(doc['number'])

        year, month, day = doc['issue_date']
        expect(page.get_by_title("Day of the month").nth(index * 2)).to_have_value(day)
        expect(page.get_by_title("Month", exact=True).nth(index * 2)).to_have_value(month)
        expect(page.get_by_title("Year").nth(index * 2)).to_have_value(year)

        expect(page.get_by_label('Issuing authority').nth(index)).to_have_value(doc['authority'])

        year, month, day = doc['expiration_date']
        expect(page.get_by_title("Day of the month").nth(index * 2 + 1)).to_have_value(day)
        expect(page.get_by_title("Month", exact=True).nth(index * 2 + 1)).to_have_value(month)
        expect(page.get_by_title("Year").nth(index * 2 + 1)).to_have_value(year)
