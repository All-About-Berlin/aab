from collections import OrderedDict
from datetime import datetime, time
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from management.models import Monitor, error_icons
from typing import Any
import requests


def get_admin_instance_url(model_instance) -> str | None:
    try:
        return settings.BASE_URL + reverse(
            "admin:%s_%s_change" % (model_instance._meta.app_label, model_instance._meta.model_name),
            args=[model_instance.pk],
        )
    except NoReverseMatch:
        return None


def get_admin_url(model) -> str | None:
    try:
        return settings.BASE_URL + reverse("admin:%s_%s_changelist" % (model._meta.app_label, model._meta.model_name))
    except NoReverseMatch:
        return None


def get_daily_digest_models(since: datetime) -> list[dict[str, Any]]:
    return [
        {
            "name": model._meta.verbose_name_plural.capitalize(),
            "url": get_admin_url(model),
            "last_created": (
                latest.creation_date if (latest := model.objects.order_by("-creation_date").first()) else None
            ),
            "instances": [
                {
                    "name": str(instance),
                    "url": get_admin_instance_url(instance),
                    "fields": OrderedDict(
                        [
                            (instance._meta.get_field(field).verbose_name.capitalize(), getattr(instance, field, None))
                            for field in instance.daily_digest_fields
                        ]
                    ),
                }
                for instance in model.objects.filter(creation_date__gte=since)
            ],
        }
        for model in apps.get_models()
        if hasattr(model, "daily_digest_fields")
    ]


def get_newsletter_subscribers(since: datetime) -> dict[str, Any]:
    response = requests.get(
        "https://api.buttondown.com/v1/subscribers",
        headers={
            "Authorization": f"Token {settings.BUTTONDOWN_API_KEY}",
            "Content-Type": "application/json",
        },
        timeout=10,
    )
    response.raise_for_status()
    results = response.json()["results"]

    for result in results:
        result["creation_date"] = datetime.fromisoformat(result["creation_date"].replace("Z", "+00:00")).astimezone()
    last_created = max([r["creation_date"] for r in results])
    return {
        "name": "Newsletter subscribers",
        "url": "https://buttondown.com/subscribers",
        "last_created": last_created,
        "instances": [
            {
                "name": result["email_address"],
                "url": None,
                "fields": {},
            }
            for result in results
            if result["creation_date"] >= since
        ],
    }


def get_daily_digest_monitors() -> list[dict[str, Any]]:
    return [
        {
            "icon": error_icons[monitor.status],
            "status": monitor.status,
            "name": monitor.name or monitor.key,
            "last_updated": monitor.last_updated,
            "message": monitor.last_update.message,
            "url": reverse(
                "admin:%s_%s_change" % (monitor._meta.app_label, monitor._meta.model_name), args=[monitor.pk]
            ),
        }
        for monitor in Monitor.objects.all()
    ]


class CustomAdminSite(admin.AdminSite):
    site_header = "All About Berlin"
    site_title = "Dashboard"
    index_title = "Overview"
    index_template = "admin/dashboard.html"

    def index(self, request, extra_context=None):
        midnight = datetime.combine(timezone.now().date(), time.min, tzinfo=timezone.now().tzinfo)
        extra_context = extra_context or {}
        extra_context["models"] = [*get_daily_digest_models(midnight), get_newsletter_subscribers(midnight)]
        extra_context["monitors"] = get_daily_digest_monitors()

        return super().index(request, extra_context=extra_context)
