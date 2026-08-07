from playwright.sync_api import expect
from tests.test_data import people
from . import fill_abmeldung_form_until


def test_download_buttons(page, test_screenshot, tmp_path):
    fill_abmeldung_form_until(page, "options", people_count=len(people))

    part_1 = page.get_by_role("button", name="Download the form for José, Renata, and Priya")  # First 3 family members
    part_2 = page.get_by_role("button", name="Download the form for Tomás")  # Family member #4
    part_3 = page.get_by_role("button", name="Download the form for Márk")  # Not a family member
    part_4 = page.get_by_role("button", name="Download the form for Sofia")  # Not a family member
    part_5 = page.get_by_role("button", name="Download the form for Élodie")  # Not a family member

    for button in (part_1, part_2, part_3, part_4, part_5):
        expect(button).not_to_be_disabled()

    with page.expect_download() as download_info:
        part_1.click()

    download = download_info.value
    assert download.suggested_filename == "abmeldung-form-filled.pdf"
    download.save_as(tmp_path / "abmeldung-1.pdf")

    with page.expect_download() as download_info:
        part_5.click()
    download = download_info.value
    assert download.suggested_filename == "abmeldung-form-filled.pdf"
    download.save_as(tmp_path / "abmeldung-5.pdf")

    form = page.get_by_role("group", name="Abmeldung form filler")
    test_screenshot(page, form)
