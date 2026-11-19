from allauth.account import views as allauth_views
from django.urls import path, re_path

from forum import views


urlpatterns = [
    path("forum", views.IndexView.as_view(), name="forum_index"),
    path("forum/page-<int:page>", views.IndexView.as_view(), name="forum_index_page"),
    path("forum/signup/welcome", views.SignupWelcomeView.as_view(), name="forum_signup_welcome"),
    path("forum/rules", views.RulesView.as_view(), name="forum_rules"),
    path("forum/login", allauth_views.login, name="account_login"),
    path("forum/logout", allauth_views.logout, name="account_logout"),
    path("forum/signup", allauth_views.signup, name="account_signup"),
    path("forum/confirm-email", allauth_views.email_verification_sent, name="account_email_verification_sent"),
    path("forum/confirm-email/<key>", allauth_views.confirm_email, name="account_confirm_email"),
    path("forum/password/reset", allauth_views.password_reset, name="account_reset_password"),
    path("forum/password/reset/done", allauth_views.password_reset_done, name="account_reset_password_done"),
    re_path(
        r"^forum/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)$",
        allauth_views.password_reset_from_key,
        name="account_reset_password_from_key",
    ),
    path(
        "forum/password/reset/key/done",
        allauth_views.password_reset_from_key_done,
        name="account_reset_password_from_key_done",
    ),
    path("forum/users/<str:username>", views.UserProfileView.as_view(), name="forum_user"),
    path("forum/new", views.NewPostView.as_view(), name="forum_new_post"),
    path("forum/unsubscribe/all", views.TurnOffNotificationsView.as_view(), name="forum_turn_off_notifications"),
    path("forum/<int:pk>", views.PostView.as_view(), name="forum_post"),
    path("forum/<int:pk>/page-<int:page>", views.PostView.as_view(), name="forum_post_page"),
]
