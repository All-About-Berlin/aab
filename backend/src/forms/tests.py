from base64 import b64encode
from copy import copy
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from forms.models import (
    CitizenshipFeedback,
    PensionRefundQuestion,
    PensionRefundReminder,
    PensionRefundRequest,
    PlaceSuggestion,
    ResidencePermitFeedback,
    TaxIdRequestFeedbackReminder,
)
from forms.utils import readable_date_range
from rest_framework.test import APITestCase
from unittest.mock import patch
import unittest


def basic_auth_headers(username: str, password: str) -> dict[str, str]:
    return {"Authorization": "Basic {}".format(b64encode(bytes(f"{username}:{password}", "utf-8")).decode("ascii"))}


class ScheduledMessageEndpointMixin:
    def test_create(self):
        response = self.client.post(self.endpoint, self.example_request, format="json")
        self.assertEqual(response.status_code, 201, response.json())

    @patch("forms.views.subscribe_to_newsletter")
    def test_create_without_subscribe_to_newsletter(self, mock_subscribe):
        response = self.client.post(self.endpoint, self.example_request, format="json")
        self.assertEqual(response.status_code, 201, response.json())
        mock_subscribe.assert_not_called()

    @patch("forms.views.subscribe_to_newsletter")
    def test_create_with_subscribe_to_newsletter(self, mock_subscribe):
        request = {**self.example_request, "subscribe_to_newsletter": True}
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 201, response.json())
        mock_subscribe.assert_called_once_with(
            self.example_request["email"], mock_subscribe.call_args[0][1], source=self.model.__name__ + "ViewSet"
        )

    @patch("forms.views.subscribe_to_newsletter", side_effect=Exception("Buttondown error"))
    def test_create_with_subscribe_to_newsletter_failure(self, mock_subscribe):
        request = {**self.example_request, "subscribe_to_newsletter": True}
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 201, response.json())

    def test_list_unauthenticated_401(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 401, response.json())

    def test_list_invalidcredentials_401(self):
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        response = self.client.get(self.endpoint, headers=basic_auth_headers("myuser", "WRONGpassword"))
        self.assertEqual(response.status_code, 401, response.json())

    def test_list_200(self):
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        response = self.client.get(self.endpoint, headers=basic_auth_headers("myuser", "testpassword"))
        self.assertEqual(response.status_code, 200, response.json())

    def test_retrieve_exists_404(self):
        new_object = self.model.objects.create(**self.example_request)
        response = self.client.get(f"{self.endpoint}/{new_object.pk}")
        self.assertEqual(response.status_code, 404)

    def test_retrieve_notexists_404(self):
        response = self.client.get(f"{self.endpoint}/invalidmodificationkey")
        self.assertEqual(response.status_code, 404)

    def test_delete_all_401(self):
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 401, response.json())

    def test_delete_one_404(self):
        new_object = self.model.objects.create(**self.example_request)
        response = self.client.delete(f"{self.endpoint}/{new_object.pk}")
        self.assertEqual(response.status_code, 404)


