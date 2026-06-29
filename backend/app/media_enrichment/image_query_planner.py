import re
from dataclasses import dataclass

from app.media_enrichment.retrieval_brief import (
    CONCRETE_PLACE_TYPES,
    RetrievalBrief,
    clean_text,
    unique_terms,
)


ARTIST_MARKERS = {"dj", "flash", "herc", "bambaataa", "gang", "force", "five"}
RELEASE_KEYWORDS = {"album", "record", "release", "single", "track"}


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

    if brief.place_type in CONCRETE_PLACE_TYPES and brief.place_name:
        plans.append(
            build_plan(
                target_type="venue_photo",
                priority=1,
                query=brief.place_name,
                strong_terms=(brief.place_name,),
                supporting_terms=(brief.year_phrase,) if brief.year_phrase else (),
                confidence_hint="high",
                reason="Exact concrete place name is suitable for venue or location imagery.",
                review_risks=(
                    "Verify the image shows the correct place and not a nearby street or unrelated building.",
                ),
            ),
        )
        if brief.year_phrase:
            plans.append(
                build_plan(
                    target_type="venue_photo",
                    priority=2,
                    query=f"{brief.place_name} {brief.year_phrase}",
                    strong_terms=(brief.place_name,),
                    supporting_terms=(brief.year_phrase,),
                    confidence_hint="medium",
                    reason="Concrete place plus year context may surface historically framed imagery.",
                    review_risks=(
                        "Verify the year in search terms does not create unrelated date matches.",
                    ),
                ),
            )

    for term in likely_artist_terms(brief):
        plans.append(
            build_plan(
                target_type="artist_photo",
                priority=2,
                query=term,
                strong_terms=(term,),
                supporting_terms=(),
                confidence_hint="medium",
                reason="Named artist or group term is suitable for artist imagery.",
                review_risks=(
                    "Verify the image subject matches the event and historical context.",
                ),
            ),
        )

    for term in quoted_work_terms(brief):
        plans.append(
            build_plan(
                target_type="album_cover",
                priority=2,
                query=term,
                strong_terms=(term,),
                supporting_terms=(brief.year_phrase,) if brief.year_phrase else (),
                confidence_hint="medium",
                reason="Quoted work title may identify release artwork or related visual material.",
                review_risks=(
                    "Verify rights and that the image is the relevant release or work, not unrelated fan art.",
                ),
            ),
        )

    if brief.event_title:
        plans.append(
            build_plan(
                target_type="archive_photo",
                priority=3,
                query=brief.event_title,
                strong_terms=(brief.event_title,),
                supporting_terms=(),
                confidence_hint="low",
                reason="Event title can be used as a fallback archive-image query.",
                review_risks=(
                    "Reject generic, modern, or only loosely related results.",
                ),
            ),
        )
        if brief.year_phrase:
            plans.append(
                build_plan(
                    target_type="archive_photo",
                    priority=4,
                    query=f"{brief.event_title} {brief.year_phrase}",
                    strong_terms=(brief.event_title,),
                    supporting_terms=(brief.year_phrase,),
                    confidence_hint="low",
                    reason="Event title plus year context is a fallback archive-image query.",
                    review_risks=(
                        "Reject generic, modern, or only loosely related results.",
                    ),
                ),
            )

    return dedupe_plans(plans)


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


def quoted_work_terms(brief: RetrievalBrief) -> tuple[str, ...]:
    text = " ".join([brief.event_title, brief.summary, brief.significance])
    terms = [
        clean_text(match.group(1) or match.group(2))
        for match in re.finditer(r"(?<!\w)'([^']{3,})'(?!\w)|\"([^\"]{3,})\"", text)
    ]

    if not terms and any(keyword in text.casefold() for keyword in RELEASE_KEYWORDS):
        terms.extend(
            term
            for term in brief.strong_terms
            if term != brief.event_title and not term_is_place_like(term, brief)
        )
    return unique_terms(term for term in terms if len(term) >= 3)


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
