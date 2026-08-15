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


class Thread(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="forum_threads")
    title = models.CharField(max_length=200)
    body = models.TextField()
    category = models.CharField(max_length=32, choices=Category, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="forum_replies")
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="replies")
    body = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["creation_date"]
