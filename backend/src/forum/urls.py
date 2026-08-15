from django.urls import include, path
from forum.views import ReplyViewSet, ThreadViewSet
from rest_framework import routers


router = routers.DefaultRouter(trailing_slash=False)
router.register("threads", ThreadViewSet, basename="thread")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "threads/<int:thread_id>/replies",
        ReplyViewSet.as_view({"get": "list", "post": "create"}),
    ),
]
