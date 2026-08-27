---
name: soundatlas-experimental-route-authoring
description: Execute, resume, or evaluate one approved stage of a SoundAtlas experimental route-authoring research run using the baseline-1.1 contracts. Use for work under docs/content/route-experiments, including creating a run brief, running numbered research or narrative stages, recording checkpoints or stopped runs, and producing comparable route-version evidence. Do not use for the current automated route pipeline, direct seed curation, canonical route publication, or unapproved route research.
---

# SoundAtlas Experimental Route Authoring

Run one explicit stage of the `baseline-1.1` experimental method and leave a
durable output that another agent or conversation can resume from.

## Required context

Before writing a run artifact, read:

- `AGENTS.md`;
- the approved GitHub Issue, its accepted Concept, current Plan, and matching
  `## Proceed to Implementation` record when repository edits are non-trivial;
- `docs/content/editorial-workflow.md` and the relevant editorial quality
  standards;
- the run's `00-run-brief.md`; and
- every named input required by the selected stage reference.

Do not reconstruct missing route state from conversation memory. Stop when a
required input, Human decision, or approved write boundary is absent.

## Authority boundary

Experimental runs live under:

```text
docs/content/route-experiments/<experiment-id>/versions/<version-id>/
```

The run brief and numbered outputs are authoring evidence, not canonical route
content. Do not copy, promote, or treat them as authority under
`docs/content/routes/<route-id>/`, `data/seed/`, editorial review, or
publication without a separately approved handoff.

A **research run** is one execution of the method. Its result is one
authoring-only **route version**. An **editorial review revision** remains the
existing exact review-state identity and is not a route version.

## Stage routing

Read only the active stage reference after the required context above:

| Stage | Reference | Output |
| --- | --- | --- |
| 00 | [Run brief](references/00-run-brief.md) | `00-run-brief.md` |
| 01 | [Topic discovery](references/01-topic-discovery.md) | `01-topic-discovery.md` |
| 02 | [Narrative concepts](references/02-narrative-concepts.md) | `02-narrative-concepts.md` |
| 03 | [Light evidence and route shape](references/03-light-evidence-route-shape.md) | `03-light-evidence-route-shape.md` |
| 04 | [Targeted gap research](references/04-targeted-gap-research.md) | `04-targeted-gap-research.md` |
| 05 | [Cohort decision](references/05-cohort-decision.md) | `05-cohort-decision.md` |
| 06 | [Deep route research](references/06-deep-route-research.md) | `06-deep-route-research.md` |
| 07 | [Cross-Event synthesis](references/07-cross-event-synthesis.md) | `07-cross-event-synthesis.md` |
| 08 | [Narrative draft](references/08-narrative-draft.md) | `08-narrative-draft.md` |
| 09 | [Evidence review](references/09-evidence-review.md) | `09-evidence-audit.md`, `09-corrected-draft.md` |
| 10a | [Final route copy](references/10a-final-route-copy.md) | `10a-final-route-copy.md` |
| 10b | [Presentation and visual claims](references/10b-presentation-visual-claims.md) | `10b-presentation-visual-claims.md` |
| 11 | [Run evaluation](references/11-run-evaluation.md) | `11-run-evaluation.md` |

Steps 01 and 02 are conditional. Skip either only when the run brief names the
declared entry point and records why the skipped responsibility is already
satisfied or outside the run.

For stages 03–11, also read [Shared output schemas](references/shared-output-schemas.md).
Use only the record types required by the active stage. Preserve stable IDs and
explicit missing-value states across later outputs; do not rediscover or rename
the same Candidate, Event, relationship, section, or claim silently.

## Execution workflow

1. Resolve the approved experiment ID, version ID, method (`baseline-1.1`),
   declared entry point, active stage, status, and write boundary from the run
   brief and Issue.
2. Read the matching stage reference, its named inputs, and the shared output
   schemas for stages 03–11. Do not read later outputs as hidden answers during
   a baseline comparison or replay.
3. Check whether the stage is authorized, its inputs are complete, and a
   material Human decision is pending. Stop with a concrete missing-input or
   decision report when any check fails.
4. Perform only the selected stage. Use current product documentation and code
   as evidence where the stage depends on actual SoundAtlas capability; do not
   design from assumed behavior.
5. Write the stage's named output without silently rewriting prior completed
   outputs. A rerun may replace the active stage output only before downstream
   work depends on it and when the approved run scope permits that replacement.
6. Update the run brief's current stage, status, checkpoint, and stop reason as
   required by the stage contract. Preserve completed outputs when work fails
   or stops.
7. Stop at every required Human checkpoint. A recommendation or successful
   validation is not a Human decision and does not authorize the next stage.
8. Report the output path, evidence gathered, material warnings, run status,
   Human decision needed, and next permitted stage.

## Lifecycle rules

- Use `in-progress` while an authorized stage is being developed.
- Use `checkpointed` when the run has a reviewable result and waits for a Human
  decision before continuing.
- Use `completed` only after the run reaches its authorized terminal stage and
  `11-run-evaluation.md` records the result.
- Use `stopped` when the Human ends the run or a material unresolved condition
  prevents continuation; record the reason and last completed stage.
- Continue an accepted checkpoint in the same version. Start a new version for
  a material restart that changes already-consumed inputs, route direction, or
  method choices rather than silently rewriting the earlier evidence.

## Human authority and safety

Agents may research, recommend, compare, draft, audit, and report. The Human
retains authority over material route direction, historical and Source
judgment, cohort acceptance, route-version selection, reader-facing copy,
media and rights approval, visual historical claims, and publication.

Never auto-advance a Human gate, write Human-owned editorial state, publish a
route, alter canonical seed data, or implement a product capability from this
skill. Route new product, schema, frontend, backend, publication, or workflow
scope through its own approved Issue.

## Common output requirements

Every numbered output must:

- identify the experiment ID, version ID, method, stage, and named inputs;
- separate observed facts, Source-supported claims, interpretations,
  recommendations, Unknowns, Evidence Gaps, and Human decisions;
- preserve relevant Source URLs and explain which claim each Source supports;
- state material map, representation, media, and rights implications when
  relevant;
- record its verdict or stop condition and the next permitted stage; and
- avoid generic `what's next` prose that duplicates this skill's routing.

For every applicable schema field, write a supported value, `unknown`, or
`not-assessed`. Never omit a required field merely because research did not
resolve it. Keep Source references claim-specific and preserve prior IDs and
status transitions so stage-to-stage and run-to-run comparisons remain valid.
