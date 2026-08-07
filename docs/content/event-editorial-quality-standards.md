# Event Editorial Quality Standards

## Purpose And Boundary

SoundAtlas events should read as source-grounded editorial chapters, not as
schema fields filled with generic historical facts. Each event should tell a
specific part of a route's story while remaining understandable when opened on
its own from the map or timeline.

Use this document before adding or revising event records in
`data/seed/events.json`. It is the source of truth for event prose, route fit,
claim framing, and source discipline. It does not change the seed schema,
define runtime presentation, or add publication gates.

`content-pipeline-interaction-contract.md` owns the target human-review
interaction. Editorial checks in this document produce revisions or visible
warnings; they do not set the private Draft, Approved, or Don’t use route state
and do not authorize route publication.

## The Event As A Self-Contained Chapter

An event should have a clear function in the route's arc. It may establish the
setting, introduce a practice, mark a turning point, show a conflict, trace a
spread or transformation, or reveal a consequence. These are editorial roles,
not new seed fields or required tags.

Write for nonlinear exploration:

- make the people, action, place, and time legible without another event open
- connect the event to earlier developments or later consequences when useful
- do not depend on the reader having followed chronological order
- avoid navigation phrases such as `as we saw` or `in the next chapter`
- give the event a route-specific purpose rather than treating it as an
  isolated fact

The prose should use an immersive literary register, but immersion must come
from documented specificity. Every concrete scene detail must be supported by
the event's source material.

## Field Standards

### `title`

Name a concrete subject, action, or historical moment. A strong title creates
editorial interest without exaggeration and remains scannable in map and
timeline contexts.

- prefer named people, groups, works, venues, practices, or changes when they
  are central to the event
- use an active, specific formulation instead of a broad topic label
- avoid unsupported superlatives and origin claims such as `first`, `birth`,
  `invented`, or `single-handedly created`
- do not impose a hard word or character limit; revise titles that stop being
  easy to scan

### `summary`

Tell what happened. A summary should generally use two to four sentences to
turn the documented event into a compact editorial chapter.

- establish the relevant people, action, place, and time
- select details that create movement or make the historical change tangible
- use scene details only when a listed source supports them
- keep interpretation secondary; the main work here is the event itself
- prefer precise nouns and verbs over labels such as `important`, `iconic`,
  `major`, or `influential`
- treat two to four sentences as a flexible target, not a validation limit

### `significance`

Explain why the event matters to this route. Significance should generally use
one or two sentences and should add interpretation rather than restate the
summary.

- name the event's function in the route's development or argument
- explain what the event enabled, changed, connected, challenged, or made
  visible
- connect backward or forward without assuming a fixed reading order
- avoid significance that could be copied unchanged onto any other route event
- treat one or two sentences as a flexible target, not a validation limit

### `source_urls`

An event meeting these standards needs at least one relevant source. One source
is sufficient when it supports the event's concrete claims and scene details.
A draft may remain visible while research continues, but an included active
Event with no Source URL is technically unready for Publication.

- use a source that addresses the event, not merely the broad genre, city, or
  era
- remove, soften, or explicitly qualify a detail that the source does not
  support
- a source may document what happened or document the circulation and cultural
  importance of a myth, disputed account, or oral tradition
- do not treat a media link, search result, or thematically related page as
  evidence unless it actually supports the claim
- keep unresolved source concerns visible instead of allowing a URL's presence
  to imply certainty

This event-level source model does not require sentence-level citation fields.
If a claim cannot be represented responsibly with the current model, keep the
event in draft or raise a separate schema proposal.

### `content_review_status`

Use `content_review_status: "draft"` for generated, uncertain, newly accepted, or not
final-reviewed event records.

- agents and automated checks must not assign `reviewed`
- passing structural or editorial checks does not constitute human approval
- unresolved editorial concerns remain warnings and do not become extra human
  approval gates
- final route approval does not imply that every warning has been resolved
- any transition associated with publication belongs to the applicable
  human-controlled route review flow, not to this quality checklist

This seed compatibility field is not the private route-scoped Draft, Approved,
or Don’t use state defined by the interaction contract. It does not determine
whether an event is included in a published route and is not a public-facing
editorial badge.

If no explicit human-controlled review decision applies, leave the event as
`draft`.

### `tags`

Treat tags as reusable discovery metadata, not as miniature summaries or
approval signals.

- prefer an existing lowercase tag when it expresses the same concept
- add a tag only when it can be reused for an artist, place, practice, genre,
  community, or narrative theme
- avoid near-synonyms, one-off editorial adjectives, and generic labels such as
  `important` or `history`
- use a narrative tag such as `origin-story` only when it is useful across
  events
- do not use a tag as a substitute for qualifying a myth or uncertain claim in
  the prose

## Route Fit

An event belongs in a route because it performs a specific narrative or
explanatory job, not merely because it shares a place, genre, or time range.

Before seed authoring, state an inclusion rationale in the accepted-event or
reviewed route artifact. Ask:

- What does this event help the route explain?
- What changes in the route's argument if the event is removed?
- Is the place part of what happened, or only a convenient map pin?
- Does the significance explain this route-specific role?

Rework, defer, merge, or reject an event when its only justification is
adjacency. Do not use seed authoring to resolve candidate selection.

