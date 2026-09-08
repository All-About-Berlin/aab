from django.test import SimpleTestCase, override_settings

from forum.templatetags.safe_markdown import safe_markdown


@override_settings(ALLOWED_HOSTS=["allaboutberlin.com", "services.allaboutberlin.com"])
class SafeMarkdownTests(SimpleTestCase):
    def test_empty(self):
        self.assertEqual(safe_markdown(""), "")

    def test_paragraph(self):
        self.assertEqual(
            safe_markdown("Paragraph one.\n\nParagraph two."),
            "<p>Paragraph one.</p>\n<p>Paragraph two.</p>",
        )

    def test_bold_italic_inline_code(self):
        self.assertEqual(
            safe_markdown("**bold**, *italic*, `code`"),
            "<p><strong>bold</strong>, <em>italic</em>, <code>code</code></p>",
        )

    def test_unordered_list(self):
        self.assertEqual(
            safe_markdown("- one\n- two"),
            "<ul>\n<li>one</li>\n<li>two</li>\n</ul>",
        )

    def test_ordered_list(self):
        self.assertEqual(
            safe_markdown("1. first\n2. second"),
            "<ol>\n<li>first</li>\n<li>second</li>\n</ol>",
        )

    def test_blockquote(self):
        self.assertEqual(
            safe_markdown("> quoted line"),
            "<blockquote>\n<p>quoted line</p>\n</blockquote>",
        )

    def test_fenced_code_block(self):
        self.assertEqual(
            safe_markdown("```\nline one\nline two\n```"),
            "<pre><code>line one\nline two\n</code></pre>",
        )

    def test_image(self):
        self.assertEqual(
            safe_markdown("![caption](/images/foo.png)"),
            '<p><img alt="caption" src="/images/foo.png"></p>',
        )

    def test_external_link_gets_rel(self):
        self.assertEqual(
            safe_markdown("[external](https://example.com/page)"),
            '<p><a href="https://example.com/page" rel="nofollow ugc noopener">external</a></p>',
        )

    def test_relative_link_has_no_rel(self):
        self.assertEqual(
            safe_markdown("[guide](/guides/foo)"),
            '<p><a href="/guides/foo">guide</a></p>',
        )

    def test_same_domain_link_has_no_rel(self):
        self.assertEqual(
            safe_markdown("[home](https://allaboutberlin.com/guides/foo)"),
            '<p><a href="https://allaboutberlin.com/guides/foo">home</a></p>',
        )

    def test_services_subdomain_has_no_rel(self):
        self.assertEqual(
            safe_markdown("[services](https://services.allaboutberlin.com/x)"),
            '<p><a href="https://services.allaboutberlin.com/x">services</a></p>',
        )

    def test_script_tag_stripped(self):
        self.assertEqual(
            safe_markdown("hello <script>alert(1)</script> world"),
            "<p>hello  world</p>",
        )

    def test_event_handler_stripped(self):
        self.assertEqual(
            safe_markdown('<a href="https://example.com" onclick="steal()">x</a>'),
            '<p><a href="https://example.com" rel="nofollow ugc noopener">x</a></p>',
        )

    def test_iframe_stripped(self):
        self.assertEqual(safe_markdown('<iframe src="https://evil.example.com"></iframe>'), "")

    def test_javascript_href_stripped(self):
        self.assertEqual(
            safe_markdown("[click](javascript:alert(1))"),
            "<p><a>click</a></p>",
        )
