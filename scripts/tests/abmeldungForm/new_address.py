from playwright.sync_api import expect
from utils import fill_abmeldung_form_until, fill_new_address, next_step, previous_step


def test_data_remembered(page):
    fill_abmeldung_form_until(page, 'newAddress')
    fill_new_address(page)
    next_step(page)
    previous_step(page)

    expect(page.get_by_label("Street address")).to_have_value("123 des Érables")
    expect(page.get_by_label("City and post code")).to_have_value("Montreal, Quebec, J2J 2W5")
    expect(page.get_by_label("Country")).to_have_value("Canada")
