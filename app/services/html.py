from functools import cache
from pathlib import Path

import markdown
import yaml
from bs4 import BeautifulSoup

from app.config import (
    AUTHOR_CONTENT_DIR,
    AUTHOR_CONTENT_FILE,
    COVER_FILENAME_TEMPLATE,
    HEADERS_DIR,
    HOMEPAGE_CONTENT_FILE,
    IMAGES_RELATIVE_DIR,
    META_CONTENT_FILE,
    POSTS_CONTENT_DIR,
    PROJECTS_CONTENT_DIR,
    STATIC_RELATIVE_DIR,
    THUMBNAILS_DIR,
)
from app.schemas import AuthorMD, HomepageMD, MetadataMD, PostMD, ProjectMD
from app.services.common import (
    estimate_reading_time,
    find_markdown_files,
    get_cover_number,
    get_creation_date,
    get_slug,
    split_markdown_file,
)


def get_alternative_file_formats(original_file_path: Path) -> dict[str, Path]:
    alt_files = {}
    for suffix in ("avif", "webp"):
        alt_file = original_file_path.with_suffix(f".{suffix}")
        if alt_file.is_file():
            alt_files[suffix] = alt_file
    return alt_files


def collect_relative_image_urls(
    default_path: Path, alternative_paths: dict[str, Path]
) -> dict[str, str | None]:
    cover_paths = {"default": default_path, **alternative_paths}
    cover_urls = {}
    for name, path in cover_paths.items():
        cover_urls[name] = str(path.relative_to(STATIC_RELATIVE_DIR))
    return cover_urls


def get_cover_urls(covers_path: Path, title: str) -> dict[str, str | None]:
    #
    number_of_covers = len(list(covers_path.glob("*.png")))
    cover_number = get_cover_number(len(title), number_of_covers)
    cover_file = COVER_FILENAME_TEMPLATE.format(cover_number)
    #
    default_cover_path = covers_path / cover_file
    alt_cover_paths = get_alternative_file_formats(default_cover_path)
    return collect_relative_image_urls(default_cover_path, alt_cover_paths)


def get_headers_and_thumbnails(title: str) -> dict[str, dict[str, str | None]]:
    return {
        "headers": get_cover_urls(HEADERS_DIR, title),
        "thumbnails": get_cover_urls(THUMBNAILS_DIR, title),
    }


def copy_pictures_to_static_dir(picture_content_path: Path) -> Path:
    picture_parent, picture = picture_content_path.parts[-2:]
    static_path = IMAGES_RELATIVE_DIR / picture_parent
    if not static_path.is_dir():
        static_path.mkdir()
    picture_static_path = static_path / picture
    if not picture_static_path.exists():
        picture_static_path.write_bytes(picture_content_path.read_bytes())
    return picture_static_path


def update_base_html(html):
    soup = BeautifulSoup(html, "html.parser")
    extras = {"code": False}
    # Check for <code> tags
    code_blocks = soup.find_all("code")
    if len(code_blocks) >= 1:
        extras["code"] = True
    # Update <a> tags
    tags = soup.find_all("a")
    for tag in tags:
        tag.attrs["class"] = "text-sky-500 font-bold"  # type: ignore
        tag.attrs["target"] = "_blank"  # type: ignore
        tag.attrs["rel"] = "noopener noreferrer"  # type: ignore
    # Update <h1> tags
    for tag in soup.find_all("h1"):
        tag.attrs["class"] = "text-4xl font-black"
    # Update <h2> tags
    for tag in soup.find_all("h2"):
        tag.attrs["class"] = "text-3xl font-black"
    # Update <h3> tags
    for tag in soup.find_all("h3"):
        tag.attrs["class"] = "text-2xl font-black"
    # Update <h4> tags
    for tag in soup.find_all("h4"):
        tag.attrs["class"] = "text-xl font-black"
    # Update <h5> tags
    for tag in soup.find_all("h5"):
        tag.attrs["class"] = "text-xl font-bold"
    # Update <h6> tags
    for tag in soup.find_all("h6"):
        tag.attrs["class"] = "text-lg font-bold"
    # Update <blockquote> tags
    for tag in soup.find_all("blockquote"):
        tag.attrs["class"] = (
            "bg-neutral-900 px-4 py-2 italic rounded-md text-base font-medium"
        )
    # Update <ul> tags
    for tag in soup.find_all("ul"):
        tag.attrs["class"] = "ps-5 space-y-1 list-disc list-inside"
    # Update <li> tags
    for tag in soup.find_all("ol"):
        tag.attrs["class"] = "ps-5 space-y-1 list-decimal list-inside"
    # Update <img> tags
    for tag in soup.find_all("img"):
        tag.attrs["class"] = "mx-auto"
    # Update <pre> tags
    for tag in soup.find_all("pre"):
        tag.attrs["class"] = "py-3 px-3 text-md overflow-x-auto"
    return {"content": str(soup), "extras": extras}


