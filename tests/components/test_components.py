import pytest


@pytest.mark.parametrize(
    "component",
    [
        "collapsible",
        "eur",
        "glossary",
        "inputs",
        "recommended",
        "tabs",
    ],
)
def test_component_snapshot(page, test_screenshot, component):
    page.goto(f"/tests/components/{component}")
    content = page.locator("main > article")
    test_screenshot(page, content)


def test_glossary_click(page, test_screenshot):
    page.goto("/tests/components/glossary")
    page.locator("main > article a").first.click()

    dialog = page.locator("dialog").first
    assert dialog.evaluate("dialog => dialog.open")
    test_screenshot(page, dialog)

    dialog.locator(".close-button").click()
    assert not dialog.evaluate("dialog => dialog.open")


def test_recommended_click(page, test_screenshot):
    page.goto("/tests/components/recommended")
    link = page.locator("main > article a.recommended").first

    # Test hover state
    link.hover()
    test_screenshot(page, page.locator("main > article"), move_mouse=False)

    # Test click
    link.click()
    assert page.locator("dialog").first.evaluate("dialog => dialog.open")