class FeedbackEndpointMixin:
    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_create(self):
        response = self.client.post(self.endpoint, self.example_request, format="json")
        self.assertEqual(response.status_code, 201, response.json())
        self.assertIn("modification_key", response.json())

    @patch("forms.views.subscribe_to_newsletter")
    def test_create_without_subscribe_to_newsletter(self, mock_subscribe):
        response = self.client.post(self.endpoint, self.example_request, format="json")
        self.assertEqual(response.status_code, 201, response.json())
        mock_subscribe.assert_not_called()

    @patch("forms.views.subscribe_to_newsletter")
    def test_create_with_subscribe_to_newsletter(self, mock_subscribe):
        request = {**self.example_request, "subscribe_to_newsletter": True}
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 201, response.json())
        mock_subscribe.assert_called_once_with(
            self.example_request["email"], mock_subscribe.call_args[0][1], source=self.model.__name__ + "ViewSet"
        )

    @patch("forms.views.subscribe_to_newsletter", side_effect=Exception("Buttondown error"))
    def test_create_with_subscribe_to_newsletter_failure(self, mock_subscribe):
        request = {**self.example_request, "subscribe_to_newsletter": True}
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 201, response.json())

    def test_update(self):
        new_object = self.model.objects.create(**self.example_request)
        updated_request = copy(self.example_request)
        updated_request["email"] = "contact@allaboutberlin.com"
        response = self.client.put(f"{self.endpoint}/{new_object.modification_key}", updated_request, format="json")
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(
            self.model.objects.get(modification_key=new_object.modification_key).email, updated_request["email"]
        )

    @patch("forms.views.subscribe_to_newsletter")
    def test_update_without_subscribe_to_newsletter(self, mock_subscribe):
        new_object = self.model.objects.create(**self.example_request)
        updated_request = copy(self.example_request)
        updated_request["email"] = "contact@allaboutberlin.com"
        response = self.client.put(f"{self.endpoint}/{new_object.modification_key}", updated_request, format="json")
        self.assertEqual(response.status_code, 200, response.json())
        mock_subscribe.assert_not_called()

    @patch("forms.views.subscribe_to_newsletter")
    def test_update_with_subscribe_to_newsletter(self, mock_subscribe):
        new_object = self.model.objects.create(**self.example_request)
        updated_request = {**self.example_request, "subscribe_to_newsletter": True}
        response = self.client.put(f"{self.endpoint}/{new_object.modification_key}", updated_request, format="json")
        self.assertEqual(response.status_code, 200, response.json())
        mock_subscribe.assert_called_once_with(
            self.example_request["email"], mock_subscribe.call_args[0][1], source=self.model.__name__ + "ViewSet"
        )

    @patch("forms.views.subscribe_to_newsletter", side_effect=Exception("Buttondown error"))
    def test_update_with_subscribe_to_newsletter_failure(self, mock_subscribe):
        new_object = self.model.objects.create(**self.example_request)
        updated_request = {**self.example_request, "subscribe_to_newsletter": True}
        response = self.client.put(f"{self.endpoint}/{new_object.modification_key}", updated_request, format="json")
        self.assertEqual(response.status_code, 200, response.json())

    def test_list_200(self):
        # When authenticated, return full object including private data
        new_object = self.model.objects.create(**self.example_request)
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        response = self.client.get(self.endpoint, headers=basic_auth_headers("myuser", "testpassword"))
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(response.json()["results"][0]["modification_key"], new_object.modification_key)
        self.assertEqual(response.json()["results"][0]["email"], new_object.email)

    def test_retrieve_200(self):
        # When authenticated, return full object including private data
        new_object = self.model.objects.create(**self.example_request)
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        response = self.client.get(
            f"{self.endpoint}/{new_object.modification_key}", headers=basic_auth_headers("myuser", "testpassword")
        )
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(response.json()["modification_key"], new_object.modification_key)
        self.assertEqual(response.json()["email"], new_object.email)

    def test_list_unauthenticated_filtered_200(self):
        # When not authenticated, return censored object without private data
        self.model.objects.create(**self.example_request)
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200, response.json())
        self.assertNotIn("email", response.json()["results"][0])
        self.assertNotIn("modification_key", response.json()["results"][0])

    def test_list_invalidcredentials_401(self):
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        response = self.client.get(self.endpoint, headers=basic_auth_headers("myuser", "WRONGpassword"))
        self.assertEqual(response.status_code, 401, response.json())

    def test_retrieve_404(self):
        response = self.client.get(f"{self.endpoint}/invalidmodificationkey")
        self.assertEqual(response.status_code, 404)

    def test_delete_all_unauthenticated_401(self):
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 401, response.json())

    def test_delete_one_unauthenticated_401(self):
        new_object = self.model.objects.create(**self.example_request)
        response = self.client.delete(f"{self.endpoint}/{new_object.pk}")
        self.assertEqual(response.status_code, 401, response.json())

    def test_delete_all_authenticated_405(self):
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        self.model.objects.create(**self.example_request)
        response = self.client.delete(self.endpoint, headers=basic_auth_headers("myuser", "testpassword"))
        self.assertEqual(response.status_code, 405, response.json())
        self.assertEqual(self.model.objects.count(), 1)

    def test_delete_one_authenticated_204(self):
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        new_object = self.model.objects.create(**self.example_request)
        response = self.client.delete(
            f"{self.endpoint}/{new_object.pk}", headers=basic_auth_headers("myuser", "testpassword")
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.model.objects.count(), 0)

    def test_delete_one_invalidcredentials_401(self):
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        new_object = self.model.objects.create(**self.example_request)
        response = self.client.delete(
            f"{self.endpoint}/{new_object.pk}", headers=basic_auth_headers("myuser", "WRONGpassword")
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.model.objects.count(), 1)


