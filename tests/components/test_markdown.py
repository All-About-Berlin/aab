def test_markdown_elements(page, test_screenshot):
    page.goto("/tests/markdown")
    content = page.locator("main > article")
    test_screenshot(page, content)


def test_services_links_rewritten(page):
    page.goto("/tests/markdown")
    article = page.locator("main article")
    assert (
        article.get_by_role("link", name="A link to /services", exact=True).get_attribute("href")
        == "https://services.localhost"
    )
    assert (
        article.get_by_role("link", name="A link to /services/health-insurance", exact=True).get_attribute("href")
        == "https://services.localhost/health-insurance"
    )
    assert (
        article.get_by_role("link", name="A link to /guides/abmeldung", exact=True).get_attribute("href")
        == "https://localhost/guides/abmeldung#who-must-deregister"
    )
