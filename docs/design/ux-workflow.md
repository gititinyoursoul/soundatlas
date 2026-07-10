# UX Improvement Workflow

This document describes a repeatable GPT-assisted process for improving the SoundAtlas UX. Use it as a step-by-step workflow for audits, redesign passes, screenshot critique, and implementation planning.

Use `docs/skills-workflow.md` as the routing guide for when UX work should stay in a prompt, move into a skill, or create a GitHub Issue Plan Update for later implementation.

The goal is not to ask for a vague redesign. The goal is to run small, inspectable UX cycles that produce clear findings, one focused implementation pass, and validation before moving on.

## SoundAtlas UX Frame

SoundAtlas is an interactive music history app. The MVP scope is **New York 1965-1985**, with the first vertical slice **Birth of Hip-Hop: Bronx 1970-1985**.

The first screen should be the actual exploration surface, not a landing page. The primary interface is:

- Map
- Timeline
- Route switching
- Event inspector

The app should make music history understandable across three axes:

- Place: map, places, neighborhoods, venues, and movement
- Time: event years, periods, and sequence
- Sound and culture: events, routes, connections, sources, and media links

The default design posture is **Research Atlas with selected Story Explorer behavior**:

- Dense, documentary, source-aware, and usable
- Map-first, with route and timeline support
- Guided enough for a user to follow a narrative route
- Grounded in real seed/API data, not mock-only UI

Use `docs/design/current-frontend-design.md` as the baseline for the current intended frontend design. UX audits should compare the implemented app against that baseline, and design passes should update it when the intended design changes.

Design documentation is organized by purpose:

- `docs/design/current-frontend-design.md` records the current intended frontend baseline.
- `docs/design/audits/` stores dated UX audits, design explorations, and critique records.
- `docs/design/screenshots/` stores the current approved screenshot set when screenshots should stay in Git.
- `docs/design/mockups/` stores visual mockups, diagrams, and supporting images referenced by audits or plans.
- `docs/design/ux-workflow.md` documents this process.

## Core Rules

Follow these rules for every UX cycle:

- Start with an audit before proposing broad redesigns.
- Compare proposed changes against `docs/design/current-frontend-design.md`.
- Work on one screen, workflow, or interaction slice at a time.
- Keep each implementation pass small enough to review independently.
- Preserve central route/event selection state unless the pass explicitly changes it.
- Use real seed/API-backed data where possible.
- Cover loading, empty, error, selected, and responsive states.
- Validate frontend changes with tests and type checks.
- Use screenshots for visual critique after implementation.
- Document durable findings or decisions in `docs/`.

## Prompt Stack

Use the existing prompts in this order:

1. `prompts/design-ux.md` - UX audit, main screen design plan, screenshot critique
2. `prompts/grill-me.md` - critique and narrow the selected UX idea before Issue planning when needed
3. `soundatlas-implementation-planning` - turn the selected design idea into one Issue Plan Update when needed
4. `prompts/implement-frontend-map.md` - implement frontend/map-related changes from an approved Issue with a Plan Update when needed
5. `prompts/write-tests.md` - add or update focused tests
6. `prompts/update-docs.md` - update durable docs that the UX change relies on or changes

Avoid creating one-off prompts for audit, design direction, or screenshot critique unless `prompts/design-ux.md` no longer covers the work.

## Reusable UX Cycle

### Step 1: Define the UX Target

Before auditing or redesigning, define the exact target.

Inputs:

- Screen, component, or workflow to improve
- Current design baseline from `docs/design/current-frontend-design.md`
- Primary user goal
- Target viewport: desktop, mobile, or both
- Surface type: public-facing, admin-only, or mixed
- Constraints and non-goals

Output:

- One-sentence UX target
- List of affected surfaces or components
- Explicit non-goals

Example:

```text
Improve the main exploration screen so a user can follow the Birth of Hip-Hop route through map, timeline, and event inspector without losing selected-event context.
```

