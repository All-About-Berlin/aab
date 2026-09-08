from django.core.management.base import BaseCommand
from meilisearch.errors import MeilisearchApiError

from forum.models import Reply, Thread
from search.services import (
    FORUM_INDEX,
    ensure_index,
    get_client,
    get_index,
    reply_document,
    thread_document,
)


class Command(BaseCommand):
    help = "Wipes the forum search index and rebuilds it from the database."

    def handle(self, *args, **options):
        client = get_client()
        try:
            client.delete_index(FORUM_INDEX)
        except MeilisearchApiError as e:
            if e.code != "index_not_found":
                raise

        ensure_index()
        index = get_index()

        threads = [thread_document(t) for t in Thread.objects.filter(removal_date__isnull=True)]
        replies = [
            reply_document(r)
            for r in Reply.objects.filter(removal_date__isnull=True, thread__removal_date__isnull=True).select_related(
                "thread"
            )
        ]

        documents = threads + replies
        if documents:
            index.add_documents(documents)

        self.stdout.write(f"Reindexed {len(threads)} threads and {len(replies)} replies.")
