from utils import fill_abmeldung_form_until


def test_base_flow(page):
    fill_abmeldung_form_until(page)
