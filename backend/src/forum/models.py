from django.contrib.auth.models import User
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Thread(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="forum_threads")
    title = models.CharField(max_length=200)
    body = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, related_name="threads")
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
