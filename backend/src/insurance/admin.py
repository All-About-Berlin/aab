from django.contrib import admin
from insurance.models import Case


class CaseAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Case information",
            {
                "fields": (
                    "creation_date",
                    "occupation",
                    "is_applying_for_first_visa",
                    "has_german_public_insurance",
                    "has_eu_public_insurance",
                    "income",
                    "age",
                    "is_married",
                    "children_count",
                    "intent",
                    "question",
                    "site",
                    "referrer",
                ),
            },
        ),
        (
            "Contact information",
            {
                "fields": (
                    "contact_method",
                    "name",
                    "email",
                )
            },
        ),
    )
    readonly_fields = ["creation_date"]
    list_display = [
        "creation_date",
        "intent",
        "name",
        "contact_method",
        "occupation",
        "income",
        "age",
        "is_married",
        "children_count",
        "site",
        "referrer",
    ]


admin.site.register(Case, CaseAdmin)
