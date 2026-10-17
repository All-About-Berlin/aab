import logging
from functools import lru_cache

import meilisearch
from django.conf import settings
from django.urls import reverse

from forum.models import Post, Reply


logger = logging.getLogger(__name__)

CONTENT_INDEX = "content"
FORUM_INDEX = "forum"


@lru_cache(maxsize=1)
def get_meili_client():
    return meilisearch.Client(settings.MEILI_URL, settings.MEILI_MASTER_KEY, timeout=2)


def get_forum_search_index():
    return get_meili_client().index(FORUM_INDEX)


def to_post_document(post: Post) -> dict:
    return {
        "id": f"post_{post.id}",
        "post_id": post.id,
        "type": "forum_post",
        "type_rank": 30,
        "title": post.title,
        "description": "",
        "body": post.body,
        "category": post.category,
        "date": int(post.modification_date.timestamp()),
        "url": reverse("forum_post", args=[post.id]),
    }


def to_reply_document(reply: Reply) -> dict:
    post = reply.post
    return {
        "id": f"reply_{reply.id}",
        "post_id": post.id,
        "type": "forum_reply",
        "type_rank": 5,
        "title": post.title,
        "description": "",
        "body": reply.body,
        "category": post.category,
        "date": int(reply.modification_date.timestamp()),
        "url": reverse("forum_post", args=[post.id]) + f"#reply-{reply.id}",
    }


def index_post(post: Post):
    if post.removed:
        remove_post(post.id)
        return
    try:
        get_forum_search_index().add_documents([to_post_document(post)])
    except Exception:
        logger.exception("Failed to index post %s", post.id)


def index_reply(reply: Reply):
    if reply.removed:
        remove_reply(reply.id)
        return
    try:
        get_forum_search_index().add_documents([to_reply_document(reply)])
    except Exception:
        logger.exception("Failed to index reply %s", reply.id)


def remove_post(post_id: int):
    index = get_forum_search_index()
    try:
        index.delete_document(f"post_{post_id}")
        index.delete_documents({"filter": f"post_id = {post_id}"})
    except Exception:
        logger.exception("Failed to remove post %s from index", post_id)


def remove_reply(reply_id: int):
    try:
        get_forum_search_index().delete_document(f"reply_{reply_id}")
    except Exception:
        logger.exception("Failed to remove reply %s from index", reply_id)
