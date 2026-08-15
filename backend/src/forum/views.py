from django.db.models import F, Max
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from forum.models import Reply, Thread
from forum.serializers import ReplySerializer, ThreadSerializer
from rest_framework import mixins, permissions, viewsets


class ThreadViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Thread.objects.annotate(
            last_activity_at=Coalesce(Max("replies__creation_date"), F("creation_date"))
        ).order_by("-last_activity_at")

        tag = self.request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(tags=tag)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ReplyViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ReplySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_thread(self):
        return get_object_or_404(Thread, pk=self.kwargs["thread_id"])

    def get_queryset(self):
        return Reply.objects.filter(thread=self.get_thread())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, thread=self.get_thread())
