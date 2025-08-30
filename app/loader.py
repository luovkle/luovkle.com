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


def get_cover(title):
    def get_cover_number(n, max):
        if n > max:
            return get_cover_number(n - max, max)
        return n

    covers_path = Path("app/static/images/headers/")
    number_of_covers = len(list(covers_path.glob("*.png")))
    cover_number = get_cover_number(len(title), number_of_covers)
    cover_file = "cover_" + "{:03d}".format(cover_number) + ".png"
    return {
        "header": f"images/headers/{cover_file}",
        "thumbnail": f"images/thumbnails/{cover_file}",
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


def copy_pictures_to_static_dir(picture_content_path):
    picture_parent, picture = picture_content_path.parts[-2:]
    static_path = Path("app/static/images") / picture_parent
    if not static_path.is_dir():
        static_path.mkdir()
    picture_static_path = static_path / picture
    picture_static_path.write_bytes(picture_content_path.read_bytes())
    return str(Path(*picture_static_path.parts[-3:]))


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


def get_meta_data():
    meta_path = Path(content_paths["meta"])
    content_md = get_data_from_markdown_file(meta_path)
    metadata_md = MetadataMD(**content_md)
    default_thumbnail = get_cover(metadata_md.author)["thumbnail"]
    return {
        **metadata_md.model_dump(),
        "og_image": metadata_md.og_image or default_thumbnail,
        "twitter_image": metadata_md.twitter_image or default_thumbnail,
    }


def get_author_data():
    path = Path(content_paths["author"])
    content_md = get_data_from_markdown_file(path)
    author_md = AuthorMD(**content_md)
    picture_content_path = Path(f"content/author/{author_md.picture}")
    return {
        **author_md.model_dump(),
        "picture": copy_pictures_to_static_dir(picture_content_path),
    }


def get_posts_data():
    def get_single_post_data(path):
        content_md = get_data_from_markdown_file(path)
        post_md = PostMD(**content_md)
        cover = get_cover(post_md.title)
        return {
            **post_md.model_dump(),
            "slug": post_md.slug or get_slug(path),
            "cover_image": cover["header"],
            "thumbnail": cover["thumbnail"],
            "reading_time": get_reading_time(post_md.content),
            "date": post_md.date or get_creation_date(path),
        }

    posts = {}
    post_paths = find_markdown_files(content_paths["posts"])
    for path in post_paths:
        data = get_single_post_data(path)
        posts[data["slug"]] = data
    return posts


def get_projects_data():
    def get_single_project_data(path):
        content_md = get_data_from_markdown_file(path)
        project_md = ProjectMD(**content_md)
        cover = get_cover(project_md.title)
        return {
            **project_md.model_dump(),
            "slug": project_md.slug or get_slug(path),
            "cover_image": cover["header"],
            "thumbnail": cover["thumbnail"],
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
    return {
        "posts_section": {
            "description": homepage_md.posts_section_description,
            "entries": str(len(posts_data)),
            "thumbnail": get_cover("posts")["thumbnail"],
        },
        "projects_section": {
            "description": homepage_md.projects_section_description,
            "entries": str(len(projects_data)),
            "thumbnail": get_cover("projects")["thumbnail"],
        },
    }


@cache
def get_content():
    data = {
        "meta": get_meta_data(),
        "author": get_author_data(),
        "posts": get_posts_data(),
        "projects": get_projects_data(),
    }
    data["homepage"] = get_homepage_data(data["posts"], data["projects"])
    return data
