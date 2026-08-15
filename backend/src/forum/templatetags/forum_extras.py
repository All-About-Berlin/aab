from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def short_date(value):
    """Short date for lists: time if today, month + day, plus year if not the current year."""
    if value is None:
        return ""
    local = timezone.localtime(value)
    today = timezone.localdate()
    if local.date() == today:
        return local.strftime("%b %-d, %H:%M")
    if local.year == today.year:
        return local.strftime("%b %-d")
    return local.strftime("%b %-d, %Y")


@register.filter
def short_datetime(value):
    """Short datetime for a single thread: time if today, drop year if current year."""
    if value is None:
        return ""
    local = timezone.localtime(value)
    today = timezone.localdate()
    if local.date() == today:
        return local.strftime("%b %-d, %H:%M")
    if local.year == today.year:
        return local.strftime("%b %-d")
    return local.strftime("%b %-d, %Y")
