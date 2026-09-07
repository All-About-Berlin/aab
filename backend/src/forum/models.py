from django.contrib.auth.models import User
from django.db import models


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


class Thread(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="forum_threads")
    title = models.CharField(max_length=200)
    body = models.TextField()
    category = models.CharField(max_length=32, choices=Category, default=Category.OTHER)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True, db_index=True)
    removal_date = models.DateTimeField(null=True, blank=True)
    removal_reason = models.CharField(max_length=32, choices=RemovalReason, blank=True)

    @property
    def removed(self):
        return self.removal_date is not None

    def __str__(self):
        return self.title


class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="forum_replies")
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="replies")
    body = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modification_date = models.DateTimeField(auto_now=True)
    removal_date = models.DateTimeField(null=True, blank=True)
    removal_reason = models.CharField(max_length=32, choices=RemovalReason, blank=True)

    @property
    def removed(self):
        return self.removal_date is not None

    class Meta:
        ordering = ["creation_date"]
