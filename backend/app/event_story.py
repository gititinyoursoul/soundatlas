from collections.abc import Mapping
from typing import Any


def event_story_values(event: Mapping[str, Any]) -> list[str]:
    sections = event.get("story_sections")
    if isinstance(sections, list) and sections:
        values: list[str] = []
        for section in sections:
            if not isinstance(section, Mapping):
                continue
            heading = section.get("heading")
            body = section.get("body")
            if isinstance(heading, str) and heading.strip():
                values.append(heading)
            if isinstance(body, str) and body.strip():
                values.append(body)
        return values

    return [
        value
        for value in (event.get("summary"), event.get("significance"))
        if isinstance(value, str) and value.strip()
    ]


def event_story_text(event: Mapping[str, Any]) -> str:
    return " ".join(event_story_values(event))


def event_story_legacy_pair(event: Mapping[str, Any]) -> tuple[str, str]:
    sections = event.get("story_sections")
    if isinstance(sections, list) and sections:
        return event_story_text(event), ""
    summary = event.get("summary")
    significance = event.get("significance")
    return (
        summary if isinstance(summary, str) else "",
        significance if isinstance(significance, str) else "",
    )
