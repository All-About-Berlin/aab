import logging
from functools import lru_cache

import meilisearch
from django.conf import settings
from django.urls import reverse

from forum.models import Reply, Thread


logger = logging.getLogger(__name__)

CONTENT_INDEX = "content"
FORUM_INDEX = "forum"


@lru_cache(maxsize=1)
def get_meili_client():
    return meilisearch.Client(settings.MEILI_URL, settings.MEILI_MASTER_KEY, timeout=2)


def get_forum_search_index():
    return get_meili_client().index(FORUM_INDEX)


def to_thread_document(thread: Thread) -> dict:
    return {
        "id": f"thread_{thread.id}",
        "thread_id": thread.id,
        "type": "forum_thread",
        "type_rank": 30,
        "title": thread.title,
        "description": "",
        "body": thread.body,
        "category": thread.category,
        "date": int(thread.modification_date.timestamp()),
        "url": reverse("forum_thread", args=[thread.id]),
    }


def to_reply_document(reply: Reply) -> dict:
    thread = reply.thread
    return {
        "id": f"reply_{reply.id}",
        "thread_id": thread.id,
        "type": "forum_reply",
        "type_rank": 5,
        "title": thread.title,
        "description": "",
        "body": reply.body,
        "category": thread.category,
        "date": int(reply.modification_date.timestamp()),
        "url": reverse("forum_thread", args=[thread.id]) + f"#reply-{reply.id}",
    }


def index_thread(thread: Thread):
    if thread.removed:
        remove_thread(thread.id)
        return
    try:
        get_forum_search_index().add_documents([to_thread_document(thread)])
    except Exception:
        logger.exception("Failed to index thread %s", thread.id)


def index_reply(reply: Reply):
    if reply.removed:
        remove_reply(reply.id)
        return
    try:
        get_forum_search_index().add_documents([to_reply_document(reply)])
    except Exception:
        logger.exception("Failed to index reply %s", reply.id)


def remove_thread(thread_id: int):
    index = get_forum_search_index()
    try:
        index.delete_document(f"thread_{thread_id}")
        index.delete_documents({"filter": f"thread_id = {thread_id}"})
    except Exception:
        logger.exception("Failed to remove thread %s from index", thread_id)


def remove_reply(reply_id: int):
    try:
        get_forum_search_index().delete_document(f"reply_{reply_id}")
    except Exception:
        logger.exception("Failed to remove reply %s from index", reply_id)
