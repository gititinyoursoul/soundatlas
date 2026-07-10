# Event Editorial Quality Standards

## Purpose

SoundAtlas events should be selected route arguments, not loose facts that only
share a genre, city, or era. These standards define the minimum editorial checks
before accepted events become seed-shaped records.

Use this document before adding or revising event records in
`data/seed/events.json`.

## Event Quality Pass

Before seed authoring, confirm that each event:

- comes from `accepted-events.json`, an accepted-event dossier, a reviewed route
  artifact, or explicit human instruction
- has a clear inclusion rationale for this route
- has enough place and year specificity for the current seed model
- has a `summary` that says what happened
- has a `significance` that says why the event matters for this route
- uses cautious wording for contested, weakly sourced, or mythologized claims
- keeps unresolved source, place, date, media, rights, or claim risks visible
- stays `review_status: "draft"` when generated, uncertain, newly accepted, or
  not final-reviewed

Do not use seed authoring to resolve candidate review. If the event's candidate
decision is unclear, stop at a proposal and request human review instead of
editing `data/seed/`.

## Candidate Decisions And Seed Review Status

Candidate decisions and seed `review_status` are separate layers.

Candidate decisions:

- `keep`: may move into the accepted-event dossier and seed authoring.
- `maybe`: research lead only; do not seed yet.
- `merge`: may move forward only after a human resolves the merge target.
- `reject`: stop for this route.

Seed `review_status`:

- describes the review state of a structured seed or runtime record
- does not decide whether a candidate belongs in the route
- does not replace `accepted-events.json` or its companion
  `accepted-events.md` dossier

A `keep` event can still become a seed record with
`review_status: "draft"`. Use `review_status: "draft"` for generated,
uncertain, newly accepted, or not-final-reviewed seed records unless the user
explicitly provides a reviewed decision.

## Legacy Candidate Labels

Older route artifacts may use labels such as `develop`, `context`, or `defer`.
Treat those labels as draft review signals only. They are not approval for seed
authoring.

When older labels appear, translate them into the editor-facing vocabulary only
after human review:

- `keep`
- `maybe`
- `merge`
- `reject`

Do not convert unresolved `maybe`, unresolved `merge`, `reject`, or unreviewed
legacy-status candidates into seed-shaped records.

## Smell Tests

Rework the event before seed transfer when:

- the event is only adjacent to the route
- the significance could describe any event in the route
- the event depends on unsupported `first`, `birthplace`, `invented`, or
  sole-origin claims
- the place is only a map pin, not part of the route argument
- the date range is too vague for the story being told
- media or source links are treated as approved before human review
- source risks disappear from the seed-facing wording
