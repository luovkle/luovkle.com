from flask import Blueprint, abort, render_template

from .content import get_meta
from .loader import get_content_data

content = get_content_data()

bp = Blueprint("views", __name__)


@bp.route("/")
def home():
    meta = get_meta()
    return render_template(
        "homepage.html",
        meta=meta,
        author=content["author"],
        homepage=content["homepage"],
    )


@bp.route("/p")
def post_list():
    meta = get_meta()
    context = list(content["posts"].values())
    return render_template("post_list.html", meta=meta, posts=context)


@bp.route("/p/<slug>")
def post_detail(slug):
    meta = get_meta()
    post = content["posts"].get(slug)
    if not post:
        abort(404)
    return render_template("post_detail.html", meta=meta, post=post)


@bp.route("/pr")
def project_list():
    meta = get_meta()
    context = list(content["projects"].values())
    return render_template("project_list.html", meta=meta, projects=context)


@bp.route("/pr/<slug>")
def project_detail(slug):
    meta = get_meta()
    project = content["projects"].get(slug)
    if not project:
        abort(404)
    return render_template("project_detail.html", meta=meta, project=project)


@bp.route("/author")
def author():
    meta = get_meta()
    author = content["author"]
    return render_template("author.html", meta=meta, author=author)
