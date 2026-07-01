import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.media_enrichment.retrieval_brief import (
    CONCRETE_PLACE_TYPES,
    DEFAULT_AVOID_TERMS,
    RISKY_TERM_TOKENS,
    RetrievalBrief,
    build_retrieval_brief,
    clean_text,
    format_year_phrase,
    unique_terms,
)


EventType = Literal[
    "scene_context",
    "technique_development",
    "symbolic_event",
    "scene_organization",
    "historical_context",
    "release",
    "venue_crossover",
]
WorkType = Literal["track", "album", "film", "documentary", "release", "unknown"]

BROAD_ONLY_TERMS = {
    "bronx",
    "city",
    "culture",
    "hip hop",
    "music",
    "new york",
    "nyc",
    "scene",
}
ARTIST_MARKERS = {"afrika", "bambaataa", "dj", "flash", "force", "gang", "herc", "kool"}
TECHNIQUE_TERMS = {
    "backspin",
    "b-boying",
    "breakbeat",
    "djing",
    "mixing",
    "punch phrasing",
    "sound systems",
    "turntablism",
}
GENRE_TAGS = {"disco", "funk", "hip-hop", "loft-jazz", "no-wave", "post-punk", "rap", "salsa"}
PRACTICE_TAGS = {
    "block-party",
    "club-culture",
    "dj-culture",
    "improvisation",
    "sound-system",
}
FILM_KEYWORDS = {"documentary", "feature film", "film", "movie"}
RELEASE_KEYWORDS = {"album", "charts", "record", "release", "single", "track"}


class EventSearchWork(BaseModel):
    title: str
    type: WorkType = "unknown"


class EventSearchEntities(BaseModel):
    artists: list[str] = Field(default_factory=list)
    places: list[str] = Field(default_factory=list)
    works: list[EventSearchWork] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    techniques: list[str] = Field(default_factory=list)
    historical_events: list[str] = Field(default_factory=list)

    @field_validator("works", mode="before")
    @classmethod
    def normalize_works(cls, value: Any) -> Any:
        if not isinstance(value, list):
            return value
        normalized = []
        for item in value:
            if isinstance(item, str):
                normalized.append({"title": item, "type": "unknown"})
            else:
                normalized.append(item)
        return normalized


class EventSearchContext(BaseModel):
    genres: list[str] = Field(default_factory=list)
    scenes: list[str] = Field(default_factory=list)
    communities: list[str] = Field(default_factory=list)
    practices: list[str] = Field(default_factory=list)
    industry_terms: list[str] = Field(default_factory=list)
    route_terms: list[str] = Field(default_factory=list)


class EventSearchTimeContext(BaseModel):
    year_start: int | None = None
    year_end: int | None = None
    query_year_phrase: str = ""


class EventSearchControl(BaseModel):
    strong_terms: list[str] = Field(default_factory=list)
    supporting_terms: list[str] = Field(default_factory=list)
    risky_terms: list[str] = Field(default_factory=list)
    avoid_terms: list[str] = Field(default_factory=list)


class EventSearchComponent(BaseModel):
    event_id: str
    event_type: EventType = "scene_context"
    entities: EventSearchEntities = Field(default_factory=EventSearchEntities)
    context: EventSearchContext = Field(default_factory=EventSearchContext)
    time_context: EventSearchTimeContext = Field(default_factory=EventSearchTimeContext)
    search_control: EventSearchControl = Field(default_factory=EventSearchControl)
    review_notes: list[str] = Field(default_factory=list)


