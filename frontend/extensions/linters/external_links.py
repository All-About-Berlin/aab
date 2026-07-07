from datetime import date, timedelta
from pathlib import Path
from typing import Iterable
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from urllib.parse import urlparse, urlunparse
from ursus.config import config
from ursus.linters.markdown import MarkdownExternalLinksLinter
import logging
import requests
import yaml


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)


def strip_url_fragment(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(fragment=""))


def verify_with_requests(url: str) -> str | None:
    """
    Returns the redirect target URL if the URL redirects, or None on clean success.
    Raises _ConnectionError if no HTTP response was received.
    Raises _HttpError if an HTTP error response was received.
    """
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": USER_AGENT}, allow_redirects=True)
    except Exception as e:
        return type(e).__name__ + f" {str(e)}"

    if response.status_code >= 400:
        return f"HTTP {response.status_code}"


def verify_with_playwright(url: str) -> str | None:
    """Returns an error status string, or None if the URL loads successfully."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            Stealth().apply_stealth_sync(page)
            response = page.goto(url, timeout=10000, wait_until="domcontentloaded")
            if response is None:
                return "ERR_EMPTY_RESPONSE"
            if not response.ok:
                return f"HTTP {response.status}"
        except Exception as e:
            return type(e).__name__
        except:
            pass  # Catch "page.goto: Download is starting"
        finally:
            browser.close()


class ExternalLinksLinter(MarkdownExternalLinksLinter):
    """
    Verifies external links in Markdown content at regular intervals.
    Results are cached in verified-urls.yml and failing-urls.yml.
    """

    verified_urls_file = config.content_path / "verified-urls.yml"
    failing_urls_file = config.content_path / "failing-urls.yml"

    verification_interval = timedelta(days=180)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.verified_urls: dict[str, date] = {}
        if self.verified_urls_file.exists():
            self.verified_urls = yaml.safe_load(self.verified_urls_file.read_text()) or {}  # type: ignore[override]

        self.failing_urls: dict[str, dict] = {}
        if self.failing_urls_file.exists():
            failures: Iterable = yaml.safe_load(self.failing_urls_file.read_text()) or []
            self.failing_urls = {f["url"]: {"status": f["status"], "date": f["date"]} for f in failures}

        self.just_verified_urls: set[str] = set()
        self._redirect_notices: dict[str, str] = {}

    def validate_link_url(self, url: str, is_image: bool, file_path: Path):
        if not url.startswith(("http://", "https://")):
            yield from super().validate_link_url(url, is_image, file_path)
            return

        clean_url = strip_url_fragment(self.unescape_url(url))

        failure_status = self.failing_urls.get(clean_url, {}).get("status")
        is_permanent_failure = failure_status in (
            "HTTP 400",
            "HTTP 404",
            "HTTP 405",
            "HTTP 410",
        )
        if is_permanent_failure:
            yield f"{self.failing_urls[clean_url]['status']} (cached)", logging.ERROR
        elif clean_url not in self.just_verified_urls:
            last_verified = self.verified_urls.get(clean_url)

            failure_status = self.failing_urls.get(clean_url, {}).get("status")

            should_verify_again = (
                # Never verified
                not last_verified
                # Due to re-verify
                or date.today() - last_verified >= self.verification_interval
                # Not a permanent failure
                and not is_permanent_failure
            )

            if should_verify_again:
                self.just_verified_urls.add(clean_url)
                try:
                    self.verify_page_loads(clean_url)
                except Exception as e:
                    yield f"URL error: {e}", logging.ERROR
            elif is_permanent_failure:
                yield f"URL error: {failure_status} (skipping re-verification)", logging.ERROR

    def add_verified_url(self, url: str):
        self.verified_urls[url] = date.today()
        self.failing_urls.pop(url, None)
        self.update_url_files()

    def add_failing_url(self, url: str, error: str):
        self.verified_urls.pop(url, None)
        self.failing_urls[url] = {"status": error, "date": date.today()}
        self.update_url_files()

    def update_url_files(self):
        self.verified_urls_file.write_text(
            str(yaml.dump(dict(sorted(self.verified_urls.items())), allow_unicode=True, sort_keys=False) or "")
        )
        self.failing_urls_file.write_text(
            str(
                yaml.dump(
                    [
                        {"url": url, "status": info["status"], "date": info["date"]}
                        for url, info in sorted(self.failing_urls.items())
                    ],
                    allow_unicode=True,
                    sort_keys=False,
                )
                or ""
            )
        )

    def verify_page_loads(self, url: str) -> None:
        error = verify_with_requests(url)
        if error and "404" not in error:
            error = verify_with_playwright(url)

        if error:
            self.add_failing_url(url, error)
        else:
            logging.info(f"Verified {url}")
            self.add_verified_url(url)
