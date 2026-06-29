# Current Screenshots

This directory stores the current approved screenshot set for SoundAtlas.

Workflow:

1. Capture temporary screenshots into `/workspace/screenshots/`.
2. Review them locally.
3. For the drawer states, run `cd /workspace/frontend && npm run capture:drawer`.
4. Copy the approved files into this directory.
5. Delete any older screenshots that should no longer represent the current
   baseline.

Keep filenames stable where possible so updated captures replace the previous
version instead of creating duplicates.
