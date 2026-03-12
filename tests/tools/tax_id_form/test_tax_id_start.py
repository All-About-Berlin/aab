from . import fill_tax_id_form_until, get_form


def test_start(page, test_screenshot):
    fill_tax_id_form_until(page, "start")
    test_screenshot(page, get_form(page))
