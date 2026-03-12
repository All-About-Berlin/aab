from playwright.sync_api import expect
from . import fill_tax_id_form_until, fill_purpose, get_form


def test_invalid_options(page, test_screenshot):
    fill_tax_id_form_until(page, "purpose")
    continue_button = page.get_by_role("button", name="Continue")
    fill_purpose(page, "I can't register my address, but I need a tax ID")
    expect(continue_button).not_to_be_disabled()
    fill_purpose(page, "I don't live in Germany, but I need a tax ID")
    expect(continue_button).not_to_be_disabled()
    fill_purpose(page, "I have a business, and I need a tax number or a VAT number ")
    expect(continue_button).to_be_disabled()
    fill_purpose(page, "I forgot my tax ID")
    expect(continue_button).to_be_disabled()
    fill_purpose(page, "Something else")
    expect(continue_button).to_be_disabled()

    test_screenshot(page, get_form(page))
