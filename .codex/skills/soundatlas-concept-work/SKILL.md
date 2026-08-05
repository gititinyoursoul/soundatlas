---
name: soundatlas-concept-work
description: Synthesize confirmed SoundAtlas product, workflow, editorial, data, or architectural decisions into a concise five-part concept and record it in the originating GitHub Issue or an approved docs source. Use when the user explicitly requests concept work or a Grill-Me check finds that implementation planning would otherwise invent material target behavior, runtime responsibilities, boundaries, or ownership; skip clear, local, low-risk work.
---

# SoundAtlas Concept Work

Turn confirmed decisions into a coherent target that implementation planning can
use without inventing product behavior.

## Required context

Read before producing a concept:

- `AGENTS.md`;
- the originating GitHub Issue and its confirmed Grill-Me findings or
  decisions, using a standalone `## Grill-Me Review` when required or an inline
  action comment when the result is clean;
- relevant current-state, product, architecture, workflow, data, or editorial
  sources; and
- an existing concept when the request revises one.

Use the smallest relevant context. Inspect discoverable facts before asking the
human to answer them.

## Workflow

1. Confirm that concept work is needed.
   Use this skill when requested explicitly or when planning would otherwise
   have to invent material target behavior, runtime responsibilities,
   boundaries, or ownership. Skip it for clear, local, low-risk work.
2. Check decision readiness.
   Use only human-confirmed material decisions. If a material decision remains
   unclear, return to `prompts/grill-me.md` and do not silently resolve it.
3. Separate current behavior from the accepted target.
   Do not describe planned behavior as already implemented.
4. Write the five-part concept in the required order.
5. Choose one authoritative location and record the result.
6. Hand the accepted concept to implementation planning by reference, without
   turning it into tasks in this skill.

## Five-part concept

Use this exact structure and keep each section as short as the concept allows:

```md
## Concept

### Target behavior

### Scope and non-goals

### Runtime responsibilities

### Boundaries and ownership

### Unresolved decisions
```

Apply these meanings:

- **Target behavior:** State the outcome the system should provide.
- **Scope and non-goals:** State what is included and deliberately excluded.
- **Runtime responsibilities:** State what the running system must do, including
  material triggers, outcomes, state changes, and failure behavior. Describe
  behavior without choosing components, files, schemas, or services unless an
  accepted constraint requires that choice.
- **Boundaries and ownership:** State who or what is responsible, which human
  decisions remain human, which source is authoritative, and where each
  responsibility stops. Do not repeat runtime behavior.
- **Unresolved decisions:** List remaining decisions and say which ones block
  planning. Write `None` only after confirming that no material decision remains.

Add another section only when omitting it would leave a material ambiguity. Do
not require tables, diagrams, or architecture notation.

## Persistence

Default to a concise `## Concept` comment on the originating Issue.

Recommend one authoritative document under `docs/` when the concept:

- spans several Issues or system areas;
- defines durable product behavior, responsibilities, or terminology;
- will guide future work beyond the originating Issue; or
- changes a product or architecture source of truth.

Obtain human confirmation before creating or changing that document. Keep the
Issue comment to a short decision record and link; do not copy the full concept
into both locations. Clearly label a document as an accepted target or current
state.

## Planning boundary

A concept is ready for planning when its material decisions are confirmed and
its unresolved section contains no decision that would force planning to invent
target behavior.

Use `soundatlas-issue-planning` for implementation slices, sequencing,
validation, and Plan Updates. Require the plan to reference the accepted concept
instead of repeating it. Return to concept work if planning exposes a missing or
contradictory target decision.

Do not create implementation tasks, code, application changes, a mandatory
concept stage, a concept registry, or a separate approval status from this
skill.

## Output

Report:

1. where the concept was recorded;
2. the five-part concept or a link to its authoritative document;
3. any decision that still blocks planning; and
4. the next workflow step.
