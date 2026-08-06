from django.conf import settings
from insurance.models import Genders, HealthInsuranceSignup, HealthInsuranceTypes, Occupation
from typing import Any


def to_german_date(value):
    return value.strftime("%d.%m.%Y") if value else None


def to_country_code(value):
    return value.code if value else None


def truncate(value, max_length):
    return value[:max_length] if value else value


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

    return {
        "metaDaten": {
            "vorgangsId": None,
            "vermittler": truncate(settings.TK_API_VERMITTLER_ID, 10),
            "kooperationId": None,
            "vorlBescheinigung": True,
        },
        "kundengruppe": "BERUFSTAETIGE",
        "sprache": truncate(signup.language, 3),
        "maklervollmacht": "ERWEITERT",
        "bestehendeVersicherung": {
            "imAuslandGelebt": signup.has_lived_abroad,
            "landLetzteVersicherung": to_country_code(signup.country_of_last_insurance),
            "krankenversicherungName": truncate(signup.current_insurer_name, 25) or None,
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
                "titel": truncate(signup.title, 15) or None,
                "vorname": truncate(signup.first_name, 27),
                "nachname": truncate(signup.last_name, 27),
                "namenszusatz": None,
            },
            "adresse": {
                "strasse": truncate(signup.street, 23),
                "hausnummer": truncate(signup.house_number, 8) or None,
                "adresszusatz": truncate(signup.address_extra, 35) or None,
                "plz": truncate(signup.postal_code, 10),
                "ort": truncate(signup.city, 35),
                "land": to_country_code(signup.country),
            },
            "email": truncate(signup.email, 241),
            "telefon": truncate(signup.phone, 20) or None,
            "geburtsdatum": to_german_date(signup.birth_date),
            "versichertennummer": None,
            "geburtsname": truncate(signup.birth_name, 45) or None,
            "geburtsort": truncate(signup.birth_place, 24),
            "geburtsland": to_country_code(signup.birth_country),
            "staatsangehoerigkeit": to_country_code(signup.nationality),
            "mitversicherungVonAngehoerigen": signup.has_familienversicherung,
            "versorgungsbezuege": signup.is_other_pension_recipient,
            "kinder": signup.has_children,
            "versicherungsbeginn": to_german_date(signup.insurance_start_date),
            "kommunikationMailEn": False,
            "rentenbezuege": signup.is_public_pension_recipient,
            "kvPvBefreit": signup.exempt_from_health_pension_contributions,
        },
        "beschaeftigte": {
            "entgeltklasse": _entgeltklasse(signup.is_salary_above_threshold),
            "ersteBeschaeftigung": signup.is_first_job_in_germany,
            "rechtsbelehrung": True,
            "beschaeftigtSeitAb": to_german_date(signup.employed_since),
            "selbststaendig": signup.is_self_employed_on_side,
            "geschaeftsfuehrer": signup.is_managing_director,
            "existenzgruender": signup.is_startup_founder,
            "beschaeftigtMehrereMinijobber": signup.employs_multiple_minijobbers,
            "beschaeftigtArbeitnehmer": signup.employs_workers,
            "stundenSelbststaendigkeit": signup.self_employment_hours_per_week,
            "einkommenSelbststaendigkeit": signup.self_employment_income_per_month,
            "stundenArbeitnehmer": signup.employment_hours_per_week,
            "entgeltArbeitnehmer": signup.employment_income_per_month,
        },
    }
