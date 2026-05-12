from decimal import Decimal
from extensions.functions import hyphenate, soft_hyphen, to_currency
from markdown.extensions import Extension
from markdown.extensions.smarty import SubstituteTextPattern
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import InlineProcessor, Treeprocessor
from typing import Callable
from ursus.config import config
from ursus.context_processors.markdown import BaseUrlExtension, BaseUrlProcessor
from xml.etree import ElementTree
import re


class ServicesAwareBaseUrlProcessor(BaseUrlProcessor):
    """
    Extends the BaseUrlProcessor to also replace /services/* URLs with https://agoodstart.de/* URLs.

    - Converts /guides/mail-a-letter to https://allaboutberlin.com/guides/mail-a-letter (or https://localhost/* in dev)
    - Converts /services/health-insurance to https://agoodstart.de/health-insurance (or https://services.localhost/* in dev)
    """

    def run(self, root):
        services_url = getattr(config, "services_site_url", None)
        for el in root.iter("a"):
            href = el.get("href", "")
            if services_url and (href == "/services" or href.startswith("/services/")):
                el.set("href", services_url + href[len("/services") :])
            elif href.startswith("/"):
                el.set("href", config.site_url + href)


class ServicesAwareBaseUrlExtension(BaseUrlExtension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(ServicesAwareBaseUrlProcessor(md), "baseurl", 15)


def process_element_text(element: ElementTree.Element, operation: Callable) -> None:
    # Replace in the element's text
    if element.text:
        element.text = operation(element.text)
    if element.tail:
        element.tail = operation(element.tail)
    for child in element:
        process_element_text(child, operation)


class HyphenatedTitleProcessor(Treeprocessor):
    soft_hyphen = "\xc2\xad"

    def run(self, root: ElementTree.Element) -> ElementTree.Element:
        def hyphenate_text(text: str) -> str:
            return hyphenate(text, "de_DE", soft_hyphen)

        for el in root.iter():
            if el.tag in ("h1", "h2", "h3"):
                process_element_text(el, hyphenate_text)
        return root


class HyphenatedTitleExtension(Extension):
    """
    Adds soft hyphens to long words in titles
    """

    def extendMarkdown(self, md):
        md.treeprocessors.register(HyphenatedTitleProcessor(self), "hyphenated_titles", 19)


class ArrowLinkIconProcessor(Treeprocessor):
    def run(self, root):
        arrow_link_marker = "➞"
        sections_before_this_link = set()
        for el in root.iter():
            if el.tag in ("h1", "h2", "h3") and (section_id := el.attrib.get("id")):
                sections_before_this_link.add("#" + section_id)
            elif el.tag == "a":
                text = el.text or ""

                if text.strip().endswith(arrow_link_marker):
                    el.text = el.text.rstrip(arrow_link_marker).rstrip()
                    url = el.attrib["href"].removeprefix(config.site_url)

                    link_class = "internal-link"
                    if url.startswith(("http://", "https://", "/out/")):
                        link_class = "external-link"
                    elif url.startswith("#"):
                        el.attrib["title"] = "Scroll to this section"
                        if el.attrib["href"] in sections_before_this_link:
                            link_class = "section-link before"
                        else:
                            link_class = "section-link after"

                    el.attrib["class"] = el.attrib.get("class", "") + " " + link_class
        return root


class ArrowLinkIconExtension(Extension):
    """
    Replaces the "➞" after a link with the appropriate icon
    """

    def extendMarkdown(self, md):
        md.treeprocessors.register(ArrowLinkIconProcessor(self), "linkicon", 0)


class CurrencyPreprocessor(Preprocessor):
    """
    Wraps euro amounts in a <span class="currency"> tag
    """

    CURRENCY_RE = re.compile(r"€((\d+(,\d{3})*(\.\d{2})?))", re.MULTILINE | re.DOTALL)

    def replace_match(self, match):
        formatted_number = to_currency(Decimal(match[1].replace(",", "")))
        return self.md.htmlStash.store(f'€<span class="currency">{formatted_number}</span>')

    def run(self, lines):
        text = "\n".join(lines)

        return re.sub(self.CURRENCY_RE, self.replace_match, text).split("\n")


class JinjaCurrencyPreprocessor(CurrencyPreprocessor):
    """
    Wraps jinja template variables followed with "€" in a <span class="currency"> tag
    """

    CURRENCY_RE = re.compile("€({{([^}]+)}})", re.MULTILINE | re.DOTALL)

    def replace_match(self, match):
        return self.md.htmlStash.store(f'€<span class="currency">{match[1]}</span>')


class CurrencyExtension(Extension):
    """
    Wraps currency in a <span class="currency"> tag
    """

    def extendMarkdown(self, md):
        md.preprocessors.register(CurrencyPreprocessor(md), "cur", 25)
        md.preprocessors.register(JinjaCurrencyPreprocessor(md), "jinja-cur", 26)


class TypographyExtension(Extension):
    """
    Minor typographic improvements
    """

    def extendMarkdown(self, md):
        inline_processor = InlineProcessor(md)

        sectionPattern = SubstituteTextPattern(r"§ ", ("§&nbsp;",), md)
        inline_processor.inlinePatterns.register(sectionPattern, "typo-section", 10)

        ellipsisPattern = SubstituteTextPattern(r"\.\.\.", ("…",), md)
        inline_processor.inlinePatterns.register(ellipsisPattern, "typo-ellipsis", 10)

        ellipsisPattern = SubstituteTextPattern(r" - ", ("&nbsp;–&nbsp;",), md)
        inline_processor.inlinePatterns.register(ellipsisPattern, "typo-emdash", 10)

        squaredPattern = SubstituteTextPattern(r"\^2\^", ("²",), md)
        inline_processor.inlinePatterns.register(squaredPattern, "squared", 65)

        cubedPattern = SubstituteTextPattern(r"\^3\^", ("³",), md)
        inline_processor.inlinePatterns.register(cubedPattern, "cubed", 65)

        md.treeprocessors.register(inline_processor, "typography", 2)


class WrappedTableProcessor(Treeprocessor):
    """
    Wrap tables in a <div> to allow scrollable tables on mobile.
    """

    def wrap_table(self, table, parent):
        wrapper = ElementTree.Element("div", attrib={"class": self.md.getConfig("wrapper_class")})
        wrapper.append(table)

        for index, element in enumerate(parent):
            if element == table:
                parent[index] = wrapper
                wrapper.tail = table.tail
                return

    def run(self, root):
        parent_map = {}
        for parent in root.iter():
            for child in parent:
                parent_map[child] = parent

        for table in root.iter("table"):
            child = table
            parents = []
            while parent := parent_map.get(child):
                parents.append(parent)
                child = parent

            self.wrap_table(table, parents[0])


class WrappedTableExtension(Extension):
    """
    Tables are wrapped in a <div>
    """

    def __init__(self, **kwargs):
        self.config = {
            "wrapper_class": [
                "",
                "CSS class to add to the <div> element that wraps the table",
            ],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        if self.getConfig("wrapper_class"):
            md.treeprocessors.register(WrappedTableProcessor(self), "wrappedtable", 0)


class CheckCrossListProcessor(Treeprocessor):
    markers = {
        "✓ ": "list-yes",
        "✗ ": "list-no",
    }

    def run(self, root: ElementTree.Element) -> ElementTree.Element:
        for li in root.iter(tag="li"):
            text = li.text or ""
            for marker, css_class in self.markers.items():
                if text.startswith(marker):
                    li.text = text.removeprefix(marker)
                    css_classes = set(li.attrib.get("class", "").split())
                    css_classes.add(css_class)
                    li.attrib["class"] = " ".join(css_classes)
                    break
        return root


class CheckCrossListExtension(Extension):
    """
    Adds CSS classes to list items starting with ✓ or ✗:

    - ✓ Good thing  → <li class="list-yes">Good thing</li>
    - ✗ Bad thing   → <li class="list-no">Bad thing</li>
    """

    def extendMarkdown(self, md):
        md.treeprocessors.register(CheckCrossListProcessor(self), "check-cross-list", 100)
