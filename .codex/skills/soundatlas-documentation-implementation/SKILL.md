---
name: soundatlas-documentation-implementation
description: Plan and implement approved SoundAtlas documentation changes by classifying source-of-truth relationships, discovering related references, preserving documentation boundaries, validating consistency, and reporting the result.
---

# SoundAtlas Documentation Implementation

This retained entrypoint supplies SoundAtlas requirements for approved
documentation and workflow-document changes. The runtime selects suitable
implementation capabilities and execution mechanics; ordinary repository/GitHub
tools may fulfil them. Issue planning remains with `soundatlas-issue-planning`.

Use the registry's [implementation and review composition](../../../docs/workflow-registry.md#implementation-and-review-composition)
for authority inputs, readiness, allowed effects, evidence and stop routes,
and its [documentation consistency](../../../docs/workflow-registry.md#documentation-consistency)
rules for classification and bounded reference discovery. When Pane is selected,
use the existing composition contract there. This skill does not prescribe or
copy a provider's editing/reporting procedure.

## Required authorities and context

- `AGENTS.md`, `docs/workflow-registry.md` and
  `docs/github-issue-workflow.md` for repository constraints and lifecycle gates.
- The current approved Issue and confirmed decisions, Concept or
  Concept-not-required basis, latest Plan and matching Proceed when required,
  exact named paths and audited derived files, exclusions and allowed effects.
- The target document's classification and authoritative owner, directly
  related documents, active references, compatibility wrappers and discovery
  consumers within the approved boundary.
- Applicable domain authorities and project execution/environment rules;
  distinguish planning, approved implementation, audit and archive outputs.

## Required outcome and evidence

Preserve source ownership, terminology, history and canonical gates while
making the smallest approved change. Derived alignment must be mechanical and
limited to the Proceed audit. Application, seed, API, deployment and production
changes require their own explicit approved scope.

Return the source-of-truth classification, owners and related references
actually checked, exact changed files and derived-file list, criteria coverage,
and actual `git diff --check` and `python scripts/check_doc_references.py`
results. Include any additional formatting/schema/domain checks required by
the Issue, scope audit, unavailable or partial execution, risks and unresolved
decisions. These results support only the claims the checks establish.

`soundatlas-implementation-review` supplies the completed comparison and
`soundatlas-issue-planning` composes the single Issue Implementation Report
including its Review Result. Commit and delivery gates remain with the
lifecycle. Preserve this path and discovery manifest until the separate #203
retirement gate.
