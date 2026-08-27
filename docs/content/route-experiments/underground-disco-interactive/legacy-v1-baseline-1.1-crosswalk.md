# Legacy Disco v1 to baseline-1.1 crosswalk

## Purpose and evidence boundary

This crosswalk establishes the comparison baseline for a later live Disco run
using the experimental route-authoring `baseline-1.1`. It evaluates the legacy
v1 process; it does not regenerate its research, create an experimental route
version, or decide whether any baseline stage should be kept, merged, or
rejected.

The immutable v1 evidence is commit `811c52b`, under
`docs/content/routes/underground-disco-interactive/`. The current untracked
`underground-disco-interactive-v1/` directory was checked byte-for-byte against
all 28 files at that commit and is only a working mirror. The notation
`v1@811c52b/<filename>` below means that exact filename at commit `811c52b` in
the route directory named above; a bare companion filename in the same table
cell uses the same immutable location.

Statuses mean:

- `met`: the v1 artifact substantially satisfies the baseline-1.1 purpose and
  output contract;
- `partial`: the substantive work exists, but a required output, control, or
  traceability element is absent;
- `missing`: no corresponding v1 work is evidenced; and
- `not-applicable`: the baseline requirement does not apply to the v1 run.

## Stage crosswalk

| Baseline stage | Status | Exact v1 evidence | What v1 demonstrates | What baseline-1.1 adds | Later live-run comparison |
| --- | --- | --- | --- | --- | --- |
| 00 — Run brief | `missing` | No corresponding artifact among the 28 files at `811c52b:docs/content/routes/underground-disco-interactive/`. | Scope emerged through the interaction and can partly be inferred from later outputs. | A named experiment/version, method, starting state, intended length, allowed variation, comparison target, stage/status, inherited inputs, Human checkpoint, and stop reason. | Whether the live run begins with enough fixed context to interpret choices, timing, skips, and termination without reconstructing chat history. |
| 01 — Topic discovery | `partial` | `v1@811c52b/01-topic-discovery-output.md`; companion method note `01-topic-discovery-docs.md`. | A genuine blank-slate pass produced eight distinct topics, source anchors, narrative questions, map potential, and three recommendations without prematurely drafting routes. This is a strong v1 standard to preserve. | Explicit material gaps for every topic, a uniform comparison contract, a recorded Human selection, and checkpoint status. | Topic diversity and usefulness; whether Source and gap fields improve the Human selection without making discovery heavier. |
| 02 — Narrative concepts | `partial` | `v1@811c52b/02-narrative-concept-framing-output.md`; companion `02-narrative-concept-framing-docs.md`. | The selected Disco topic was tested through three thesis options, two materially different arcs, place relevance, tensions, actors, and route functions. It kept the thesis provisional. | Four to eight consistently specified competing arcs, risks and disconfirming evidence per arc, side-by-side criteria, a bounded shortlist, and an explicit recorded Human decision. | Whether broader, structured comparison produces a materially better selected arc than v1's three thesis directions/two arcs, and how much Human effort selection requires. |
| 03 — Light evidence and route shape | `partial` | `v1@811c52b/03-light-evidence-route-shape-test-output.md`; companion `03-light-evidence-route-shape-test-docs.md`. | Seven provisional Candidates were tested with minimal evidence, roles, route value, an evidence verdict, and a meaningful geographic hypothesis. The test exposed a Manhattan gay-nightlife bias and reshaped the concept before deep research. | Stable Candidate IDs and shared fields, verified coordinates or product place records, a recorded spatial-comparison method, early media fields, explicit counterevidence questions, and a durable Human decision when the community boundary changes. | Whether coordinate-backed comparison changes the map conclusion; Candidate/schema completeness; time spent; and whether the same representation gap is detected as early. |
| 04 — Targeted gap research | `partial` | `v1@811c52b/04-target-gap-research-output.md`; continuation rationale `04-target-gap-research-whats-next.md`; companion `04-target-gap-research-docs.md`. | Focused research corrected the initial bias by adding Black ownership/promotion, Puerto Rican dancer agency, and record-pool infrastructure. Its ten-row landscape records retain/add/remove direction and changes the thesis from a linear club genealogy to parallel streams. | Preserved Candidate IDs, previous/current status and changed-at history, claim-specific Source mapping, mapped new Candidates, a normalized landscape, and unresolved Source/place questions in shared fields. | Which gaps and Candidates are found; whether status history makes the ten-row reshaping reproducible; Source quality; representation correction; and research effort. |
| 05 — Cohort decision | `partial` | `v1@811c52b/05-sufficient-chort-test-output.md`; continuation rationale `05-sufficient-chort-test-whats-next.md`; companion `05-sufficient-chort-test-docs.md`. | A rigorous removal test produced a six-Event minimum core, explained the unique function and removal cost of each Event, retained named context/reserve options, tested geography and coverage, and provisionally locked the cohort. | A second enrichment/challenger pass, honest route-length options, normalized classifications for every serious Candidate, at least one plausible challenger comparison, experience/media checks, and an explicit Human cohort decision. | Whether baseline-1.1 preserves v1's defensible six-Event core while reducing its one-way compression bias; additions or replacements; route-length choice; and Human intervention. |
| 06 — Deep route research | `partial` | Actual six-Event research at `v1@811c52b/06-deep-rout-research-docs.md`; reusable v1 method at `06-deep-rout-research.md`; continuation rationale `06-deep-rout-research-whats-next.md`. | All six Events received tighter boundaries, actors, supported/non-supported claims, Sources, confidence, route function, and focused follow-up needs. Five were strong; Leviticus remained provisionally locked pending corroboration. | Stable Event IDs linked to Candidate IDs, claim-level Source records, explicit non-claims, separate historical-confidence and experience/media-readiness assessments, rights/availability fields, and equally deep challenger research when selected. | Boundary and claim changes, Source coverage, confidence, Leviticus handling, media readiness, challenger performance, and whether stable records reduce later rework. |
| 07 — Cross-Event synthesis | `partial` | `v1@811c52b/07-cross-stop-synthesis-output.md`; continuation rationale `07-cross-stop-synthesis-whats-next.md`; companion `07-cross-stop-synthesis-docs.md`. | This is one of v1's strongest outputs: it gives every Event a unique contribution, separates direct influence from parallel development and narrative convergence, preserves all six Events, produces four coherent Sections, and prevents a false linear history. | Stable relationship and Section IDs, Source-linked relationship records, an explicit event-centric versus argument-centric comparison, assignment checks, formal visual-claim constraints, and a durable Human direction decision when needed. | Whether the live run reaches the same or a better thesis/structure; relationship traceability; accidental-causality findings; Event assignment continuity; and Human approval effort. |
| 08 — Narrative draft | `partial` | `v1@811c52b/08-narrative-draft-output.md`; continuation rationale `08-narrative-draft-whats-next.md`; companion `08-narrative-draft-docs.md`. | A complete, coherent reader-facing draft carries the six Events through four Sections, maintains parallel rather than invented causal development, and makes every stop advance the route argument rather than read as an isolated venue biography. | Stable Event/Section identity, explicit structure choice, an Event-to-Section completeness check, drafting notes for risky claims, and a clean separation between route identity and narrative grouping. | Reader clarity, Event retention, section logic, claim drift introduced during drafting, length, and the amount of repair required in step 09. |
| 09 — Evidence review | `partial` | Review method at `v1@811c52b/09-evidence-review-whats-docs.md`; corrected copy at `09-evidence-review-whats-output.md`; continuation rationale `09-evidence-review-whats-next.md`. | V1 defined a careful claim-level audit method and produced a corrected six-Event draft with softened boundaries and causality. It understood that transitions and vivid prose are evidence risks. | A separate durable `09-evidence-audit.md` containing one stable record per material claim, exact passage ownership, supporting/contrary Sources, action, unresolved materiality, Human decision, and traceability into the corrected draft. | Number and type of claim corrections; whether the audit is independently inspectable; unresolved claims; Human decisions; and whether corrected copy can be traced back to evidence. |
| 10a — Final route copy | `partial` | Combined output `v1@811c52b/10-final-route-copy-and-map-presentation-output.md`; companion `10-final-route-copy-and-map-presentation-docs.md`; continuation rationale `10-final-route-copy-and-map-presentation-whats-next.md`. | Concise final copy preserves the evidence-aware six-Event argument, improves reader rhythm, and retains necessary qualifications such as rejecting a single birthplace or inevitable endpoint. | A separate copy artifact with stable final-stop/Section records, explicit length targets and compression notes, protected meanings, and a recorded Human copy decision independent of presentation approval. | Length and clarity, retained qualifications, compression losses, evidence drift, Human acceptance, and whether separating copy from presentation improves review. |
| 10b — Presentation and visual claims | `partial` | Presentation half of `v1@811c52b/10-final-route-copy-and-map-presentation-output.md`; companion `10-final-route-copy-and-map-presentation-docs.md`. | A strong progressive map treatment communicates one room, simultaneous 1974 nodes, a record network, and convergence. It explicitly prohibits a continuous route line that would invent causality. | Inspection of current SoundAtlas implementation and documentation; separate current-capability and future-proposal layers; stable presentation records; evidence-linked claims; media rights/availability and accessibility; and separate Intake routing for product gaps. | Historical meaning communicated by each map state; feasibility in the current product; prohibited implications caught; media/rights readiness; accessibility; and product gaps exposed. |
| 11 — Run evaluation | `partial` | `v1@811c52b/11-procees-review.md`. | A substantial retrospective identifies v1's strengths, compression bias, early candidate constraint, late media work, missing product-model inspection, map risks, Human-gate needs, and reusable prompt/schema recommendations. It also records the final shape as six Events in four Sections and directly informed baseline-1.1. | Starting/terminal run state, executed/skipped stages, elapsed time, actual Human decisions and retries, checkpoint counts, schema/ID audit, remaining editorial/publication work, structured Human assessment, and explicit method-finding classifications. | Comparable time/count/decision evidence; observed versus remembered intervention; schema continuity; historical and experiential result; and which method changes are reusable after a live run. |
| Shared output schemas | `missing` | No stable cross-stage schema artifact or stable object IDs appear in the v1 files. The retrospective proposes fields in `v1@811c52b/11-procees-review.md`, but they were not used during the run. | Prose tables preserve many useful fields locally, and repeated Event names allow a Human reader to infer continuity. | Stable Candidate, Event, relationship, Section, claim, final-stop, and presentation IDs; explicit Source links; status history; and `unknown`/`not-assessed` rather than silent omission. | Missing fields, ID continuity, unexplained transitions, traceability across stages, and the cost of producing and reviewing structured records. |

