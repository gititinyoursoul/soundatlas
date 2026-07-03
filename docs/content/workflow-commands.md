# Editorial Workflow Commands

## Purpose

This document is the command reference for the route content pipeline. The
pipeline turns route-folder editorial inputs into reviewable Markdown and JSON
artifacts before any seed data is changed.

The commands are deterministic local tooling. They do not replace editorial
judgment, source review, or final wording work.

The `agent` command adds Codex CLI automation for editorial drafting. Codex
outputs are local drafts by default. A human review step must mark an output
reviewed before it becomes a reviewed route-folder variant.

## Command Shape

Run commands from the repository root:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py <command> [options]
```

By default, route content is read from `docs/content/routes/` and seed files are
read from `data/seed/`.

Use `--content-root <path>` or `--seed-dir <path>` only when working against a
temporary fixture or alternate content tree.

## Route Setup

Initialize a route pipeline manifest:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py init --route-id birth-of-hip-hop
```

This creates or updates:

- `docs/content/routes/<route-id>/pipeline.json`

The manifest records the active dossier and the output filenames for each step.
If `research-dossier-mvp-edit.md` exists, it is preferred as the active dossier.
Otherwise the command uses the first matching `research-dossier*.md`, or falls
back to `research-dossier.md`.

To select a specific dossier:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py init --route-id birth-of-hip-hop --dossier research-dossier-mvp-edit.md --renew
```

Use `--renew` on `init` when the manifest should be rewritten.

## Generate Agent Prompts

Create a prompt for a single Codex-backed editorial step without calling Codex:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step brief_to_dossier --dry-run
```

Dry-run mode writes:

- `<step>-prompt.ai-draft.md`
- `<step>-run.ai-draft.json`

It does not write `<step>-output.ai-draft.md` and it does not change seed
files.

Available agent steps:

| Step | Editorial quality job | Reviewed variant |
| --- | --- | --- |
| `brief_to_dossier` | Expand a route brief into a source-aware dossier without narrowing research direction too early. | `research-dossier-agent-reviewed.md` |
| `dossier_to_event_review` | Separate strong route events from context-only or weak candidates while preserving source leads, risk notes, and thesis rationale. | `event-list-agent-reviewed.json` |
| `event_review_to_concept` | Turn reviewed candidates into a coherent route argument with phases, place logic, risks, and open questions. | `route-concept-agent-reviewed.md` |
| `concept_to_event_framing` | Turn the route concept into story-led event framing with product-facing prose, source needs, connection logic, and wording risks. | `event-framing-agent-reviewed.md` |
| `validation_to_revision_plan` | Convert preview and validation findings into a prioritized editorial revision plan. | `revision-plan-agent-reviewed.md` |

Each agent step is expected to improve editorial quality, not merely reformat
the previous artifact. Prompts ask Codex to preserve useful detail, sharpen
route logic, and mark unresolved review needs.

For event framing, headings should serve the route story rather than mirror
backend field names. The prompt asks for event-level prose that can later map
to seed fields:

- product-facing event title, usually under 90 characters
- one-sentence what-happens prose for later seed `summary`
- one-sentence why-this-matters-here prose for later seed `significance`
- combined what-happens and why-this-matters-here prose usually under 70 words

These are editorial guidelines, not enforced word-count validation.

## Invoke Codex CLI

