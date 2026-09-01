The process is strong as a **research-to-narrative funnel**, but your observation is correct: it has a noticeable bias toward **compression and narrative coherence**. That is useful for getting to a finished route quickly, but it can also discard potentially rich material too early.

One correction first: the route ended with **6 Events grouped into 4 narrative Sections**, not 4 Events. That distinction actually exposes one of the central design questions in the process.

## 1. What worked

### Evidence gradually took control of the narrative

The strongest part was that we did not simply decide on a disco story and then fill it with famous clubs.

The concept began roughly as:

> underground disco clubs change nightlife

Then the evidence forced several changes:

* Black-owned/promoted nightlife became a distinct strand.
* Puerto Rican dancers became active historical agents rather than audience context.
* the Record Pool introduced infrastructure as an Event type.
* Paradise Garage became a convergence point rather than an inevitable endpoint.
* the route stopped implying that everything descended from the Loft.

That is exactly what a research process should do: **the narrative changed when the evidence changed**.

### Different research depths had clear purposes

The stages did useful kinds of work:

**Topic discovery** found possibilities.

**Concept framing** asked what might be interesting.

**Light evidence testing** checked whether there was actually a route there.

**Gap research** challenged blind spots.

**Minimum cohort testing** prevented route bloat.

**Deep research** tightened event boundaries.

**Cross-stop synthesis** prevented unsupported causality.

**Evidence review** checked whether prose had become stronger than the sources.

That division is valuable because it prevents doing full archival research on a topic that might later prove unsuitable.

### Event identity improved substantially

The Events became much better over time.

Instead of:

> The Gallery

we ended up closer to:

> The Gallery's Mercer Street incarnation develops a larger DJ-led sound/light/dance environment in 1974.

Instead of:

> St. Mary's — birthplace of Hustle

we got:

> St. Mary's becomes an important 1974 incubator for an already developing South Bronx Latin Hustle culture.

That is a major improvement in historical defensibility.

### The map influenced the historical interpretation

The map wasn't only used at the end.

It helped reveal:

* downtown clustering,
* the South Bronx as a distinct node,
* Midtown Black nightlife,
* simultaneous developments in 1974,
* the problem with drawing a single causal route line.

The strongest result was probably realizing that **Leviticus, St. Mary's, and the Gallery should appear simultaneously rather than sequentially**.

That is exactly the kind of thing a map-based historical product should discover.

---

# 2. What's problematic or challenging

## The process strongly optimizes toward a compact route

Your funnel observation is correct.

Almost every stage asks some version of:

> Can this candidate be removed?

That is excellent if the product goal is:

> get to a coherent, publishable 6-stop route quickly.

But it embeds an editorial preference:

**minimal sufficient narrative > expansive historical exploration.**

There is no corresponding stage asking:

> Now that the core story is stable, would adding one or two events materially enrich it?

So the process is asymmetric.

It has:

**discovery → reduction → reduction → locking**

but not:

**locking → optional enrichment**

That probably should change.

## Candidate generation became constrained too early

There were several opportunities to increase candidates.

During **light evidence testing**, we began with around seven.

During **targeted gap research**, the pool actually grew significantly:

* Ginza
* La Martinique
* Leviticus
* St. Mary's
* the Gallery
* the Record Pool
* Paradise Garage
* Flamingo
* Continental Baths
* the Saint
* Studio 54
* wider Best of Friends venues

So yes—**candidate expansion did happen**.

But the explicit purpose of the next stage was the *minimum-sufficient cohort test*. That stage immediately asked which candidates could be removed.

Consequently, candidates discovered during gap research mostly served as competitors for six slots rather than possibilities for a richer route.

That was a methodological choice, not something demanded by the evidence.

## The route shape was optimized before media richness was understood

This is probably the largest process weakness.

We selected Events mainly according to:

* evidence strength,
* narrative role,
* chronology,
* geography,
* representation,
* causal defensibility.

Those are excellent criteria.

But we didn't systematically ask:

* Does this Event have a strong photograph?
* Is there usable archival ephemera?
* Is there audio?
* Are there records strongly associated with it?
* Can we legally display those assets?
* Is there a compelling visualization?
* Will this stop feel visually different from the previous one?

That means we could theoretically select a historically ideal Event that produces a poor interactive experience.

For SoundAtlas, **media viability should probably enter earlier than final presentation treatment**.

