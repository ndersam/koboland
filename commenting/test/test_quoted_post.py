from django.test import TestCase

from commenting.quoted_post import MarkdownWithQuotedPost, HighlighterRenderer


class TestQuotedPostRendering(TestCase):

    def setUp(self) -> None:
        self.renderer = MarkdownWithQuotedPost(renderer=HighlighterRenderer())

    def test_quoted_post(self):
        md = "<<<[[puskin|23]]There's hope bro. Stay put.<<<"
        html = "<blockquote><a href=\"23\">puskin</a><br>There's hope bro. Stay put.</blockquote>"
        self.assertEquals(self.renderer(md), html)
