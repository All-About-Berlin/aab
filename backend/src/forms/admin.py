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


class PensionRefundQuestionAdmin(admin.ModelAdmin):
    list_display = ["name", "nationality", "country_of_residence", "question", "creation_date"]


class PensionRefundRequestAdmin(admin.ModelAdmin):
    list_display = ["name", "partner", "nationality", "country_of_residence", "creation_date"]


class PensionRefundReminderAdmin(admin.ModelAdmin):
    list_display = ["email", "creation_date", "delivery_date"]


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


class PlaceSuggestionAdmin(admin.ModelAdmin):
    list_display = ["business_name", "category", "is_owner", "email", "creation_date"]


class ImmigrationOfficeLawsuitAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "application_type",
        "city",
        "application_date",
        "creation_date",
    ]


admin.site.register(PlaceSuggestion, PlaceSuggestionAdmin)
admin.site.register(PensionRefundRequest, PensionRefundRequestAdmin)
admin.site.register(PensionRefundReminder, PensionRefundReminderAdmin)
admin.site.register(PensionRefundQuestion, PensionRefundQuestionAdmin)
admin.site.register(ResidencePermitFeedback, ResidencePermitFeedbackAdmin)
admin.site.register(CitizenshipFeedback, CitizenshipFeedbackAdmin)
admin.site.register(ImmigrationOfficeLawsuit, ImmigrationOfficeLawsuitAdmin)
