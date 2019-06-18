import re

from mistune import Renderer, Markdown, BlockLexer

IMG_REGEX = re.compile('!\[.*?\]\([A-Za-z0-9_\-.]+\)')


class QuotedPostRenderer(Renderer):
    def quoted_post(self, post_href, author_name, post_content):
        return '<blockquote><a href="%s">%s</a><br>%s</blockquote>' % (post_href, author_name, post_content)


class QuotedPostInlineLexer(BlockLexer):
    def enable_quoted_post(self):
        # add wiki_link rules
        self.rules.quoted_post = re.compile(
            r'>>>\s*\[\['  # ``[[
            r'([\s\S]+?\|[\s\S]+?)'  # Author|PostID
            r'\]\](.*)>>>'  # ]] some stuf the author said``
        )
        print(self.default_rules)
        self.default_rules.insert(6, 'quoted_post')

    def output_quoted_post(self, m):
        post = m.group(1)
        author, post_id = post.split('|')
        return self.renderer.quoted_post(post_id, author, m.group(2))


def render(markdown, quoted_post=True):
    renderer = QuotedPostRenderer()
    # inline = QuotedPostInlineLexer(renderer)
    # if quoted_post:
    #     inline.enable_quoted_post()
    md = Markdown(renderer)
    return md(markdown)


def clean_quoted_content(content: str):
    return IMG_REGEX.sub('', content)


# TODO.... remove image and videos from content
def quote_post(post):
    return f'>>>[[{post.author}|{post.id}]]\n{clean_quoted_content(post.content)}>>>'


if __name__ == '__main__':
    print(IMG_REGEX.match('![alt text](image.jpg) fasdfdsfadf'))
    print(render(">>>[[puskin|23]] There's hope bro. Stay put.>>>"))
