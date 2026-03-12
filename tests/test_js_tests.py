from playwright.sync_api import sync_playwright
import pytest

# Run the frontend unit tests, then generate a list of pytest cases out of them,
# so that successes and failures are displayed as individual tests.


mocha_test_results = None


def get_mocha_test_results(base_url):
    global mocha_test_results
    if not mocha_test_results:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(ignore_https_errors=True)
            page.goto(f"{base_url}/tests/unit")
            page.wait_for_function("() => window.testResults !== undefined", timeout=5000)
            mocha_test_results = page.evaluate("window.testResults")
            browser.close()
    return mocha_test_results


def pytest_generate_tests(metafunc):
    global mocha_test_results
    if "client_side_cases" in metafunc.fixturenames:
        get_mocha_test_results(metafunc.config.getoption("base_url"))
        metafunc.parametrize(
            "client_side_cases",
            mocha_test_results,
            ids=[r["name"] for r in mocha_test_results],
        )


def test_mocha_case(client_side_cases):
    """One pytest test per mocha test case."""
    if client_side_cases["status"] == "failed":
        pytest.fail(client_side_cases.get("error", "Test failed"))
