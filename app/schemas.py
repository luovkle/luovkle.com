from pydantic import BaseModel, Field, HttpUrl, field_serializer


class Extras(BaseModel):
    code: bool = False


class Content(BaseModel):
    extras: Extras
    content: str | None = None


class MetadataMD(Content):
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


class HomepageMD(Content):
    posts_section_description: str
    projects_section_description: str


class AuthorMD(Content):
    picture: str
    full_name: str
    role: str
    about: str
    github_url: HttpUrl | None = None
    linkedin_url: HttpUrl | None = None


class PostMD(Content):
    title: str
    description: str | None = None
    slug: str | None = None
    date: str | None = None
    topic: str | None = None


class ProjectMD(Content):
    title: str
    description: str | None = None
    repository: str | None = None
    website: HttpUrl | None = None
    slug: str | None = None
    date: str | None = None
