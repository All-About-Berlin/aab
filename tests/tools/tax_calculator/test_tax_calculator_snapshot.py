def test_snapshot(page, test_screenshot):
    page.goto("/tests/tools/tax-calculator")
    calculator = page.get_by_role("group", name="German tax calculator")
    test_screenshot(page, calculator)
    page.get_by_role("link", name="Show options").click()
    test_screenshot(page, calculator)
