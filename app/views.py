from flask import Blueprint, abort, render_template

from .content import get_content
from .extensions import cache

bp = Blueprint("views", __name__)


@bp.route("/")
@cache.cached()
def home():
    content = get_content()
    return render_template(
        "homepage.html",
        meta=content["meta"],
        author=content["author"],
        homepage=content["homepage"],
    )


@bp.route("/p")
@cache.cached()
def post_list():
    content = get_content()
    context = list(content["posts"].values())
    return render_template("post_list.html", meta=content["meta"], posts=context)


@bp.route("/p/<slug>")
@cache.cached()
def post_detail(slug):
    content = get_content()
    post = content["posts"].get(slug)
    if not post:
        abort(404)
    return render_template("post_detail.html", meta=content["meta"], post=post)


@bp.route("/pr")
@cache.cached()
def project_list():
    content = get_content()
    context = list(content["projects"].values())
    return render_template("project_list.html", meta=content["meta"], projects=context)


@bp.route("/pr/<slug>")
@cache.cached()
def project_detail(slug):
    content = get_content()
    project = content["projects"].get(slug)
    if not project:
        abort(404)
    return render_template("project_detail.html", meta=content["meta"], project=project)


@bp.route("/author")
@cache.cached()
def author():
    content = get_content()
    author = content["author"]
    return render_template("author.html", meta=content["meta"], author=author)