### Step 2: Audit Without Editing

Use the **UX Audit** template in `prompts/design-ux.md`.

Rules:

- Do not make code changes.
- Inspect current layout, data flow, component boundaries, visual hierarchy, and missing states.
- Ground findings in current code and real seed/API data.
- Compare implementation against `docs/design/current-frontend-design.md`.
- If screenshots are unavailable, state that the audit is source-based.

Output:

- Top usability issues
- Top visual hierarchy issues
- Data/state-flow issues
- Missing loading, empty, error, selected, or responsive states
- Recommended design direction
- Proposed first UX pass
- Files and components likely affected

Store durable audits in `docs/design/audits/` with a date or frontend version in the filename, for example:

```text
docs/design/audits/YYYY-MM-DD-frontend-ux-audit.md
```

If an audit or exploration includes visual mockups, store them in `docs/design/mockups/` and reference them with relative links from the audit or plan.

### Step 3: Choose the Design Direction

Choose a direction before implementation. The design direction is a decision lens, not the implementation scope. It describes what the experience should optimize for and how tradeoffs should be resolved.

Output:

- Chosen direction
- Why it fits the current UX target
- Tradeoffs
- What should not change in this pass

For the current MVP, the default direction is:

```text
Research Atlas with selected Story Explorer behavior.
```

This means the map remains primary, the timeline clarifies sequence, the event inspector explains the selected event, and source/media links stay visible but secondary.

Use the direction to evaluate workflow slices. For example, if the direction is Research Atlas with selected Story Explorer behavior, a proposed slice should strengthen map-first exploration, selected-event context, sequence clarity, or source-aware storytelling.

### Step 4: Select One Workflow Slice

Define the exact user path for the next pass. The workflow slice is the unit of work: it turns the design direction into one concrete user action path.

Candidate workflow slices should come from:

- Product goal: what the app must help the user accomplish
- Current app behavior: what users can already click, select, navigate, or inspect
- Audit findings: where the current experience breaks down
- Expected user tasks: what a first-time or returning user is likely trying to understand

Pick one workflow slice based on:

- Highest user value
- Smallest reviewable implementation size
- Highest audit severity
- Lowest implementation risk

Do not improve the whole app at once.

Output:

- Workflow steps
- Primary state changes
- Expected visible state after each action
- Success criteria

Example candidate workflow slices for the current MVP:

- First arrival path: user opens the app, sees the default route, and understands the relationship between map, timeline, and inspector.
- Event selection path: user selects a timeline event, then map and inspector update with clear selected-event context.
- Map exploration path: user selects a map marker, then inspector and timeline show what happened there and where it sits in sequence.
- Source/media inspection path: user reads an event, inspects sources/media, then returns to the route sequence.

Example detailed workflow slice:

1. User opens the app.
2. The Birth of Hip-Hop route is selected by default.
3. The map shows relevant places.
4. The timeline shows the event sequence.
5. User selects an event from the map or timeline.
6. Map, timeline, and event inspector update from the same selected event state.
7. User inspects summary, significance, sources, and media.

### Step 5: Plan One UX Pass

Use the **UX Pass Plan** template in `prompts/design-ux.md` to narrow the
selected workflow slice before implementation planning. Then use
`prompts/grill-me.md` or direct conversation to critique the UX slice, and use
`soundatlas-implementation-planning` to turn it into one GitHub Issue Plan
Update before implementing non-trivial approved work.

Plan only one pass at a time.

Useful pass types:

- Layout and visual hierarchy pass
- Shared state and interaction pass
- Map marker or map context pass
- Timeline sequence/navigation pass
- Event inspector readability/content pass
- Loading, empty, and error states pass
- Responsive layout pass
- Final polish pass

Output:

- Affected files/components
- State changes
- Layout and interaction changes
- Responsive behavior
- Test plan
- Acceptance criteria
- Risks and open questions
- Suggested commit grouping

