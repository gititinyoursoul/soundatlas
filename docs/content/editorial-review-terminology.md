# Editorial review terminology

This is the canonical state vocabulary for SoundAtlas editorial data.

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
