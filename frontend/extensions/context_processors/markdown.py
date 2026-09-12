import re

from ursus.config import config
from ursus.context_processors import Context, EntryContextProcessor, EntryURI


FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
JINJA_TAG_RE = re.compile(r"\{%.*?%\}", re.DOTALL)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^[^\]]+\]:.*$", re.MULTILINE)
FOOTNOTE_REF_RE = re.compile(r"\[\^[^\]]+\]")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")


def markdown_to_plaintext(text: str) -> str:
    text = FRONTMATTER_RE.sub("", text, count=1)
    text = JINJA_TAG_RE.sub("", text)
    text = IMAGE_RE.sub("", text)
    text = FOOTNOTE_DEF_RE.sub("", text)
    text = FOOTNOTE_REF_RE.sub("", text)
    text = LINK_RE.sub(r"\1", text)
    return text


class MarkdownPlaintextProcessor(EntryContextProcessor):
    def process_entry(self, context: Context, entry_uri: EntryURI) -> None:
        if not entry_uri.lower().endswith(".md"):
            return
        raw = (config.content_path / entry_uri).read_text()
        context["entries"][entry_uri]["plaintext"] = markdown_to_plaintext(raw)
