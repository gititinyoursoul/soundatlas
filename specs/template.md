# Spec: <feature/change name>

## Status

Draft

<!--
Use one of:
- Draft
- Approved
- Implemented
- Superseded
-->

## Revision

r01

<!--
Filename: rNN-<short-desc>.md
-->

## Supersedes

None

## Request

What the human asked for.

## Goal

What outcome should this change achieve?

## Non-goals

What are we explicitly not doing in this change?

* NG1:
* NG2:

## Change type

<!--
Choose one or more:
- frontend-only
- backend-only
- seed-data-only
- enrichment workflow
- documentation-only
- cross-cutting
-->

* Type:

## Scope

What parts of the product, data, or workflow are affected?

* Routes/pages:
* Components:
* Backend endpoints:
* Seed files:
* Enrichment files:
* Docs/TODOs:

## Requirements

* R1:
* R2:
* R3:

## Acceptance criteria

Acceptance criteria should be concrete and testable.

* AC1:
* AC2:
* AC3:

## Assumptions

* A1:
* A2:

## Open questions

* Q1:
* Q2:

## Blocking questions

These must be resolved before implementation if they affect data loss, destructive writes, schema changes, seed data shape changes, permissions/security, privacy, external API behavior, generated media review boundaries, historically sensitive claims, irreversible workflow changes, or production stability.

* BQ1:

## UX states

<!-- Required for frontend or UX changes. Delete if not relevant. -->

* User action:
* Visible state:
* Loading state:
* Empty state:
* Error state:
* Selected state:
* Keyboard/accessibility considerations:

## Backend/API behavior

<!-- Required for backend/API changes. Delete if not relevant. -->

* Endpoints:
* Request/query parameters:
* Response shape:
* Error behavior:
* Filtering behavior:
* Unknown ID behavior:
* Empty result behavior:

## Data and seed impact

<!-- Required for seed-data, data workflow, or enrichment changes. Delete if not relevant. -->

* Seed files affected:
* Schema/shape changes:
* Validation impact:
* Media review boundary:
* Draft/reviewed behavior:

## Implementation plan

Each step should reference requirement IDs.

1. * Satisfies:
   * Files likely affected:

2. * Satisfies:
   * Files likely affected:

3. * Satisfies:
   * Files likely affected:

## Validation plan

Map checks to acceptance criteria.

* AC1:

  * Check:
  * Command:
* AC2:

  * Check:
  * Command:
* AC3:

  * Check:
  * Command:

## Suggested validation commands

```sh
# Frontend
npm run check

# Backend
cd backend
uv run pytest
```

## Risks

* Risk:

## Review notes

Suggested file groups for review:

* Spec/docs:
* Backend:
* Frontend:
* Data/seed:
* Tests:

## Suggested commit grouping

* `feat(frontend): ...`
* `feat(backend): ...`
* `test(backend): ...`
* `docs: ...`

## Verification report

<!-- Fill this in after implementation. -->

### Requirement mapping

* R1: implemented in `<file path>`
* R2: implemented in `<file path>`
* R3: implemented in `<file path>`

### Acceptance criteria verification

* AC1: Pass/Fail — evidence
* AC2: Pass/Fail — evidence
* AC3: Pass/Fail — evidence

### Tests/checks run

* `<command>` — Pass/Fail

### Files changed

* `<path>`: `<reason>`

### Spec updates during implementation

* None, or:
* `<what changed and why>`
