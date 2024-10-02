import os
import re
from datetime import datetime
from pathlib import Path

import markdown
import yaml
from flask import url_for

content_paths = {
    "author": "content/author/author.md",
    "posts": "content/posts",
    "projects": "content/projects",
    "homepage": "content/homepage.md",
    "metadata": "content/metadata.md",
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
    html_body = markdown.markdown(body)
    return {**metadata_dict, "content": html_body}


def get_meta_tags_data():
    metadata_path = Path(content_paths["metadata"])
    metadata_data = get_data_from_markdown_file(metadata_path)
    default_image = get_cover(metadata_data["author"])
    default_image_url = url_for(
        "static", filename=default_image["thumbnail"], _external=True
    )
    return {
        "description": metadata_data["description"],
        "keywords": ", ".join(metadata_data["keywords"]),
        "author": metadata_data["author"],
        "language": ", ".join(metadata_data["language"]),
        "robots": ", ".join(metadata_data["robots"]),
        "og": {
            "title": metadata_data["og:title"],
            "description": metadata_data["og:description"],
            "image": metadata_data.get("og:image") or default_image_url,
            "url": metadata_data["og:url"],
            "type": metadata_data["og:type"],
            "locale": metadata_data["og:locale"],
        },
        "twitter": {
            "card": metadata_data["twitter:card"],
            "title": metadata_data["twitter:title"],
            "description": metadata_data["twitter:description"],
            "image": metadata_data.get("twitter:image") or default_image_url,
            "creator": metadata_data["twitter:creator"],
        },
    }


def get_author_data():
    path = Path(content_paths["author"])
    data = get_data_from_markdown_file(path)
    data["picture"] = f"images/author/{data['picture']}"
    return data


def get_posts_data():
    def get_single_post_data(path):
        data = get_data_from_markdown_file(path)
        cover = get_cover(data["title"])
        return {
            **data,
            "slug": data.get("slug") or get_slug(path),
            "cover_image": cover["header"],
            "thumbnail": cover["thumbnail"],
            "reading_time": get_reading_time(data["content"]),
            "date": data.get("date") or get_creation_date(path),
        }

    posts = {}
    post_paths = find_markdown_files(content_paths["posts"])
    for path in post_paths:
        data = get_single_post_data(path)
        posts[data["slug"]] = data
    return posts


def get_projects_data():
    def get_single_project_data(path):
        data = get_data_from_markdown_file(path)
        cover = get_cover(data["title"])
        return {
            **data,
            "slug": data.get("slug") or get_slug(path),
            "cover_image": cover["header"],
            "thumbnail": cover["thumbnail"],
            "reading_time": get_reading_time(data["content"]),
            "date": data.get("date") or get_creation_date(path),
        }

    projects = {}
    project_paths = find_markdown_files(content_paths["projects"])
    for path in project_paths:
        data = get_single_project_data(path)
        projects[data["slug"]] = data
    return projects


def get_homepage_data(posts_data, projects_data):
    path = Path(content_paths["homepage"])
    data = get_data_from_markdown_file(path)
    return {
        "posts_section": {
            "description": data["posts_section_description"],
            "entries": str(len(posts_data)),
            "cover_image": get_cover("posts")["thumbnail"],
        },
        "projects_section": {
            "description": data["projects_section_description"],
            "entries": str(len(projects_data)),
            "cover_image": get_cover("projects")["thumbnail"],
        },
    }


def get_content_data():
    data = {
        "author": get_author_data(),
        "posts": get_posts_data(),
        "projects": get_projects_data(),
    }
    data["homepage"] = get_homepage_data(data["posts"], data["projects"])
    return data
