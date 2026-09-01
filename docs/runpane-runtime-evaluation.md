# Persistent RunPane Runtime Evaluation

## Conclusion

SoundAtlas should keep its current controlled workspace as the default execution
boundary and treat a dedicated persistent agent runtime as a conditional target,
not as an adopted architecture. A dedicated runtime best matches the intended
separation:

```text
security isolation = dedicated VM or container boundary
task isolation     = RunPane Pane plus Git worktree
process isolation  = fresh panel and Codex process for each workflow stage
```

The current Windows installation proves that RunPane can create, isolate, and
clean up Issue worktrees without creating a development container. It does not
provide a strong security boundary: the Pane daemon and panel shells run on the
host, and the current Codex application server is a separate host process.

A bounded attempt to bootstrap RunPane in a Linux container failed in the
RunPane release-resolution path before Pane state was created. A direct pinned
artifact fallback was not authorized during the experiment. The dedicated
runtime is therefore technically plausible from Pane's upstream headless-daemon
contract, but its complete daemon/UI/built-in-Codex and persistence path remains
an evidence gap. SoundAtlas should not migrate until a follow-up prototype
closes that gap without a Docker socket, privileged mode, broad host mounts,
writable host credentials, or a disabled Electron sandbox.

This document is an investigation record. It does not change the current
development or RunPane workflow.

## Scope and evidence method

Issue #192 evaluates runtime placement, persistence, worktree behavior,
security, service use, and developer workflow. It does not implement a runtime.
Evidence is classified as:

- **Tested**: directly observed during this investigation.
- **Inspected**: derived from repository configuration or host process state.
- **Upstream contract**: documented by the pinned Pane release or source.
- **Evidence gap**: not demonstrated; no architectural claim is inferred.

Private host paths, user names, tokens, connection codes, and raw process output
are intentionally omitted. Tests used disposable state only. No RunPane agent
performed planning, implementation, or review.

## Version and provenance ledger

| Item | Observed version or revision | Evidence |
| --- | --- | --- |
| SoundAtlas | `02b154a3bdfd3697418d25fae8e183c7a923b9e4` | Tested Issue worktree baseline |
| RunPane wrapper / Pane | `2.4.95` | `runpane doctor --json`; installed Windows application |
| Pane source | `5ac1b04831746724d84ab5b0a3487ac11a150c05` | Pinned upstream release revision |
| Pane packaged runtime | Electron `41.10.3`, Node `24.18.0` | RunPane doctor output |
| Host Docker | client/server `29.7.2`, Linux/amd64 Docker Desktop engine | Host inspection |
| Host Codex CLI | `0.142.5` | Host command inspection |
| Workspace Codex CLI | `0.147.0` | `.devcontainer/Dockerfile` |
| Host Git | `2.45.2.windows.1` | Host command inspection |
| Host language tools | Node `24.11.1`, npm `11.6.2`, Python `3.12.2` | Host command inspection |
| Workspace base tools | Node `24.11.1`, Python `3.13`, `uv` | `.devcontainer/Dockerfile` |

