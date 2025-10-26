"""Content loading and static asset preparation utilities.

This module provides helpers to:
- Discover content objects (Markdown files and/or directories).
- Build a context for each content item (index file, images, flags).
- Copy (or move) images to a static directory and rewrite <img> src in HTML.
- Render Markdown to HTML and produce a final Content model.

All inline comments are written in English.
Function/class docstrings follow the Google-style format.
"""

import shutil
from pathlib import Path
from urllib.parse import urlsplit

import markdown
from bs4 import BeautifulSoup

from app.config import IMAGES_DIR, STATIC_RELATIVE_DIR
from app.schemas import Content, ContentContext


def get_content_objects(directory: Path) -> list[Path]:
    """Enumerate content objects inside a directory.

    A content object can be either:
    - A subdirectory (expected to contain an `index.md`).
    - A Markdown file with the `.md` suffix.

    Args:
        directory: Directory to scan.

    Returns:
        A list of Paths representing either subdirectories or `.md` files.

    Raises:
        NotADirectoryError: If `directory` is not a directory.
        ValueError: If an entry is a file without `.md` extension or if it has an
            unsupported type.
    """
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a valid directory")
    content: list[Path] = []
    for path in directory.iterdir():
        # Accept nested directories as potential content containers.
        if path.is_dir():
            content.append(path)
        # Accept only Markdown files when the entry is a file.
        elif path.is_file():
            if not path.suffix == ".md":
                raise ValueError(f"Invalid file type: {path.name}")
            content.append(path)
        else:
            # Reject special file types (symlinks to sockets, fifos, etc.).
            raise ValueError(f"Unsupported path type: {path!s}")
    return content


def get_content_context(path: Path) -> ContentContext:
    """Build a ContentContext from a path to a directory or a Markdown file.

    For directories, this expects:
    - An `index.md` inside the directory.
    - An optional `images/` subdirectory with assets.

    Args:
        path: Path to a content directory or a Markdown file.

    Returns:
        A ContentContext with the resolved index file and optional images list.

    Raises:
        FileNotFoundError: If `path` doesn't exist or `index.md` is missing.
        NotADirectoryError: If `images` exists but is not a directory.
        ValueError: If `path` is neither a directory nor a `.md` file.
    """
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path!s}")
    if path.is_dir():
        index_file = path / "index.md"
        if not index_file.is_file():
            raise FileNotFoundError(index_file)
        images_dir = path / "images"
        # If an `images` path exists, validate it is a directory.
        if images_dir.exists() and not images_dir.is_dir():
            raise NotADirectoryError(
                f"'{images_dir.name}' exists but is not a directory"
            )
        img_files = list(images_dir.iterdir()) if images_dir.is_dir() else None
        # The `content_type` is inferred from the parent directory's name.
        return ContentContext(
            index_file=index_file,
            img_files=img_files,
            is_dir=True,
            content_type=path.parent.stem,
        )
    if path.is_file():
        if not path.suffix == ".md":
            raise ValueError(f"Invalid file type: {path.name}")
        return ContentContext(index_file=path, content_type=path.parent.stem)
    # Unsupported path types are explicitly rejected.
    raise ValueError(f"Unsupported path type: {path!s}")


def move_image(content_context: ContentContext) -> list[Path]:
    """Copy image assets from `<dir>/images` into the static images tree.

    This function rebuilds the destination directory (removes any previous
    folder of the same name), then copies all files found in the source images
    directory.

    Note:
        The function name says "move", but the operation performed is a copy
        (`shutil.copy`). If true moving is desired, replace copy with move.

    Args:
        content_context: A ContentContext referencing the `index_file` and the
            content type.

    Returns:
        A list of destination Paths for the copied images.

    Raises:
        NotADirectoryError: If the base content directory is invalid or if
            `images` is not a directory.
        FileNotFoundError: If the images directory is missing or if there are
            no files to copy.
        ValueError: If the destination path is an unsupported type.
        OSError: For underlying filesystem errors (permissions, locks, etc.).
    """
    # Resolve the directory that contains the index file.
    directory = content_context.index_file.parent
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a valid directory")
    images_content_dir = directory / "images"
    if not images_content_dir.exists():
        raise FileNotFoundError(f"Missing images directory: {images_content_dir}")
    if images_content_dir.exists() and not images_content_dir.is_dir():
        raise NotADirectoryError(
            f"'{images_content_dir.name}' exists but is not a directory"
        )
    # Destination: /static/images/<content_type>/<dir_name>
    images_static_dir = IMAGES_DIR / content_context.content_type / directory.name
    # If the destination exists, remove it to ensure a clean state.
    if images_static_dir.exists():
        if images_static_dir.is_dir():
            shutil.rmtree(images_static_dir)
        elif images_static_dir.is_file():
            images_static_dir.unlink()
        else:
            raise ValueError(f"Unsupported path type: {images_static_dir!s}")
    # Create a fresh destination directory (with parents).
    images_static_dir.mkdir(parents=True, exist_ok=False)
    # Find files (non-recursive) to copy from the source images directory.
    image_content_items = list(images_content_dir.iterdir())
    if not image_content_items:
        raise FileNotFoundError(f"No image files found in {images_content_dir}")
    # Copy images to the destination. Track destination paths for the return.
    dst_paths: list[Path] = []
    for src in image_content_items:
        dst = images_static_dir / src.name
        moved_path_str = shutil.copy(src, dst)
        dst_paths.append(Path(moved_path_str))
    return dst_paths


