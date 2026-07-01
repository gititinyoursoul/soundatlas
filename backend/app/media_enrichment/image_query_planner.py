import re
from dataclasses import dataclass

from app.media_enrichment.retrieval_brief import (
    CONCRETE_PLACE_TYPES,
    RetrievalBrief,
    clean_text,
    unique_terms,
)


ARTIST_MARKERS = {"dj", "flash", "herc", "bambaataa", "gang", "force", "five"}
BOROUGH_TERMS = ("Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island")
CITY_TERMS = ("New York", "NYC")
FILM_KEYWORDS = {"documentary", "feature film", "film", "movie"}
RELEASE_KEYWORDS = {"album", "charts", "record", "release", "single", "track"}
SCENE_CONTEXT_TERMS = (
    ("hip hop", "hip hop"),
    ("rap", "rap"),
    ("graffiti", "graffiti"),
    ("turntablism", "turntablism"),
    ("block party", "block party"),
    ("breaking", "breaking"),
    ("dj", "DJ"),
)
WORK_STOP_TERMS = {"charts", "records", "industry", "mainstream", "rap"}


@dataclass(frozen=True)
class ImageQueryPlan:
    target_type: str
    priority: int
    query: str
    strong_terms: tuple[str, ...]
    supporting_terms: tuple[str, ...]
    confidence_hint: str
    reason: str
    review_risks: tuple[str, ...]


def plan_image_queries(brief: RetrievalBrief) -> tuple[ImageQueryPlan, ...]:
    plans: list[ImageQueryPlan] = []
    time_terms = time_query_terms(brief)
    primary_time_term = time_terms[0] if time_terms else ""

    if brief.place_type in CONCRETE_PLACE_TYPES and brief.place_name:
        plans.extend(
            build_venue_photo_plans(
                brief=brief,
                time_terms=time_terms,
            ),
        )

    for term in likely_artist_terms(brief):
        plans.extend(
            build_artist_photo_plans(
                artist=term,
                brief=brief,
                time_terms=time_terms,
            ),
        )

    for term in work_terms(brief):
        plans.extend(
            build_work_plans(
                work=term,
                brief=brief,
                primary_time_term=primary_time_term,
            ),
        )

    if brief.event_title:
        plans.extend(
            build_archive_photo_plans(
                brief=brief,
                primary_time_term=primary_time_term,
            )
        )

    return dedupe_plans(plans)


def build_venue_photo_plans(
    brief: RetrievalBrief,
    time_terms: tuple[str, ...],
) -> tuple[ImageQueryPlan, ...]:
    plans = []
    disambiguators = venue_location_disambiguators(brief)
    primary_location = disambiguators[0] if disambiguators else "New York"
    primary_time = time_terms[0] if time_terms else ""
    decade_time = next((term for term in time_terms if term.endswith("s")), "")
    yearly_terms = tuple(term for term in time_terms[2:] if term.isdigit())

    query_specs = []
    if primary_time:
        query_specs.append(
            (f"{brief.place_name} {primary_location} {primary_time}", primary_time, 1, "high"),
        )
    if decade_time:
        query_specs.append(
            (f"{brief.place_name} {primary_location} {decade_time}", decade_time, 2, "medium"),
        )
    for year_term in yearly_terms:
        query_specs.append(
            (f"{brief.place_name} {primary_location} {year_term}", year_term, 3, "medium"),
        )
    query_specs.append((f"{brief.place_name} {primary_location}", "", 4, "medium"))

    for query, time_term, priority, confidence_hint in query_specs:
        supporting_terms = tuple(term for term in (primary_location, time_term) if term)
        plans.append(
            build_plan(
                target_type="venue_photo",
                priority=priority,
                query=query,
                strong_terms=(brief.place_name,),
                supporting_terms=supporting_terms,
                confidence_hint=confidence_hint,
                reason=(
                    "Concrete place query includes city or borough context to reduce "
                    "same-name place matches."
                ),
                review_risks=(
                    "Verify the image shows the correct New York place, not a same-name "
                    "venue or park elsewhere.",
                    "Check the source date and description for wrong-era venue photos.",
                ),
            ),
        )
    return tuple(plans)


