from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from email_validator import validate_email as original_validate_email, EmailNotValidError
from typing import List, Tuple
import functools
import logging
import random
import requests


logger = logging.getLogger(__name__)


def _offset_from_now(**kwargs):
    return timezone.now() + timedelta(**kwargs)


def relative_default_date(**kwargs):
    return functools.partial(_offset_from_now, **kwargs)


def random_key() -> str:
    return "{k:032x}".format(k=random.getrandbits(128))


def fuzzy_readable_duration(days: int) -> Tuple[int, str]:
    """
    Turns a number of days like 45 into a fuzzy duration tuple like (6, 'weeks')
    """
    if days <= 7 * 2:
        return (round(days), "days")
    elif days <= 7 * 8:
        return (round(days / 7), "weeks")
    else:
        return (round(days / 30), "months")


def pluralize(qty, unit):
    # 0 days, 1 day, 2 days...
    return unit.removesuffix("s") if qty == 1 else unit


def readable_duration(days: int) -> str:
    qty, unit = fuzzy_readable_duration(days)
    return f"{qty} {pluralize(qty, unit)}"


def readable_date_range(days_1: int, days_2: int) -> str:
    qty_1, unit_1 = fuzzy_readable_duration(days_1)
    qty_2, unit_2 = fuzzy_readable_duration(days_2)

    if unit_1 == unit_2:
        if qty_1 == qty_2:  # 3 weeks
            return f"{qty_1} {pluralize(qty_1, unit_1)}"
        return f"{qty_1} to {qty_2} {pluralize(qty_2, unit_2)}"  # 3 to 6 weeks

    # 3 weeks to 6 months
    return f"{qty_1} {pluralize(qty_1, unit_1)} to {qty_2} {pluralize(qty_2, unit_2)}"


def validate_email(email: str) -> None:
    try:
        original_validate_email(email, check_deliverability=True)
    except EmailNotValidError as exc:
        raise ValidationError("Invalid email") from exc


def subscribe_to_newsletter(email: str, ip: str | None = None, source: str | None = None):
    """
    Subscribe an email address to the newsletter via Buttondown API.
    Raises an exception on failure.
    """
    if not settings.BUTTONDOWN_API_KEY:
        raise Exception("BUTTONDOWN_API_KEY is not set")

    response = requests.post(
        "https://api.buttondown.com/v1/subscribers",
        headers={
            "Authorization": f"Token {settings.BUTTONDOWN_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "email_address": email,
            "ip_address": ip,
            **({"tags": [source]} if source else {}),
        },
        timeout=10,
    )

    logger.info(f"Newsletter subscriber added: {email} (IP: {ip}, source: {source or 'None'})")
    return response


def send_email(recipients: List[str], subject: str, body: str, reply_to: str | None = None):
    message_data = {
        "from": "All About Berlin <contact@allaboutberlin.com>",
        "to": recipients,
        "subject": subject,
        "html": body,
    }

    if reply_to:
        message_data["h:Reply-To"] = reply_to

    response = requests.post(
        "https://api.eu.mailgun.net/v3/allaboutberlin.com/messages",
        auth=("api", settings.MAILGUN_API_KEY),
        data=message_data,
    )

    if response.status_code != 200:
        raise Exception("Mailgun request returned status %s. %s" % (response.status_code, response.json()))
