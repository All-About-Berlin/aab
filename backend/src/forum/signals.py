from django.db.models.signals import post_save
from django.dispatch import receiver

from forum.models import Reply


@receiver(post_save, sender=Reply)
def bump_post_modification_date(sender, instance, **kwargs):
    instance.post.save()  # Trigger a change on the parent post
