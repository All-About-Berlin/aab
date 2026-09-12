from django.contrib import admin
from forum.models import Reply, Thread


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "author", "creation_date", "removal_date"]
    list_filter = ["category", "removal_reason"]
    search_fields = ["title", "body", "author__username"]
    fields = ["author", "title", "body", "category", "removal_date", "removal_reason"]


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ["thread", "author", "creation_date", "removal_date"]
    list_filter = ["removal_reason"]
    search_fields = ["body", "author__username", "thread__title"]
    fields = ["thread", "author", "body", "removal_date", "removal_reason"]
