import logging
from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Count, F, Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from forms.utils import send_email
from forum.models import Post, PostSubscription, Reply, User
from forum.views import get_unsubscribe_url_token
from management.models import update_monitor

logger = logging.getLogger(__name__)


def get_new_replies_by_user(since_date: datetime) -> dict[str, list[dict]]:
    subscriptions_with_new_replies = (
        PostSubscription.objects.filter(user__email_notifications=True)
        .annotate(
            new_reply_count=Count(
                "post__replies",
                filter=Q(
                    post__replies__creation_date__gte=since_date,
                    post__replies__removal_date__isnull=True,
                )
                & ~Q(post__replies__author=F("user")),
            )
        )
        .filter(new_reply_count__gt=0)
        .select_related("user", "post")
        .order_by("-post__creation_date")
    )
    replies_by_user: dict[str, list[dict]] = {}
    for subscription in subscriptions_with_new_replies:
        replies_by_user.setdefault(subscription.user.username, []).append(
            {
                "post": subscription.post,
                "count": subscription.new_reply_count,
                "unsubscribe_url": get_post_unsubscribe_url(subscription.user, subscription.post),
            }
        )
    return replies_by_user


def get_new_posts(since_date: datetime) -> list[Post]:
    return list(Post.objects.visible().filter(creation_date__gte=since_date).order_by("-creation_date"))


def get_new_mentions_by_user(since_date: datetime) -> dict[str, list[Post | Reply]]:
    new_posts = Post.objects.visible().filter(creation_date__gte=since_date).select_related("author")
    new_replies = Reply.objects.visible().filter(creation_date__gte=since_date).select_related("post", "author")
    new_posts_and_replies: list[Post | Reply] = sorted(
        [*new_posts, *new_replies],
        key=lambda item: item.creation_date,
        reverse=True,
    )

    mentions_by_user: dict[str, list[Post | Reply]] = {}
    for mention in new_posts_and_replies:
        for username in mention.user_mentions:
            if mention.author.username == username:
                continue
            mentions_by_user.setdefault(username, []).append(mention)
    return mentions_by_user


def get_unsubscribe_url(user: User) -> str:
    query = urlencode({"user": user.username, "token": get_unsubscribe_url_token(user)})
    return f"{settings.BASE_URL}{reverse('forum_turn_off_notifications')}?{query}"


def get_post_unsubscribe_url(user: User, post: Post) -> str:
    query = urlencode({"user": user.username, "token": get_unsubscribe_url_token(user, post.pk)})
    return f"{settings.BASE_URL}{reverse('forum_unsubscribe_from_post', args=[post.pk])}?{query}"


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
        try:
            since_date = timezone.now() - timedelta(hours=24)
            mentions_by_user = get_new_mentions_by_user(since_date)
            replies_by_user = get_new_replies_by_user(since_date)
            new_posts = get_new_posts(since_date)

            users_to_notify = get_user_model().objects.filter(
                is_active=True,
                email_notifications=True,
                username__in=replies_by_user.keys() | mentions_by_user.keys(),
            )

            sent_count = 0
            failed_count = 0
            email_queue = []
            for user in users_to_notify:
                try:
                    new_replies = replies_by_user.get(user.username, [])
                    new_mentions = mentions_by_user.get(user.username, [])

                    context = {
                        "user": user,
                        "new_mentions": new_mentions,
                        "new_replies": new_replies,
                        "new_posts": new_posts,
                        "unsubscribe_url": get_unsubscribe_url(user),
                    }
                    reply_count = sum(summary["count"] for summary in new_replies)
                    subject = get_digest_email_subject(reply_count, len(new_posts), len(new_mentions))
                    body = render_to_string("forum/email/digest.html", context)
                    email_queue.append((user, subject, body))
                except Exception:
                    logger.exception("Could not prepare forum digest email for %s", user.username)
                    failed_count += 1

            for user, subject, body in email_queue:
                try:
                    send_email([user.email], subject, body)
                    sent_count += 1
                except Exception:
                    logger.exception("Could not send forum digest email to %s", user.username)
                    failed_count += 1

            if failed_count and not sent_count:
                level = logging.ERROR
            elif failed_count:
                level = logging.WARNING
            else:
                level = logging.INFO
            update_monitor("forum-digest", level, f"{sent_count} sent, {failed_count} failed")
        except Exception as exc:
            logger.exception("Forum digest command failed")
            update_monitor("forum-digest", logging.ERROR, str(exc))
