# Step 00 — Run Brief

## Purpose

Create the minimum authority and resume context for one research run before any
research stage executes.

## Required inputs

- Approved Issue and accepted Concept
- Human-confirmed experiment scope
- Proposed experiment and version IDs

## Work

Confirm that IDs are lowercase, stable, and URL-safe. Record the starting
condition as `open-topic`, `fixed-topic`, or `fixed-direction`. State what this
run tests, what may vary, and what comparison evidence it should preserve.

Use `baseline-1`. Do not invent a route ID for canonical publication unless the
Human has already selected one; an experiment ID is not a public route ID.

## Output contract

Write `00-run-brief.md` with:

- experiment ID and version ID;
- method: `baseline-1`;
- status: `in-progress`, `checkpointed`, `completed`, or `stopped`;
- declared starting condition and first executable stage;
- topic, place, period, research question, scope, and non-goals;
- intended route-length and content-depth choices, when any;
- method changes or hypotheses being tested;
- named inherited inputs or earlier versions used as evidence;
- skipped conditional stages and a reason for each;
- current stage, last completed stage, and required Human checkpoint;
- stop reason when status is `stopped`; and
- approved Issue and Plan links.

## Stop condition

Stop before research if the Human has not confirmed the material route scope or
if the declared entry point cannot be justified from named inputs.
