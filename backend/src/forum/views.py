from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, F, Max
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.views.generic.edit import FormMixin

from forum.forms import ReplyForm, ThreadForm
from forum.models import Category, Reply, Thread


REPLIES_PER_PAGE = 20
REPLY_RATE_LIMIT = timedelta(minutes=1)
THREAD_RATE_LIMIT = timedelta(minutes=1)


def _get_page(paginator: Paginator, page_number: int):
    try:
        return paginator.page(page_number)
    except EmptyPage:
        raise Http404


class ForumSignupWelcomeView(LoginRequiredMixin, TemplateView):
    template_name = "forum/signup/welcome.html"


class ForumRulesView(TemplateView):
    template_name = "forum/rules.html"


class ForumNewThreadView(LoginRequiredMixin, CreateView):
    form_class = ThreadForm
    template_name = "forum/newThread.html"

    def form_valid(self, form):
        recent_cutoff = timezone.now() - THREAD_RATE_LIMIT
        if Thread.objects.filter(author=self.request.user, creation_date__gte=recent_cutoff).exists():
            form.add_error(None, "You're posting too fast! Please wait a minute before posting again.")
            return self.form_invalid(form)
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("forum_thread", args=[self.object.pk])


class ForumIndexView(ListView):
    template_name = "forum/index.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Thread.objects.annotate(
                last_activity_date=Coalesce(Max("replies__creation_date"), F("creation_date")),
                reply_count=Count("replies"),
            )
            .select_related("author")
            .order_by("-last_activity_date")
        )
        category = self.request.GET.get("category")
        if category:
            if category not in Category.values:
                raise Http404
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.request.GET.get("category")
        context["category"] = Category(category) if category else None
        return context


class ForumUserProfileView(DetailView):
    model = User
    template_name = "forum/userProfile.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        threads = (
            Thread.objects.filter(author=user)
            .annotate(
                last_activity_date=Coalesce(Max("replies__creation_date"), F("creation_date")),
                reply_count=Count("replies"),
            )
            .select_related("author")
            .order_by("-creation_date")
        )
        replies = user.forum_replies.select_related("thread").order_by("-creation_date")
        context["threads"] = threads
        context["replies"] = replies
        context["thread_count"] = threads.count()
        context["post_count"] = replies.count()
        return context


class ForumThreadView(FormMixin, DetailView):
    model = Thread
    template_name = "forum/thread.html"
    form_class = ReplyForm
    pk_url_kwarg = "thread_id"
    context_object_name = "thread"

    def get_queryset(self):
        return Thread.objects.select_related("author")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        replies = self.object.replies.select_related("author").order_by("creation_date")
        paginator = Paginator(replies, REPLIES_PER_PAGE)
        context["page_obj"] = _get_page(paginator, self.kwargs.get("page", 1))
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        recent_cutoff = timezone.now() - REPLY_RATE_LIMIT
        if Reply.objects.filter(author=self.request.user, creation_date__gte=recent_cutoff).exists():
            form.add_error(None, "You're posting too fast! Please wait a minute before replying again.")
            return self.form_invalid(form)
        reply = form.save(commit=False)
        reply.author = self.request.user
        reply.thread = self.object
        reply.save()
        last_page = max(1, -(-self.object.replies.count() // REPLIES_PER_PAGE))
        url = (
            reverse("forum_thread_page", args=[self.object.pk, last_page])
            if last_page > 1
            else reverse("forum_thread", args=[self.object.pk])
        )
        return redirect(f"{url}#reply-{reply.pk}")
