# Query Input Quality

## Purpose

This document describes the shared upstream checks that happen before provider
execution in media and image enrichment.

These checks do not validate seed schema correctness. They evaluate whether the
available event text and structured enrichment inputs are specific enough to
produce useful queries.

## Scope

Query input quality currently covers:

- event-search-component validation warnings
- precise anchor checks for artists, works, organizations, techniques, or
  historical events
- place disambiguation checks for borough or city context
- retrieval-critical tags missing from event prose
- wrong-era media playlist warnings in enrichment quality reports

## Trigger Points

Seed/query readiness checks run during event-search-component generation:

```bash
cd backend
uv run python scripts/generate_event_search_components.py --route-id birth-of-hip-hop --dry-run
```

Candidate-quality warnings run during enrichment quality reporting:

```bash
cd backend
uv run python scripts/report_enrichment_quality.py --kind media --route-id birth-of-hip-hop
uv run python scripts/report_enrichment_quality.py --kind image --route-id birth-of-hip-hop
```

## Current Warning Model

Warnings are review prompts, not failures.

Examples:

- strong terms are broad or missing
- no precise enrichment anchors are present
- a concrete place lacks borough or city disambiguation
- a retrieval-critical tag is missing from prose
- a playlist candidate exposes year or decade evidence outside the event range

## Practical Rule

If a problem is about structured seed correctness, document it in
`docs/data/seed-data-validation.md`.

If a problem is about whether the enrichment layer has good enough input for
query planning or review, document it here or in another upstream enrichment
doc.

## Related Docs

- `docs/enrichment/upstream/event-search-components.md`
- `docs/enrichment/upstream/workflow-commands.md`
- `docs/enrichment/workflow.md`
- `docs/data/seed-data-validation.md`
