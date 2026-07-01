# Design UX

Reusable prompts for UX and design work on SoundAtlas. These are working templates, not project documentation.

This prompt set is the UX entrypoint for the current workflow. If the repo has a matching UX skill, use that skill's instructions and keep these prompts as the compatibility wrapper.

Design UX prompts produce audit findings, critique, and UX slice proposals.
They do not authorize implementation.
Use `prompts/plan-feature.md` or direct conversation to turn a selected UX slice into a GitHub Issue Plan Update before implementation.

## Shared Context

Use this context at the top of UX/design prompts when the session does not already have enough project context:

```text
Act as a senior UX/product designer and frontend engineer for SoundAtlas.

Project context:
- SoundAtlas is an interactive music history app.
- MVP scope: New York 1965-1985.
- Vertical slice: Birth of Hip-Hop: Bronx 1970-1985.
- The map is the primary interface.
- Timeline, route switching, and event inspector should share one central selection state.
- Use real seed data where possible; avoid mock-only UI.
- The visual tone should be dense, documentary, source-aware, and usable.
- Treat `docs/design/current-frontend-design.md` as the current intended frontend design baseline when available.
- Store durable UX audits, critiques, and design explorations in `docs/design/audits/`.
- Store current approved screenshots in `docs/design/screenshots/` when they are meant to stay in Git.
- Store visual mockups, diagrams, and supporting images in `docs/design/mockups/`.

When reviewing or designing, focus on:
- Map-first exploration
- Place/time/story clarity
- Visual hierarchy
- Interaction flow
- Responsive behavior
- Source and media discoverability
- Small, reviewable implementation steps

Do not suggest a landing page unless explicitly requested.
Do not propose broad redesigns before auditing the current frontend.
If the intended design changes, recommend updating `docs/design/current-frontend-design.md`.
```

## UX Audit

Use this before changing frontend code:

```text
Review the current SvelteKit frontend as a UX/product engineer.

Focus on the MVP: map-first exploration of New York 1965-1985, with the first vertical slice being Birth of Hip-Hop: Bronx 1970-1985.

Use `docs/design/current-frontend-design.md` as the design baseline when available.

Identify the biggest usability and visual design issues. Cover:
- Current layout structure
- Data flow and shared selection state
- Component boundaries
- UX friction
- Missing states
- Visual hierarchy and design inconsistencies

Ground findings in:
- Current implementation files or components
- `docs/design/current-frontend-design.md`
- Screenshots if available
- Real seed/API data where relevant

Do not make changes yet. Return:
- Findings ordered by severity
- Evidence for each finding
- Gaps between implementation and current design baseline
- Recommended design direction
- Candidate UX slices
- Suggested first UX slice
- Files and components likely affected
- Suggested audit filename under `docs/design/audits/` if the findings should be saved
- Suggested mockup filenames under `docs/design/mockups/` if visual artifacts are needed
- Next step: usually turn the selected UX slice into an implementation plan with `prompts/plan-feature.md`
```

## UX Pass Plan

Use this after a UX audit or screenshot critique, before implementation planning.

```text
Plan one SoundAtlas UX pass.

Constraints:
- SvelteKit + TypeScript
- Leaflet map is primary
- Use existing seed data
- Respect `docs/design/current-frontend-design.md` unless the plan explicitly recommends changing the design baseline
- Components should stay small and domain-named, such as MapView, Timeline, NavigationDrawer, RouteFilter, and StoryPanel
- No mock-only UI
- Dense, documentary, usable MVP style
- The first screen should be the product experience, not a landing page
- Save durable design plans or explorations under `docs/design/audits/`
- Save visual mockups and diagrams under `docs/design/mockups/`

Plan exactly one workflow slice. Do not redesign the whole app unless explicitly requested.

Return:
- UX target
- User workflow slice
- Affected surfaces/components
- State/data flow impact
- Visual/layout changes
- Responsive behavior
- Accessibility considerations
- Out of scope
- Acceptance criteria candidates
- Risks or open questions
- Recommended audit/design-plan path under `docs/design/audits/`, if this should be saved
- Recommended mockup path under `docs/design/mockups/`, if visual artifacts are needed
- Next step: create or update the GitHub Issue Plan Update with `prompts/plan-feature.md`
```

## Screenshot Critique

Use this after running the app and capturing desktop or mobile screenshots:

```text
Critique this SoundAtlas screen like a senior product designer.

Focus on:
- Whether the map feels like the primary surface
- Place/time/story clarity
- Visual hierarchy
- Spacing and density
- Readability
- Affordances and interaction cues
- Source and media discoverability
- Responsive layout issues

Suggest specific changes, not general advice.
Prioritize the changes by user impact and implementation size.

Return:
- Prioritized visual/UX findings
- Screenshot evidence
- Whether each finding is bug, polish, or design-direction issue
- Recommended follow-up UX slice
- Whether a GitHub Issue Plan Update is needed
- Whether `docs/design/current-frontend-design.md` should change
- Whether the critique should be saved under `docs/design/audits/`
- Whether supporting annotated screenshots or mockups should be saved under `docs/design/mockups/`
- Next step: usually create the follow-up plan with `prompts/plan-feature.md`, or update the design baseline with `prompts/update-docs.md`
```
