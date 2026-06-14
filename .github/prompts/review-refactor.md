# Review Refactor

Use this prompt to review a SoundAtlas refactor with a "trust but verify" mindset.

Context to provide
- Diff, PR, or changed files.
- Stated refactor goals and constraints.
- Expected stable behavior, API shapes, and seed data contracts.

Review focus
- Behavioral regressions in backend endpoints, frontend state, map/timeline filtering, or seed loading.
- Broken references between routes, places, events, and connections.
- Seed schema drift from `docs/seed-validation.md`.
- Missing or weakened validation and error handling.
- Frontend regressions: blank map, broken marker selection, stale Story Panel state, inaccessible filters.
- Missing tests or tests that no longer reflect behavior.
- Performance issues only when directly evident.

Output format
- Findings first, ordered by severity.
- Include concrete file references like `backend/app/main.py:12`.
- Separate assumptions and open questions.
- If behavior appears unchanged and coverage is sufficient, say so explicitly.
