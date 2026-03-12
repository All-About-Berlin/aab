from tests.test_data import people


def next_step(page):
    page.get_by_role("button", name="Continue").click()


def previous_step(page):
    page.get_by_role("button", name="Go back").click()


def load_abmeldung_form(page):
    page.goto("/tests/tools/abmeldung-form-filler")


def start_abmeldung(page):
    page.get_by_role("button", name="Start").click()


def fill_new_address(page):
    address = people[0]["foreign_address"]
    page.get_by_label("Street address").fill(address["street"])
    page.get_by_label("City and post code").fill(address["city"])
    page.get_by_label("Country").select_option(address["country"])


def fill_old_address(page):
    address = people[0]["local_address"]
    page.get_by_label("Street address").fill(address["street"])
    page.get_by_label("Post code").fill(address["post_code"])
    page.get_by_label("Building details").fill(address["zusatz"])
    page.get_by_label("Move-out date").fill(people[0]["move_out_date"])


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


def fill_people(page, multiple_people=False):
    fill_person(page)
    if multiple_people:
        for index in range(1, 5):
            add_person(page)
            fill_person(page, index)


def fill_abmeldung_form_until(page, step=None, multiple_people=False):
    load_abmeldung_form(page)
    start_abmeldung(page)

    if step == "oldAddress":
        return

    fill_old_address(page)
    next_step(page)

    if step == "newAddress":
        return

    fill_new_address(page)
    next_step(page)

    if step == "addPeople":
        return

    fill_people(page, multiple_people)

    page.get_by_role("button", name="Finish").click()
