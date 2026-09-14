# Pane Workspace Runtime Target Principles

## Status and purpose

This document records the current target direction confirmed in
[#241](https://github.com/gititinyoursoul/soundatlas/issues/241). Milestone 10
should prove a minimal, project-neutral Pane Workspace Runtime. It should not
build a Development Platform or prepare a shared control plane without a
demonstrated current need.

The earlier Development Platform principles, architecture evaluation, and
C-compatible migration design remain useful historical evidence. Their
Candidate C and future-contract direction is not a requirement for this target.

## Target outcome

An existing Git repository can be attached to a Pane-managed isolated
workspace, with Codex and the minimum common development capabilities available
inside that workspace. Codex lifecycle and supported-version ownership are
project-neutral rather than coupled to a consuming repository. Runtime and
repository identity are explicit, required capability failures are visible,
and the generic path contains no project names, services, ports, workflow
stages, model policy, or setup logic.

The target must be validated with SoundAtlas and one independent
non-SoundAtlas repository. This is bounded evidence that the runtime is not a
renamed SoundAtlas environment; it is not proof of compatibility with every
possible repository.

SoundAtlas and the second repository must remain usable without Pane. A project
may add tooling it needs without modifying or forking the generic base runtime.
The representation of that extension is a later planning choice.

## Responsibility boundary

| Owner | Responsibilities | Boundary |
| --- | --- | --- |
| Pane Workspace Runtime | Isolated workspace lifecycle; exact repository/worktree attachment and identity; project-neutral Codex lifecycle and supported-version/compatibility ownership; an empirically justified common tool minimum; explicit runtime and capability status; actionable failure reporting; generic credential-injection and network/egress mechanisms; continuity state required to avoid identity or necessary tool-state loss. | It does not interpret project meaning, choose requested credential scopes or network destinations, or define project workflows and services. |
| Project | Application dependencies and additional toolchains; build, test, and validation commands; services and ports; preview and browser requirements; requested credential scopes and network destinations; repository and workflow policy; model and agent roles; independently usable non-Pane guidance. | Project requirements may consume or extend generic capabilities but must not become base-runtime defaults. |
| Human/operator | Credential values and grants; authorization of requested access; host and runtime security decisions; destructive cleanup; migration, integration, push, and other protected decisions. | Technical capability never implies Human authorization. |

The runtime implements reusable credential-injection and network-enforcement
mechanisms. Project configuration declares what access is requested, and the
Human/operator authorizes it. Missing or unsupported required capabilities must
fail visibly rather than silently widening access or substituting a project
default.

## Target principles

1. Deliver a workspace runtime, not a Development Platform.
2. Keep the base project-neutral.
3. Keep project meaning, policy, dependencies, services, and validation with
   the project.
4. Keep every project independently usable without Pane.
5. Allow projects to extend the runtime without modifying or forking the base.
6. Persist only state required for identity or necessary continuity;
   rebuildable caches are optional.
7. Add abstractions only after SoundAtlas and another repository demonstrate
   the repeated need.

## Evidence boundary

The bounded proof should establish:

- start, stop, and restart behavior with unambiguous workspace and repository
  identity;
- exact repository/worktree attachment;
- Codex, shell, and source-control operation through the common runtime;
- credential and network capability results without exposing secret values or
  weakening an existing boundary;
- necessary persistence and recovery behavior;
- absence of SoundAtlas names, services, ports, workflow stages, model policy,
  and setup assumptions from the generic path;
- project-owned extension behavior only where a repository demonstrates the
  need; and
- ordinary non-Pane development for both proof repositories.

Relevant evidence from the broader capability and security investigations may
be reused. Their complete scope is not a Milestone 10 gate. An unresolved
credential, egress, privilege, or security fact blocks only the affected test
unless evidence shows that it invalidates the runtime target.

## Non-goals

- A Development Platform or Candidate C shared control plane.
- A generic project-definition schema or final Project ↔ Platform contract.
- An agent-provider abstraction, model router, workflow engine, or plugin
  architecture.
- Generalized preview, artifact, CI, or deployment infrastructure.
- A mandatory project-specific development image.
- A runtime implementation delivery lane, package layout, extension format, or
  persistence mechanism selected by this document.

## Questions deferred until multi-project evidence exists

- Whether a shared control plane provides enough demonstrated value.
- Whether repeated project declarations justify a contract, schema, API, or
  extension format.
- Whether more than Codex creates a real need for an agent-provider boundary.
- Whether repeated preview, artifact, cache, service, credential, or network
  needs justify generalized infrastructure.
- Whether multi-user administration, workflow automation, or scale needs exist.

## Historical evidence

- [Development Platform Target Principles](development-platform-target-principles.md)
  preserves the ownership principles derived from the #209 coupling audit.
- [Development Platform Runtime Architecture Evaluation](development-platform-runtime-architecture-evaluation.md)
  preserves #208's candidate comparison and evidence gaps.
- [C-Compatible Per-Project Runtime Migration](development-platform-c-compatible-per-project-runtime-migration.md)
  preserves #237's separation, rollback, and second-project evidence analysis.

Those documents explain how the earlier direction was reached. The #241 Issue
record remains authoritative for the detailed triage and smallest-value
sequence under the corrected scope.
