# Upstream Query Input Workflow Commands

## Purpose

This document describes the practical command sequence for preparing and
checking shared enrichment inputs before the media and image workflows split.

Use it when you want to improve query quality, inspect warnings, or confirm
that an event is ready for provider-specific enrichment work.

## Workflow Overview

```text
accepted event dossier or seed data
-> generate or review event-search-components
-> inspect query-input warnings
-> preview quality reports
-> decide whether to fix editorial text, seed data, or provider plans
```

When `docs/content/routes/<route-id>/accepted-events.md` exists, use it to
confirm that the event is enrichment-ready before generating search components.
Do not generate enrichment inputs for unresolved `maybe`, unresolved `merge`,
or `reject` candidates.

For the shared enrichment flow and split points, see
`docs/enrichment/workflow.md`.

## 1. Generate Components For One Event

```bash
cd backend
uv run python scripts/generate_event_search_components.py --event-id kool-herc-back-to-school-jam --dry-run
```

Use `--dry-run --json` to inspect the generated component and validation report
as structured JSON:

```bash
cd backend
uv run python scripts/generate_event_search_components.py --event-id kool-herc-back-to-school-jam --dry-run --json
```

## 2. Generate Components For A Whole Route

```bash
cd backend
uv run python scripts/generate_event_search_components.py --route-id birth-of-hip-hop --dry-run
```

This is the fastest way to inspect route-wide upstream warnings after seed or
editorial changes.

## 3. Write Component Files

After reviewing the dry-run output, remove `--dry-run`:

```bash
cd backend
uv run python scripts/generate_event_search_components.py --route-id birth-of-hip-hop
```

This writes files under:

```text
data/enrichment/event-search-components/
```

## 4. Check Media-Side Quality Warnings

```bash
cd backend
uv run python scripts/report_enrichment_quality.py --kind media --route-id birth-of-hip-hop --baseline-from-seed
```

Use this when you want to catch issues such as `wrong_era_playlist` before
writing media changes.

## 5. Check Image-Side Quality Warnings

```bash
cd backend
uv run python scripts/report_enrichment_quality.py --kind image --route-id birth-of-hip-hop --baseline-from-seed
```

Use this when you want to compare current image-query behavior and spot weak
specificity or rights metadata issues.

## 6. Preview Image Query Ladders

```bash
cd backend
uv run python scripts/enrich_image_links.py --event-id kool-herc-back-to-school-jam --preview-queries
```

Use this to confirm that artist and place queries are era-aware and properly
disambiguated before provider calls.

## 7. Validate After Seed Or Upstream Changes

```bash
cd backend
uv run pytest
```

## Review Rules

- Warnings do not block the app from loading seed data.
- Fix editorial text when the issue is missing or vague event wording.
- Fix component files when the issue is retrieval-specific structure.
- Fix provider plans only after the upstream input looks sound.

## Related Docs

- `docs/content/editorial-workflow.md`
- `docs/data/seed-data-structure.md`
- `docs/data/seed-data-validation.md`
- `docs/enrichment/upstream/query-input-quality.md`
- `docs/enrichment/media/workflow-commands.md`
- `docs/enrichment/image/workflow-commands.md`
