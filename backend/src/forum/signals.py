from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from forum.models import Reply, Thread


@receiver(post_save, sender=Reply)
def bump_thread_modification_date(sender, instance, **kwargs):
    Thread.objects.filter(pk=instance.thread_id).update(modification_date=timezone.now())