def build_artist_photo_plans(
    artist: str,
    brief: RetrievalBrief,
    time_terms: tuple[str, ...],
) -> tuple[ImageQueryPlan, ...]:
    plans = []
    primary_time = time_terms[0] if time_terms else ""
    decade_time = next((term for term in time_terms if term.endswith("s")), "")
    yearly_terms = tuple(term for term in time_terms[2:] if term.isdigit())
    role_term = artist_role_term(artist, brief)
    scene_term = primary_scene_context(brief)

    query_specs = []
    if primary_time:
        query_specs.append((f"{artist} {primary_time}", (primary_time,), 2, "high"))
    if decade_time:
        query_specs.append((f"{artist} {decade_time}", (decade_time,), 3, "medium"))
    for year_term in yearly_terms:
        query_specs.append((f"{artist} {year_term}", (year_term,), 4, "medium"))
    if role_term and primary_time:
        query_specs.append(
            (f"{artist} {role_term} {primary_time}", (role_term, primary_time), 5, "medium"),
        )
    if scene_term:
        query_specs.append((f"{artist} {scene_term}", (scene_term,), 6, "medium"))
    query_specs.append((artist, (), 7, "low"))

    for query, supporting_terms, priority, confidence_hint in query_specs:
        plans.append(
            build_plan(
                target_type="artist_photo",
                priority=priority,
                query=query,
                strong_terms=(artist,),
                supporting_terms=supporting_terms,
                confidence_hint=confidence_hint,
                reason=(
                    "Artist query starts with artist name plus the strongest available "
                    "time context."
                ),
                review_risks=(
                    "Verify the image subject is the artist and not a modern or unrelated "
                    "same-name result.",
                ),
            ),
        )
    return tuple(plans)


def build_work_plans(
    work: str,
    brief: RetrievalBrief,
    primary_time_term: str,
) -> tuple[ImageQueryPlan, ...]:
    text = combined_event_text(brief)
    if is_film_work(work, text):
        return build_film_work_plans(work=work, brief=brief, primary_time_term=primary_time_term)
    return (
        build_plan(
            target_type="album_cover",
            priority=2,
            query=" ".join(term for term in (work, primary_time_term) if term),
            strong_terms=(work,),
            supporting_terms=(primary_time_term,) if primary_time_term else (),
            confidence_hint="high" if primary_time_term else "medium",
            reason=(
                "Quoted release or track title plus time context may identify relevant "
                "cover art."
            ),
            review_risks=(
                "Verify rights and that the image is the relevant release or work, not "
                "unrelated fan art.",
            ),
        ),
    )


def build_film_work_plans(
    work: str,
    brief: RetrievalBrief,
    primary_time_term: str,
) -> tuple[ImageQueryPlan, ...]:
    scene_term = primary_scene_context(brief)
    plans = []
    if primary_time_term:
        plans.append(
            build_plan(
                target_type="archive_photo",
                priority=1,
                query=f"{work} {primary_time_term}",
                strong_terms=(work,),
                supporting_terms=(primary_time_term,),
                confidence_hint="high",
                reason=(
                    "Quoted film title plus release year is the most concise "
                    "disambiguating query."
                ),
                review_risks=(
                    "Verify the result refers to the film context, not decorative or "
                    "unrelated uses of the title.",
                ),
            ),
        )
        plans.append(
            build_plan(
                target_type="archive_photo",
                priority=2,
                query=f"{work} {primary_time_term} film",
                strong_terms=(work,),
                supporting_terms=(primary_time_term, "film"),
                confidence_hint="medium",
                reason=(
                    "Film title plus year and medium adds context when the concise query "
                    "is ambiguous."
                ),
                review_risks=(
                    "Verify the result refers to the film context, not decorative or "
                    "unrelated uses of the title.",
                ),
            ),
        )
    if scene_term:
        plans.append(
            build_plan(
                target_type="archive_photo",
                priority=3,
                query=f"{work} {scene_term} film",
                strong_terms=(work,),
                supporting_terms=(scene_term, "film"),
                confidence_hint="medium",
                reason="Film title plus scene context helps avoid unrelated title matches.",
                review_risks=(
                    "Verify the result refers to the film context, not decorative or "
                    "unrelated uses of the title.",
                ),
            ),
        )
    return tuple(plans)


def build_archive_photo_plans(
    brief: RetrievalBrief,
    primary_time_term: str,
) -> tuple[ImageQueryPlan, ...]:
    plans = []
    scene_term = primary_scene_context(brief)
    if primary_time_term and scene_term:
        plans.append(
            build_plan(
                target_type="archive_photo",
                priority=8,
                query=f"{brief.event_title} {primary_time_term} {scene_term}",
                strong_terms=(brief.event_title,),
                supporting_terms=(primary_time_term, scene_term),
                confidence_hint="low",
                reason="Event title plus time and scene context is a fallback archive-image query.",
                review_risks=(
                    "Reject generic, modern, or only loosely related results.",
                ),
            ),
        )
    if primary_time_term:
        plans.append(
            build_plan(
                target_type="archive_photo",
                priority=9,
                query=f"{brief.event_title} {primary_time_term}",
                strong_terms=(brief.event_title,),
                supporting_terms=(primary_time_term,),
                confidence_hint="low",
                reason="Event title plus time context is a fallback archive-image query.",
                review_risks=(
                    "Reject generic, modern, or only loosely related results.",
                ),
            ),
        )
    plans.append(
        build_plan(
            target_type="archive_photo",
            priority=10,
            query=brief.event_title,
            strong_terms=(brief.event_title,),
            supporting_terms=(),
            confidence_hint="low",
            reason="Event title can be used as the broadest fallback archive-image query.",
            review_risks=(
                "Reject generic, modern, or only loosely related results.",
            ),
        ),
    )
    return tuple(plans)