## Reconstructable progression

The v1 funnel can be reconstructed at major checkpoints, but not as a complete
Candidate ledger:

| Checkpoint | Observable count and change | Limitation |
| --- | --- | --- |
| Topic discovery | Eight topics; Yiddish Broadway, Harlem-to-salsa, and underground Disco recommended for investigation. | The Human selection of Disco is evident from the next artifact but is not recorded as a decision record. |
| Concept framing | Three thesis options and two developed narrative arcs. | The output announces a possible next comparison of three concepts but does not contain that comparison or the Human arc decision. |
| Light test | Seven named Candidates. | No stable IDs; statuses exist only in this table. |
| Gap research | Ten Candidate rows after additions, retentions, optional treatment, and proposed removals. | Bundled entries such as Ginza/La Martinique and changed omissions prevent a trustworthy one-object-per-row history back to step 03. |
| Cohort decision | Six core Events; five named cut/context/reserve groupings. | It is not possible to prove a complete status transition for every earlier Candidate. The output is clear about the chosen core but not a normalized full landscape. |
| Deep research through final copy | Six Events retained. | Names, not stable IDs, carry identity. |
| Synthesis through final copy | Four narrative Sections contain those six Events. | Section identity and revisions are not machine-traceable. |

## What v1 did well

V1 set a meaningful editorial standard that baseline-1.1 should preserve:

