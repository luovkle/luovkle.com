from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.ansi import get_ansi_content
from app.services.html import get_content
from app.views.utils import is_cli_user_agent, render_ansi_template

router = APIRouter(include_in_schema=False)

templates = Jinja2Templates(directory="app/templates/")


def post_html_detail(request: Request, slug: str):
    content = get_content()
    post = content["posts"].get(slug)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    context = {"metadata": content["metadata"], "post": post}
    return templates.TemplateResponse(request, "post_detail.html", context=context)


def post_ansi_detail(slug: str):
    content = get_ansi_content()
    post = content["posts"].get(slug)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return render_ansi_template("post_template", **post)


def project_html_detail(request: Request, slug: str):
    content = get_content()
    project = content["projects"].get(slug)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    context = {"metadata": content["metadata"], "project": project}
    return templates.TemplateResponse(request, "project_detail.html", context)


def project_ansi_detail(slug: str):
    content = get_ansi_content()
    project = content["projects"].get(slug)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return render_ansi_template("project_template", **project)


def internal_exception(request: Request):
    content = get_content()
    context = {"metadata": content["metadata"]}
    return templates.TemplateResponse(
        request,
        "500.html",
        context=context,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def not_found_exception(request: Request):
    content = get_content()
    context = {"metadata": content["metadata"]}
    return templates.TemplateResponse(
        request,
        "404.html",
        context=context,
        status_code=status.HTTP_404_NOT_FOUND,
    )


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    content = get_content()
    context = {
        "metadata": content["metadata"],
        "author": content["author"],
        "homepage": content["homepage"],
    }
    return templates.TemplateResponse(request, "homepage.html", context)


@router.get("/p", response_class=HTMLResponse)
async def post_list(request: Request):
    content = get_content()
    posts = list(content["posts"].values())
    context = {
        "metadata": content["metadata"],
        "posts": posts,
    }
    return templates.TemplateResponse(request, "post_list.html", context)


@router.get("/p/{slug}", response_class=HTMLResponse)
async def post_detail(request: Request, slug: str):
    if is_cli_user_agent(str(request.headers.get("User-Agent"))):
        return post_ansi_detail(slug)
    return post_html_detail(request, slug)


@router.get("/pr", response_class=HTMLResponse)
async def project_list(request: Request):
    content = get_content()
    projects = list(content["projects"].values())
    context = {
        "metadata": content["metadata"],
        "projects": projects,
    }
    return templates.TemplateResponse(request, "project_list.html", context)


@router.get("/pr/{slug}", response_class=HTMLResponse)
async def project_detail(request: Request, slug: str):
    if is_cli_user_agent(str(request.headers.get("User-Agent"))):
        return project_ansi_detail(slug)
    return project_html_detail(request, slug)


@router.get("/author", response_class=HTMLResponse)
async def author(request: Request):
    content = get_content()
    author = content["author"]
    context = {
        "metadata": content["metadata"],
        "author": author,
    }
    return templates.TemplateResponse(request, "author.html", context)
