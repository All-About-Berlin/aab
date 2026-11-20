import html
import re
from datetime import timedelta
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from api.jinja2 import safe_markdown
from forum.models import Post, PostSubscription, Reply
from forum.views import IndexView, get_unsubscribe_url_token


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


class UserMentionsTests(SimpleTestCase):
    def test_post_user_mentions(self):
        cases = [
            ("@alice hello", {"alice"}),
            ("hey @alice and @bob", {"alice", "bob"}),
            ("@alice and @alice again", {"alice"}),
            ("@Alice and @alice", {"Alice", "alice"}),
            ("@alice.b and @bob-c and @dev_1", {"alice.b", "bob-c", "dev_1"}),
            ("hi (@alice)", {"alice"}),
            ("line one\n@alice", {"alice"}),
            ("email bob@gmail.com for help", set()),
            ("see https://user@host/path", set()),
            ("@ab is too short", set()),
            ("@abcdefghijklmnopqrstuvwxyz is too long", set()),
            ("hi @abc", {"abc"}),
            ("hi @abcdefghijklmnopqrst done", {"abcdefghijklmnopqrst"}),
        ]
        for body, expected in cases:
            with self.subTest(body=body):
                self.assertEqual(Post(body=body).user_mentions, expected)

    def test_reply_user_mentions(self):
        self.assertEqual(Reply(body="thanks @alice").user_mentions, {"alice"})


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "forum-cache-tests"}}
)
class ForumCacheTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(username="alice")
        self.post = Post.objects.create(author=self.user, title="Original title", body="Original body")
        self.url = reverse("forum_post", args=[self.post.pk])

    def test_anonymous_response_is_cached(self):
        first = self.client.get(self.url)
        self.assertEqual(first["X-Cache"], "MISS")
        self.assertContains(first, "Original body")

        Post.objects.filter(pk=self.post.pk).update(body="Silent edit")

        second = self.client.get(self.url)
        self.assertEqual(second["X-Cache"], "HIT")
        self.assertContains(second, "Original body")
        self.assertNotContains(second, "Silent edit")

    def test_authenticated_response_is_not_cached(self):
        self.client.get(self.url)
        Post.objects.filter(pk=self.post.pk).update(body="Silent edit")

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertFalse(response.has_header("X-Cache"))
        self.assertContains(response, "Silent edit")

    def test_reply_invalidates_cache(self):
        primed = self.client.get(self.url)
        self.assertEqual(primed["X-Cache"], "MISS")
        self.assertNotContains(primed, "First reply")

        Reply.objects.create(author=self.user, post=self.post, body="First reply")

        response = self.client.get(self.url)
        self.assertEqual(response["X-Cache"], "MISS")
        self.assertContains(response, "First reply")

    def test_post_edit_invalidates_cache(self):
        primed = self.client.get(self.url)
        self.assertEqual(primed["X-Cache"], "MISS")
        self.assertContains(primed, "Original title")

        self.post.title = "Edited title"
        self.post.save()

        response = self.client.get(self.url)
        self.assertEqual(response["X-Cache"], "MISS")
        self.assertContains(response, "Edited title")
        self.assertNotContains(response, "Original title")


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "forum-links-tests"}},
    RESULTS_PER_PAGE=2,
)
@patch.object(IndexView, "paginate_by", 2)
class ForumPaginationMetadataTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(username="alice")

    def test_forum_index_prev_next_head_links(self):
        for i in range(5):
            Post.objects.create(author=self.user, title=f"Post {i}", body="body")
        response = self.client.get(reverse("forum_index_page", args=[2]))
        self.assertContains(response, '<link rel="prev" href="https://localhost/forum">')
        self.assertContains(response, '<link rel="next" href="https://localhost/forum/page-3">')

    def test_forum_index_prev_link_preserves_query_string(self):
        for i in range(3):
            Post.objects.create(author=self.user, title=f"Post {i}", body="body", category="work")
        response = self.client.get(reverse("forum_index_page", args=[2]) + "?category=work")
        self.assertContains(response, '<link rel="prev" href="https://localhost/forum?category=work">')

    def test_forum_post_prev_next_head_links(self):
        post = Post.objects.create(author=self.user, title="Post", body="body")
        for i in range(3):
            Reply.objects.create(author=self.user, post=post, body=f"reply {i}")
        response = self.client.get(reverse("forum_post_page", args=[post.pk, 2]))
        self.assertContains(response, f'<link rel="prev" href="https://localhost/forum/{post.pk}">')


