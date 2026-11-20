import re

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

from forum.validators import USERNAME_REGEX


MENTION_REGEX = rf"\B@({USERNAME_REGEX})(?![A-Za-z0-9._\-])"


class User(AbstractUser):
    email_notifications = models.BooleanField(default=True)

    @transaction.atomic
    def ban(self, delete_posts: bool) -> None:
        self.is_active = False
        self.save()
        if delete_posts:
            now = timezone.now()
            self.forum_posts.filter(removal_date__isnull=True).update(
                removal_date=now, removal_reason=RemovalReason.USER_BANNED
            )
            self.forum_replies.filter(removal_date__isnull=True).update(
                removal_date=now, removal_reason=RemovalReason.USER_BANNED
            )

    @transaction.atomic
    def unban(self) -> None:
        self.is_active = True
        self.save()
        self.forum_posts.filter(removal_reason=RemovalReason.USER_BANNED).update(removal_date=None, removal_reason="")
        self.forum_replies.filter(removal_reason=RemovalReason.USER_BANNED).update(removal_date=None, removal_reason="")


class Category(models.TextChoices):
    HOUSING = "housing", "Housing"
    WORK = "work", "Work"
    IMMIGRATION = "immigration", "Immigration"
    LIVING_IN_GERMANY = "living-in-germany", "Life in Germany"
    PERSONAL_FINANCE = "personal-finance", "Personal finance"
    FAMILY_FRIENDS_PETS = "family-friends-pets", "Family, friends, pets"
    HEALTH = "health", "Health"
    WHERE_TO_FIND = "where-to-find", "Where to find..."
    SELF_EMPLOYMENT = "self-employment", "Self-employment"
    OTHER = "other", "Other"


class RemovalReason(models.TextChoices):
    USER_BANNED = "user_banned", "User banned"
    DELETED_BY_MODERATOR = "deleted_by_moderator", "Deleted by moderator"
    DELETED_BY_USER = "deleted_by_user", "Deleted by user"
    OTHER = "other", "Other"


class PostAndReplyQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(removal_date__isnull=True)


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="forum_posts")
    title = models.CharField(max_length=200)
    body = models.TextField()
    category = models.CharField(max_length=32, choices=Category, default=Category.OTHER)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True, db_index=True)
    removal_date = models.DateTimeField(null=True, blank=True)
    removal_reason = models.CharField(max_length=32, choices=RemovalReason, blank=True)

    objects = PostAndReplyQuerySet.as_manager()

    @property
    def removed(self) -> bool:
        return self.removal_date is not None

    @property
    def user_mentions(self) -> set[str]:
        return set(re.findall(MENTION_REGEX, self.body))

    @property
    def post(self) -> "Post":
        return self

    def get_absolute_url(self) -> str:
        return reverse("forum_post", args=[self.pk])

    def __str__(self):
        return self.title


class Reply(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="forum_replies")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="replies")
    body = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modification_date = models.DateTimeField(auto_now=True)
    removal_date = models.DateTimeField(null=True, blank=True)
    removal_reason = models.CharField(max_length=32, choices=RemovalReason, blank=True)

    objects = PostAndReplyQuerySet.as_manager()

    @property
    def removed(self) -> bool:
        return self.removal_date is not None

    @property
    def user_mentions(self) -> set[str]:
        return set(re.findall(MENTION_REGEX, self.body))

    def get_absolute_url(self) -> str:
        return f"{reverse('forum_post', args=[self.post.pk])}#reply-{self.pk}"

    class Meta:
        ordering = ["creation_date"]


class PostSubscription(models.Model):
    """
    Subscribes a user to notifications when someone replies to a post
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_subscriptions")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="subscriptions", db_index=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")
