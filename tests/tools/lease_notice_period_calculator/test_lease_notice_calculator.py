from playwright.sync_api import expect


def test_results(page, test_screenshot):
    page.goto("/tests/tools/lease-notice-period-calculator")
    calculator = page.get_by_role("group", name="Lease notice period calculator")

    calculator.get_by_label("Notice date").fill("1992-01-01")
    expect(calculator.get_by_label("Move-out date")).to_have_value("1992-03-31")

    calculator.get_by_label("Move-out date").fill("1992-05-01")
    expect(calculator.get_by_label("Notice date")).to_have_value("1992-03-04")

    test_screenshot(page, calculator)
