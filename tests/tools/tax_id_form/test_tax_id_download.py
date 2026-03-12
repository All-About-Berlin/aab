from tests.test_data import people
from . import fill_tax_id_form_until, get_form


def test_download_buttons_no_anmeldung(page, test_screenshot, tmp_path):
    fill_tax_id_form_until(
        page, "options", multiple_people=True, purpose="I can't register my address, but I need a tax ID"
    )

    for index in range(0, 5):
        download_button = page.get_by_role(
            "button", name=f"Download the application form for {people[index]['first_name']}"
        )
        with page.expect_download() as download_info:
            download_button.click()
            download = download_info.value
            assert download.suggested_filename == "tax-id-form-filled.pdf"
            download.save_as(tmp_path / f"tax-id-{index}.pdf")

    test_screenshot(page, get_form(page))


def test_download_buttons_living_abroad(page, tmp_path):
    fill_tax_id_form_until(
        page, "options", multiple_people=True, purpose="I don't live in Germany, but I need a tax ID"
    )

    for index in range(0, 5):
        download_button = page.get_by_role(
            "button", name=f"Download the application form for {people[index]['first_name']}"
        )
        with page.expect_download() as download_info:
            download_button.click()
            download = download_info.value
            assert download.suggested_filename == "tax-id-form-filled.pdf"
            download.save_as(tmp_path / f"tax-id-{index}.pdf")
