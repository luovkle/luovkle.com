from typing import TypedDict

from app.schemas import CoverUrls


class HeadersAndThumbnailsDict(TypedDict):
    headers: CoverUrls
    thumbnails: CoverUrls
