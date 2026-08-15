import json
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from forum.models import Reply, Thread


FIXTURE_PATH = Path(__file__).resolve().parent.parent.parent / "fixtures" / "test_data.json"


class Command(BaseCommand):
    help = "Loads forum test data from the committed fixture. Idempotent."

    def handle(self, *args, **options):
        data = json.loads(FIXTURE_PATH.read_text())

        users = {
            u["username"]: User.objects.get_or_create(
                username=u["username"],
                defaults={"email": u["email"]},
            )[0]
            for u in data["users"]
        }

        created_threads = 0
        for t in data["threads"]:
            thread, created = Thread.objects.get_or_create(
                title=t["title"],
                defaults={"author": users[t["author"]], "body": t["body"], "category": t.get("category", "")},
            )
            if not created:
                continue
            Reply.objects.bulk_create(
                Reply(thread=thread, author=users[r["author"]], body=r["body"]) for r in t.get("replies", [])
            )
            created_threads += 1

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {len(data['threads'])} threads ({created_threads} newly created).")
        )
