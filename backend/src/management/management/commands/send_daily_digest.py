from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from forms.utils import send_email
from management.admin_site import get_daily_digest_models, get_daily_digest_monitors, get_newsletter_subscribers
from management.models import error_icons, update_monitor
from requests.exceptions import HTTPError
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send a daily digest to the admins"

    def handle(self, *args, **options):
        error_level = logging.INFO

        last_24_hours = timezone.now() - timedelta(hours=24)
        context = {
            "models": [*get_daily_digest_models(last_24_hours), get_newsletter_subscribers(last_24_hours)],
            "monitors": get_daily_digest_monitors(),
        }

        error_level = max(logging.INFO, *[m["status"] for m in context["monitors"]])

        subject = f"{error_icons[error_level]} All About Berlin daily digest"
        recipients = User.objects.filter(is_superuser=True).values_list("email", flat=True)
        body = render_to_string("daily-digest.html", context)

        if settings.DEBUG_EMAILS:
            logger.info("Pretending to send daily digest...")
        else:
            logger.info("Sending daily digest...")

        try:
            send_email(recipients, subject, body)
        except HTTPError as exc:
            logger.exception(f"Could not send daily digest  (HTTP {exc.response.status_code})")
            update_monitor(
                "daily-digest", logging.ERROR, f"Could not send daily digest (HTTP {exc.response.status_code})"
            )
        except Exception as exc:
            logger.exception("Could not send daily digest")
            update_monitor("daily-digest", logging.ERROR, str(exc))
        else:
            logger.info("Sent daily digest.")
            update_monitor("daily-digest", logging.INFO)
