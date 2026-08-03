# Content Pipeline Interaction Contract

## Purpose

This document is the normative interaction contract for agent-assisted route
generation and future admin review in SoundAtlas. It defines how people inspect
pipeline results, make the smallest necessary editorial decisions, understand
pipeline provenance, and approve a route for publication.

The contract describes the target interaction model. It does not claim that
every behavior is implemented today. Each requirement is marked `Current`,
`Partial`, or `Future` so planning and implementation do not confuse intended
behavior with current capability.

SoundAtlas should begin with a small, human review loop, not an admin platform:
preview the story, choose what belongs, notice the warnings, and publish the
route.

For the no-user MVP, publication uses one fixed-scope review. The review must
show enough read-only context for an informed decision, but it is a policy and
handoff boundary rather than a dashboard or generalized content-management
surface.

## Authority And Boundaries

This contract owns interaction requirements for pipeline review. It does not
own historical judgment, source-quality rules, media approval rules, route-entry
map presentation, or runtime data shapes.

- `editorial-workflow.md` owns the currently implemented editorial flow.
- `event-editorial-quality-standards.md` owns event prose, route fit, claim, and
  source-discipline guidance.
- `accepted-event-dossier-template.md` owns the current accepted-event handoff.
- [Issue #70](https://github.com/gititinyoursoul/soundatlas/issues/70) owns the
  future map presentation and data model for heterogeneous route entries.
- [Issue #71](https://github.com/gititinyoursoul/soundatlas/issues/71) owns the
  future pipeline implementation of the two-gate cascade defined here.
- [Issue #73](https://github.com/gititinyoursoul/soundatlas/issues/73) owns the
  future publication review, approval action, and publication-state behavior.
- [Issue #77](https://github.com/gititinyoursoul/soundatlas/issues/77) owns the
  later transition from draft-visible seed content to route-approved-only
  public content.

When this target contract differs from current pipeline behavior, the current
workflow documentation remains descriptive of what the software does until the
corresponding implementation Issue is completed.

## Terminology

- **Pipeline run:** one execution for a route with identifiable model, prompt
  or rule version, pipeline version, and timestamp.
- **Review preview:** a navigable representation of generated route content
  before event selection. It is review material, not runtime seed or published
  content.
- **Event proposal:** an event presented for a route-scoped Yes/No decision.
  Issue #70 may later define a broader route-entry data model without changing
  the interaction principle.
- **Warning or flag:** an unresolved editorial, source, place, media, or claim
  concern shown to the human. It does not block MVP publication by itself.
- **Technical error:** structurally invalid data or a failed reference that the
  software cannot process safely. It may stop execution but is not a human
  editorial gate.
- **Active working state:** the run currently used for ongoing work.
- **Archived run:** an earlier, read-only run and its intermediate results.
- **Publication review:** one route-level view of selected content and all
  unresolved warnings before final approval. For the MVP, it identifies the
  exact route result, lists every selected entry with essential context, keeps
  warnings connected to what they affect, shows technical readiness, and
  offers one publish action.
- **Publication authorization:** the human decision to make the complete route
  public with its warning state visible. Initial authorization uses the
  publication review and publish action. A later authorized human edit is
  itself renewed publication authorization.

## Target Cascade

```text
CLI starts route pipeline run
  -> navigable review preview
  -> human gate 1: Yes/No for each event
  -> selected events continue through draft processing
  -> warnings and technical diagnostics remain visible
  -> publication review
  -> human gate 2: approve the complete route for publication
```

The cascade has exactly two human gates. Internal statuses, quality checks,
warnings, and diagnostics must not silently become additional approval steps.

## Interaction Requirements

### Minimal Human Decisions

| ID | Support | Requirement |
| --- | --- | --- |
| `CPI-R1` | Future | The normal route-selection decision is one Yes/No decision per event proposal. |
| `CPI-R2` | Future | Yes continues the event through downstream draft processing for the current route. |
| `CPI-R3` | Future | No stops downstream processing for the current route without deleting the proposal, its decision history, or its potential use in another route or later run. |
| `CPI-R4` | Future | Final publication is one explicit, human-only decision for the complete route. |
| `CPI-R5` | Partial | Agent suggestions, diagnostics, human decisions, draft state, and publication approval must remain visibly distinct. Current artifacts distinguish some of these states, but the complete interaction is not implemented. |

Special editorial cases may have detailed internal states or recommendations.
Their meaning belongs to the editorial workflow; they must not expand the
normal Yes/No decision surface without a separately approved requirement.

### Review Preview

| ID | Support | Requirement |
| --- | --- | --- |
| `CPI-R6` | Future | The human can navigate the generated route result before making event decisions. |
| `CPI-R7` | Future | The preview is unmistakably labeled as generated review material and cannot be mistaken for published or approved seed content. |
| `CPI-R8` | Future | Map, timeline, route, and story navigation use one shared preview selection state. Detailed route-entry presentation and data shape are delegated to Issue #70. |

### Warnings And Publication

| ID | Support | Requirement |
| --- | --- | --- |
| `CPI-R9` | Future | Missing or weak sources, unresolved claims or merges, uncertain place or time data, unreviewed media or images, and other unresolved editorial risks appear as warnings or flags for the MVP rather than technical publication blockers. |
| `CPI-R10` | Future | The publication review identifies the exact route result using the minimum run context from `CPI-R18`, lists every selected route entry with its title and essential place/time context, associates every entry-specific warning with the affected entry, shows route-level warnings separately, and shows technical readiness distinctly from non-blocking editorial warnings. |
| `CPI-R11` | Future | Initial publication uses one explicit, human-only route-level approval after the publication review is shown. Approval records publication authorization for the complete route with the warning state then displayed; it does not state that warnings were resolved. A later authorized human edit is itself renewed publication authorization and remains approved without another publish action. |
| `CPI-R12` | Current | Structurally invalid data or failed or unresolved references may stop technical execution independently of editorial warning policy. |
| `CPI-R25` | Current | Until Issue #77 is implemented, the public explorer may display any runtime seed content, including records marked as drafts; record-level review status is not a route-publication filter. |
| `CPI-R26` | Future | Automatic processes cannot alter approved content or treat an automatic change as renewed publication authorization. |

Warnings inform human judgment. They must not be hidden, automatically
resolved, or treated as human approval. Publication approval does not convert a
warning into a statement that the underlying concern was corrected.

The fixed-scope MVP publication review presents:

- **Route and result identity:** the route plus the model, prompt or
  editorial-rule version, pipeline version, and timestamp required by
  `CPI-R18`, so the human can verify the exact result under review.
- **Selected content:** a compact list of every selected route entry, including
  its title and essential place/time context. Uncertain place or time details
  remain visible as warnings rather than being presented as false precision.
- **Editorial warnings:** each entry-specific warning appears with the affected
  entry, while route-level warnings appear separately. Together they expose
  every unresolved warning for the complete selected set.
- **Technical readiness:** structural validity and reference failures are shown
  separately from editorial warnings. A technical error may prevent the
  publish action; an editorial warning does not.
- **Publication decision:** one action publishes the complete route.

The review may organize warnings by the entry they affect, but it does not turn
them into a management workflow or ask the human to resolve, categorize,
filter, or acknowledge them individually. It provides no dashboard, roles,
editing tools, recommendations, or automated approval. Candidate selection,
downstream draft processing, and route publication remain distinct states even
while the temporary `CPI-R25` policy allows drafts to appear in the public
explorer.

Initial publication records the human decision made after this complete review
is shown. If an authorized human later edits approved content, that edit itself
renews publication authorization for the edited content and its then-current
warning state. This is a policy rule, not an authentication or audit-system
requirement. Automatic processes receive no equivalent authority and cannot
change approved content.

### CLI And Admin Responsibilities

| ID | Support | Requirement |
| --- | --- | --- |
| `CPI-R13` | Current | Pipeline runs are started through the CLI for the MVP. |
| `CPI-R14` | Future | The admin experience presents the navigable review result and records event-level Yes/No decisions. |
| `CPI-R15` | Future | The admin experience presents the route-level publication review and records the final publication decision. |
| `CPI-R16` | Future | Starting, configuring, skipping, or rerunning pipeline steps is not required in the MVP admin experience. Corrections and reruns remain CLI operations. |

### Pipeline Transparency

| ID | Support | Requirement |
| --- | --- | --- |
| `CPI-R17` | Partial | Each pipeline step exposes its purpose, input, and output. Current commands expose artifacts, but not yet through one consistent review surface. |
| `CPI-R18` | Future | A review result shows its route, model, prompt or editorial-rule version, pipeline version, and timestamp. |
| `CPI-R19` | Future | Pipeline output may report facts, changes, uncertainties, risks, and diagnostics, but the human decides whether the result is better. |

The pipeline must not present its own output as improved merely because a later
step or newer model produced it.

### Run Archive

| ID | Support | Requirement |
| --- | --- | --- |
| `CPI-R20` | Future | Pipeline runs and their intermediate results remain inspectable as read-only archived records after the active working state is replaced. |
| `CPI-R21` | Future | Archived runs cannot be edited or resumed directly. The active working state may be replaced by a later run. |
| `CPI-R22` | Future | Archive storage technology and retention policy are implementation decisions and are not defined by this contract. |
| `CPI-R23` | Future | Archives must exclude secrets, credentials, audio, video, and other media binaries. External media links may remain part of textual or structured artifacts. |
| `CPI-R24` | Future | Comparing or diffing separate runs is outside the MVP interaction contract. Runs may be inspected separately. |

## Current And Future Support Summary

| Capability | Current support | Target owner |
| --- | --- | --- |
| Start a route pipeline run through the CLI | Current | Existing pipeline workflow |
| Inspect route-folder draft artifacts | Current | Existing editorial workflow |
| Distinguish candidate, accepted, and draft data | Partial | Existing workflow; revised cascade in Issue #71 |
| Navigate a pre-approval route preview | Future | Issues #70 and #71 plus future admin work |
| Record route-scoped event Yes/No decisions | Future | Issue #71 plus future admin work |
| Show the fixed-scope publication review and approve the route | Future | Issue #73 |
| Display draft seed content in the public explorer | Current temporary policy | Issue #77 owns the approved-only transition |
| Protect approved content from automatic changes | Future | Issues #71 and #73 implementation boundaries |
| Inspect immutable archived runs and intermediate results | Future | Follow-up storage and admin implementation |
| Compare separate pipeline runs | Out of MVP scope | Unplanned |

## Acceptance Criteria

| ID | Contract acceptance condition |
| --- | --- |
| `CPI-AC1` | The interaction exposes exactly two human gates: event-level Yes/No and one final route-level publication approval. |
| `CPI-AC2` | No stops an event only for the current route cascade and does not delete its record or broader reuse potential. |
| `CPI-AC3` | The pre-approval preview is navigable and clearly separated from accepted, seed, and published content. |
| `CPI-AC4` | Editorial concerns are presented as visible MVP warnings without creating per-warning approval steps. |
| `CPI-AC5` | Technical execution errors remain distinct from editorial warnings and human gates. |
| `CPI-AC6` | CLI execution and future admin review responsibilities are explicit. |
| `CPI-AC7` | Every review result exposes the minimum run context defined by `CPI-R18`. |
| `CPI-AC8` | Pipeline steps expose purpose, input, and output without judging their own improvement. |
| `CPI-AC9` | Archived runs and intermediate results are inspectable and read-only, while storage technology remains unspecified. |
| `CPI-AC10` | Every requirement states whether support is current, partial, future, or outside MVP scope. |
| `CPI-AC11` | Map presentation/data modeling and pipeline implementation remain owned by Issues #70 and #71 respectively. |
| `CPI-AC12` | The contract contains no requirement to compare or diff separate pipeline runs for the MVP. |
| `CPI-AC13` | One fixed-scope publication review identifies the exact route result, lists every selected entry with essential place/time context, associates warnings with affected entries or the route, distinguishes technical readiness, and offers one publish action without adding management workflows or extra human decisions. |
| `CPI-AC14` | Initial approval and later authorized human edits preserve publication authorization with the warning state then present, while automatic processes cannot alter approved content or grant authorization. |
| `CPI-AC15` | The temporary public policy permits draft seed content until Issue #77 implements route-approved-only visibility. |

## Follow-Up Boundary

This contract authorizes no runtime behavior by itself. Implementation work
must use separately approved Issues and preserve the current workflow until the
replacement behavior is implemented and verified.

Issue #71 should implement the two-gate pipeline cascade. Issue #70 should
define how heterogeneous route entries are represented across the map,
timeline, and story experience. Issue #73 should implement the publication
review, approval action, and publication-state behavior. Issue #77 should
replace the temporary draft-visible policy with route-approved-only public
content. These Issues should cite the relevant `CPI-R*` and `CPI-AC*` IDs
rather than copying this contract.
