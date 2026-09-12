from django.contrib import admin
from forms.models import (
    CitizenshipFeedback,
    ImmigrationOfficeLawsuit,
    PensionRefundReminder,
    PensionRefundRequest,
    PensionRefundQuestion,
    PlaceSuggestion,
    ResidencePermitFeedback,
)


@admin.register(PensionRefundQuestion)
class PensionRefundQuestionAdmin(admin.ModelAdmin):
    list_display = ["name", "nationality", "country_of_residence", "question", "creation_date"]


@admin.register(PensionRefundRequest)
class PensionRefundRequestAdmin(admin.ModelAdmin):
    list_display = ["name", "partner", "nationality", "country_of_residence", "creation_date"]


@admin.register(PensionRefundReminder)
class PensionRefundReminderAdmin(admin.ModelAdmin):
    list_display = ["email", "creation_date", "delivery_date"]


@admin.register(ResidencePermitFeedback)
class ResidencePermitFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        "short_modification_date",
        "has_notes",
        "department",
        "residence_permit_type",
        "application_date",
        "first_response_date",
        "appointment_date",
        "pick_up_date",
        "validity_in_months",
        "health_insurance_name",
        "email",
    ]

    def short_modification_date(self, obj):
        return obj.modification_date.strftime("%b. %d, %Y")

    short_modification_date.short_description = "Created"

    def has_notes(self, obj):
        return bool(obj.notes)

    has_notes.boolean = True  # Show as a boolean icon
    has_notes.short_description = "Has notes"


@admin.register(CitizenshipFeedback)
class CitizenshipFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        "short_modification_date",
        "has_notes",
        "department",
        "application_date",
        "first_response_date",
        "appointment_date",
        "email",
    ]

    def short_modification_date(self, obj):
        return obj.modification_date.strftime("%b. %d, %Y")

    short_modification_date.short_description = "Created"

    def has_notes(self, obj):
        return bool(obj.notes)

    has_notes.boolean = True  # Show as a boolean icon
    has_notes.short_description = "Has notes"


@admin.register(PlaceSuggestion)
class PlaceSuggestionAdmin(admin.ModelAdmin):
    list_display = ["business_name", "category", "is_owner", "email", "creation_date"]


@admin.register(ImmigrationOfficeLawsuit)
class ImmigrationOfficeLawsuitAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "application_type",
        "city",
        "application_date",
        "creation_date",
    ]
