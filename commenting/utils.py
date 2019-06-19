import re

from commenting.quoted_post import MarkdownWithQuotedPost, HighlighterRenderer

IMG_REGEX = re.compile('!\[.*?\]\([A-Za-z0-9_\-.]+\)')


def render_html(text):
    markdown_renderer = MarkdownWithQuotedPost(renderer=HighlighterRenderer())
    return markdown_renderer(text)


def clean_quoted_content(content: str):
    return IMG_REGEX.sub('', content)


# TODO.... remove image and videos from content
def quote_votable(votable):
    return f'<<<[[{votable.author}|{votable.id}]]\n{clean_quoted_content(votable.content)}<<<\n'
