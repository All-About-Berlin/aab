from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from forum.models import Reply, Thread
from search.services import index_reply, index_thread, remove_reply, remove_thread


@receiver(post_save, sender=Thread)
def on_thread_saved(sender, instance, **kwargs):
    transaction.on_commit(lambda: index_thread(instance))


@receiver(post_delete, sender=Thread)
def on_thread_deleted(sender, instance, **kwargs):
    thread_id = instance.id
    transaction.on_commit(lambda: remove_thread(thread_id))


@receiver(post_save, sender=Reply)
def on_reply_saved(sender, instance, **kwargs):
    transaction.on_commit(lambda: index_reply(instance))


@receiver(post_delete, sender=Reply)
def on_reply_deleted(sender, instance, **kwargs):
    reply_id = instance.id
    transaction.on_commit(lambda: remove_reply(reply_id))
