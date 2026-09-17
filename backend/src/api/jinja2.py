"""Jinja2 environment for the Django Jinja2 template backend.

Sets StrictUndefined so template bugs raise instead of silently rendering as
empty strings, and registers the filters and globals the templates need.
"""

import re
from urllib.parse import urlparse

import markdown
import nh3
from django.conf import settings
from django.contrib.humanize.templatetags import humanize
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template import defaultfilters
from django.template.backends.jinja2 import Jinja2
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PrefixLoader, StrictUndefined
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class Jinja2Templates(Jinja2):
    """Look for templates in each app's `templates/` directory (Django's convention)."""

    app_dirname = "templates"


SAFE_MARKDOWN_TAGS = {"p", "br", "strong", "em", "a", "ul", "ol", "li", "blockquote", "code", "pre"}
SAFE_MARKDOWN_ATTRIBUTES = {"a": {"href", "rel"}}


def is_external_href(href: str) -> bool:
    parsed = urlparse(href)
    if not parsed.scheme or not parsed.netloc:
        return False
    return parsed.hostname not in settings.ALLOWED_HOSTS


class NoFollowExternalLinkProcessor(Treeprocessor):
    def run(self, root):
        for anchor in root.iter("a"):
            href = anchor.get("href", "")
            if is_external_href(href):
                anchor.set("rel", "nofollow ugc noopener")


class NoFollowExternalLinkExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(NoFollowExternalLinkProcessor(md), "external_rel", 5)


def safe_markdown(value: str):
    if not value:
        return mark_safe("")
    html = markdown.markdown(
        value,
        extensions=["fenced_code", "nl2br", "sane_lists", NoFollowExternalLinkExtension()],
    )
    cleaned = nh3.clean(
        html,
        tags=SAFE_MARKDOWN_TAGS,
        attributes=SAFE_MARKDOWN_ATTRIBUTES,
        link_rel=None,
    )
    return mark_safe(cleaned)


def short_datetime(value):
    """Time if today, drop year if this year, otherwise full date."""
    if value is None:
        return ""
    local = timezone.localtime(value)
    today = timezone.localdate()
    if local.date() == today:
        return local.strftime("%b %-d, %H:%M")
    if local.year == today.year:
        return local.strftime("%b %-d")
    return local.strftime("%b %-d, %Y")


def url(name, *args, **kwargs):
    """Wraps `reverse` so templates can call `url('name', arg1, arg2)` positionally."""
    return reverse(name, args=args, kwargs=kwargs)


STYLE_BLOCK_RE = re.compile(r"(<style[^>]*>)(.*?)(</style>)", re.DOTALL)


class FrontendLayoutLoader(FileSystemLoader):
    """Loads the Ursus-generated forum layout, wrapping its inline CSS in
    `{% raw %}` so `{#…}` selectors aren't parsed as Jinja2 comments."""

    def get_source(self, environment, template):
        source, filename, uptodate = super().get_source(environment, template)
        source = STYLE_BLOCK_RE.sub(r"\1{% raw %}\2{% endraw %}\3", source)
        return source, filename, uptodate


def environment(**options):
    options["undefined"] = StrictUndefined
    # `forum/layout.html` lives in Ursus output; scope the loader so unrelated
    # files there (404.html, about.html, etc.) can't be picked up as templates.
    app_loader = options.pop("loader")
    frontend_loader = PrefixLoader({"forum": FrontendLayoutLoader("/var/frontend-output/forum")})
    options["loader"] = ChoiceLoader([app_loader, frontend_loader])
    env = Environment(**options)
    env.globals.update(
        {
            "url": url,
            "static": staticfiles_storage.url,
            "SITE_URL": settings.BASE_URL,
        }
    )
    env.filters.update(
        {
            "safe_markdown": safe_markdown,
            "short_datetime": short_datetime,
            "date": defaultfilters.date,
            "pluralize": defaultfilters.pluralize,
            "timesince": defaultfilters.timesince_filter,
            "linebreaks": defaultfilters.linebreaks_filter,
            "linebreaksbr": defaultfilters.linebreaksbr,
            "escapejs": defaultfilters.escapejs_filter,
            "default": defaultfilters.default,
            "default_if_none": defaultfilters.default_if_none,
            "yesno": defaultfilters.yesno,
            "add": defaultfilters.add,
            "intcomma": humanize.intcomma,
        }
    )
    return env
