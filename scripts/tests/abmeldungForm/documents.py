from pathlib import Path
from playwright.sync_api import expect
from utils import fill_abmeldung_form_until, add_documents, fill_documents, next_step, previous_step


def test_data_remembered(page):
    fill_abmeldung_form_until(page, 'documents')
    fill_documents(page)
    next_step(page)
    previous_step(page)
    expect(page.get_by_text('test-document.jpg')).to_have_count(1)
    expect(page.get_by_text('test-document.pdf')).to_have_count(1)
    expect(page.get_by_text('test-document.png')).to_have_count(1)


def test_reupload_same_file(page):
    fill_abmeldung_form_until(page, 'documents')

    add_documents(page, [
        Path(__file__).parent / "test-document.pdf",
        Path(__file__).parent / "test-document.png",
    ])
    expect(page.get_by_text('test-document.jpg')).to_have_count(0)
    expect(page.get_by_text('test-document.pdf')).to_have_count(1)
    expect(page.get_by_text('test-document.png')).to_have_count(1)

    add_documents(page, [
        Path(__file__).parent / "test-document.jpg",
        Path(__file__).parent / "test-document.png",
    ])
    expect(page.get_by_text('test-document.jpg')).to_have_count(1)
    expect(page.get_by_text('test-document.pdf')).to_have_count(1)
    expect(page.get_by_text('test-document.png')).to_have_count(1)
