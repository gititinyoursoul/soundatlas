# Agent Context Quality Baseline

Issue: [#186](https://github.com/gititinyoursoul/soundatlas/issues/186)
Cohort: 30 top-level SoundAtlas Codex sessions
Period: 2026-08-07 14:29 UTC through 2026-08-29 10:07 UTC
Dataset: [context-quality-baseline.csv](context-quality-baseline.csv)

## Executive summary

Repository discovery was normal in this cohort, not exceptional. Twenty-nine
of 30 sessions expanded their task-relevant context; the remaining trace ended
without an agent response, so expansion is unknown. Git and GitHub state were
inspected in all 29 active sessions, and the Issue-planning skill was loaded in
26. This reflects the repository's Issue-led workflow and frequently dirty or
divergent local state.

The initial task context was sufficient to begin the correct course without a
material preliminary reconstruction in 11 runs (36.7%). Eighteen runs (60.0%)
first had to reconstruct an Issue, branch, prior-session, design, or workflow
state. One run (3.3%) is unknown. Required discovery alone is not classified as
a failure.

Ten runs (33.3%) contain evidence of a context-delivery, discoverability, or
use problem: missing context, poor discoverability, or context misuse. Eight
different runs (26.7%) instead expose missing knowledge or a deficient concept.
Those categories are kept separate because loading more existing context would
not have supplied a decision that did not yet exist. Some runs have more than
one supported classification.

Rework was observed in 20 runs. Context quality contributed to rework in eight
runs (26.7% of the cohort and 40.0% of runs with observed rework). The other 12
rework cases followed new Human decisions, concept development, ordinary
validation failures, or deliberate rollback and correction. The evidence does
not support treating all rework as a context failure.

## Cohort and evidence

A run is one substantive, top-level Codex session rooted in the SoundAtlas
workspace. The cohort is ordered by session start time and excludes:

- the Issue #186 audit conversations;
- subagent-only traces; and
- two brief Codex installation or update sessions that did not exercise the
  SoundAtlas repository workflow.

The stable Codex session ID is the join key for the follow-up consumption and
outcome audits in Issues #187 and #188. A session may contain several tasks and
turns; this is a material limitation discussed below.

Evidence came from local Codex JSONL traces, linked GitHub Issue records, Git
history, validation output, and repository artifacts. The committed dataset is
sanitized: it contains concise task and evidence labels, not raw prompts,
transcript excerpts, tool outputs, tokens, secrets, or user-specific local
paths.

Each row has one evidence status:

- `observed`: directly supported by a trace, artifact, validation result, or
  explicit Human correction;
- `derived`: consistently inferred from the order of observed actions and
  corrections;
- `approximate`: supported only at a coarse session level because several
  tasks or causes overlap; or
- `unknown`: the historical trace cannot support a conclusion.

The dataset contains 18 `observed`, nine `derived`, two `approximate`, and one
`unknown` row.

## Classification method

`initial_context_sufficient` answers whether the initial task and automatically
available repository guidance were enough to begin the correct course without
first reconstructing a material prior state. It does not require the agent to
already know the code or current Issue contents.

`meaningful_context_expansion` records task-relevant information loaded after
the initial request. Normal Issue, code, document, and Git inspection counts as
expansion but not automatically as a failure.

Gap classifications follow the Issue definitions:

- `missing context`: relevant information existed but was not initially
  available;
- `poor discoverability`: relevant information existed but was difficult to
  locate or connect;
- `missing knowledge`: the required decision or documentation did not exist;
- `context misuse`: relevant context was available but ignored or interpreted
  incorrectly;
- `concept deficiency`: the available context represented an underlying
  concept that was not sufficiently developed;
- `none observed`: reviewed evidence supports no gap; and
- `unknown`: the trace is insufficient.

Multiple classifications appear only when the trace supports separate causes.
`context_contributed_to_rework` is conservative: it is `yes` only when a later
correction can be linked to missing, difficult-to-find, or misused context.

## Aggregate baseline

| Signal | Result |
| --- | ---: |
| Audited runs | 30 |
| Initial context sufficient | 11/30 (36.7%) |
| Initial context insufficient | 18/30 (60.0%) |
| Initial-context sufficiency unknown | 1/30 (3.3%) |
| Meaningful context expansion observed | 29/30 (96.7%) |
| Discovery required before useful work | 18/30 (60.0%) |
| Context delivery, discoverability, or misuse problem | 10/30 (33.3%) |
| Missing knowledge or concept deficiency | 8/30 (26.7%) |
| Rework observed | 20/30 (66.7%) |
| Context contributed to rework | 8/30 (26.7%) |
| Rework observed without a supported context contribution | 12/30 (40.0%) |
| Rework status unknown | 1/30 (3.3%) |

Classification counts are not mutually exclusive:

| Classification | Runs | Interpretation |
| --- | ---: | --- |
| None observed | 11 | Discovery occurred without a supported context failure |
| Missing context | 3 | Prior-session, design, or commit-state information had to be recovered |
| Poor discoverability | 2 | Existing stage files or active worktree state were difficult to connect |
| Missing knowledge | 5 | A required workflow or product decision did not yet exist |
| Context misuse | 6 | Available scope, design, or target-outcome evidence was applied incorrectly |
| Concept deficiency | 5 | The underlying workflow or domain concept needed development |
| Unknown | 1 | No agent response or tool evidence was recorded |

## Repeated context discovery

The following counts are mechanically reconstructed from tool calls. They show
that a source was accessed, not that every loaded statement influenced the
result.

| Context source or operation | Runs | Observed role |
| --- | ---: | --- |
| Git status, history, diff, or revision checks | 29 | Established the actual work package, branch, and pending range |
| GitHub Issue reads | 29 | Established scope, decisions, acceptance criteria, and lifecycle state |
| Issue-planning skill | 26 | Selected and formatted Issue workflow artifacts |
| `AGENTS.md` | 25 | Established repository, Git, validation, and scope constraints |
| GitHub Issue workflow | 25 | Established authorization, commit, push, and closure gates |
| Workflow registry | 25 | Selected authority and skill boundaries |
| Grill-Me skill | 25 | Checked ambiguous or consequential decisions |
| Readiness validator | 22 | Verified non-trivial implementation authorization |
| Documentation-reference validator | 22 | Checked documentation consistency |
| Editorial workflow | 16 | Established review, route, and publication responsibilities |
| Desktop design authorities | 10 | Established current frontend and mockup constraints |

Three patterns follow from these observations:

1. **Repository state had high decision value.** Many sessions operated beside
   unrelated user changes, unpushed commits, divergent branches, or work in
   another shell. Git and GitHub reconstruction repeatedly prevented unrelated
   files or Issues from entering a work package.
2. **The workflow bundle was repeatedly reloaded.** `AGENTS.md`, the Issue
   workflow, registry, Issue-planning skill, and Grill-Me skill each appeared in
   at least 25 sessions. These sources regularly affected authorization and
   delivery decisions, but locating and reading the same bundle consumed a
   large share of discovery activity.
3. **Domain context remained task-dependent.** Editorial and frontend design
   authorities appeared less frequently and primarily in tasks where their
   decisions were material. This is evidence for targeted domain discovery,
   not for injecting every domain authority into every run.

## Context failures versus knowledge and concept failures

The ten context-related runs fall into three practical groups:

- Prior conversation or commit intent was absent, requiring reconstruction of
  why work was uncommitted or what another shell had decided.
- Existing artifacts or the active local range were difficult to locate, so an
  otherwise-correct change appeared missing or ineffective.
- Available authorities were applied incorrectly, including an over-broad
  publication commit, a mockup that contradicted the implemented hierarchy,
  and a route experiment whose stopping condition did not match the accepted
  fast-path outcome.

The eight missing-knowledge or concept-deficiency runs are different. They
introduced or clarified decisions such as flexible reviewed story sections,
Project lifecycle states, reader-first narrative planning, Research lifecycle
boundaries, and review-versus-publication semantics. More initial repository
text would not have supplied these decisions because they were being created or
corrected in the run.

This distinction also explains the rework results. Twenty sessions contain
observable correction, rollback, regeneration, or material revision, but only
eight can be linked conservatively to context quality. The remainder arose
from new Human preferences, deliberately changed scope, validation evidence,
or concept and workflow development.

## Context with high and low decision value

Git state, Issue records, accepted plans, and the domain authority applicable
to the task had demonstrable decision value. They changed file boundaries,
prevented premature pushes, exposed stale worktrees, preserved reviewed copy,
or established which Human decisions remained open.

The historical traces do not support a reliable list of documents with low
decision value. A file read proves availability, not attention or influence,
and the traces do not record which loaded passages were unused. High load
frequency must therefore not be interpreted as waste. Future instrumentation
should record why an artifact was requested and whether it changed a decision
before any source is removed from initial context.

## Improvement candidates

These are candidates for later context-management work, not changes authorized
by Issue #186:

1. Give a run a compact task handoff containing the active Issue, latest Plan
   and Proceed links, branch or worktree, pending commit range, and known
   unrelated changes.
2. Provide one compact workflow entrypoint that identifies the applicable
   authority and skill bundle without replacing the underlying sources.
3. Preserve targeted domain loading: include editorial or design authorities
   when the task touches those decisions rather than placing every domain
   document into every run.
4. Introduce a stable task identifier below the session identifier. Several
   cohort sessions contain many unrelated tasks, making one session a poor unit
   for causal comparison.
5. Record context acquisitions with a reason such as `scope`, `current state`,
   `authority`, `validation`, or `follow-up reconstruction`.
6. Record an explicit marker when newly discovered context changes the plan,
   invalidates work, or causes material rework.
7. Link session and task identifiers to Issues, commits, validation runs, and
   explicit Human corrections so later audits do not infer these joins from
   prose.

These candidates do not assume that the bounded-context approach in Issue #185
is correct. A later comparison should test whether it preserves decision value
while reducing avoidable reconstruction.

## Reusable metrics

Future cohorts should retain these definitions:

- **Initial-context sufficiency rate:** runs that can begin the correct course
  without material prior-state reconstruction divided by audited runs.
- **Meaningful context-expansion rate:** runs that acquire task-relevant context
  beyond the initial handoff divided by audited runs.
- **Pre-work discovery rate:** runs requiring material discovery before useful
  work can begin divided by audited runs.
- **Context-problem rate:** runs with missing context, poor discoverability, or
  context misuse divided by audited runs.
- **Knowledge-or-concept-gap rate:** runs with missing knowledge or concept
  deficiency divided by audited runs.
- **Context-related rework rate:** runs where context quality contributed to
  observable rework divided by audited runs.
- **Unknown rate:** runs whose historical evidence cannot support the requested
  classification divided by audited runs.
- **Repeated-source frequency:** runs accessing a named context source divided
  by active runs, reported with the source's observed decision role.

Rates should always include explicit numerators, denominators, and unknowns.
They describe observed associations and must not be interpreted as causal
quality scores.

## Limitations

- A session is not a stable unit of work. Several sessions span many Issues,
  design discussions, implementations, pushes, and follow-up corrections.
- Session traces record loaded content and actions but do not record attention,
  comprehension, or the exact context that changed a decision.
- Persistent conversation context cannot always be separated from information
  rediscovered in the same session.
- Later Issue and Git evidence can establish outcomes but not always the cause
  of an earlier choice.
- Rework is easier to observe than to attribute. `context_contributed_to_rework`
  is therefore conservative and sometimes session-level.
- The cohort is temporally clustered: 12 runs began on August 27–29, 16 on
  August 9–12, one on August 8, and one on August 7. There were no included
  sessions from August 13–26.
- The single no-response trace is retained with `unknown` values rather than
  silently replaced or interpreted as a context failure.

## Acceptance-criteria coverage

- Exactly 30 recent substantive sessions are represented by unique stable IDs.
- Every run has a minimal task, context, outcome, gap, rework, and evidence
  classification, including explicit `unknown` values where necessary.
- Repeated context discovery is quantified across the cohort.
- Context delivery and misuse are separated from missing knowledge and concept
  deficiency.
- The report records unobservable causal and attention data as unavailable
  rather than guessing.
- The aggregate baseline and reusable metric definitions can be applied to a
  later bounded-context cohort.
- Future observability recommendations identify the signals needed to reduce
  retrospective inference.
