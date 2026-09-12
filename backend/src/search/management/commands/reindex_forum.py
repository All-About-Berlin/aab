from django.core.management.base import BaseCommand

from forum.models import Reply, Thread
from search.services import get_forum_search_index, to_reply_document, to_thread_document


class Command(BaseCommand):
    help = "Rebuilds the forum search index from scratch"

    def handle(self, *args, **options):
        index = get_forum_search_index()

        index.delete_all_documents()

        threads = [to_thread_document(t) for t in Thread.objects.filter(removal_date__isnull=True)]
        replies = [
            to_reply_document(r)
            for r in Reply.objects.filter(removal_date__isnull=True, thread__removal_date__isnull=True).select_related(
                "thread"
            )
        ]

        documents = threads + replies
        if documents:
            index.add_documents(documents)

        self.stdout.write(f"Reindexed {len(threads)} threads and {len(replies)} replies.")
