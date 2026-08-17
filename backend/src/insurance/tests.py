from datetime import date, datetime, timedelta, timezone as dt_timezone
from unittest.mock import patch
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from forms.tests import ScheduledMessageEndpointMixin
from insurance.models import Case, CustomerNotification, BrokerNotification, FeedbackNotification
from insurance.tk import format_phone
from rest_framework.test import APITestCase


class CaseTestCase(ScheduledMessageEndpointMixin, APITestCase):
    model = Case
    endpoint = "/api/insurance/case"

    def setUp(self):
        self.example_request = {
            "contact_method": "EMAIL",
            "name": "John Smith",
            "income": 30000,
            "occupation": "selfEmployed",
            "age": 30,
            "is_married": True,
            "children_count": 3,
            "is_applying_for_first_visa": True,
            "has_eu_public_insurance": True,
            "has_german_public_insurance": True,
            "email": "contact@nicolasbouliane.com",
            "question": "Did you ever think that maybe there’s more to life than being really, really... really ridiculously well insured?\n\nI don't think so.",
            "referrer": "partner123",
        }

    def test_retrieve_exists_404(self):
        super().test_retrieve_exists_404()

    def test_delete_one_404(self):
        super().test_retrieve_exists_404()

    def test_create_confirmation_message(self):
        self.client.post(self.endpoint, self.example_request, format="json")
        case = Case.objects.get(email="contact@nicolasbouliane.com")
        customer_email = CustomerNotification.objects.get(case=case)
        broker_email = BrokerNotification.objects.get(case=case)
        feedback_email = FeedbackNotification.objects.get(case=case)

        self.assertEqual(
            feedback_email.recipients,
            [
                "contact@nicolasbouliane.com",
            ],
        )
        self.assertEqual(
            timezone.now().replace(second=0, microsecond=0),
            feedback_email.creation_date.replace(second=0, microsecond=0),
        )
        self.assertEqual(
            feedback_email.delivery_date.replace(microsecond=0),
            (feedback_email.creation_date + timedelta(days=5)).replace(microsecond=0),
        )

        self.assertEqual(
            broker_email.recipients,
            [
                "Seamus.Wolf@horizon65.com",
            ],
        )
        self.assertEqual(
            timezone.now().replace(second=0, microsecond=0), broker_email.delivery_date.replace(second=0, microsecond=0)
        )

        self.assertEqual("Seamus" in customer_email.get_body(), True)
        self.assertEqual(
            customer_email.recipients,
            [
                "contact@nicolasbouliane.com",
            ],
        )
        self.assertEqual(
            timezone.now().replace(second=0, microsecond=0),
            customer_email.delivery_date.replace(second=0, microsecond=0),
        )


class MinimalCaseTestCase(CaseTestCase):
    """
    Test with the minimum amount of information in the request
    """

    def setUp(self):
        self.example_request = {
            "name": "John Smith",
            "email": "contact@nicolasbouliane.com",
        }


class CaseSeamusVacationTestCase(TestCase):
    """
    Test that settings.SEAMUS_VACATION works properly
    """

    def setUp(self):
        case = Case.objects.create(name="John Smith", email="contact@nicolasbouliane.com")
        self.notification = CustomerNotification.objects.get(case=case)

        frozen_now = datetime(2026, 8, 7, 12, 0, tzinfo=dt_timezone.utc)
        patcher = patch("insurance.models.timezone.now", return_value=frozen_now)
        patcher.start()
        self.addCleanup(patcher.stop)

    @override_settings(SEAMUS_VACATION=None)
    def test_unset_uses_default_template(self):
        self.assertEqual(self.notification.get_template(), "CustomerNotification.html")
        self.assertNotIn("on vacation", self.notification.get_body())

    @override_settings(SEAMUS_VACATION=(date(2026, 8, 5), date(2026, 8, 12)))
    def test_during_vacation_uses_vacation_template(self):
        self.assertEqual(self.notification.get_template(), "CustomerNotificationVacation.html")
        self.assertIn("from August 5 to August 12", self.notification.get_body())

    @override_settings(SEAMUS_VACATION=(date(2026, 8, 7), date(2026, 8, 12)))
    def test_start_boundary_is_inclusive(self):
        self.assertEqual(self.notification.get_template(), "CustomerNotificationVacation.html")

    @override_settings(SEAMUS_VACATION=(date(2026, 8, 1), date(2026, 8, 7)))
    def test_end_boundary_is_inclusive(self):
        self.assertEqual(self.notification.get_template(), "CustomerNotificationVacation.html")

    @override_settings(SEAMUS_VACATION=(date(2026, 8, 8), date(2026, 8, 14)))
    def test_before_vacation_uses_default_template(self):
        self.assertEqual(self.notification.get_template(), "CustomerNotification.html")

    @override_settings(SEAMUS_VACATION=(date(2026, 8, 1), date(2026, 8, 6)))
    def test_after_vacation_uses_default_template(self):
        self.assertEqual(self.notification.get_template(), "CustomerNotification.html")


class FormatPhoneTestCase(SimpleTestCase):
    def test_blank_input_returns_none(self):
        self.assertIsNone(format_phone(None))
        self.assertIsNone(format_phone(""))

    def test_german_landline_variants_normalize(self):
        for phone in [
            "030 12345678",
            "+49 30 12345678",
            "+493012345678",
            "+49-30-12345678",
            "0049 30 12345678",
            "30 12345678",
        ]:
            with self.subTest(phone=phone):
                self.assertEqual(format_phone(phone), "+49-3012345678")

    def test_german_mobile_with_country_code(self):
        self.assertEqual(format_phone("+49 176 12345678"), "+49-17612345678")

    def test_german_mobile_with_trunk_prefix(self):
        self.assertEqual(format_phone("01761234567"), "+49-1761234567")

    def test_us_number_variants_normalize(self):
        for phone in ["+1 212 555 0100", "00 1 212 555 0100", "+12125550100"]:
            with self.subTest(phone=phone):
                self.assertEqual(format_phone(phone), "+1-2125550100")

    def test_number_without_country_code_defaults_to_germany(self):
        self.assertEqual(format_phone("(212) 555-0100"), "+49-2125550100")

    def test_unparseable_string_raises(self):
        with self.assertRaisesMessage(ValueError, "Could not parse phone number"):
            format_phone("not-a-phone")

    def test_too_short_raises(self):
        with self.assertRaisesMessage(ValueError, "Invalid phone number"):
            format_phone("12")

    def test_reserved_us_555_number_is_invalid(self):
        with self.assertRaisesMessage(ValueError, "Invalid phone number"):
            format_phone("+1-555-123-4567")
