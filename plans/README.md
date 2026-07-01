# Local Implementation Plans

SoundAtlas stores implementation plan records locally for later revision.

These files are not committed by default. Only the guidance and template in
this folder are tracked.

## Location

Create local plan records under:

```text
plans/records/
```

The directory is gitignored.

## Naming

Use this filename shape:

```text
plans/records/P-###-<short-slug>.md
```

Examples:

- `plans/records/P-001-map-selection-sync.md`
- `plans/records/P-014-enrichment-query-input.md`

## ID Allocation

Plan IDs are repo-local sequential IDs:

```text
P-001
P-002
P-003
```

Allocate the next ID by inspecting existing files in `plans/records/` and
incrementing the highest number.

## When To Create A Record

Create a local plan record when:

- non-trivial work has been planned and approved for implementation
- the work changes product behavior, workflow behavior, data behavior, or
  cross-cutting implementation details
- later revision or verification would benefit from a durable local record

A local plan record is usually not needed for:

- trivial copy edits
- typo fixes
- formatting-only changes
- tiny mechanical edits with no behavior change

## Lifecycle

Use these statuses:

- `Draft`
- `Approved`
- `Implemented`
- `Superseded`

Typical flow:

```text
Draft -> Approved -> Implemented
```

## Commit Reference

When commits are made for implemented plan work, keep the Conventional Commit
subject clean and reference the plan ID in the commit body:

```text
feat(enrichment): improve query planner

Plan: P-014
```

This is a documented convention, not a repository-enforced hook in the current
workflow.
