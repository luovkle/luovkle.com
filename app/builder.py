import os
import re
from datetime import datetime
from pathlib import Path

import markdown
import yaml

content_paths = {
    "author": "app/content/author/author.md",
    "posts": "app/content/posts",
    "projects": "app/content/projects",
    "homepage": "app/content/homepage.md",
}

template_paths = {
    "author": "app/templates",
    "posts": "app/templates/posts",
    "projects": "app/templates/projects",
    "homepage": "app/templates",
}

source_paths = {
    "author": "app/sources/author.html",
    "posts": "app/sources/post.html",
    "projects": "app/sources/project.html",
    "homepage": "app/sources/homepage.html",
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


def build_post_template(post_data):
    post_template_source = Path(source_paths["posts"]).read_text()
    replacements = {
        "{{ post.title }}": post_data["title"],
        "{{ post.reading_time }}": post_data["reading_time"],
        "{{ post.date }}": post_data["date"],
        "{{ post.content }}": post_data["content"],
        "{{ post.slug }}": post_data["slug"],
        "{{ post.cover_image }}": post_data["cover_image"],
    }
    template = render_source(post_template_source, replacements)
    slug = post_data["slug"].replace("-", "_")
    template_path = Path(f"{template_paths['posts']}/{slug}.html")
    template_path.write_text(template)
    return Path(*template_path.parts[-2:])


def build_project_template(project_data):
    project_template_source = Path(source_paths["projects"]).read_text()
    replacements = {
        "{{ project.title }}": project_data["title"],
        "{{ project.reading_time }}": project_data["reading_time"],
        "{{ project.date }}": project_data["date"],
        "{{ project.content }}": project_data["content"],
        "{{ project.slug }}": project_data["slug"],
        "{{ project.cover_image }}": project_data["cover_image"],
        "{{ project.website }}": project_data["website"],
    }
    if project_data.get("repository"):
        replacements["{{ project.repository }}"] = project_data["repository"]
    template = render_source(project_template_source, replacements)
    if not project_data.get("repository"):
        pattern = r'<a\s+[^>]*href="{{\s*project\.repository\s*}}".*?>.*?</a>'
        template = re.sub(pattern, "", template, flags=re.DOTALL)
    slug = project_data["slug"].replace("-", "_")
    template_path = Path(f"{template_paths['projects']}/{slug}.html")
    template_path.write_text(template)
    return Path(*template_path.parts[-2:])


def build_author_template(author_data):
    author_template_source = Path(source_paths["author"]).read_text()
    replacements = {
        "{{ author.full_name }}": author_data["full_name"],
        "{{ author.role }}": author_data["role"],
        "{{ author.about }}": author_data["about"],
        "{{ author.linkedin_url }}": author_data["linkedin_url"],
        "{{ author.github_url }}": author_data["github_url"],
        "{{ author.picture }}": author_data["picture"],
    }
    template = render_source(author_template_source, replacements)
    template_path = Path(f"{template_paths['author']}/author.html")
    template_path.write_text(template)


def build_homepage_template(homepage_data, author_data, posts_data, projects_data):
    homepage_template_source = Path(source_paths["homepage"]).read_text()
    replacements = {
        "{{ author.full_name }}": author_data["full_name"],
        "{{ author.role }}": author_data["role"],
        "{{ posts_section.cover_image }}": get_cover("posts")["thumbnail"],
        "{{ posts_section.entries }}": str(len(posts_data)),
        "{{ posts_section.description }}": homepage_data["posts_section_description"],
        "{{ projects_section.cover_image }}": get_cover("projects")["thumbnail"],
        "{{ projects_section.entries }}": str(len(projects_data)),
        "{{ projects_section.description }}": homepage_data[
            "projects_section_description"
        ],
    }
    template = render_source(homepage_template_source, replacements)
    template_path = Path(f"{template_paths['homepage']}/homepage.html")
    template_path.write_text(template)


def build_content():
    content_template_paths = {
        "posts": {},
        "projects": {},
    }
    # Create directories for templates
    for template_path in template_paths.values():
        path = Path(template_path)
        if not path.is_dir():
            path.mkdir()
    # Build templates for posts
    post_paths = find_markdown_files(content_paths["posts"])
    posts_data = []
    for path in post_paths:
        data = get_data_from_markdown_file(path)
        cover = get_cover(data["title"])
        data = {
            **data,
            "cover_image": cover["header"],
            "thumbnail": cover["thumbnail"],
            "reading_time": get_reading_time(data["content"]),
            "date": get_creation_date(path),
        }
        template_path = build_post_template(data)
        content_template_paths["posts"][data["slug"]] = {
            "slug": data["slug"],
            "template": str(template_path),
            "cover_image": data["cover_image"],
            "title": data["title"],
            "topic": data["topic"],
            "reading_time": data["reading_time"],
            "date": data["date"],
        }
        posts_data.append(data)
    # Build templates for projects
    project_paths = find_markdown_files(content_paths["projects"])
    projects_data = []
    for path in project_paths:
        data = get_data_from_markdown_file(path)
        cover = get_cover(data["title"])
        data = {
            **data,
            "cover_image": cover["header"],
            "thumbnail": cover["thumbnail"],
            "reading_time": get_reading_time(data["content"]),
            "date": get_creation_date(path),
        }
        template_path = build_project_template(data)
        content_template_paths["projects"][data["slug"]] = {
            "slug": data["slug"],
            "template": str(template_path),
            "cover_image": data["cover_image"],
            "title": data["title"],
            "description": data["description"],
            "repository": data.get("repository"),
            "reading_time": data["reading_time"],
            "date": data["date"],
        }
        projects_data.append(data)
    # Build template for author
    author_path = Path(content_paths["author"])
    author_data = get_data_from_markdown_file(author_path)
    build_author_template(author_data)
    # Build template for homepage
    homepage_path = Path(content_paths["homepage"])
    homepage_data = get_data_from_markdown_file(homepage_path)
    build_homepage_template(homepage_data, author_data, posts_data, projects_data)
    return content_template_paths
