from allauth.account.adapter import DefaultAccountAdapter
from django.template.loader import render_to_string

from forms.utils import send_email


class ForumAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        subject = render_to_string(f"{template_prefix}_subject.txt", context).strip()
        body = render_to_string(f"{template_prefix}_message.html", context)
        send_email(recipients=[email], subject=subject, body=body)