class FeedbackReminderMixin:
    feedback_email_delay = timedelta(days=7)

    def test_feedback_reminder_scheduled(self):
        self.client.post(self.endpoint, self.example_request, format="json")
        reminder = self.model.objects.get(email=self.example_request["email"]).feedback_reminder

        self.assertEqual(
            timezone.now().replace(second=0, microsecond=0), reminder.creation_date.replace(second=0, microsecond=0)
        )
        self.assertEqual(
            reminder.delivery_date.replace(microsecond=0),
            (reminder.creation_date + self.feedback_email_delay).replace(microsecond=0),
        )
        self.assertEqual(
            reminder.recipients,
            [
                self.example_request["email"],
            ],
        )


class PensionRefundQuestionTestCase(FeedbackReminderMixin, ScheduledMessageEndpointMixin, APITestCase):
    model = PensionRefundQuestion
    endpoint = "/api/forms/pension-refund-question"
    feedback_email_delay = timedelta(days=7)

    example_request = {
        "name": "John Test",
        "email": "contact@nicolasbouliane.com",
        "country_of_residence": "CA",
        "nationality": "CA",
        "question": "I am John and I have questions",
    }


class PensionRefundRequestTestCase(FeedbackReminderMixin, ScheduledMessageEndpointMixin, APITestCase):
    model = PensionRefundRequest
    endpoint = "/api/forms/pension-refund-request"
    feedback_email_delay = timedelta(days=7)

    example_request = {
        "arrival_date": "2017-07-01",
        "departure_date": "2020-01-01",
        "birth_date": "1990-10-01",
        "country_of_residence": "CA",
        "nationality": "CA",
        "email": "contact@nicolasbouliane.com",
        "name": "John Test",
        "partner": "fundsback",
    }

    def test_create_invalid_nationality_400(self):
        bad_request = copy(self.example_request)
        bad_request["nationality"] = "XX"
        response = self.client.post(self.endpoint, bad_request, format="json")
        self.assertEqual(response.status_code, 400, response.json())

    def test_create_invalid_country_of_residence_400(self):
        bad_request = copy(self.example_request)
        bad_request["country_of_residence"] = "XX"
        response = self.client.post(self.endpoint, bad_request, format="json")
        self.assertEqual(response.status_code, 400, response.json())

    def test_create_invalid_partner_400(self):
        bad_request = copy(self.example_request)
        bad_request["partner"] = "notapartner"
        response = self.client.post(self.endpoint, bad_request, format="json")
        self.assertEqual(response.status_code, 400, response.json())


class PensionRefundReminderTestCase(ScheduledMessageEndpointMixin, APITestCase):
    model = PensionRefundReminder

    endpoint = "/api/forms/pension-refund-reminder"
    example_request = {
        "email": "contact@nicolasbouliane.com",
        "refund_amount": 9000,
        "delivery_date": timezone.now() + relativedelta(months=6),
    }


class TaxIdRequestFeedbackReminderTestCase(ScheduledMessageEndpointMixin, APITestCase):
    model = TaxIdRequestFeedbackReminder
    endpoint = "/api/forms/tax-id-request-feedback-reminder"
    example_request = {
        "email": "contact@nicolasbouliane.com",
        "name": "John Test",
    }

    def test_create_delivery_date(self):
        self.client.post(self.endpoint, self.example_request, format="json")
        reminder = self.model.objects.get(email="contact@nicolasbouliane.com", name="John Test")
        self.assertEqual(
            timezone.now().replace(second=0, microsecond=0), reminder.creation_date.replace(second=0, microsecond=0)
        )
        self.assertEqual(
            reminder.delivery_date.replace(microsecond=0),
            (reminder.creation_date + timedelta(weeks=8)).replace(microsecond=0),
        )


