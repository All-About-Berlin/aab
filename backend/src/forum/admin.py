from django.contrib import admin
from forum.models import Reply, Tag, Thread


class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


class ThreadAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "creation_date"]
    search_fields = ["title", "body", "author__username"]


class ReplyAdmin(admin.ModelAdmin):
    list_display = ["thread", "author", "creation_date"]
    search_fields = ["body", "author__username", "thread__title"]


admin.site.register(Tag, TagAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Reply, ReplyAdmin)