Relevant upstream contracts are Pane's
[self-hosted daemon documentation](https://github.com/dcouple/Pane/blob/main/docs/SELF_HOSTED_REMOTE_DAEMON.md),
[RunPane CLI contract](https://github.com/dcouple/Pane/blob/main/docs/RUNPANE_CLI_CONTRACT.md),
and [release v2.4.95](https://github.com/dcouple/Pane/releases/tag/v2.4.95).
The self-hosted documentation says that one `PANE_DIR` owns daemon state, the
daemon listens on loopback, and remote UI access uses an approved SSH, Tailscale,
or HTTPS exposure layer. It also records that the packaged Pane runtime is
currently downloaded because no separate daemon binary is published.

## Current execution and security models

### Host RunPane

Host process inspection located the Pane application and daemon as Windows
`Pane.exe` processes. Disposable Pane panels opened Windows shells in their
managed worktrees. The active Codex session is a separate process launched by
the VS Code OpenAI extension, not a child demonstrated to have been launched by
RunPane. The UI reaches the local daemon through a Windows named pipe.

This model offers task separation through Git worktrees, but a Pane shell or
host Codex process has the host account's filesystem, process, credential, and
network reach. Git worktrees are not a security sandbox.

### Current SoundAtlas workspace

The normal workspace is a long-running Linux container and does not require VS
Code after Compose starts it. Repository inspection shows:

- a non-root `soundatlas` user with UID/GID `10001` after startup;
- `no-new-privileges`, `NET_ADMIN`, and `seccomp=unconfined`;
- an egress guard that permits controlled HTTPS and selected app-service
  destinations;
- the selected repository bind-mounted at `/workspace`;
- read-only inputs for host Codex state, the app secret file, and the
  repository-scoped GitHub token file;
- named volumes for Codex state, GitHub CLI state, dependencies, and caches;
- no Docker socket, Docker CLI, host PID namespace, or privileged mode.

This is a useful coding boundary, not a general hostile-code sandbox. In
particular, `NET_ADMIN` and unconfined seccomp are deliberate implementation
tradeoffs. The container combines a task checkout, task-visible credentials,
tool caches, and a cleanup lifecycle. Those properties make it a poor durable
control plane for every future Pane and Issue without redesign.

### Existing host RunPane plus container execution

The strongest currently available shape is host RunPane for UI/worktree
orchestration with Codex invoked inside the controlled workspace. It preserves
the container boundary and optional VS Code use, but it needs a reliable
launcher, mount translation, and container lifecycle for every stage. This
investigation does not restore or adopt the earlier experimental launcher.

## Tested RunPane worktree behavior

Two disposable panes were created from the saved SoundAtlas base repository:
`issue-192-probe-a` and `issue-192-probe-b`. Neither pane launched an agent.
Each panel reported its own branch and clean working directory.

Both worktrees used the base repository's shared Git common directory. Each had
its own worktree administrative directory and index; one used a Pane reserve
administrative slot, showing that callers should not infer lifecycle from the
administrative directory name. A harmless untracked marker created in probe A
appeared in probe A's Git status and filesystem and did not appear in probe B.

After the marker was removed, RunPane archived each exact pane. Its safety check
reported no uncommitted files or unpushed commits, and worktree cleanup
completed. Both filesystem paths then ceased to exist. An initially supplied
stale pane identifier was rejected rather than deleting a different pane; the
live pane list provided the correct identifier. This is useful fail-closed
behavior, but cleanup automation must still resolve and display the exact pane
and worktree before archive.

The test establishes branch, index, working-tree, and generated-file separation
for normal repository-local changes. It does not isolate the shared Git object
database, Git configuration, credentials, host processes, environment,
temporary directories, caches, ports, or external services.

## Persistent runtime experiments

### Candidate A: reuse the current workspace image and configuration

The workspace image already contains Git, Codex, `gh`, Node, Python, `uv`, and
long-running Compose behavior. It does not contain RunPane or Docker, and it
does not expose a daemon or Docker socket. A disposable attempt to install and
start the pinned RunPane daemon in this Linux image failed before state creation
with a release-resolver validation error (`input.body: expected string`). The
same result occurred with the latest wrapper and the pinned `2.4.95` wrapper.

This failure is evidence against the current bootstrap path, not proof that Pane
cannot run in Linux. Upstream documents a Linux headless path and a normal
Electron sandbox. The experiment did not use `--no-sandbox` or add a prohibited
host-control mount.

Even if bootstrap is repaired, reusing the current workspace is not recommended:

- the repository mount represents one selected task, not a durable base plus
  sibling worktree store;
- task credentials and caches would become global daemon resources;
- `NET_ADMIN` and unconfined seccomp should be reconsidered for a persistent
  control plane rather than inherited accidentally;
- rebuilding or removing the development container would also interrupt Pane
  state and every Issue; and
- current dependency and app-service volumes have workspace-wide names and
  fixed-port assumptions.

### Candidate B: dedicated persistent controlled runtime

The preferred target is a separately managed runtime containing Pane/RunPane,
Codex, Git, `gh`, SoundAtlas language tooling, a base checkout, sibling
worktrees, and narrowly seeded credentials. Two labeled volumes were allocated
for a disposable prototype. Wrapper-based daemon installation encountered the
same release-resolution failure before state creation. Volume ownership was
prepared without network access, but the direct pinned-release download was not
authorized, so no daemon, UI connection, built-in Codex process, or restart
matrix was demonstrated. The disposable volumes could not later be inspected
or removed because those Docker operations were not authorized; their cleanup
status is an evidence gap that the follow-up prototype must resolve before
creating new resources.

Candidate B has the cleanest responsibility boundary, but remains conditional.
Its prototype must demonstrate all of these together:

1. non-root headless Pane with the Electron sandbox enabled;
2. loopback daemon access through SSH, Tailscale, or authenticated HTTPS;
3. a built-in Codex process in the selected worktree and runtime namespace;
4. retained state across daemon and container restart;
5. controlled recovery across container and image replacement; and
6. complete cleanup without host-control privileges.

## Storage and persistence contract

The following paths represent responsibilities, not prescribed host locations.

| Data | Persistence | Sharing | Recovery requirement |
| --- | --- | --- | --- |
| `PANE_DIR` database and configuration | Runtime replacement | One runtime | Versioned backup and restore test |
| Base repository and Git common directory | Runtime replacement | All panes for this repository | Stable in-runtime path; `git fsck` and worktree audit |
| Worktree roots and per-worktree Git admin data | Until pane archive | One pane/Issue | Preserve relative pairing with the common directory |
| Codex configuration/login cache | Runtime replacement where policy permits | Prefer runtime; restrict access | Seed from read-only input; rotate independently |
| GitHub/app credentials | Not baked into image | Only processes that need them | Read-only secret input; rotation and revocation |
| Dependency/tool caches | Optional | Global by tool/version | Safe to delete and rebuild |
| Application state and Compose resources | Per integration task | Selective | Explicit project names and teardown |
| Logs and temporary files | Short retention | Per process or pane | Redaction and bounded cleanup |

Restart levels must not be conflated. A daemon restart should retain all rows
except process-local temporary state. A container restart should retain declared
volumes. Container or image replacement must remount those volumes at identical
in-runtime paths or perform an explicit migration. Git worktree link files can
contain paths; replacement is accepted only after `git worktree list
--porcelain`, status checks in every retained worktree, and archive cleanup all
pass. These replacement cases were not demonstrated in this investigation.

## Effective security boundary

A successful persistent runtime may mount only its dedicated storage and narrow
read-only credential inputs. It must not require:

- `/var/run/docker.sock`, a Podman control socket, or an equivalent API;
- privileged mode, host PID namespace, host network mode, or broad host roots;
- writable host SSH, Codex, GitHub CLI, or application-secret directories;
- the Electron `--no-sandbox` flag; or
- ambient secrets in Compose files, images, committed files, or pane prompts.

The runtime should use a fixed non-root UID, `no-new-privileges`, a restrictive
seccomp/AppArmor profile compatible with Pane and Codex, dropped capabilities,
explicit outbound destinations, and loopback-only daemon binding. Pane's
connection credential protects transport access; it does not replace runtime
isolation. Tool updates should be pinned in the image and promoted by rebuild,
not installed unpredictably by individual panes.

The current workspace's `NET_ADMIN` capability exists to configure its egress
guard and its seccomp profile is unconfined. A dedicated prototype must either
retain and justify these exceptions or move firewall setup outside the agent
process boundary. Access to other containers and host services should be denied
by default and added only for named integration tasks.

## Cross-pane isolation

| Resource | Required classification | Reason |
| --- | --- | --- |
| Working tree, branch, index, untracked outputs | Per pane | Directly tested; prevents repository write collision |
| Panel/Codex process and conversation | Per workflow stage | Prevents context and process-state transfer |
| Git object database and read-only base history | Global per repository | Efficient worktree operation; corruption affects every pane |
| `PANE_DIR` control database | Global per runtime | Pane coordination; requires serialized migrations and backup |
| Credentials | Global input with least-privilege access | Rotation is global; exposure should be process-limited |
| Git identity and global config | Runtime-global, immutable to panes | A pane mutation would affect unrelated Issues |
| `/tmp`, logs, sockets, and environment files | Per pane/process | Names and permissions otherwise permit interference |
| Package caches | Shared by pinned tool/version where safe | Saves resources; cache poisoning remains a risk |
| `node_modules` and Python environment | Prefer per worktree or lock-hash cache | Concurrent installs can corrupt shared mutable state |
| Ports, Compose project, networks, volumes, database | Per integration task | Fixed names and migrations cause cross-pane interference |

RunPane worktrees solve only the first row. The runtime supervisor and task
launcher must enforce the remaining classifications.

## Services and developer workflow

Most planning, documentation, review, lint, type-check, and unit-test work does
not need running application services. A Pane should begin with only its shell,
Codex process, repository worktree, and tool/cache access. This satisfies the
goal of starting an Issue without creating a new development container when the
persistent runtime already exists.

Full-stack checks are selective integration tasks. SoundAtlas currently binds
backend port `8000` and frontend port `5173`, and its dependency volumes have
shared Compose names. Concurrent stacks therefore need explicit per-task
Compose project names, available port assignments, isolated mutable volumes,
and database/migration ownership. Until that policy exists, run at most one
shared full stack, or use the existing controlled workspace for integration
tests. Do not give every Pane a stack by default.

One Issue maps to one Pane and worktree. Planning, implementation, review, and
test may use fresh panels/processes in that Pane when they intentionally share
the Issue filesystem. Different Issues use different panes/worktrees. VS Code
may attach to or open a worktree for manual work, but is not a daemon or workflow
dependency.

## Alternatives

| Alternative | Security boundary | Startup/resource cost | Task isolation | Built-in RunPane flow | Assessment |
| --- | --- | --- | --- | --- | --- |
| Container per Issue or stage | Strong when narrowly mounted | Highest; repeated lifecycle | Strong filesystem/process isolation | Indirect launcher required | Safe fallback for high-risk or conflicting tasks |
| Host RunPane plus host Codex | Host account only | Lowest | Worktree only | Native | Functional baseline, not acceptable as the primary security model |
| Host RunPane plus container-exec Codex | Controlled container | Medium; lifecycle and mount translation | Worktree plus container process | Indirect launcher required | Strongest currently available model; operationally awkward |
| Current workspace as persistent runtime | Existing controlled container | Low after startup | Requires redesign for sibling panes | Not demonstrated; bootstrap failed | Reject as durable control plane |
| Dedicated persistent runtime | Dedicated VM/container | Low per Issue after setup | Worktrees plus supervised processes | Intended native path, not yet demonstrated | Recommended conditional target |

The dedicated runtime reduces Issue startup friction without claiming that all
tasks have identical risk. Selected untrusted, dependency-mutating, full-stack,
or destructive tests may still receive an additional per-task container.

## Recommendation and decision gates

Prototype candidate B in a disposable environment. Keep host RunPane plus the
current controlled workspace as the operational default until the prototype
passes. Do not migrate merely because the daemon starts.

Adoption requires evidence for:

- daemon, UI, and built-in Codex placement in one controlled boundary;
- restart and replacement persistence for every declared data class;
- two concurrent panes with the isolation classifications above;
- lightweight checks without app services and one isolated integration task;
- credential rotation, backup, restore, upgrade, and failed-upgrade recovery;
- archive cleanup and orphan reconciliation; and
- operation without any prohibited boundary bypass.

If those gates fail, keep the exec-based controlled-container model and improve
its launcher/lifecycle separately. Security isolation and task isolation remain
separate decisions in either outcome.

## Risks and evidence gaps

- The Linux daemon installer failed in release resolution; the failure may be
  wrapper-specific rather than a Pane runtime limitation.
- Built-in Codex launch inside a persistent runtime was not tested because this
  Issue's corrected execution boundary prohibited using Pane to run agents.
- UI transport, daemon authentication, and reconnection were not exercised.
- Daemon restart, container restart, replacement, image upgrade, backup, and
  restore were not exercised.
- Candidate-B prototype volumes may remain on the Docker host; cleanup was not
  authorized and is unverified.
- Worktree isolation was tested for repository-local state, not shared caches,
  ports, credentials, `/tmp`, Compose resources, or concurrent dependency
  installation.
- Pane upstream notes that full live remote end-to-end CI is currently limited;
  SoundAtlas must own its acceptance smoke test.

## Acceptance evidence map

| Acceptance criterion | Result | Evidence |
| --- | --- | --- |
| Actual RunPane and Codex location verified | Pass for current model | Host process inspection and disposable panel shells; current Codex is a separate VS Code process |
| Persistent containerized RunPane tested or shown infeasible | Pass for the supported bootstrap path | Latest and pinned wrapper-based Linux bootstrap attempts both failed before state; a direct-artifact workaround and live daemon remain adoption gaps |
| Current workspace compared with dedicated runtime | Pass | Candidate sections and alternatives matrix |
| Worktree creation and cleanup tested | Pass | Two panes, isolation marker, archive safety checks, and removed worktree paths |
| Main repository, worktree, and Pane persistence documented | Pass | Storage contract and restart-level requirements |
| Security mounts, credentials, Docker, and capabilities documented | Pass | Current models and effective-boundary sections |
| Cross-pane risks identified | Pass | Isolation classification table |
| Frontend/backend use evaluated without stack per pane | Pass | Services and developer workflow |
| Issue can start without a new development container | Pass for host baseline; conditional for target | Disposable host panes started immediately; target requires one already-running runtime |
| VS Code remains optional | Pass | Host panels work without VS Code; target workflow treats attachment as optional |
| Required alternatives compared | Pass | Alternatives matrix includes the four requested shapes plus current-workspace candidate |
| Recommendation separates security and task isolation | Pass | Conclusion and recommendation |
| Follow-up implementation Issues identified | Pass | Proposals below; none created |
| Architecture note includes required implications and risks | Pass | This document |

The failed supported bootstrap prevents adoption as a proven production
architecture, while satisfying this investigation's requirement to record an
evidence-backed infeasible path. It does not justify weakening the boundary,
treating the untested direct-artifact workaround as successful, or silently
converting upstream documentation into test evidence.

## Follow-up Issue proposals

Create these only after Human review of this recommendation:

1. **Prototype a pinned dedicated RunPane runtime.** Resolve the Linux release
   installer or consume a checksum-pinned official artifact; demonstrate
   sandboxed daemon/UI/built-in-Codex operation and clean teardown.
2. **Validate persistent state and recovery.** Exercise daemon restart,
   container restart, replacement, image upgrade, backup/restore, worktree path
   repair, and failed-upgrade rollback.
3. **Define runtime security and credential policy.** Specify mounts, UID,
   capabilities, seccomp/AppArmor, egress, secret seeding/rotation, update
   authority, logging, and incident cleanup.
4. **Implement pane resource isolation.** Enforce per-pane temporary paths,
   process environments, dependency policy, Compose names, ports, volumes, and
   orphan reconciliation.
5. **Add a SoundAtlas acceptance smoke test.** Verify two Issue panes,
   lightweight validation, one isolated full-stack task, optional VS Code
   attachment, archive cleanup, and recovery after interruption.
