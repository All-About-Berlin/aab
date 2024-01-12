from playwright.sync_api import expect
from ..test_data import people


def next_step(page):
    page.get_by_role("button", name="Continue").click()


def previous_step(page):
    page.get_by_role("button", name="Go back").click()


def load_anmeldung_form(page):
    page.goto("/docs/anmeldung")


def start_anmeldung(page):
    page.get_by_role("button", name="Start").click()


def fill_new_address(page):
    address = people[0]['local_address']
    page.get_by_label("Street address").fill(address['street'])
    page.get_by_label("Post code").fill(address['post_code'])
    page.get_by_label("Building details").fill(address['zusatz'])

    year, month, day = people[0]['move_out_date']
    page.get_by_title("Day of the month").fill(day)
    page.get_by_title("Month", exact=True).fill(month)
    page.get_by_title("Year").fill(year)


def fill_old_address(page):
    address = people[0]['local_address_2']
    page.get_by_label("Country").select_option(address['country'])
    page.get_by_label("Street address").fill(address['street'])
    page.get_by_placeholder("12345").fill(address['post_code'])
    page.get_by_placeholder("Berlin").fill(address['city'])
    page.get_by_label("Building details").fill(address['zusatz'])
    page.get_by_label("State").select_option(address['state'][0])


def add_person(page):
    page.get_by_role("button", name="Add another person").click()


def fill_person(page, index=0):
    person = people[index]

    # Note: this link disappears after clicking, so we can't select by index
    page.get_by_title("First name").nth(index).fill(person['first_name'])
    page.get_by_title("Last name").nth(index).fill(person['last_name'])

    page.get_by_role("link", name="Add a title or birth name").nth(0).click()
    page.get_by_label("Title").nth(index).fill(person['title'])
    page.get_by_label("Name at birth").nth(index).fill(person['birth_name'])

    page.get_by_text(person['gender'], exact=True).nth(index).set_checked(True)

    page.get_by_label("Place of birth").nth(index).fill(person['birth_place'])
    page.get_by_label("Nationality").nth(index).fill(person['nationality'])
    page.get_by_label("Religion").nth(index).select_option(person['religion'][0])

    year, month, day = person['birth_date']
    page.get_by_title("Day of the month").nth(index).fill(day)
    page.get_by_title("Month", exact=True).nth(index).fill(month)
    page.get_by_title("Year").nth(index).fill(year)


def fill_people(page, multiple_people=False):
    fill_person(page)
    if multiple_people:
        for index in range(1, 5):
            add_person(page)
            fill_person(page, index)


def fill_bei_address(page, multiple_people=False):
    if multiple_people:
        control = page.get_by_label('Our names are on our mailbox')
    else:
        control = page.get_by_label('My name is on my mailbox')

    expect(control).to_be_checked()
    control.set_checked(False)
    page.get_by_label('Name on mailbox').fill("Müller")


def fill_documents(page, multiple_people=False):
    for index in range(0, 5 if multiple_people else 1):
        doc = people[index]['id_document']
        page.get_by_label(doc['type'][0], exact=True).nth(index).set_checked(True)

        # Passport/ID card number. The name changes with the document type
        page.get_by_label('number').nth(index).fill(doc['number'])

        year, month, day = doc['issue_date']
        page.get_by_title("Day of the month").nth(index * 2).fill(day)
        page.get_by_title("Month", exact=True).nth(index * 2).fill(month)
        page.get_by_title("Year").nth(index * 2).fill(year)

        page.get_by_label('Issuing authority').nth(index).fill(doc['authority'])

        year, month, day = doc['expiration_date']
        page.get_by_title("Day of the month").nth(index * 2 + 1).fill(day)
        page.get_by_title("Month", exact=True).nth(index * 2 + 1).fill(month)
        page.get_by_title("Year").nth(index * 2 + 1).fill(year)


def fill_anmeldung_form_until(page, step=None, multiple_people=False):
    load_anmeldung_form(page)
    start_anmeldung(page)

    if step == 'newAddress':
        return

    fill_new_address(page)
    next_step(page)

    if step == 'oldAddress':
        return

    fill_old_address(page)
    next_step(page)

    if step == 'addPeople':
        return

    fill_people(page, multiple_people)
    next_step(page)

    if step == 'beiAddress':
        return

    fill_bei_address(page, multiple_people)
    next_step(page)

    if step == 'idDocuments':
        return

    fill_documents(page, multiple_people)
    page.get_by_role("button", name="Finish").click()
