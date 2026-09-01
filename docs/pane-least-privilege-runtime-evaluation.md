# Pane least-privilege Docker runtime evaluation

**Issue:** #194
**Test date:** 2026-09-02
**Status:** validated in a disposable container derived from the current
`soundatlas-workspace` image; no workspace configuration was changed.

## Conclusion

Pane can run without root, Docker capabilities, `--privileged`, a Docker
socket, `--no-sandbox`, or `seccomp=unconfined`. It needs a narrow custom
Seccomp profile because Docker's default profile rejects Chromium sandbox
namespace syscalls. `no-new-privileges` remains enabled.

The tested runtime started the Pane daemon, made it reachable from the local
Pane UI through an authenticated SSH tunnel, and ran Pane's built-in Codex agent
in a clean worktree as UID 10001. No Pane daemon port was published on the host.

## Baseline and cause

The baseline used a non-root user, `cap_drop: ALL`,
`no-new-privileges:true`, Docker's default Seccomp profile, no host mounts,
and an internal-only network. Electron exited with:

```text
The setuid sandbox is not running as root.
Failed to move to new namespace: PID namespaces supported, Network namespace
supported, but failed: errno = Operation not permitted
```

`chrome-sandbox` had the expected root-owned setuid mode (`4755`), but
`NoNewPrivs: 1` intentionally prevents that fallback. `strace` showed
Docker default Seccomp denying Chromium namespace creation:

```text
clone(CLONE_NEWUSER|SIGCHLD) = -1 EPERM
clone(CLONE_NEWPID|CLONE_NEWNET|SIGCHLD) = -1 EPERM
```

Turning only `no-new-privileges` off did not change the failure. A
diagnostic-only `seccomp=unconfined` run succeeded and showed:

```text
clone(CLONE_NEWUSER|SIGCHLD) = success
unshare(CLONE_NEWUSER) = success
clone(CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET|SIGCHLD) = success
chroot("/proc/self/fdinfo/") = 0
```

`clone3` remained Docker-default behaviour (`ENOSYS`), so no `clone3`
rule was added. Seccomp, not capabilities, Docker userns mode, or
`no-new-privileges`, is the original blocking control.

## Final runtime

The test image was derived from
`soundatlas-workspace@sha256:b068d1ecf2e81e37d95c9cfb492afaa07d3174369448636d1f31dc8696770529`.
It added Pane 2.4.95, its Linux dependencies, OpenSSH for authenticated
transport, and diagnostic tools. It created `soundatlas` (UID/GID 10001);
the runtime process never ran as root.

This Compose-equivalent configuration is the final tested shape. The named
volumes are initialized once by a separate disposable helper, then owned by
UID/GID 10001. The runtime has no added capabilities.

```yaml
services:
  pane:
    image: soundatlas-pane-runtime:probe
    user: "10001:10001"
    cap_drop: [ALL]
    security_opt:
      - no-new-privileges:true
      - seccomp:./pane-seccomp.json
    pids_limit: 512
    mem_limit: 3g
    cpus: 4
    networks: [pane-runtime]
    ports: ["127.0.0.1:53660:2222"] # SSH only
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=256m
      - /run:rw,nosuid,size=64m
    volumes:
      - pane-state:/runtime/pane
      - repo-cache:/runtime/repos
      - worktrees:/runtime/worktrees
      - codex-state:/home/soundatlas/.codex
      - tool-cache:/home/soundatlas/.cache
      - ssh-state:/home/soundatlas/.ssh
      - ./authorized_keys:/home/soundatlas/.ssh/authorized_keys:ro
      - ./codex-auth.json:/run/secrets/codex-auth.json:ro
      - ./sshd_config:/run/sshd_config:ro
networks: {pane-runtime: {}}
volumes: {pane-state: {}, repo-cache: {}, worktrees: {}, codex-state: {}, tool-cache: {}, ssh-state: {}}
```

