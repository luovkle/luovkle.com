from typing import TypedDict

from app.schemas import CoverUrls, PostANSIContent, ProjectANSIContent


class HeadersAndThumbnailsDict(TypedDict):
    headers: CoverUrls
    thumbnails: CoverUrls


class ANSIContent(TypedDict):
    posts: dict[str, PostANSIContent]
    projects: dict[str, ProjectANSIContent]
