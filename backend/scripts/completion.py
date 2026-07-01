import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SEED_DIR = REPO_ROOT / "data" / "seed"

SCRIPT_OPTIONS = {
    "enrich_image_links.py": [
        "--event-id",
        "--route-id",
        "--limit",
        "--provider",
        "--dry-run",
        "--json",
        "--preview-queries",
        "--query-planner",
        "--component-dir",
    ],
    "enrich_media_links.py": [
        "--event-id",
        "--results-dir",
        "--limit",
        "--dry-run",
        "--json",
    ],
    "generate_event_search_components.py": [
        "--event-id",
        "--route-id",
        "--output-dir",
        "--dry-run",
        "--json",
    ],
    "report_enrichment_quality.py": [
        "--kind",
        "--event-id",
        "--route-id",
        "--limit",
        "--results-dir",
        "--query-planner",
        "--compare-to",
        "--baseline-from-seed",
        "--json",
    ],
    "report_seed_link_counts.py": [
        "--event-id",
        "--route-id",
        "--json",
    ],
    "run_youtube_search_requests.py": [
        "--event-id",
        "--request-dir",
        "--output-dir",
        "--dry-run",
        "--json",
    ],
}

ARG_CHOICES = {
    "--kind": ["image", "media"],
    "--provider": ["wikimedia"],
    "--query-planner": ["legacy", "v2"],
}


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in {"options", "values"}:
        print("usage: completion.py {options,values} name [prefix]", file=sys.stderr)
        return 2

    mode = sys.argv[1]
    name = sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 else ""

    if mode == "options":
        matches = SCRIPT_OPTIONS.get(name, [])
    elif name == "--event-id":
        matches = seed_ids(SEED_DIR / "events.json", "events")
    elif name == "--route-id":
        matches = seed_ids(SEED_DIR / "routes.json", "routes")
    else:
        matches = ARG_CHOICES.get(name, [])

    for match in matches:
        if match.startswith(prefix):
            print(match)
    return 0


def seed_ids(path: Path, collection_key: str) -> list[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    records = payload.get(collection_key, [])
    if not isinstance(records, list):
        return []

    ids = [
        record.get("id")
        for record in records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    ]
    return sorted(ids)


if __name__ == "__main__":
    raise SystemExit(main())
