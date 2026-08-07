from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

ContentReviewStatus = Literal["draft", "reviewed"]
# Kept as an input/type alias for downstream callers during the bounded
# migration. Canonical models expose ``content_review_status`` instead.
ReviewStatus = ContentReviewStatus
MediaReviewAction = Literal["reviewed", "reject"]
LinkReviewKind = Literal["media", "image"]
MediaProvider = Literal["youtube", "spotify", "qobuz"]
MediaType = Literal["track", "album", "playlist", "video", "search"]
MediaPlaybackMode = Literal["embed", "external"]
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
GeometryPrecision = Literal["site", "interpretive"]
GeometrySourceType = Literal["external", "curated"]
PlaceRelationshipDirection = Literal["undirected", "forward", "reciprocal"]

Position = tuple[float, float]
LinearRing = list[Position]
PolygonCoordinates = list[LinearRing]
MultiPolygonCoordinates = list[PolygonCoordinates]


def _validate_polygon_coordinates(
    coordinates: PolygonCoordinates,
) -> PolygonCoordinates:
    if not coordinates:
        raise ValueError("Polygon coordinates must contain at least one ring")

    for ring in coordinates:
        if len(ring) < 4:
            raise ValueError("Polygon rings must contain at least four positions")
        if ring[0] != ring[-1]:
            raise ValueError("Polygon rings must be closed")
        for longitude, latitude in ring:
            if longitude < -180 or longitude > 180:
                raise ValueError("geometry longitude must be between -180 and 180")
            if latitude < -90 or latitude > 90:
                raise ValueError("geometry latitude must be between -90 and 90")

    return coordinates


class PolygonGeometry(BaseModel):
    type: Literal["Polygon"]
    coordinates: PolygonCoordinates

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(
        cls,
        coordinates: PolygonCoordinates,
    ) -> PolygonCoordinates:
        return _validate_polygon_coordinates(coordinates)


class MultiPolygonGeometry(BaseModel):
    type: Literal["MultiPolygon"]
    coordinates: MultiPolygonCoordinates

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(
        cls,
        coordinates: MultiPolygonCoordinates,
    ) -> MultiPolygonCoordinates:
        if not coordinates:
            raise ValueError("MultiPolygon coordinates must contain at least one polygon")
        return [_validate_polygon_coordinates(polygon) for polygon in coordinates]


PlaceGeometry = Annotated[
    PolygonGeometry | MultiPolygonGeometry,
    Field(discriminator="type"),
]


class YearRangeMixin(BaseModel):
    year_start: int
    year_end: int

    @model_validator(mode="after")
    def validate_year_range(self):
        if self.year_start > self.year_end:
            raise ValueError("year_start must be less than or equal to year_end")
        return self


class ContentReviewMixin(BaseModel):
    """Human content-review state with a legacy input compatibility shim."""

    content_review_status: ContentReviewStatus

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_review_status(cls, value: Any) -> Any:
        if isinstance(value, dict) and "content_review_status" not in value:
            legacy = value.get("review_status")
            if legacy is not None:
                value = dict(value)
                value["content_review_status"] = legacy
        return value

    @property
    def review_status(self) -> ContentReviewStatus:
        """Read-only compatibility accessor; never emitted in canonical JSON."""

        return self.content_review_status


class Route(ContentReviewMixin, YearRangeMixin):
    id: str
    title: str
    color: str
    creator: str
    summary: str
    thesis: str
    tags: list[str]
    source_urls: list[str]


class Place(ContentReviewMixin):
    id: str
    name: str
    borough: str
    place_type: str
    latitude: float
    longitude: float
    summary: str
    source_urls: list[str]
    geometry: PlaceGeometry | None = None
    geometry_precision: GeometryPrecision | None = None
    geometry_source_type: GeometrySourceType | None = None
    geometry_source_url: str | None = None
    geometry_source_note: str | None = None
    geometry_license: str | None = None

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

    @model_validator(mode="after")
    def validate_geometry_provenance(self):
        provenance_values = (
            self.geometry_precision,
            self.geometry_source_type,
            self.geometry_source_url,
            self.geometry_source_note,
            self.geometry_license,
        )
        if self.geometry is None:
            if any(value is not None for value in provenance_values):
                raise ValueError("geometry provenance requires geometry")
            return self

        if self.geometry_precision is None:
            raise ValueError("geometry_precision is required with geometry")
        if self.geometry_source_type is None:
            raise ValueError("geometry_source_type is required with geometry")
        if not self.geometry_source_note or not self.geometry_source_note.strip():
            raise ValueError("geometry_source_note is required with geometry")
        if self.geometry_source_type == "external":
            if not self.geometry_source_url or not self.geometry_source_url.strip():
                raise ValueError("external geometry requires geometry_source_url")
            if not self.geometry_license or not self.geometry_license.strip():
                raise ValueError("external geometry requires geometry_license")

        return self


class MediaLink(ContentReviewMixin):
    provider: MediaProvider
    type: MediaType
    title: str
    url: str
    query: str
    confidence: float
    playback_mode: MediaPlaybackMode = "embed"
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


class ImageLink(ContentReviewMixin):
    provider: ImageProvider
    type: ImageType
    title: str
    image_url: str
    source_url: str
    rights_status: RightsStatus
    alt_text: str
    query: str
    confidence: float
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


class PlaceRelationship(BaseModel):
    from_place_id: str
    to_place_id: str
    directionality: PlaceRelationshipDirection
    context_label: str
    source_urls: list[str]

    @field_validator("context_label")
    @classmethod
    def validate_context_label(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("context_label must not be empty")
        return value

    @field_validator("source_urls")
    @classmethod
    def validate_source_urls(cls, value: list[str]) -> list[str]:
        if not value or any(not source_url.strip() for source_url in value):
            raise ValueError("place relationships require at least one source URL")
        return value

    @model_validator(mode="after")
    def validate_distinct_places(self):
        if self.from_place_id == self.to_place_id:
            raise ValueError("place relationship endpoints must be distinct")
        return self


class Event(ContentReviewMixin, YearRangeMixin):
    id: str
    route_id: str
    place_id: str
    place_ids: list[str]
    default_place_id: str
    place_relationships: list[PlaceRelationship] = Field(default_factory=list)
    title: str
    summary: str
    significance: str
    tags: list[str]
    source_urls: list[str]
    media_links: list[MediaLink]
    image_links: list[ImageLink]

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_place(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        normalized = dict(value)
        legacy_place_id = normalized.get("place_id")
        place_ids = normalized.get("place_ids")
        default_place_id = normalized.get("default_place_id")

        if place_ids is None and legacy_place_id is not None:
            place_ids = [legacy_place_id]
            normalized["place_ids"] = place_ids
        if default_place_id is None:
            if legacy_place_id is not None:
                default_place_id = legacy_place_id
            elif isinstance(place_ids, list) and place_ids:
                default_place_id = place_ids[0]
            if default_place_id is not None:
                normalized["default_place_id"] = default_place_id
        if legacy_place_id is None and default_place_id is not None:
            normalized["place_id"] = default_place_id

        return normalized

    @model_validator(mode="after")
    def validate_event_places(self):
        if not self.place_ids:
            raise ValueError("place_ids must contain at least one place")
        if len(self.place_ids) != len(set(self.place_ids)):
            raise ValueError("place_ids must contain unique place IDs")
        if self.default_place_id not in self.place_ids:
            raise ValueError("default_place_id must appear in place_ids")
        if self.place_id != self.default_place_id:
            raise ValueError("place_id must equal default_place_id during compatibility")
        return self


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