### Step 6: Implement One Pass

Use `prompts/implement-frontend-map.md` for frontend map or exploration-surface changes from an approved Issue with a Plan Update when needed, or the matching skill if that workflow has already been extracted.

Rules:

- Implement only the planned pass.
- Keep components small and domain-named.
- Use existing seed/API-backed data.
- Do not introduce unrelated refactors.
- Do not add mock-only UI when real data exists.
- Keep route switching, timeline, map, and event inspector synchronized through shared state.
- Capture real follow-up work that is out of scope for the pass in GitHub Issues.

If the pass changes shared state, filtering, API behavior, or interaction logic, use `prompts/write-tests.md` to add or update focused tests.

### Step 7: Validate

For frontend changes, run:

```bash
npm test
npm run check
```

For larger visual, layout, or build-impacting changes, also run:

```bash
npm run build
```

For active local frontend test development, use:

```bash
npm run test:watch
```

When possible, inspect the running app in desktop and mobile viewports before considering a UX pass complete.

### Step 8: Critique With Screenshots

After a visual pass, run the app and capture desktop and mobile screenshots where practical.

Use the **Screenshot Critique** template in `prompts/design-ux.md`.

If the screenshots are meant to become the current tracked reference set, promote
the approved files into `docs/design/screenshots/` and delete any stale files
from that tracked folder before committing.

Output:

- Whether the map still feels primary
- Place/time/story clarity issues
- Visual hierarchy issues
- Spacing, density, and readability issues
- Affordance and interaction cue issues
- Responsive issues
- Prioritized polish items

Do not implement every critique item automatically. Pick the highest-impact small item, plan it as a new pass, or stop if the pass is good enough.

### Step 9: Document and Commit

Before committing, decide whether the cycle produced durable knowledge.

Update documentation when:

- A UX audit identifies reusable findings.
- A design direction changes.
- The intended frontend design changes.
- A product or architecture decision is made.
- New work packages arise.

Likely docs:

- `docs/design/audits/`
- `docs/design/mockups/`
- `docs/design/current-frontend-design.md`
- `docs/mvp-concept.md`
- GitHub Issues for planned follow-up work

Commit in small groups, for example:

```text
docs(design): add frontend UX audit
feat(frontend): improve map-first layout hierarchy
fix(frontend): clarify timeline prehistory event state
test(frontend): cover route event selection
```

Do not commit unless explicitly requested.

## Stop Conditions

Stop a UX cycle when:

- The planned pass is implemented.
- Acceptance criteria pass.
- `npm test` and `npm run check` pass for frontend changes.
- Screenshot critique shows no high-impact issue that belongs in the same pass.
- Remaining issues can be captured as follow-up work.

Avoid rolling multiple UX passes into one large change unless the user explicitly asks for a broader redesign.

## Design Checklist

Use this checklist before finishing each UX pass:

- Can the user immediately tell this is about music history in place and time?
- Is the map clearly the main surface?
- Does selecting a place or event update map, timeline, and inspector together?
- Does the timeline clarify sequence rather than just decorate the page?
- Are source links visible but not dominant?
- Does the UI work with real seed/API data?
- Are empty, loading, and error states handled?
- Is the app usable on laptop-size screens first?
- Does the responsive version preserve the exploration workflow?
- Are admin-only controls clearly gated or marked for gating?
- Are follow-up tasks documented when they are not part of the current pass?

## Starting a New UX Cycle

Use this sequence:

1. Define the UX target.
2. Read `docs/design/current-frontend-design.md`.
3. Run a no-code audit with `prompts/design-ux.md`.
4. Save durable audit findings in `docs/design/audits/`.
5. Choose one design direction.
6. Select one workflow slice.
7. Plan one UX pass.
8. Implement that pass.
9. Validate with tests/checks and screenshots.
10. Critique, polish, document, and commit if requested.