class ResidencePermitFeedbackTestCase(FeedbackEndpointMixin, APITestCase):
    model = ResidencePermitFeedback
    endpoint = "/api/forms/residence-permit-feedback"
    example_request = {
        "email": "contact@nicolasbouliane.com",
        "application_date": "2023-01-01",
        "first_response_date": "2023-02-02",
        "appointment_date": None,
        "pick_up_date": None,
        "department": "E2",
        "notes": "Just some notes",
        "residence_permit_type": "BLUE_CARD",
    }

    def test_list_filter(self):
        # Filter the list with querystring params
        e2_pr = {
            "email": "contact@nicolasbouliane.com",
            "application_date": "2023-01-01",
            "first_response_date": "2023-02-02",
            "appointment_date": None,
            "pick_up_date": None,
            "department": "E2",
            "notes": "Just some notes",
            "residence_permit_type": "PERMANENT_RESIDENCE",
        }
        b1_b2_b3_b4_bc = {
            "email": "contact@nicolasbouliane.com",
            "application_date": "2023-01-01",
            "first_response_date": "2023-02-02",
            "appointment_date": None,
            "pick_up_date": None,
            "department": "B1_B2_B3_B4",
            "notes": "Just some notes",
            "residence_permit_type": "BLUE_CARD",
        }
        b1_b2_b3_b4_pr = {
            "email": "contact@nicolasbouliane.com",
            "application_date": "2023-01-01",
            "first_response_date": "2023-02-02",
            "appointment_date": None,
            "pick_up_date": None,
            "department": "B1_B2_B3_B4",
            "notes": "Just some notes",
            "residence_permit_type": "PERMANENT_RESIDENCE",
        }
        self.model.objects.create(**e2_pr)
        self.model.objects.create(**b1_b2_b3_b4_bc)
        self.model.objects.create(**b1_b2_b3_b4_pr)

        response = self.client.get(f"{self.endpoint}?department=B1_B2_B3_B4")
        self.assertEqual(response.json()["count"], 2)
        self.assertEqual(response.json()["results"][0]["department"], "B1_B2_B3_B4")
        self.assertEqual(response.json()["results"][1]["department"], "B1_B2_B3_B4")

        response = self.client.get(f"{self.endpoint}?residence_permit_type=PERMANENT_RESIDENCE")
        self.assertEqual(response.json()["count"], 2)
        self.assertEqual(response.json()["results"][0]["residence_permit_type"], "PERMANENT_RESIDENCE")
        self.assertEqual(response.json()["results"][1]["residence_permit_type"], "PERMANENT_RESIDENCE")

        response = self.client.get(f"{self.endpoint}?department=B1_B2_B3_B4&residence_permit_type=PERMANENT_RESIDENCE")
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["department"], "B1_B2_B3_B4")
        self.assertEqual(response.json()["results"][0]["residence_permit_type"], "PERMANENT_RESIDENCE")

    def test_date_order_400(self):
        request = {
            "application_date": "2023-02-02",
            "first_response_date": "2023-01-01",  # Smaller than application_date
            "department": "E2",
            "residence_permit_type": "BLUE_CARD",
        }
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 400, response.json())

        request = {
            "application_date": "2023-02-02",
            "first_response_date": "2023-03-03",
            "appointment_date": "2023-02-02",  # Smaller than first_response_date
            "department": "E2",
            "residence_permit_type": "BLUE_CARD",
        }
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 400, response.json())

        request = {
            "application_date": "2023-02-02",
            "first_response_date": "2023-03-03",
            "appointment_date": "2023-04-04",
            "pick_up_date": "2023-03-03",  # Smaller than appointment_date
            "department": "E2",
            "residence_permit_type": "BLUE_CARD",
        }
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 400, response.json())

    def test_schedule_feedback_email(self):
        response = self.client.post(self.endpoint, self.example_request, format="json")
        new_object = self.model.objects.get(modification_key=response.json()["modification_key"])
        reminders = list(new_object.feedback_reminders.all().order_by("delivery_date"))
        self.assertEqual(len(reminders), 2)

        self.assertEqual(
            reminders[0].delivery_date.replace(microsecond=0),
            (reminders[0].creation_date + relativedelta(months=2)).replace(microsecond=0),
        )
        self.assertEqual(
            reminders[1].delivery_date.replace(microsecond=0),
            (reminders[1].creation_date + relativedelta(months=6)).replace(microsecond=0),
        )

    def test_schedule_feedback_email_only_pickup_left(self):
        request = copy(self.example_request)
        request["appointment_date"] = "2023-03-03"
        response = self.client.post(self.endpoint, request, format="json")
        new_object = self.model.objects.get(modification_key=response.json()["modification_key"])
        reminders = list(new_object.feedback_reminders.all())
        self.assertEqual(len(reminders), 1)

        self.assertEqual(
            reminders[0].delivery_date.replace(microsecond=0),
            (reminders[0].creation_date + relativedelta(months=2)).replace(microsecond=0),
        )

    def test_no_feedback_email_if_feedback_complete(self):
        request = copy(self.example_request)
        request["appointment_date"] = "2023-03-03"
        request["pick_up_date"] = "2023-04-04"
        response = self.client.post(self.endpoint, request, format="json")
        new_object = self.model.objects.get(modification_key=response.json()["modification_key"])
        self.assertEqual(new_object.feedback_reminders.count(), 0)

    def test_no_feedback_email_if_email_missing(self):
        request = copy(self.example_request)
        request["email"] = ""
        response = self.client.post(self.endpoint, request, format="json")
        new_object = self.model.objects.get(modification_key=response.json()["modification_key"])
        self.assertEqual(new_object.feedback_reminders.count(), 0)

    def test_stats_fewer_rows(self):
        date_start = date.today()

        self.model.objects.create(
            application_date=date_start,
            first_response_date=date_start + timedelta(days=3),
            appointment_date=date_start + timedelta(days=6),
            pick_up_date=date_start + timedelta(days=9),
            department="E2",
            residence_permit_type="BLUE_CARD",
        )
        self.model.objects.create(
            application_date=date_start,
            first_response_date=date_start + timedelta(days=4),
            appointment_date=date_start + timedelta(days=8),
            pick_up_date=date_start + timedelta(days=12),
            department="E2",
            residence_permit_type="BLUE_CARD",
        )
        self.model.objects.create(
            application_date=date_start,
            first_response_date=date_start + timedelta(days=5),
            appointment_date=date_start + timedelta(days=10),
            pick_up_date=date_start + timedelta(days=15),
            department="E2",
            residence_permit_type="BLUE_CARD",
        )
        self.model.objects.create(
            application_date=date_start,
            first_response_date=date_start + timedelta(days=6),
            appointment_date=date_start + timedelta(days=12),
            pick_up_date=None,
            department="E2",
            residence_permit_type="BLUE_CARD",
        )
        self.model.objects.create(
            application_date=date_start,
            first_response_date=date_start + timedelta(days=7),
            appointment_date=None,
            pick_up_date=None,
            department="E2",
            residence_permit_type="BLUE_CARD",
        )
        response = self.client.get(self.endpoint, format="json").json()

        # 3 out of 5 objects. Percentiles are 1st and 3rd objects.
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["count"], 3)
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["percentile_20"], 9)
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["percentile_80"], 15)

        # 5 out of 5 objects. Percentiles are 1st and 5th objects.
        self.assertEqual(response["stats"]["first_response_date"]["all_time"]["count"], 5)
        self.assertEqual(response["stats"]["first_response_date"]["all_time"]["percentile_20"], 3)
        self.assertEqual(response["stats"]["first_response_date"]["all_time"]["percentile_80"], 7)

        # 4 out of 5 objects. Percentiles are 1st and 4rd objects.
        self.assertEqual(response["stats"]["appointment_date"]["all_time"]["count"], 4)
        self.assertEqual(response["stats"]["appointment_date"]["all_time"]["percentile_20"], 6 - 3)
        self.assertEqual(response["stats"]["appointment_date"]["all_time"]["percentile_80"], 12 - 6)

        # 3 out of 5 objects. Percentiles are 1st and 3rd objects.
        self.assertEqual(response["stats"]["pick_up_date"]["all_time"]["count"], 3)
        self.assertEqual(response["stats"]["pick_up_date"]["all_time"]["percentile_20"], 9 - 6)
        self.assertEqual(response["stats"]["pick_up_date"]["all_time"]["percentile_80"], 15 - 10)

    def test_stats_more_rows(self):
        date_start = date.today()
        for i in range(0, 50):
            self.model.objects.create(
                application_date=date_start,
                first_response_date=date_start + timedelta(days=i),
                appointment_date=date_start + timedelta(days=i * 2),
                pick_up_date=date_start + timedelta(days=i * 3),
                department="E2",
                residence_permit_type="BLUE_CARD",
            )
        response = self.client.get(self.endpoint, format="json").json()

        # 50 objects. Percentiles are 10th and 40th objects.
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["count"], 50)
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["percentile_20"], (10 - 1) * 3)
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["percentile_80"], 40 * 3)

    def test_stats_filtered_rows(self):
        date_start = date.today()
        for i in range(0, 50):
            self.model.objects.create(
                application_date=date_start,
                first_response_date=date_start + timedelta(days=i),
                appointment_date=date_start + timedelta(days=i * 2),
                pick_up_date=date_start + timedelta(days=i * 3),
                department="B1_B2_B3_B4",
                residence_permit_type="BLUE_CARD",
            )

        # Ignored by residence_permit_type
        for i in range(0, 20):
            self.model.objects.create(
                application_date=date_start,
                first_response_date=date_start + timedelta(days=i * 1000),
                appointment_date=date_start + timedelta(days=i * 2000),
                pick_up_date=date_start + timedelta(days=i * 3000),
                department="E2",
                residence_permit_type="PERMANENT_RESIDENCE",
            )

        # Ignored by department
        for i in range(0, 20):
            self.model.objects.create(
                application_date=date_start,
                first_response_date=date_start + timedelta(days=i * 111),
                appointment_date=date_start + timedelta(days=i * 222),
                pick_up_date=date_start + timedelta(days=i * 333),
                department="B6",
                residence_permit_type="BLUE_CARD",
            )
        response = self.client.get(
            self.endpoint + "?residence_permit_type=BLUE_CARD&department=B1_B2_B3_B4", format="json"
        ).json()
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["count"], 50)
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["percentile_20"], (10 - 1) * 3)
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["percentile_80"], 40 * 3)

    def _make_feedback(self, application_date, first_response_date, pick_up_date=None):
        return self.model.objects.create(
            application_date=application_date,
            first_response_date=first_response_date,
            pick_up_date=pick_up_date,
            department="E2",
            residence_permit_type="BLUE_CARD",
        )

    def test_order_by_default(self):
        obj1 = self._make_feedback(date(2023, 1, 1), date(2023, 2, 1))
        obj2 = self._make_feedback(date(2022, 1, 1), date(2022, 2, 1))
        obj3 = self._make_feedback(date(2024, 1, 1), date(2024, 2, 1))
        self.model.objects.filter(pk=obj1.pk).update(creation_date=timezone.now() - timedelta(days=10))
        self.model.objects.filter(pk=obj2.pk).update(creation_date=timezone.now() - timedelta(days=5))
        self.model.objects.filter(pk=obj3.pk).update(creation_date=timezone.now() - timedelta(days=1))

        response = self.client.get(self.endpoint).json()

        dates = [r["application_date"] for r in response["results"]]
        self.assertEqual(dates, ["2024-01-01", "2022-01-01", "2023-01-01"])

    def test_order_by_valid_field(self):
        self._make_feedback(date(2022, 1, 1), date(2022, 2, 1), pick_up_date=date(2024, 6, 1))
        self._make_feedback(date(2024, 1, 1), date(2024, 2, 1), pick_up_date=None)
        self._make_feedback(date(2023, 1, 1), date(2023, 2, 1), pick_up_date=date(2023, 6, 1))

        response = self.client.get(f"{self.endpoint}?order_by=pick_up_date").json()

        pick_up_dates = [r["pick_up_date"] for r in response["results"]]
        self.assertEqual(pick_up_dates, ["2024-06-01", "2023-06-01", None])

    def test_order_by_invalid_field_400(self):
        response = self.client.get(f"{self.endpoint}?order_by=not_a_real_field")
        self.assertEqual(response.status_code, 400)


