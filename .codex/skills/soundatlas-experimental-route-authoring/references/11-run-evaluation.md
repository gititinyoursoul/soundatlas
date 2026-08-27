# Step 11 — Run Evaluation

## Purpose

Record comparable evidence about the run so later route selection and method
changes are based on observed results rather than memory.

## Required inputs

- `00-run-brief.md`
- Every executed stage output
- Human checkpoint decisions and stop reasons
- Existing comparison baseline named in the run brief, when any

## Work

Evaluate the method separately from the route's historical quality. Name what
changed the route, what merely repeated information, where Human intervention
was required, which boundaries failed, and what work remains before the result
could enter existing editorial review.

Do not claim cross-topic generality from one topic or use a single automated
quality score for Human editorial judgment.

## Output contract

Write `11-run-evaluation.md` with:

- starting condition, method, executed/skipped stages, and terminal status;
- elapsed-time evidence when available, Human decisions, retries, and stop
  points;
- Candidate and Event counts across material checkpoints;
- Source coverage, Evidence Gaps, representation corrections, and claim changes;
- narrative, geographic, experience, and presentation findings;
- work required to reach current editorial-review and publication readiness;
- Human assessment of the result when provided;
- reusable, topic-dependent, merge, parallel, reject, and unresolved method
  findings; and
- recommendation for the next run or baseline revision.

## Stop condition

Set the run to `completed` only when its authorized terminal work and evaluation
are complete. Otherwise record `checkpointed` or `stopped` with the exact next
decision or blocking condition.
