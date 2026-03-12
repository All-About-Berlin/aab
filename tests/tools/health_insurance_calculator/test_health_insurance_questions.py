import pytest
from . import (
    assert_stage,
    occupations,
    see_options,
    fill_calculator_until,
    get_calculator,
    select_occupation,
)
from playwright.sync_api import expect

import re


@pytest.mark.parametrize("occupation", occupations, ids=occupations)
def test_questions_by_occupation(page, test_screenshot, occupation):
    fill_calculator_until(page, "questions", occupation=occupation)
    test_screenshot(page, get_calculator(page))

    page.get_by_label("Go back").click()
    assert_stage(page, "occupation")


def test_data_validity_check(page, test_screenshot):
    fill_calculator_until(page, "questions", occupation="employee")
    expect(get_calculator(page)).not_to_have_class(re.compile(r".*show-errors.*"))

    see_options(page)

    expect(get_calculator(page)).to_have_class(re.compile(r".*show-errors.*"))

    test_screenshot(page, get_calculator(page))


def test_its_complicated_no_questions(page, test_screenshot):
    fill_calculator_until(page, "occupation")
    select_occupation(page, occupation="other")
    assert_stage(page, "askABroker")
    test_screenshot(page, get_calculator(page))

    page.click("text=WhatsApp")
    page.get_by_label("Go back").click()
    assert_stage(page, "occupation")
