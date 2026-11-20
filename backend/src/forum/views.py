import hashlib
import hmac
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, F, Max
from django.db.models.functions import Coalesce
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseGone
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView, TemplateView, View
from django.views.generic.edit import FormMixin

from forum.forms import PostForm, ReplyForm
from forum.models import Category, Post, PostSubscription, Reply, User


def is_user_posting_too_fast(model, user):
    cutoff = timezone.now() - timedelta(minutes=1)
    return model.objects.filter(author=user, creation_date__gte=cutoff).exists()


def get_unsubscribe_url_token(user: User, post_id: int | None = None) -> str:
    message = f"{user.pk}:{user.date_joined.isoformat()}"
    if post_id is not None:
        message += f":{post_id}"
    return hmac.new(settings.SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()


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


class NewPostView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = "forum/newPost.html"

    def form_valid(self, form):
        if is_user_posting_too_fast(Post, self.request.user):
            form.add_error(None, "You are posting too fast. Please wait a bit before creating another post.")
            return self.form_invalid(form)
        form.instance.author = self.request.user
        response = super().form_valid(form)
        if form.cleaned_data["reply_notifications"]:
            PostSubscription.objects.create(user=self.request.user, post=self.object)
        return response

    def get_success_url(self):
        return reverse("forum_post", args=[self.object.pk])


class IndexView(VersionedCacheMixin, ListView):
    template_name = "forum/index.html"
    paginate_by = settings.RESULTS_PER_PAGE

    def get_base_queryset(self):
        queryset = Post.objects.filter(removal_date__isnull=True)
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


class UserProfileView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = "forum/userProfile.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile_user"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_active and not request.user.is_staff:
            return HttpResponseGone()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        posts = user.forum_posts.annotate(
            last_activity_date=Coalesce(Max("replies__creation_date"), F("creation_date")),
            reply_count=Count("replies"),
        ).order_by("-creation_date")
        replies = user.forum_replies.select_related("post").order_by("-creation_date")
        context["posts"] = posts[: settings.RESULTS_PER_PAGE]
        context["replies"] = replies[: settings.RESULTS_PER_PAGE]
        context["post_count"] = posts.count()
        context["reply_count"] = replies.count()
        return context


class StaffRequiredMixin(LoginRequiredMixin):
    """
    Only mods and admins
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class BanUserView(StaffRequiredMixin, View):
    def post(self, request, username):
        user = get_user_model().objects.filter(username=username).first()
        if user is None:
            raise Http404
        delete_posts = request.POST.get("delete_posts") == "1"
        user.ban(delete_posts=delete_posts)
        return redirect("forum_user", username=username)


class UnbanUserView(StaffRequiredMixin, View):
    def post(self, request, username):
        user = get_user_model().objects.filter(username=username).first()
        if user is None:
            raise Http404
        user.unban()
        return redirect("forum_user", username=username)


class PostView(VersionedCacheMixin, FormMixin, DetailView):
    model = Post
    template_name = "forum/post.html"
    form_class = ReplyForm
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(removal_date__isnull=True).select_related("author")

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
        reply.post = self.object
        reply.save()
        last_page = Paginator(self.object.replies.all(), settings.RESULTS_PER_PAGE).num_pages
        url = (
            reverse("forum_post_page", args=[self.object.pk, last_page])
            if last_page > 1
            else reverse("forum_post", args=[self.object.pk])
        )
        return redirect(f"{url}#reply-{reply.pk}")


class SignupWelcomeView(LoginRequiredMixin, TemplateView):
    template_name = "forum/signup/welcome.html"


class RulesView(TemplateView):
    template_name = "forum/rules.html"


class TurnOffNotificationsView(View):
    """
    The URL requires an unguessable HMAC hash to prevent one user from
    turning off notifications for another.
    """

    template_name = "forum/turnOffAllNotifications.html"

    def get_user_to_unsubscribe(self, params):
        user = get_user_model().objects.filter(username=params["user"]).first()
        if user is None:
            raise KeyError
        if not hmac.compare_digest(get_unsubscribe_url_token(user), params["token"]):
            raise KeyError
        return user

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_user_to_unsubscribe(request.GET)
        except KeyError:
            return HttpResponseBadRequest()
        return render(
            request,
            self.template_name,
            {"user_to_unsubscribe": user, "token": request.GET["token"]},
        )

    def post(self, request, *args, **kwargs):
        try:
            user = self.get_user_to_unsubscribe(request.POST)
        except KeyError:
            return HttpResponseBadRequest()
        user.email_notifications = False
        user.save()
        return render(request, self.template_name, {"user_to_unsubscribe": user})


class UnsubscribeFromPostView(View):
    """
    The URL requires an unguessable HMAC hash to prevent one user from
    unsubscribing another from a post.
    """

    template_name = "forum/unsubscribeFromPost.html"

    def get_user_and_post_to_unsubscribe(self, params, pk):
        post = Post.objects.filter(pk=pk).first()
        user = get_user_model().objects.filter(username=params["user"]).first()
        if user is None or post is None:
            raise KeyError
        if not hmac.compare_digest(get_unsubscribe_url_token(user, post.pk), params["token"]):
            raise KeyError
        return user, post

    def get(self, request, pk, *args, **kwargs):
        try:
            user, post = self.get_user_and_post_to_unsubscribe(request.GET, pk)
        except KeyError:
            return HttpResponseBadRequest()
        return render(
            request,
            self.template_name,
            {
                "user_to_unsubscribe": user,
                "post": post,
                "token": request.GET["token"],
                "is_subscribed": PostSubscription.objects.filter(user=user, post=post).exists(),
            },
        )

    def post(self, request, pk, *args, **kwargs):
        try:
            user, post = self.get_user_and_post_to_unsubscribe(request.POST, pk)
        except KeyError:
            return HttpResponseBadRequest()
        PostSubscription.objects.filter(user=user, post=post).delete()
        return render(
            request,
            self.template_name,
            {"user_to_unsubscribe": user, "post": post, "is_subscribed": False},
        )
