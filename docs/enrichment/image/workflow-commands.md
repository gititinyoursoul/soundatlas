# Image Workflow Commands

## Purpose

This document describes the practical command sequence for the Wikimedia-only
image enrichment pass.

The shared enrichment workflow is documented in
`docs/enrichment/workflow.md`. This page stays command-focused.

Use it when you want to enrich one or more SoundAtlas events with draft
`image_links`.

## Workflow Overview

```text
CLI plans event-specific image queries
-> CLI queries Wikimedia Commons
-> CLI normalizes image metadata into image_links
-> CLI previews or writes draft links into seed data
-> editor reviews generated draft links
```

For the shared enrichment flow and split points, see
`docs/enrichment/workflow.md`.

The default query planner is `v2`. It prefers an optional
`data/enrichment/event-search-components/<event-id>.json` file when present,
otherwise it builds a retrieval brief from the event, route, and place data.
It then plans short ladders of searches around strong identity terms and
compact supporting context. Venue queries include city or borough context,
artist and work queries start with the event year/range when available, and
short ranges also get decade and individual-year fallbacks. The legacy planner
is still available for comparison with `--query-planner legacy`.

The v2 preview groups queries by target type and shows the planner's priority
and confidence hint for each query. Use that preview to check that venues are
disambiguated, artist queries are era-aware, and quoted works such as films are
not treated as generic title searches.

## 0. Preview Query Plans

Preview the planned v2 query ladder before calling Wikimedia:

```bash
cd backend
uv run python scripts/enrich_image_links.py --event-id kool-herc-back-to-school-jam --preview-queries
```

Compare the legacy query planner when needed:

```bash
cd backend
uv run python scripts/enrich_image_links.py --event-id kool-herc-back-to-school-jam --preview-queries --query-planner legacy
```

## 1. Preview One Event

Run a dry run before writing seed data:

```bash
cd backend
uv run python scripts/enrich_image_links.py --event-id kool-herc-back-to-school-jam --dry-run
```

Expected result:

- the command prints a readable summary of changed events and candidate counts
- no seed file is written
- generated links have `review_status: "draft"`

To inspect the full changed seed payload, add `--json`:

```bash
cd backend
uv run python scripts/enrich_image_links.py --event-id kool-herc-back-to-school-jam --dry-run --json
```

If the command prints `No image candidates found.`, Wikimedia did not return
acceptable candidates for the current queries and scoring threshold.

## 2. Write Draft Image Links For One Event

After reviewing the dry-run output, write the merge:

```bash
cd backend
uv run python scripts/enrich_image_links.py --event-id kool-herc-back-to-school-jam
```

This updates:

```text
data/seed/events.json
```

Rejected image links are also written into the top-level `ignored_links`
collection in the same seed file, so future enrichment runs skip them for the
same event.

## 3. Preview A Whole Route

Use `--route-id` to process every event in a route:

```bash
cd backend
uv run python scripts/enrich_image_links.py --route-id birth-of-hip-hop --dry-run
```

## 4. Write Draft Image Links For A Whole Route

After reviewing the dry-run output, remove `--dry-run`:

```bash
cd backend
uv run python scripts/enrich_image_links.py --route-id birth-of-hip-hop
```

## 5. Process The First 5 Events In A Route

The image enrichment script does not currently have an event-count flag.
Use a shell loop from `backend` to run the first five events in route order.

Preview first:

```bash
cd backend

for event_id in $(uv run python -c 'import json; events=json.load(open("../data/seed/events.json"))["events"]; print("\n".join([e["id"] for e in events if e["route_id"]=="birth-of-hip-hop"][:5]))'); do
  uv run python scripts/enrich_image_links.py --event-id "$event_id" --dry-run
done
```

Then write:

```bash
cd backend

for event_id in $(uv run python -c 'import json; events=json.load(open("../data/seed/events.json"))["events"]; print("\n".join([e["id"] for e in events if e["route_id"]=="birth-of-hip-hop"][:5]))'); do
  uv run python scripts/enrich_image_links.py --event-id "$event_id"
done
```

Replace `birth-of-hip-hop` with another route ID as needed.

## Useful Variants

Report dry-run quality metrics and compare them to current seed image links:

```bash
cd backend
uv run python scripts/report_enrichment_quality.py --kind image --route-id birth-of-hip-hop --baseline-from-seed
```

Limit generated image links per event:

```bash
cd backend
uv run python scripts/enrich_image_links.py --route-id birth-of-hip-hop --limit 3 --dry-run
```

Use the explicit provider flag:

```bash
cd backend
uv run python scripts/enrich_image_links.py --event-id kool-herc-back-to-school-jam --provider wikimedia --dry-run
```

Use the legacy query planner for comparison:

```bash
cd backend
uv run python scripts/enrich_image_links.py --event-id kool-herc-back-to-school-jam --query-planner legacy --dry-run
```

Combine route and per-event image limit:

```bash
cd backend
uv run python scripts/enrich_image_links.py --route-id birth-of-hip-hop --limit 5 --dry-run
```

## Validate After Writing

Run backend tests after writing generated links:

```bash
cd backend
uv run pytest
```

## Review Generated Links

Manually review every generated image link before treating it as accepted
content.

Check:

- historical relevance
- source page quality
- creator and attribution metadata
- license and rights status
- whether the image should stay `draft`, be promoted to `reviewed`, or be removed

Only set:

```json
"review_status": "reviewed"
```

after editorial review.

If you reject an image or media item, the UI removes it from the event and the
review flow records it in the ignore list. Subsequent enrichment runs skip that
link for the same event and kind.

## Safety Rules

- Do not download image files into the repository.
- Do not commit API keys, secrets, or local machine paths.
- Keep generated image links as `draft` until manual review.
- Do not invent image URLs, source URLs, creators, licenses, or API results.
- Prefer no result over padding events with weak generic images.
