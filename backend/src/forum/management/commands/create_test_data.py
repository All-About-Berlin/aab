import json
import random
from datetime import timedelta
from pathlib import Path

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from forum.models import Reply, Thread


FIXTURE_PATH = Path(__file__).resolve().parent.parent.parent / "fixtures" / "test_data.json"


class Command(BaseCommand):
    help = "Loads forum test data from the committed fixture. Idempotent."

    def handle(self, *args, **options):
        data = json.loads(FIXTURE_PATH.read_text())
        rng = random.Random(0)
        now = timezone.now()

        users = {}
        for u in data["users"]:
            user, _ = User.objects.get_or_create(
                username=u["username"],
                defaults={"email": u["email"]},
            )
            user.set_password(u["username"])
            user.save()
            EmailAddress.objects.update_or_create(
                user=user,
                email=u["email"],
                defaults={"verified": True, "primary": True},
            )
            users[u["username"]] = user

        created_threads = 0
        for t in data["threads"]:
            thread, created = Thread.objects.get_or_create(
                title=t["title"],
                defaults={"author": users[t["author"]], "body": t["body"], "category": t.get("category", "")},
            )
            if not created:
                continue

            thread_date = now - timedelta(seconds=rng.randint(0, 365 * 24 * 60 * 60))
            Thread.objects.filter(pk=thread.pk).update(creation_date=thread_date)

            replies = [
                Reply.objects.create(thread=thread, author=users[r["author"]], body=r["body"])
                for r in t.get("replies", [])
            ]
            for reply in replies:
                reply_date = thread_date + timedelta(seconds=rng.randint(60, 5 * 24 * 60 * 60))
                Reply.objects.filter(pk=reply.pk).update(creation_date=reply_date)
            created_threads += 1

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {len(data['threads'])} threads ({created_threads} newly created).")
        )
