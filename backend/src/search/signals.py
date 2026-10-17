from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from forum.models import Post, Reply
from search.services import index_post, index_reply, remove_post, remove_reply


@receiver(post_save, sender=Post)
def on_post_saved(sender, instance, **kwargs):
    transaction.on_commit(lambda: index_post(instance))


@receiver(post_delete, sender=Post)
def on_post_deleted(sender, instance, **kwargs):
    post_id = instance.id
    transaction.on_commit(lambda: remove_post(post_id))


@receiver(post_save, sender=Reply)
def on_reply_saved(sender, instance, **kwargs):
    transaction.on_commit(lambda: index_reply(instance))


@receiver(post_delete, sender=Reply)
def on_reply_deleted(sender, instance, **kwargs):
    reply_id = instance.id
    transaction.on_commit(lambda: remove_reply(reply_id))