## We didn't actually inspect SoundAtlas's technical model

This is important.

When I discussed things such as:

* 6 Events / 4 Sections,
* parallel Events,
* contextual Candidates,
* relationship types,
* progressive map states,
* generic visualization primitives,

I was reasoning from the **conceptual SoundAtlas context you had provided in conversation**.

I did **not** inspect:

* your actual Event schema,
* route JSON/model,
* Candidate schema,
* frontend map implementation,
* source model,
* media model,
* database constraints,
* existing route examples,
* route rendering code.

So some of the design conclusions may fit SoundAtlas conceptually while requiring significant model changes technically.

We were designing the ideal route representation before checking what the current product can actually encode.

That is useful for product design—but it should be recognized as such.

---

# 3. Main risks

## Risk 1: The funnel creates confirmation by selection

Although we deliberately tried to avoid confirmation bias, another kind can appear.

Once six Events are declared "minimum sufficient," subsequent deep research concentrates on those six.

That makes them increasingly well researched while discarded candidates remain lightly researched.

Eventually the chosen cohort looks much stronger simply because it received more attention.

A candidate that might have replaced one of them with equal research effort may never get that opportunity.

A useful safeguard would be a **challenger slot** during deep research:

> Research one plausible reserve candidate deeply enough to see whether it beats a core Event.

## Risk 2: Minimum sufficient becomes minimum interesting

Narratively, six stops are clean.

Experientially, however, the richest route might be eight or nine stops.

For example, Studio 54 was removed because it was unnecessary to *prove* the thesis.

But it might still be valuable because users already know its cultural image. It could function as a deliberate contrast:

> What most people think disco looked like versus the histories this route has just uncovered.

That Event could be narratively redundant but **pedagogically powerful**.

The current process doesn't distinguish those two ideas very well.

## Risk 3: Evidence quality and experience quality can diverge

An Event can be:

* impeccably sourced,
* narratively necessary,
* geographically meaningful,

and still be boring to experience.

Conversely, an Event with fantastic archival imagery and audio might produce a memorable route moment even if its narrative function is secondary.

SoundAtlas probably needs both scores.

Something like:

**Historical value**

* evidence strength
* route necessity
* significance

**Experience value**

* visual assets
* audio potential
* spatial interest
* interactive potential
* recognizability

## Risk 4: Map visualization can silently rewrite history

We caught this during the disco test.

A line:

**A → B → C**

doesn't merely show order.

Users naturally read it as:

> A led to B led to C.

Likewise:

* zoom hierarchy can imply importance,
* marker size can imply significance,
* animation order can imply chronology,
* connections can imply influence,
* clustering can imply community relationships.

So **visual historical claims need evidence review too**, not merely prose review.

## Risk 5: Community representation can become mechanical

We deliberately avoided quotas, which was good.

But there is an opposite danger: one Event can become responsible for representing an enormous cultural contribution.

For example:

> St. Mary's = Puerto Rican contribution.

That is obviously too reductive if the final presentation lets it read that way.

The route needs to communicate:

> this is one evidentiary window into a larger history,

not:

> this pin represents the history of this community.

---

# Your first observation: could the route have become larger?

Absolutely.

I can see at least **three explicit expansion points**.

### After targeted gap research

This was probably the strongest moment.

We had uncovered several genuinely different possibilities. Instead of going straight to:

> minimum-sufficient cohort

we could have done:

> **candidate landscape review**

and maintained perhaps:

**6 core candidates + 4 enrichment candidates + 3 contextual candidates.**

Then test what route lengths of 6, 8, and 10 would feel like.

### After cross-stop synthesis

Once the four-part structure emerged, we could have asked:

> Are there sections that would benefit from another Event?

For example:

**Section 2: Different New Yorkers Remake the Dance Floor**

already had three.

But perhaps:

**Section 3: The Scene Builds a System**

only had the Record Pool.

That could trigger a deliberate search for another infrastructure node—radio, record store, label, promoter network, etc.

### After the core route was stable

This is the missing stage I would now add:

## Enrichment Test

After finding the minimum sufficient route, ask:

> **What additional Event would create the greatest new value without weakening the narrative?**

Candidate value could come from:

* stronger geography,
* richer media,
* audience recognition,
* contrast,
* musical example,
* missing mechanism,
* emotional pacing,
* visual variety.

