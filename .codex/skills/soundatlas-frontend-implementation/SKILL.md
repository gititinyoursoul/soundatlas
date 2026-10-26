---
name: soundatlas-frontend-implementation
description: Implement SoundAtlas SvelteKit and TypeScript frontend changes from approved GitHub Issues, including map, timeline, route switching, navigation drawer, StoryPanel, media UI, shared selection state, Leaflet integration, and frontend validation.
---

# SoundAtlas Frontend Implementation

This retained entrypoint supplies SoundAtlas requirements for scoped frontend
implementation. The runtime selects suitable implementation capabilities and
execution mechanics; ordinary repository/GitHub tools may fulfil them.

Use the registry's [implementation and review composition](../../../docs/workflow-registry.md#implementation-and-review-composition)
for authority inputs, readiness, allowed effects, evidence and stop routes.
When Pane is selected, use its existing composition contract in that registry.
This skill does not prescribe or copy a provider's implementation procedure.

## Required authorities and context

- `AGENTS.md`, `docs/workflow-registry.md` and
  `docs/github-issue-workflow.md` for repository constraints and lifecycle gates.
- The current approved Issue and confirmed decisions, Concept or
  Concept-not-required basis, latest Plan and matching Proceed when required,
  exact named paths and audited derived files, exclusions and allowed effects.
- `docs/architecture/frontend.md` for SvelteKit/TypeScript/Leaflet, shared
  selection, data/media boundaries and Tailwind migration constraints.
- `docs/design/desktop-ui-guide.md`,
  `docs/design/current-frontend-design.md` and
  `docs/design/ux-workflow.md` for non-trivial frontend or UX work, plus every
  target mockup explicitly referenced for the affected slice.
- Existing components, central route/event state owner, API client, types and
  relevant seed/API/static-data shapes. Identify the viewport, selection model,
  public/admin boundary and affected interaction states from accepted scope.
- Applicable project execution/environment authorities and the validation
  commands in `AGENTS.md`, including Pages validation when affected.

## Required outcome and evidence

The approved frontend slice must preserve the architecture and design
contracts, synchronized selection and relevant loading/empty/error states.
Report the actual route, timeline, marker, StoryPanel and related-event effects
where affected. Data-access changes require aligned types/client behavior;
focused deterministic coverage follows `soundatlas-testing-implementation`.

Non-trivial user-visible work requires the Plan's desktop rules, states,
target references and proportionate runtime/visual evidence. Mobile evidence
is conditional on affected mobile behavior. For non-visual work, retain the
Plan's reason visual evidence is inapplicable. Missing required browser evidence
is a blocker; unresolved material UI-quality findings prevent acceptance under
`soundatlas-implementation-review` and the UX authorities.

Return changed paths, acceptance-criteria evidence, actual validation results,
unavailable or partial execution, risks and unresolved decisions through the
registry contract. `soundatlas-issue-planning` composes the single Issue
Implementation Report including the Review Result; commit and delivery gates
remain with the lifecycle. Preserve this path and discovery manifest until
the separate #203 retirement gate.
