import pytest


@pytest.fixture
def ksk_cost_difference_calculator(page):
    page.goto("/tests/tools/ksk-cost-difference-calculator")
    return page.get_by_role("group", name="Künstlersozialkasse cost difference calculator")


def test_snapshot(page, ksk_cost_difference_calculator, test_screenshot):
    test_screenshot(page, ksk_cost_difference_calculator)
