# Development Platform Runtime Architecture Evaluation

## 1. Decision status and evidence discipline

This document records the architecture evaluation requested by
[#208](https://github.com/gititinyoursoul/soundatlas/issues/208). It recommends
a responsibility-placement direction for later design work; it does not
describe the current system, define the final Project ↔ Platform Contract, or
authorize implementation or migration.

The non-binding
[Development Platform Target Principles](development-platform-target-principles.md)
are the comparison criteria. The accepted
[#209 coupling audit](https://github.com/gititinyoursoul/soundatlas/issues/209#issuecomment-5621011312)
is the primary ownership and current-coupling evidence. This evaluation reuses
that audit rather than repeating it and expands a responsibility only where its
placement materially distinguishes the candidates.

Evidence statements use these labels:

- **Verified repository evidence:** observed in the current checkout at
  `deb2d118cc0dfbfb9063dab3809ddf2f034e6712`.
- **Verified lifecycle evidence:** an accepted Issue report whose reviewed
  commit is published on `origin/main`.
- **Accepted audit evidence:** an observation or conclusion accepted in #209.
- **Assumption:** a candidate property inferred from its proposed topology but
  not demonstrated here.
- **Evidence gap:** a fact needed to confirm or reject a material claim.

At this checkout baseline, the repository still pins Pane/RunPane `2.4.95` and
the Pane-specific Codex CLI `0.153.4`. #209 separately observed a live
Pane/RunPane `2.4.102` and Codex `0.154.0`, together with an inventory decode
failure. **Verified lifecycle evidence:** since that baseline,
[#235](https://github.com/gititinyoursoul/soundatlas/issues/235) and
[#236](https://github.com/gititinyoursoul/soundatlas/issues/236) completed and
published the reproducible Pane/RunPane `2.4.102`, Codex `0.154.0`, and npm
`11.19.1` pins with a fresh image build, recreation, and read-only runtime
health evidence. Those results establish the current versioned image baseline,
but not the full compatibility and launch contract. Likewise,
[#233](https://github.com/gititinyoursoul/soundatlas/issues/233) completed the
bounded `--yolo` correction, but did not prove full native versus stage-routed
launch parity.

No PoC was run for this evaluation. The material candidate-distinguishing
tests require host or RunPane operation, disposable runtime/repository creation,
or credential/network boundary work. Pane Chat owns already-authorized RunPane
interactions, and the approved #208 implementation scope authorizes only this
document and its index entry. The missing tests are therefore recorded as
bounded follow-ups rather than claimed as evidence.

## 2. Responsibility map before placement

Ownership in this table follows #209 and the Target Principles. It is defined
before any host, container, or shared-runtime location is selected.

| Responsibility | Required behavior and observable outcome | Owner and stopping boundary | Failure and recovery expectation | Evidence status |
| --- | --- | --- | --- | --- |
| Repository and worktree location | Select a project, create/list its worktrees, preserve exact worktree identity, and recover path-sensitive Git links after restart or replacement. | SoundAtlas owns repository identity and Git/delivery policy. Pane/RunPane owns generic repository, Pane, worktree, inventory, and archive semantics. A reusable runtime owns storage and path-mapping mechanisms, not project identity. | Ambiguous creation is not retried automatically. Recovery must rediscover every retained worktree and preserve Git common data before old state is removed. | **Accepted audit evidence:** current repositories and worktrees use persistent container storage; the inventory helper hardcodes `soundatlas`, and worktree links are path-sensitive. **Gap:** no host/container path-portability or shared multi-project recovery test. |
| Agent launch | Launch the requested agent in the exact worktree with stable native behavior, explicit SoundAtlas stage policy, truthful execution context, readiness, and failure reporting. | SoundAtlas owns stage names, model/effort/permission choices, and workflow authorization. Pane/RunPane owns generic panel/process lifecycle and native launch behavior. A reusable execution layer owns process provisioning. | Unknown stage, invalid policy, missing runtime, or unavailable execution context fails before launch; unintended native/routed differences are defects. | **Verified repository evidence:** `scripts/run_codex_stage.py` resolves project policy and requires a Pane workspace container; #233 restored one missing native behavior. **Gap:** complete launch parity and cross-boundary launch have not been tested. |
| Service attachment | Let a worktree reach only the application services and preview behavior declared by its project, without making unrelated planning or review depend on the full app stack. | SoundAtlas owns whether a service exists, its modes, and preview requirements. Reusable infrastructure owns a generic attachment and reachability mechanism, not service names or ports. | An absent or unhealthy service is reported for the affected task without corrupting the Pane or requiring unrelated services to start. | **Verified repository evidence:** `pane-egress` currently hardcodes `backend:8000` and `frontend:5173`, and Pane startup depends on them. **Gap:** generic per-project attachment and exact-worktree preview across runtime boundaries. |
| Credentials | Supply only the credential capability required by one project/session while keeping values and rotation under Human/secret-provider control and authorization separate from technical access. | SoundAtlas owns required scopes and delivery gates. A reusable runtime owns narrow injection and process provisioning. The Human/secret provider owns values, rotation, pairing, and revocation. | Missing credentials fail closed; rotation or revocation has a bounded restart path; project, Project Tracker, agent, and app credentials do not become ambient platform defaults. | **Accepted audit evidence:** the current entrypoint exports repository `GH_TOKEN` to descendants and seeds persistent Codex auth; separation is operational, not proven process isolation. **Gap:** [#226](https://github.com/gititinyoursoul/soundatlas/issues/226) has not produced the non-secret visibility matrix. |
| Networking | Enforce a reusable isolation/egress mechanism while accepting project-declared service exceptions and authenticated remote transport. | SoundAtlas owns required destinations and app-service exceptions. Reusable infrastructure owns enforcement, isolation, and transport mechanisms. The Human/operator owns host firewall and exposure decisions. | Required public and project service access remains available; private/host access does not widen silently; rule or namespace replacement fails closed and is recoverable. | **Verified repository evidence:** the sidecar mechanism is reusable but its destinations and lifecycle are SoundAtlas-coupled. **Gap:** [#227](https://github.com/gititinyoursoul/soundatlas/issues/227) and [#229](https://github.com/gititinyoursoul/soundatlas/issues/229) remain open. |
| Lifecycle and recovery | Create, start, stop, restart, upgrade, back up, restore, replace, and retire orchestration and execution state with clear ownership. | Pane/RunPane owns Pane/panel/worktree lifecycle semantics. A reusable runtime owns daemon, transport, persistent-state, and recovery mechanisms. SoundAtlas owns project acceptance checks. The Human owns destructive cleanup and migration approval. | Daemon, SSH/pairing, repository, worktree, auth, and cache state are distinguished; persistent state is preserved until replacement is proven; broad volume deletion is never a rollback. | **Accepted audit evidence:** current state spans independent named volumes, and restart was exercised. **Gap:** backup/restore, replacement, downgrade, path repair, pairing recovery, and shared-runtime failure isolation. |
| Version compatibility | Name and test a supported tuple across Pane, RunPane, agent runtime, launcher, image, container engine, and compatibility controls. | Reusable runtime distribution owns the tested generic tuple and upgrade/rollback gates. SoundAtlas owns only tool versions required by its application or workflow policy. | Mismatch fails visibly; the last reviewed tuple/image remains available; no global fallback hides an invalid project launcher or platform update. | **Verified and accepted evidence:** repository/live version authorities diverged, and deterministic fixtures passed while live inventory failed. **Gap:** no completed supported tuple, native/routed smoke matrix, or upgrade/downgrade proof. |
| Non-Pane contribution | Let a contributor understand, develop, validate, and preview SoundAtlas from repository-owned guidance and commands without Pane or generated Pane context. | SoundAtlas owns its commands, documentation, validation, and workflow meaning. Pane may orchestrate those capabilities but cannot become their sole definition. | Pane absence degrades orchestration only; normal repository workflows remain discoverable and independently usable. | **Verified repository evidence:** project commands and policy live in the repository. **Gap:** no explicit parity exercise across all development and preview capabilities; #229 owns the broader capability matrix. |

The ownership map deliberately does not equate reusable ownership with host
placement. A generic mechanism may run on the host, in one shared runtime, or
in an isolated project environment without changing who owns its meaning.

## 3. Candidates

### Candidate A: host control plane, project-container execution

Pane/RunPane and generic remote access run on the host. The canonical project
checkout or a host-visible worktree is mapped into a project container. A
generic adapter launches the agent in that container and attaches it to
project-declared services; project tools and agent credentials remain scoped to
the project execution environment.

This topology deduplicates the control plane and keeps project toolchains
containerized. Its decisive assumption is that Pane/RunPane can preserve
repository/worktree identity, native launch semantics, liveness, terminal
interaction, and failure reporting while the actual agent process runs across
the host/container boundary. That capability is not established by current
evidence.

### Candidate B: per-project containerized runtime

Each project instantiates its own Pane/RunPane daemon, remote transport,
repository/worktree storage, and agent runtime in its project environment.
Generic image and lifecycle implementation can be extracted from SoundAtlas,
but the project instance remains the control and execution boundary.

This is closest to the current validated shape and gives direct worktree,
toolchain, service, and process locality. It also preserves the root coupling
symptom identified by #209: every project carries separate daemon, pairing,
SSH, state, ports, upgrades, and recovery, even if their implementation comes
from a reusable package.

### Candidate C: shared project-neutral platform runtime

One reusable containerized platform runtime owns Pane/RunPane, authenticated
transport, compatible agent/runtime packaging, generic lifecycle, and
project-neutral repository/worktree inventory. Each project supplies its own
identity, workflow policy, toolchain and service requirements, credential
references, network exceptions, cache policy, and validation commands.
Execution occurs in an isolated per-project environment attached to that
shared control plane; SoundAtlas-specific defaults do not enter the shared
runtime.

This candidate reuses the strongest proven property of the current system—a
dedicated containerized Pane runtime—while removing the requirement that every
repository package and operate a complete control plane. The exact declaration,
attachment protocol, storage mapping, and failure semantics are intentionally
left to later Project ↔ Platform Contract work.

## 4. Common comparison

| Criterion | Candidate A: host control / project execution | Candidate B: per-project runtime | Candidate C: shared platform runtime |
| --- | --- | --- | --- |
| Responsibility alignment | **Assumption:** can keep policy in the project and generic control on the host, but a launch adapter becomes a critical boundary. | Reusable packaging can be separated, but project configuration still instantiates generic daemon and transport lifecycle. | Best structural match: project meaning remains project-owned while generic orchestration and runtime mechanisms have one neutral owner. |
| Repository/worktree identity | Requires a stable host-to-container path mapping and agreement on the canonical Git location; untested. | Direct locality is already evidenced, but each project owns separate persistent repository state. | One neutral inventory can serve multiple projects, but isolated execution must preserve canonical paths or explicit mappings; untested. |
| Agent launch | Requires cross-boundary process, terminal, environment, readiness, and failure parity; current `--tool-command` evidence does not prove it. | Lowest launch-path change and strongest current evidence; nevertheless project launch replacement already drifted from native behavior in #233. | Can centralize launch compatibility while applying project declarations at the execution boundary; the generic attachment and parity contract remain gaps. |
| Service attachment | Naturally keeps agents beside project services, but host control must discover and attach the correct container/network without project hardcoding. | Direct access is simple, but current Pane lifecycle is coupled to SoundAtlas services even for tasks that do not need them. | Can make service attachment opt-in per project/session and keep control-plane health independent; no live generic attachment evidence exists. |
| Credentials | Could keep agent secrets out of the host control plane, but adapter authority and host-visible repository credentials require proof. | Current credential behavior is known operationally but same-UID visibility and per-project duplication remain unresolved. | Offers one generic injection mechanism with project/session scoping, but isolation and rotation must be proven before sharing the runtime. |
| Networking | Separates host control transport from project execution egress, at the cost of two boundaries and host policy dependencies. | Existing sidecar is evidenced but hardcodes project services and couples restart. | Can separate control transport from namespaced per-project egress and service exceptions; enforcement and failure isolation are unproven. |
| Lifecycle/recovery | One control plane reduces duplication, but host state and container/worktree coordination create a new recovery seam. | Most familiar rollback: retain existing volumes and runtime. Recovery and upgrade work is repeated for every project. | One generic lifecycle reduces duplication; it also increases the importance of tenant isolation, backup/restore, and failure containment. |
| Version compatibility | Host Pane, adapter, project image, and agent runtime add a cross-boundary tuple. | Smallest immediate tuple, though current repository/live skew shows it is not yet controlled. | Centralizes the generic tuple while allowing declared project toolchains; shared upgrades require compatibility and rollback gates. |
| Non-Pane contribution | Preserved if project containers and commands remain independently usable. | Preserved if Pane-specific setup remains optional rather than defining project commands. | Preserved by design: the platform consumes project requirements while repository commands remain independently usable. |
| Multi-project reuse | One host control plane is promising, but each project's adapter, path, services, and credentials must work without copied bootstrap; no second-project proof. | Reusable code is possible, but runtime, remote access, pairing, ports, and state are duplicated per project. | Directly targets one neutral capability with isolated project declarations; no second-project proof yet. |
| Operational burden | Removes per-project control planes but adds host installation, host upgrades, and cross-boundary diagnostics. | Lowest migration effort, highest continuing duplication and project-owned operations. | Removes per-project control-plane duplication without requiring agent tooling on the host; requires a new shared-runtime operating and isolation model. |
| Evidence maturity | Low for the decisive host/container adapter and host recovery behavior. | Highest current runtime evidence, but it evidences the coupling that #208 is meant to address. | Medium: current dedicated-runtime mechanics are relevant, while shared and multi-project behavior remain assumptions. |

### Material multi-project criterion

A candidate is reusable only if one disposable second repository with a
different identity, toolchain, and service declaration can use the same generic
repository listing and launch mechanisms without copying SoundAtlas bootstrap
or inheriting SoundAtlas stages, service names, network destinations,
credentials, caches, or defaults. The test must also show:

- distinct canonical repositories and worktrees with unambiguous inventory;
- the correct project execution environment and service attachment per launch;
- separate credential references and mutable caches;
- failure in one project does not stop, expose, or relabel the other; and
- both projects remain usable through their repository-owned non-Pane commands.

Candidate B does not meet the intended operational reuse outcome because it
duplicates a complete control-plane instance. Candidates A and C could meet it
by design, but neither has live evidence. Candidate C has the better ownership
fit because project-neutral multi-project lifecycle is its primary boundary,
not an adapter layered onto a host-centric control plane.

## 5. Recommendation and rejected alternatives

**Recommend Candidate C, a shared project-neutral platform runtime with
isolated per-project execution environments, as the direction for subsequent
contract and PoC work.** This is a recommended direction, not a migration
approval or a claim that the architecture is ready to implement.

Candidate C best satisfies the Target Principles because it:

- gives generic orchestration, transport, compatibility, isolation, and
  lifecycle mechanisms one reusable owner without locating project meaning in
  that layer;
- removes per-project Remote Daemon, SSH/pairing, state, port, and upgrade
  duplication identified by #209;
- retains containerized execution and avoids requiring agent runtimes or
  project toolchains on the host;
- allows SoundAtlas services, stages, validation, preview, credentials, and
  network exceptions to remain project-owned declarations; and
- makes multi-project reuse and non-Pane operation explicit design invariants.

The recommendation is conditional on evidence that one shared runtime can
isolate two materially different projects, preserve exact worktree and launch
identity, attach only declared services and credentials, and recover without
cross-project impact. Failure of those tests returns the decision to this
evaluation rather than defaulting to Candidate C.

**Reject Candidate A as the target at this evidence level.** It remains a
plausible deployment variant, but it introduces an unproven host-to-container
launch and path-mapping boundary and makes host lifecycle part of the supported
tuple. Moving Pane to the host does not itself solve the ownership, launch,
credential, network, compatibility, or recovery gaps established by #209.

**Reject Candidate B as the target, while retaining it as the closest
operational fallback and rollback model.** It has the strongest current
operational evidence and the smallest initial change, but it keeps generic
control-plane responsibilities and per-project Remote Daemon/access duplication
inside every project environment. Extracting a reusable image alone would
reduce copy/paste without resolving that ownership and lifecycle result.

Use a **C-compatible form of Candidate B as the migration strategy** before
attempting the final shared-runtime topology. First extract a reusable,
SoundAtlas-neutral per-project runtime and separate generic runtime mechanisms
from SoundAtlas policy and configuration. Keep its project-facing integration
boundary compatible with later shared-runtime use, and do not introduce
interfaces or lifecycle assumptions that require one control plane per project.
This intermediate state reduces migration risk; it does not change Candidate C
as the target recommendation or make Candidate B the target architecture.

## 6. Unknowns, compatibility, migration, and rollback

### Outcome-determining evidence gaps

- A supported Pane/RunPane/agent/launcher/image/container-engine tuple and
  native-versus-routed launch contract.
- A two-project Candidate C exercise covering repository/worktree identity,
  launch, service attachment, cache and credential separation, and isolated
  failure/recovery.
- The credential process/file visibility matrix owned by #226.
- The minimum useful egress and runtime capability results owned by #227 and
  #229.
- Backup/restore, image replacement, upgrade/downgrade, worktree path repair,
  pairing recovery, and shared-runtime failure containment.
- Non-Codex agent installation, authentication, and launch behavior; current
  evidence supports only Codex.

### Compatibility implications

The recommended shared runtime must version its generic compatibility tuple as
one tested unit. Project application toolchains remain independently declared.
An upgrade is not compatible merely because deterministic fixtures pass: live
inventory, native and stage-routed launches, terminal readiness, service
attachment, and recovery must agree. Invalid or unknown versions fail closed,
and the last reviewed runtime remains available for rollback.

### Migration implications

Later work should proceed through separate bounded stages: stabilize the current
compatibility and launch baseline; complete credential, network, and runtime-
capability evidence; design and extract the C-compatible reusable per-project
runtime described above; validate multi-project isolation and shared-runtime
behavior; define the final Project ↔ Platform Contract; and only then plan the
remaining migration and legacy retirement. Migration should keep the current
per-project runtime alongside the new path until repository/worktree state,
launches, service access, credentials, networking, restart, and replacement are
verified. Legacy workspace retirement remains last.

### Rollback implications

Candidate B is the bounded rollback until Candidate C is accepted. Preserve
the existing runtime image and all Pane, repository/worktree, SSH, Codex, and
credential state until every retained worktree is rediscovered and validated
through the replacement. Stop migration on widened network/credential access,
lost or ambiguous inventory, launch-parity regression, service misattachment,
or cross-project failure. Never use broad volume deletion as rollback and never
retry ambiguous Pane creation automatically.

## 7. Bounded follow-up Issue proposals

These are proposals only; #208 does not create them.

| Follow-up | Bounded outcome | Dependency |
| --- | --- | --- |
| Complete the Pane/RunPane/Codex compatibility and launch baseline | Extend the versioned image baseline into a supported compatibility contract; compare native and stage-routed command, context, permissions, readiness, inventory, and failure behavior; retain upgrade/rollback evidence. | Reuse completed #233, #235, and #236. |
| Complete [#226](https://github.com/gititinyoursoul/soundatlas/issues/226) | Produce the non-secret credential visibility, inheritance, persistence, and rotation matrix; make no credential change. | Before shared-runtime credential design or PoC. |
| Complete [#227](https://github.com/gititinyoursoul/soundatlas/issues/227) and [#229](https://github.com/gititinyoursoul/soundatlas/issues/229) | Separate required egress controls and normal development capabilities from SoundAtlas-specific complexity; make no runtime change. | Before choosing shared network/service attachment. |
| Design and extract a C-compatible reusable per-project runtime | Separate generic runtime mechanisms from SoundAtlas policy and configuration while preserving a project-facing boundary that can later connect to a shared control plane; do not require one control plane per project in new interfaces or lifecycle assumptions. | Compatibility, credential, network, and runtime-capability evidence; separate approved design and implementation Issues. |
| Candidate C disposable two-project PoC | Run one shared project-neutral runtime with SoundAtlas and a materially different disposable repository; test all multi-project criteria and cleanup without migration. | C-compatible reusable per-project runtime; separate exact authorization for runtime/repository creation. |
| Shared-runtime recovery PoC | Exercise backup/restore, image replacement, version rollback, path repair, pairing recovery, and failure isolation using disposable state only. | Candidate C multi-project PoC passes. |
| Define the final Project ↔ Platform Contract | Specify the minimum project declarations, capability results, ownership, validation, and failure semantics without embedding SoundAtlas defaults. | Human accepts the candidate after the distinguishing PoCs. |
| Plan and implement migration | Sequence extraction, dual-path operation, state transition, verification, rollback, and eventual legacy retirement. | Accepted contract and separately approved migration Issue. |

## 8. Non-goals retained

This evaluation does not define a contract schema or API, implement a launcher
or runtime, move repositories or state, change credentials or networking,
operate Pane/RunPane, create follow-up Issues, alter CI or deployment, or claim
that the recommended architecture is current behavior. The Target Principles
remain non-binding evaluation guidance; this document records only the #208
recommendation and the evidence required before later approval.