- evidence repeatedly changed the thesis instead of merely confirming it;
- the light test detected representation bias before full research;
- targeted research introduced community agency and non-venue infrastructure;
- the minimum-core test gave every retained Event a necessary role;
- deep research narrowed Event boundaries and kept uncertainty visible;
- synthesis clearly separated documented influence, parallel development, and
  narrative convergence;
- the draft remained an argument rather than six disconnected biographies;
- evidence review softened origin, boundary, and causal claims; and
- presentation logic carried historical meaning and explicitly rejected a map
  line that would misrepresent the evidence.

These strengths explain why every substantive stage is `partial`, rather than
`missing`: baseline-1.1 mostly strengthens control, comparison, and
traceability around a productive v1 editorial process.

## Material v1 gaps

The main gaps are process evidence, not proof that the resulting route is poor:

- no run brief, version identity, stage status, or terminal state;
- no durable record of actual Human choices, approvals, retries, or stop points;
- no stable IDs or normalized status history across Candidate, Event,
  relationship, Section, claim, and presentation layers;
- no verified coordinate-backed spatial comparison at the light-test stage;
- a one-way compression step without a distinct enrichment/challenger pass;
- deep research of the selected core without an equally researched challenger;
- historical confidence and media/experience readiness were not independent;
- no separate, inspectable evidence-audit artifact;
- final copy and presentation were combined, and presentation did not inspect
  the implemented SoundAtlas capability;
- no elapsed-time evidence or complete checkpoint counts; and
- no explicit account of the remaining work needed for current editorial review
  and publication readiness.

## Observable Human intervention

The artifact sequence proves that the route direction changed to Disco after
step 01 and that later stages continued. It does not prove who made those
decisions or how. The process review responds to Human observations about route
size, product fit, and media, and recommends five future gates. It does **not**
durably record which v1 outputs were approved, what alternatives the Human
considered, whether a stage was retried, or how long decisions took. Those
facts must remain `unknown`; they should not be inferred from the existence of
the next file.

## Comparison contract for the live Disco run

The later baseline-1.1 run should compare process evidence against v1 at the
same material checkpoints, without requiring it to reproduce v1's historical
conclusions:

1. Record the starting scope, inherited v1 evidence, route-length hypothesis,
   executed/skipped stages, elapsed time, Human decisions, retries, and terminal
   status.
2. Preserve Candidate counts and status transitions at steps 03, 04, and 05;
   Event counts after step 06; and Section counts after step 07.
3. Compare thesis changes, representation corrections, geographic findings,
   Source gaps, Event-boundary changes, and claim corrections with the v1
   evidence above.
4. Test whether enrichment/challenger work changes v1's six-Event minimum core
   or improves the route without losing its argument.
5. Evaluate historical-evidence confidence separately from media/experience
   readiness and record the work needed for editorial and publication review.
6. Compare narrative clarity, Event uniqueness, relationship accuracy, map
   meaning, current-product feasibility, and Human review effort.
7. Audit stable ID continuity and whether decisions remain traceable from
   Candidate through final copy and presentation.

The live run's step 11 evaluation may then recommend `reusable`,
`topic-dependent`, `merge`, `parallel`, `reject`, or `unresolved` findings.
This crosswalk intentionally makes none of those final method decisions.
