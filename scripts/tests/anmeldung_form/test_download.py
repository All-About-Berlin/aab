from playwright.sync_api import expect
from ..test_data import people
from ..anmeldung_form import fill_anmeldung_form_until


def test_download_button(page):
    fill_anmeldung_form_until(page, 'options')


def test_download_button_multiple_people(page):
    fill_anmeldung_form_until(page, 'options', multiple_people=True)

    download_1 = page.get_by_role("button", name="Download your Anmeldung form (part 1)")
    expect(download_1).to_contain_text(people[0]['first_name'])
    expect(download_1).to_contain_text(people[1]['first_name'])

    download_2 = page.get_by_role("button", name="Download your Anmeldung form (part 2)")
    expect(download_2).to_contain_text(people[2]['first_name'])
    expect(download_2).to_contain_text(people[3]['first_name'])

    download_3 = page.get_by_role("button", name="Download your Anmeldung form (part 3)")
    expect(download_3).to_contain_text(people[4]['first_name'])
