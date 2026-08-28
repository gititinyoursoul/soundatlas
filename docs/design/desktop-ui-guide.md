# Desktop UI Guide

This document is the concise design contract for SoundAtlas desktop frontend
and UX decisions. Use it for non-trivial planning, implementation, and visual
review. Desktop is the initial design authority; the mobile section below is a
compatibility boundary, not a mobile design system.

## Authority and Evidence

| Artifact | Meaning | How to use it |
| --- | --- | --- |
| This guide | Durable desktop rules and review expectations | Apply to every non-trivial frontend or UX change. |
| [`current-frontend-design.md`](current-frontend-design.md) | Fuller current intended product, state, and component baseline | Check the affected workflow and component responsibilities. Update it only when the intended design changes. |
| Explicitly referenced repository mockup, including native SVG mockups in [`mockups/`](mockups/) | Target state for the named slice | Treat a mockup as a target only when this guide, the current design baseline, or an accepted Issue explicitly names it. Folder presence alone does not approve it. |
| Approved screenshot in [`screenshots/`](screenshots/) | Reviewed evidence of an observed implementation state | Compare current rendering with it. A screenshot does not independently authorize a new target. |
| Running frontend | Actual current behavior | Inspect it to find implementation gaps; do not infer that existing behavior is intended merely because it is implemented. |

An accepted Issue defines the scope of a change. When an approved change
intentionally alters a rule or the intended frontend baseline, update the
relevant authority in the same work package rather than leaving contradictory
guidance.

## Desktop Review Viewports

- Use `1440x1000` as the primary full-shell review viewport.
- When a change affects layout, also inspect widths around `1280px` and
  `1024px`. Choose a height that exposes the complete affected workflow.
- Review the states that the change can affect, not only the initial success
  state.
- Require mobile evidence only when the change affects mobile layout,
  reachability, input, or interaction behavior.

These are design-review targets, not application breakpoints. A component may
need additional checks when its own content or interaction creates a credible
failure between them.

## Shell Hierarchy

The desktop experience is a dense, documentary research atlas:

1. The map remains the primary spatial surface.
2. Compact route context identifies the active narrative without becoming a
   second route-selection surface.
3. First-level navigation owns route selection and mode-specific operations.
4. The timeline explains chronology and the selected event's position.
5. The selected-event inspector provides story, place, source, related-event,
   and media detail.

Map, timeline, route context, and inspector use the same selected route and
event state. A local design must not introduce a competing selection model.

## Density and Visual Conventions

- Prefer compact, repeated-use controls and panels over marketing-style cards
  or generous dashboard spacing.
- Use the existing system sans-serif stack. Preserve readable hierarchy through
  weight, size, spacing, and labels before adding decoration.
- Use the restrained existing neutral palette as the default: dark text,
  light-grey canvas and panels, and quiet borders. Route colours identify
  narrative context; they should not dominate large map fills or replace text
  and programmatic state.
- Keep the current visible focus convention: a clearly contrasting 2px outline
  with separation from the control. The current blue `#2454d6` treatment is the
  desktop reference unless an approved change updates the design authority.
- Keep interactive targets at least 44px in both dimensions. Repeated route rows
  use the current compact 60px minimum treatment so title plus years or review
  context remain readable.
- Truncate a long single-line label only when its full value remains available
  through accessible naming or nearby context. Do not solve routine density by
  removing identity or state information.

These values document proven conventions. They do not create a token system or
require migration of unchanged CSS.

## Reusable Patterns

### Route and navigation rows

- Route selection happens only in navigation.
- List `Routes` and, in Editorial Mode, `Routes to review` as separate
  first-level groups. Do not introduce a nested route screen.
- A route row keeps its title, years or review-revision context, route-colour
  cue, selected state, and keyboard focus treatment.
- The selected state must be conveyed by text or programmatic state as well as
  colour.

### Review surfaces

- Public mode exposes reader behavior, not editorial or media authority.
- API/admin mode may expose media review.
- Editorial Mode may expose route review and revision-bound publication.
- Keep review context explicit: reader baseline and review revision may share a
  stable route identity while remaining different selectable contexts.
- Keep authoritative actions route- and revision-specific. Avoid bulk approval,
  bulk publication, or platform-style administration in the MVP.

### Map, timeline, and inspector

- Selection from any primary exploration surface updates all other surfaces
  through central state.
- Use route colour as an accent for narrative selection. Preserve semantic map
  fills and readable selected-place treatment.
- Keep sources and media discoverable but visually secondary to understanding
  the event, place, and chronology.

## Interaction States

For every affected interactive surface, review the applicable states:

- default and hover;
- keyboard focus;
- selected or active;
- disabled or unavailable, with a reason where needed;
- loading;
- empty;
- error and retry;
- success or saved feedback for state-changing work; and
- warning, blocked, or destructive/authoritative action confirmation when the
  workflow can produce those outcomes.

Do not add states that the workflow cannot reach. Do not omit a credible state
merely because the happy path mockup does not show it.

## Anti-Patterns

- Duplicate route selectors in the header, map view, or footer.
- A second-level route-navigation screen.
- Several routes' events displayed as one default map or timeline state.
- Mock-only UI when seed or API data exists.
- Colour-only meaning, hidden keyboard focus, or unreachable controls.
- Treating an exploratory mockup or an old screenshot as automatic authority.
- Broad dashboard, multi-user administration, component-library, token-system,
  or visual-regression infrastructure work without an approved Issue.
- Unrelated component redesign or speculative responsive behavior inside a
  focused frontend change.

## Mobile Compatibility

Until a separate mobile design contract is approved, desktop rules remain the
design authority. Frontend changes must still preserve:

- a reachable critical workflow, including route selection where applicable;
- keyboard and touch accessibility;
- readable content and explicit selected/error state; and
- the absence of desktop-only controls that silently disappear without an
  equivalent path.

Independent mobile hierarchy, mobile-specific density, and detailed mobile
visual styling are deferred. If a change affects mobile layout or interaction,
its Issue Plan must name the affected mobile states and require narrow-screen
runtime evidence. Otherwise, do not expand a desktop slice into a mobile
redesign.

## Frontend Change Record

A non-trivial frontend or UX Plan must record:

- **Applicable contract rules:** the sections or concrete rules used;
- **Affected states:** the interaction and failure states changed or preserved;
- **Target references:** relevant explicitly approved mockups, or `None` with a
  reason;
- **Desktop evidence:** the viewport and screenshot/browser checks that prove
  the visual claim; and
- **Mobile evidence:** required only when mobile layout or interaction is
  affected.

Implementation review compares the accepted Issue, those recorded design
inputs, the actual diff, and proportional runtime evidence. Visual evidence is
not required for a non-visual frontend change when the Plan explains why it
cannot affect presentation.
