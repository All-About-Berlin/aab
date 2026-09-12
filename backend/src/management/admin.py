from django.contrib import admin
from management.models import Monitor, error_icons


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ["key", "name", "status_display", "last_updated"]

    def status_display(self, obj):
        return error_icons[obj.status]

    status_display.admin_order_field = "status"  # allow column sorting
    status_display.short_description = "Status"
