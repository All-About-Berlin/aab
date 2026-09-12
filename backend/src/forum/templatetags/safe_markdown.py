from urllib.parse import urlparse

import markdown
import nh3
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


register = template.Library()


ALLOWED_TAGS = {"p", "br", "strong", "em", "a", "ul", "ol", "li", "blockquote", "code", "pre"}
ALLOWED_ATTRIBUTES = {"a": {"href", "rel"}}


def _is_external(href: str) -> bool:
    parsed = urlparse(href)
    if not parsed.scheme or not parsed.netloc:
        return False
    return parsed.hostname not in settings.ALLOWED_HOSTS


class NoFollowExternalLinkProcessor(Treeprocessor):
    def run(self, root):
        for anchor in root.iter("a"):
            href = anchor.get("href", "")
            if _is_external(href):
                anchor.set("rel", "nofollow ugc noopener")


class NoFollowExternalLinkExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(NoFollowExternalLinkProcessor(md), "external_rel", 5)


@register.filter
def safe_markdown(value: str):
    if not value:
        return mark_safe("")
    html = markdown.markdown(
        value,
        extensions=["fenced_code", "nl2br", "sane_lists", NoFollowExternalLinkExtension()],
    )
    cleaned = nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        link_rel=None,
    )
    return mark_safe(cleaned)
