from pathlib import Path

# Base directories for project structure
_BASE_DIR = Path(__file__).parent.parent
_CONTENT_DIR = _BASE_DIR / "content"
_STATIC_DIR = _BASE_DIR / "app" / "static"

# Content organization (used to render dynamic pages)
AUTHOR_CONTENT_DIR = _CONTENT_DIR / "author"
AUTHOR_CONTENT_FILE = AUTHOR_CONTENT_DIR / "index.md"
HOMEPAGE_CONTENT_FILE = _CONTENT_DIR / "homepage.md"
META_CONTENT_FILE = _CONTENT_DIR / "meta.md"
POSTS_CONTENT_DIR = _CONTENT_DIR / "posts"
PROJECTS_CONTENT_DIR = _CONTENT_DIR / "projects"

# Directories for cover images
HEADERS_DIR = _STATIC_DIR / "images" / "headers"
THUMBNAILS_DIR = _STATIC_DIR / "images" / "thumbnails"

# Relative references used in templates
STATIC_RELATIVE_DIR = _STATIC_DIR
IMAGES_RELATIVE_DIR = _STATIC_DIR / "images"

# Template for cover images, zero-padded to 3 digits (e.g., cover_001.png)
COVER_FILENAME_TEMPLATE = "cover_{:03d}.png"
