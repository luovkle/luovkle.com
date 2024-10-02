from functools import cache

from flask import g

from .loader import get_content_data


@cache
def get_content():
    if "content" not in g:
        g.content = get_content_data()
    return g.content
