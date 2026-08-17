from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
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
    A question/request that usually results in a health insurance policy being signed.
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

    referrer = models.CharField(blank=True)
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


class Genders(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    NON_BINARY = "non_binary", "Non-binary"
    UNSPECIFIED = "unspecified", "Unspecified"


class HealthInsuranceTypes(models.TextChoices):
    PUBLIC = "public", "Public/statutory"
    PRIVATE = "private", "Private"


class HealthInsurerChoices(models.TextChoices):
    TK = "tk", "Techniker Krankenkasse"


class SignupStatus(models.TextChoices):
    NEW = "new", "New"
    SUBMITTED = "submitted", "Submitted to insurer"
    ACCEPTED = "accepted", "Accepted by insurer"
    REJECTED = "rejected", "Rejected by insurer"
    ERROR = "error", "Submission error"


class IdDocumentTypes(models.TextChoices):
    PASSBILD = "PASSBILD", "Passport photo"
    DOKUMENT = "DOKUMENT", "Document"
    OTHER = "OTHER", "Other"


class Languages(models.TextChoices):
    EN = "EN", "English"
    DE = "DE", "German"


class HealthInsuranceSignup(models.Model):
    """
    A request to sign someone up for health insurance
    """

    # Case information

    referrer = models.CharField(blank=True)

    creation_date = models.DateTimeField(auto_now_add=True)
    submission_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=SignupStatus, default=SignupStatus.NEW)

    insurer = models.CharField(max_length=10, choices=HealthInsurerChoices, default=HealthInsurerChoices.TK)
    insurance_start_date = models.DateField()

    # Person information

    occupation = models.CharField(max_length=50, choices=Occupation, default=Occupation.OTHER)

    gender = models.CharField(max_length=15, choices=Genders)
    title = models.CharField(max_length=15, blank=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    birth_name = models.CharField(max_length=150, blank=True)

    birth_date = models.DateField()
    birth_place = models.CharField(max_length=50)
    birth_country = CountryField()
    nationality = CountryField()

    # Contact information

    email = models.EmailField(validators=[validate_email])
    phone = models.CharField(max_length=30, blank=True)
    language = models.CharField(max_length=2, choices=Languages, default=Languages.EN)

    # Address information

    street = models.CharField(max_length=150)
    house_number = models.CharField(max_length=30, blank=True)
    address_extra = models.CharField(max_length=150, blank=True)
    postal_code = models.CharField(max_length=15)
    city = models.CharField(max_length=150)
    country = CountryField()

    # Insurance information

    has_children = models.BooleanField()

    insure_family_members = models.BooleanField(default=False)
    receives_other_pension = models.BooleanField(default=False)
    receives_public_pension = models.BooleanField(default=False)
    is_exempt_from_social_contributions = models.BooleanField(default=False)

    # Current insurance

    has_lived_abroad = models.BooleanField()
    country_of_last_insurance = CountryField(blank=True, null=True)
    current_insurer_name = models.CharField(max_length=25, blank=True)
    current_insurance_type = models.CharField(max_length=15, choices=HealthInsuranceTypes, blank=True)
    is_currently_pflichtversichert = models.BooleanField(blank=True, null=True)
    is_currently_policy_holder = models.BooleanField(blank=True, null=True)

    # Employees

    is_salary_above_threshold = models.BooleanField()  # TODO: Can be calculated from vars in ursus_config
    is_first_job_in_germany = models.BooleanField()

    employment_start_date = models.DateField()
    employment_hours_per_week = models.PositiveIntegerField(blank=True, null=True)
    employment_income_per_month = models.PositiveIntegerField(blank=True, null=True)

    is_self_employed = models.BooleanField(default=False)
    self_employment_hours_per_week = models.PositiveIntegerField(default=0)
    self_employment_income_per_month = models.PositiveIntegerField(default=0)

    is_managing_director = models.BooleanField(default=False)
    is_startup_founder = models.BooleanField(default=False)
    has_employees = models.BooleanField(default=False, help_text="Hires employees, excluding minijobbers")
    has_multiple_minijob_employees = models.BooleanField(default=False, help_text="Hires MORE THAN ONE minijobber")

    class Meta:
        verbose_name = "Health insurance signup"
        ordering = ["-creation_date"]

    def clean(self):
        super().clean()
        errors: dict[str, str] = {}
        today = timezone.now().date()

        if self.has_lived_abroad and not self.country_of_last_insurance:
            errors["country_of_last_insurance"] = "Required when has_lived_abroad is True."

        insurance_is_german = not self.has_lived_abroad or (
            self.country_of_last_insurance and self.country_of_last_insurance.code == "DE"
        )
        if insurance_is_german and not self.current_insurer_name:
            errors["current_insurer_name"] = "Required when the current or last insurance is German."

        if self.insurance_start_date:
            earliest = today - relativedelta(months=18)
            latest = today + relativedelta(months=12)
            if not earliest <= self.insurance_start_date <= latest:
                errors["insurance_start_date"] = "Must be within 18 months in the past and 12 months in the future."

        if self.birth_date:
            if self.birth_date >= today:
                errors["birth_date"] = "Must be in the past."
            elif self.birth_date < today - relativedelta(years=120):
                errors["birth_date"] = "Must be less than 120 years ago."

        if self.is_self_employed:
            if self.employment_hours_per_week is None:
                errors["employment_hours_per_week"] = "Required when is_self_employed is True."
            if self.employment_income_per_month is None:
                errors["employment_income_per_month"] = "Required when is_self_employed is True."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.insurer})"