@patch("forum.management.commands.send_forum_digest.send_email")
class SendForumDigestCommandTests(TestCase):
    def setUp(self):
        self.alice = get_user_model().objects.create_user(username="alice", email="alice@example.com")
        self.bob = get_user_model().objects.create_user(username="bob", email="bob@example.com")

    def test_subscribed_reply_triggers_email(self, send_email):
        post = Post.objects.create(author=self.alice, title="Hello", body="body")
        PostSubscription.objects.create(user=self.alice, post=post)
        Reply.objects.create(author=self.bob, post=post, body="reply!")

        call_command("send_forum_digest")

        send_email.assert_called_once()
        recipients, subject, _ = send_email.call_args.args
        self.assertEqual(recipients, ["alice@example.com"])
        self.assertIn("1 reply", subject)

    def test_mention_triggers_email(self, send_email):
        Post.objects.create(author=self.bob, title="Hey", body="hey @alice")

        call_command("send_forum_digest")

        send_email.assert_called_once()
        self.assertEqual(send_email.call_args.args[0], ["alice@example.com"])
        self.assertIn("1 mention", send_email.call_args.args[1])

    def test_self_mention_does_not_trigger_email(self, send_email):
        Post.objects.create(author=self.alice, title="Hey", body="hey @alice")

        call_command("send_forum_digest")

        send_email.assert_not_called()

    def test_own_reply_to_subscribed_post_does_not_trigger_email(self, send_email):
        post = Post.objects.create(author=self.alice, title="Hi", body="body")
        PostSubscription.objects.create(user=self.alice, post=post)
        Reply.objects.create(author=self.alice, post=post, body="my own reply")

        call_command("send_forum_digest")

        send_email.assert_not_called()

    def test_items_older_than_24h_are_excluded(self, send_email):
        post = Post.objects.create(author=self.alice, title="Old subscribed", body="body")
        PostSubscription.objects.create(user=self.alice, post=post)
        old = timezone.now() - timedelta(hours=25)
        Post.objects.filter(pk=post.pk).update(creation_date=old)
        reply = Reply.objects.create(author=self.bob, post=post, body="hey @alice")
        Reply.objects.filter(pk=reply.pk).update(creation_date=old)
        mention_post = Post.objects.create(author=self.bob, title="Old mention", body="hi @alice")
        Post.objects.filter(pk=mention_post.pk).update(creation_date=old)

        call_command("send_forum_digest")

        send_email.assert_not_called()

    def test_removed_items_do_not_trigger_email(self, send_email):
        subscribed = Post.objects.create(author=self.alice, title="Hi", body="body")
        PostSubscription.objects.create(user=self.alice, post=subscribed)
        Reply.objects.create(author=self.bob, post=subscribed, body="reply", removal_date=timezone.now())
        Post.objects.create(author=self.bob, title="Mention", body="hey @alice", removal_date=timezone.now())

        call_command("send_forum_digest")

        send_email.assert_not_called()

    def test_only_new_posts_skips_user(self, send_email):
        Post.objects.create(author=self.bob, title="Unrelated", body="no mentions")

        call_command("send_forum_digest")

        send_email.assert_not_called()

    def test_disabled_notifications_skips_user(self, send_email):
        self.alice.email_notifications = False
        self.alice.save()
        post = Post.objects.create(author=self.alice, title="Hi", body="body")
        PostSubscription.objects.create(user=self.alice, post=post)
        Reply.objects.create(author=self.bob, post=post, body="reply")

        call_command("send_forum_digest")

        send_email.assert_not_called()

    def test_subject_combines_counts(self, send_email):
        post = Post.objects.create(author=self.alice, title="Hi", body="body")
        PostSubscription.objects.create(user=self.alice, post=post)
        Reply.objects.create(author=self.bob, post=post, body="first")
        Reply.objects.create(author=self.bob, post=post, body="second")
        Post.objects.create(author=self.bob, title="New thread", body="hi @alice")

        call_command("send_forum_digest")

        self.assertEqual(
            send_email.call_args.args[1],
            "Yesterday on All About Berlin: 2 replies, 2 new posts, 1 mention",
        )

    def test_subject_hides_zero_parts(self, send_email):
        post = Post.objects.create(author=self.alice, title="Old", body="body")
        PostSubscription.objects.create(user=self.alice, post=post)
        Reply.objects.create(author=self.bob, post=post, body="reply")
        Post.objects.filter(pk=post.pk).update(creation_date=timezone.now() - timedelta(hours=25))

        call_command("send_forum_digest")

        self.assertEqual(send_email.call_args.args[1], "Yesterday on All About Berlin: 1 reply")

    def test_unsubscribe_url_in_email_disables_notifications(self, send_email):
        Post.objects.create(author=self.bob, title="Hey", body="hey @alice")

        call_command("send_forum_digest")

        body = send_email.call_args.args[2]
        match = re.search(r'href="([^"]+/forum/unsubscribe/all[^"]+)"', body)
        self.assertIsNotNone(match)
        parsed = urlparse(html.unescape(match.group(1)))
        params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        response = self.client.post(parsed.path, params)

        self.assertEqual(response.status_code, 200)
        self.alice.refresh_from_db()
        self.assertFalse(self.alice.email_notifications)


class TurnOffNotificationsViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="alice", email_notifications=True)
        self.token = get_unsubscribe_url_token(self.user)
        self.url = reverse("forum_turn_off_notifications")

    def test_get_renders_confirmation(self):
        response = self.client.get(self.url, {"user": "alice", "token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "alice")

    def test_post_with_valid_token_disables_notifications(self):
        response = self.client.post(self.url, {"user": "alice", "token": self.token})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.email_notifications)

    def test_post_with_tampered_token_rejected(self):
        response = self.client.post(self.url, {"user": "alice", "token": "wrong"})
        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_notifications)


class NewPostAutoSubscribeTests(TestCase):
    def test_creating_a_post_auto_subscribes_the_author(self):
        user = get_user_model().objects.create_user(username="alice", password="pw")
        self.client.force_login(user)

        self.client.post(
            reverse("forum_new_post"),
            {"title": "Hello", "category": "other", "body": "body"},
        )

        post = Post.objects.get(title="Hello")
        self.assertTrue(PostSubscription.objects.filter(user=user, post=post).exists())
