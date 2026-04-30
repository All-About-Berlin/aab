from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, connection
from django.template.loader import render_to_string
from django.utils import timezone
from django_countries.fields import CountryField
from forms.utils import random_key, validate_email
from typing import Any, List
import logging


logger = logging.getLogger(__name__)
filler_string = "AAAAA"
filler_email = "AAAAA@AAAAA.COM"
filler_datetime = datetime(year=2000, month=1, day=1)
filler_date = filler_datetime.date()


class EmailMixin(models.Model):
    email = models.EmailField(validators=[validate_email])

    def remove_personal_data(self):
        super().remove_personal_data()
        self.email = filler_email

    class Meta:
        abstract = True


class NameMixin(models.Model):
    name = models.CharField(max_length=150)

    def remove_personal_data(self):
        super().remove_personal_data()
        self.name = filler_string

    class Meta:
        abstract = True


class MessageStatus(models.IntegerChoices):
    SCHEDULED = 0, "Scheduled"
    FAILED = 1, "Error"
    SENT = 2, "Sent"
    REDACTED = 3, "Sent and redacted for privacy"


class ScheduledMessage(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(default=timezone.now)
    status = models.PositiveSmallIntegerField(choices=MessageStatus, default=MessageStatus.SCHEDULED)  # type: ignore

    @property
    def recipients(self) -> List[str]:
        raise NotImplementedError

    subject: str = ""
    template: str | None = None
    reply_to: str | None = None

    def save(self, *args, **kwargs):
        if not self.pk:
            logger.info(f"Scheduling 1 message ({self.__class__.__name__})")
            if settings.DEBUG_EMAILS:
                logger.info(
                    "Scheduling email message:\n"
                    f"\tDeliver on: {self.delivery_date}\n"
                    f"\tTo: {', '.join(self.recipients)}\n"
                    f"\tReply-To: {self.reply_to}\n"
                    f"\tSubject: {self.subject}\n"
                )
                logger.debug(f"\tEmail body: \n{self.get_body()}")
        super().save(*args, **kwargs)

    def remove_personal_data(self):
        self.status = MessageStatus.REDACTED

    def get_body(self) -> str:
        return render_to_string(self.template, {"message": self})

    class Meta:
        abstract = True
        ordering = ["-creation_date"]


class MultiStageFeedback(EmailMixin, models.Model):
    modification_key = models.CharField(primary_key=True, max_length=32, unique=True, default=random_key)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    email = models.EmailField(validators=[validate_email], blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["-modification_date"]


class PensionRefundQuestion(NameMixin, EmailMixin, ScheduledMessage):
    nationality = CountryField()
    country_of_residence = CountryField()
    question = models.TextField()

    recipients = ["support@pension-refund.com"]
    template = "pension-refund-question.html"
    daily_digest_fields = ["question", "nationality", "country_of_residence"]

    @property
    def subject(self) -> str:
        return f"Pension refund question from {self.name} (All About Berlin)"

    @property
    def reply_to(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        PensionRefundQuestionFeedbackReminder.objects.get_or_create(
            refund_question=self, delivery_date=timezone.now() + relativedelta(days=7)
        )

    def __str__(self):
        return self.name

    class Meta(ScheduledMessage.Meta):
        pass


class PensionRefundQuestionFeedbackReminder(ScheduledMessage):
    refund_question = models.OneToOneField(
        PensionRefundQuestion, related_name="feedback_reminder", on_delete=models.CASCADE
    )

    subject = "Did Pension Refund Germany answer your question?"
    template = "pension-refund-question-feedback.html"

    @property
    def recipients(self) -> list[str]:
        return [
            self.refund_question.email,
        ]

    class Meta(ScheduledMessage.Meta):
        pass


pension_refund_partners = {
    "fundsback": "partner@fundsback.org",
    "germanypensionrefund": "refund@germanypensionrefund.com",
    "pensionrefundgermany": "support@pension-refund.com",
}


class PensionRefundRequest(NameMixin, EmailMixin, ScheduledMessage):
    arrival_date = models.DateField()
    birth_date = models.DateField()
    country_of_residence = CountryField()
    departure_date = models.DateField()
    nationality = CountryField()
    partner = models.CharField(max_length=30, choices=pension_refund_partners)

    template = "pension-refund-request.html"
    daily_digest_fields = ["partner", "nationality", "country_of_residence"]

    def remove_personal_data(self):
        super().remove_personal_data()
        self.birth_date = filler_date

    @property
    def recipients(self) -> List[str]:
        return [pension_refund_partners[self.partner]]

    @property
    def subject(self) -> str:
        return f"Pension refund request from {self.name} (All About Berlin)"

    @property
    def reply_to(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        PensionRefundRequestFeedbackReminder.objects.get_or_create(
            refund_request=self, delivery_date=timezone.now() + relativedelta(days=7)
        )

    def __str__(self):
        return self.name

    class Meta(ScheduledMessage.Meta):
        pass


class PensionRefundRequestFeedbackReminder(ScheduledMessage):
    refund_request = models.OneToOneField(
        PensionRefundRequest, related_name="feedback_reminder", on_delete=models.CASCADE
    )

    subject = "Did you get your pension refund?"
    template = "pension-refund-request-feedback.html"

    @property
    def recipients(self) -> list[str]:
        return [
            self.refund_request.email,
        ]

    class Meta(ScheduledMessage.Meta):
        pass


class PensionRefundReminder(EmailMixin, ScheduledMessage):
    refund_amount = models.PositiveIntegerField()

    subject = "Reminder: you can now get your German pension payments back"
    template = "pension-refund-reminder.html"
    daily_digest_fields = ["delivery_date"]

    @property
    def recipients(self) -> List[str]:
        return [
            str(self.email),
        ]

    class Meta(ScheduledMessage.Meta):
        pass


def in_8_weeks():
    return timezone.now() + timedelta(weeks=8)


class FeedbackManager(models.Manager):
    def wait_time(self, date_column_start: str, date_column_end: str, extra_filters: dict[str, str]) -> dict[str, Any]:
        where_extras = ""
        for column_name, value in extra_filters.items():
            where_extras += f" AND {column_name}=%({column_name})s" if value else ""

        db_table = connection.ops.quote_name(self.model._meta.db_table)
        column_start = connection.ops.quote_name(date_column_start)
        column_end = connection.ops.quote_name(date_column_end)

        percentiles_query = f"""
            WITH time_diffs AS (
                SELECT
                    CAST( (julianday({column_end}) - julianday({column_start})) AS INT) AS time_diff
                FROM {db_table}
                WHERE
                    {column_end} IS NOT NULL
                    AND {column_start} IS NOT NULL
                    {where_extras}
                ORDER BY time_diff ASC
            ),
            row_count AS (
                SELECT COUNT(*) AS row_count FROM time_diffs
            ),
            percentile_rows AS(
                SELECT
                    CAST(CEIL(row_count * 0.2) AS INT) AS row_20,
                    CAST(FLOOR(row_count * 0.8) AS INT) + 1 AS row_80
                FROM row_count
            ),
            numbered_rows AS (
                SELECT
                    time_diff,
                    row_20,
                    row_80,
                    ROW_NUMBER() over (order by time_diff) as rownum
                FROM time_diffs, percentile_rows
            )
            SELECT
                time_diff,
                row_count,
                AVG(time_diff) OVER () AS average
            FROM numbered_rows, row_count
            WHERE
                rownum >= row_20
                AND rownum <= row_80
        """

        with connection.cursor() as cursor:
            cursor.execute(
                percentiles_query,
                {
                    "date_column_start": date_column_start,
                    "date_column_end": date_column_end,
                    **extra_filters,
                },
            )
            results = list(zip(*cursor.fetchall()))
        if results and len(results[0]) >= 2:
            percentile_20 = results[0][0]
            percentile_80 = results[0][-1]
            row_count = results[1][0]
            average = results[2][0]
        else:  # No data
            percentile_20 = None
            percentile_80 = None
            row_count = 0
            average = None

        return {
            "percentile_20": percentile_20,
            "percentile_80": percentile_80,
            "count": row_count,
            "average": average,
        }


class HealthInsuranceTypes(models.TextChoices):
    PUBLIC = "PUBLIC", "Public health insurance"
    PRIVATE = "PRIVATE", "Private health insurance"
    EXPAT = "EXPAT", "Expat health insurance"
    FAMILY = "FAMILY", "Familienversicherung"
    EHIC = "EHIC", "EHIC"
    OTHER = "OTHER", "Other"
    UNKNOWN = "", "Unknown"


class ResidencePermitTypes(models.TextChoices):
    BLUE_CARD = "BLUE_CARD", "Blue Card"
    CITIZENSHIP = "CITIZENSHIP", "Citizenship"
    FAMILY_REUNION_VISA = "FAMILY_REUNION_VISA", "Family reunion visa"
    FREELANCE_VISA = "FREELANCE_VISA", "Freelance visa"
    JOB_SEEKER_VISA = "JOB_SEEKER_VISA", "Job seeker visa"
    PERMANENT_RESIDENCE = "PERMANENT_RESIDENCE", "Permanent residence"
    STUDENT_VISA = "STUDENT_VISA", "Student visa"
    WORK_VISA = "WORK_VISA", "Work visa"


class ResidencePermitDepartments(models.TextChoices):
    A1_A5 = "A1_A5", "A1, A5"
    A2_A3_A4 = "A2_A3_A4", "A2, A3, A4"
    B1_B2_B3_B4 = "B1_B2_B3_B4", "B1, B2, B3, B4"
    B6 = "B6", "B6"
    E1 = "E1", "E1"
    E2 = "E2", "E2"
    E3 = "E3", "E3"
    E4 = "E4", "E4"
    E5 = "E5", "E5"
    E6 = "E6", "E6"
    F1_F2 = "F1_F2", "F1, F2"
    M1 = "M1", "M1"
    M2 = "M2", "M2"
    M3 = "M3", "M3"
    M4 = "M4", "M4"


class ResidencePermitFeedback(MultiStageFeedback):
    residence_permit_type = models.CharField(choices=ResidencePermitTypes, max_length=30)

    application_date = models.DateField()
    first_response_date = models.DateField(null=True, blank=True)
    appointment_date = models.DateField(null=True, blank=True)
    pick_up_date = models.DateField(null=True, blank=True)
    validity_in_months = models.PositiveSmallIntegerField(null=True, blank=True, default=None)

    department = models.CharField(max_length=30, choices=ResidencePermitDepartments)
    notes = models.TextField(blank=True)

    health_insurance_type = models.CharField(
        max_length=20, blank=True, choices=HealthInsuranceTypes, default=HealthInsuranceTypes.UNKNOWN
    )
    health_insurance_name = models.CharField(blank=True, max_length=150)

    objects = FeedbackManager()
    daily_digest_fields = [
        "notes",
        "application_date",
        "first_response_date",
        "appointment_date",
        "pick_up_date",
        "validity_in_months",
        "health_insurance_type",
        "health_insurance_name",
    ]

    def clean(self):
        if self.first_response_date and self.application_date > self.first_response_date:
            raise ValidationError("application_date can't be after first_response_date")
        if self.appointment_date and self.first_response_date > self.appointment_date:
            raise ValidationError("first_response_date can't be after appointment_date")
        if self.pick_up_date and self.appointment_date > self.pick_up_date:
            raise ValidationError("appointment_date can't be after pick_up_date")

    def save(self, *args, **kwargs):
        """
        Schedule feedback reminders in the future
        """
        self.feedback_reminders.all().delete()  # type: ignore

        if self.email and self.pick_up_date:
            self.email = filler_email

        super().save(*args, **kwargs)

        # No feedback email needed if the feedback is complete
        if self.email and not self.pick_up_date:
            self.feedback_reminders.create(delivery_date=timezone.now() + relativedelta(months=2))  # type: ignore
            if not self.appointment_date:
                self.feedback_reminders.create(delivery_date=timezone.now() + relativedelta(months=6))  # type: ignore

    def __str__(self):
        return f"{self.get_residence_permit_type_display()} ({self.get_department_display()})"  # type: ignore

    class Meta(MultiStageFeedback.Meta):
        verbose_name_plural = "Residence permit feedback"


class ResidencePermitFeedbackReminder(ScheduledMessage):
    feedback = models.ForeignKey(ResidencePermitFeedback, related_name="feedback_reminders", on_delete=models.CASCADE)

    subject = "Did you get your residence permit?"
    template = "residence-permit-feedback-reminder.html"

    @property
    def recipients(self) -> list[str]:
        return [
            self.feedback.email,  # type: ignore
        ]

    class Meta(ScheduledMessage.Meta):
        pass


class CitizenshipDepartments(models.TextChoices):
    S1 = "S1", "S1"
    S2 = "S2", "S2"
    S3 = "S3", "S3"
    S4 = "S4", "S4"
    S5 = "S5", "S5"
    S6 = "S6", "S6"


class CitizenshipFeedback(MultiStageFeedback):
    application_date = models.DateField()
    first_response_date = models.DateField(null=True, blank=True)
    appointment_date = models.DateField(null=True, blank=True)

    department = models.CharField(max_length=30, choices=CitizenshipDepartments)
    notes = models.TextField(blank=True)

    objects = FeedbackManager()
    daily_digest_fields = [
        "notes",
        "application_date",
        "first_response_date",
        "appointment_date",
        "email",
    ]

    def clean(self):
        if self.first_response_date and self.application_date > self.first_response_date:
            raise ValidationError("application_date can't be after first_response_date")
        if self.appointment_date and self.first_response_date > self.appointment_date:
            raise ValidationError("first_response_date can't be after appointment_date")

    def save(self, *args, **kwargs):
        """
        Schedule feedback reminders in the future
        """
        self.feedback_reminders.all().delete()  # type: ignore

        if self.email and self.appointment_date:
            self.email = filler_email

        super().save(*args, **kwargs)

        # No feedback email needed if the feedback is complete
        if self.email and not self.appointment_date:
            self.feedback_reminders.create(delivery_date=timezone.now() + relativedelta(months=3))  # type: ignore

    def __str__(self):
        return f"Citizenship ({self.get_department_display()})"  # type: ignore

    class Meta(MultiStageFeedback.Meta):
        verbose_name_plural = "Citizenship feedback"


class CitizenshipFeedbackReminder(ScheduledMessage):
    feedback = models.ForeignKey(CitizenshipFeedback, related_name="feedback_reminders", on_delete=models.CASCADE)

    subject = "Did you get your German citizenship?"
    template = "citizenship-feedback-reminder.html"

    @property
    def recipients(self) -> list[str]:
        return [
            self.feedback.email,  # type: ignore
        ]

    class Meta(ScheduledMessage.Meta):
        pass


class PlaceCategories(models.TextChoices):
    BOARD_GAMES = "board-games"
    CINEMAS = "cinemas"
    DENTISTS = "dentists"
    DOCTORS = "doctors"
    DRIVING_SCHOOLS = "driving-schools"
    FOREIGN_INGREDIENTS = "foreign-ingredients"
    GYMS = "gyms"
    GYNECOLOGISTS = "gynecologists"
    HAIRDRESSERS = "hairdressers"
    LAWYERS = "lawyers"
    MOTORCYCLE_STORES = "motorcycle-stores"
    PIZZA = "pizza"
    PSYCHIATRISTS = "psychiatrists"
    PSYCHOTHERAPISTS = "psychotherapists"
    RELOCATION_AGENCIES = "relocation-agencies"
    STEUERBERATER = "steuerberater"
    VETERINARIANS = "veterinarians"


class PlaceSuggestion(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100, choices=PlaceCategories)
    business_name = models.CharField(max_length=200)
    google_maps_id = models.CharField(max_length=200, blank=True)
    languages = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    is_owner = models.BooleanField(default=False)
    email = models.EmailField(validators=[validate_email], blank=True)
    accepts_public_health_insurance = models.BooleanField(null=True, default=None)

    daily_digest_fields = ["category", "google_maps_id", "languages", "notes", "is_owner"]

    def __str__(self):
        return self.business_name

    class Meta:
        ordering = ["-creation_date"]


class TaxIdRequestFeedbackReminder(NameMixin, EmailMixin, ScheduledMessage):
    delivery_date = models.DateTimeField(default=in_8_weeks)

    subject = "Did you receive your tax ID?"
    template = "tax-id-request-feedback-reminder.html"

    @property
    def recipients(self) -> list[str]:
        return [
            self.email,  # type: ignore
        ]

    class Meta(ScheduledMessage.Meta):
        pass
