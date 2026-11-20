import logging
from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import QuerySet
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from forms.utils import send_email
from forum.models import Post, Reply, User
from forum.views import get_unsubscribe_url_token

logger = logging.getLogger(__name__)


def get_new_replies_to_subscribed_posts(user: User, from_date: datetime) -> QuerySet[Reply]:
    return (
        Reply.objects.visible()
        .filter(post__subscriptions__user=user, creation_date__gte=from_date)
        .exclude(author=user)
        .select_related("post", "author")
        .order_by("-creation_date")
    )


def get_new_posts(from_date: datetime) -> QuerySet[Post]:
    return Post.objects.visible().filter(creation_date__gte=from_date).order_by("-creation_date")


def get_new_mentions(from_date: datetime) -> dict[str, list[Post | Reply]]:
    posts = Post.objects.visible().filter(creation_date__gte=from_date).select_related("author")
    replies = Reply.objects.visible().filter(creation_date__gte=from_date).select_related("post", "author")
    posts_and_replies: list[Post | Reply] = sorted(
        [*posts, *replies],
        key=lambda item: item.creation_date,
        reverse=True,
    )

    mentions_by_user: dict[str, list[Post | Reply]] = {}
    for entry in posts_and_replies:
        for username in entry.user_mentions:
            if entry.author.username == username:
                continue
            mentions_by_user.setdefault(username, []).append(entry)
    return mentions_by_user


def get_unsubscribe_url(user: User) -> str:
    query = urlencode({"user": user.username, "token": get_unsubscribe_url_token(user)})
    return f"{settings.BASE_URL}{reverse('forum_turn_off_notifications')}?{query}"


def group_replies_by_post(replies):
    groups = {}
    for reply in replies:
        group = groups.setdefault(reply.post.pk, {"post": reply.post, "count": 0})
        group["count"] += 1
    return list(groups.values())


def get_digest_email_subject(reply_count, new_post_count, mention_count):
    parts = []
    if reply_count:
        parts.append(f"{reply_count} {'reply' if reply_count == 1 else 'replies'}")
    if new_post_count:
        parts.append(f"{new_post_count} new {'post' if new_post_count == 1 else 'posts'}")
    if mention_count:
        parts.append(f"{mention_count} {'mention' if mention_count == 1 else 'mentions'}")
    return "Yesterday on All About Berlin: " + ", ".join(parts)


class Command(BaseCommand):
    help = "Send the daily forum digest to subscribed users"

    def handle(self, *args, **options):
        from_date = timezone.now() - timedelta(hours=24)
        mentions_by_user = get_new_mentions(from_date)
        new_posts = list(get_new_posts(from_date))

        users = get_user_model().objects.filter(email_notifications=True)
        for user in users:
            try:
                replies = list(get_new_replies_to_subscribed_posts(user, from_date))
                mentions = mentions_by_user.get(user.username, [])

                # If there are no notifications, send no emails
                if not replies and not mentions:
                    continue

                context = {
                    "user": user,
                    "mentions": mentions,
                    "new_replies": group_replies_by_post(replies),
                    "new_posts": new_posts,
                    "unsubscribe_url": get_unsubscribe_url(user),
                }
                subject = get_digest_email_subject(len(replies), len(new_posts), len(mentions))
                body = render_to_string("forum/email/digest.html", context)
                send_email([user.email], subject, body)
            except Exception:
                logger.exception("Could not send forum digest to %s", user.username)