def get_data_from_markdown_file(md_file: Path):
    md_content = md_file.read_text(encoding="utf-8")
    metadata, body = split_markdown_file(md_content)
    metadata_dict = yaml.safe_load(metadata)
    if not metadata_dict:
        raise KeyError("No properties found in metadata")
    html_body = markdown.markdown(
        body, extensions=["fenced_code", "codehilite"], output_format="html"
    )
    updated_html = update_base_html(html_body)
    return {
        **metadata_dict,
        "content": updated_html["content"],
        "extras": updated_html["extras"],
    }


def get_metadata_content():
    content_md = get_data_from_markdown_file(META_CONTENT_FILE)
    metadata_md = MetadataMD(**content_md)
    headers_and_thumbnails = get_headers_and_thumbnails(metadata_md.author)
    default_thumbnail = headers_and_thumbnails["thumbnails"]["default"]
    return {
        **metadata_md.model_dump(),
        "og_image": metadata_md.og_image or default_thumbnail,
        "twitter_image": metadata_md.twitter_image or default_thumbnail,
    }


def get_author_content():
    content_md = get_data_from_markdown_file(AUTHOR_CONTENT_FILE)
    author_md = AuthorMD(**content_md)
    picture_content_path = AUTHOR_CONTENT_DIR / author_md.picture
    picture_path = copy_pictures_to_static_dir(picture_content_path)
    alt_picture_paths = get_alternative_file_formats(picture_path)
    return {
        **author_md.model_dump(),
        "picture": collect_relative_image_urls(picture_path, alt_picture_paths),
    }


def get_posts_content():
    def get_single_post_data(path):
        content_md = get_data_from_markdown_file(path)
        post_md = PostMD(**content_md)
        headers_and_thumbnails = get_headers_and_thumbnails(post_md.title)
        return {
            **post_md.model_dump(),
            "slug": post_md.slug or get_slug(path),
            "cover_image": headers_and_thumbnails["headers"]["default"],
            "thumbnail": headers_and_thumbnails["thumbnails"]["default"],
            "reading_time": f"{estimate_reading_time(post_md.content)} min",
            "date": post_md.date or get_creation_date(path),
        }

    posts = {}
    post_paths = find_markdown_files(POSTS_CONTENT_DIR)
    for path in post_paths:
        data = get_single_post_data(path)
        posts[data["slug"]] = data
    return posts


def get_projects_content():
    def get_single_project_data(path):
        content_md = get_data_from_markdown_file(path)
        project_md = ProjectMD(**content_md)
        headers_and_thumbnails = get_headers_and_thumbnails(project_md.title)
        return {
            **project_md.model_dump(),
            "slug": project_md.slug or get_slug(path),
            "cover_image": headers_and_thumbnails["headers"]["default"],
            "thumbnail": headers_and_thumbnails["thumbnails"]["default"],
            "reading_time": f"{estimate_reading_time(project_md.content)} min",
            "date": project_md.date or get_creation_date(path),
        }

    projects = {}
    project_paths = find_markdown_files(PROJECTS_CONTENT_DIR)
    for path in project_paths:
        data = get_single_project_data(path)
        projects[data["slug"]] = data
    return projects


def get_homepage_data(posts_data, projects_data):
    path = Path(HOMEPAGE_CONTENT_FILE)
    content_md = get_data_from_markdown_file(path)
    homepage_md = HomepageMD(**content_md)
    posts_headers_and_thumbnails = get_headers_and_thumbnails("posts")
    projects_headers_and_thumbnails = get_headers_and_thumbnails("projects")
    return {
        "posts_section": {
            "description": homepage_md.posts_section_description,
            "entries": str(len(posts_data)),
            "thumbnail": posts_headers_and_thumbnails["thumbnails"],
        },
        "projects_section": {
            "description": homepage_md.projects_section_description,
            "entries": str(len(projects_data)),
            "thumbnail": projects_headers_and_thumbnails["thumbnails"],
        },
    }


@cache
def get_content():
    data = {
        "metadata": get_metadata_content(),
        "author": get_author_content(),
        "posts": get_posts_content(),
        "projects": get_projects_content(),
    }
    data["homepage"] = get_homepage_data(data["posts"], data["projects"])
    return data