class ComponentValidationReport(BaseModel):
    event_id: str
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def build_event_search_component(
    *,
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
) -> EventSearchComponent:
    brief = build_retrieval_brief(event=event, route=route, place=place)
    text = combined_text(event, route, place)
    tags = normalized_tags(event)
    works = infer_works(text)
    artists = infer_artist_terms(brief)
    places = infer_place_terms(place)
    organizations = infer_organizations(place, text)
    techniques = infer_techniques(text, tags)
    context = infer_context(route=route, tags=tags, text=text)
    risky_terms = unique_strings(
        [
            *brief.risky_terms,
            *(term for term in brief.supporting_terms if term.casefold() in RISKY_TERM_TOKENS),
        ],
    )

    return EventSearchComponent(
        event_id=brief.event_id,
        event_type=infer_event_type(event=event, text=text, works=works, techniques=techniques),
        entities=EventSearchEntities(
            artists=artists,
            places=places,
            works=works,
            organizations=organizations,
            techniques=techniques,
            historical_events=[],
        ),
        context=context,
        time_context=EventSearchTimeContext(
            year_start=brief.year_start,
            year_end=brief.year_end,
            query_year_phrase=brief.year_phrase,
        ),
        search_control=EventSearchControl(
            strong_terms=unique_strings(
                [
                    *artists,
                    *(work.title for work in works),
                    *organizations,
                    *brief.strong_terms,
                ],
            ),
            supporting_terms=unique_strings([*brief.supporting_terms, *places]),
            risky_terms=risky_terms,
            avoid_terms=list(DEFAULT_AVOID_TERMS),
        ),
        review_notes=build_review_notes(brief=brief, works=works, text=text),
    )


def retrieval_brief_from_component(
    *,
    component: EventSearchComponent,
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
) -> RetrievalBrief:
    fallback = build_retrieval_brief(event=event, route=route, place=place)
    time_context = component.time_context
    return RetrievalBrief(
        event_id=component.event_id or fallback.event_id,
        route_id=clean_text(event.get("route_id")) or fallback.route_id,
        event_title=clean_text(event.get("title")) or fallback.event_title,
        route_title=clean_text(route.get("title")) or fallback.route_title,
        place_id=clean_text(event.get("place_id") or place.get("id")) or fallback.place_id,
        place_name=clean_text(place.get("name")) or fallback.place_name,
        place_type=clean_text(place.get("place_type")).casefold() or fallback.place_type,
        year_start=time_context.year_start if time_context.year_start is not None else fallback.year_start,
        year_end=time_context.year_end if time_context.year_end is not None else fallback.year_end,
        year_phrase=time_context.query_year_phrase or fallback.year_phrase,
        tags=tuple(clean_text(value) for value in event.get("tags", []) if clean_text(value)),
        summary=clean_text(event.get("summary")) or fallback.summary,
        significance=clean_text(event.get("significance")) or fallback.significance,
        strong_terms=tuple(component.search_control.strong_terms) or fallback.strong_terms,
        supporting_terms=tuple(component.search_control.supporting_terms)
        or fallback.supporting_terms,
        risky_terms=tuple(component.search_control.risky_terms),
        avoid_terms=tuple(component.search_control.avoid_terms) or fallback.avoid_terms,
    )