Run one Codex-backed step:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step brief_to_dossier
```

The command invokes Codex CLI through `codex exec` using a read-only sandbox and
writes the final response to:

- `<step>-output.ai-draft.md`

The local prompt, raw output, and run metadata files are ignored by git:

- `docs/content/routes/*/*.ai-draft.*`

Only reviewed variants should be committed as durable route content.

To pass a specific Codex model:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step brief_to_dossier --model <model-name>
```

To use a non-default Codex executable in tests or local tooling:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step brief_to_dossier --codex-command /path/to/codex
```

Do not commit local executable paths or credentials.

## Review Agent Outputs

Agent outputs default to draft. After inspecting `<step>-output.ai-draft.md`,
mark one step reviewed:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step brief_to_dossier --mark-reviewed
```

This copies the raw draft output into the step's reviewed variant, updates
`pipeline.json`, and leaves the raw prompt/output/run metadata local.

For `brief_to_dossier`, the reviewed variant becomes the active dossier. Later
steps may update route-local inputs in the manifest when their reviewed variant
can safely feed the deterministic pipeline.

## Draft Gating

By default, a later agent step will not run if an earlier agent step has a draft
raw output. Review that earlier output first, or explicitly allow draft chaining:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py agent --route-id birth-of-hip-hop --step dossier_to_event_review --allow-draft-inputs
```

Use `--allow-draft-inputs` only for exploratory full-draft passes. The outputs
remain unreviewed.

## Run Missing Steps

Create all missing downstream artifacts:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --missing
```

`--missing` is the default run mode. A step is skipped when all of its expected
outputs already exist.

Expected outputs:

| Step | Outputs |
| --- | --- |
| `event_list` | `event-list.md`, `event-list.json` |
| `route_concept` | `route-concept.md` |
| `event_framing` | `event-framing.md`, `event-framing.json`, `place-framing.json`, `connection-framing.json` |
| `seed_preview` | `seed-transfer-report.md` |
| `validation` | `validation-report.md` |

## Run One Step

Regenerate or create only one step:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --step event_list
```

Available steps:

- `event_list`
- `route_concept`
- `event_framing`
- `seed_preview`
- `validation`

Use a single step when one artifact was deleted or when you want to inspect the
effect of a specific upstream edit.

## Renew Outputs

Regenerate selected outputs and keep `.bak` copies of overwritten files:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --renew
```

Renewing all steps is useful after a dossier rewrite. Renewing one step is safer
when only a narrow artifact needs to be refreshed:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py run --route-id birth-of-hip-hop --step event_framing --renew
```

Review `.bak` files before deleting them. They are there to make regenerated
editorial drafts auditable.

## Check Status

Inspect route pipeline state:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py status --route-id birth-of-hip-hop
```

Use status before continuing work to confirm:

- the active dossier
- which outputs exist
- which outputs are missing
- each step's current `review_status`
- agent-step reviewed variants and draft/reviewed state

## Preview Seed Promotion

Preview seed promotion without writing files:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py promote --route-id birth-of-hip-hop --to-seed
```

This is a dry run. Use it to inspect which draft places, events, and
connections would be merged into `data/seed/`.

## Write Seed Data

Write reviewed route drafts into seed files:

```bash
uv run --project backend python backend/scripts/route_content_pipeline.py promote --route-id birth-of-hip-hop --to-seed --write
```

Do this only after editorial review. The command requires the `event_framing`
step in `pipeline.json` to be marked:

```json
"review_status": "reviewed"
```

The command validates the merged seed payloads before writing. It can add or
update drafted places, events, and connections, but it does not create the route
metadata record in `routes.json`.

## Review Boundaries

Use these gates before seed writing:

- The dossier identifies source directions and risk notes.
- Candidate events have inclusion rationale, not only chronology.
- Event framing has reviewed titles, summaries, significance text, and source
  fields.
- Draft places either reuse existing seed places or have coordinates and source
  risks reviewed.
- Draft connections explain a meaningful relationship.
- `seed-transfer-report.md` and `validation-report.md` have been inspected.
- Agent outputs that shaped route content have reviewed variants in the route
  folder.

Generated draft text should stay cautious. Do not use the pipeline to turn
weakly sourced or contested claims into settled statements.

## Verification

After changing the pipeline or route artifacts, run the relevant backend tests:

```bash
uv run --project backend pytest backend/tests/test_route_content_pipeline.py
```

For broader backend confidence, run from the backend directory:

```bash
cd backend
uv run pytest
```