def _is_external_url(src: str) -> bool:
    """Determine whether the given string is an absolute (external) URL.

    An external URL is considered one that includes a scheme (e.g., http/https),
    and:
      - has a network location (netloc), or
      - uses a scheme like `data:` or `mailto:` which is absolute by definition.

    Args:
        src: URL or path string to evaluate.

    Returns:
        True if `src` is an absolute/external URL, otherwise False.

    Raises:
        ValueError: If `src` is not a string or is empty/whitespace.
    """
    if type(src) is not str:
        raise ValueError(f"Expected a string, got {type(src).__name__!r}")
    if not src.strip():
        raise ValueError("URL source cannot be empty or only whitespace")
    parts = urlsplit(src)
    if parts.scheme:
        if parts.netloc or parts.scheme in {"data", "mailto"}:
            return True
    return False


def load_content(content_context: ContentContext) -> Content:
    """Render a content item from Markdown and rewrite local image paths.

    Steps:
      1. Compute a title from the file or parent directory name.
      2. Render Markdown to HTML.
      3. If images are present in the context, copy them to the static dir.
      4. Parse the HTML and rewrite `<img src="...">` for local images to use
         `url_for('static', filename=...)`.

    Args:
        content_context: The ContentContext describing the item to render.

    Returns:
        A Content model with the final HTML and an optional title.

    Raises:
        FileNotFoundError: If the context's index file does not exist.
        ValueError: If image rewriting hits unsupported paths (rare).
        OSError: For filesystem-related errors during image copying.
    """
    index_path: Path = content_context.index_file
    if not index_path.is_file():
        raise FileNotFoundError(f"index file not found: {index_path!s}")
    # Derive a human-friendly title from the filename or the directory name.
    content_title = (
        index_path.parent.stem if content_context.is_dir else index_path.stem
    )
    # Convert Markdown to HTML (no extra extensions enabled here by design).
    md_content = content_context.index_file.read_text(encoding="utf-8")
    html_content = markdown.markdown(md_content)
    # If the context provides images, copy them into the static images directory.
    if content_context.img_files:
        move_image(content_context)
    # Parse rendered HTML to find and rewrite image sources when they are local.
    soup = BeautifulSoup(html_content, "html.parser")
    imgs = soup.find_all("img")
    # Use the directory containing the index file to compute a unique static path.
    directory = content_context.index_file.parent
    for img in imgs:
        img_src_raw = img.get("src")
        img_src_str = str(img_src_raw)  # Normalize to string for checks.
        # Skip empty sources or external URLs (keep as-is).
        if not img_src_raw or _is_external_url(img_src_str):
            continue
        # Only use the filename part to avoid leaking nested relative paths.
        src_name = Path(img_src_str).name
        # Destination: /static/images/<content_type>/<dir_name>/<src_name>
        dest = IMAGES_DIR / content_context.content_type / directory.name / src_name
        # Try to generate a path relative to the static root to feed url_for().
        try:
            rel = dest.relative_to(STATIC_RELATIVE_DIR).as_posix()
        except ValueError:
            # Fallback to a POSIX-style path if relative computation fails.
            rel = dest.as_posix()
        # Inject a Jinja expression that Flask will resolve at render time.
        img["src"] = "{{ url_for('static', filename='" + rel + "') }}"
    return Content(title=content_title, content=str(soup))
