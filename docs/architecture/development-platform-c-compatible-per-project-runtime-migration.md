# C-Compatible Per-Project Runtime Migration

## Status and purpose

This is the authoritative Issue #237 intermediate migration-design artifact. It
defines how SoundAtlas can move from its repository-coupled Pane/Codex runtime
to reusable per-project runtime packaging while preserving a later move to the
shared project-neutral runtime recommended by
[Issue #208](development-platform-runtime-architecture-evaluation.md).

This document is not implemented current-state architecture, final architecture
policy, or the final Project ↔ Platform Contract. The per-project runtime is a
migration topology derived from Candidate B; Candidate C remains the destination
direction. No interface, deployment assumption, or lifecycle rule introduced
during this migration may require one Pane/RunPane control plane per project.

The design reuses the accepted
[#209 coupling and ownership findings](https://github.com/gititinyoursoul/soundatlas/issues/209#issuecomment-5621011312)
instead of recreating that audit. Current configuration is evidence for
migration decisions, not proof that its placement should remain unchanged.

## Intermediate design

The intermediate runtime has two responsibility surfaces:

- The **project surface** owns project identity and meaning: workflow policy,
  application services, validation and preview requirements, toolchain needs,
  credential policy, network exceptions, and project-specific launch choices.
- The **reusable runtime surface** owns project-neutral mechanisms: Pane/RunPane
  and agent packaging, tested compatibility, isolation, authenticated transport,
  lifecycle, secret injection, network enforcement, persistence, recovery, and
  observable capability results.

During migration, one reusable runtime instance may be deployed for one project.
That cardinality is outside the stable project surface. A later shared runtime
must be able to consume the same project meaning and integration concepts while
replacing the per-project control-plane topology.

Human authority remains separate from component ownership. A Human selects the
architecture, authorizes migrations and destructive cleanup, and controls secret
values and external authorization. Runtime capability does not grant any of
those decisions.

## Decision-focused responsibility map

The accepted #209 map remains the detailed current-state audit. The table below
adds only decisions that affect the intermediate design, sequencing, rollback,
value, reuse, or Candidate C portability.

| Area | Current owner / evidence | Intermediate owner | Remains project-owned | Candidate C stability requirement | Migration risk and rollback |
| --- | --- | --- | --- | --- | --- |
| Runtime packaging and versions | SoundAtlas's `.devcontainer/Dockerfile` currently combines project tooling with Pane, RunPane, Codex, browser, and system packages. #235 and #236 aligned the current Pane runtime pins. | A reusable runtime distribution owns the tested Pane/RunPane/agent/container compatibility unit; each project owns application toolchain requirements. | Required application and workflow tool versions and the decision to support an agent. | A shared runtime can select a tested generic runtime without inheriting project toolchain defaults. | An unproved tuple can break inventory or launches. Retain the reviewed image and configuration until live compatibility and downgrade evidence pass. |
| Pane/RunPane and agent provisioning | The Pane image and repository bootstrap provision Pane, RunPane, Codex, and browser support together. | Reusable runtime packaging owns generic provisioning and launch compatibility. | Agent choice, workflow-stage meaning, and intentional model, effort, or permission policy. | Agent support and generic launch results do not depend on one project or one control-plane instance. | A custom launcher can drift from native behavior. Stop on parity regression and retain the last validated launch path. |
| Daemon and remote access | The SoundAtlas Compose profile and Pane entrypoint start the daemon, SSH transport, pairing state, and loopback publication. | The reusable runtime owns daemon and authenticated transport mechanisms; the operator owns external exposure and pairing authorization. | Whether and how the project permits remote development access. | Transport addresses runtime/project identity without encoding a per-project control-plane requirement. | Replacement can lose pairing or expose a broader endpoint. Keep old state stopped but recoverable until reconnect, rotation, and revocation checks pass. |
| Lifecycle, persistence, replacement, and recovery | Compose services, the Pane entrypoint, named volumes, RunPane, and the operator runbook divide these responsibilities. | Pane/RunPane retains Pane, panel, terminal, worktree, and archive semantics; the reusable runtime owns service lifecycle and state backup/restore mechanisms. | Project acceptance probes and decisions about which project data or caches matter. | State identity and recovery remain project-addressable when control-plane cardinality changes. | Path-sensitive worktrees or runtime state can be stranded. Preserve old volumes and runtime; require inventory, Git integrity, restart, restore, downgrade, and path-recovery evidence before cutover. |
| Credential injection and policy | Repository configuration mounts credential inputs and the entrypoint exposes selected credentials to descendant processes. #226 remains open. | A reusable mechanism injects referenced secrets narrowly and reports non-secret outcomes; the secret provider/Human owns values and rotation. | Required credential classes, scopes, allowed tasks, and delivery authorization. | Secret references and results attach to project/session identity, not to a dedicated project control plane. | Visibility may widen or required access may disappear. Do not migrate this boundary before #226; revoke affected credentials and return to the current injection path on regression. |
| Network enforcement and service exceptions | The `pane-egress` mechanism is generic in shape but its policy and lifecycle are coupled to named application services. #227 and #229 remain open. | The reusable runtime owns isolation and enforcement; projects declare required service access; the operator owns host exposure. | Necessary public access and project-service exceptions. | Rules attach to an isolated project execution context independently of control-plane placement. | A change can widen private/host access or block required services. Keep the current guard available; fail closed and roll back on either result until the open evidence work completes. |
| Repository and worktree attachment | Pane/RunPane owns worktree mechanics, while repository helpers and persistent paths contain SoundAtlas assumptions. | Pane/RunPane and the reusable runtime own generic discovery, attachment, identity, and recovery mechanisms. | Repository identity, Git policy, and authorization to mutate or publish it. | Canonical identity remains explicit and unambiguous across per-project and shared control planes. | Path or ownership changes can orphan worktrees. Preserve the existing base clone and Git common data until every retained worktree passes inventory, status, and integrity checks. |
| Application services and exact-worktree preview | Compose services and `scripts/pane-preview.sh` are project-specific adapters over runtime networking, worktree, process, and transport capabilities. | The runtime owns generic service/process attachment and authenticated forwarding; SoundAtlas owns preview behavior. | Service existence and behavior, data/editorial modes, preview identity, readiness, and exact-worktree requirements. | A project session can request and observe service attachment without a SoundAtlas service becoming a runtime default. | Wrong-worktree or wrong-service attachment gives misleading evidence. Retain the current preview and normal non-Pane path until exact identity and failure cases pass. |
| Project validation and non-Pane contribution | Repository commands, `AGENTS.md`, and project documentation own validation and workflow rules. | The project continues to own them; reusable infrastructure may invoke them without interpreting their meaning. | Commands, acceptance thresholds, workflow gates, and reporting meaning. | The same project-owned commands work with a per-project runtime, shared runtime, or no Pane. | Generated context or runtime-only commands can become accidental authority. Roll back any runtime wrapper that prevents direct repository use. |
| Repository artifacts versus runtime mechanisms | Current Compose, Dev Container, entrypoint, egress, Seccomp, inventory, launch, and preview artifacts mix the surfaces to different degrees. | Durable generic mechanisms move under reusable ownership; project policy and bounded adapters remain with SoundAtlas. | All SoundAtlas names, services, stages, ports, validation, preview semantics, credential requirements, and workflow authority. | Only project-neutral responsibilities cross into reusable artifacts; topology-specific adapters are replaceable. | A broad move can carry hidden defaults or remove rollback. Extract only at stage checkpoints and retain compatibility wrappers until replacement evidence passes. |

The current SoundAtlas value of this split is concentrated in controlled version
updates, clearer recovery, reduced launch drift, and smaller credential/network
responsibility seams. Its reuse value comes from preventing a second project
from copying SoundAtlas's service names, workflow policy, ports, credentials,
and bootstrap lifecycle.

## Stable project-facing integration concepts

These concepts constrain later design without choosing fields, schemas, hooks,
APIs, messages, serialization, adapters, or lifecycle protocols. Any need for
those representations is an input to the later final Project ↔ Platform Contract
Issue.

| Responsibility | Purpose | Invariant | Required observable outcome | Candidate C portability |
| --- | --- | --- | --- | --- |
| Project identity | Associate requirements and results with the intended project. | Identity is stable and cannot be inferred from a control-plane instance. | An operator or agent can tell which project supplied a requirement or received a result. | Several projects can be distinguished within one shared runtime. |
| Repository/worktree attachment | Select the exact source and working state used by a session. | One attachment resolves to one canonical repository and worktree identity. | Inventory, launch, validation, and preview report the same source identity or fail visibly. | Attachment does not depend on a path convention unique to a per-project control plane. |
| Execution requirements | Express the project-owned toolchain and supported agent needs. | Generic infrastructure does not add project tools or agent defaults implicitly. | Missing or incompatible capability is reported before work begins. | Isolated execution can be selected independently for each project. |
| Launch policy boundary | Apply intentional project workflow choices without taking ownership of generic launch behavior. | Unchanged native behavior remains equivalent; intentional differences remain project-owned and visible. | A launch reports its project policy inputs, generic capabilities, readiness, and failure. | The same policy can be applied at an isolated execution boundary behind a shared control plane. |
| Service attachment | Make only the project services required by a task reachable. | Service meaning stays with the project and attachment never becomes a platform default. | Required service reachability and identity are observable; missing or wrong attachment fails visibly. | Attachments are scoped to project execution rather than control-plane identity. |
| Credential responsibility | Connect project-authorized credential needs to generic narrow injection. | Values remain Human/secret-provider owned; runtime access never implies workflow authorization. | Availability, scope class, rotation state, and failure are observable without revealing secret material. | Credentials are scoped to a project/session within a shared runtime. |
| Network responsibility | Combine reusable enforcement with project-owned exceptions. | Access does not widen silently and unsupported policy fails closed. | Allowed and denied capability results are observable for the selected execution context. | Enforcement is isolated per project execution, not tied to a dedicated control plane. |
| State and cache classes | Distinguish durable runtime/project state from rebuildable caches. | Recovery and cleanup never treat all stored data as disposable. | Ownership, persistence expectation, backup result, and recovery result are visible. | State remains attributable and isolated when several projects share the control layer. |
| Validation and preview | Preserve project-owned proof of correctness and exact-worktree presentation. | Orchestration may invoke project commands but cannot redefine their acceptance meaning. | Results identify the exact source, mode, service attachment, and readiness state. | The same project commands work through shared orchestration or without Pane. |
| Capability and failure reporting | Give agents and operators reliable runtime facts. | Unknown or unsupported capability is unavailable; ambiguous mutation is never retried automatically. | Readiness, identity, liveness, failure, and recovery state can be inspected separately. | Results are project/session-addressable rather than global or instance-implied. |

## Current artifact decisions

This is not a second coupling inventory. It identifies only the current groups
whose treatment changes migration value or rollback.

| Current artifacts | Classification | Migration decision |
| --- | --- | --- |
| `.devcontainer/Dockerfile`, Pane portion of `.devcontainer/docker-compose.devcontainer.yml`, `.devcontainer/pane-entrypoint.sh`, `.devcontainer/pane-seccomp.json` | Mixed boundary with durable runtime mechanisms | Separate generic packaging, compatibility, isolation, daemon, transport, and startup mechanisms from project tools and values. Keep the current image/profile as rollback until replacement evidence passes. |
| `docker/pane-egress.Dockerfile`, `docker/pane-egress-guard.sh`, Pane Compose network/dependency settings | Mixed boundary; enforcement mechanism can be durable, current exceptions and dependency graph are project policy | Wait for #227/#229 evidence, then separate enforcement from declared exceptions and app lifecycle. Do not generalize the current named destinations. |
| Credential mounts and `.devcontainer/pane-entrypoint.sh` credential setup | Mixed security boundary | Wait for #226. Preserve project scope and Human authorization while extracting only generic injection and non-secret result reporting. |
| `.devcontainer/pane-inventory.sh` | Temporary project adapter over generic inventory | Preserve during migration; replace hard-coded project selection only after a generic identity result is proven. Do not optimize it as a long-term per-project interface. |
| `.codex/model-routing.toml`, `scripts/run_codex_stage.py`, `scripts/pane_execution_context.py` | SoundAtlas policy plus a mixed launch/capability seam | Keep stage meaning and model policy in SoundAtlas. Move only generic capability truth and launch-parity responsibility behind a reusable boundary. |
| `scripts/pane-preview.sh` and frontend preview identity behavior | SoundAtlas-owned preview with reusable attachment needs | Keep preview semantics in the project; consume generic exact-worktree process and forwarding capabilities when proven. |
| `AGENTS.md`, workflow docs, project commands and validation | Project authority | Do not extract. Keep usable without Pane and prevent generated context from becoming authoritative. |
| Pane, repository/worktree, SSH, Codex, dependency, and browser volumes | Mixed persistent state and rebuildable caches | Classify and migrate separately. Preserve all current state through cutover; discard only a proven rebuildable cache under an exact rollback plan. |
| Per-project daemon naming, port ergonomics, pairing convenience, or automatic per-project runtime creation | Candidate B optimization | Defer or remove unless required for safe rollback. It has low reuse value and risks making the migration topology contractual. |

## Value-based stage prioritization

The qualitative assessments expose tradeoffs; they are not an aggregate score.
`Enables C` means the result is required or materially reused by Candidate C.

| Stage | SoundAtlas value | Reuse value | Cost / risk | Enables C | Work type | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Compatibility, state, and rollback baseline | **High** — reduces current update and recovery risk | **Medium** — creates evidence reusable by another project | **Medium** — live recovery checks can disturb state if poorly bounded | **Yes** — shared operation needs trusted compatibility and recovery | Durable evidence and temporary rollback preparation | **Now** |
| 2. Conceptual project/runtime boundary | **Medium** — prevents new coupling and ownership drift | **High** — gives a second project a neutral integration meaning | **Low** — documentation/design work only | **Yes** — Candidate C consumes the same concepts | Durable | **Now** |
| 3. Generic packaging and version ownership | **High** — reduces duplicated update authority and launch incompatibility | **High** — gives another project a tested runtime without copied bootstrap | **Medium** — image and toolchain separation can regress compatibility | **Yes** — Candidate C needs a reusable runtime unit | Durable | **Next** |
| 4. Generic lifecycle, transport, persistence, and isolation extraction | **Medium** — improves recovery and removes app-lifecycle coupling | **High** — eliminates copied daemon/bootstrap mechanisms | **High** — path, state, access, and recovery seams move together | **Yes** — these become shared-runtime responsibilities | Durable, with temporary compatibility wrappers | **Next, after Stage 1 evidence** |
| 5. Credential, network, and service attachment separation | **High** — can reduce exposure ambiguity and app-start coupling | **High** — prevents project secrets and services becoming runtime defaults | **High** — security and connectivity regression risk | **Yes** — Candidate C requires isolated project attachment | Durable, with temporary SoundAtlas adapters | **Next, only after #226/#227/#229** |
| 6. SoundAtlas dual-path attachment and cutover proof | **High** — preserves worktrees, launches, preview, validation, and rollback | **Medium** — project adapter is specific, but its proof exercises reusable boundaries | **High** — temporary duplication and cutover risk | **Yes** — proves the boundary can carry a real project | Temporary migration plus durable project policy | **Later, after Stages 3–5** |
| 7. Materially different second-project proof | **Medium** — reduces the risk that SoundAtlas coupling was merely renamed | **High** — directly establishes cross-project reuse | **Medium** — requires a disposable project and exact cleanup | **Yes** — prerequisite evidence for shared operation | Durable evidence; disposable setup | **Later, separately authorized** |
| 8. Candidate C shared-runtime PoC and final contract | **Low now** — little immediate operational benefit before prior evidence | **High** — delivers the target multi-project topology | **High** — new isolation and recovery model | **Yes, directly** | Durable, but outside #237 migration implementation | **Defer until Stages 1–7 pass** |
| 9. Legacy runtime retirement | **Medium** — lowers maintenance and security burden after cutover | **Low** — removal is mainly SoundAtlas cleanup | **Medium** — premature removal destroys rollback | **No** — Candidate C does not depend on early deletion | Temporary migration cleanup | **Defer; #230 remains last** |
| 10. Candidate B convenience optimization | **Low** — polish for an intermediate topology | **Low** — reinforces per-project duplication | **Medium** — consumes effort and can ossify topology | **No** | Candidate B optimization | **Remove by default** |

Stage 8 has low immediate SoundAtlas value but is retained because it is the
accepted destination. It is deliberately deferred until the durable boundary
and distinguishing evidence exist. Stage 9 is justified only after cutover
because it then provides maintainability and security value. Stage 10 is the
explicit low-value/low-reuse category and receives no work without a concrete
rollback or immediate operational justification.

## Ordered extraction and rollback checkpoints

Each stage is independently stoppable. Passing deterministic checks alone does
not authorize a cutover or prove live compatibility.

| Stage | Prerequisites and output | Success evidence and stop condition | Preserved state and rollback |
| --- | --- | --- | --- |
| 1. Baseline | Current reviewed versions and config; produce live compatibility, inventory, launch, state classification, backup/restore, downgrade, and recovery evidence. Durable evidence survives into C. | Required signals agree for the same runtime and every retained worktree; stop on ambiguous identity, failed restore, or version drift. | Make no in-place destructive update. Retain the reviewed image, configuration, volumes, pairing, repositories, worktrees, and credential inputs. |
| 2. Boundary | Accepted #208/#209 decisions; preserve the conceptual integration concepts and anti-cardinality invariant. | A cold read can describe the project without naming runtime placement; stop if any concept requires a dedicated control plane. | Documentation-only; revert the proposal without runtime effect. |
| 3. Packaging | Stages 1–2; separate a project-neutral tested runtime unit from project tooling and policy. | Current SoundAtlas and a neutral consumer can identify the same generic compatibility unit without inheriting project defaults; stop on launch, browser, inventory, or toolchain regression. | Keep the current SoundAtlas-built runtime available and all state compatible with it. |
| 4. Runtime core | Stages 1–3; extract lifecycle, daemon, transport, persistence, isolation, and recovery mechanisms. Compatibility wrappers are temporary. | Restart, replace, recover, and reconnect preserve exact identity and fail visibly; stop on lost worktree, state ambiguity, broader exposure, or unrecoverable downgrade. | Run old and new paths only with explicit identities. Preserve old runtime/state read-only or stopped but recoverable until the new path passes. |
| 5. Secure attachment | #226/#227/#229 conclusions plus Stages 1–4; separate generic injection/enforcement/attachment from project policy. | Non-secret credential outcomes, allowed/denied network probes, and exact service identity match project requirements; stop on widened visibility/access or lost required capability. | Revoke affected credentials when needed, restart processes, and return to current mounts, egress guard, and service attachment. Never copy secret values into project/runtime configuration. |
| 6. SoundAtlas migration | Stages 3–5; connect repository/worktree, stage launch, services, preview, and validation through the portable boundary. Project policy is durable; dual-path glue is temporary. | Native/routed behavior, inventory, exact-worktree preview, project checks, restart, and failure reporting pass on the selected path; stop on identity mismatch, ambiguous creation, or non-Pane regression. | Retain the existing Pane profile and legacy workspace. Do not retry ambiguous creation; resolve inventory first and select one explicit rollback path. |
| 7. Reuse proof | Stage 6 plus separate authorization for disposable resources; use a materially different project without copied defaults. | Both projects remain distinct; launch, services, credentials, caches, failures, and cleanup are isolated; stop on inherited project assumptions or cross-project impact. | Remove only named disposable resources. SoundAtlas and its current rollback state remain untouched. |
| 8. Candidate C handoff | Accepted Stage 7 evidence; later Issues own the shared-runtime PoC and final contract representation. | The shared topology can replace per-project control planes without changing any project concept; otherwise return to architecture evaluation. | Candidate B remains the bounded operational rollback until Candidate C is separately accepted. |
| 9. Retirement | Accepted replacement, recovery, and Human authorization; #230 owns exact removal. | No live dependency or Issue-relevant state remains on the old path; stop on any missing evidence. | Retirement is last. Never use broad volume deletion as rollback or cleanup. |

## Coherent follow-up work packages

These are proposals, not created Issues or a mandatory decomposition. Before
creation, combine or split them only when ownership, write/runtime boundary,
prerequisites, rollback, and validation evidence still align.

| Proposed package | Included responsibilities and grouping rationale | Dependencies | Durable / temporary boundary | Validation and rollback |
| --- | --- | --- | --- | --- |
| Reusable runtime foundation and recovery baseline | Combine supported packaging/version ownership with daemon, transport, lifecycle, persistent-state classification, and recovery evidence because they share runtime distribution ownership, image/state rollback, and compatibility proof. | Current baseline; completed #235/#236; separately authorized recovery exercises. | Generic packaging and recovery mechanisms are durable; old-image/state retention and compatibility wrappers are temporary. | Live version, inventory, native/routed launch, restart, backup/restore, replacement, downgrade, worktree recovery, and reconnect evidence. Roll back to the retained reviewed image and untouched state. |
| Secure project attachment | Combine secret injection, network enforcement, and application-service attachment only if #226/#227/#229 confirm a shared execution-boundary change, prerequisite set, fail-closed behavior, and rollback. Split if their evidence or security boundary differs. | Accepted #226, #227, and #229 results; reusable foundation. | Neutral injection/enforcement/attachment mechanisms are durable; SoundAtlas transition adapters are temporary. | Non-secret visibility/rotation evidence, allowed/denied probes, exact service identity, and isolated failure. Roll back credentials, guard, and attachment independently when required. |
| SoundAtlas portable attachment and dual-path migration | Combine repository/worktree identity, project launch policy, capability truth, preview, validation, and non-Pane parity because they share the SoundAtlas project boundary and exact-worktree cutover/rollback. | Prior packages and current project acceptance checks. | Project policy and portable concepts are durable; inventory/launch/preview bridge glue and dual operation are temporary. | Exact identity across inventory, launch, validation, and preview; failure cases; restart/recovery; non-Pane commands. Roll back to the current Pane profile or legacy workspace without losing state. |
| Cross-project proof and Candidate C handoff | Keep the disposable second-project proof separate from SoundAtlas migration because it has different resources, cleanup, and authorization. Keep the shared-runtime PoC and final contract in later separately approved work because they change topology and select representations. | Accepted SoundAtlas migration evidence; separate exact authorization for disposable/runtime resources. | Reuse evidence and conceptual boundary are durable; disposable resources are temporary. Candidate C implementation and contract are later work. | Two-project isolation and cleanup evidence. Any inherited SoundAtlas assumption or cross-project failure returns the design to evaluation; SoundAtlas remains on its accepted rollback path. |

Candidate B convenience work is not a package. Per-project daemon polish,
automatic one-runtime-per-project creation, dedicated-port management, or other
topology-specific optimization stays deferred unless a later Issue demonstrates
significant immediate SoundAtlas value or a safe-rollback need.

## Completion conditions for this design

The migration design is satisfied when later work can use the stages and
packages without rediscovering ownership, value, prerequisites, preserved
state, evidence, or rollback decisions. It intentionally leaves concrete
configuration, API, protocol, schema, message, hook, and serialization choices
to the final Project ↔ Platform Contract and implementation Issues.

No extraction, runtime change, credential or network change, state migration,
follow-up Issue creation, Candidate C PoC, or legacy retirement is authorized by
this document.