Then stop when marginal value falls below route complexity.

So the process becomes less of a pure funnel:

**expand → reduce → stabilize → selectively expand → finalize.**

I think that would improve it.

---

# What SoundAtlas information actually shaped the route?

Very little formal technical information.

What shaped it came mostly from our discussions:

* SoundAtlas is map-based.
* Events should have defensible locations.
* broad context should not automatically become Events.
* routes should remain reasonably concise.
* sources matter for publication.
* Candidate/Event distinction exists.
* map presentation can communicate historical arguments.
* you want a relatively fast path toward a finished route.

That was enough to develop the methodology, but not enough to validate implementation.

## Documentation that would materially improve future route creation

I'd want six things.

### 1. Route domain model

A concise explanation of:

* Route
* Section/Chapter
* Event
* Candidate
* Topic
* Source
* Media
* relationship between them.

Especially cardinalities:

> Can one Section contain many Events?
> Can one Event belong to multiple Sections?
> Can Sources support route-level claims?
> Can contextual places appear without becoming Events?

### 2. Event schema

Fields and constraints for:

* title
* dates
* location
* coordinates
* narrative
* significance
* actors
* source relationships
* confidence
* status
* media
* event type

### 3. Map capability specification

What can the current frontend actually do?

For example:

* reveal/hide pins
* highlight groups
* draw areas
* animate movement
* draw directional links
* show relationship edges
* control camera
* synchronize with narrative
* display historical boundaries
* change marker styles
* layer images/graphics

This could substantially influence route conception.

### 4. Narrative presentation model

How the UI currently represents:

* chapters,
* Events,
* transitions,
* parallel Events,
* context,
* intro/outro,
* scroll behavior.

### 5. Media specification

What types are supported:

* images,
* archive scans,
* audio,
* Spotify/YouTube links,
* playlists,
* record covers,
* video,
* animated graphics,
* diagrams.

Plus copyright/licensing requirements.

### 6. A few exemplary finished routes

Probably the most useful document of all.

Two or three routes annotated with:

> Here's the route model.
> Here's why this became an Event.
> Here's what stayed context.
> Here's how map behavior was encoded.
> Here's how media were selected.

That would give the narrative agent a much stronger understanding of the **actual product grammar**.

---

# Your media observation is also correct

Media was considered, but **far too late and too lightly**.

During deep research I occasionally noted things like:

* period photographs exist,
* flyers survive,
* membership cards exist,
* the Bronx Historical Society has dance imagery,
* the Gallery has archival photography,
* Paradise Garage has strong visual material.

Then during presentation treatment I proposed:

* invitations,
* dance photography,
* promoter/venue graphics,
* sound-system graphics,
* record-pool network graphics.

But we did **not perform a systematic media audit**.

So I cannot currently say:

> Yes, every one of these six Events has enough usable media for production.

We established probable archival potential, not asset readiness.

That should become a formal stage.

---

# Media viability should probably be tested alongside deep research

For each Event, I'd add:

**Images**

* period exterior?
* interior?
* people?
* flyers/posters?
* archival scan?
* rights/status?

**Audio**

* associated tracks?
* DJ recordings?
* oral history?
* radio recording?
* ambient reconstruction?

**Music**

* artist
* track
* record
* label
* release year
* documented relationship to Event

**Visualization**

* map movement?
* network?
* floor plan?
* timeline?
* sound-system diagram?
* audience/community geography?
* record circulation?

Then give each Event a **media readiness score**.

---

# Music and playlists

We didn't seriously develop this.

And I think that is a missed opportunity because for SoundAtlas, the musical material should arguably be almost as important as the map.

The goal shouldn't merely be:

> choose famous disco songs from 1974.

It should be:

> **What can the user hear that helps explain this specific Event?**

For example, conceptually:

**The Loft**

* records reflecting Mancuso's eclectic party programming
* perhaps one example showing why the Loft story isn't identical to later standardized “disco”

**Leviticus / Black disco network**

* music documented in Black disco-party contexts rather than generic disco hits

**St. Mary's**

* records connected to Latin Hustle and South Bronx dance practice

**The Gallery**

* music associated with Nicky Siano's DJ style and manipulation

**Record Pool**

* an example of a promotional record whose circulation illustrates the system

**Paradise Garage**

* records strongly associated with Larry Levan and Garage culture

This could produce either:

