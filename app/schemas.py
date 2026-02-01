from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl, computed_field, field_serializer


class Extras(BaseModel):
    code: bool = False


class ContentMD(BaseModel):
    extras: Extras
    content: str | None = None


class MetadataMD(ContentMD):
    # SEO
    description: str
    keywords: list[str] = Field(min_length=1)
    author: str
    language: list[str] = Field(min_length=1)
    robots: list[str] = Field(min_length=1)
    # Social Media
    og_title: str = Field(alias="og:title")
    og_description: str = Field(alias="og:description")
    og_image: HttpUrl | None = Field(None, alias="og:image")
    og_url: HttpUrl = Field(alias="og:url")
    og_type: str = Field(alias="og:type")
    og_locale: str = Field(alias="og:locale")
    # Twitter
    twitter_card: str = Field(alias="twitter:card")
    twitter_title: str = Field(alias="twitter:title")
    twitter_description: str = Field(alias="twitter:description")
    twitter_image: HttpUrl | None = Field(None, alias="twitter:image")
    twitter_creator: str = Field(alias="twitter:creator")

    @field_serializer("keywords")
    def serialize_keyworkds(self, keywords: list[str]):
        return ", ".join(keywords)

    @field_serializer("language")
    def serialize_language(self, language: list[str]):
        return ", ".join(language)

    @field_serializer("robots")
    def serialize_robots(self, robots: list[str]):
        return ", ".join(robots)


class HomepageMD(ContentMD):
    posts_section_description: str
    projects_section_description: str


class AuthorMD(ContentMD):
    picture: str
    full_name: str
    role: str
    about: str
    github_url: HttpUrl | None = None
    linkedin_url: HttpUrl | None = None


class PostMD(ContentMD):
    title: str
    description: str | None = None
    slug: str | None = None
    date: str | None = None
    topic: str | None = None


class ProjectMD(ContentMD):
    title: str
    description: str | None = None
    repository: str | None = None
    website: HttpUrl | None = None
    slug: str | None = None
    date: str | None = None


class ContentContext(BaseModel):
    """Context information required to process a specific content item.

    Attributes:
        index_file: Path to the Markdown file to render (for directories this
            is typically `<dir>/index.md`; for files, it is the file itself).
        img_files: Optional list of image files discovered under `<dir>/images`.
            May be None when the item is a standalone Markdown file.
        is_dir: Whether the content item is a directory-based content unit.
        content_type: Logical type or category for the content (e.g., "posts",
            "pages"); used to build the final static path.
    """

    index_file: Path
    img_files: list[Path] | None = None
    is_dir: bool = False
    content_type: str


class Content(BaseModel):
    """Rendered content payload.

    Attributes:
        title: Optional title extracted from the file or directory name.
        content: HTML rendered from Markdown, with image paths rewritten if needed.
    """

    title: str | None = None
    content: str


class CoverUrls(BaseModel):
    default: Path
    avif: Path | None = None
    webp: Path | None = None

    @computed_field
    @property
    def default_url(self) -> str:
        return str(self.default)

    @computed_field
    @property
    def avif_url(self) -> str | None:
        return str(self.avif) if self.avif else None

    @computed_field
    @property
    def webp_url(self) -> str | None:
        return str(self.webp) if self.webp else None
