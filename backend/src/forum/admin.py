from django.contrib import admin
from forum.models import Reply, Thread


class ThreadAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "author", "creation_date"]
    list_filter = ["category"]
    search_fields = ["title", "body", "author__username"]


class ReplyAdmin(admin.ModelAdmin):
    list_display = ["thread", "author", "creation_date"]
    search_fields = ["body", "author__username", "thread__title"]


admin.site.register(Thread, ThreadAdmin)
admin.site.register(Reply, ReplyAdmin)
