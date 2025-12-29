from functools import cache
from pathlib import Path

import yaml
from rich.console import Console
from rich.markdown import Markdown

from app.config import (
    ANSI_HEADERS_DIR,
    COVER_ANSI_FILENAME_TEMPLATE,
    HEADERS_DIR,
    POSTS_CONTENT_DIR,
    PROJECTS_CONTENT_DIR,
)
from app.schemas import PostMD, ProjectMD
from app.services.common import (
    estimate_reading_time,
    find_markdown_files,
    get_cover_number,
    get_creation_date,
    get_slug,
    split_markdown_file,
)


def get_ansi_header_path(title: str) -> Path:
    number_of_covers = len(list(HEADERS_DIR.glob("*.png")))
    cover_number = get_cover_number(len(title), number_of_covers)
    cover_file = COVER_ANSI_FILENAME_TEMPLATE.format(cover_number)
    return ANSI_HEADERS_DIR / cover_file


def render_markdown_to_ansi(md_content: str, width: int = 79) -> str:
    console = Console(
        width=width, record=True, force_terminal=True, color_system="truecolor"
    )
    with console.capture() as cap:
        console.print(Markdown(md_content, code_theme="github-dark"))
    return cap.get()


def load_data_from_md_file(md_file: Path) -> dict:
    md_content = md_file.read_text(encoding="utf-8")
    raw_metadata, raw_body = split_markdown_file(md_content)
    metadata = yaml.safe_load(raw_metadata)
    if not metadata:
        raise KeyError("No properties found in metadata")
    ansi_content = render_markdown_to_ansi(raw_body)
    return {**metadata, "content": ansi_content, "extras": {}}


def get_post_data_from_md_file(md_file: Path) -> dict:
    md_data = load_data_from_md_file(md_file)
    md_post = PostMD(**md_data)
    slug = md_post.slug or get_slug(md_file)
    header_path = get_ansi_header_path(md_post.title)
    header = header_path.read_text(encoding="utf-8")
    reading_time = f"{estimate_reading_time(md_post.content)} min"
    date = md_post.date or get_creation_date(md_file)
    return {
        **md_post.model_dump(),
        "slug": slug,
        "header": header,
        "reading_time": reading_time,
        "date": date,
    }


def get_project_data_from_md_file(md_file: Path) -> dict:
    md_data = load_data_from_md_file(md_file)
    md_project = ProjectMD(**md_data)
    slug = md_project.slug or get_slug(md_file)
    header_path = get_ansi_header_path(md_project.title)
    header = header_path.read_text(encoding="utf-8")
    reading_time = f"{estimate_reading_time(md_project.content)} min"
    date = md_project.date or get_creation_date(md_file)
    return {
        **md_project.model_dump(),
        "slug": slug,
        "header": header,
        "reading_time": reading_time,
        "date": date,
    }


def get_posts_data() -> dict:
    posts = {}
    for md_file in find_markdown_files(POSTS_CONTENT_DIR):
        data = get_post_data_from_md_file(md_file)
        posts[data["slug"]] = data
    return posts


def get_projects_data() -> dict:
    projects = {}
    for md_file in find_markdown_files(PROJECTS_CONTENT_DIR):
        data = get_project_data_from_md_file(md_file)
        projects[data["slug"]] = data
    return projects


@cache
def get_ansi_content() -> dict[str, dict]:
    return {"posts": get_posts_data(), "projects": get_projects_data()}
