import logging
from functools import lru_cache

import meilisearch
from django.conf import settings
from django.urls import reverse

from forum.models import Reply, Thread


logger = logging.getLogger(__name__)

FORUM_INDEX = "forum"
SEARCHABLE_ATTRIBUTES = ["title", "body"]
FILTERABLE_ATTRIBUTES = ["category", "thread_id"]
SORTABLE_ATTRIBUTES = ["creation_date"]


@lru_cache(maxsize=1)
def get_client():
    return meilisearch.Client(settings.MEILI_URL, settings.MEILI_MASTER_KEY, timeout=2)


def get_index():
    return get_client().index(FORUM_INDEX)


def ensure_index():
    client = get_client()
    client.create_index(FORUM_INDEX, {"primaryKey": "id"})
    index = client.index(FORUM_INDEX)
    index.update_searchable_attributes(SEARCHABLE_ATTRIBUTES)
    index.update_filterable_attributes(FILTERABLE_ATTRIBUTES)
    index.update_sortable_attributes(SORTABLE_ATTRIBUTES)


def thread_document(thread: Thread) -> dict:
    return {
        "id": f"thread:{thread.id}",
        "thread_id": thread.id,
        "title": thread.title,
        "body": thread.body,
        "category": thread.category,
        "creation_date": int(thread.creation_date.timestamp()),
        "url": reverse("forum_thread", args=[thread.id]),
    }


def reply_document(reply: Reply) -> dict:
    thread = reply.thread
    return {
        "id": f"reply:{reply.id}",
        "thread_id": thread.id,
        "title": thread.title,
        "body": reply.body,
        "category": thread.category,
        "creation_date": int(reply.creation_date.timestamp()),
        "url": reverse("forum_thread", args=[thread.id]) + f"#reply-{reply.id}",
    }


def index_thread(thread: Thread):
    if thread.removed:
        remove_thread(thread.id)
        return
    try:
        get_index().add_documents([thread_document(thread)])
    except Exception:
        logger.exception("Failed to index thread %s", thread.id)


def index_reply(reply: Reply):
    if reply.removed:
        remove_reply(reply.id)
        return
    try:
        get_index().add_documents([reply_document(reply)])
    except Exception:
        logger.exception("Failed to index reply %s", reply.id)


def remove_thread(thread_id: int):
    index = get_index()
    try:
        index.delete_document(f"thread:{thread_id}")
        index.delete_documents({"filter": f"thread_id = {thread_id}"})
    except Exception:
        logger.exception("Failed to remove thread %s from index", thread_id)


def remove_reply(reply_id: int):
    try:
        get_index().delete_document(f"reply:{reply_id}")
    except Exception:
        logger.exception("Failed to remove reply %s from index", reply_id)
