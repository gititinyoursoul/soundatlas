# Agent Outcome Signals Baseline

Issue: [#188](https://github.com/gititinyoursoul/soundatlas/issues/188)
Cohort: 30 top-level SoundAtlas Codex sessions
Period: 2026-08-07 14:29 UTC through 2026-08-29 10:07 UTC
Follow-up evidence cutoff: 2026-09-01 00:00 UTC
Dataset: [outcome-signals-baseline.csv](outcome-signals-baseline.csv)
Context companion: [context-quality-baseline.md](context-quality-baseline.md)
Consumption companion: [consumption-baseline.md](consumption-baseline.md)

## Executive summary

The historical record supports session-level completion and validation signals
more consistently than it supports later-outcome attribution. A requested
session result is observable as completed in 28 of 30 runs (93.3%); the other
two are unknown because one trace has no agent activity and one long session
ends with a blocked task after completing several earlier work packages. This
does not mean 28 runs produced objectively successful or final product
outcomes. Completion here means the requested session-level result was
delivered, including a completed analysis, plan, diagnostic, or local
implementation.

An explicit validation mechanism is reconstructable in 28 runs. Twenty-seven
have passing evidence relevant to their delivered endpoint; one multi-task run
has both passing packages and a final failed regeneration, so its session-level
pass signal is unknown. The two runs without an available mechanism have
`validation_passed=unknown`, not false. Intermediate failures that were fixed
before delivery do not become endpoint failures.

Material in-run revision is observable in 16 runs (53.3%). Fifteen of those
also contain explicit Human correction. This includes changed integration
mechanisms, replacement plans, rebuilt artifacts, and discarded implementations;
it excludes ordinary edit-test-fix work. A completed result and a material
revision coexist in 15 runs, demonstrating why revision is not a failure or
quality score by itself.

Required post-run follow-up is linked conservatively in 11 runs (36.7%). Four
later implementations were materially replaced and one was explicitly
reverted. The other linked follow-ups include repairs, completion-state work,
or further implementation of an unresolved concern without wholesale
replacement. Seventeen runs have no qualifying linked event observed through
the cutoff, and two are unknown.

The post-run results are time-bounded. The newest run has fewer than three days
of later history while the oldest has more than three weeks. A false follow-up
signal means "not observed through the cutoff after reviewing available
links," not "will never occur."

## Cohort and evidence

This audit uses the exact 30 stable session IDs in the Issues #186 and #187
datasets. The IDs, start timestamps, and task labels match both companion CSVs
exactly. No run was added or removed because its outcome evidence was sparse.

Evidence came from local Codex JSONL traces, linked GitHub Issues and comments,
Git history, recorded validation results, and repository artifacts. Follow-up
history was reviewed only through 2026-09-01 00:00 UTC. The audit conversations
for Issues #186 through #188 are outside the cohort.

The committed CSV is sanitized. It contains short factual labels and derived
tri-state signals, not prompts, transcript excerpts, reasoning, tool payloads,
credentials, tokens, or user-specific local paths.

Each row has one evidence status:

- `observed`: the main classifications are directly supported by explicit
  trace, Issue, Git, validation, or Human records;
- `derived`: the classification follows consistently from ordered observed
  actions, but the trace does not state it as one fact;
- `approximate`: the session contains several tasks or Issues and one
  session-level result is necessarily coarse; or
- `unknown`: the historical record cannot establish a result.

The dataset contains 23 `observed`, one `derived`, five `approximate`, and one
`unknown` row.

## Evidence model and dataset structure

The CSV separates three evidence levels:

1. **Observed facts** appear in the five `*_fact` columns. These are concise
   reconstructions of delivered results, validation, revision, explicit Human
   intervention, and linked later history.
2. **Derived signals** appear in `artifact_produced` and the eleven requested
   signal columns. Each uses only `true`, `false`, or `unknown` under the rules
   below.
3. **Interpretation** is not stored at run level. Possible causes and quality
   judgments are not baseline facts.

The join fields are `run_id`, `started_at_utc`, and `task_label`.
`follow_up_observed_through_utc` makes the later-history boundary explicit.
The fact fields explain the evidence without reproducing raw trace content.

## Classification criteria

### Completion and artifact production

`artifact_produced=true` requires an observable implementation, commit,
document, dataset, Issue record, durable analysis, or other requested artifact.
It is false when the trace directly shows that nothing was produced. It is
unknown when activity exists but the output cannot be reconstructed.

`completed=true` requires the materially requested session scope to reach its
stated result. A completed diagnostic, plan, or bounded analysis counts even
when implementation is intentionally later work. An explicit stop with a
required result still outstanding is false. A missing trace or multi-task
session whose results cannot be collapsed reliably is unknown.

Completion is therefore narrower than overall success. It does not claim that
the implementation was later retained, that every broader product intention
was achieved, or that no follow-up was needed.

### Validation

`validation_available=true` requires an applicable, explicit acceptance
mechanism that can be reconstructed, such as tests, lint/type checks, document
checks, artifact validation, commit or remote reachability, an Issue-state
readback, or a structured review comparison. It is false when no applicable
mechanism is present in the record and unknown when applicability itself cannot
be reconstructed.

`validation_passed=true` requires passing evidence relevant to the delivered
endpoint. It is false only when an applicable required check was explicitly
failing at that endpoint. It is unknown when validation is unavailable,
inapplicable, incomplete, or mixed across a multi-task session. Passing a
mechanical check does not prove historical, editorial, UX, or product quality
beyond the responsibility that check actually exercises.

### In-run revision

`material_revision=true` requires an already-started plan, target, or
implementation to be substantially discarded, rebuilt, rolled back, or
replaced. Examples in this cohort include replacing a cherry-pick with
full-history integration, rebuilding an accepted delivery helper around a new
responsibility boundary, and replacing an implemented route handoff with
evidence-audited copy.

Ordinary edits, test failures followed by a local fix, formatting, plan wording
corrections, and incremental additions do not qualify by themselves.

`approach_changed=true` requires an observable change to the implementation or
execution path after work began. A scope correction can be material revision
without a different technical approach, so the two signals are independent.

### Human intervention

`human_correction=true` requires an explicit Human correction of a requirement,
assumption, classification, scope, or produced result. `human_redirection=true`
requires the Human to request a materially different target, responsibility,
or execution approach. Ordinary questions, approvals, refinements, and choices
presented before implementation do not count.

These signals record intervention, not dissatisfaction. A Human correction can
improve an otherwise completed run, and a redirection may reflect a new
preference rather than an agent error.

### Post-run follow-up

All later signals require an explicit same-Issue, same-commit or artifact,
stated same-concern, Git revert, or equally strong link. A later change merely
touching the same directory or product area is not sufficient.

`follow_up_required=true` means later work was needed to finish or correct the
original intent. `same_concern_revisited=true` means later evidence explicitly
returns to the same concern. Normal downstream execution of a completed plan,
integration of an already reviewed commit, or ordinary push/closure work does
not automatically qualify.

`implementation_replaced_later=true` requires a later linked artifact or
implementation to materially supersede the earlier result. `later_reverted=true`
requires explicit rollback or removal of the earlier implementation. False
means no qualifying linked event was observed through the cutoff; unknown is
used when session aggregation, trace coverage, or linkage is insufficient.

## Aggregate baseline

| Signal | True | False | Unknown |
| --- | ---: | ---: | ---: |
| Artifact produced | 29 (96.7%) | 1 (3.3%) | 0 |
| Completed | 28 (93.3%) | 0 | 2 (6.7%) |
| Validation available | 28 (93.3%) | 2 (6.7%) | 0 |
| Validation passed | 27 (90.0%) | 0 | 3 (10.0%) |
| Material revision | 16 (53.3%) | 13 (43.3%) | 1 (3.3%) |
| Approach changed | 15 (50.0%) | 14 (46.7%) | 1 (3.3%) |
| Human correction | 18 (60.0%) | 11 (36.7%) | 1 (3.3%) |
| Human redirection | 15 (50.0%) | 14 (46.7%) | 1 (3.3%) |
| Follow-up required | 11 (36.7%) | 17 (56.7%) | 2 (6.7%) |
| Same concern revisited | 11 (36.7%) | 17 (56.7%) | 2 (6.7%) |
| Implementation replaced later | 4 (13.3%) | 23 (76.7%) | 3 (10.0%) |
| Later reverted | 1 (3.3%) | 27 (90.0%) | 2 (6.7%) |

Among the 28 runs with observable completion, all 28 reached their requested
session result. This is a reconstruction property of the confirmed substantive
cohort, not a comparative success rate. The two unknown runs remain in every
cohort denominator.

Among the 28 runs with an explicit validation mechanism, 27 have endpoint pass
evidence and one is unknown because completed work packages and a final blocked
regeneration share the session. No run has `validation_passed=false`: explicit
intermediate failures were either corrected before the endpoint or occurred in
the mixed session whose aggregate is unknown.

## Observable patterns

### Material revision often accompanied explicit Human intervention

Fifteen of the 16 material-revision runs also contain explicit Human
correction, and 13 contain Human redirection. The remaining material revision
was the Human-authorized withdrawal of an unpublished feature rather than a
correction of the implementation record.

This overlap shows that material revision is reconstructable most reliably
when the Human states what must change. It does not establish that the
intervention was avoidable or caused by context, model choice, or resource use.

### Completion and revision commonly coexist

Fifteen runs have both `completed=true` and `material_revision=true`. Ten
material-revision runs have no qualifying later follow-up through the cutoff.
In-run rebuilding can therefore end in a completed, retained result; counting
revision alone as failure would misclassify these runs.

### Required follow-up was broader than replacement

Eleven runs required linked later work. Four had their implementation replaced,
one of those was explicitly reverted, and six have required follow-up without
later replacement. Examples include repairing a lockfile regression, revisiting
stale completion-state handling, and adding Pages-specific validation after a
hosted failure exposed a remaining delivery gap.

Replacement is consequently a narrower signal than follow-up. The single
reversion is the approved withdrawal of the unpublished source-first Research
feature; it is not evidence about published product stability.

### Long multi-task sessions reduce attribution precision

Five rows are `approximate`, including the sessions with the broadest mixes of
frontend, workflow, editorial, and pipeline work. These sessions can support
facts such as commits, tests, explicit corrections, and later Issue links, but
they cannot always support one session-level claim that every produced result
was later retained or replaced. This matches the phase-attribution limitation
in the consumption baseline.

## Relationship to context and consumption baselines

All three datasets contain the same 30 `run_id` values and can be joined
one-to-one. The outcome dataset does not copy or reinterpret context or token
fields. Its signal criteria were applied independently, while concise evidence
from the context audit was used only as a lead for reviewing the underlying
record.

The joined data can support later descriptive questions about context gaps,
discovery, token/tool consumption, revision, and follow-up. This report does
not calculate causal effects or rank runs. The cohort is small, selected,
session-level, and highly heterogeneous; correlations would be exploratory and
confounded by task count, task type, duration, and observation window.

## Observability gaps

### Sessions are not stable task units

Several sessions contain many Issues and delivery phases. A final session-level
signal can become unknown even when individual task outcomes are clear.

Future records should assign a stable `task_id` below `run_id` and link every
Plan, Proceed record, worktree, commit range, validation result, implementation
report, push, and completion record to that task.

### Completion is reconstructed from prose and external artifacts

The traces do not emit a first-class requested outcome, completion disposition,
or reason for stopping. A final answer can say work is complete, but it cannot
by itself prove that the original task and its later revisions were satisfied.

Future instrumentation should record `requested_outcome`, `completion_status`,
`completion_evidence`, and `stop_reason`, with links rather than copied
transcript text.

### Validation lacks a normalized task result

Tool calls show tests and checks, but historical traces do not consistently
link them to a task, artifact, commit, or accepted criterion. One session can
contain both expected test failures and a later passing endpoint.

Future instrumentation should record the validation name, applicability,
result, artifact or commit tested, timestamp, and whether it is required for
completion. Raw logs need not be retained in the baseline record.

### Revision has no explicit replacement marker

Material revision is reconstructed from action order, commit history, and
explicit correction. Ordinary iteration and discarded implementation are not
first-class trace events.

Future tasks should record `plan_superseded_by`, `artifact_replaces`, and a
bounded revision reason such as `scope`, `requirement`, `validation`,
`implementation`, or `human_redirection`. This should identify replacement,
not store reasoning.

### Human correction and redirection are prose-only

Explicit Human statements make these signals observable, but there is no
normalized reference to the affected requirement, plan, or artifact.

Future Issue/task records should allow a short Human-owned correction or
redirection marker linked to the affected task and replacement Plan. Ordinary
follow-up messages should remain unclassified by default.

### Post-run linkage and observation windows are weak

Issue numbers and commits provide strong links in some cases. Other work shares
a route or workflow concern without an explicit relationship. Recent runs also
have much shorter opportunity for later events.

Future instrumentation should record `follow_up_to_task_id`,
`corrects_commit`, `replaces_artifact`, or `reverts_commit` at the time the
later work is created. Outcome snapshots should retain both an evidence cutoff
and the actual observation duration so later analyses can refresh or censor
the follow-up comparison consistently.

## Interpretation boundary

This baseline records observable signals, not overall quality. A completed run
may deliver only an analysis; a revised run may end with the retained solution;
a Human redirection may reflect a new preference; and later replacement may be
healthy product learning. Conversely, passing tests cover only their stated
responsibilities.

Possible explanations such as avoidable rework, inadequate context, premature
implementation, design deficiency, or inefficient reasoning remain hypotheses.
They require a task-level comparison design and stronger linkage than this
retrospective session cohort provides.
