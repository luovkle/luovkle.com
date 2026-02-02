from functools import cache
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

from app.config import (
    ANSI_HEADERS_DIR,
    COVER_ANSI_FILENAME_TEMPLATE,
    HEADERS_DIR,
    POSTS_CONTENT_DIR,
    PROJECTS_CONTENT_DIR,
)
from app.schemas import (
    ContentContext,
    GenericANSIContent,
    PostANSIContent,
    ProjectANSIContent,
)
from app.services.common import (
    estimate_reading_time,
    get_content_context,
    get_content_objects,
    get_cover_number,
    get_creation_date,
    get_slug,
    load_markdown_content,
    move_image,
)
from app.types import ANSIContent


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


def _get_generic_ansi_content(
    content_context: ContentContext,
) -> GenericANSIContent:
    index_path: Path = content_context.index_file
    if not index_path.is_file():
        raise FileNotFoundError(f"index file not found: {index_path!s}")
    # Derive a human-friendly title from the filename or the directory name.
    title = index_path.parent.stem if content_context.is_dir else index_path.stem
    # If the context provides images, copy them into the static images directory.
    if content_context.img_files:
        move_image(content_context)
    # Load markdown content and metadata from the source file
    markdown_content = load_markdown_content(content_context.index_file)
    # Parse markdown only if a body exists; otherwise use safe defaults
    if markdown_content.body:
        body = render_markdown_to_ansi(markdown_content.body)
    else:
        body = None
    # Resolve derived fields and fallbacks
    slug = markdown_content.slug or get_slug(content_context.index_file)
    reading_time_minutes = estimate_reading_time(markdown_content.body)
    publish_date = markdown_content.date or get_creation_date(
        content_context.index_file
    )
    header_path = get_ansi_header_path(title)
    header = header_path.read_text(encoding="utf-8")
    # Assemble final payload for the published content model
    generic_ansi_content_dict = {
        **markdown_content.model_dump(),
        "slug": slug,
        "header": header,
        "title": title,
        "reading_time_minutes": reading_time_minutes,
        "publish_date": publish_date,
        "body": body,
    }
    return GenericANSIContent(**generic_ansi_content_dict)


def _get_post_ansi_content(content_context: ContentContext) -> PostANSIContent:
    generic_ansi_content = _get_generic_ansi_content(content_context)
    return PostANSIContent(**generic_ansi_content.model_dump())


def _get_project_ansi_content(
    content_context: ContentContext,
) -> ProjectANSIContent:
    generic_ansi_content = _get_generic_ansi_content(content_context)
    return ProjectANSIContent(**generic_ansi_content.model_dump())


def get_posts_content() -> dict[str, PostANSIContent]:
    posts: dict[str, PostANSIContent] = {}
    for content_obj in get_content_objects(POSTS_CONTENT_DIR):
        content_context = get_content_context(content_obj)
        content = _get_post_ansi_content(content_context)
        posts[content.slug] = content
    return posts


def get_projects_content() -> dict[str, ProjectANSIContent]:
    projects: dict[str, ProjectANSIContent] = {}
    for content_obj in get_content_objects(PROJECTS_CONTENT_DIR):
        content_context = get_content_context(content_obj)
        content = _get_project_ansi_content(content_context)
        projects[content.slug] = content
    return projects


@cache
def get_ansi_content() -> ANSIContent:
    return {"posts": get_posts_content(), "projects": get_projects_content()}
