from bs4 import BeautifulSoup
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from ursus.context_processors import Context, EntryURI
from ursus.context_processors.markdown import MarkdownProcessor
from xml.etree.ElementTree import Element


class PlaintextTreeprocessor(Treeprocessor):
    def run(self, root: Element) -> None:
        """
        Converts the ElementTree to plaintext.
        """
        parts: list[str] = []

        def is_footnote(el: Element) -> bool:
            # Footnotes at the bottom
            if el.tag == "details" and el.get("id") == "footnotes":
                return True

            # Footnote markers in the text
            if el.tag == "sup" and (el.get("id") or "").startswith("fnref:"):
                return True
            return False

        def walk(el: Element) -> None:
            if el.tag == "li":
                parts.append("- ")
            if el.text:
                parts.append(el.text)
            for child in el:
                if is_footnote(child):
                    if child.tail:
                        parts.append(child.tail)
                    continue
                walk(child)
                if self.md.is_block_level(child.tag) or child.tag == "br":
                    parts.append("\n")
                if child.tail:
                    parts.append(child.tail)

        walk(root)
        resolved = "".join(parts)
        for postprocessor in self.md.postprocessors:
            resolved = postprocessor.run(resolved)
        self.md.plaintext = BeautifulSoup(resolved, "html.parser").get_text()  # pyright: ignore[reportAttributeAccessIssue]


class PlaintextExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(PlaintextTreeprocessor(md), "plaintext", -100)


class MarkdownHtmlAndPlaintextProcessor(MarkdownProcessor):
    """
    Also renders the markdown as plaintext for the search index.
    """

    def __init__(self):
        super().__init__()
        PlaintextExtension().extendMarkdown(self.markdown)

    def process_entry(self, context: Context, entry_uri: EntryURI) -> None:
        super().process_entry(context, entry_uri)
        if entry_uri.lower().endswith(".md"):
            context["entries"][entry_uri]["body_plaintext"] = self.markdown.plaintext
