from playwright.sync_api import expect
from tests.test_data import people, companies


def get_form(page):
    return page.get_by_role("group", name="Tax ID request form")


def next_step(page):
    page.get_by_role("button", name="Continue").click()


def previous_step(page):
    page.get_by_role("button", name="Go back").click()


def load_tax_id_form(page):
    page.goto("/tests/tools/tax-id-request-form-filler")


def start_form(page):
    page.get_by_role("button", name="Start").click()


def fill_purpose(page, purpose):
    page.get_by_text(purpose, exact=True).set_checked(True)


def fill_address(page, purpose):
    if purpose == "I can't register my address, but I need a tax ID":
        address = people[0]["local_address"]
        page.get_by_label("Street address").fill(address["street"])
        page.get_by_placeholder("12345").fill(address["post_code"])
        page.get_by_placeholder("Berlin", exact=True).fill(address["city"])
        page.get_by_label("State").select_option(address["state"][0])
    elif purpose == "I don't live in Germany, but I need a tax ID":
        address = people[0]["foreign_address"]
        page.get_by_label("Country").select_option(address["country"])
        page.get_by_label("Street address").fill(address["street"])
        page.get_by_label("City and post code").fill(" ".join([address["city"], address["post_code"]]))


def add_person(page):
    page.get_by_role("button", name="Add another person").click()


def fill_person(page, index=0):
    person = people[index]

    page.get_by_title("First name").nth(index).fill(person["first_name"])
    page.get_by_title("Last name").nth(index).fill(person["last_name"])

    # Note: this link disappears after clicking, so we can't select by index
    page.get_by_role("link", name="Add a title or birth name").nth(0).click()
    page.get_by_label("Name at birth").nth(index).fill(person["birth_name"])
    page.get_by_label("Date of birth").nth(index).fill(person["birth_date"])
    page.get_by_label("Place of birth").nth(index).fill(person["birth_place"])


def fill_people(page, multiple_people=False):
    fill_person(page)
    if multiple_people:
        for index in range(1, 5):
            add_person(page)
            fill_person(page, index)


def fill_bei_address(page, multiple_people=False):
    if multiple_people:
        control = page.get_by_label("Our names are on our mailbox")
    else:
        control = page.get_by_label("My name is on my mailbox")

    expect(control).to_be_checked()
    control.set_checked(False)
    page.get_by_label("Name on mailbox").fill("Müller")


def fill_documents(page, multiple_people=False):
    for index in range(0, 5 if multiple_people else 1):
        doc = people[index]["id_document"]
        page.get_by_label(doc["type"][0], exact=True).nth(index).set_checked(True)

        # Passport/ID card number. The name changes with the document type
        page.get_by_label("number").nth(index).fill(doc["number"])
        page.get_by_label("Date issued").nth(index).fill(doc["issue_date"])
        page.get_by_label("Issuing authority").nth(index).fill(doc["authority"])
        page.get_by_label("Expiration date").nth(index).fill(doc["expiration_date"])


def fill_employer(page, send_to_employer=False):
    page.get_by_label("Send the tax ID to my employer").set_checked(send_to_employer)
    if send_to_employer:
        page.get_by_label("Employer name").fill(companies[0]["name"])
        page.get_by_label("Address").fill(companies[0]["address"])
        page.get_by_placeholder("12345").fill(companies[0]["post_code"])
        page.get_by_placeholder("Berlin", exact=True).fill(companies[0]["city"])
        page.get_by_label("State").select_option(companies[0]["state"][0])


def fill_feedback(page):
    page.get_by_label("Email").fill("test@emailaddress.com")


def fill_tax_id_form_until(
    page,
    step=None,
    multiple_people=False,
    purpose="I can't register my address, but I need a tax ID",
    send_to_employer=False,
):
    load_tax_id_form(page)

    if step == "start":
        return

    start_form(page)

    if step == "purpose":
        return

    fill_purpose(page, purpose)
    next_step(page)

    if step == "address":
        return

    fill_address(page, purpose)
    next_step(page)

    if step == "addPeople":
        return

    fill_people(page, multiple_people)
    next_step(page)

    if step == "beiAddress":
        return

    # This step is skipped if someone lives outside of Germany
    if purpose == "I can't register my address, but I need a tax ID":
        fill_bei_address(page, multiple_people)
        next_step(page)

    if step == "employer":
        return

    fill_employer(page, send_to_employer)
    next_step(page)

    if step == "feedback":
        return

    fill_feedback(page)

    page.get_by_role("button", name="Finish").click()
