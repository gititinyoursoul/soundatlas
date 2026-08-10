# Editorial review terminology

This is the canonical state vocabulary for SoundAtlas editorial data.

## Pipeline and artifact terms

- A **generated route result** is the agent-produced working result stored under
  the compatibility filename `complete-draft.json` (`complete_draft` remains
  the pipeline step key). It is not approved or published.
- A **route editorial review** is the route-scoped Human editorial record stored
  under the compatibility filename `route-review.json`. It is not private
  access-controlled data; repository access remains unchanged.
- An **editorial review revision** is one revision of that record. The API keeps
  the `RouteReviewResult` OpenAPI component as a compatibility wrapper around
  the internal `RouteEditorialReview` domain model.
- **Publication blocking checks** are the human-facing meaning of the retained
  `technical_ready` compatibility field. They are separate from editorial and
  source review.
- Canonical runtime records are **canonical seed data**. A published result is
  an **editorially published route revision**.
- Classify outputs precisely: a generated working artifact may be reviewed, a
  deterministic derived view mirrors it, and a diagnostic report explains a
  check or failure.

- `agent_recommendation` is an agent proposal for a candidate or event:
  `include`, `context`, `merge`, or `exclude`. It is never a Human approval.
- `editorial_state` is the Human route decision for a candidate or event:
  `draft`, `approved`, or `dont_use`. `context` is only a candidate/event
  recommendation; it is not a general record state.
- `content_review_status` is the Human content-review lifecycle for routes,
  places, events, and enrichment links: `draft` or `reviewed`. It does not
  decide route inclusion or publication. Media and image links remain
  Human-reviewed; generated links start as `draft`.
- Technical validity, enrichment quality, and route publication are separate
  checks. Agents must not write Human-owned states.

During the bounded migration, readers may accept legacy `status`,
`review_state`, and `review_status` input and normalize it at the boundary.
New or regenerated payloads must emit only the canonical names. Once all
consumers have migrated, the legacy `review_status` field is removed rather
than emitted alongside `content_review_status`.

Connections are deferred from the MVP because their current implementation is
not developed enough to add sufficient user value while adding editorial and
runtime complexity. Existing records remain readable temporarily for
compatibility, but new runs and publication do not depend on them. Shared
places retain their own content-review status; route use is derived from route
entries rather than a global place inclusion decision.