class CitizenshipFeedbackTestCase(FeedbackEndpointMixin, APITestCase):
    model = CitizenshipFeedback
    endpoint = "/api/forms/citizenship-feedback"
    example_request = {
        "email": "contact@nicolasbouliane.com",
        "application_date": "2023-01-01",
        "first_response_date": "2023-02-02",
        "appointment_date": None,
        "department": "S2",
        "notes": "Just some notes",
    }

    def test_list_filter(self):
        # Filter the list with querystring params
        s1_citizenship = {
            "email": "contact@nicolasbouliane.com",
            "application_date": "2023-01-01",
            "first_response_date": "2023-02-02",
            "appointment_date": None,
            "department": "S1",
            "notes": "Just some notes",
        }
        s1_citizenship_2 = {
            "email": "contact@nicolasbouliane.com",
            "application_date": "2023-01-01",
            "first_response_date": "2023-02-02",
            "appointment_date": None,
            "department": "S1",
            "notes": "Just some notes",
        }
        s3_citizenship = {
            "email": "contact@nicolasbouliane.com",
            "application_date": "2023-01-01",
            "first_response_date": "2023-02-02",
            "appointment_date": None,
            "department": "S3",
            "notes": "Just some notes",
        }
        self.model.objects.create(**s1_citizenship)
        self.model.objects.create(**s1_citizenship_2)
        self.model.objects.create(**s3_citizenship)

        response = self.client.get(f"{self.endpoint}?department=S1")
        self.assertEqual(response.json()["count"], 2)
        self.assertEqual(response.json()["results"][0]["department"], "S1")
        self.assertEqual(response.json()["results"][1]["department"], "S1")

        response = self.client.get(f"{self.endpoint}?department=S3")
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["department"], "S3")

    def test_date_order_400(self):
        request = {
            "application_date": "2023-02-02",
            "first_response_date": "2023-01-01",  # Smaller than application_date
            "department": "S2",
        }
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 400, response.json())

        request = {
            "application_date": "2023-02-02",
            "first_response_date": "2023-03-03",
            "appointment_date": "2023-02-02",  # Smaller than first_response_date
            "department": "S2",
        }
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 400, response.json())

    def test_schedule_feedback_email(self):
        response = self.client.post(self.endpoint, self.example_request, format="json")
        new_object = self.model.objects.get(modification_key=response.json()["modification_key"])
        reminders = list(new_object.feedback_reminders.all().order_by("delivery_date"))
        self.assertEqual(len(reminders), 1)
        self.assertEqual(
            reminders[0].delivery_date.replace(microsecond=0),
            (reminders[0].creation_date + relativedelta(months=3)).replace(microsecond=0),
        )

    def test_no_feedback_email_if_feedback_complete(self):
        request = copy(self.example_request)
        request["appointment_date"] = "2023-03-03"
        response = self.client.post(self.endpoint, request, format="json")
        new_object = self.model.objects.get(modification_key=response.json()["modification_key"])
        self.assertEqual(new_object.feedback_reminders.count(), 0)

    def test_no_feedback_email_if_email_missing(self):
        request = copy(self.example_request)
        request["email"] = ""
        response = self.client.post(self.endpoint, request, format="json")
        new_object = self.model.objects.get(modification_key=response.json()["modification_key"])
        self.assertEqual(new_object.feedback_reminders.count(), 0)

    def test_stats_fewer_rows(self):
        date_start = date.today()

        self.model.objects.create(
            application_date=date_start,
            first_response_date=date_start + timedelta(days=3),
            appointment_date=date_start + timedelta(days=6),
            department="S2",
        )
        self.model.objects.create(
            application_date=date_start,
            first_response_date=date_start + timedelta(days=4),
            appointment_date=date_start + timedelta(days=8),
            department="S2",
        )
        self.model.objects.create(
            application_date=date_start,
            first_response_date=date_start + timedelta(days=5),
            appointment_date=date_start + timedelta(days=10),
            department="S2",
        )
        self.model.objects.create(
            application_date=date_start,
            first_response_date=date_start + timedelta(days=6),
            appointment_date=None,
            department="S2",
        )
        self.model.objects.create(
            application_date=date_start,
            first_response_date=date_start + timedelta(days=7),
            appointment_date=None,
            department="S2",
        )
        response = self.client.get(self.endpoint, format="json").json()

        # 3 out of 5 objects. Percentiles are 1st and 3rd objects.
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["count"], 3)
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["percentile_20"], 6)
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["percentile_80"], 10)

    def test_stats_more_rows(self):
        date_start = date.today()
        for i in range(0, 50):
            self.model.objects.create(
                application_date=date_start,
                first_response_date=date_start + timedelta(days=i),
                appointment_date=date_start + timedelta(days=i * 2),
                department="S2",
            )
        response = self.client.get(self.endpoint, format="json").json()

        # 50 objects. Percentiles are 10th and 40th objects.
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["count"], 50)
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["percentile_20"], (10 - 1) * 2)
        self.assertEqual(response["stats"]["start_to_finish"]["all_time"]["percentile_80"], 40 * 2)

    def _make_feedback(self, application_date, first_response_date, appointment_date=None):
        return self.model.objects.create(
            application_date=application_date,
            first_response_date=first_response_date,
            appointment_date=appointment_date,
            department="S2",
        )

    def test_order_by_valid_field(self):
        self._make_feedback(date(2024, 1, 1), date(2024, 2, 1), appointment_date=None)
        self._make_feedback(date(2023, 1, 1), date(2023, 2, 1), appointment_date=date(2023, 6, 1))
        self._make_feedback(date(2022, 1, 1), date(2022, 2, 1), appointment_date=date(2024, 6, 1))

        response = self.client.get(f"{self.endpoint}?order_by=appointment_date").json()

        appointment_dates = [r["appointment_date"] for r in response["results"]]
        self.assertEqual(appointment_dates, ["2024-06-01", "2023-06-01", None])

    def test_order_by_invalid_field_400(self):
        response = self.client.get(f"{self.endpoint}?order_by=not_a_real_field")
        self.assertEqual(response.status_code, 400)


