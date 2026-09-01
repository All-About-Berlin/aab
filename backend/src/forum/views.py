from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, F, Max
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from forum.forms import ReplyForm
from forum.models import Category, Thread


THREADS_PER_PAGE = 20
REPLIES_PER_PAGE = 20


def _get_page(paginator: Paginator, page_number: int):
    try:
        return paginator.page(page_number)
    except EmptyPage:
        raise Http404


@login_required
def forum_signup_welcome(request):
    return render(request, "forum/signup/welcome.html")


def forum_rules(request):
    return render(request, "forum/rules.html")


def forum_index(request, page: int = 1):
    threads = (
        Thread.objects.annotate(
            last_activity_at=Coalesce(Max("replies__creation_date"), F("creation_date")),
            reply_count=Count("replies"),
        )
        .select_related("author")
        .order_by("-last_activity_at")
    )
    category = request.GET.get("category")
    if category:
        if category not in Category.values:
            raise Http404
        threads = threads.filter(category=category)
    paginator = Paginator(threads, THREADS_PER_PAGE)
    page_obj = _get_page(paginator, page)

    return render(
        request,
        "forum/index.html",
        {
            "page_obj": page_obj,
            "paginator": paginator,
            "base_url": reverse("forum_index"),
            "category": Category(category) if category else None,
        },
    )


def forum_user_profile(request, username: str):
    user = get_object_or_404(User, username=username)
    threads = Thread.objects.filter(author=user).select_related("author").order_by("-creation_date")
    replies = user.forum_replies.select_related("thread").order_by("-creation_date")
    thread_count = threads.count()
    post_count = replies.count()

    return render(
        request,
        "forum/userProfile.html",
        {
            "profile_user": user,
            "threads": threads,
            "replies": replies,
            "thread_count": thread_count,
            "post_count": post_count,
        },
    )


def forum_thread(request, thread_id: int, page: int = 1):
    thread = get_object_or_404(Thread.objects.select_related("author"), pk=thread_id)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("account_login")
        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.author = request.user
            reply.thread = thread
            reply.save()
            last_page = max(1, -(-thread.replies.count() // REPLIES_PER_PAGE))
            url = (
                reverse("forum_thread_page", args=[thread.pk, last_page])
                if last_page > 1
                else reverse("forum_thread", args=[thread.pk])
            )
            return redirect(f"{url}#reply-{reply.pk}")
    else:
        reply_form = ReplyForm()

    replies = thread.replies.select_related("author").order_by("creation_date")
    paginator = Paginator(replies, REPLIES_PER_PAGE)
    page_obj = _get_page(paginator, page)

    return render(
        request,
        "forum/thread.html",
        {
            "thread": thread,
            "page_obj": page_obj,
            "paginator": paginator,
            "base_url": reverse("forum_thread", args=[thread.pk]),
            "reply_form": reply_form,
        },
    )
