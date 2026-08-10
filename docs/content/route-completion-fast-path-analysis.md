# Fast Path to a Complete Route: Current Workflow Analysis

- **Status:** Analysis and recommendation; not implemented workflow behavior
- **Issue:** [#148](https://github.com/gititinyoursoul/soundatlas/issues/148)
- **Scope:** Current SoundAtlas route editorial workflow
- **Excluded:** The separate source-first Research feature

## Purpose

SoundAtlas needs a short path from a route topic to a coherent,
evidence-grounded complete route. This analysis evaluates whether the current
route editorial workflow can provide that path, which activities are necessary
before the first route is complete, and which work can happen later.

The analysis distinguishes route completeness from research completeness. It
does not change the current workflow, publication rules, prompts, route
artifacts, or runtime behavior. The recommendations require separately approved
implementation work before they become authoritative workflow instructions.

## Current Workflow

The current route-centered path is described by
[`editorial-workflow.md`](editorial-workflow.md) and the thin Human review and
publication boundary in
[`content-pipeline-interaction-contract.md`](content-pipeline-interaction-contract.md):

```text
route input
  -> route brief
  -> research dossier
  -> Candidate outline
  -> generated route result
  -> route-scoped Human review
  -> publication blocking checks
  -> exact-result publication
  -> canonical seed data
```

Conceptually, the workflow needs one authoritative generated result and one
authoritative reviewed result. In the current system, `complete-draft.json`
provides the generated Content authority and `route-review.json` binds that
Content to Human Draft, Approved, and Don't use decisions. These filenames are
current implementation observations, not required parts of the fast-path
concept.

The current generated result can add, omit, merge, split, and reorder Candidate
material before creating seed-shaped Event and Place content. The current
review record keeps Human decisions separate from agent recommendations,
warnings, technical errors, and publication authorization.

Exact publication consumes the Event and Place content bound into the route
review. The legacy `accepted-events` handoff, framing files, seed-transfer
preview, and validation report remain compatibility or diagnostic artifacts;
they do not own the active generated result or Human route state.

## Completion States

The workflow needs four distinct meanings of completion:

| State | Meaning |
| --- | --- |
| Generated route | One coherent route-shaped result has complete reader-facing Event drafts and a proposed sequence. |
| Evidence-grounded route | Every included Event has a defensible boundary and enough relevant evidence for the claims actually expressed. |
| Publishable route | The exact reviewed result is structurally valid, sufficiently supports the claims necessary to each included Event, and has no publication blocking errors. |
| Published route | The Human has explicitly promoted that exact reviewed result to canonical seed data. |

Research completeness is not one of these states. A route can be credible and
publishable without exhausting every Source, Candidate, interpretation, or
possible enrichment direction. Likewise, generating a structurally complete
route does not mean its historical claims are sufficiently supported.

For fast-path evaluation, the meaningful outcome is the first **publishable
route**. Time to a generated route remains a useful intermediate measure, but
it must not count an unsupported route draft as completion.

## Evidence from the Current Bronx Route

The current Birth of Hip-Hop artifacts show that SoundAtlas can reach generated
route completeness before it reaches evidence-grounded or publishable
completeness:

- The route dossier contains 23 Candidate Events.
- The active generated result retains 19 of them as reader-facing Events.
- Seven active Events have an `include` recommendation and twelve have a
  `context` recommendation.
- All 19 active Events have empty `source_urls` arrays.
- The route review consequently records a missing-Source publication error for
  every active Event.
- The compatibility seed-transfer preview still proposes 23 Events, while the
  active generated route contains 19, demonstrating that the two paths can
  describe different route cohorts.

These observations come from the route's
[`research-dossier.md`](routes/birth-of-hip-hop/research-dossier.md),
[`complete-draft.json`](routes/birth-of-hip-hop/complete-draft.json),
[`route-review.json`](routes/birth-of-hip-hop/route-review.json), and
[`seed-transfer-report.md`](routes/birth-of-hip-hop/seed-transfer-report.md).
They describe draft workflow artifacts, not accepted historical content.

The result exposes two different bottlenecks:

1. The route composition remains close to the longlist instead of selecting a
   minimum sufficient provisional cohort.
2. Source directions in the dossier have not been resolved into evidence for
   the selected Events. Current publication policy expresses part of this gap
   through required Source URLs, but URL presence alone would not establish
   claim support.

## Alignment with a Fast Path

### Existing strengths

The current workflow already provides the main fast-path foundation:

- A lightweight brief establishes the question, thesis hypothesis, geography,
  time range, Candidate anchors, and known risks.
- The dossier can widen historical coverage before the route roster is fixed.
- The Candidate outline preserves considered material without making it
  canonical Content.
- Complete drafting produces one coherent route result rather than requiring
  the Human to assemble a route from individual Event proposals.
- Agent composition can narrow or reshape the outline.
- Generated Events default to Draft, so the Human does not have to approve each
  Event individually for it to remain included.
- Don't use excludes an Event without deleting its Candidate or review history.
- Materially changed content returns for review, while unchanged Human
  decisions can be preserved.
- Exact publication protects the currently published route from later
  regeneration.

Together, these boundaries allow SoundAtlas to create an initial route and
later strengthen it through bounded revisions rather than reconstructing all
unaffected Content.

### Current friction

#### Dossier breadth

The full dossier template covers artists, communities, places, influences,
circumstances, Candidates, Connections, editorial Sources, media, images, and
risks. This breadth is useful for route development, but media, image, optional
Connection, and peripheral-Candidate work does not all need to block the first
publishable route.

The first-route critical path needs only enough dossier work to establish the
historical argument, narrative phases, plausible Candidate boundaries, likely
route anchors, Source directions, and material gaps.

#### Longlist breadth becoming route breadth

A Candidate longlist preserves research and editorial possibilities. It should
not become the route roster by default. The first complete route needs a
**minimum sufficient provisional cohort**: small enough to investigate
efficiently, but sufficient to explain the topic across the dimensions that
matter to the route.

The cohort is coherent when its Events collectively:

- answer the route question and support its thesis rather than merely sharing
  a genre, place, or period;
- form an intelligible historical development with no missing transition that
  materially changes the explanation;
- provide sufficient chronological and geographic coverage for the route's
  declared scope;
- represent the communities, practices, institutions, or circulation paths
  necessary to avoid a materially distorted account; and
- give every included Event a distinct narrative function.

“Minimum sufficient” is not a fixed count and does not mean mechanically
minimizing Events. Removing another Event has gone too far when the removal
creates a material explanatory, chronological, geographic, community, or
narrative gap.

A Candidate is provisionally Event-ready when it has a plausible historical
boundary, a distinct route function, an honest place/time representation, and
claims that can be tested with available or targeted evidence. Event readiness
is not final before that evidence test. A structurally attractive Candidate may
still be narrowed, merged, replaced, or removed when the evidence does not
support its identity or narrative role.

The current complete-draft contract allows a `context` recommendation to remain
a full map and timeline Event. Broad conditions can therefore become Event-sized
evidence and editorial obligations even when the draft itself says that the
material lacks a bounded occurrence, place, or date.

Context should become an active Event only when it has an honest Event
boundary, a useful route function, a defensible place/time representation, and
a viable evidence basis. Other context can remain in route framing, Event
significance, inactive Candidate records, or later research.

This reflects a broader principle: **research concepts and route units do not
need to share one ontology**. Historical orientation may identify conditions,
communities, scenes, institutions, technologies, trends, interpretations, and
specific occurrences. The route should turn only suitable route units into
Event pins; historical importance alone does not make every research concept
an Event.

#### Missing selected-cohort evidence activity

The current path can move from dossier Source leads to reader-facing Event
prose without resolving those leads into evidence. The generation contract
correctly prohibits invented Source support, but the route remains blocked
when no bounded activity acquires evidence for the selected cohort.

Evidence work becomes more efficient after a provisional cohort is known. It
can then focus on the Events SoundAtlas is actually trying to publish rather
than applying equal effort to every longlist Candidate. The selection remains
provisional during this work: evidence may expose a weaker boundary, support a
different Event, reveal a missing Candidate, or show that the route needs a
different balance before its first publication.

The conceptual evidence floor is therefore not a Source count. **The claims
necessary to an Event's identity and narrative role must be sufficiently
supported.** One strong Source may support those claims, while one tangential
URL may support none of them. Contested, causal, origin, invention, or similarly
high-risk claims may require comparison, narrower wording, explicit
uncertainty, or deferral. Concrete Source-count and publication-blocking rules
remain implementation and publication policy, currently described by
[`event-editorial-quality-standards.md`](event-editorial-quality-standards.md).

#### Compatibility-path duplication

The active generated-result and exact-publication path no longer depends on
the legacy accepted-events gate. However, route concept, framing,
seed-transfer, and validation artifacts remain visible in the file-based
pipeline and can imply an additional sequence of required handoffs.

These artifacts may remain useful diagnostics or compatibility views until
their separately approved retirement. They should not define route
completeness when they differ from the active complete draft and bound route
review.

## Minimum Work for the First Publishable Route

The current workflow needs the following outcomes on its critical path:

> Every critical-path activity should reduce uncertainty that could prevent a
> coherent route from being published.

1. **Bounded route intent:** question, thesis hypothesis, geography, time
   range, and known historical risks.
2. **Sufficient historical orientation:** narrative phases, major practices,
   communities, places, institutions, and circulation changes needed to avoid
   a flat chronology or single-origin account.
3. **Candidate longlist:** possible Events with inclusion rationales and
   boundary risks.
4. **Provisional route cohort:** a minimum sufficient set of provisionally
   Event-ready Candidates that explains the thesis without material coverage
   gaps.
5. **Selected-Event evidence test:** sufficient support for the claims needed
   by each Candidate's identity and route function, with proportionate
   treatment of contested or high-risk claims.
6. **Adjusted route cohort:** boundaries and membership revised in response to
   evidence before the route is treated as complete.
7. **Complete reader-facing result:** route sequence, Event titles, dates,
   places, summaries, significance, Sources, and visible warnings.
8. **Human review:** inspect the route through the coordinated map, timeline,
   and StoryPanel; approve, exclude, or leave Events as Draft.
9. **Publication validation and decision:** publish only the exact reviewed
   result when blocking checks clear.

The following work can normally happen after the first route without reducing
its credibility:

- exhaustive research across unused Candidates;
- full archive or artifact sweeps;
- corroboration of low-risk details not expressed in route Content;
- media and image discovery or review;
- optional Connection development;
- alternate route structures;
- research into deferred or excluded Candidates; and
- broader contextual material that does not affect the current route thesis.

Deferral is inappropriate when missing work could change an included Event's
existence, place, period, participants, central significance, or the route's
overall argument.

## Recommended Fast Path

```text
route input
  -> concise brief
  -> lean route-structure dossier
  -> Candidate longlist
  -> minimum sufficient provisional route cohort
  -> evidence test
  -> adjusted route cohort
  -> complete reader-facing route result
  -> explorer review
  -> exact publication
```

This is a conceptual responsibility order, not a prescribed new architecture
or set of persisted stages. Different implementation mechanisms may satisfy it
while retaining the current route-folder, CLI, review, and publication
boundaries.

The principal change in emphasis is that breadth happens before provisional
cohort selection, while detailed effort follows and may adjust that cohort.
Efficiency focuses investigation without prematurely fixing the historical
narrative. The system should not require maximum research depth, complete
enrichment, or development of every Candidate before it can produce a credible
first route.

## Later Strengthening

After publication, later evidence or editorial work should produce a new Draft
proposal while leaving the published route unchanged. Strengthening may:

- add or improve Sources;
- make dates, places, participants, or wording more precise;
- narrow uncertain claims;
- merge or split an affected Event;
- replace an unsupported Event;
- add a previously deferred Candidate; or
- revise route sequence when new evidence materially changes the argument.

Unchanged Events and Human decisions should remain stable. Only evidence that
materially changes the thesis or route arc should require broad recomposition.
This follows the existing exact-result publication and selective regeneration
boundaries rather than requiring a generalized versioning or workflow platform.

## Evaluation Criteria

The concept should first be evaluated through three questions:

1. Can the process reliably reach a defensible route without researching the
   entire topic?
2. Does early provisional cohort selection focus investigation without
   prematurely fixing the historical narrative?
3. Can deferred work genuinely remain deferred without undermining the
   published route?

If those conditions hold, operational evidence can test whether a particular
implementation realizes the concept efficiently:

- elapsed and agent-run effort from route input to the first generated route;
- elapsed and Human-review effort from route input to the first publishable
  route;
- number of included Events that lack required evidence after generation;
- proportion of the longlist developed as active Events;
- number of Human decisions needed before publication;
- route-cohort churn after targeted evidence work;
- whether later strengthening preserves unaffected Event content and decisions;
- historical coherence, place/time coverage, and cautious treatment of
  contested claims; and
- whether deferral hides any gap material to the route's argument.

A faster generated draft is not an improvement if most Events remain blocked
or later evidence requires the route to be rebuilt. Conversely, researching
every possible Candidate before producing a reviewable cohort is unnecessary
when a smaller evidence-grounded route can satisfy the MVP.

## Recommendation and Decision Boundary

The current route workflow should remain the foundation for the fast path. The
main opportunity is to tighten its editorial contract:

- keep the brief and dossier sufficient but lean;
- preserve breadth in the Candidate longlist;
- choose a minimum sufficient provisional cohort and adjust it through an
  evidence test before complete drafting;
- do not force weakly bounded context into active Event membership;
- concentrate evidence work on the provisional cohort without treating its
  membership or boundaries as fixed;
- preserve one authoritative generated result and one authoritative reviewed
  result, independently of their current artifact names;
- keep compatibility artifacts outside the conceptual completion gate; and
- preserve later strengthening through bounded reviewed revisions.

This recommendation does not authorize those workflow changes. Human Event
inclusion, historical interpretation, Source judgment, route composition, and
publication authority remain unchanged. Any implementation must be planned and
approved through its own GitHub Issue.