class PlaceSuggestionTestCase(APITestCase):
    endpoint = "/api/forms/place-suggestion"
    example_request = {
        "category": "veterinarians",
        "business_name": "Test Vet Clinic",
        "google_maps_id": "ChIJTestPlaceId123",
        "languages": "English, German",
        "notes": "Great vet, very friendly",
        "is_owner": False,
        "email": "",
    }

    def test_create(self):
        response = self.client.post(self.endpoint, self.example_request, format="json")
        self.assertEqual(response.status_code, 201, response.json())
        self.assertEqual(PlaceSuggestion.objects.count(), 1)
        suggestion = PlaceSuggestion.objects.first()
        self.assertEqual(suggestion.business_name, "Test Vet Clinic")
        self.assertEqual(suggestion.category, "veterinarians")

    def test_create_minimal(self):
        request = {
            "category": "dentists",
            "business_name": "Minimal Dentist",
        }
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 201, response.json())

    def test_create_with_owner_email(self):
        request = {
            **self.example_request,
            "is_owner": True,
            "email": "tests@allaboutberlin.com",
        }
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 201, response.json())
        suggestion = PlaceSuggestion.objects.first()
        self.assertTrue(suggestion.is_owner)
        self.assertEqual(suggestion.email, "tests@allaboutberlin.com")

    def test_create_invalid_category_400(self):
        request = {**self.example_request, "category": "invalid-category"}
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 400)

    def test_create_missing_business_name_400(self):
        request = {**self.example_request}
        del request["business_name"]
        response = self.client.post(self.endpoint, request, format="json")
        self.assertEqual(response.status_code, 400)

    def test_list_unauthenticated_401(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 401)

    def test_list_invalidcredentials_401(self):
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        response = self.client.get(self.endpoint, headers=basic_auth_headers("myuser", "WRONGpassword"))
        self.assertEqual(response.status_code, 401)

    def test_list_200(self):
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        PlaceSuggestion.objects.create(**self.example_request)
        response = self.client.get(self.endpoint, headers=basic_auth_headers("myuser", "testpassword"))
        self.assertEqual(response.status_code, 200)

    def test_delete_one_unauthenticated_403(self):
        suggestion = PlaceSuggestion.objects.create(**self.example_request)
        response = self.client.delete(f"{self.endpoint}/{suggestion.pk}")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(PlaceSuggestion.objects.count(), 1)

    def test_delete_one_invalidcredentials_401(self):
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        suggestion = PlaceSuggestion.objects.create(**self.example_request)
        response = self.client.delete(
            f"{self.endpoint}/{suggestion.pk}", headers=basic_auth_headers("myuser", "WRONGpassword")
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(PlaceSuggestion.objects.count(), 1)

    def test_delete_one_authenticated_204(self):
        User.objects.create_superuser("myuser", "myemail@test.com", "testpassword")
        suggestion = PlaceSuggestion.objects.create(**self.example_request)
        response = self.client.delete(
            f"{self.endpoint}/{suggestion.pk}", headers=basic_auth_headers("myuser", "testpassword")
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(PlaceSuggestion.objects.count(), 0)


class ReadableDateRangeTestCase(unittest.TestCase):
    def test_days(self):
        self.assertEqual(readable_date_range(0, 0), "0 days")
        self.assertEqual(readable_date_range(0, 7), "0 to 7 days")
        self.assertEqual(readable_date_range(7, 14), "7 to 14 days")
        self.assertEqual(readable_date_range(7, 15), "7 days to 2 weeks")
        self.assertEqual(readable_date_range(15, 17), "2 weeks")
        self.assertEqual(readable_date_range(15, 18), "2 to 3 weeks")
        self.assertEqual(readable_date_range(15, 7 * 8), "2 to 8 weeks")
        self.assertEqual(readable_date_range(15, 7 * 8 + 1), "2 weeks to 2 months")
        self.assertEqual(readable_date_range(2 * 30, 6 * 30), "2 to 6 months")
        self.assertEqual(readable_date_range(6 * 30, 6 * 30), "6 months")
