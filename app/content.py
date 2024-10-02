from flask import g

from .loader import get_content_data


def get_content():
    if "content" not in g:
        g.content = get_content_data()
    return g.content
