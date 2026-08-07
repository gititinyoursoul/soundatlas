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
  `event-list.alternate-draft.json`,
  `accepted-events.alternate-draft.json`, and
  `route-concept.alternate-draft.md`.

Use lowercase hyphenated variant names, for example `alternate-draft`.

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
| `dossier_to_event_review` | `event-list.json`, refreshed `event-list.md` |
| `complete_draft` | `complete-draft.json`, `complete-draft.md`, refreshed active route artifacts and `route-review.json` |
| `event_review_to_concept` | `route-concept.md` |
| `concept_to_event_framing` | `event-framing.md` |
| `validation_to_revision_plan` | `revision-plan.md` |

`dossier_to_event_review` preserves its generated candidate outline as
`candidate-outline.json`. `complete_draft` reads that outline and the active
dossier, then may add, omit, merge, split, or reorder proposals before
materializing one validated active result. It records an outcome, Reason,
relationships, review Context, phase coverage, and owned findings for every
outline Candidate and every addition. Only active and added Candidates become
Events; inactive Candidates remain reviewable without becoming editorial state.

The complete-draft step does not require `accepted-events.json`. It validates
the same output contract named in its prompt, permits at most one deterministic
JSON-envelope repair, records input/output hashes and the repair outcome, and
activates the complete draft, views, and bound `route-review.json` together or
preserves the prior revision on replacement failure.

For a correction that is local to one or more Candidates, provide a route-local
request file with the current review revision, correction text, Candidate IDs,
and `selective` scope:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent \
  --route-id birth-of-hip-hop --step complete_draft --renew \
  --revision-request revision-request.json
```

Selective regeneration carries unaffected Events forward verbatim and creates a
complete new revision. Broad brief, thesis, dossier, route-wide Source, whole
Route, or non-local corrections use `full` scope instead. The command consumes
the request; #85 owns capturing it from the review surface.

Prompt and run metadata stay in ignored local files:

- `docs/content/routes/*/*-prompt.ai-draft.md`
- `docs/content/routes/*/*-run.ai-draft.json`

Use `--renew` to overwrite an existing output with a `.bak` copy:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step brief_to_dossier --renew
```

Use `--variant` to draft an alternate chain:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step brief_to_dossier --variant alternate-draft
```

This writes `research-dossier.alternate-draft.md`. Later variant steps read and
write the matching variant filenames when you pass the same `--variant`.

## Deterministic Steps

Create missing downstream artifacts:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --missing
```

`--missing` is the default. Expected outputs:

| Step | Outputs |
| --- | --- |
| `event_list` | `event-list.md`, `event-list.json` |
| `accepted_events` | `accepted-events.json`, `accepted-events.md` |
| `route_concept` | `route-concept.md` |
| `event_framing` | `event-framing.md`, `event-framing.json`, `place-framing.json`, `connection-framing.json` |
| `seed_preview` | `seed-transfer-report.md` |
| `validation` | `validation-report.md` |

`event_list` generates candidate-review artifacts with `maybe` decisions and
`review_state: pending` by default. Agent-reviewed event lists use `status` for
the proposed candidate decision: `keep`, `maybe`, `merge`, or `reject`.
Human review uses `review_state`: `pending`, `approved`, or `rejected`.
`accepted_events` only includes `keep` and resolved `merge` candidates whose
`review_state` is `approved`. A `merge` candidate must include
`merge_target_id` and `merge_rationale`; the target cannot live only in prose.
The `accepted_events` step creates or consumes `accepted-events.json` as the
structured handoff and generates `accepted-events.md` as a readable companion
view only when missing, unless `--renew` is passed. The Markdown file helps
humans inspect the same handoff; it is not a separate approval gate.

`event-list.md` is regenerated as a decision-first review guide:

- overview counts
- overlap cluster recommendations
- merge decisions
- `maybe` items
- full candidate appendix

Overlap clusters are optional, but when present they should recommend one of
`keep_separate`, `merge`, or `use_as_context` so review can confirm an agent
proposal rather than synthesize a decision from scratch.

The legacy deterministic `route_concept`, `event_framing`, `seed_preview`, and
`promote` steps are blocked until every accepted event confirms:

- `route_fit_confirmed`
- `place_and_year_specificity_confirmed`
- `source_risks_visible`
- `seed_draft_ready`

