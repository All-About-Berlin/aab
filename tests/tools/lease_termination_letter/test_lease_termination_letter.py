import pytest


@pytest.fixture
def lease_termination_letter_generator(page):
    page.clock.set_fixed_time("2026-02-22T10:00:00")
    page.goto("/tests/tools/lease-termination-letter")
    return page.get_by_role("group", name="Lease termination letter generator")


def test_snapshot(page, lease_termination_letter_generator, test_screenshot):
    tool = lease_termination_letter_generator
    test_screenshot(page, tool)
    tool.get_by_role("button", name="Customize").click()

    tool.get_by_label("Apartment address").fill("Pasewalker Str. 65\n13127 Berlin")
    tool.get_by_label("Your full name").fill("John Smith")

    tool.get_by_label("Company name").fill("Hausverwaltung Geiz")
    tool.get_by_label("Address", exact=True).fill("Vermieter Str. 333\n10115 Berlin")

    tool.get_by_label("Ask for your deposit back").check()
    tool.get_by_label("Bank account holder").fill("John Bartholomy Smith")
    tool.get_by_label("IBAN").fill("DE75512108001245126199")

    tool.get_by_role("button", name="Preview").click()
    test_screenshot(page, tool)
