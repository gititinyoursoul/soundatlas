# Tracked Screenshot Evidence

This directory preserves reviewed screenshot evidence for SoundAtlas. A file
here does not by itself establish that it represents the current product
surface.

## Current status

`drawer-closed-desktop.png`, `drawer-expanded-desktop.png`, and
`drawer-routes-desktop.png` were captured before the current first-level
`Routes` and `Routes to review` navigation. They remain historical evidence and
must not be used to verify the current route-navigation baseline. A future
replacement capture requires Human approval before it becomes current visual
evidence.

## Replacement workflow

1. Capture temporary screenshots into `/workspace/screenshots/`.
2. Review them locally against the current intended design baseline.
3. For drawer states, run `cd /workspace/frontend && npm run capture:drawer`.
4. Obtain Human approval for the replacement set and its stated coverage.
5. Copy approved files into this directory and update this status section.

Keep stable filenames only when a new approved capture intentionally replaces
the prior evidence. Do not delete historical files merely because a newer
design exists.
