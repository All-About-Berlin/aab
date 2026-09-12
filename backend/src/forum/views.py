from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, F, Max
from django.db.models.functions import Coalesce
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.views.generic.edit import FormMixin

from forum.forms import ReplyForm, ThreadForm
from forum.models import Category, Reply, Thread


def is_user_posting_too_fast(model, user):
    cutoff = timezone.now() - timedelta(minutes=1)
    return model.objects.filter(author=user, creation_date__gte=cutoff).exists()


class VersionedCacheMixin:
    """
    Serves a cached page to anonymous GET and HEAD requests. No cache for logged-in users.

    Cache gets invalidated when get_content_modification_date changes.
    """

    cached_methods = {"GET", "HEAD"}

    def get_content_modification_date(self, request: HttpRequest) -> datetime | None:
        raise NotImplementedError

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.method not in self.cached_methods or request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        content_timestamp = self.get_content_modification_date(request)
        if content_timestamp is None:
            return super().dispatch(request, *args, **kwargs)

        cache_key = f"{type(self).__name__}:{request.get_full_path()}:{content_timestamp.isoformat()}"
        cached_response = cache.get(cache_key)
        if cached_response:
            cached_response["X-Cache"] = "HIT"
            return cached_response

        response = super().dispatch(request, *args, **kwargs)
        if response.status_code == 200:
            if hasattr(response, "render") and not response.is_rendered:
                response.render()
            for cookie in list(response.cookies):
                del response.cookies[cookie]
            cache.set(cache_key, response)
        response["X-Cache"] = "MISS"
        return response


class ForumNewThreadView(LoginRequiredMixin, CreateView):
    form_class = ThreadForm
    template_name = "forum/newThread.html"

    def form_valid(self, form):
        if is_user_posting_too_fast(Thread, self.request.user):
            form.add_error(None, "You are posting too fast. Please wait a bit before creating another thread.")
            return self.form_invalid(form)
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("forum_thread", args=[self.object.pk])


class ForumIndexView(VersionedCacheMixin, ListView):
    template_name = "forum/index.html"
    paginate_by = settings.RESULTS_PER_PAGE

    def get_base_queryset(self):
        queryset = Thread.objects.filter(removal_date__isnull=True)
        category = self.request.GET.get("category")
        if category:
            if category not in Category.values:
                raise Http404
            queryset = queryset.filter(category=category)
        return queryset

    def get_content_modification_date(self, request: HttpRequest) -> datetime | None:
        return (
            self.get_base_queryset().order_by("-modification_date").values_list("modification_date", flat=True).first()
        )

    def get_queryset(self):
        return (
            self.get_base_queryset()
            .annotate(
                last_activity_date=Coalesce(Max("replies__creation_date"), F("creation_date")),
                reply_count=Count("replies"),
            )
            .order_by("-last_activity_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.request.GET.get("category")
        context["category"] = Category(category) if category else None
        return context


class ForumUserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "forum/userProfile.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        threads = user.forum_threads.annotate(
            last_activity_date=Coalesce(Max("replies__creation_date"), F("creation_date")),
            reply_count=Count("replies"),
        ).order_by("-creation_date")
        replies = user.forum_replies.select_related("thread").order_by("-creation_date")
        context["threads"] = threads[: settings.RESULTS_PER_PAGE]
        context["replies"] = replies[: settings.RESULTS_PER_PAGE]
        context["thread_count"] = threads.count()
        context["post_count"] = replies.count()
        return context


class ForumThreadView(VersionedCacheMixin, FormMixin, DetailView):
    model = Thread
    template_name = "forum/thread.html"
    form_class = ReplyForm
    context_object_name = "thread"

    def get_queryset(self):
        return Thread.objects.filter(removal_date__isnull=True).select_related("author")

    def get_content_modification_date(self, request: HttpRequest) -> datetime | None:
        return self.get_queryset().filter(pk=self.kwargs["pk"]).values_list("modification_date", flat=True).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        replies = self.object.replies.select_related("author").order_by("creation_date")
        paginator = Paginator(replies, settings.RESULTS_PER_PAGE)
        try:
            context["page_obj"] = paginator.page(self.kwargs.get("page", 1))
        except EmptyPage:
            raise Http404
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        if is_user_posting_too_fast(Reply, self.request.user):
            form.add_error(None, "You are replying too fast. Please wait a bit before replying again.")
            return self.form_invalid(form)
        reply = form.save(commit=False)
        reply.author = self.request.user
        reply.thread = self.object
        reply.save()
        last_page = Paginator(self.object.replies.all(), settings.RESULTS_PER_PAGE).num_pages
        url = (
            reverse("forum_thread_page", args=[self.object.pk, last_page])
            if last_page > 1
            else reverse("forum_thread", args=[self.object.pk])
        )
        return redirect(f"{url}#reply-{reply.pk}")


class ForumSignupWelcomeView(LoginRequiredMixin, TemplateView):
    template_name = "forum/signup/welcome.html"


class ForumRulesView(TemplateView):
    template_name = "forum/rules.html"
