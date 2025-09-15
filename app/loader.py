import os
import re
from datetime import datetime
from functools import cache
from pathlib import Path

import markdown
import yaml
from bs4 import BeautifulSoup

from .schemas import AuthorMD, HomepageMD, MetadataMD, PostMD, ProjectMD

content_paths = {
    "author": "content/author/index.md",
    "posts": "content/posts",
    "projects": "content/projects",
    "homepage": "content/homepage.md",
    "meta": "content/meta.md",
}


def render_source(source, replacements):
    for pattern, replacement in replacements.items():
        source = re.sub(pattern, replacement, source)
    return source


def get_cover_number(n: int, max: int) -> int:
    if n > max:
        return get_cover_number(n - max, max)
    return n


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
        cover_urls[name] = str(path.relative_to("app/static"))
    return cover_urls


def get_cover_urls(covers_path: Path, title: str) -> dict[str, str | None]:
    #
    number_of_covers = len(list(covers_path.glob("*.png")))
    cover_number = get_cover_number(len(title), number_of_covers)
    cover_file = "cover_" + "{:03d}".format(cover_number) + ".png"
    #
    default_cover_path = covers_path / cover_file
    alt_cover_paths = get_alternative_file_formats(default_cover_path)
    return collect_relative_image_urls(default_cover_path, alt_cover_paths)


def get_headers_and_thumbnails(title: str) -> dict[str, dict[str, str | None]]:
    headers_path = Path("app/static/images/headers/")
    thumbnails_path = Path("app/static/images/thumbnails/")
    return {
        "headers": get_cover_urls(headers_path, title),
        "thumbnails": get_cover_urls(thumbnails_path, title),
    }


def get_slug(file_path):
    file = file_path.parts[-1]
    return file.removesuffix(".md").replace("_", "-")


def get_reading_time(content):
    # number of words in an post / 200 words per minute
    reading_time = round(len(content.split()) / 200)
    return f"{reading_time} min"


def get_creation_date(file_path):
    c_time = os.path.getctime(file_path)
    return datetime.fromtimestamp(c_time).strftime("%d.%m.%Y")


def find_markdown_files(path):
    files_path = Path(path)
    if not files_path.is_dir():
        return []
    return list(files_path.glob("*.md"))


def copy_pictures_to_static_dir(picture_content_path: Path) -> Path:
    picture_parent, picture = picture_content_path.parts[-2:]
    static_path = Path("app/static/images") / picture_parent
    if not static_path.is_dir():
        static_path.mkdir()
    picture_static_path = static_path / picture
    picture_static_path.write_bytes(picture_content_path.read_bytes())
    return picture_static_path


def update_base_html(html):
    soup = BeautifulSoup(html, "html.parser")
    extras = {"code": False}
    # Check for <code> tags
    code_blocks = soup.find_all("code")
    if len(code_blocks) >= 1:
        extras["code"] = True
    # Update anchor tags
    tags = soup.find_all("a")
    for tag in tags:
        tag.attrs["class"] = "text-sky-500 font-bold"  # type: ignore
        tag.attrs["target"] = "_blank"  # type: ignore
        tag.attrs["rel"] = "noopener noreferrer"  # type: ignore
    return {"content": str(soup), "extras": extras}


def get_data_from_markdown_file(file_path):
    content = file_path.read_text(encoding="utf-8")
    metadata_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(metadata_pattern, content, re.DOTALL)
    if match:
        metadata = match.group(1)
        body = match.group(2)
    else:
        raise ValueError("Could not find the metadata in the markdown file")
    metadata_dict = yaml.safe_load(metadata)
    if not metadata_dict:
        raise KeyError("No properties found in metadata")
    html_body = markdown.markdown(body, extensions=["extra"])
    updated_html = update_base_html(html_body)
    return {
        **metadata_dict,
        "content": updated_html["content"],
        "extras": updated_html["extras"],
    }


def get_metadata_content():
    meta_path = Path(content_paths["meta"])
    content_md = get_data_from_markdown_file(meta_path)
    metadata_md = MetadataMD(**content_md)
    headers_and_thumbnails = get_headers_and_thumbnails(metadata_md.author)
    default_thumbnail = headers_and_thumbnails["thumbnails"]["default"]
    return {
        **metadata_md.model_dump(),
        "og_image": metadata_md.og_image or default_thumbnail,
        "twitter_image": metadata_md.twitter_image or default_thumbnail,
    }


def get_author_content():
    path = Path(content_paths["author"])
    content_md = get_data_from_markdown_file(path)
    author_md = AuthorMD(**content_md)
    picture_content_path = Path(f"content/author/{author_md.picture}")
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
            "reading_time": get_reading_time(post_md.content),
            "date": post_md.date or get_creation_date(path),
        }

    posts = {}
    post_paths = find_markdown_files(content_paths["posts"])
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
            "reading_time": get_reading_time(project_md.content),
            "date": project_md.date or get_creation_date(path),
        }

    projects = {}
    project_paths = find_markdown_files(content_paths["projects"])
    for path in project_paths:
        data = get_single_project_data(path)
        projects[data["slug"]] = data
    return projects


def get_homepage_data(posts_data, projects_data):
    path = Path(content_paths["homepage"])
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
