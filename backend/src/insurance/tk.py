from typing import Any

import phonenumbers
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone
from insurance.models import Genders, HealthInsuranceSignup, HealthInsuranceTypes, Occupation


def to_german_date(value):
    return value.strftime("%d.%m.%Y") if value else None


def to_country_code(value):
    return value.code if value else None


def check_length(field_name, value, min_length, max_length):
    if not value:
        return None
    if len(value) > max_length:
        raise ValueError(f"{field_name} exceeds max length {max_length}: {value!r}")
    if len(value) < min_length:
        raise ValueError(f"{field_name} is shorter than min length {min_length}: {value!r}")
    return value


def check_range(field_name, value, min, max):
    if value is None:
        return None
    if value > max:
        raise ValueError(f"{field_name} exceeds max {max}: {value}")
    if value < min:
        raise ValueError(f"{field_name} is below min {min}: {value}")
    return value


def format_phone(phone):
    if not phone:
        return None
    try:
        parsed = phonenumbers.parse(phone, "DE")
    except phonenumbers.NumberParseException as e:
        raise ValueError(f"Could not parse phone number {phone!r}: {e}")
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError(f"Invalid phone number: {phone!r}")
    # TK requires a '-' or '/' between the region prefix and the local number.
    formatted = f"+{parsed.country_code}-{parsed.national_number}"
    return check_length("phone", formatted, 0, 20)


def _entgeltklasse(is_above_threshold):
    if is_above_threshold is None:
        return None
    return "ueber-jag" if is_above_threshold else "versicherungspflichtig"


def to_tk_payload(signup: HealthInsuranceSignup) -> dict[str, Any]:
    """
    Convert a HealthInsuranceSignup into a payload for the TK /einreichen
    endpoint. Only Occupation.EMPLOYEE (BERUFSTAETIGE) is supported.
    """
    if signup.occupation != Occupation.EMPLOYEE:
        raise NotImplementedError(f"TK payload conversion is not implemented for occupation {signup.occupation!r}")

    if not settings.TK_API_VERMITTLER_ID:
        raise RuntimeError("TK_API_VERMITTLER_ID is not set")

    today = timezone.now().date()

    if signup.has_lived_abroad:
        if not signup.country_of_last_insurance:
            raise ValueError("country_of_last_insurance is required when has_lived_abroad is True")
    else:
        if signup.is_currently_policy_holder is None:
            raise ValueError("is_currently_policy_holder is required when has_lived_abroad is False")
        if signup.is_currently_pflichtversichert is None:
            raise ValueError("is_currently_pflichtversichert is required when has_lived_abroad is False")

    if signup.is_managing_director is None:
        raise ValueError("is_managing_director must not be None")

    if signup.birth_date >= today:
        raise ValueError("birth_date must be in the past")
    if signup.birth_date < today - relativedelta(years=120):
        raise ValueError("birth_date must be less than 120 years ago")

    if signup.employment_start_date < today - relativedelta(years=70):
        raise ValueError("employment_start_date must be less than 70 years ago")
    if signup.employment_start_date > today + relativedelta(months=18):
        raise ValueError("employment_start_date must not be more than 18 months in the future")

    if signup.employment_start_date and signup.insurance_start_date < signup.employment_start_date:
        raise ValueError("insurance_start_date must be on or after employment_start_date")

    beschaeftigte: dict[str, Any] = {
        "entgeltklasse": _entgeltklasse(signup.is_salary_above_threshold),
        "ersteBeschaeftigung": signup.is_first_job_in_germany,
        "rechtsbelehrung": True,
        "beschaeftigtSeitAb": to_german_date(signup.employment_start_date),
        "selbststaendig": signup.is_self_employed,
        "geschaeftsfuehrer": signup.is_managing_director,
        "existenzgruender": signup.is_startup_founder,
        "beschaeftigtMehrereMinijobber": signup.has_multiple_minijob_employees,
        "beschaeftigtArbeitnehmer": signup.has_employees,
        "stundenSelbststaendigkeit": check_range(
            "self_employment_hours_per_week", signup.self_employment_hours_per_week, 0, 999.99
        ),
        "einkommenSelbststaendigkeit": check_range(
            "self_employment_income_per_month", signup.self_employment_income_per_month, 0, 99999.99
        ),
    }
    if signup.is_self_employed:
        beschaeftigte["stundenArbeitnehmer"] = check_range(
            "employment_hours_per_week", signup.employment_hours_per_week, 0, 999.9
        )
        beschaeftigte["entgeltArbeitnehmer"] = check_range(
            "employment_income_per_month", signup.employment_income_per_month, 0, 999999.99
        )

    return {
        "metaDaten": {
            "vorgangsId": None,
            "vermittler": check_length("TK_API_VERMITTLER_ID", settings.TK_API_VERMITTLER_ID, 0, 10),
            "kooperationId": None,
            "vorlBescheinigung": True,
        },
        "kundengruppe": "BERUFSTAETIGE",
        "sprache": check_length("language", signup.language, 0, 3),
        "maklervollmacht": "ERWEITERT",
        "bestehendeVersicherung": {
            "imAuslandGelebt": signup.has_lived_abroad,
            "landLetzteVersicherung": to_country_code(signup.country_of_last_insurance),
            "krankenversicherungName": check_length("current_insurer_name", signup.current_insurer_name, 0, 25),
            "versicherungsart": (
                {
                    HealthInsuranceTypes.PUBLIC: "gesetzlich",
                    HealthInsuranceTypes.PRIVATE: "privat",
                }[signup.current_insurance_type]
                if signup.current_insurance_type
                else None
            ),
            "selbstVersichert": signup.is_currently_policy_holder,
            "pflichtversichert": signup.is_currently_pflichtversichert,
        },
        "persDaten": {
            "name": {
                "geschlecht": {
                    Genders.MALE: "MAENNLICH",
                    Genders.FEMALE: "WEIBLICH",
                    Genders.NON_BINARY: "DIVERS",
                    Genders.UNSPECIFIED: "UNBESTIMMT",
                }[signup.gender],
                "titel": check_length("title", signup.title, 2, 15),
                "vorname": check_length("first_name", signup.first_name, 2, 27),
                "nachname": check_length("last_name", signup.last_name, 2, 27),
                "namenszusatz": None,
            },
            "adresse": {
                "strasse": check_length("street", signup.street, 2, 23),
                "hausnummer": check_length("house_number", signup.house_number, 0, 8),
                "adresszusatz": check_length("address_extra", signup.address_extra, 0, 35),
                "plz": check_length("postal_code", signup.postal_code, 0, 10),
                "ort": check_length("city", signup.city, 2, 35),
                "land": to_country_code(signup.country),
            },
            "email": check_length("email", signup.email, 0, 241),
            "telefon": format_phone(signup.phone),
            "geburtsdatum": to_german_date(signup.birth_date),
            "versichertennummer": None,
            "geburtsname": check_length("birth_name", signup.birth_name or signup.last_name, 0, 45),
            "geburtsort": check_length("birth_place", signup.birth_place, 0, 24),
            "geburtsland": to_country_code(signup.birth_country),
            "staatsangehoerigkeit": to_country_code(signup.nationality),
            "mitversicherungVonAngehoerigen": signup.insure_family_members,
            "versorgungsbezuege": signup.receives_other_pension,
            "kinder": signup.has_children,
            "versicherungsbeginn": to_german_date(signup.insurance_start_date),
            "kommunikationMailEn": False,
            "rentenbezuege": signup.receives_public_pension,
            "kvPvBefreit": signup.is_exempt_from_social_contributions,
        },
        "beschaeftigte": beschaeftigte,
    }
