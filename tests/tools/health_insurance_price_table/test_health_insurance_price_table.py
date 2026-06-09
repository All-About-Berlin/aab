import pytest


@pytest.fixture
def price_table(page):
    page.goto("/tests/tools/health-insurance-price-table")
    return page.locator(".health-insurance-price-table")


def test_snapshot(price_table, test_screenshot):
    price_table.get_by_text("Freelancer", exact=True).set_checked(True)
    test_screenshot(price_table.page, price_table)
