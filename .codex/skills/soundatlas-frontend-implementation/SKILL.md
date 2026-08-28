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
- `docs/github-issue-workflow.md`
- `docs/workflow-registry.md`
- `docs/design/desktop-ui-guide.md` and
  `docs/design/current-frontend-design.md` for non-trivial frontend or UX work
- every target mockup explicitly referenced by the accepted Issue, Plan, or
  design authorities for the affected slice
- the approved GitHub Issue, including any recorded Grill-Me findings or
  decisions and its `## Plan Update` or `## Detailed Plan Update` when risk
  flags are present. A standalone `## Grill-Me Review` is used when the result
  is material or explicitly standalone; a clean check may be inline in the
  relevant action comment.

Optional context may clarify the Issue without overriding it:

- viewport target: desktop, mobile, or both
- route selection model: single-select or multi-select
- surface type: public-facing, admin-only, or mixed
- expected interactions and related API or seed fields

## Implementation gate

Implement only when the user explicitly requests implementation of the approved
Issue, for example `implement issue #<number>`, or when the work is clearly
trivial and low-risk.

For non-trivial Issue-based work, require a current `## Plan Update` or
`## Detailed Plan Update` and a later `## Proceed to Implementation` record
linking that exact Plan.

For security, credentials, infrastructure, networking, workflow, UX, editorial,
cross-cutting, user-visible, vague, or materially ambiguous risk flags, also
require a recorded Grill-Me result with required material decisions confirmed
and incorporated into the Plan.

Use a standalone `## Grill-Me Review` for material findings, decisions,
blockers, or explicitly standalone sessions. Record a clean check inline in the
action comment when useful.

Explicit implementation wording does not bypass these gates. Stop for approval
if implementation reveals product behavior or another high-risk decision outside
the approved Issue. Record low-risk local assumptions in the Implementation
Report or Issue comment.

Before the first repository edit, and again before resuming after a canonical
revision or blocking decision, export the current Issue fields defined in
`docs/github-issue-workflow.md` and require
`python scripts/check_issue_readiness.py --file <export>` to pass. Add
`--require-grill-review` when risk flags require a recorded Grill-Me result. If
the Human has authorized the latest Plan but the Proceed record is missing, use
`soundatlas-issue-planning` to record it first. Do not duplicate validator rules
in this Skill.

## Frontend constraints

For non-trivial work, edit only named authorities and the audited direct
consumers listed by the Plan's planned write boundary and Proceed record. Route
any other path or material scope change to a linked Intake Issue.

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

## Tailwind migration policy

Tailwind CSS is the canonical styling approach for application UI.

- New application UI styling must use Tailwind utilities; do not add new
  component-specific legacy CSS.
- Existing component-scoped CSS may remain until that component is migrated.
  A component is fully migrated only when its obsolete component-specific CSS
  has been removed.
- The tracked legacy-CSS baseline, including component CSS and approved global
  exception surfaces, is monotonic: it may stay the same or decrease, but must
  not increase.
- `src/styles/app.css` is the global base-style exception. Third-party or
  library selector overrides belong only in `src/styles/library-overrides.css`;
  neither exception is for new application component styling.
- A stricter requirement to migrate every substantially touched component is a
  separate, later policy phase unless an approved Issue explicitly requires it.

## Process

1. Read the approved Issue and identify the exact frontend acceptance criteria.
   For non-trivial user-visible work, also identify the recorded UI-quality
   findings, applicable desktop-contract rules, planned runtime evidence, and
   any correction required before acceptance.
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

For non-trivial user-visible work, inspect the changed runtime states at the
desktop viewports recorded in the Plan. Inspect narrow screens only when mobile
layout, reachability, input, or interaction is affected. Compare the result
with the recorded UI-quality findings and design authorities. Correct a
material finding within scope or route it as follow-up work; do not present it
as accepted implementation evidence.

## Validation

Run the narrowest relevant checks first:

```sh
cd frontend
npm run validate
```

For larger frontend changes, run the release-level validation instead:

```sh
npm run validate:release
```

For layout-affecting work, run the desktop screenshot or browser checks recorded
in the Plan and compare the affected states with the applicable desktop
contract rules and target references. Require mobile evidence only when the
change affects mobile layout or interaction. For non-visual work, preserve the
Plan's reason that visual evidence is not applicable. If a required browser or
screenshot environment is unavailable, report the blocker clearly.

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

Follow the commit-ready and local-commit lifecycle in
`docs/github-issue-workflow.md`. Use a Conventional Commit and include
`Issue: #<number>` in the commit body.

After a successful push for completed Issue work, follow the post-push
completion lifecycle in `docs/github-issue-workflow.md`: run the local
completion gate, capture the published commit hash, verify acceptance criteria
and Issue-relevant working-tree state, post the single standard completion
comment, and close the Issue only after that comment succeeds.
