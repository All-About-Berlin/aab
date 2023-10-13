from pathlib import Path


def next_step(page):
    page.get_by_role("button", name="Continue").click()


def previous_step(page):
    page.get_by_role("button", name="Go back").click()


def load_abmeldung_form(page):
    page.goto("/tools/calculator")


def choose_online_abmeldung(page):
    page.get_by_role("button", name="Do your Abmeldung online").click()
    page.get_by_role("button", name="Start").click()


def fill_old_address(page):
    page.get_by_label("Street address").fill("Pasewalker Str. 65")
    page.get_by_label("Post code").fill("13127")
    page.get_by_label("Building details").fill("Haus B, 2. Etage rechts")

    page.get_by_title("Day of the month").fill("10")
    page.get_by_title("Month", exact=True).fill("10")
    page.get_by_title("Year").fill("2023")


def fill_new_address(page):
    page.get_by_label("Street address").fill("123 des Érables")
    page.get_by_label("City and post code").fill("Montreal, Quebec, J2J 2W5")
    page.get_by_label("Country").select_option("Canada")


def add_person(page):
    page.get_by_role("button", name="Add another person").click()


def fill_person(page, index=0):
    page.get_by_title("First name").nth(index).fill("Nicolas")
    page.get_by_title("Last name").nth(index).fill("Bouliane")

    # Note: this link disappears after clicking, so we can't select by index
    page.get_by_role("link", name="Add a title or birth name").nth(0).click()
    page.get_by_label("Title").nth(index).fill("Dr.")
    page.get_by_label("Name at birth").nth(index).fill("Nicole Bouliane")

    page.get_by_text("Male", exact=True).nth(index).click()

    page.get_by_label("Nationality").nth(index).fill("Canada")
    page.get_by_label("Religion").nth(index).select_option("Sonstiges, nicht kirchensteuerpflichtig")

    page.get_by_title("Day of the month").nth(index).fill("10")
    page.get_by_title("Month", exact=True).nth(index).fill("10")
    page.get_by_title("Year").nth(index).fill("1990")

    page.get_by_label("Place of birth").nth(index).fill("Chicoutimi, Quebec, Canada")


def fill_documents(page):
    add_documents(page, [
        Path(__file__).parent / "test-document.pdf",
        Path(__file__).parent / "test-document.png",
        Path(__file__).parent / "test-document.jpg",
    ])


def add_documents(page, documents):
    with page.expect_file_chooser() as fc_info:
        page.click('button:is(:text("Add documents"), :text("Add more documents"))')
        file_chooser = fc_info.value
        file_chooser.set_files(documents)


def fill_permission(page):
    page.get_by_label("I allow All About Berlin to deregister my address at the Bürgeramt.").check()
    page.locator("canvas").click(position={"x": 552, "y": 147})
    page.get_by_label("Email").fill("contact@allaboutberlin.com")


def fill_abmeldung_form_until(page, step=None):
    load_abmeldung_form(page)
    choose_online_abmeldung(page)

    if step == 'oldAddress':
        return

    fill_old_address(page)
    next_step(page)

    if step == 'newAddress':
        return

    fill_new_address(page)
    next_step(page)

    if step == 'addPeople':
        return

    fill_person(page)
    next_step(page)

    if step == 'documents':
        return

    fill_documents(page)
    next_step(page)

    if step == 'permission':
        return

    fill_permission(page)
    page.get_by_role("button", name="Finish").click()
