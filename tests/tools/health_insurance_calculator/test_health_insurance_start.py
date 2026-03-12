from . import fill_calculator_until, occupations, get_calculator
import pytest


def test_first_step(page, test_screenshot):
    fill_calculator_until(page, "occupation")
    test_screenshot(page, get_calculator(page))


@pytest.mark.parametrize("occupation", occupations, ids=occupations)
def test_first_step_preset_occupation(page, test_screenshot, occupation):
    fill_calculator_until(page, "occupation", preset_occupation=True, occupation=occupation)
    test_screenshot(page, get_calculator(page))
