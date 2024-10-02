from flask import g

from .loader import get_meta_tags_data


def get_meta():
    if "meta" not in g:
        g.meta = get_meta_tags_data()
    return g.meta
