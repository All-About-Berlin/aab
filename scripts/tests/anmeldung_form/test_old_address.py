from playwright.sync_api import expect
from ..test_data import people
from ..anmeldung_form import fill_anmeldung_form_until, fill_old_address, next_step, previous_step


def test_data_remembered(page):
    fill_anmeldung_form_until(page, 'oldAddress')
    fill_old_address(page)
    next_step(page)
    previous_step(page)

    address = people[0]['local_address_2']
    expect(page.get_by_label("Country")).to_have_value(address['country'])
    expect(page.get_by_label("Street address")).to_have_value(address['street'])
    expect(page.get_by_placeholder("12345")).to_have_value(address['post_code'])
    expect(page.get_by_placeholder("Berlin")).to_have_value(address['city'])
    expect(page.get_by_label("Building details")).to_have_value(address['zusatz'])
    expect(page.get_by_label("State")).to_have_value(address['state'][1])
