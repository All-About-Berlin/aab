import pytest
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@pytest.mark.parametrize(
    "path, expected_location",
    [
        ("/services", "https://services.localhost/"),
        ("/services/", "https://services.localhost/"),
        ("/services/health-insurance", "https://services.localhost/health-insurance"),
        ("/services/health-insurance/calculator", "https://services.localhost/health-insurance/calculator"),
    ],
)
def test_services_redirect(path, expected_location, base_url):
    response = requests.get(base_url.replace("http://", "https://") + path, allow_redirects=False, verify=False)
    assert response.status_code == 301
    assert response.headers["Location"] == expected_location


@pytest.mark.parametrize(
    "path",
    [
        "/health-insurance",
        "/contact",
    ],
)
def test_services_pages(path):
    response = requests.get("https://services.localhost" + path, verify=False)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "path, expected_location",
    [
        ("/", ""),
        ("/guides/", "/guides"),
        ("/guides/anmeldung/", "/guides/anmeldung"),
        ("/health-insurance/", "/health-insurance"),
        ("/out/anmeldung-online/", "/out/anmeldung-online"),
        ("/forum/", "/forum"),
        ("/forum/rules/", "/forum/rules"),
        ("/forum/login/", "/forum/login"),
        ("/forum/1/", "/forum/1"),
        ("/forum/1/page-2/", "/forum/1/page-2"),
    ],
)
def test_trailing_slash_redirect(path, expected_location, base_url):
    response = requests.get(base_url.replace("http://", "https://") + path, allow_redirects=False, verify=False)
    assert response.status_code == 301
    assert response.headers["Location"] == expected_location
