from flask import Blueprint, abort, render_template

from .builder import build_content
from .content import get_meta

content_template_paths = build_content()

bp = Blueprint("views", __name__)


@bp.route("/")
def home():
    meta = get_meta()
    return render_template("homepage.html", meta=meta)


@bp.route("/p")
def posts():
    meta = get_meta()
    context = list(content_template_paths["posts"].values())
    return render_template("post_list.html", meta=meta, posts=context)


@bp.route("/p/<slug>")
def single_post(slug):
    meta = get_meta()
    post = content_template_paths["posts"].get(slug)
    if not post:
        abort(404)
    return render_template(post["template"], meta=meta)


@bp.route("/pr")
def projects():
    meta = get_meta()
    context = list(content_template_paths["projects"].values())
    return render_template("project_list.html", meta=meta, projects=context)


@bp.route("/pr/<slug>")
def single_project(slug):
    meta = get_meta()
    project = content_template_paths["projects"].get(slug)
    if not project:
        abort(404)
    return render_template(project["template"], meta=meta)


@bp.route("/author")
def author():
    meta = get_meta()
    return render_template("author.html", meta=meta)