The runtime mounts neither the host checkout nor a global home directory, and
never mounts `/var/run/docker.sock`. The only published port is SSH bound to
host loopback. The Pane daemon is loopback-only in the container and reached
through `ssh -L`.

## Final Seccomp profile

`pane-seccomp.json` is Docker/Moby v29.7.2's default profile, downloaded from
the v29.7.2 source (SHA-256
`536529b665dd0972c37bfb569f5d4ac8a53592e7b00752bc39ff063ca9864c74`), plus
only this patch. Retaining the upstream default preserves all other Docker
syscall restrictions.

```diff
@@ Docker default profile syscall rules
+{"names":["clone"],"action":"SCMP_ACT_ALLOW","args":[
+  {"index":0,"value":2114060288,"valueTwo":268435456,"op":"SCMP_CMP_MASKED_EQ"}]}
+{"names":["clone"],"action":"SCMP_ACT_ALLOW","args":[
+  {"index":0,"value":2114060288,"valueTwo":1879048192,"op":"SCMP_CMP_MASKED_EQ"}]}
+{"names":["unshare"],"action":"SCMP_ACT_ALLOW","args":[
+  {"index":0,"value":2114060288,"valueTwo":268435456,"op":"SCMP_CMP_MASKED_EQ"}]}
+{"names":["chroot"],"action":"SCMP_ACT_ALLOW"}
```

The mask is `CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET` (`2114060288`). It
permits only Chromium's observed user-namespace operations, not general
namespace creation. The unconditional `chroot` rule is needed after
unprivileged user-namespace creation and avoids adding `CAP_SYS_CHROOT`.

Reduction tests removed one allowance at a time:

- Removing `clone(CLONE_NEWUSER)` or `unshare(CLONE_NEWUSER)` reproduced
  the namespace `EPERM` failure.
- Removing the combined
  `clone(CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET)` made Electron abort during
  sandbox initialization.
- Removing `chroot` reproduced
  `sys_chroot("/proc/self/fdinfo/") == 0`.
- A separately observed `clone(CLONE_NEWPID)` call was not required by the
  final daemon path and was removed; the daemon still became ready.

## Verification matrix

| Check | Result | Evidence |
| --- | --- | --- |
| Electron sandbox | Pass | Chromium created its nested user namespace; no parent `--no-sandbox` argument was supplied. |
| Pane daemon | Pass | Headless daemon listened on its Unix socket and through the SSH-forwarded local endpoint. |
| Pane UI path | Pass | Authenticated SSH tunnel to the loopback-only daemon succeeded; the generated remote URI opened in the installed local Pane client. |
| Integrated Codex | Pass | Pane's built-in `codex` agent ran read-only checks in a clean Pane worktree as UID 10001. |
| Capabilities | Pass | `CapInh`, `CapPrm`, `CapEff`, `CapBnd`, and `CapAmb` were all zero. |
| `no-new-privileges` | Pass | `/proc/.../status` reported `NoNewPrivs: 1`. |
| Docker userns | Default | No Docker userns override was needed; Chromium creates the nested unprivileged user namespace. |

Headless D-Bus warnings were non-blocking. Pane's post-create hook also assumes
`/workspace`; it failed in Pane's generated worktree but did not prevent the
daemon or Codex terminal. Address that separately only if full devcontainer
post-create behaviour is required.

## Security assessment

This is a defensible least-privilege setup for a dedicated Pane runtime. The
only Docker-default relaxation is four tightly constrained syscall rules for
the observed Chromium sandbox path. It retains the rest of Docker's default
Seccomp restrictions, non-root execution, zero capabilities,
`no-new-privileges`, private container state, host-loopback SSH exposure, and
no Docker socket or source checkout mount.

The tested Pane daemon, remote UI path, and Codex workflow are reliable under
this profile. Treat the SSH private key and Codex authentication file as
short-lived secrets: provide them through an external secret mechanism, restrict
their permissions, and delete volumes when retiring the Pane.
