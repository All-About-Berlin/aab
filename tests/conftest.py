from pathlib import Path
import pytest
import shutil


devices = {
    "mobile": {  # iPhone 13 Mini
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 375, "height": 629},
        "has_touch": True,
    },
    "tablet": {  # iPad Mini
        "user_agent": "Mozilla/5.0 (iPad; iPad14,2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Firefox/120.0 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 744, "height": 1133},
        "has_touch": True,
    },
    "desktop": {  # Desktop
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 15.6; rv:142.0) Gecko/20100101 Firefox/142.0",
        "viewport": {"width": 1280, "height": 800},
        "has_touch": False,
    },
}


@pytest.fixture(autouse=True)
def set_default_timeout(page):
    """
    Enforce 2-second default timeout on all Playwright tests
    """
    page.set_default_timeout(2000)


@pytest.fixture
def browser_context_args(request, browser_context_args):
    """
    Override Playwright's default browser_context_args
    """

    # Allow pytest.mark.device("mobile")
    device_id = "desktop"
    if device_marker := request.node.get_closest_marker("device"):
        device_id = device_marker.args[0]

    return {
        **browser_context_args,
        **devices[device_id],
        "reduced_motion": "reduce",  # Disable smooth scrolling
        "timezone_id": "Europe/Berlin",
        "locale": "fr-CA",
        "ignore_https_errors": True,
    }


@pytest.fixture(
    params=[
        pytest.param("mobile", marks=pytest.mark.device("mobile")),
        pytest.param("tablet", marks=pytest.mark.device("tablet")),
        pytest.param("desktop", marks=pytest.mark.device("desktop")),
    ],
)
def test_screenshot(request, page, assert_snapshot):
    """
    Adds a test_screenshot function that does snapshot testing on multiple devices
    """

    def test(page, element_to_screenshot, remove_focus=True, move_mouse=True):
        # Blur any focused elements to fix flakiness
        if remove_focus:
            page.evaluate("document.activeElement.blur()")
        # Move mouse away to avoid hover flakiness
        if move_mouse:
            page.mouse.move(0, 0)
        assert_snapshot(element_to_screenshot.screenshot())

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
