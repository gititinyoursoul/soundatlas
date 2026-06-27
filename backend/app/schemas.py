from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


ReviewStatus = Literal["draft", "reviewed"]
MediaReviewAction = Literal["reviewed", "reject"]
LinkReviewKind = Literal["media", "image"]
MediaProvider = Literal["youtube", "spotify", "qobuz"]
MediaType = Literal["track", "album", "playlist", "video", "search"]
ImageProvider = Literal[
    "wikimedia",
    "loc",
    "nypl",
    "internet_archive",
    "cover_art_archive",
    "manual",
]
ImageType = Literal[
    "venue_photo",
    "artist_photo",
    "album_cover",
    "flyer_poster",
    "archive_photo",
    "map_image",
    "press_scan",
]
RightsStatus = Literal[
    "open_license",
    "public_domain",
    "provider_restricted",
    "unknown",
]


class YearRangeMixin(BaseModel):
    year_start: int
    year_end: int

    @model_validator(mode="after")
    def validate_year_range(self):
        if self.year_start > self.year_end:
            raise ValueError("year_start must be less than or equal to year_end")
        return self


class Route(YearRangeMixin):
    id: str
    title: str
    color: str
    creator: str
    summary: str
    thesis: str
    tags: list[str]
    review_status: ReviewStatus
    source_urls: list[str]


class Place(BaseModel):
    id: str
    name: str
    borough: str
    place_type: str
    latitude: float
    longitude: float
    summary: str
    review_status: ReviewStatus
    source_urls: list[str]

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        if value < -90 or value > 90:
            raise ValueError("latitude must be between -90 and 90")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        if value < -180 or value > 180:
            raise ValueError("longitude must be between -180 and 180")
        return value


class MediaLink(BaseModel):
    provider: MediaProvider
    type: MediaType
    title: str
    url: str
    query: str
    confidence: float
    review_status: ReviewStatus
    video_id: str | None = None
    channel_title: str | None = None
    description: str | None = None
    published_at: str | None = None
    reason: str | None = None

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: float) -> float:
        if value < 0 or value > 1:
            raise ValueError("confidence must be between 0 and 1")
        return value


class ImageLink(BaseModel):
    provider: ImageProvider
    type: ImageType
    title: str
    image_url: str
    source_url: str
    rights_status: RightsStatus
    alt_text: str
    query: str
    confidence: float
    review_status: ReviewStatus
    thumbnail_url: str | None = None
    creator: str | None = None
    license: str | None = None
    license_url: str | None = None

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: float) -> float:
        if value < 0 or value > 1:
            raise ValueError("confidence must be between 0 and 1")
        return value


class Event(YearRangeMixin):
    id: str
    route_id: str
    place_id: str
    title: str
    summary: str
    significance: str
    tags: list[str]
    review_status: ReviewStatus
    source_urls: list[str]
    media_links: list[MediaLink]
    image_links: list[ImageLink]


class Connection(BaseModel):
    id: str
    from_event_id: str
    to_event_id: str
    type: str
    summary: str
    review_status: ReviewStatus

    @model_validator(mode="after")
    def validate_distinct_events(self):
        if self.from_event_id == self.to_event_id:
            raise ValueError("from_event_id and to_event_id must be distinct")
        return self


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])


class ErrorResponse(BaseModel):
    detail: str


class MediaLinkReviewRequest(BaseModel):
    url: str
    action: MediaReviewAction


class LinkReviewRequest(MediaLinkReviewRequest):
    kind: LinkReviewKind
