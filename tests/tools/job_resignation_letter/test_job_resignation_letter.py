import pytest


@pytest.fixture
def job_resignation_letter_generator(page):
    page.clock.set_fixed_time("2026-02-22T10:00:00")
    page.goto("/tests/tools/job-resignation-letter")
    return page.get_by_role("group", name="Job resignation letter generator")


def test_snapshot(page, job_resignation_letter_generator, test_screenshot):
    tool = job_resignation_letter_generator
    test_screenshot(page, tool)
    tool.get_by_role("button", name="Customize").click()

    tool.get_by_label("Your full name").fill("John Smith")
    tool.get_by_label("Your address").fill("Pasewalker Straße 65\n13127 Berlin")
    tool.get_by_label("Employee number").fill("AB1234567")

    tool.get_by_label("Employer name").fill("ACME GmbH")
    tool.get_by_label("Employer address").fill("Arbeitstraße 78\n12345 Berlin")

    # Recipient name
    tool.locator(".gender-input").select_option("Madam")
    tool.locator(".first-name-input").fill("Katharina")
    tool.locator(".last-name-input").fill("Bossmann")

    tool.get_by_label("Last day of work", exact=True).fill("2022-03-04")

    tool.get_by_label("Provisional letter of reference").check()
    tool.get_by_label("Qualified letter of reference").check()

    tool.get_by_role("button", name="Preview and print").click()
    test_screenshot(page, tool)
