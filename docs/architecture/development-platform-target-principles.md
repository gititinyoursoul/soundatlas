# Development Platform Target Principles

## 1. Purpose

This document offers non-binding principles for separating SoundAtlas project
responsibilities from reusable development infrastructure. Derived from the
[#209 coupling audit](https://github.com/gititinyoursoul/soundatlas/issues/209),
it is a reference for later evaluation, not a final architecture, contract,
schema, placement, or migration plan.

The scope is the environment in which a contributor or agent inspects, changes,
validates, or previews a SoundAtlas worktree, locally or remotely. CI and
deployed or production-like application environments are outside this scope.

**Pane** is the generic orchestration interface for repositories, worktrees,
panes, panels, and terminals; **RunPane** is its command-line interface. A
**native launch** starts an agent with Pane/RunPane's default command. A
**stage-routed launch** asks a SoundAtlas-owned launcher to construct and run an
agent command from project workflow policy. A future **Project ↔ Platform
boundary** would connect project declarations to
reusable capabilities; its final form and implementation owner remain open.

One #209 example shows why the boundary matters. SoundAtlas replaced the
Pane/RunPane default command to apply stage-specific model policy, so the repository
also became responsible for preserving unrelated launch behavior. The routed
launch omitted Codex's `--yolo` option until #233 corrected it. Without that
option, Codex requested interactive command approvals that the Pane default
launch avoided. A local policy extension had silently acquired generic launch
responsibility, producing user-visible behavioral drift.

## 2. Target Principles

- **Keep project meaning with the project.** SoundAtlas owns product and domain
  rules, application-service definitions, workflow stages and approval gates,
  model/effort/permission policy, repository identity, validation, and preview
  requirements. Reusable infrastructure executes declared requirements without
  interpreting or redefining them.
- **Keep reusable mechanisms project-neutral.** Generic orchestration,
  execution-environment packaging, isolation, transport, lifecycle mechanisms,
  tested component/version compatibility, secret injection, and network
  enforcement should not embed SoundAtlas repository names, services, workflow
  stages, or domain assumptions.
- **Judge responsibilities before placement.** Project policy and domain
  knowledge point toward SoundAtlas ownership; mechanisms that can serve
  multiple projects without project meaning point toward reusable ownership.
  Later work can use this distinction to compare whether a mechanism belongs in
  Pane/RunPane or in a separate reusable execution layer, and where either runs,
  without treating the component split as settled here.
- **Keep the handoff small and visible.** A future boundary could carry project
  identity, toolchain and service requirements, credential references, cache
  needs, and observable capability results. Its exact fields, failure semantics,
  and representation belong to later contract work.
- **Keep non-Pane contribution first-class.** Repository-owned guidance and
  commands should remain sufficient to understand, develop, validate, and
  preview SoundAtlas without Pane or generated Pane context.
- **Use evidence to compare proposals.** Compatibility, launch behavior,
  project isolation, service access, credentials, networking, recovery, and
  non-Pane operation are evidence categories for later evaluation, not gates
  defined by this document.

Authors and reviewers of #208, compatibility-baseline work, and later contract
proposals are the expected users of these principles. Their controlling issue—
the GitHub issue that records the work's scope and Human approval—or its linked
design artifact can summarize each applicable question, the evidence available,
and remaining unknowns. Those later efforts decide evidence thresholds,
exceptions, and whether a proposal is accepted.

Useful evaluation questions include:

- Does each responsibility have a clear project-policy or reusable-mechanism
  rationale, including where that responsibility stops?
- Does the candidate name the concrete components and artifacts it depends on—
  such as Pane, RunPane, Codex, a container image, or a launcher—and the tested
  versions of those items?
- For launch properties not intentionally changed by documented SoundAtlas
  policy, do native and stage-routed launches produce the same observable result
  for repository/worktree identity, command behavior, execution context,
  service access, readiness, and failure reporting? Are intentional model,
  effort, or permission differences documented and justified as project policy?
- Can a small disposable second repository, with a different identity and
  service declaration, use the same generic launch and repository/worktree
  listing behavior without copying SoundAtlas bootstrap or inheriting
  SoundAtlas defaults?
- Which claims have live compatibility or boundary evidence, and which remain
  assumptions for the later decision?

## 3. Provisional Responsibility Model

| Responsibility area | Recommended target outcome | Boundary still open |
| --- | --- | --- |
| SoundAtlas meaning | A target design would keep product/domain policy, workflow meaning, application-service definitions, project validation, and project-specific launch policy with SoundAtlas. | How those declarations are represented to reusable infrastructure. |
| Orchestration behavior | A target design would keep repository/worktree listing, pane, panel, terminal, and agent-launch behavior project-neutral. | Which behaviors Pane/RunPane implements directly and which depend on a separate reusable execution layer. |
| Execution mechanisms | A target design would make packaging, isolation, transport, persistence, component compatibility, secret injection, and network enforcement reusable across projects. | Which concrete artifact owns each mechanism and where it runs. |
| Project integration | A target design would let project configuration supply project requirements and consume observable results without reimplementing generic infrastructure. | The minimum future Project ↔ Platform boundary and its failure semantics. |

SoundAtlas owns whether an application service exists and how it behaves. A
reusable layer may provide a generic way to connect a declared service to a
development session; it should not hardcode that service as a platform default.

Human approval authority is separate from component ownership. Humans choose
architecture and placement, approve migrations, control secret values and
authorization, and authorize destructive actions; these decisions do not make
the Human an implementation layer.

#209 observed repository/live version differences and a failure while RunPane
decoded the list of existing Panes, but did not identify which component or
update caused that failure. At
the design level, it concluded that repeated coupling symptoms reflect
incomplete or unstable handoffs between project policy and reusable runtime
capabilities. These statements address different levels of causality and do not
select a final component boundary.

## 4. Non-Goals

This document does not select host versus container placement; define the final
Project ↔ Platform Contract, YAML/API schema, launcher, repository split, or
migration; move files; or change Pane, RunPane, Codex, containers, networking,
credentials, workflows, CI, preview services, deployment, or application
behavior. It does not reproduce the full #209 audit.

## 5. Open Questions and Assumptions

The split between Pane/RunPane and a separate reusable execution layer, generic
versus project-owned workflow concepts, minimum future integration boundary,
and placement-dependent responsibilities remain open.

Evidence gaps include a compatibility baseline for the concrete Pane, RunPane,
Codex, launcher, container image, or other runtime artifacts selected by a
candidate; native-versus-routed launch comparisons; host and out-of-repository
state; multi-project operation; credential and network boundaries; and
proportionate recovery evidence. These are inputs to later evaluation, not
assumed facts or requirements resolved here.

## 6. Relationship to Current and Later Work

[#209](https://github.com/gititinyoursoul/soundatlas/issues/209) is the evidence
base and detailed coupling map. [#233](https://github.com/gititinyoursoul/soundatlas/issues/233)
is a completed, bounded launch correction rather than proof of all launch
behavior. The compatibility-baseline work is an unnumbered follow-up proposed
in #209 and has no result yet. [#208](https://github.com/gititinyoursoul/soundatlas/issues/208)
and later Project ↔ Platform Contract work can use these principles to compare
options while retaining authority over their own evidence and decisions.
