from datetime import timedelta
from django.utils import timezone
from forms.tests import ScheduledMessageEndpointMixin
from insurance.models import Case, CustomerNotification, BrokerNotification, FeedbackNotification
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
