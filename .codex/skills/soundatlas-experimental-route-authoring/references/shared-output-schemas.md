# Shared Output Schemas

Use these minimum records wherever the active stage creates or revises the
corresponding object. Markdown tables or repeated field blocks are both valid.
Use stable lowercase URL-safe IDs within one route version. Preserve an ID when
an object changes status; record `unknown` or `not-assessed` rather than omitting
a required field.

## Candidate record — steps 03–05

- `candidate_id`, title, and Event boundary;
- `date_start`, `date_end`, and date precision;
- place name, address or place reference, and verified coordinates when known;
- actors, historical mechanism, narrative role, and map role;
- evidence summary and claim-specific Source references;
- historical-evidence confidence;
- media/experience readiness;
- status, status reason, previous status, and changed-at stage; and
- open questions and material gaps.

## Event dossier — steps 06–10b

- `event_id`, assigned once at the first Event dossier, and originating
  `candidate_id`;
- title, Event boundary, dates and precision, place decision, and actors;
- documented facts separated from interpretation;
- route function, geographic significance, and supported claims with Sources;
- risky claims, non-claims, uncertainty, and historical-evidence confidence;
- media leads by type, relevance, Event linkage, availability, Source URL,
  rights status, and experience/media-readiness assessment; and
- current verdict and unresolved work.

## Relationship record — steps 07, 09, and 10b

- `relationship_id`, from/to Event IDs, and relationship type;
- claim communicated and `documented` or `interpretive-synthesis` basis;
- supporting or contrary Sources;
- uncertainty and prohibited stronger implication; and
- permitted narrative and visual treatment.

Use relationship types such as `documented-influence`, `parallel-development`,
`contrast`, `structural-link`, `convergence`, `chronology`, or
`interpretive-synthesis`. Chronology alone never proves influence.

## Narrative-section record — steps 07–10a

- `section_id`, title, historical question, and narrative function;
- ordered Event IDs and grouping rationale;
- order basis and accidental-causality check;
- transition into and out of the section; and
- presentation implication and unresolved claim gaps.

## Evidence-audit record — step 09

- `claim_id`, exact passage, and owning Event, relationship, or section ID;
- classification, supporting or contrary Sources, and confidence;
- correction action, corrected wording, and rationale; and
- unresolved materiality, owner, and required Human decision.

## Final-stop record — step 10a

- Event ID, stop title, date/place line, and narrative hook;
- final Event copy and route significance;
- preserved uncertainty or qualification;
- section ID and transition role; and
- deliberate compression and meaning presentation must not obscure.

## Presentation record — step 10b

- `moment_id` and owning section, Event, or relationship IDs;
- implemented map state and historical claim communicated;
- evidence basis and prohibited implication;
- visual/media treatment with availability and rights status;
- copy/presentation consistency and accessibility requirement; and
- unsupported future capability, when any, separated from the baseline need.