def validate_component_for_seed(
    *,
    component: EventSearchComponent,
    event: dict[str, Any] | None,
    place: dict[str, Any] | None = None,
) -> ComponentValidationReport:
    report = ComponentValidationReport(event_id=component.event_id)
    if event is None:
        report.errors.append(f"Component references unknown event '{component.event_id}'.")
        return report

    expected_year_phrase = format_year_phrase(
        event.get("year_start") if isinstance(event.get("year_start"), int) else None,
        event.get("year_end") if isinstance(event.get("year_end"), int) else None,
    )
    if component.time_context.query_year_phrase != expected_year_phrase:
        report.errors.append(
            "time_context.query_year_phrase must match the event year range "
            f"('{expected_year_phrase}').",
        )

    strong_terms = [
        term
        for term in component.search_control.strong_terms
        if clean_text(term)
    ]
    if strong_terms and all(term.casefold() in BROAD_ONLY_TERMS for term in strong_terms):
        report.warnings.append("strong_terms only contains broad terms.")
    if not strong_terms:
        report.warnings.append("search_control.strong_terms is empty.")
    if not has_precise_enrichment_anchor(component=component, strong_terms=strong_terms):
        report.warnings.append(
            "no precise enrichment anchors found; add a specific artist, work, organization, technique, or historical event.",
        )

    if place:
        place_type = clean_text(place.get("place_type")).casefold()
        if not component.entities.places:
            report.warnings.append("entities.places is empty.")
        if place_type in CONCRETE_PLACE_TYPES:
            place_terms = " ".join(component.entities.places).casefold()
            borough = clean_text(place.get("borough")).casefold()
            has_city_context = any(term in place_terms for term in ("new york", "nyc"))
            has_borough_context = bool(borough and borough not in {"citywide", "external"} and borough in place_terms)
            if not has_city_context and not has_borough_context:
                report.warnings.append("concrete place lacks borough or city disambiguation.")

    for work in component.entities.works:
        if work.type == "unknown":
            report.warnings.append(f"work '{work.title}' has unknown type.")

    text = combined_text(event, {}, {})
    tag_names = [
        tag.replace("-", " ")
        for tag in event.get("tags", [])
        if isinstance(tag, str) and any(marker in tag.casefold() for marker in ARTIST_MARKERS)
    ]
    for tag_name in tag_names:
        if tag_name.casefold() not in text.casefold():
            report.warnings.append(
                f"tag '{tag_name}' looks retrieval-critical but is missing from event prose.",
            )

    return report


def has_precise_enrichment_anchor(
    *,
    component: EventSearchComponent,
    strong_terms: list[str],
) -> bool:
    if (
        component.entities.artists
        or component.entities.works
        or component.entities.organizations
        or component.entities.techniques
        or component.entities.historical_events
    ):
        return True
    return any(term.casefold() not in BROAD_ONLY_TERMS for term in strong_terms)


def load_component(path: Path) -> EventSearchComponent:
    return EventSearchComponent.model_validate_json(path.read_text(encoding="utf-8"))


def component_path_for_event(component_dir: Path, event_id: str) -> Path:
    return component_dir / f"{event_id}.json"


def infer_event_type(
    *,
    event: dict[str, Any],
    text: str,
    works: list[EventSearchWork],
    techniques: list[str],
) -> EventType:
    normalized = text.casefold()
    tags = set(normalized_tags(event))
    if works and any(work.type in {"track", "album", "release"} for work in works):
        return "release"
    if works and any(work.type in {"film", "documentary"} for work in works):
        return "historical_context"
    if techniques:
        return "technique_development"
    if {"label", "media", "radio"} & tags:
        return "scene_organization"
    if "club" in normalized or "crossover" in normalized:
        return "venue_crossover"
    if "origin" in normalized or "symbolic" in normalized:
        return "symbolic_event"
    return "scene_context"


def infer_artist_terms(brief: RetrievalBrief) -> list[str]:
    terms = []
    for term in brief.strong_terms:
        if term == brief.event_title:
            continue
        normalized = term.casefold().replace("-", " ")
        tokens = set(normalized.split())
        if tokens & ARTIST_MARKERS:
            terms.append(term)
    return unique_strings(terms)


def infer_place_terms(place: dict[str, Any]) -> list[str]:
    place_name = clean_text(place.get("name"))
    borough = clean_text(place.get("borough"))
    terms = [place_name]
    if borough and borough not in {"Citywide", "External"}:
        terms.append(borough)
    if place_name and "new york" not in place_name.casefold():
        terms.append("New York")
    return unique_strings(terms)


def infer_works(text: str) -> list[EventSearchWork]:
    works = []
    for term in extract_quoted_terms(text):
        works.append(EventSearchWork(title=term, type=infer_work_type(term, text)))
    return dedupe_works(works)


def infer_work_type(work: str, text: str) -> WorkType:
    normalized = text.casefold()
    work_context = context_window(work, text).casefold()
    if any(keyword in work_context or keyword in normalized for keyword in FILM_KEYWORDS):
        return "film"
    if any(keyword in work_context or keyword in normalized for keyword in RELEASE_KEYWORDS):
        return "release"
    return "unknown"


