# Dedicated RunPane Runtime Prototype

## Outcome

Candidate B is blocked under the security boundary approved for Issue #193.
The pinned Pane package was verified and installed in a dedicated Linux image,
and the disposable runtime met the planned container, mount, credential, and
network restrictions. Pane could not start its daemon as the fixed non-root
user while both `no-new-privileges` and Docker's default seccomp profile were
active. Electron reported that its setuid sandbox could not run with
`no-new-privileges`, then failed to create the namespace required by its other
sandbox path with `EPERM`.

The test did not add `--no-sandbox`, `seccomp=unconfined`, a privileged mode,
an added capability, or a host-control socket. Because daemon startup is a
prerequisite for the UI, Pane worktree, and built-in Codex stages, those stages
are recorded as blocked rather than inferred from upstream documentation.

SoundAtlas should retain the current controlled-workspace execution model. It
should not proceed to Candidate B persistence and recovery validation until a
separately planned prototype demonstrates a normal Electron sandbox with a
restrictive container policy. This result does not authorize a runtime
migration or change the current RunPane workflow.

## Scope and evidence method

The prototype ran on 2026-09-01 from the normal Codex-owned Issue #193
worktree. RunPane was only the disposable system under test; it did not host
planning, repository implementation, or review.

Evidence labels used below are:

- **Tested**: observed directly in the disposable runtime.
- **Inspected**: read from the image, container, process, or repository state.
- **Upstream contract**: documented by the selected Pane release.
- **Blocked**: a prerequisite failed without an approved boundary-preserving
  path to the dependent stage.
- **Evidence gap**: deliberately not claimed because the prerequisite was not
  reached.

Private host paths, user names, tokens, connection codes, key material, raw
environment values, and unredacted logs are omitted. The runtime never mounted
the SoundAtlas host checkout or Git common directory.

## Version and provenance ledger

