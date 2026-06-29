from __future__ import annotations

from collections.abc import Iterable
from typing import Any


IGNORED_LINKS_KEY = "ignored_links"
IGNORED_LINK_FIELDS = ("url", "image_url", "source_url", "thumbnail_url")


def link_identity_values(link: Any) -> set[str]:
    values = set()
    for field in IGNORED_LINK_FIELDS:
        value = None
        if isinstance(link, dict):
            value = link.get(field)
        else:
            value = getattr(link, field, None)
        if isinstance(value, str) and value:
            values.add(value)
    return values


def build_ignored_link_index(
    payload: dict[str, Any],
) -> dict[tuple[str, str], set[str]]:
    ignored_index: dict[tuple[str, str], set[str]] = {}
    for entry in iter_ignored_links(payload):
        event_id = entry.get("event_id")
        kind = entry.get("kind")
        values = entry.get("values")
        if not isinstance(event_id, str) or not isinstance(kind, str):
            continue
        if not isinstance(values, list):
            continue
        key = (event_id, kind)
        ignored_values = ignored_index.setdefault(key, set())
        for value in values:
            if isinstance(value, str) and value:
                ignored_values.add(value)
    return ignored_index


def link_is_ignored(
    ignored_index: dict[tuple[str, str], set[str]],
    event_id: str,
    kind: str,
    link: Any,
) -> bool:
    return bool(link_identity_values(link) & ignored_index.get((event_id, kind), set()))


def record_ignored_link(
    payload: dict[str, Any],
    event_id: str,
    kind: str,
    link: Any,
) -> bool:
    values = sorted(link_identity_values(link))
    if not values:
        return False

    entry = {
        "event_id": event_id,
        "kind": kind,
        "values": values,
    }
    ignored_links = payload.setdefault(IGNORED_LINKS_KEY, [])
    if entry in ignored_links:
        return False

    ignored_links.append(entry)
    return True


def iter_ignored_links(payload: dict[str, Any]) -> Iterable[dict[str, Any]]:
    ignored_links = payload.get(IGNORED_LINKS_KEY, [])
    if not isinstance(ignored_links, list):
        return []
    return [entry for entry in ignored_links if isinstance(entry, dict)]
