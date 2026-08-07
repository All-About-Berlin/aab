from playwright.sync_api import expect
from tests.test_data import people


def next_step(page):
    page.get_by_role("button", name="Continue").click()


def previous_step(page):
    page.get_by_role("button", name="Go back").click()


def load_anmeldung_form(page):
    page.goto("/tests/tools/anmeldung-form-filler")


def start_anmeldung(page):
    page.get_by_role("button", name="Start").click()


def fill_new_address(page):
    address = people[0]["local_address"]
    page.get_by_label("Street address").fill(address["street"])
    page.get_by_label("Post code").fill(address["post_code"])
    page.get_by_label("Building details").fill(address["zusatz"])
    page.get_by_label("Move-in date").fill(people[0]["move_out_date"])


def fill_old_address(page):
    address = people[0]["local_address_2"]
    page.get_by_label("Country").select_option(address["country"])
    page.get_by_label("Street address").fill(address["street"])
    page.get_by_placeholder("12345").fill(address["post_code"])
    page.get_by_placeholder("Berlin").fill(address["city"])
    page.get_by_label("Building details").fill(address["zusatz"])
    page.get_by_label("State").select_option(address["state"][0])


def add_person(page):
    page.get_by_role("button", name="Add another person").click()


def fill_person(page, index=0):
    person = people[index]

    # Note: this link disappears after clicking, so we can't select by index
    page.get_by_title("First name").nth(index).fill(person["first_name"])
    page.get_by_title("Last name").nth(index).fill(person["last_name"])

    page.get_by_role("link", name="Add a title or birth name").nth(0).click()
    page.get_by_label("Title").nth(index).fill(person["title"])
    page.get_by_label("Name at birth").nth(index).fill(person["birth_name"])

    page.get_by_text(person["gender"], exact=True).nth(index).set_checked(True)

    page.get_by_label("Place of birth").nth(index).fill(person["birth_place"])
    page.get_by_label("Nationality").nth(index).select_option(person["nationality"])
    page.get_by_label("Religion").nth(index).select_option(person["religion"][0])

    page.get_by_label("Date of birth").nth(index).fill(person["birth_date"])

    if person["is_family_member"]:
        primary_name = people[0]["first_name"]
        family_label = f"{person['first_name']} is {primary_name}'s parent, child or spouse"
        page.get_by_label(family_label).check()


def fill_people(page, people_count=len(people)):
    fill_person(page)
    for index in range(1, people_count):
        add_person(page)
        fill_person(page, index)


def fill_bei_address(page, people_count=1):
    if people_count > 1:
        control = page.get_by_label("Our names are on our mailbox")
    else:
        control = page.get_by_label("My name is on my mailbox")

    expect(control).to_be_checked()
    control.set_checked(False)
    page.get_by_label("Name on mailbox").fill("Müller")


def fill_documents(page, people_count=len(people)):
    for index in range(0, people_count):
        doc = people[index]["id_document"]
        page.get_by_label(doc["type"][0], exact=True).nth(index).evaluate("el => el.checked = true")

        # Passport/ID card number. The name changes with the document type
        page.get_by_label("number").nth(index).fill(doc["number"])
        page.get_by_label("Date issued").nth(index).fill(doc["issue_date"])
        page.get_by_label("Issuing authority").nth(index).fill(doc["authority"])
        page.get_by_label("Expiration date").nth(index).fill(doc["expiration_date"])


def fill_anmeldung_form_until(page, step=None, people_count=3):
    load_anmeldung_form(page)
    start_anmeldung(page)

    if step == "newAddress":
        return

    fill_new_address(page)
    next_step(page)

    if step == "oldAddress":
        return

    fill_old_address(page)
    next_step(page)

    if step == "addPeople":
        return

    fill_people(page, people_count)
    next_step(page)

    if step == "beiAddress":
        return

    fill_bei_address(page, people_count)
    next_step(page)

    if step == "idDocuments":
        return

    fill_documents(page, people_count)
    page.get_by_role("button", name="Finish").click()
