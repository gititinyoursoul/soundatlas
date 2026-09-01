# Agent Consumption Baseline

Issue: [#187](https://github.com/gititinyoursoul/soundatlas/issues/187)
Cohort: 30 top-level SoundAtlas Codex sessions
Period: 2026-08-07 14:29 UTC through 2026-08-29 10:07 UTC
Dataset: [consumption-baseline.csv](consumption-baseline.csv)
Context companion: [context-quality-baseline.md](context-quality-baseline.md)

## Executive summary

The historical traces make token and tool consumption substantially observable,
but not actual per-run monetary spend. Twenty-nine of the 30 confirmed sessions
contain cumulative token counters. Those runs report 773,047,915 total tokens:
770,295,057 input and 2,752,858 output tokens. The median was 17,199,430 total
tokens per run, with a range of 1,290,344 to 136,483,990.

Prompt caching dominates the token profile. Cached input accounts for
747,253,504 tokens, or 97.0% of reported input. Reasoning output accounts for
1,000,649 tokens, or 36.3% of reported output. These are subsets of the input
and output totals, respectively, and are not added again when calculating total
tokens.

The 30 traces contain 5,730 tool-call envelopes, with a median of 110.5 and a
range of zero to 984 per run. Repository interaction was present in 5,089
envelopes; 2,303 met the conservative discovery/search classification. An
envelope can contain several shell commands or nested tool operations, so these
figures are not file-read or command counts.

Actual paid US-dollar cost per run is unavailable. The Human confirmed that the
runs used a Codex Pro subscription, whose fixed monthly fee covers shared usage;
the traces do not record per-run billing, purchased credits, or a defensible way
to allocate that fee. At the 2026-09-01 rate snapshot, the 29 measurable runs
represent an estimated 8,198.455 Codex credit-equivalent units. Their normalized
API-equivalent comparison is $327.9382. Neither estimate is actual subscription
spend.

Long, multi-task sessions dominate every high-consumption group. The largest
token run and the two tool-call outliers all span several Issues or delivery
phases. The evidence supports a practical instrumentation conclusion: future
comparisons need a stable task identifier below the session identifier. It does
not support the conclusion that lower token use, less discovery, or a smaller
initial context is inherently better.

## Cohort and evidence

This report reuses the exact 30 session IDs confirmed and classified by Issue
#186. A run remains one substantive top-level Codex session rooted in the
SoundAtlas workspace, even when it contains several Human turns, Issues, or
implementation phases. The stable session ID is the join key for Issue #186,
this audit, and the future outcome audit in Issue #188.

Evidence came from local Codex JSONL traces and the sanitized Issue #186
dataset. The committed dataset contains task labels, counters, classifications,
and short evidence notes. It does not contain prompts, transcript excerpts,
reasoning content, tool inputs or outputs, credentials, account details, or
user-specific local paths.

Coverage is:

| Evidence | Runs | Status |
| --- | ---: | --- |
| Complete cumulative token counters | 28 | `reported` |
| Recoverable token counters with one malformed JSONL line | 1 | `partial` |
| No token-usage record | 1 | `unavailable` |
| Complete tool-call envelopes | 29 | `reported` |
| Recoverable tool envelopes with one malformed JSONL line | 1 | `partial` |
| Operation-envelope classifications | 29 complete, 1 partial | `derived` / `partial` |
| Credit/API comparison estimate | 28 | `estimated` |
| Recoverable estimate from malformed trace | 1 | `partial` |
| Actual paid USD per run | 0 | `unavailable` |
| Reliable retrospective phase attribution | 0 | `unavailable` |

Run `019ff0f0-29f6-79c0-b860-beda16bbc221` has one truncated JSONL line. Its
preceding cumulative counters and tool records are recoverable, but its row is
marked partial because the missing tail could contain additional activity. Run
`01a04cfd-444e-7772-88f0-daaa88ee10a2` contains the substantive request but no
agent response, tool call, or token-usage record.

## Measurement method

### Tokens and models

For each trace, the final monotonic `total_token_usage` record supplies input,
cached-input, cache-write-input, output, reasoning-output, and total tokens.
Every measurable row passed these checks:

- input tokens plus output tokens equal total tokens;
- cached-input plus cache-write-input does not exceed input tokens;
- reasoning-output does not exceed output tokens; and
- cumulative counters never decrease.

Intermediate cumulative records are not summed. Model-specific totals are
reconstructed from monotonic deltas and the active recorded model. This avoids
assigning an entire multi-model session to whichever model happened to run
last. All 29 measurable sessions had complete model attribution. Cache-write
input was zero throughout this cohort.

### Turns and tools

An agent turn is one explicit `task_started` event. A tool-call envelope is one
recorded `custom_tool_call` or `function_call`. The exact primary envelope
classes reconcile to the total:

| Primary envelope class | Count |
| --- | ---: |
| Execution/orchestration envelope | 5,458 |
| Wait envelope | 261 |
| Subagent envelope | 11 |
| Other envelope | 0 |
| **Total** | **5,730** |

The dataset also provides overlapping, conservative classifications based on
explicit recorded operations:

- `repository_interaction_envelopes`: Git, GitHub, repository commands, or
  named repository files appear in the envelope;
- `file_read_envelopes`: explicit search/list/read commands appear;
- `discovery_search_envelopes`: repository-state, Issue, history, listing, or
  search operations appear;
- `validation_envelopes`: an explicit test, validator, type, lint, or diff check
  appears;
- `github_cli_envelopes`: a GitHub CLI command appears; and
- `external_tool_operation_mentions`: explicit web, image, or MCP operations
  appear inside orchestration source.

These are envelope counts, not claims about attention, successful completion,
unique files, shell subcommands, or nested API requests. A single envelope may
appear in several overlapping classifications. The envelope existence and
outer call name are reported; the repository, read, discovery, validation,
GitHub, and external-operation labels are explicitly marked `derived` because
they come from a reproducible text taxonomy rather than first-class trace
fields.

### Cost and credit treatment

The primary cost proxy is estimated Codex credit-equivalent consumption using
the official [Codex pricing rate card](https://learn.chatgpt.com/docs/pricing)
retrieved on 2026-09-01:

| Model | Input credits / 1M | Cached-input credits / 1M | Output credits / 1M |
| --- | ---: | ---: | ---: |
| GPT-5.6 Sol | 100 | 10 | 500 |
| GPT-5.6 Terra | 50 | 5 | 300 |
| GPT-5.6 Luna | 5 | 0.5 | 30 |

For each model, the estimate is:

`uncached input × input rate + cached input × cached rate + output × output rate`

Reasoning output is already included in output tokens. Credit estimates do not
claim that included subscription usage caused a separate debit.

The secondary comparison uses the 2026-09-01 official
[API model rate snapshot](https://developers.openai.com/api/docs/models/compare):
Sol at $4/$0.40/$20, Terra at $2/$0.20/$12, and Luna at
$0.20/$0.02/$1.20 per million uncached-input/cached-input/output tokens. It is a
normalized repricing of the observed tokens, not a historical invoice, marginal
subscription charge, or recommendation to use API billing. The estimate uses
standard-speed rates because the historical trace does not expose a billable
speed multiplier. No recorded request exceeds the current 272,000-input-token
long-context threshold (the observed maximum is 234,486), so no long-context
multiplier is applied.

## Aggregate baseline

| Signal | Available runs | Median | Range | Cohort total |
| --- | ---: | ---: | ---: | ---: |
| Total tokens | 29 | 17,199,430 | 1,290,344–136,483,990 | 773,047,915 |
| Input tokens | 29 | 17,156,843 | 1,280,678–136,124,972 | 770,295,057 |
| Cached-input tokens | 29 | 16,454,400 | 1,217,536–133,318,912 | 747,253,504 |
| Output tokens | 29 | 42,587 | 8,876–359,018 | 2,752,858 |
| Reasoning-output tokens | 29 | 15,851 | 3,695–150,830 | 1,000,649 |
| Agent turns | 30 | 15 | 1–139 | 782 |
| Tool-call envelopes | 30 | 110.5 | 0–984 | 5,730 |
| Repository-interaction envelopes | 30 | 90 | 0–813 | 5,089 |
| File-read envelopes | 30 | 36 | 0–291 | 1,885 |
| Discovery/search envelopes | 30 | 43.5 | 0–302 | 2,303 |
| Validation envelopes | 30 | 22.5 | 0–196 | 1,111 |
| Estimated Codex credits | 29 | 140.757 | 1.206–906.378 | 8,198.455 |
| API-equivalent USD comparison | 29 | $5.6303 | $0.0483–$36.2551 | $327.9382 |

The aggregate cache-hit share is 97.0% of input tokens. This makes raw input
tokens a poor cost proxy by themselves: uncached input and output have materially
different credit weights. Likewise, output tokens are only 0.36% of total
reported tokens but still materially affect credit-equivalent consumption.

## Model and workload structure

Model participation is not mutually exclusive: Sol appears in 26 runs, Terra
in 14, and Luna in nine. Sixteen of the 29 measurable runs use more than one
model.

| Model composition | Runs | Median total tokens | Median tool calls | Median estimated credits |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol only | 11 | 9,338,521 | 65 | 140.757 |
| GPT-5.6 Terra only | 1 | 17,485,454 | 139 | 124.352 |
| GPT-5.6 Luna only | 1 | 1,290,344 | 22 | 1.206 |
| Multi-model | 16 | 21,259,029.5 | 153 | 242.0215 |

These are workload descriptions, not model-efficiency comparisons. The
multi-model sessions generally contain more tasks, subagent activity, and
delivery phases. The cohort does not control for task difficulty or outcome.

## Outliers

Outliers use the reproducible upper-fence rule `Q3 + 1.5 × IQR`.

Four runs exceed the 70,002,763.5-token fence:

| Run | Task label | Total tokens | Tool calls |
| --- | --- | ---: | ---: |
| `019fdca0-bb23-7101-b3d8-7079c4b52568` | Implement pipeline and review changes across several Issues | 136,483,990 | 984 |
| `01a04778-d0fa-7bf1-82c0-27681ce5a9ab` | Revise navigation and deliver several frontend workflow Issues | 99,984,347 | 712 |
| `019fe871-8db8-7fd2-a6d2-4c39fbfa6339` | Evolve pipeline review and Git delivery workflow | 73,084,121 | 514 |
| `01a04777-6fb0-7382-a2f0-0b862f216252` | Continue experimental route stages and editorial handoff | 71,212,608 | 503 |

The first two also exceed the 527.25 tool-call fence. Five runs exceed the
188.5 discovery-envelope fence: the four token outliers above plus the Disco
editorial-handoff and replay-authoring run. This overlap identifies long,
multi-Issue sessions as the main investigation target. It does not show that
discovery caused the token consumption.

Credit-equivalent consumption has no Tukey upper-fence outlier. Its maximum,
906.378 credits, belongs to the pipeline-review and Git-delivery run rather than
the highest-token run. Model mix and the cached/uncached/output composition
change the ranking, which is why total tokens and cost proxy should remain
separate metrics.

## Relationship to context

The Issue #186 classifications allow descriptive comparisons with common join
keys:

| Context group | Runs with tokens | Median total tokens | Median tool calls | Median discovery calls |
| --- | ---: | ---: | ---: | ---: |
| Initial context sufficient | 11 | 6,872,715 | 63 | 29 |
| Initial context insufficient | 18 | 27,092,210 | 186.5 | 80.5 |
| Context problem observed | 10 | 24,203,021 | 169.5 | 77 |
| No context problem observed | 19 | 9,338,521 | 65 | 30 |
| Rework observed | 20 | 20,286,433.5 | 148 | 45 |
| No rework observed | 9 | 9,338,521 | 63 | 28 |

The same 18 runs marked as requiring discovery before useful work are the runs
whose initial context was insufficient under Issue #186's definitions; their
median values therefore match in this cohort.

These associations do not establish causality. The higher-consumption groups
also contain broader multi-Issue sessions, concept and workflow development,
implementation, validation, and Human-directed correction. Larger initial
context might increase prompt tokens, while better context might prevent
rework; this retrospective session-level dataset cannot isolate either effect.

## Phase attribution

Reliable phase-level consumption is unavailable for all 30 runs. The traces
record ordered turns, counters, messages, and tool calls but no stable task or
phase identifiers. Several sessions switch Issues or return from implementation
to planning and correction. Assigning token deltas to phases from command names
or prose would create false precision.

Future phase attribution requires:

- a stable task ID below the session ID;
- explicit phase-transition events for understanding, discovery, planning,
  implementation, validation, and correction;
- per-request token usage tied to task, phase, model, and reasoning effort;
- nested tool-operation records tied to the same identifiers; and
- explicit markers when Human feedback or validation causes rework.

## Observability gaps

- **Actual subscription cost:** no per-run invoice, included-quota debit,
  purchased-credit use, or subscription allocation is recorded.
- **Included usage versus purchased credits:** the traces record model tokens,
  not which account bucket funded them.
- **Task boundaries:** a session can span many Issues and outcomes, making a
  session too coarse for causal or efficiency comparisons.
- **Tool granularity:** outer envelopes can contain many shell or nested tool
  operations; unique commands and files are not first-class events.
- **Phase:** no explicit phase or transition marker exists.
- **Attention and value:** a file read or tool call does not show whether its
  result changed a decision or prevented rework.
- **Partial trace health:** one truncated JSONL line is observable only during
  retrospective parsing; the trace does not contain its own completeness flag.
- **Outcome linkage:** Issue, commit, validation, and follow-up outcomes must be
  reconstructed rather than joined through stable task metadata.

## Recommended automatic instrumentation

1. Emit stable session, task, Issue, parent/subagent, and turn IDs on every
   usage and tool event.
2. Emit per-request and cumulative token counters with model, reasoning effort,
   cached-input, cache-write-input, output, and reasoning-output fields.
3. Record the authenticated billing mode (`subscription`, `purchased credits`,
   or `API key`) and rate-card version without exposing account or payment data.
4. Record outer tool envelopes and nested operations separately, including
   operation type, target class, duration, completion status, and a sanitized
   discovery/validation/write reason.
5. Emit explicit task and phase transitions and a marker when new context,
   validation, or Human feedback changes the approach.
6. Link tasks to Issues, local commits, validations, push results, and outcome
   review so consumption can be compared with delivered value.
7. Emit trace-completeness and dropped-event counters so partial records are
   detected at collection time.

## Reusable metrics

Future cohorts should retain these definitions with explicit available-value
denominators:

- **Total tokens per run/task:** final reported input plus output tokens.
- **Cached-input share:** cached-input tokens divided by input tokens.
- **Output share:** output tokens divided by total tokens.
- **Reasoning-output share:** reasoning-output tokens divided by output tokens.
- **Agent turns per run/task:** explicit task-started events.
- **Tool-call envelopes per run/task:** outer recorded calls, kept separate from
  nested operation counts.
- **Repository interaction intensity:** repository-classified envelopes per
  run/task.
- **Discovery intensity:** discovery/search envelopes per run/task.
- **Validation intensity:** validation envelopes per run/task.
- **Estimated Codex credits:** normalized model-attributed tokens repriced with
  a named rate-card snapshot.
- **Actual-cost coverage:** runs with a direct per-run billed amount divided by
  audited runs; zero in this cohort.
- **Phase-attribution coverage:** runs/tasks with explicit usage-bearing phase
  events divided by audited runs/tasks; zero in this cohort.
- **Partial/unavailable rate:** rows with incomplete or absent evidence divided
  by the cohort.

Raw token and operation counters should remain available so a later audit can
reprice usage or revise classifications without rewriting historical evidence.
These metrics describe consumption, not quality or efficiency by themselves.

## Limitations

- The 30 sessions are a deliberately selected SoundAtlas workflow cohort, not a
  random sample of all Codex work.
- Sessions differ materially in duration, task count, model mix, complexity,
  and outcome.
- Credit and API-equivalent estimates use a 2026-09-01 snapshot rather than a
  historical bill and may not reproduce account-side quota behavior.
- Envelope classifications are conservative text-based reconstruction and can
  undercount dynamic operations or overstate a tool's decision value.
- One trace is partial and one contains no agent activity.
- Session-level context comparisons are descriptive associations with
  confounding workload differences.
- No conclusion here establishes that lower context, fewer tokens, fewer tool
  calls, or lower estimated credits would have produced a better result.
