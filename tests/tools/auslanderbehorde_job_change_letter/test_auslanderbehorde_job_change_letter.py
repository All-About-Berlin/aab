from playwright.sync_api import expect
import pytest


@pytest.fixture
def job_change_letter_generator(page):
    page.clock.set_fixed_time("2026-02-22T10:00:00")
    page.goto("/tests/tools/auslaenderbehoerde-job-change-letter")
    return page.get_by_role("group", name="Ausländerbehörde job change notice letter generator")


def test_snapshot(page, job_change_letter_generator, test_screenshot):
    tool = job_change_letter_generator
    test_screenshot(page, tool)
    tool.get_by_role("button", name="Customize").click()

    tool.get_by_label("I was fired or laid off").check()
    expect(tool).not_to_contain_text("In Berlin, use the official form to report a job change.")

    tool.get_by_label("I am changing jobs").check()
    expect(tool).to_contain_text("In Berlin, use the official form to report a job change.")

    tool.get_by_label("I quit my job").check()
    expect(tool).not_to_contain_text("In Berlin, use the official form to report a job change.")

    tool.get_by_label("Last day of work").fill("2021-02-03")

    tool.get_by_label("Your full name").fill("John Smith")
    tool.get_by_label("Your address").fill("Pasewalker Straße 65\n13127 Berlin")

    tool.get_by_label("Date of birth").fill("1993-04-05")
    tool.get_by_label("Place of birth").fill("Montreal, Canada")
    tool.get_by_label("Nationality").select_option("Turkey")

    tool.get_by_role("button", name="Preview").click()
    test_screenshot(page, tool)
