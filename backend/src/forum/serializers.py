from django.contrib.auth import get_user_model
from rest_framework import serializers
from forum.models import Reply, Tag, Thread


User = get_user_model()


class UserInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ThreadSerializer(serializers.ModelSerializer):
    author = UserInlineSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)
    last_activity_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Thread
        fields = ["id", "author", "title", "body", "tags", "creation_date", "last_activity_at"]
        read_only_fields = ["id", "author", "creation_date", "last_activity_at"]


class ReplySerializer(serializers.ModelSerializer):
    author = UserInlineSerializer(read_only=True)

    class Meta:
        model = Reply
        fields = ["id", "author", "thread", "body", "creation_date"]
        read_only_fields = ["id", "author", "thread", "creation_date"]
