from playwright.sync_api import expect
from tests.test_data import people
from . import fill_abmeldung_form_until


def test_download_buttons(page, test_screenshot, tmp_path):
    fill_abmeldung_form_until(page, "options", multiple_people=True)

    download_1 = page.get_by_role("button", name="Download part 1 of the form")
    expect(download_1).to_contain_text(people[0]["first_name"])
    expect(download_1).to_contain_text(people[1]["first_name"])
    expect(download_1).to_contain_text(people[2]["first_name"])

    download_2 = page.get_by_role("button", name="Download part 2 of the form")
    expect(download_2).to_contain_text(people[3]["first_name"])
    expect(download_2).to_contain_text(people[4]["first_name"])

    with page.expect_download() as download_info:
        download_1.click()
        expect(download_1).to_be_disabled()
        download = download_info.value
        assert download.suggested_filename == "abmeldung-form-filled.pdf"
        download.save_as(tmp_path / "abmeldung-1.pdf")

    with page.expect_download() as download_info:
        download_2.click()
        expect(download_2).to_be_disabled()
        download = download_info.value
        assert download.suggested_filename == "abmeldung-form-filled.pdf"
        download.save_as(tmp_path / "abmeldung-2.pdf")

    expect(download_1).not_to_be_disabled()
    expect(download_2).not_to_be_disabled()

    form = page.get_by_role("group", name="Tool to fill the Abmeldung form")
    test_screenshot(page, form)
