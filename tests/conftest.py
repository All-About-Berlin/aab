from pathlib import Path
import pytest
import shutil
import sys


viewports = {
    "mobile": {"width": 375, "height": 629},  # iPhone 13 Mini
    "tablet": {"width": 744, "height": 1133},  # iPad Mini
    "desktop": {"width": 1280, "height": 800},
}


@pytest.fixture(autouse=True)
def set_default_timeout(page):
    """
    Enforce 2-second default timeout on all Playwright tests
    """
    page.set_default_timeout(2000)


@pytest.fixture(autouse=True)
def mock_exchange_rates(page):
    """
    Mock the currency conversion API to make tests work offline.
    The external API call is also quite slow and makes the currency conversion tooltips flaky in snapshot testing.
    """
    page.route(
        "**/api/exchangerates.json",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"rates":{"EUR":1,"USD":1.08,"GBP":0.86,"INR":90.5,"CAD":1.47,"CHF":0.97,"JPY":162.5,"AUD":1.65,"SEK":11.2,"PLN":4.32}}',
        ),
    )


@pytest.fixture
def browser_context_args(browser_context_args):
    """
    Override Playwright's default browser_context_args
    """
    return {
        **browser_context_args,
        "viewport": viewports["desktop"],
        "reduced_motion": "reduce",  # Disable smooth scrolling
        "timezone_id": "Europe/Berlin",
        "locale": "fr-CA",
        "ignore_https_errors": True,
    }


@pytest.fixture
def test_screenshot(request, page, assert_snapshot, browser_name):
    call_counter = [0]

    def test(page, element_to_screenshot, remove_focus=True, move_mouse=True, multiple_screen_sizes=False):
        # Blur any focused elements to fix flakiness
        if remove_focus:
            page.evaluate("document.activeElement.blur()")
        # Move mouse away to avoid hover flakiness
        if move_mouse:
            page.mouse.move(0, 0)

        # Adds number to file name when called multiple times in the same test
        call_count_suffix = "" if call_counter[0] == 0 else f"_{call_counter[0]}"
        call_counter[0] += 1

        node_id = request.node.name
        mask = [page.locator("p:has-text('You are updating the feedback')")]

        device_ids = viewports if multiple_screen_sizes else ["desktop"]

        for device_id in device_ids:
            page.set_viewport_size(viewports[device_id])
            name_id = node_id.replace(f"[{browser_name}", f"[{device_id}-{browser_name}")
            file_name = f"{name_id}[{sys.platform}]{call_count_suffix}.png"
            img = element_to_screenshot.screenshot(mask=mask)
            assert_snapshot(img, name=file_name)

        # Leave the page at the default viewport for any code that runs after.
        page.set_viewport_size(viewports["desktop"])

    return test


def pytest_configure(config):
    tests_root = Path(__file__).parent.resolve()
    snapshots_dir = tests_root / "snapshots"
    snapshot_failures_dir = tests_root / "snapshot-failures"

    if snapshot_failures_dir.exists():
        shutil.rmtree(snapshot_failures_dir)

    # Print errors as they happen, not at the end
    config.option.instafail = True

    # Hard-coded base URL
    config.option.base_url = "http://localhost"

    config.option.playwright_visual_snapshot_threshold = 0.2
    config.option.playwright_visual_snapshots_path = snapshots_dir
    config.option.playwright_visual_snapshot_failures_path = snapshot_failures_dir
    config.option.playwright_visual_ignore_size_diff = True
