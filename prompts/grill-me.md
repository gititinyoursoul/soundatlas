# Grill Me

Use this prompt as the default SoundAtlas critique mechanism for non-trivial
feature, route, seed, enrichment, documentation, UX, editorial, concept,
planning, implementation, or workflow work.

Grill Me may be used at any stage of the workflow. The active stage determines
which artifact is being challenged.

This prompt is the human-facing critique entrypoint. It does not replace the
GitHub Issue workflow, `soundatlas-concept-work`,
`soundatlas-implementation-review`, `soundatlas-issue-planning`, or
implementation.

Core rule:

> Critique first. Do not edit files, implement changes, publish content, modify
> normative artifacts, or mark work as approved from this prompt alone.

Use Grill Me whenever material ambiguity, risk, conflicting assumptions, scope
growth, or new evidence appears. Clearly trivial, local, low-risk work may use
the direct path.

## Context To Provide

Provide the relevant artifact and the smallest useful context:

* Idea, Issue, concept, plan, implementation, UX proposal, editorial artifact,
  or workflow change.
* Target area:

  * `frontend`
  * `backend`
  * `data/seed`
  * `data/enrichment`
  * `docs`
  * `content/editorial`
  * workflow
  * cross-cutting
* Related GitHub Issue, route, event, place, media item, prompt, skill,
  specification, or workflow document.
* Desired outcome, if known.
* Constraints, non-goals, and anything that must remain human-reviewed.
* For implementation review: relevant diff, tests, validation evidence, and
  current-state documentation.

## Task

Inspect the relevant repository context, then challenge the current request or
artifact before the workflow proceeds.

Focus on:

* missing product, architectural, or editorial decisions
* unclear goals, scope, or non-goals
* hidden assumptions and contradictions
* weak or untestable acceptance criteria
* missing runtime responsibilities
* overcomplicated implementation paths
* premature automation
* speculative future scope
* concept, plan, or implementation drift
* candidate, draft, accepted, reviewed, and published boundary confusion
* source, media, rights, and historical-claim risks
* unapproved or unrelated changes
* missing validation evidence
* stale documentation
* whether GitHub Issue planning or follow-up work is needed

For discoverable facts, inspect the repository before asking questions. Ask only
when the answer materially affects product intent, target behavior, data shape,
source quality, implementation risk, validation, or publication boundaries.

## Lightweight Check

Apply a lightweight Grill-Me check automatically:

* at Intake
* before accepting a consequential concept
* before approving a broad or risky implementation plan
* when implementation reveals drift, conflicting assumptions, or new
  constraints
* before accepting completed implementation

If there is no material finding, continue without starting an interactive
session or asking for approval. Mention the clean check only when it helps the
handoff. If a material finding needs human confirmation, enter the interactive
one-finding flow below.

For a clean check, do not create a standalone `## Grill-Me Review` comment. If
the check enables a next action, add a concise inline note such as:

```md
- Grill-Me check: clean — no material findings; proceeding.
```

If no durable action follows, the clean check may be omitted. Use a standalone
`## Grill-Me Review` for material findings, confirmed decisions, blockers, or
an explicitly requested standalone session.

Before accepting completed non-trivial Issue work, use
`soundatlas-implementation-review` for the routine target, implementation, and
evidence comparison. A clean result continues to the combined Implementation
Report. If the skill returns a material decision, use the interactive
one-finding flow here. Do not create a separate routine review comment.

If the check finds that planning would otherwise invent material target
behavior, runtime responsibilities, boundaries, or ownership, use Grill Me to
resolve the material decisions, then use `soundatlas-concept-work` to synthesize
and record the confirmed concept.

## Relationship To The Workflow

Grill Me challenges the active artifact but does not own it.

* The Issue defines why the work is needed.
* `soundatlas-concept-work` records what the system should do.
* Implementation planning defines how the target will be built.
* Implementation contains the actual changes.
* Current-state documentation describes how the system works now.
* `soundatlas-implementation-review` determines whether the implementation
  matches the accepted target with proportionate evidence.

Grill Me findings may inform these artifacts, but must not silently modify them.
Material decisions remain open until the user confirms them.

Grill Me owns critique, not concept synthesis. After the human confirms the
material decisions, use `soundatlas-concept-work` to produce or update the
five-part concept when concept work is needed.

Use Grill Me:

* during problem discovery
* before accepting a consequential concept
* before approving a broad or risky implementation plan
* when implementation reveals unexpected constraints
* when concept or scope drift is suspected
* when implementation review returns a material human decision
* whenever the user requests it

## Review Modes

Use the smallest mode that fits the active artifact:

* `idea grill`: test whether an idea is worth pursuing.
* `issue grill`: stress-test an Intake Issue or problem statement.
* `concept grill`: challenge scope, non-goals, target behavior, boundaries, and
  runtime responsibilities.
* `plan grill`: challenge coverage, sequencing, dependencies, validation, and
  hidden scope.
* `editorial grill`: review route briefs, dossiers, candidate events, sources,
  media plans, seed-promotion readiness, and publication boundaries.
* `ux grill`: review UX findings, flows, accessibility, and proposed UX slices.
* `implementation readiness grill`: check whether approved work is ready to
  implement.
* `implementation grill`: challenge work in progress, complexity, shortcuts,
  newly discovered constraints, and concept or plan drift.
* `implementation review grill`: challenge a material decision or ambiguity
  returned by `soundatlas-implementation-review`.

