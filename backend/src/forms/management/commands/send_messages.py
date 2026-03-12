from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from forms.models import MessageStatus, ScheduledMessage
from django.utils import timezone
from forms.utils import send_email
from management.models import update_monitor
from requests.exceptions import HTTPError
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send all scheduled messages"

    def handle(self, *args, **options):
        if settings.DEBUG_EMAILS:
            logger.info("Pretending to send scheduled messages...")
        else:
            logger.info("Sending scheduled messages...")

            if not settings.DEBUG and not settings.MAILGUN_API_KEY:
                raise Exception("MAILGUN_API_KEY is not set")

        successes = 0
        failures = 0

        scheduled_message_models = [model for model in apps.get_models() if issubclass(model, ScheduledMessage)]

        for model in scheduled_message_models:
            scheduled_messages = model.objects.filter(status=MessageStatus.SCHEDULED, delivery_date__lte=timezone.now())
            for message in scheduled_messages:
                try:
                    if settings.DEBUG:
                        if settings.DEBUG_EMAILS:
                            logger.info(
                                "SENDING EMAIL MESSAGE\n"
                                f"To: {', '.join(message.recipients)}\n"
                                f"Reply-To: {message.reply_to}\n"
                                f"Subject: {message.subject}\n"
                                f"Body: \n{message.get_body()}"
                            )
                        else:
                            logger.info(f"Pretending to send 1 message ({message.__class__.__name__})")
                    else:
                        send_email(message.recipients, message.subject, message.get_body(), message.reply_to)
                    message.status = MessageStatus.SENT
                    successes += 1
                except HTTPError as exc:
                    logger.exception(f"Could not send scheduled message (HTTP {exc.response.status_code})")
                    if 400 <= exc.response.status_code < 500:
                        message.status = MessageStatus.FAILED
                except:
                    logger.exception(f"Could not send scheduled message (#{message.id}, {message.__class__.__name__})")
                    failures += 1
                message.save()

        level = logging.ERROR if failures else logging.INFO
        logger.log(level, f"Sent scheduled messages. {successes} sent, {failures} failed.")
        update_monitor("send-messages", level, f"{successes} sent, {failures} failed.")
