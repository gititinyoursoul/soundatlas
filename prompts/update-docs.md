# Update Docs

Compatibility wrapper for the `soundatlas-documentation-implementation` skill.

Use this historical prompt entrypoint when planning or implementing approved
SoundAtlas documentation work. The reusable skill owns document classification,
source-of-truth analysis, related-reference discovery, documentation boundaries,
validation, reporting, and post-commit lifecycle:

`.codex/skills/soundatlas-documentation-implementation/SKILL.md`

Provide the approved Issue number or URL and, when useful, optional context:

- target documentation area or file
- related product, architecture, workflow, or source-of-truth decision
- whether the output is a plan, approved edit, audit, or archive update
- formatting or validation commands

The approved GitHub Issue remains the scope authority. This wrapper does not
replace `soundatlas-issue-planning` for Issue intake or Plan Updates,
does not authorize implementation by itself, and does not replace the required
Grill-Me/Plan Update gates for risk-flagged work.
