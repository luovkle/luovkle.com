from flask import Blueprint, abort, render_template

from app.extensions import cache
from app.services.html import get_content

bp = Blueprint("views", __name__)


@bp.route("/")
@cache.cached()
def home():
    content = get_content()
    return render_template(
        "homepage.html",
        metadata=content["metadata"],
        author=content["author"],
        homepage=content["homepage"],
    )


@bp.route("/p")
@cache.cached()
def post_list():
    content = get_content()
    context = list(content["posts"].values())
    return render_template(
        "post_list.html", metadata=content["metadata"], posts=context
    )


@bp.route("/p/<slug>")
@cache.cached()
def post_detail(slug):
    content = get_content()
    post = content["posts"].get(slug)
    if not post:
        abort(404)
    return render_template("post_detail.html", metadata=content["metadata"], post=post)


@bp.route("/pr")
@cache.cached()
def project_list():
    content = get_content()
    context = list(content["projects"].values())
    return render_template(
        "project_list.html", metadata=content["metadata"], projects=context
    )


@bp.route("/pr/<slug>")
@cache.cached()
def project_detail(slug):
    content = get_content()
    project = content["projects"].get(slug)
    if not project:
        abort(404)
    return render_template(
        "project_detail.html", metadata=content["metadata"], project=project
    )


@bp.route("/author")
@cache.cached()
def author():
    content = get_content()
    author = content["author"]
    return render_template("author.html", metadata=content["metadata"], author=author)


@cache.cached()
def page_not_found(_):
    content = get_content()
    return render_template("404.html", metadata=content["metadata"]), 404


@cache.cached()
def internal_server_error(_):
    content = get_content()
    return render_template("500.html", metadata=content["metadata"]), 500