| Item | Pinned or observed value | Evidence |
| --- | --- | --- |
| SoundAtlas baseline | `02b154a3bdfd3697418d25fae8e183c7a923b9e4` | Clean runtime-owned clone of `main` |
| Pane package | `Pane-2.4.95-linux-amd64.deb` | Official [Pane v2.4.95 release](https://github.com/dcouple/Pane/releases/tag/v2.4.95) |
| Pane package SHA-256 | `4de2274ecd9617e642bb06b430c210da28052151d090aa0ade94f19368482265` | Compared successfully before package installation with the release checksum |
| Pane source revision | `5ac1b04831746724d84ab5b0a3487ac11a150c05` | Release provenance |
| RunPane wrapper | `2.4.95` | Runtime command |
| Codex CLI | `0.147.0` | Runtime command |
| Runtime base | `node@sha256:48abc13a19400ca3985071e287bd405a1d99306770eb81d61202fb6b65cf0b57` | Digest-pinned build input |
| `uv` build stage | `ghcr.io/astral-sh/uv@sha256:531f855bda2c73cd6ef67d56b733b357cea384185b3022bd09f05e002cd144ca` | Digest-pinned build input |
| Final disposable image | `sha256:c7fb5848a362d4145abfd90e8d47ac4daac20496c509ab88fb1314d2d5b46959` | Local image inspection before teardown |
| Runtime tools | Node `24.11.1`, npm `11.6.2`, Python `3.11.2`, `uv` `0.9.30`, Git `2.39.5` | Independent runtime commands |
| Container engine | Docker client/server `29.7.2`, Linux/amd64 Docker Desktop engine | Host inspection |

The checksum-pinned official package bypassed only the RunPane wrapper's
previously observed artifact-resolution failure. Pane's daemon and worktree
behavior were not replaced. Package installation required the normal packaged
runtime dependencies plus `libgbm1` and `libasound2`; both missing-library
failures were corrected in the disposable build context without changing the
runtime security policy.

## Reproducible runtime shape

The test used the unique prefix `soundatlas-193-20260901a`. Its build context
was outside the repository. The image fixed UID and GID `10001`, installed the
verified Pane package, RunPane, Codex, Git, Node, Python, and `uv`, and ran the
container as that non-root identity. GitHub CLI was not installed because no
prototype step required GitHub access.

The runtime used:

- dropped Linux capabilities (`ALL`), `no-new-privileges`, Docker's default
  seccomp filter, no privileged mode, no host PID or network namespace, a
  512-process limit, 3 GiB memory limit, and four-CPU limit;
- one private Docker network and only one dynamically assigned SSH port
  published on host loopback;
- runtime-owned volumes for `PANE_DIR`, repositories, sibling worktrees, Codex
  state, caches, and SSH host state;
- read-only single-file inputs for the disposable SSH public key, SSH daemon
  configuration, Codex authentication, and a dedicated minimal Codex
  configuration; and
- no Docker or Podman socket, broad host directory, host repository, host Git
  state, writable host credential directory, application secret, or ambient
  token.

An initial unexercised container mounted the host Codex configuration file too
broadly for the planned credential boundary. It was stopped and removed before
Pane setup, then replaced with a dedicated minimal configuration file. All
reported test evidence comes from the corrected container.

The runtime-owned repository was cloned at `/runtime/repos/soundatlas`. It was
clean on `main` at the recorded baseline. Pane state, repositories, worktrees,
Codex state, caches, and SSH state were isolated from all pre-existing
SoundAtlas and Pane state.

## Observed execution

### Artifact and repository baseline

The downloaded Pane package matched the published SHA-256 value before
installation. Runtime commands reported Pane and RunPane `2.4.95` and Codex
`0.147.0`. The runtime-owned SoundAtlas clone was clean. Running
`python scripts/check_doc_references.py` directly in that clone completed with
`Documentation references are valid on active guidance surfaces.` No frontend,
backend, database, or application service was started.

This direct command proves the runtime's lightweight repository baseline. It
does not substitute for the blocked built-in Codex probe.

### Authenticated exposure baseline

A non-root SSH daemon listened on the container's port `2222`; Docker published
that port only on a dynamically allocated host-loopback endpoint. A disposable
Ed25519 key authenticated successfully from the host and returned UID/GID
`10001`. No Pane daemon port was published directly.

The planned SSH local forward and Pane pairing could not be completed because
Pane never created its loopback daemon listener or usable connection code. The
SSH result therefore proves the approved exposure mechanism's transport shape,
not a Pane UI connection.

### Daemon blocker

Both a direct packaged-runtime probe and the official command
`runpane install daemon --pane-path /usr/bin/pane` reached the same failure.
Electron reported:

```text
The setuid sandbox is not running as root.
Failed to move to new namespace: ... errno = Operation not permitted
```

The packaged `chrome-sandbox` helper was owned by root with setuid permissions,
but process inspection showed `NoNewPrivs: 1`, zero inherited, permitted,
effective, bounding, and ambient capabilities, and `Seccomp: 2`. The Pane and
`chrome-sandbox` child processes exited before a Pane listener appeared.
`runpane doctor --json` consequently reported the daemon socket absent and the
daemon unreachable.

Disabling Electron's sandbox or using unconfined seccomp would have violated
the authorized boundary. The prototype stopped at this phase. No Pane session,
sibling worktree, built-in Codex process, imported remote UI profile, or Pane
bearer credential was created.

## Boundary audit

| Boundary property | Result | Direct evidence |
| --- | --- | --- |
| Fixed non-root runtime identity | Pass | UID/GID `10001`; Pane probes ran as that identity |
| Capabilities | Pass | All five capability masks were zero; container dropped `ALL` |
| Privilege and namespaces | Pass | `Privileged=false`; no host PID or host network mode |
| Seccomp and privilege escalation | Pass | `Seccomp: 2`; `NoNewPrivs: 1`; no unconfined override |
| Host-control sockets | Pass | Docker and Podman socket paths absent |
| Host mounts | Pass | Only six runtime volumes and four read-only single-file inputs |
| Credential handling | Pass | Narrow read-only inputs seeded runtime-owned state; contents not logged |
| Network exposure | Pass for transport shape | Only SSH published on host loopback; no Pane port published |
| Pane loopback listener and authentication | Blocked | Daemon exited before listener and pairing state existed |
| Prohibited workaround use | Pass | No `--no-sandbox`, privilege, host namespace, added capability, or unconfined seccomp |

The boundary compliance result means the attempted runtime respected the
approved restrictions. It does not claim that a functioning Pane daemon was
contained, because daemon startup failed first.

## Persistence responsibility

| Data class | Prototype responsibility | Tested persistence |
| --- | --- | --- |
| Pane state (`PANE_DIR`) | Dedicated runtime volume | Setup failure files only; restart and replacement untested |
| Base repository and Git common data | Dedicated repository volume | Clean clone verified; restart and replacement untested |
| Sibling Pane worktrees | Dedicated worktree volume | None created because daemon startup was blocked |
| Codex configuration and login state | Dedicated volume seeded from narrow read-only inputs | Version command worked; agent login/execution and rotation untested |
| Tool and dependency caches | Rebuildable dedicated cache volume | Present only for the disposable run; recovery untested |
| SSH host state | Dedicated volume | Public-key login tested; restart and rotation untested |

Daemon restart, container restart, image replacement, backup, restore, upgrade,
failed-upgrade recovery, worktree path repair, and credential rotation remain
evidence gaps. This failed core prototype provides no basis to start the
separate persistence/recovery validation.

## Result matrix

| Stage | Result | Evidence or blocker |
| --- | --- | --- |
| Official artifact integrity | Pass | Official package checksum matched before installation; installed version was `2.4.95` |
| Dedicated image and runtime creation | Pass | Digest-pinned image and isolated non-root container started |
| Pane daemon startup | Blocked | Normal Electron sandbox could not initialize with `no-new-privileges` and default seccomp |
| Authenticated Pane UI connection | Blocked | SSH loopback transport worked, but no Pane listener or pairing state existed |
| RunPane Pane and sibling worktree creation | Blocked | Requires the unavailable Pane daemon |
| Built-in Codex execution | Blocked | Requires a Pane/worktree; no compatibility launcher was substituted |
| Security-boundary compliance | Pass | No prohibited socket, mount, namespace, capability, privilege, sandbox flag, or seccomp override |
| Lightweight repository validation | Pass with limitation | Documentation reference check passed directly in the runtime-owned clone, not through built-in Codex |
| Exact shutdown and cleanup | Pass | No Pane/profile/worktree existed; exact container, six volumes, network, images, key material, and build context were removed |

## Cleanup evidence

The failed Pane and sandbox processes were stopped with the container. Cleanup
then removed the exact `soundatlas-193-20260901a` container, its six labeled
volumes, private network, prototype image, newly pulled Node base image,
disposable SSH key and known-host record, generated configuration, setup logs,
and temporary build context. The `uv` base image predated the run and was left
untouched.

Post-run inventory reported zero containers, volumes, networks, and images with
the prototype identity, and the temporary directory no longer existed. No Pane
archive or remote-profile removal was necessary because neither was created.
Pre-existing Issue #192 resources and all existing SoundAtlas, Pane, repository,
worktree, and credential state were left outside the cleanup scope.

Docker BuildKit may retain content-addressed build cache shared by the engine;
it has no unique Issue resource identity and was not broadly pruned. No runnable
prototype resource or named prototype state remains.

## Recommendation

Retain the current controlled SoundAtlas workspace execution model. Candidate B
has a clean conceptual ownership boundary, but this prototype did not establish
its required daemon/UI/built-in-Codex path without weakening the accepted
security policy.

A future Intake may investigate a documented, sandbox-compatible restrictive
profile or a dedicated VM boundary. It must preserve the normal Electron
sandbox and provide direct daemon evidence before persistence/recovery work is
useful. This Issue neither creates that follow-up nor changes production,
workspace, RunPane, or application configuration.
+

## Corrective rerun — 2026-09-02

Issue #194 supplied the missing Seccomp evidence. A new disposable image was
derived from the same workspace-image digest and verified the official Pane
2.4.95 package checksum. Its profile started from Docker/Moby v29.7.2 default
Seccomp and added only the four #194 rules for Chromium's observed
`clone(CLONE_NEWUSER)`,
`clone(CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET)`,
`unshare(CLONE_NEWUSER)`, and `chroot` path.

The result changes the prior Electron/daemon conclusion:

| Corrective check | Result | Evidence |
| --- | --- | --- |
| Electron namespace sandbox | Pass | Headless Pane reached `Headless host ready` with the constrained profile; no parent `--no-sandbox` flag. |
| Pane daemon | Pass | Daemon created and listened on its Unix socket. |
| Boundary controls | Pass | Runtime UID/GID 10001; all `Cap*` masks zero; `NoNewPrivs: 1`; `Seccomp: 2`. |
| Runtime-owned clone and Pane worktree | Pass | RunPane registered the cloned repository and created a sibling `seccomp-rerun` worktree. |
| Built-in Codex panel | Partial | The built-in Codex panel initialized with scoped runtime-owned auth, but the Pane CLI create path left its terminal at a shell and injected malformed input; no read-only Codex probe was claimed. |
| Authenticated remote UI | Evidence reused | #194 verified the same loopback-only SSH forwarding and local Pane-client connection path. It was not repeated in this short corrective run. |
| Exact cleanup | Pass | The Pane was archived after a clean-worktree check; the exact container, image, profile, and temporary context were removed. |

The narrowed Seccomp profile therefore resolves the original #193 blocker while
retaining the required least-privilege boundary. The remaining direct evidence
gap is a successful bounded Codex command through the Pane create API; it is an
implementation/tooling defect, not grounds to relax the container profile.
