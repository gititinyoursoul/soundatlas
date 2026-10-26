# Design UX

Compatibility entrypoint for bounded SoundAtlas UX findings and proposals.
Use the three modes below with the canonical
[UX workflow](../docs/design/ux-workflow.md). Every mode is inspection and
proposal only: do not edit code, data, or documentation from this prompt.

## Shared Context

Provide the screen/component/workflow, user goal, constraints, relevant audit,
runtime or screenshots, viewport, and known evidence gaps.

Read the [desktop contract](../docs/design/desktop-ui-guide.md) and
[current intended frontend baseline](../docs/design/current-frontend-design.md).
Apply the UX workflow's SoundAtlas UX Frame, Core Rules, and UI Quality Loop,
including its region/evidence/owner/impact/correction format. Inspect a target
mockup only when explicitly referenced by an accepted Issue or design authority;
approved screenshots are observed evidence. State when review is source-based.

Use [workflow routing](../docs/workflow-registry.md) for critique and Issue
planning and the [Issue lifecycle](../docs/github-issue-workflow.md) for
authorization. A UX slice proposal does not replace the canonical Issue Plan.
Recommend artifact paths for durable findings or visual explorations using the
UX workflow's documentation locations; this prompt grants no write authority.

## UX Audit

Use before frontend changes. Inspect the current SvelteKit implementation,
layout, real seed/API data, shared selection state, component boundaries,
friction, missing states, hierarchy, and design consistency.

Return the outputs in the UX workflow's **Step 2: Audit Without Editing**:
severity-ordered findings and evidence, baseline gaps, applicable desktop rules
and states, recommended direction, candidate slices and a suggested first
slice, affected files/components, and suggested audit/mockup paths when useful.
Identify the next critique or Issue-planning step without implementing it.

## UX Pass Plan

Use after an audit or screenshot critique, before implementation planning.
Propose exactly one workflow slice using **Steps 3–5** of the UX workflow.
Preserve the intended baseline unless recommending an explicit design change;
use SvelteKit/TypeScript, small domain-named components, Leaflet as the primary
map, and real seed data. Avoid broad redesign unless explicitly requested.

Return the UX target, workflow slice, state/data flow, affected surfaces,
visual/layout changes, responsive and accessibility considerations, desktop
rules and interaction/failure states, target mockups or `None` with a reason,
planned desktop evidence/viewports, and mobile evidence only when affected.
Include UI-quality findings/disposition, exclusions, acceptance-criteria
candidates, risks/open questions, suggested audit/mockup paths when useful,
and the next critique or canonical Issue-planning step. This remains a proposal.

## Screenshot Critique

Use after runtime capture. Follow **Step 8: Critique With Screenshots** and the
UI Quality Loop in the UX workflow. Review map primacy, place/time/story
clarity, hierarchy, spacing/density, readability, affordances, source/media
discoverability, and responsive behavior.

Return specific findings with screenshot evidence, prioritized by user impact
and implementation size. Classify each as bug, polish, or design direction;
state whether each material finding is corrected, needs follow-up, or blocks
acceptance. Recommend one follow-up slice, whether an Issue Plan or design
baseline change is needed, and suggested audit/annotated-image/mockup paths
when useful. End at the appropriate critique, Issue-planning, or documentation
handoff; do not apply the recommendations automatically.
