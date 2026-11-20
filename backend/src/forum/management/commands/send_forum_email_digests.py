import logging
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from forms.utils import send_email
from forum.models import Post, PostSubscription, Reply, User
from forum.views import get_unsubscribe_url_token
from management.models import update_monitor

logger = logging.getLogger(__name__)


def get_new_replies_by_user(since_date: datetime) -> dict[str, list[tuple[Post, list[Reply]]]]:
    subscriptions_with_updates = (
        PostSubscription.objects.filter(
            user__is_active=True,  # Banned users don't get emails
            user__email_notifications=True,
            post__replies__creation_date__gte=since_date,
            post__replies__removal_date__isnull=True,
        )
        .select_related("user", "post")
        .distinct()
    )

    subscribed_post_ids = {subscription.post_id for subscription in subscriptions_with_updates}
    recent_replies_by_post_id: dict[int, list[Reply]] = {}
    for reply in Reply.objects.visible().filter(creation_date__gte=since_date, post_id__in=subscribed_post_ids):
        recent_replies_by_post_id.setdefault(reply.post_id, []).append(reply)

    new_replies_by_user: dict[str, list[tuple[Post, list[Reply]]]] = {}
    for subscription in subscriptions_with_updates:
        replies = [
            reply
            for reply in recent_replies_by_post_id.get(subscription.post_id, [])
            if reply.author_id != subscription.user_id
        ]
        if replies:
            new_replies_by_user.setdefault(subscription.user.username, []).append((subscription.post, replies))
    return new_replies_by_user


def get_new_mentions_by_user(since_date: datetime) -> dict[str, list[Post | Reply]]:
    new_posts = (
        Post.objects.visible().filter(creation_date__gte=since_date, body__contains="@").select_related("author")
    )
    new_replies = (
        Reply.objects.visible()
        .filter(creation_date__gte=since_date, body__contains="@")
        .select_related("post", "author")
    )
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


def get_digest_email_subject(mention_count: int, reply_count: int, post_count: int) -> str:
    parts = []
    if mention_count:
        parts.append(f"{mention_count} {'mention' if mention_count == 1 else 'mentions'}")
    if reply_count:
        parts.append(f"{reply_count} {'reply' if reply_count == 1 else 'replies'}")
    if post_count:
        parts.append(f"{post_count} {'post' if post_count == 1 else 'posts'}")
    return "Recently on the All About Berlin forum: " + ", ".join(parts)


def get_unsubscribe_url(user: User) -> str:
    query = urlencode({"user": user.username, "token": get_unsubscribe_url_token(user)})
    return f"{settings.BASE_URL}{reverse('forum_turn_off_notifications')}?{query}"


def get_post_unsubscribe_url(user: User, post: Post) -> str:
    query = urlencode({"user": user.username, "token": get_unsubscribe_url_token(user, post.pk)})
    return f"{settings.BASE_URL}{reverse('forum_unsubscribe_from_post', args=[post.pk])}?{query}"


class Command(BaseCommand):
    help = "Send the forum digest to subscribed users"

    def get_user_digest_email(
        self,
        user: User,
        since_date: datetime,
        mentions_by_user: dict[str, list[Post | Reply]],
        replies_by_user: dict[str, list[tuple[Post, list[Reply]]]],
        new_posts: list[Post],
    ) -> tuple[str, str] | None:
        since = max(user.last_email_digest_date or user.date_joined, since_date)
        hit_cap = since == since_date

        user_mentions = [m for m in mentions_by_user.get(user.username, []) if m.creation_date >= since]
        user_replies = []
        for post, replies in replies_by_user.get(user.username, []):
            count = sum(1 for reply in replies if reply.creation_date >= since)
            if count:
                user_replies.append(
                    {
                        "post": post,
                        "count": count,
                        "unsubscribe_url": get_post_unsubscribe_url(user, post),
                    }
                )
        user_new_posts = [post for post in new_posts if post.creation_date >= since]

        should_send = bool(user_mentions or user_replies) or (hit_cap and user_new_posts)
        if not should_send:
            return None

        context = {
            "user": user,
            "new_mentions": user_mentions,
            "new_replies": user_replies,
            "new_posts": user_new_posts,
            "unsubscribe_url": get_unsubscribe_url(user),
        }
        reply_count = sum(item["count"] for item in user_replies)
        subject = get_digest_email_subject(len(user_mentions), reply_count, len(user_new_posts))
        body = render_to_string("forum/email/digest.html", context)
        return subject, body

    def send_digest_emails(self, emails_to_send: list[tuple[User, str, str]]) -> tuple[list[int], int]:
        sent_user_ids = []
        failed_count = 0
        with requests.Session() as session:
            for user, subject, body in emails_to_send:
                try:
                    send_email([user.email], subject, body, session=session)
                    sent_user_ids.append(user.pk)
                except Exception:
                    logger.exception("Could not send forum digest email to %s", user.username)
                    failed_count += 1
        return sent_user_ids, failed_count

    def handle(self, *args, **options):
        try:
            now = timezone.now()
            since_date = now - timedelta(days=7)

            mentions_by_user = get_new_mentions_by_user(since_date)
            replies_by_user = get_new_replies_by_user(since_date)
            new_posts = list(Post.objects.visible().filter(creation_date__gte=since_date).order_by("-creation_date"))

            usernames_with_activity = set(mentions_by_user.keys()) | set(replies_by_user.keys())

            # Include users with activity, plus dormant users (last digest 7+ days ago, or never got one
            # and joined 7+ days ago) when there are new posts to show them.
            candidate_filter = Q(username__in=usernames_with_activity)
            if new_posts:
                candidate_filter |= Q(last_email_digest_date__lte=since_date) | Q(
                    last_email_digest_date__isnull=True, date_joined__lte=since_date
                )

            users_to_notify = (
                get_user_model().objects.filter(is_active=True, email_notifications=True).filter(candidate_filter)
            )

            emails_to_send = []
            for user in users_to_notify:
                digest = self.get_user_digest_email(user, since_date, mentions_by_user, replies_by_user, new_posts)
                if digest:
                    subject, body = digest
                    emails_to_send.append((user, subject, body))

            sent_user_ids, failed_count = self.send_digest_emails(emails_to_send)
            get_user_model().objects.filter(pk__in=sent_user_ids).update(last_email_digest_date=now)

            sent_count = len(sent_user_ids)
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
