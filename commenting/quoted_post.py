import re

from mistune import Renderer, Markdown, InlineLexer, BlockLexer, BlockGrammar, InlineGrammar

QUOTED_POST_RE = re.compile(
    r'^<<<\s*\[\['  # <<<[[
    r'([\s\S]+?)\|([\s\S]+?)'  # Author|PostID
    r'\]\](.*)<<<',  # ]] some stuf the author said <<<
    flags=re.DOTALL)


class QuotedPostBlockGrammar(BlockGrammar):
    quoted_post = QUOTED_POST_RE


class QuotedPostBlockLexer(BlockLexer):
    default_rules = ['quoted_post'] + BlockLexer.default_rules

    def __init__(self, rules=None, **kwargs):
        if rules is None:
            rules = QuotedPostBlockGrammar()
        super().__init__(rules=rules, **kwargs)

    def parse_quoted_post(self, m):
        post = m.group(1)
        # author, post_id = post.split('|')
        self.tokens.append({
            'type': 'quoted_post',
            'author': m.group(1),
            'post_id': m.group(2),
            'text': m.group(3),
        })


class QuotedPostInlineGrammar(InlineGrammar):
    quoted_post = QUOTED_POST_RE
    text = re.compile(r'^[\s\S]+?(?=[\\<!\[_*`~]|https?://| {2,}\n|$)')


class QuotedPostInlineLexer(InlineLexer):
    default_rules = ['quoted_post'] + InlineLexer.default_rules

    def __init__(self, renderer, rules=None, **kwargs):
        if rules is None:
            rules = QuotedPostInlineGrammar()
        super().__init__(renderer=renderer, rules=rules, **kwargs)

    def output_quoted_post(self, m):
        # post = m.group(1)
        # author, post_id = post.split('|')
        return self.renderer.quoted_post(m.group(1), m.group(2), m.group(3))


class MarkdownWithQuotedPost(Markdown):
    def __init__(self, renderer, **kwargs):
        if 'inline' not in kwargs:
            kwargs['inline'] = QuotedPostInlineLexer
        if 'block' not in kwargs:
            kwargs['block'] = QuotedPostBlockLexer
        super().__init__(renderer=renderer, **kwargs)

    def output_quoted_post(self):
        return self.renderer.quoted_post(self.token['author'], self.token['post_id'], self.token['text'])


class HighlighterRenderer(Renderer):
    def quoted_post(self, author_name, post_href, post_content):
        return '<blockquote><a href="%s">%s</a><br>%s</blockquote>' % (post_href, author_name, post_content)