* one representative track per Event,
* 3–5 tracks per section,
* or a complete route playlist.

But those associations should themselves be researched. Otherwise we risk attaching plausible disco music to a place without historical evidence that it mattered there.

---

# Infographics and visualizations

This route already suggests several strong ones.

### Parallel New York — 1974

Map simultaneously showing:

* Midtown → promoter/ownership
* South Bronx → dancers
* downtown → DJ/technology

This expresses the central **multiple-development thesis** better than prose.

### Record circulation loop

**label → promo record → record pool → DJ → dancers → response → label**

Probably the clearest infographic in the entire route.

### Evolution of the dance space

Instead of a strict timeline:

**private room → community space → nightclub → network → purpose-built club**

Could show how the *type of space* changes.

### Components of the dance floor

Gradually assemble:

* record
* turntable
* DJ
* sound system
* lighting
* dancer
* community

Then reveal them together at Paradise Garage.

### Network of actors

Potentially show roles rather than people:

**promoters / dancers / DJs / engineers / labels / audiences**

and which Events foreground each one.

That would reinforce one of the route's most interesting arguments: disco wasn't produced only by musicians.

---

# What I would change in the process

I would keep most of what we did, but insert two explicit stages.

The revised middle/end would be:

**Topic discovery**
→ **Concept framing**
→ **Light evidence + route-shape test**
→ **Targeted gap research**
→ **Minimum-sufficient cohort**
→ **Deep research + media viability**
→ **Cross-stop synthesis**
→ **Enrichment test**
→ **Narrative draft**
→ **Evidence + visual-claim review**
→ **Final copy + presentation treatment**
→ **Implementation**
→ **Production QA**

The two additions matter:

**Deep research + media viability** prevents us from discovering too late that an Event is visually/audio-poor.

**Enrichment test** counteracts the funnel bias by asking whether adding something after the core route is stable would make the experience substantially better.

Overall, I think the process did an unusually good job at producing a **defensible compact historical argument**. Where it is weaker is producing a **rich multimedia exploration**. Right now, it optimizes more strongly for *“what is the smallest route that proves the story?”* than for *“what is the best route experience we can construct from the history?”*

For SoundAtlas, I suspect the ideal process needs to optimize for **both**.


I would add **human review gates at points where the next step makes an expensive or hard-to-reverse commitment**. I would *not* require approval after every stage; that would make the process slow and turn the human into a workflow babysitter.

## Where I would put human review

| Gate                                     | After                                             | Human decision                                                                                               | Why it matters                                                                          |
| ---------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| **A. Topic / concept review**            | Concept framing                                   | Is this a story we actually want to tell?                                                                    | Prevents spending research effort on a technically viable but uninteresting route.      |
| **B. Route-shape review**                | Targeted gap research + minimum-sufficient cohort | Does this candidate set feel historically and editorially right? Should we broaden, narrow, or challenge it? | This is the main defense against the funnel becoming too reductive.                     |
| **C. Research / media readiness review** | Deep research + media viability                   | Are the core Events sufficiently evidenced and experientially viable?                                        | Prevents weak sources or poor media availability from surfacing only during production. |
| **D. Narrative approval**                | Cross-stop synthesis + enrichment test            | Do we agree with the thesis, section structure, and final Event set?                                         | This is where the route becomes editorially “locked.”                                   |
| **E. Pre-production review**             | Evidence-reviewed copy + presentation treatment   | Does the proposed text/map/media treatment communicate the intended history?                                 | Stops visual design from silently changing the historical argument.                     |
| **F. Release review**                    | Implementation / production QA                    | Publish or send back?                                                                                        | Final correctness and quality gate.                                                     |

If you want a **fast route mode**, I would collapse those to four mandatory gates:

**Concept → Cohort → Narrative → Release.**

Everything between them can run relatively autonomously unless the agent discovers a route-breaking issue.

### The most important human gate is probably the cohort review

This is where I would explicitly present the human with more than the proposed minimum route.

Instead of:

> Here are the six Events I recommend.

the review should look more like:

> **Recommended core:** 6
> **Strong enrichment candidates:** 4
> **Context candidates:** 5
> **Rejected candidates:** 7
> **Why each was classified that way**

Then the human can say:

> “I want Studio 54 in despite its redundancy because users know it.”

or:

> “We are overcompressing the Black disco network; keep another stop.”

