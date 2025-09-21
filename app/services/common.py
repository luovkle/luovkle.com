import os
import re
from datetime import datetime
from pathlib import Path


def get_slug(md_file: Path) -> str:
    file = md_file.name
    return file.removesuffix(".md").replace("_", "-")


def estimate_reading_time(content: str | None = None) -> int:
    # number of words in an post / 200 words per minute
    if not content:
        return 0
    return round(len(content.split()) / 200)


def get_creation_date(md_file: Path) -> str:
    c_time = os.path.getctime(md_file)
    return datetime.fromtimestamp(c_time).strftime("%d.%m.%Y")


def get_cover_number(n: int, max: int) -> int:
    if n > max:
        return get_cover_number(n - max, max)
    return n


def find_markdown_files(dir: Path) -> list[Path]:
    if not dir.is_dir():
        return []
    return list(dir.glob("*.md"))


def split_markdown_file(md_content: str) -> tuple[str, str]:
    metadata_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(metadata_pattern, md_content, re.DOTALL)
    if not match:
        raise ValueError("Could not find the metadata in the markdown file")
    return match.group(1), match.group(2)
