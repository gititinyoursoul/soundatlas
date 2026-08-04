---
name: soundatlas-frontend-implementation
description: Implement SoundAtlas SvelteKit and TypeScript frontend changes from approved GitHub Issues, including map, timeline, route switching, navigation drawer, StoryPanel, media UI, shared selection state, Leaflet integration, and frontend validation.
---

# SoundAtlas Frontend Implementation

Use this skill for frontend implementation work from an approved SoundAtlas
GitHub Issue. The approved Issue is the primary product and scope authority.

## Required context

Read these before editing:

- `AGENTS.md`
- `docs/implementation-plan-workflow.md`
- `docs/workflow-registry.md`
- the approved GitHub Issue, including its `## Grill-Me Review` and `## Plan
Update` or `## Detailed Plan Update` comments when risk flags are present

Optional context may clarify the Issue without overriding it:

- viewport target: desktop, mobile, or both
- route selection model: single-select or multi-select
- surface type: public-facing, admin-only, or mixed
- expected interactions and related API or seed fields

## Implementation gate

Implement only when the user explicitly requests implementation of the approved
Issue, for example `implement issue #<number>`, or when the work is clearly
trivial and low-risk.

For Issue-based work with security, credentials, infrastructure, networking,
workflow, UX, editorial, cross-cutting, user-visible, vague, or materially
ambiguous risk flags, require both:

- a `## Grill-Me Review` comment with required material decisions confirmed;
- a `## Plan Update` or `## Detailed Plan Update` that incorporates them.

Explicit implementation wording does not bypass these gates. Stop for approval
if implementation reveals product behavior or another high-risk decision outside
the approved Issue. Record low-risk local assumptions in the Implementation
Report or Issue comment.

## Frontend constraints

- Use SvelteKit, TypeScript, and Leaflet patterns already established in the app.
- Keep the map as the primary MVP surface and use seed- or API-backed data.
- Keep components small and domain-named, such as `MapView`, `Timeline`,
  `RouteFilter`, `NavigationDrawer`, and `StoryPanel`.
- Identify the central owner of selected route and selected event state before
  editing components.
- Keep map markers, timeline interactions, route selection, story navigation,
  and related-event navigation synchronized through shared state.
- Preserve route colors, event ranges, selected states, and loading, empty, and
  error states when relevant to the approved Issue.
- Keep Leaflet browser-safe and preserve required global Leaflet selectors.
- Do not add local audio, video, image, generated media, secrets, or API keys.
- Treat media and review controls as admin-only unless the approved Issue
  explicitly defines a public-facing behavior and its gating.

## Process

1. Read the approved Issue and identify the exact frontend acceptance criteria.
2. Inspect the existing route, components, state owner, API client, types, and
   related seed/API response shapes before editing.
3. Define or update TypeScript types and API client behavior before wiring UI
   state when the Issue changes data access.
4. Implement only the approved frontend slice. Preserve existing visual design
   and responsive behavior unless the Issue explicitly changes them.
5. Keep filtering, selection, and derived state testable where practical.
6. Check Svelte warnings, including invalid self-closing non-void elements such
   as `<iframe />`.
7. If an implementation reveals a missing product or high-risk decision, stop
   and update the Issue rather than silently expanding scope.

## Validation

Run the narrowest relevant checks first:

```sh
cd frontend
npm run lint
npm run check
npm test
```

For larger frontend changes, also run:

```sh
npm run build
```

Use screenshot or browser checks when the approved Issue requires them. If a
browser or screenshot environment is unavailable, report the blocker clearly.

## Implementation Report

Before finalizing the report for completed non-trivial Issue work, use
`soundatlas-implementation-review`. Resolve or route required findings, then
include its Review Result in this same report. Do not post a separate routine
review comment.

Report in the Issue and final response:

```md
## Summary

- What frontend behavior changed.
- Which approved Issue behavior was implemented.

## Interaction behavior

- Route selection:
- Timeline:
- Marker selection:
- Story Panel:
- Empty/loading/error states:

## Acceptance Criteria Result

- AC1: Pass/Fail — evidence

## Verification

- `<command>` — Pass/Fail

## Review Result

- Verdict:
- Reviewer mode:
- Compared artifacts:
- Evidence coverage:
- Findings and routing:
- Documentation impact:

## Remaining Risks

- None, or the specific blocker.
```

Do not commit unless the user explicitly requests it. If committed, use a
Conventional Commit and include `Issue: #<number>` in the commit body.

After a successful commit for completed Issue work, capture the commit hash,
verify the acceptance criteria and Issue-relevant working-tree state, post the
standard completion comment, and close the Issue. Do not close for uncommitted,
partial, WIP, incomplete, or ambiguously scoped work, or when the human asks to
keep the Issue open. If commenting or closing fails, report the failure and
leave the Issue open when possible.