That creates an editorial intervention **before the funnel has permanently narrowed the story**.

---

# Standardized prompts have very high potential here

I would **not** build one giant “create a SoundAtlas route” prompt.

The process we just tested shows why.

A single prompt tends to mix:

* discovery
* historical judgment
* candidate selection
* research
* narrative writing
* map design
* media selection

and the model starts making downstream decisions before upstream questions are settled.

Instead, I would create a **prompt suite**, with one prompt per stage.

Each prompt should have four stable components:

**Input contract → task → output contract → stop condition.**

The output of one stage becomes the input to the next.

That makes the process inspectable and testable.

---

## Example: Topic discovery prompt

The prompt should say roughly:

> Generate research-derived narrative topic candidates for `[place / broad topic]`.
>
> Start from a blank slate. Do not inherit previous route structures or candidate Events.
>
> Search broadly across eras, communities, genres, institutions, technologies, and forms of musical activity.
>
> Prefer topics where geography materially contributes to the historical story.
>
> For each candidate provide:
>
> * working title
> * timeframe
> * narrative question
> * initial evidence basis
> * geographic mechanism
> * why it differs from the other candidates
>
> Do not create a route, chapters, or final thesis.
>
> Stop when there is a diverse candidate set sufficient for concept selection.

That is essentially the generalized documentation we built, converted into an agent contract.

---

## Concept framing prompt

> Take Topic X and explore what kinds of historical narratives it might support.
>
> Generate several competing interpretations rather than selecting the first plausible one.
>
> Identify tensions, possible geographic mechanisms, narrative questions, and provisional thesis directions.
>
> Do not search for route Events merely to fill the concept.
>
> Output a small set of testable narrative hypotheses.
>
> Stop when at least one hypothesis is specific enough for evidence testing but still open to revision.

The important phrase here is **competing interpretations**. That reduces premature lock-in.

---

## Light evidence + route-shape prompt

> Test the provisional concept against a small cohort of real historical places/events.
>
> Identify approximately 5–8 candidates with minimum sufficient evidence.
>
> For each record:
>
> * event boundary
> * date
> * place
> * source
> * possible narrative role
> * map value
> * initial inclusion status
>
> Plot or spatially compare the cohort.
>
> Explicitly identify ways the evidence contradicts or reshapes the concept.
>
> Do not optimize solely for confirming the hypothesis.

This last line should probably appear in several research prompts.

---

# I would standardize the *review prompts* too

This may be even more useful than standardizing the research prompts.

For example, the **cohort human-review packet** could always ask:

> The current recommended cohort contains 6 Events.
>
> Please review:
>
> **Narrative coverage:** What important part of the story is missing?
>
> **Candidate pressure:** Which excluded candidate would most improve the route?
>
> **Compression:** Is any community, mechanism, or period being represented by too few Events?
>
> **Experience:** Is there an Event worth retaining for recognition, emotion, media, or contrast even if it is not strictly necessary to prove the thesis?
>
> **Decision:** Approve / expand / replace / reframe.

This directly counters the “minimum sufficient” bias we identified.

---

# Deep research prompt should include media

I would change our earlier stage to:

## Deep Event Research + Media Viability

The standardized prompt for each retained Event could look roughly like:

> Deep-research Event X.
>
> Establish:
>
> * defensible event boundary
> * dates and precision
> * location
> * actors
> * documented facts
> * route claim supported
> * claims that should not be made
> * primary/contemporary sources
> * strong secondary sources
> * uncertainties
>
> Also evaluate media viability:
>
> * period photographs
> * flyers/posters
> * archival documents
> * audio
> * music directly associated with the Event
> * potential representative tracks/artists
> * video/oral history
> * possible infographic or visualization
> * known rights/licensing considerations
>
> Give separate confidence scores for:
> **historical evidence** and **experience/media readiness**.

That would have materially improved the process we just ran.

---

# Then add an explicit enrichment prompt

This is the missing anti-funnel step.

After the minimum route is stable:

> Treat the current route as the minimum defensible core.
>
> Do not remove core Events.
>
> Review reserve, contextual, and newly discoverable candidates for possible enrichment.
>
> Recommend additions only when they create substantial new value in at least one dimension:
>
> * historical coverage
> * geographic coverage
> * community agency
> * contrast
> * recognizability
> * musical richness
> * visual/media richness
> * interactive potential
> * pacing
>
> For every proposed addition explain:
>
> * what new value it adds
> * why an existing Event cannot provide that value
> * route complexity cost
>
> Recommend 0–3 additions.
>
> It is valid to recommend none.

