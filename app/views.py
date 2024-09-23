from flask import Blueprint, abort, render_template

from .builder import build_content

content_template_paths = build_content()

bp = Blueprint("views", __name__)


@bp.route("/")
def home():
    return render_template("homepage.html")


@bp.route("/p")
def posts():
    context = list(content_template_paths["posts"].values())
    return render_template("post_list.html", posts=context)


@bp.route("/p/<slug>")
def single_post(slug):
    post = content_template_paths["posts"].get(slug)
    if not post:
        abort(404)
    return render_template(post["template"])


@bp.route("/pr")
def projects():
    context = list(content_template_paths["projects"].values())
    return render_template("project_list.html", projects=context)


@bp.route("/pr/<slug>")
def single_project(slug):
    project = content_template_paths["projects"].get(slug)
    if not project:
        abort(404)
    return render_template(project["template"])


@bp.route("/author")
def author():
    return render_template("author.html")