def likely_artist_terms(brief: RetrievalBrief) -> tuple[str, ...]:
    artist_terms = []
    for term in brief.strong_terms:
        if term == brief.event_title:
            continue
        normalized = term.casefold()
        tokens = set(normalized.replace("-", " ").split())
        if tokens & ARTIST_MARKERS:
            artist_terms.append(term)
    return unique_terms(artist_terms)


def work_terms(brief: RetrievalBrief) -> tuple[str, ...]:
    text = combined_event_text(brief)
    terms = extract_quoted_terms(text)

    if not terms and any(keyword in text.casefold() for keyword in RELEASE_KEYWORDS):
        terms.extend(
            term
            for term in brief.strong_terms
            if term != brief.event_title and not term_is_place_like(term, brief)
        )
    return unique_terms(
        term
        for term in terms
        if len(term) >= 3 and term.casefold() not in WORK_STOP_TERMS
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
    return terms


def time_query_terms(brief: RetrievalBrief) -> tuple[str, ...]:
    terms = []
    if brief.year_phrase:
        terms.append(brief.year_phrase)
    decades = decade_terms(brief.year_start, brief.year_end)
    terms.extend(decades)
    if brief.year_start is not None and brief.year_end is not None:
        year_count = brief.year_end - brief.year_start + 1
        if 1 < year_count <= 5:
            terms.extend(str(year) for year in range(brief.year_start, brief.year_end + 1))
    return unique_terms(terms)


def decade_terms(year_start: int | None, year_end: int | None) -> tuple[str, ...]:
    if year_start is None:
        return ()
    end_year = year_end if year_end is not None else year_start
    return tuple(
        f"{decade}s"
        for decade in range((year_start // 10) * 10, (end_year // 10) * 10 + 1, 10)
    )


def venue_location_disambiguators(brief: RetrievalBrief) -> tuple[str, ...]:
    text = combined_event_text(brief)
    terms = []
    for borough in BOROUGH_TERMS:
        if term_in_text(borough, text) or term_in_text(borough, brief.place_name):
            terms.append(borough)
    for city in CITY_TERMS:
        if term_in_text(city, text) or term_in_text(city, brief.place_name):
            terms.append(city)
    if not any(term.casefold() in {"new york", "nyc"} for term in terms):
        terms.append("New York")
    return unique_terms(terms)


def artist_role_term(artist: str, brief: RetrievalBrief) -> str:
    text = f"{artist} {combined_event_text(brief)}".casefold()
    if "dj" in text and "dj" not in artist.casefold():
        return "DJ"
    if any(term in text for term in ("group", "gang", "force", "crew", "band")):
        return "group"
    return ""


def primary_scene_context(brief: RetrievalBrief) -> str:
    text = combined_event_text(brief).casefold().replace("-", " ")
    for match_term, query_term in SCENE_CONTEXT_TERMS:
        if match_term in text:
            return query_term
    return ""


def is_film_work(work: str, text: str) -> bool:
    normalized_text = text.casefold()
    normalized_work = work.casefold()
    return (
        any(keyword in normalized_text for keyword in FILM_KEYWORDS)
        and normalized_work in normalized_text
    )


def combined_event_text(brief: RetrievalBrief) -> str:
    return " ".join(
        term
        for term in (
            brief.event_title,
            brief.route_title,
            brief.place_name,
            brief.summary,
            brief.significance,
            *brief.tags,
        )
        if term
    )


def term_in_text(term: str, text: str) -> bool:
    return term.casefold() in text.casefold()


def term_is_place_like(term: str, brief: RetrievalBrief) -> bool:
    normalized = term.casefold()
    return bool(brief.place_name and normalized == brief.place_name.casefold()) or any(
        marker in normalized
        for marker in ("avenue", "street", "park", "bronx", "new york", "room")
    )


def build_plan(
    target_type: str,
    priority: int,
    query: str,
    strong_terms: tuple[str, ...],
    supporting_terms: tuple[str, ...],
    confidence_hint: str,
    reason: str,
    review_risks: tuple[str, ...],
) -> ImageQueryPlan:
    return ImageQueryPlan(
        target_type=target_type,
        priority=priority,
        query=clean_text(query),
        strong_terms=tuple(term for term in strong_terms if term),
        supporting_terms=tuple(term for term in supporting_terms if term),
        confidence_hint=confidence_hint,
        reason=reason,
        review_risks=review_risks,
    )


def dedupe_plans(plans: list[ImageQueryPlan]) -> tuple[ImageQueryPlan, ...]:
    deduped_plans = []
    seen_queries = set()
    for plan in plans:
        normalized_query = plan.query.casefold()
        if not normalized_query or normalized_query in seen_queries:
            continue
        deduped_plans.append(plan)
        seen_queries.add(normalized_query)
    return tuple(sorted(deduped_plans, key=lambda plan: (plan.priority, plan.query.casefold())))
