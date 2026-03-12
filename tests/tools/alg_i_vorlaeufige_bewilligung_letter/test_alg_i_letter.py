import pytest


@pytest.fixture
def alg_i_letter_generator(page):
    page.clock.set_fixed_time("2026-02-22T10:00:00")
    page.goto("/tests/tools/alg-i-vorlaeufige-bewilligung")
    return page.get_by_role("group", name="Letter generator to request a preliminary decision for ALG I")


def test_snapshot(page, alg_i_letter_generator, test_screenshot):
    tool = alg_i_letter_generator
    test_screenshot(page, tool)
    tool.get_by_role("button", name="Customize").click()
    tool.get_by_label("Your full name").fill("John Smith")
    tool.get_by_label("Your address").fill("Wohnungstr. 123\n13122 Berlin")
    tool.get_by_label("Agentur für Arbeit address").fill("Finanzstraße 54\n10115 Berlin")

    # Recipient name
    tool.locator(".gender-input").select_option("Madam")
    tool.locator(".first-name-input").fill("Katharina")
    tool.locator(".last-name-input").fill("Verwalterin")

    tool.get_by_label("Case number").fill("C4S3NUMB3R")

    tool.get_by_role("button", name="Preview").click()
    test_screenshot(page, tool)
