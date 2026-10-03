# Development credentials

Host development and the backend/frontend Compose dev containers are supported.
The former workspace/devcontainer setup is retired. Host consumer configuration
is described below; component containers accept an individual application file
as documented in [local development](local-development.md#optional-provider-tasks).
Pane delivery remains separate and dependent on the integration work listed at
the end.

Normal application startup, setup and validation require no GitHub credentials.
Live YouTube enrichment needs a provider key; offline/dry-run work does not.
Authentication required to clone a private repository is separate from startup.

## Ownership and consumers

| Role | Owner / authoritative location | Consumer and delivery |
| --- | --- | --- |
| Application/provider credentials | SoundAtlas; one external `secrets/soundatlas/.env` | Media settings and YouTube runner read the selected file; only `YOUTUBE_API_KEY` and `SOUNDATLAS_USE_DUMMY_SERVICES` are supported |
| Host repository authentication | Developer/operator; existing Git credential manager and `gh` credential store | Host Git and ordinary `gh` use their own configured authentication |
| Dedicated user-based Project Tracker PAT | Developer/operator; independent external file, e.g. `secrets/github/project-tracker.env` | `scripts/gh_project.py` selects it explicitly and supplies `GH_TOKEN` to its child `gh` |
| Pane agent repository authentication | Pane Runtime; GitHub App private key and generated installation tokens | Runtime App resolver, Git credential helper and Runtime `gh` wrapper |
| Codex, OpenRouter, SSH and other Runtime authentication | Pane Runtime/operator; Runtime-managed files or persistent state | Their respective Runtime consumers; not the SoundAtlas application store |
| Dummy/test values | Synthetic fixtures and `.env.codex.example` | Offline tests and optional dummy fallback; never authoritative live credentials |

Spotify and Qobuz entries in the examples have no active provider credential
consumer. `github-agent.env` denotes Runtime's optional static repository-token
input; it is outside the target GitHub App model. SoundAtlas does not read it or
remove that Runtime mode. `github-project-agent.env` is an older Project PAT
filename and remains usable when explicitly selected. These are distinct roles;
the shared transport variable `GH_TOKEN` does not make them interchangeable.

## Select the application file on the host

Keep real values once in the external SoundAtlas application store. Configure
the location in the process environment. Replace these example absolute paths:

```powershell
$env:SOUNDATLAS_SECRETS_DIR = 'C:\external\secrets\soundatlas'
```

```sh
export SOUNDATLAS_SECRETS_DIR=/external/secrets/soundatlas
```

Media settings select the source in this order:

1. Non-empty `SOUNDATLAS_ENV_FILE`: an explicit file, including an individually
   attached file inside a receiving container. Existing relative paths remain
   relative to the command's working directory; absolute paths are recommended.
2. Non-empty `SOUNDATLAS_SECRETS_DIR`: an absolute, accessible directory outside
   the checkout, containing the existing application filename `.env`. Resolved
   paths are checked, so a directory alias into the checkout is rejected.
3. With neither setting, an optional repository-root `.env.codex` dummy file.
   `.env.codex.example` documents it; never put real values in the fallback.
4. Without a file, offline/dummy defaults.

The explicit file overrides the root even if that root is invalid. An invalid
selected root or file fails with a configuration error; it never falls back to
another file or to a process key. Selected files must be readable regular UTF-8
files. Check the path and file type when recovering from an error; do not create
a directory at a missing file path. An empty external application file is valid.

Non-empty supported process keys override values from a valid selected file.
An external file defaults to live mode, while fallback/no-file defaults to dummy
mode; `SOUNDATLAS_USE_DUMMY_SERVICES` can explicitly select either. Live YouTube
requests require a key and dummy mode disabled. GitHub keys are never imported
by the application file reader. The examples are not shell scripts and Python
commands do not automatically load repository `.env` configuration.

The path settings do not move, copy, rename or create credential files. Keep real
values out of repository-local `.env` files, source, logs and command examples.

## Select the independent Project credential

The operator supplies a dedicated file containing exactly one non-empty literal
`GH_TOKEN=...` assignment; blank lines and lines starting with `#` are allowed.
Do not use shell quoting, `export`, or other assignments in this file. The helper
does not evaluate shell code. The PAT is user-based and needs Project permissions
for the intended operation; ordinary repository authentication is a different
credential and is never its fallback.

```powershell
$env:SOUNDATLAS_GITHUB_PROJECT_ENV_FILE = 'C:\external\secrets\github\project-tracker.env'
python scripts/gh_project.py list
```

```sh
export SOUNDATLAS_GITHUB_PROJECT_ENV_FILE=/external/secrets/github/project-tracker.env
python scripts/gh_project.py list
```

The variable's SoundAtlas prefix names its consumer, not its owner. The helper
never derives this path from `SOUNDATLAS_SECRETS_DIR`. Existing filenames work
without migration. It replaces child `GH_TOKEN`, removes child `GITHUB_TOKEN`,
and keeps the parent environment unchanged. Missing/invalid configuration fails
before `gh` starts. Host Git and `gh` retain their existing independent login;
the Project helper does not configure them. The completion helper delegates
Project operations to this same explicit credential path.

## Pane delivery contract and remaining dependencies

Pane repository authentication targets a Runtime-owned GitHub App. For an
application task, attach only the authoritative application file, read-only,
and set `SOUNDATLAS_ENV_FILE` to its receiving-container path. A Project task
needs its own separately approved PAT file and explicit Project path setting.
Never mount the complete secret root. A Runtime credential mount is not
automatically available to a project container. The receiving container/task is
the access boundary; a file mount does not isolate arbitrary same-user processes.

Source evidence from Runtime revision
`3cae0988ee70ecc3bfd54304fb724b21b1de9993`, recorded in
[#269's Plan](https://github.com/gititinyoursoul/soundatlas/issues/269#issuecomment-5962011423),
recorded the following integration limitations:

- Historically, the broker selected the former devcontainer declaration before
  root Compose discovery. [#270](https://github.com/gititinyoursoul/soundatlas/issues/270)
  retires that SoundAtlas setup independently of Pane compatibility. This is not
  evidence that the external broker has been adapted or its integration verified.
- External attachment requires exact service/source/destination approval and
  protected host interpolation inputs. Project `.env` and `env_file` loading
  are unsupported. No approved replacement project route is claimed here.
- Runtime has no Python, and its `gh` wrapper selects repository/App auth even
  when the Project wrapper supplies a PAT through `GH_TOKEN`. The host helper
  therefore does not establish a working Pane Project route. Do not bypass the
  Runtime wrapper or install an alternative authentication path as a workaround.

[Runtime #37](https://github.com/gititinyoursoul/pane-dev-runtime/issues/37)
owns lifecycle evidence; [#267](https://github.com/gititinyoursoul/soundatlas/issues/267)
is related credential coordination. Their required project-selection and
Project-PAT delivery evidence still blocks full #269 acceptance. Host fixtures
and source inspection are not proof of live Pane delivery or token permissions.