## Source-Grounded Immersion And Myths

Immersive prose is welcome when its details are documented. Do not invent:

- dialogue or quotations
- thoughts, motives, or emotional reactions
- crowd behavior or atmosphere
- sensory details
- actions, chronology, or causal links

If a source documents those details, they may be used. If it does not, build
narrative movement from supported people, actions, places, circumstances, and
consequences instead.

Myths, legends, disputed origins, and retrospective canonization can be part of
the story. Identify their status directly with language such as:

- `often remembered as`
- `later canonized as`
- `accounts differ about`
- `oral histories describe`
- `the story is commonly told as`

A source may establish that a story is culturally important even when it does
not establish the story as literal fact. Tags such as `origin-story` may
supplement this framing, but the prose must carry the distinction.

## Rewrite Guidance

The examples below are illustrative patterns, not proposed seed revisions or
approved historical claims. Bracketed details may be used only when a listed
source supports them.

| Check | Weak | Stronger pattern |
| --- | --- | --- |
| Title | `An Important Party` | `[Artist] Brings [Practice] to [Venue]` |
| Summary | `DJ culture became popular in the neighborhood.` | `At [venue] in [year], [artist] used [documented technique] during [documented event]. [Source-supported response or consequence] carried the practice beyond that occasion.` |
| Significance | `This was important to music history.` | `The event turns the route from [earlier condition] toward [later development], linking [practice] to [route-specific consequence].` |
| Myth framing | `[Event] was where [genre] was born.` | `[Event] is often remembered as the birth of [genre]. That later canonization gives one documented gathering a symbolic place in a longer, disputed origin story.` |
| Source discipline | A general genre page is listed while the prose supplies an undocumented crowd scene. | The prose uses only the people, actions, place, date, and response documented by the listed event source. |
| Route fit | `The event happened in the same city and era.` | `The event belongs because it shows how [route practice] moved from [earlier state] to [later state].` |
| Tags | `important`, `music`, `history`, and a new synonym for an existing term | Reused tags such as `dj-culture`, `block-party`, and `bronx` when each describes the event and recurs across the collection |

A complete event should let the fields do different work:

```text
Title: [Named subject] [specific action or change]

Summary: What happened, rendered through two to four sentences of documented
people, action, place, time, and consequence.

Significance: Why this chapter changes or clarifies the route's story, rendered
in one or two sentences without repeating the summary.
```

## Candidate Recommendations, Route State, And Seed Review Status

Candidate recommendations, the target private route-review state, and seed
`review_status` are separate layers.

Current candidate recommendations:

- `keep`: may move into the accepted-event dossier and seed authoring
- `maybe`: research lead only; do not seed yet
- `merge`: may move forward only after a human resolves the merge target
- `reject`: stop for this route

The current pipeline pairs those recommendations with its implemented review
and accepted-event handoff. The target review surface instead gives the human
Draft, Approved, and Don’t use controls. Draft and Approved events may be
published; Don’t use events remain in editorial history but are excluded. The
target state does not make an agent recommendation authoritative.

Seed `content_review_status` describes the Human content review state of a structured seed or runtime
record. It does not decide whether a candidate belongs in the route and does
not replace `accepted-events.json` or its companion `accepted-events.md`.

A candidate with `agent_recommendation: "include"` can still become a seed record with `content_review_status: "draft"`.
Do not convert unresolved `maybe`, unresolved `merge`, `reject`, or unreviewed
legacy-status candidates into seed-shaped records.

Older route artifacts may use `develop`, `context`, or `defer`. Treat these as
draft review signals only and translate them into `keep`, `maybe`, `merge`, or
`reject` only after human review.

## Editorial Review Checklist

### Selection And Route Fit

- [ ] The event has a confirmed candidate decision and inclusion rationale.
- [ ] Its place, period, and subject fit the route for more than adjacency.
- [ ] Removing it would leave an identifiable gap in the route's story.

### Chapter And Prose

- [ ] The event is a self-contained chapter with a clear role in the route arc.
- [ ] The title names a concrete subject, action, or historical moment.
- [ ] The summary says what happened through specific, sourced detail.
- [ ] The significance says why it matters here without repeating the summary.
- [ ] The prose remains understandable when events are opened out of order.
- [ ] Vague importance claims and generic editorial adjectives have been
      replaced with concrete meaning.

### Claims And Sources

- [ ] At least one relevant source supports the event.
- [ ] Every concrete scene detail is supported by that source material.
- [ ] `first`, `birthplace`, invention, and sole-origin claims are supported or
      explicitly qualified.
- [ ] Myths, oral traditions, disputed accounts, and later canonization are
      identified in the prose.
- [ ] Unresolved source, place, date, media, rights, or claim risks remain
      visible.

### Metadata And Review Boundary

- [ ] Tags reuse useful lowercase vocabulary and avoid near-synonyms.
- [ ] Candidate selection remains separate from seed `review_status`.
- [ ] Generated or unresolved content remains `draft`.
- [ ] No agent, automated check, or warning resolution is presented as human
      publication approval.

A failed editorial check calls for revision or a visible warning. It does not
silently resolve uncertainty, automatically block publication, or create a new
human approval gate.
