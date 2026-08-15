from django.urls import path

from forum import views


urlpatterns = [
    path("forum", views.forum_index, name="forum-index"),
    path("forum/page-<int:page>", views.forum_index, name="forum-index-page"),
    path("forum/<int:thread_id>", views.forum_thread, name="forum-thread"),
    path("forum/<int:thread_id>/page-<int:page>", views.forum_thread, name="forum-thread-page"),
]