That converts the process from a pure funnel into:

**expand → test → reduce → stabilize → selectively enrich.**

I think that is a much healthier route-creation pattern.

---

# Standardized output schemas matter as much as prompts

If you want this to become an actual SoundAtlas pipeline, I would avoid passing free-form essays from one agent stage to another.

For example, a candidate should eventually have structured fields like:

```text
candidate_id
title
event_boundary
date_start
date_end
date_precision
location
actors
historical_mechanism
narrative_role
map_role
evidence_summary
source_refs
evidence_confidence
media_readiness
visual_options
audio_options
status
status_reason
open_questions
```

And a route synthesis might output:

```text
working_thesis
sections
events_by_section
relationship_types
documented_links
interpretive_links
parallel_groups
convergence_points
context_candidates
reserve_candidates
remaining_claim_gaps
```

Then your prompts become more reliable because the agent has a precise place to put its decisions.

It also becomes much easier to test:

> Did every retained Event receive a source?

> Did any `interpretive_link` accidentally become `direct_influence`?

> Does every section have at least one Event?

> Are media-readiness fields empty?

---

# Prompts should also encode conceptual boundaries

This connects directly to the issue we discussed with your grill-me skill.

Each stage prompt should explicitly say both:

**what it is allowed to decide**
and
**what it must not decide yet**.

For example:

### Concept framing

Allowed:

> narrative questions, tensions, hypotheses.

Not allowed:

> final Events, schema design, implementation architecture.

### Minimum cohort

Allowed:

> Event selection and classification.

Not allowed:

> polished route copy.

### Narrative drafting

Allowed:

> wording and transitions.

Not allowed:

> inventing new historical relationships to make the story flow.

### Presentation treatment

Allowed:

> visual interpretation of established relationships.

Not allowed:

> drawing causal connections not supported by the synthesis.

This is probably one of the most important things to standardize.

---

# I would also make the prompts route-mode aware

You probably don't always want the same process.

For example:

**Quick route**

* lighter discovery
* one gap pass
* 5–7 Events
* fewer deep sources
* four human gates

**Standard route**

* process we developed
* media viability
* enrichment test
* 6–10 Events

**Deep editorial route**

* competing concepts
* challenger candidates
* deeper primary-source work
* music/media curation
* more human review

Same stages, different depth requirements.

That gives SoundAtlas a way to balance **speed versus editorial ambition** without inventing a new workflow each time.

---

## Where I would land

I think the process is very amenable to standardized prompts because the stages now have **clear epistemic responsibilities**.

The main thing I would standardize is not the wording of one magical prompt. I would standardize:

**stage contracts + structured outputs + review gates + stop conditions.**

Then individual prompts can evolve without destabilizing the overall process.

The architecture becomes something like:

**AI stage → structured artifact → automated checks → human gate when necessary → next AI stage.**

That seems particularly well suited to SoundAtlas because route creation mixes **research judgment, editorial judgment, geographic reasoning, media curation, and implementation constraints**—areas where full automation is possible in pieces, but human approval is still valuable at the moments where the story itself gets defined.

# Media availablity / rights situation

| Event               | Images / artifacts                          | Music / audio                       | Difficulty        | Main issue                                                   |
| ------------------- | ------------------------------------------- | ----------------------------------- | ----------------- | ------------------------------------------------------------ |
| **The Loft**        | Excellent                                   | Excellent                           | **Easy–moderate** | Rights, not discovery                                        |
| **Leviticus**       | Good archival ephemera, fewer iconic photos | Moderate/weak                       | **Moderate–hard** | Connecting specific music to the venue                       |
| **St. Mary’s**      | Excellent                                   | Moderate                            | **Moderate**      | Music associated with the dance ≠ proven St. Mary’s playlist |
| **The Gallery**     | Excellent                                   | Excellent                           | **Easy–moderate** | Choosing historically appropriate tracks                     |
| **NY Record Pool**  | Good documentary material                   | Good conceptual music possibilities | **Moderate**      | Event is infrastructure, so soundtrack is less obvious       |
| **Paradise Garage** | Exceptional                                 | Exceptional                         | **Easy**          | Mostly rights/licensing/embedding                            |
