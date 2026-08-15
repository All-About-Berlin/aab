from pathlib import Path

from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, F, Max
from django.db.models.functions import Coalesce
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from forum.models import Thread


SHELL_PATH = Path("/var/frontend-output/forum/shell.html")
SHELL_MARKER = "<!--FORUM_CONTENT-->"
THREADS_PER_PAGE = 20
REPLIES_PER_PAGE = 20


def _render(content_html: str) -> HttpResponse:
    shell = SHELL_PATH.read_text()
    return HttpResponse(shell.replace(SHELL_MARKER, content_html))


def _get_page(paginator: Paginator, page_number: int):
    try:
        return paginator.page(page_number)
    except EmptyPage:
        raise Http404


def forum_index(request, page: int = 1):
    threads = (
        Thread.objects.annotate(
            last_activity_at=Coalesce(Max("replies__creation_date"), F("creation_date")),
            reply_count=Count("replies"),
        )
        .select_related("author")
        .order_by("-last_activity_at")
    )
    paginator = Paginator(threads, THREADS_PER_PAGE)
    page_obj = _get_page(paginator, page)

    content = render_to_string(
        "forum/index.html",
        {"page_obj": page_obj, "paginator": paginator, "base_url": "/forum"},
        request=request,
    )
    return _render(content)


def forum_thread(request, thread_id: int, page: int = 1):
    thread = get_object_or_404(Thread.objects.select_related("author"), pk=thread_id)
    replies = thread.replies.select_related("author").order_by("creation_date")
    paginator = Paginator(replies, REPLIES_PER_PAGE)
    page_obj = _get_page(paginator, page)

    content = render_to_string(
        "forum/thread.html",
        {
            "thread": thread,
            "page_obj": page_obj,
            "paginator": paginator,
            "base_url": f"/forum/{thread.pk}",
        },
        request=request,
    )
    return _render(content)
