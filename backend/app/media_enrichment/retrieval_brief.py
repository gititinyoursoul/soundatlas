import re
from dataclasses import dataclass
from typing import Any


CONCRETE_PLACE_TYPES = {"building", "club", "housing_complex", "park", "venue"}
BROAD_PLACE_TYPES = {"city", "neighborhood", "region"}
DEFAULT_AVOID_TERMS = (
    "ai cover",
    "clip",
    "cover",
    "icon",
    "logo",
    "reaction",
    "shorts",
    "stock photo",
    "tutorial",
)
RISKY_TERM_TOKENS = {
    "bronx",
    "city",
    "culture",
    "hip hop",
    "music",
    "new york",
    "scene",
}


@dataclass(frozen=True)
class RetrievalBrief:
    event_id: str
    route_id: str
    event_title: str
    route_title: str
    place_id: str
    place_name: str
    place_type: str
    year_start: int | None
    year_end: int | None
    year_phrase: str
    tags: tuple[str, ...]
    summary: str
    significance: str
    strong_terms: tuple[str, ...]
    supporting_terms: tuple[str, ...]
    risky_terms: tuple[str, ...]
    avoid_terms: tuple[str, ...]


def build_retrieval_brief(
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
) -> RetrievalBrief:
    event_title = clean_text(event.get("title"))
    route_title = clean_text(route.get("title"))
    place_name = clean_text(place.get("name"))
    place_type = clean_text(place.get("place_type")).casefold()
    place_borough = clean_text(place.get("borough"))
    tags = tuple(
        tag
        for tag in (clean_text(value) for value in event.get("tags", []))
        if tag
    )
    summary = clean_text(event.get("summary"))
    significance = clean_text(event.get("significance"))
    year_start = int_or_none(event.get("year_start"))
    year_end = int_or_none(event.get("year_end"))
    year_phrase = format_year_phrase(year_start, year_end)

    notable_terms = extract_notable_terms(". ".join([event_title, summary, significance]))
    strong_terms = unique_terms(
        [
            event_title,
            place_name if place_type in CONCRETE_PLACE_TYPES else "",
            *notable_terms,
        ],
    )
    supporting_terms = unique_terms(
        [
            route_title,
            place_name if place_type in BROAD_PLACE_TYPES else "",
            place_borough if place_borough not in {"Citywide", "External"} else "",
            "New York" if place_type in CONCRETE_PLACE_TYPES else "",
            year_phrase,
            *tags,
        ],
    )
    risky_terms = tuple(
        term
        for term in unique_terms([*tags, place_name, route_title])
        if term.casefold() in RISKY_TERM_TOKENS
    )

    return RetrievalBrief(
        event_id=clean_text(event.get("id")),
        route_id=clean_text(event.get("route_id")),
        event_title=event_title,
        route_title=route_title,
        place_id=clean_text(event.get("place_id") or place.get("id")),
        place_name=place_name,
        place_type=place_type,
        year_start=year_start,
        year_end=year_end,
        year_phrase=year_phrase,
        tags=tags,
        summary=summary,
        significance=significance,
        strong_terms=strong_terms,
        supporting_terms=supporting_terms,
        risky_terms=risky_terms,
        avoid_terms=DEFAULT_AVOID_TERMS,
    )


def clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", value).strip()


def int_or_none(value: Any) -> int | None:
    return value if isinstance(value, int) else None


def format_year_phrase(year_start: int | None, year_end: int | None) -> str:
    if year_start is None:
        return ""
    if year_end is not None and year_end != year_start:
        return f"{year_start} {year_end}"
    return str(year_start)


def extract_notable_terms(text: str) -> tuple[str, ...]:
    normalized_text = re.sub(r"[.?!;:]+", "\n", text)
    phrases = re.findall(
        r"\b(?:[A-Z][A-Za-z0-9']+)(?:[ \t]+[A-Z][A-Za-z0-9']+)*\b",
        normalized_text,
    )
    return unique_terms(
        phrase
        for phrase in phrases
        if len(phrase) >= 4 and not phrase.casefold().startswith(("the ", "this "))
    )


def unique_terms(values: Any) -> tuple[str, ...]:
    terms: list[str] = []
    seen_terms: set[str] = set()
    for value in values:
        term = clean_text(value)
        if not term:
            continue
        normalized = term.casefold()
        if normalized in seen_terms:
            continue
        terms.append(term)
        seen_terms.add(normalized)
    return tuple(terms)
