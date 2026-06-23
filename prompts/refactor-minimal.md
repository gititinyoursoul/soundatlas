# Refactor Minimal

Use this prompt for low-risk cleanup that improves readability without changing SoundAtlas behavior.

Context to provide
- Target files or directories.
- Known pain points: unclear names, long functions, repeated parsing, awkward component state, or schema duplication.
- Constraints: API stability, seed schema stability, UI behavior, or content wording to preserve.

Task
- Refactor naming, clarity, and structure only.

Project constraints
- Keep behavior identical, including edge cases.
- Do not change API response shapes, seed file shapes, or route IDs unless explicitly requested.
- Do not edit historical content unless the task is content cleanup.
- Avoid drive-by formatting, broad rewrites, or unrelated cleanup.
- Prefer existing local patterns over new abstractions.

Process
- Start with a short plan.
- Make the smallest reasonable diff that improves readability.
- For backend changes, run targeted tests if available.
- For frontend changes, run the narrowest available build or smoke check if available.
- For seed/data changes, validate JSON and references if tooling exists.

Deliverables
- Code or data changes.
- Brief summary of what changed and why.
- Validation run and outcome, or a clear reason why validation could not be run.
- Suggested commit message.
