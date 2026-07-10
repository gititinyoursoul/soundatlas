# Grill Me

Use this prompt as the default SoundAtlas planning and critique entrypoint
before non-trivial feature, route, seed, enrichment, documentation, UX, or
workflow work.

This prompt replaces `prompts/plan-feature.md` as the human-facing planning
front door. It does not replace the GitHub Issue workflow or the
`soundatlas-implementation-planning` skill.

Core rule:

> Critique first. Do not edit files, implement changes, publish content, or
> mark work as approved from this prompt alone.

## Context To Provide

* Idea, feature, route, data change, UX change, workflow change, or artifact to
  review.
* Target area:
  * `frontend`
  * `backend`
  * `data/seed`
  * `data/enrichment`
  * `docs`
  * `content/editorial`
  * cross-cutting
* Related GitHub Issue, route, event, place, media item, prompt, skill, or
  workflow document.
* Desired outcome, if known.
* Constraints, non-goals, and anything that should stay human-reviewed.

## Task

Inspect the relevant repo context, then challenge the request or artifact before
it becomes implementation work.

Focus on:

* missing product or editorial decisions
* unclear scope
* weak or untestable acceptance criteria
* overcomplicated implementation paths
* premature automation
* candidate, draft, accepted, reviewed, and published boundary confusion
* source, media, rights, and historical-claim risks
* whether GitHub Issue planning is needed before implementation

For discoverable facts, inspect the repo before asking questions. Ask only when
the answer affects product intent, data shape, source quality, implementation
risk, or publication boundaries.

## Relationship To Issue Planning

Use this prompt before `soundatlas-implementation-planning` when the request is
vague, risky, editorially sensitive, cross-cutting, or likely to create a broad
plan.

After grill-me review:

* If the work is not worth doing, stop with the critique.
* If the work is worth doing but not decision-complete, list the missing
  decisions.
* If the recommended next step changes prompts, skills, workflow docs,
  `AGENTS.md`, planning rules, or implementation gates, create or update a
  GitHub Issue before implementation.
* If the work should proceed, recommend using
  `soundatlas-implementation-planning` to create or update the GitHub Issue,
  Plan Update, Detailed Plan Update, or Implementation Report.

Do not create local or repo-versioned implementation plan files.

## Project Constraints

* Keep changes small, reviewable, and MVP-oriented.
* Treat SoundAtlas as an editorial-cultural product, not only a data pipeline.
* Current product scope is New York 1965-1985 with curated routes, events,
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

## Review Modes

Use the smallest mode that fits the request:

* `idea grill`: test whether an idea is worth planning.
* `issue grill`: stress-test an Intake Issue, Plan Update, or Detailed Plan
  Update before implementation.
* `editorial grill`: review route briefs, dossiers, candidate events, accepted
  event dossiers, source notes, media plans, and seed-promotion readiness.
* `ux grill`: review UX audit findings or a proposed UX slice before Issue
  planning.
* `implementation readiness grill`: check whether an approved Issue is ready
  for an implementation prompt.

## Output

Run the critique as a sequence of one-finding turns.

For each finding, return only the next finding that has not yet been discussed.
Do not batch multiple findings into a single response.

Each finding should use this shape:

```md
## Verdict

Ready / Needs revision / Blocked

## Finding <n>

- Severity: Critical / Major / Minor
- What I found: <short statement>
- Decision recommendation: Proceed / Revise / Stop
- Why this recommendation: <short rationale>
- What to confirm next: <one concrete question or decision>

## Recommended Next Step

- Continue with the next finding, revise the artifact, run another grill-me
  pass, create/update a GitHub Issue with `soundatlas-implementation-planning`,
  or proceed to the relevant implementation prompt after approval.
```

After presenting one finding, pause and wait for the user to confirm before
moving on to the next finding. When there are no material issues, say so
clearly and identify any remaining review or test risk.
