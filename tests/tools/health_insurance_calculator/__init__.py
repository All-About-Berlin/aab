occupations = [
    "azubi",
    "employee",
    "selfEmployed",
    "studentUnemployed",
    "unemployed",
    # "other",
]

cases = {
    "selfEmployed-20k": {
        "income": 20000,
        "occupation": "selfEmployed",
        "age": 30,
        "is_married": True,
        "children_count": 3,
        "is_applying_for_first_visa": True,
        "has_eu_public_insurance": True,
        "has_german_public_insurance": True,
        "can_have_private": False,
    },
    "selfEmployed-100k": {
        "income": 100000,
        "occupation": "selfEmployed",
        "age": 40,
        "is_married": False,
        "children_count": 0,
        "is_applying_for_first_visa": True,
        "has_eu_public_insurance": False,
        "has_german_public_insurance": False,
        "can_have_private": True,
    },
    "employee-30k": {
        "income": 30000,
        "occupation": "employee",
        "age": 40,
        "is_married": True,
        "children_count": 1,
        "is_applying_for_first_visa": True,
        "has_eu_public_insurance": False,
        "has_german_public_insurance": False,
        "can_have_private": False,
    },
    "employee-100k": {
        "income": 100000,
        "occupation": "employee",
        "age": 40,
        "is_married": True,
        "children_count": 1,
        "is_applying_for_first_visa": True,
        "has_eu_public_insurance": False,
        "has_german_public_insurance": False,
        "can_have_private": True,
    },
    "studentUnemployed": {
        "income": 0,
        "occupation": "studentUnemployed",
        "age": 23,
        "is_married": True,
        "children_count": 0,
        "is_applying_for_first_visa": True,
        "has_eu_public_insurance": False,
        "has_german_public_insurance": True,
        "can_have_private": True,
    },
    "studentOver30": {
        "income": 0,
        "occupation": "studentUnemployed",
        "age": 30,
        "is_married": False,
        "children_count": 0,
        "is_applying_for_first_visa": True,
        "has_eu_public_insurance": False,
        "has_german_public_insurance": True,
        "can_have_private": True,
    },
    "studentEmployee": {
        "income": 10000,
        "occupation": "studentEmployee",
        "age": 23,
        "is_married": False,
        "children_count": 1,
        "is_applying_for_first_visa": True,
        "has_eu_public_insurance": False,
        "has_german_public_insurance": True,
        "can_have_private": True,
    },
    "studentSelfEmployed": {
        "income": 10000,
        "occupation": "studentSelfEmployed",
        "age": 23,
        "is_married": True,
        "children_count": 1,
        "is_applying_for_first_visa": True,
        "has_eu_public_insurance": False,
        "has_german_public_insurance": True,
        "can_have_private": True,
    },
}


def get_calculator(page):
    return page.get_by_role("group", name="Health insurance calculator")


def see_options(page):
    page.get_by_role("button", name="See options").click()


def previous_stage(page):
    page.get_by_label("Go back").click()


def load_calculator(page, preset_occupation: str | None = None):
    page.goto(
        f"/tests/tools/health-insurance-calculator-{preset_occupation}?ref=test-referrer"
        if preset_occupation
        else "/tests/tools/health-insurance-calculator?ref=test-referrer"
    )


def select_occupation(page, occupation: str):
    if occupation.startswith("student"):
        page.locator("button[data-occupation=studentUnemployed]").click()
    else:
        page.locator(f"button[data-occupation={occupation}]").click()


def fill_questions(
    page,
    occupation,
    income: int | None = None,
    age: int | None = None,
    is_married: bool | None = None,
    children_count: int | None = None,
    is_applying_for_first_visa: bool | None = None,
    has_eu_public_insurance: bool | None = None,
    has_german_public_insurance: bool | None = None,
    **kwargs,
):
    if age is not None:
        page.get_by_label("Age", exact=True).fill(str(age))

    if is_married is not None:
        if is_married:
            page.click("text=Married")
        else:
            page.click("text=Not married")

    if children_count is not None:
        page.get_by_label("Children").select_option(str(children_count))

    if is_applying_for_first_visa is not None:
        page.get_by_label("I am applying for").set_checked(is_applying_for_first_visa)

    if has_eu_public_insurance is not None:
        page.get_by_label("I have public health insurance in another EU country").set_checked(has_eu_public_insurance)

    if has_german_public_insurance is not None:
        page.get_by_label("I have public health insurance in Germany").set_checked(has_german_public_insurance)

    if income is not None:
        if occupation == "studentEmployee":
            page.get_by_label("I have a job").check()
        elif occupation == "studentSelfEmployed":
            page.get_by_label("I am self-employed").check()

        if occupation == "employee":
            page.get_by_label("Salary").fill(str(income))
        elif occupation == "studentUnemployed":
            pass  # No income
        else:
            page.get_by_label("Income").fill(str(income))


def assert_stage(page, expected_stage: str):
    stage = get_calculator(page).get_attribute("data-stage")
    assert stage == expected_stage, f"Expected stage '{expected_stage}', got '{stage}'"


def fill_calculator_until(page, stage=None, preset_occupation: bool = False, **case):
    load_calculator(page, case["occupation"] if preset_occupation else None)
    assert_stage(page, "occupation")

    if stage == "occupation":
        return

    select_occupation(page, case["occupation"])
    assert_stage(page, "questions")

    if stage == "questions":
        return

    fill_questions(page, **case)
    see_options(page)

    assert_stage(page, "options")

    if stage == "options":
        return

    page.get_by_label("Ask our expert", exact=True).click()
    assert_stage(page, "askABroker")

    if stage == "askABroker":
        return
