# Editorial Workflow Commands

## Purpose

This is the command reference for the route content pipeline. The pipeline
turns route-folder editorial inputs into checkable Markdown and JSON artifacts
before seed data is changed.

The commands can call Codex CLI for editorial drafting, but they do not replace
source review, editorial judgment, or final wording work.

## Command Shape

Run commands from the repository root:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py <command> [options]
```

By default, route content is read from `docs/content/routes/` and seed files are
read from `data/seed/`.

## Existing Files

The workflow has three file modes:

- Default / `--missing`: create only missing outputs. Existing outputs are left
  untouched.
- `--renew`: regenerate selected outputs and write `.bak` copies before
  overwriting existing files.
- `--variant <name>`: write a named alternate chain such as
  `event-list.mvp-edit.json` and `route-concept.mvp-edit.md`.

Use lowercase hyphenated variant names, for example `mvp-edit`.

## Route Setup

Initialize a route pipeline manifest:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py init --route-id birth-of-hip-hop
```

The manifest records the active dossier and the default output filenames. If
`research-dossier.md` exists, it is preferred as the active dossier.

To select a specific dossier:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py init --route-id birth-of-hip-hop --dossier research-dossier.md --renew
```

## Agent Steps

Create a prompt without calling Codex:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step brief_to_dossier --dry-run
```

Dry-run mode writes:

- `<step>-prompt.ai-draft.md`
- `<step>-run.ai-draft.json`

Run one Codex-backed editorial step:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step brief_to_dossier
```

The command invokes `codex exec` in a read-only sandbox and writes directly to
the step output:

| Step | Output |
| --- | --- |
| `brief_to_dossier` | `research-dossier.md` |
| `dossier_to_event_review` | `event-list.json` |
| `event_review_to_concept` | `route-concept.md` |
| `concept_to_event_framing` | `event-framing.md` |
| `validation_to_revision_plan` | `revision-plan.md` |

Prompt and run metadata stay in ignored local files:

- `docs/content/routes/*/*-prompt.ai-draft.md`
- `docs/content/routes/*/*-run.ai-draft.json`

Use `--renew` to overwrite an existing output with a `.bak` copy:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step brief_to_dossier --renew
```

Use `--variant` to draft an alternate chain:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step brief_to_dossier --variant mvp-edit
```

This writes `research-dossier.mvp-edit.md`. Later variant steps read and write
the matching variant filenames when you pass the same `--variant`.

## Deterministic Steps

Create missing downstream artifacts:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --missing
```

`--missing` is the default. Expected outputs:

| Step | Outputs |
| --- | --- |
| `event_list` | `event-list.md`, `event-list.json` |
| `route_concept` | `route-concept.md` |
| `event_framing` | `event-framing.md`, `event-framing.json`, `place-framing.json`, `connection-framing.json` |
| `seed_preview` | `seed-transfer-report.md` |
| `validation` | `validation-report.md` |

Run one step:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --step event_list
```

Regenerate outputs with backups:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --step event_framing --renew
```

Create a deterministic variant:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --step event_list --variant mvp-edit
```

## Status

Inspect route pipeline state:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py status --route-id birth-of-hip-hop
```

Use status before continuing work to confirm the active dossier, configured
inputs, and which outputs are present or missing.

## Seed Preview And Write

Preview seed promotion without writing files:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py promote --route-id birth-of-hip-hop --to-seed
```

Preview a variant:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py promote --route-id birth-of-hip-hop --to-seed --variant mvp-edit
```

Write route drafts into seed files:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py promote --route-id birth-of-hip-hop --to-seed --write
```

The command validates the merged seed payloads before writing. It can add or
update drafted places, events, and connections, but it does not create the route
metadata record in `routes.json`.

## Editorial Checks

Before seed writing, inspect:

- the dossier source directions and risk notes
- candidate event rationale, not only chronology
- event titles, summaries, significance text, and source fields
- draft place coordinates and source risks
- connection logic
- `seed-transfer-report.md` and `validation-report.md`

Generated text should stay cautious. Do not use the pipeline to turn weakly
sourced or contested claims into settled statements.

## Verification

After changing the pipeline or route artifacts, run:

```bash
uv run --project backend pytest backend/tests/test_route_content_pipeline.py
```

For broader backend confidence:

```bash
cd backend
uv run pytest
```
