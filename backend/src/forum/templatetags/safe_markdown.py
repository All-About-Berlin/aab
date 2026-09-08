import re
from urllib.parse import urlparse

import markdown
import nh3
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe


register = template.Library()


ALLOWED_TAGS = {"p", "br", "strong", "em", "a", "ul", "ol", "li", "blockquote", "code", "pre", "img"}
ALLOWED_ATTRIBUTES = {"a": {"href", "rel"}, "img": {"src", "alt", "title"}}
EXTERNAL_REL = "nofollow ugc noopener"

_ANCHOR_RE = re.compile(r"<a\b([^>]*)>", flags=re.IGNORECASE)
_HREF_RE = re.compile(r"""href\s*=\s*(?:"([^"]*)"|'([^']*)')""", flags=re.IGNORECASE)
_REL_RE = re.compile(r"""\srel\s*=\s*(?:"[^"]*"|'[^']*')""", flags=re.IGNORECASE)


def _is_external(href: str) -> bool:
    parsed = urlparse(href)
    if not parsed.scheme or not parsed.netloc:
        return False
    return parsed.hostname not in settings.ALLOWED_HOSTS


def _add_external_rel(html: str) -> str:
    def replace(match: re.Match) -> str:
        attrs = match.group(1)
        href_match = _HREF_RE.search(attrs)
        if not href_match:
            return match.group(0)
        href = href_match.group(1) or href_match.group(2) or ""
        if not _is_external(href):
            return match.group(0)
        attrs_without_rel = _REL_RE.sub("", attrs)
        return f'<a{attrs_without_rel} rel="{EXTERNAL_REL}">'

    return _ANCHOR_RE.sub(replace, html)


@register.filter
def safe_markdown(value: str):
    if not value:
        return mark_safe("")
    html = markdown.markdown(value, extensions=["fenced_code", "nl2br", "sane_lists"])
    cleaned = nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        link_rel=None,
    )
    return mark_safe(_add_external_rel(cleaned))
