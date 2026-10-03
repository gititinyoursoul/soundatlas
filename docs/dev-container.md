# Retired Workspace Setup

The dedicated SoundAtlas workspace container and `.devcontainer` files were
removed by [Issue #270](https://github.com/gititinyoursoul/soundatlas/issues/270).
This page preserves historical inbound links; it is not a startup guide.

Use [local development](local-development.md) for host or component-container
setup, validation, static builds, and Chromium checks. Backend and frontend dev
images own their development tools. Neither component needs a production image
for this workflow. Pane compatibility is outside this SoundAtlas migration.

Existing workspace containers and cache volumes are not automatically deleted.
Do not use volume deletion as routine migration or cleanup.
