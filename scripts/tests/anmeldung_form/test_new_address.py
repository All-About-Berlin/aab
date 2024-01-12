from playwright.sync_api import expect
from ..test_data import people
from ..anmeldung_form import fill_anmeldung_form_until, fill_new_address, next_step, previous_step


def test_data_remembered(page):
    fill_anmeldung_form_until(page, 'newAddress')
    fill_new_address(page)
    next_step(page)
    previous_step(page)

    address = people[0]['local_address']
    expect(page.get_by_label("Street address")).to_have_value(address['street'])
    expect(page.get_by_label("Post code")).to_have_value(address['post_code'])
    expect(page.get_by_label("Building details")).to_have_value(address['zusatz'])

    year, month, day = people[0]['move_out_date']
    expect(page.get_by_title("Day of the month")).to_have_value(day)
    expect(page.get_by_title("Month", exact=True)).to_have_value(month)
    expect(page.get_by_title("Year")).to_have_value(year)
