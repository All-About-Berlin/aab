from django.core.exceptions import ValidationError
from django.db import models
from forms.models import ScheduledMessage
from forms.utils import relative_default_date


class ContactMethod(models.TextChoices):
    EMAIL = "EMAIL", "Email"
    WHATSAPP = "WHATSAPP", "WhatsApp"
    PHONE = "PHONE", "Phone"


class Occupation(models.TextChoices):
    EMPLOYEE = "employee", "Employee"
    AZUBI = "azubi", "Azubi"
    STUDENT_EMPLOYEE = "studentEmployee", "Student (working)"
    STUDENT_SELFEMPLOYED = "studentSelfEmployed", "Student (self-employed)"
    STUDENT_UNEMPLOYED = "studentUnemployed", "Student (unemployed)"
    SELF_EMPLOYED = "selfEmployed", "Self-employed"
    UNEMPLOYED = "unemployed", "Unemployed"
    OTHER = "other", "Other/unknown"


class Intent(models.TextChoices):
    HEALTH_GENERAL = "health", "Health insurance question"
    HEALTH_PRIVATE = "private", "Choose private health insurance"
    HEALTH_PUBLIC = "public", "Choose public health insurance"
    HEALTH_EXPAT = "expat", "Choose expat health insurance"
    OTHER = "other", "Other/unknown"


class Brokers(models.TextChoices):
    CHRISTINA_WEBER = "christina-weber", "Christina Weber"
    SEAMUS_WOLF = "seamus-wolf", "Seamus Wolf"


class Case(models.Model):
    """
    A need that usually results in an insurance policy being signed.
    """

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    contact_method = models.CharField(
        "Contact method", max_length=15, choices=ContactMethod, default=ContactMethod.EMAIL
    )

    occupation = models.CharField(max_length=50, choices=Occupation, default=Occupation.OTHER)
    income = models.PositiveIntegerField("Yearly income", blank=True, null=True, default=None)
    age = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    is_married = models.BooleanField(null=True, default=None)
    children_count = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    is_applying_for_first_visa = models.BooleanField(default=None, null=True)
    has_german_public_insurance = models.BooleanField(default=None, null=True)
    has_eu_public_insurance = models.BooleanField(default=None, null=True)

    intent = models.CharField(max_length=50, choices=Intent, default=Intent.OTHER)

    creation_date = models.DateTimeField(auto_now_add=True)
    question = models.TextField("Question", blank=True)

    broker = models.CharField(max_length=30, choices=Brokers, default=Brokers.SEAMUS_WOLF)
    referrer = models.CharField(blank=True, help_text="Part of the commissions will be paid out to that referrer")
    site = models.CharField(max_length=100, blank=True, default="allaboutberlin.com")

    daily_digest_fields = [
        "contact_method",
        "question",
        "intent",
        "income",
        "occupation",
        "name",
        "age",
        "is_married",
        "children_count",
    ]

    def clean(self):
        super().clean()
        if self.contact_method == ContactMethod.EMAIL and not self.email:
            raise ValidationError({"email": "Email is required when contact_method is EMAIL."})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.email:
            CustomerNotification.objects.get_or_create(case=self)
            FeedbackNotification.objects.get_or_create(case=self)

        if self.contact_method != ContactMethod.WHATSAPP:
            BrokerNotification.objects.get_or_create(case=self)

    @property
    def broker_info(self):
        return {
            "christina-weber": {
                "is_male": False,
                "first_name": "Christina",
                "full_name": "Christina Weber",
                "email": "hello@feather-insurance.com",
            },
            "seamus-wolf": {
                "is_male": True,
                "first_name": "Seamus",
                "full_name": "Seamus Wolf",
                "email": "Seamus.Wolf@horizon65.com",
            },
        }[self.broker]

    class Meta:
        verbose_name = "Insurance case"
        ordering = ["-creation_date"]

    def __str__(self):
        return self.name


class CaseNotificationMixin(ScheduledMessage):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class CustomerNotification(CaseNotificationMixin, ScheduledMessage):
    @property
    def recipients(self) -> list[str]:
        return [
            self.case.email,
        ]

    @property
    def subject(self) -> str:
        return f"{self.case.broker_info['first_name']} will contact you soon"

    class Meta(ScheduledMessage.Meta):
        pass


class BrokerNotification(CaseNotificationMixin, ScheduledMessage):
    @property
    def recipients(self) -> list[str]:
        return [
            self.case.broker_info["email"],
        ]

    @property
    def subject(self) -> str:
        return f"Insurance question from {self.case.name} (All About Berlin)"

    @property
    def reply_to(self) -> str:
        return self.case.email

    class Meta(ScheduledMessage.Meta):
        pass


class FeedbackNotification(CaseNotificationMixin):
    delivery_date = models.DateTimeField(default=relative_default_date(days=5))

    @property
    def subject(self) -> str:
        return f"Did {self.case.broker_info['first_name']} help you get insured?"

    @property
    def recipients(self) -> list[str]:
        return [
            self.case.email,
        ]

    class Meta(ScheduledMessage.Meta):
        pass
