from django.core.management.base import BaseCommand

from forum.models import Post, Reply
from search.services import get_forum_search_index, to_post_document, to_reply_document


class Command(BaseCommand):
    help = "Rebuilds the forum search index from scratch"

    def handle(self, *args, **options):
        index = get_forum_search_index()

        index.delete_all_documents()

        posts = [to_post_document(p) for p in Post.objects.filter(removal_date__isnull=True)]
        replies = [
            to_reply_document(r)
            for r in Reply.objects.filter(removal_date__isnull=True, post__removal_date__isnull=True).select_related(
                "post"
            )
        ]

        documents = posts + replies
        if documents:
            index.add_documents(documents)

        self.stdout.write(f"Reindexed {len(posts)} posts and {len(replies)} replies.")