def infer_organizations(place: dict[str, Any], text: str) -> list[str]:
    place_name = clean_text(place.get("name"))
    place_type = clean_text(place.get("place_type")).casefold()
    organizations = []
    if place_name and place_type in {"label", "media_node", "arts_institution"}:
        organizations.append(place_name)
    if "records" in text.casefold() and place_name:
        organizations.append(place_name)
    return unique_strings(organizations)


def infer_techniques(text: str, tags: list[str]) -> list[str]:
    normalized = text.casefold().replace("-", " ")
    terms = []
    for term in TECHNIQUE_TERMS:
        if term in normalized or term.replace(" ", "-") in tags:
            terms.append(term)
    return unique_strings(terms)


def infer_context(
    *,
    route: dict[str, Any],
    tags: list[str],
    text: str,
) -> EventSearchContext:
    normalized = text.casefold().replace("-", " ")
    return EventSearchContext(
        genres=unique_strings(tag.replace("-", " ") for tag in tags if tag in GENRE_TAGS),
        scenes=unique_strings(
            term
            for term in (
                "Bronx hip-hop" if "bronx" in normalized and "hip hop" in normalized else "",
                "early hip-hop" if "early hip hop" in normalized else "",
            )
            if term
        ),
        practices=unique_strings(tag.replace("-", " ") for tag in tags if tag in PRACTICE_TAGS),
        industry_terms=unique_strings(
            tag.replace("-", " ")
            for tag in tags
            if tag in {"industry", "label", "mainstream", "media", "radio"}
        ),
        route_terms=unique_strings([clean_text(route.get("title"))]),
    )


def build_review_notes(
    *,
    brief: RetrievalBrief,
    works: list[EventSearchWork],
    text: str,
) -> list[str]:
    notes = []
    if any(term.casefold() in BROAD_ONLY_TERMS for term in brief.supporting_terms):
        notes.append("Check broad place or scene matches carefully during review.")
    for work in works:
        if work.type == "unknown":
            notes.append(f"Confirm what kind of work '{work.title}' is before query planning.")
    if "playlist" in text.casefold():
        notes.append("Check playlist era and historical fit before accepting candidates.")
    return unique_strings(notes)


def normalized_tags(event: dict[str, Any]) -> list[str]:
    return [
        tag.casefold()
        for tag in event.get("tags", [])
        if isinstance(tag, str) and tag.strip()
    ]


def combined_text(
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
) -> str:
    return " ".join(
        term
        for term in (
            clean_text(event.get("title")),
            clean_text(event.get("summary")),
            clean_text(event.get("significance")),
            " ".join(tag.replace("-", " ") for tag in event.get("tags", []) if isinstance(tag, str)),
            clean_text(route.get("title")),
            clean_text(place.get("name")),
        )
        if term
    )


def extract_quoted_terms(text: str) -> list[str]:
    terms = [
        clean_text(match.group(1))
        for match in re.finditer(r"(?<!\w)'((?:[^']|'(?=\w)){3,}?)'(?!\w)", text)
    ]
    terms.extend(
        clean_text(match.group(1))
        for match in re.finditer(r'"([^"]{3,})"', text)
    )
    return unique_strings(terms)


def context_window(term: str, text: str, width: int = 80) -> str:
    index = text.casefold().find(term.casefold())
    if index == -1:
        return text
    start = max(index - width, 0)
    end = min(index + len(term) + width, len(text))
    return text[start:end]


def dedupe_works(works: list[EventSearchWork]) -> list[EventSearchWork]:
    deduped = []
    seen = set()
    for work in works:
        key = work.title.casefold()
        if key in seen:
            continue
        deduped.append(work)
        seen.add(key)
    return deduped


def unique_strings(values: Any) -> list[str]:
    return list(unique_terms(values))
