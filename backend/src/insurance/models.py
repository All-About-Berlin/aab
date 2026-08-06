from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from forms.models import ScheduledMessage
from forms.utils import relative_default_date, validate_email


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


class Case(models.Model):
    """
    A need that usually results in an insurance policy being signed.
    """

    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[validate_email], blank=True)
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

    class Meta:
        verbose_name = "Insurance case"
        ordering = ["-creation_date"]

    def __str__(self):
        return self.name


class CustomerNotification(ScheduledMessage):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)

    @property
    def recipients(self) -> list[str]:
        return [self.case.email]

    @property
    def subject(self) -> str:
        return "Seamus will contact you soon"

    def get_template(self) -> str:
        try:
            if settings.SEAMUS_VACATION[0] <= timezone.now().date() <= settings.SEAMUS_VACATION[1]:
                return f"{self.__class__.__name__}Vacation.html"
        except:
            pass
        return super().get_template()

    def get_context(self) -> dict:
        context = super().get_context()
        if settings.SEAMUS_VACATION:
            context["vacation_start"], context["vacation_end"] = settings.SEAMUS_VACATION
        return context

    class Meta(ScheduledMessage.Meta):
        pass


class BrokerNotification(ScheduledMessage):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)

    @property
    def recipients(self) -> list[str]:
        return ["Seamus.Wolf@horizon65.com"]

    @property
    def subject(self) -> str:
        return f"Insurance question from {self.case.name} (All About Berlin)"

    @property
    def reply_to(self) -> str:
        return self.case.email

    class Meta(ScheduledMessage.Meta):
        pass


class FeedbackNotification(ScheduledMessage):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    delivery_date = models.DateTimeField(default=relative_default_date(days=5))

    @property
    def subject(self) -> str:
        return "Did Seamus help you get insured?"

    @property
    def recipients(self) -> list[str]:
        return [self.case.email]

    class Meta(ScheduledMessage.Meta):
        pass

    class Meta(ScheduledMessage.Meta):
        pass