## Mode-Specific Focus

### Concept Grill

Check:

* whether the target behavior is explicit
* whether scope and non-goals constrain the design
* whether runtime responsibilities are complete
* whether ownership and boundaries are clear
* whether the concept conflicts with existing normative artifacts
* whether the concept remains lean and MVP-oriented
* whether implementation work can be derived without inventing decisions

### Plan Grill

Check:

* whether the plan covers the accepted concept or Issue
* whether runtime responsibilities map to implementation tasks
* whether sequencing and dependencies are sound
* whether tests and validation prove the intended behavior
* whether the plan adds unapproved scope
* whether implementation tasks are small and reviewable

### Implementation Grill

Check:

* whether implementation still follows the accepted concept and plan
* whether technical constraints created an unrecorded design change
* whether complexity or workarounds are hiding a conceptual problem
* whether unrelated files or responsibilities were added
* whether work should continue or return to concept or planning

### Implementation Review Grill

Use `soundatlas-implementation-review` for the repeatable comparison, evidence
assessment, finding classification, and routing. Use this Grill mode only when
the review exposes a material decision, conflicting intent, or ambiguity that
requires human confirmation. Challenge that finding without repeating the
entire implementation review.

After confirmation, return the decision to the workflow destination named by
the review skill. Grill Me does not fix the implementation, rewrite the plan or
concept, finalize the Implementation Report, commit, or close the Issue.

## Project Constraints

* Keep changes small, reviewable, and MVP-oriented.
* Treat SoundAtlas as an editorial-cultural product, not only a data pipeline.
* Current product scope is New York 1965–1985 with curated routes, events,
  places, connections, and external media links.
* Preserve seed file shapes documented in `docs/data/seed-data-validation.md`.
* Keep generated media links as `review_status: "draft"` until manually
  reviewed.
* Do not store audio or video files in the repository.
* Do not automate final editorial judgment, source approval, media approval, or
  publication approval.
* Do not commit secrets, API keys, local paths, generated media files, audio, or
  video.
* Do not commit changes unless explicitly requested.
* Do not overwrite unrelated user changes.
* Do not treat speculative future behavior as an MVP requirement.
* Do not expand SoundAtlas into an admin platform unless explicitly approved.

## Output

Begin with a short overview of whether material findings are present.

For a lightweight check with no material finding, do not manufacture an
interactive finding. Continue the active workflow.

Use one-finding turns when a finding requires a material user decision. Batch
independent factual findings when they do not require separate confirmation.

For an interactive finding, use:

```md
## Current Assessment

Proceeding / Needs revision / Blocked

## Finding <n>

- Severity: Critical / Major / Minor
- What I found: <short statement>
- Decision recommendation: Proceed / Revise / Stop
- Confirmation required: Yes / No — <why>
- Why this recommendation: <short rationale>
- What to confirm next: <one concrete question or decision>

Options:

1. <meaningful option>
2. <meaningful option>

Recommendation: <recommended option and short reason>

## Recommended Next Step

- Continue with the next finding, revise the artifact, create or update a
  GitHub Issue, return to concept or planning, proceed with implementation, or
  begin implementation review.
```

Include `Options` only when the user must choose between materially different
decisions. Always include a recommendation when options are shown.

After an interactive finding, pause and wait for confirmation before continuing
to dependent findings.

Do not publish a standalone `## Grill-Me Review` while a material finding is
still awaiting confirmation. After all material findings in the session have a
decision, record one consolidated Issue comment containing the stage, each
finding with its decision, and the next step. For multiple findings, keep the
findings numbered in that single comment.

When the review is complete, give one final verdict:

* Ready
* Ready with follow-up
* Needs revision
* Blocked
* Return to concept
* Return to planning

Do not describe a material decision as closed until the user confirms it.

## GitHub Issue Recording

When a related GitHub Issue exists and GitHub write access is available, record
material findings, confirmed decisions, blockers, or explicitly requested
standalone sessions in an Issue comment under:

```md
## Grill-Me Review
```

Use this minimal completed-record shape:

```md
## Grill-Me Review

**Stage:** Intake | Plan | Implementation | Implementation Review

### Findings and decisions

1. **Finding:** <material finding>
   **Decision:** Confirmed by human — <decision>

**Next step:** <Plan Update | Concept Work | Blocked>
```

For multiple findings, add one numbered `Finding`/`Decision` pair per finding.
Do not publish a pending finding as a completed record, and do not leave a
material finding without an explicit decision. Decisions may confirm, defer,
reject, or block the finding.

For a clean lightweight check, record the result inline in the next action
comment when useful instead of creating a separate review comment. Omit it when
no durable record is needed.

Do not record unresolved assumptions as confirmed decisions. Do not add partial
findings during an active session unless explicitly requested.

## Relationship To Implementation Planning

Use `soundatlas-issue-planning` when accepted work must be converted
into or reflected in a GitHub Issue, Plan Update, Detailed Plan Update,
implementation tasks, validation steps, or Implementation Report.

When an accepted concept exists, treat its target behavior, scope and non-goals,
runtime responsibilities, boundaries and ownership, and resolved decisions as
the target for later planning and review.

If planning or implementation reveals a missing or contradictory concept
decision, return it to Concept Grill and then update the concept through
`soundatlas-concept-work` instead of silently resolving it.

Do not create local or repository-versioned implementation plan files.