`validation` may still run when the gate is blocked; in that case,
`validation-report.md` records accepted-events gate errors instead of reporting
the route as seed-ready.

The accepted-events gate is a legacy compatibility path for the deterministic
`run` and `promote` commands. It is not required by the active `complete_draft`
path and is not the authority for the private Draft, Approved, and Don’t use
state described below.

Run one step:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --step event_list
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --step accepted_events
```

Regenerate outputs with backups:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --step event_framing --renew
```

Create a deterministic variant:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --step event_list --variant alternate-draft
```

## Private Route Review

Create the first private review result from an existing event list by explicitly
migrating its legacy human states:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py review --route-id birth-of-hip-hop --migrate-legacy
```

The migration reports counts and maps only `pending` to Draft, `approved` to
Approved, and `rejected` to Don’t use. Agent recommendations and membership in
`accepted-events.json` never determine the private state.

After generating or regenerating `event-list.json`, refresh the active review
result. The `complete_draft` agent step performs this refresh automatically after
successful activation; the command remains useful for compatibility and manual
refreshes:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py review --route-id birth-of-hip-hop
```

The command writes `route-review.json` atomically in the route folder. It keeps
one active result and a minimal dormant record for removed active proposals.
Newly active Candidates start as Draft; unchanged proposals retain state;
materially changed Approved proposals return to Draft; and Don’t use remains
excluded until a human changes it. Inactive Candidate accounts have no Draft,
Approved, or Don’t use state.

The private backend boundary for the later explorer review surface is:

- `GET /editorial/routes/<route-id>/review`
- `PATCH /editorial/routes/<route-id>/review/events/<candidate-id>` with the
  current `revision_id` and `editorial_state`

State updates create a new exact revision. A stale revision is rejected so a
review action cannot overwrite a newer regeneration or decision. These private
fields do not appear in the public route or event responses.

## Status

Inspect route pipeline state:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py status --route-id birth-of-hip-hop
```

Use status before continuing work to confirm the active dossier, candidate
outline, complete-draft output, configured inputs, and whether the legacy path is
present only for compatibility. Status separately reports the private
route-review revision, state and inclusion counts, dormant decisions, warnings,
technical errors, and readiness. A present complete draft is not reported as
stale merely because `accepted-events.json` is absent.

## Seed Preview And Write

Preview seed promotion without writing files:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py promote --route-id birth-of-hip-hop --to-seed
```

Preview a variant:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py promote --route-id birth-of-hip-hop --to-seed --variant alternate-draft
```

Write route drafts into seed files:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py promote --route-id birth-of-hip-hop --to-seed --write
```

The command validates the merged seed payloads before writing. It can add or
update drafted places, events, and connections, but it does not create the route
metadata record in `routes.json`. `--write` refuses to write while the
accepted-events gate is missing or blocked.

## Editorial Checks

Before seed writing, inspect:

- the dossier source directions and risk notes
- candidate event rationale, not only chronology
- `event-list.md`, starting with overview counts, cluster recommendations,
  merge decisions, and `maybe` items before the full appendix
- `accepted-events.json`, to confirm that only approved `keep` candidates and
  human-resolved `merge` outcomes are moving forward and that the required
  quality flags are true. Use `accepted-events.md` as the optional readable
  view for the same review, not as a separate approval gate.
- the event editorial quality checks in
  `docs/content/event-editorial-quality-standards.md`
- event titles, summaries, significance text, and source fields
- draft place coordinates and source risks
- connection logic
- `seed-transfer-report.md` and `validation-report.md`

Generated text should stay cautious. Do not use the pipeline to turn weakly
sourced or contested claims into settled statements.

The legacy deterministic downstream pipeline uses `accepted-events.json` as its
enforcement contract. `accepted-events.md` is the companion view and is not
parsed as the source of truth or approved separately. Treat both files as
enrichment-ready compatibility handoff material only; `complete-draft.json`
feeds the active route-review path, `route-review.json` owns private human
state, and Issue #73 owns exact-result publication.

## Verification

After changing the pipeline or route artifacts, run:

```bash
uv run --project backend pytest backend/tests/test_route_content_pipeline.py backend/tests/test_route_review_repository.py
```

For broader backend confidence:

```bash
cd backend
uv run ruff check .
uv run pyright
uv run pytest
```
