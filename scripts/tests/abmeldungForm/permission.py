from playwright.sync_api import expect
from utils import fill_abmeldung_form_until, fill_permission, previous_step


def test_data_remembered(page):
    fill_abmeldung_form_until(page, 'permission')
    fill_permission(page)
    page.get_by_role("button", name="Finish").click()
    previous_step(page)

    expect(page.get_by_label("I allow All About Berlin to deregister my address at the Bürgeramt.")).to_be_checked()
    expect(page.locator("canvas")).not_to_have_class('empty')
    expect(page.get_by_label("Email")).to_have_value("contact@allaboutberlin.com")

    page.get_by_role("button", name="Finish").click()
    expect(page.get_by_text("One last thing")).to_have_count(1)
