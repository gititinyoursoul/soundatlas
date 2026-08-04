# Content Pipeline Interaction Contract

## Purpose

This document is the normative interaction contract for the smallest useful
SoundAtlas editorial review loop. It defines how one human editor inspects a
generated route, decides which proposed events remain in it, sees unresolved
risks, and publishes one exact reviewed result.

The MVP needs a usable visual review surface, but it does not need a generalized
admin platform. Route generation and regeneration remain CLI operations. Review
reuses the existing explorer experience instead of requiring the editor to work
through raw Markdown or JSON files.

## Current And Target Boundary

The route pipeline currently produces reviewable route-folder artifacts and
uses `accepted-events.json` as its downstream gate. That implemented behavior
remains authoritative until the focused follow-up Issues are completed.

The target MVP interaction is:

```text
CLI generates or regenerates one route result
  -> editor opens that result in editorial review mode
  -> editor explores it through the map, timeline, and StoryPanel
  -> editor may set each event to Draft, Approved, or Don’t use
  -> editor inspects warnings and technical readiness
  -> editor publishes the exact Draft-plus-Approved route result
  -> validated content becomes canonical runtime data
```

This contract defines that target interaction without claiming that its review
or publication behavior is implemented today.

## Authority And Boundaries

This contract owns the human interaction and state boundaries for route review
and publication. It does not own historical judgment, source-quality rules,
media approval rules, runtime geography, or seed schemas.

- `editorial-workflow.md` describes the currently implemented file-based flow.
- `event-editorial-quality-standards.md` owns event prose, route fit, claim, and
  source-discipline guidance.
- `accepted-event-dossier-template.md` owns the current accepted-event handoff.
- Issue #81 implemented the compositional event-geography runtime established
  by completed Issue #70.
- Issue #71 owns private route-review data and state behavior.
- Issue #72 owns the explorer-based editorial review surface.
- Issue #73 owns exact-result validation and publication.
- Issue #85 owns the deferred per-event revision-request handoff.

When this target differs from implemented pipeline behavior, current workflow
and command documentation remain descriptive until the corresponding follow-up
Issue is implemented and verified.

## Editorial Review Surface

The editor reviews one generated route result in a clearly marked editorial
mode that reuses the normal explorer map, timeline, and StoryPanel. The route
result must not be mistaken for canonical or published content.

The surface must:

- identify the route result under review;
- keep map, timeline, and StoryPanel selection coordinated;
- show every proposed event with its current private editorial state;
- show agent recommendations and rationales as advisory information;
- keep relevant event and route warnings visible;
- distinguish technical readiness from editorial warnings; and
- provide one route-level Publish action when technical validation permits it.

The first MVP surface is read-only apart from editorial-state controls. Content
corrections continue through the existing Codex or CLI workflow. Direct field
editing and revision requests are not part of this initial interaction.

## Private Editorial States

Each proposed event has one route-scoped human editorial state:

| State | Meaning | Included when the route is published? |
| --- | --- | --- |
| Draft | Included in the route but not marked as human-approved. This is the default for generated proposals. | Yes |
| Approved | Included in the route and explicitly accepted by the human editor. | Yes |
| Don’t use | Excluded from this route without deleting its proposal or editorial history. | No |

The controls must use text and shape or icon cues in addition to green,
neutral, and red styling. Color alone must not communicate state.

These states are editorial-only. The public explorer presents Draft and
Approved events in the same way and displays no editorial-state badge or
control. Don’t use events do not appear in the published route.

## State Separation

Private editorial state must remain distinct from:

- agent `keep`, `maybe`, `merge`, or `reject` recommendations and merge targets;
- the existing seed `review_status` compatibility field;
- source, media, and image review state;
- warnings and technical validation results; and
- route-level publication authorization.

Agent recommendations help the editor decide but never set human state,
combine content, exclude an event, or authorize publication automatically.
Approving an event does not approve all of its sources or media. Publishing a
route does not convert its Draft events to Approved.

## Warnings And Technical Errors

Missing or weak sources, unresolved claims or merges, uncertain place or time
data, unreviewed media or images, and other editorial risks remain visible as
warnings. Warnings inform judgment but do not require individual acknowledgment
and do not block publication by themselves.

Structurally invalid data and failed or unresolved references are technical
errors. They are not editorial decisions and may prevent publication when the
system cannot safely produce canonical runtime data.

Neither warnings nor successful validation constitute human approval.

## Publication

Publish is one explicit, human-only route decision over the exact result shown
in editorial review. The publication summary must identify the route result,
list the Draft and Approved events that will be included, show excluded Don’t
use counts, preserve visible warnings, and report technical readiness.

After the decision, the system validates and promotes that exact
Draft-plus-Approved result into canonical runtime data. Publication:

- excludes Don’t use events without deleting their editorial records;
- preserves the current Draft or Approved state internally;
- does not resolve warnings or approve Draft events;
- does not apply agent recommendations automatically; and
- does not commit, push, or deploy repository changes.

Commit, push, and deployment remain explicit developer operations.

## Changes After Publication

Published content is a stable result, not a mutable pointer to the latest agent
output. Automatic generation or regeneration must not replace it.

A later content change creates a new Draft proposal. The currently published
route remains unchanged until the revised result is opened in editorial review
and explicitly published. The MVP does not require a generalized version
browser, immutable run archive, or cross-run comparison interface to enforce
this boundary.

## Minimal-Input Principle

Generated events default to Draft, so the editor does not have to approve every
event for a route to remain usable. The review surface should lead with counts,
agent recommendations, merge targets, rationales, warnings, and clear defaults.
The human normally needs to approve, exclude, or leave an event as Draft rather
than synthesize decisions from raw artifacts.

## Non-Goals

The current MVP contract does not require:

- accounts, roles, authentication, approval chains, or multi-user editing;
- a generalized content dashboard or CMS;
- direct structured-field editing;
- pipeline configuration, execution, or reruns from the review surface;
- normalized model, prompt, or pipeline-version provenance;
- immutable run archival, retention rules, or run comparison;
- automatic editorial, source, media, or publication approval; or
- automatic commit, push, deployment, or public-repository management.

These ideas require independently justified Issues. They are not implied by
the existence of the thin editorial review mode.

## Acceptance Conditions

The interaction satisfies this contract when:

- one generated route result can be inspected through the coordinated explorer
  without reading raw structured files;
- every proposed event has a private Draft, Approved, or Don’t use state and
  generated proposals default to Draft;
- Draft and Approved events are included, while Don’t use events are excluded
  without deletion;
- public presentation exposes none of those editorial states;
- agent recommendations, seed compatibility state, media/source review,
  warnings, technical errors, and publication authorization remain distinct;
- warnings remain visible and non-blocking while unsafe technical errors may
  prevent publication;
- one explicit action publishes the exact reviewed Draft-plus-Approved result;
- later changes cannot replace the published result without another explicit
  review and publication decision; and
- the workflow adds no generalized admin, provenance, archive, editing, or
  deployment platform.

## Follow-Up Boundary

This contract authorizes no runtime behavior by itself. Issues #71, #72, and
#73 implement the focused data, review-surface, and publication slices. Issue
#85 remains deferred correction-loop work. Issues #74 and #75 remain open as
independently valuable but deferred provenance and archive ideas; this contract
does not require them.
