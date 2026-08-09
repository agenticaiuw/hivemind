# Harness derivation — unified — round 239

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live interrupted-ledger signal** — GET /ledger/interrupted currently reports 2 interrupted ledgers, including one with status open and one inflight step; this is a real signal suitable for the departure/continuation capabilities, but it must be treated cautiously because stale records can still exist.
  - evidence: describe GET /ledger/interrupted returned HTTP 200 at 2026-08-09T01:06:00Z with count 2 and progress.inflight=1

## Capabilities it proposed

### "“Continue the thing I was doing before the interruption, but tell me exactly what is already done and stop before repeating anything.”"
- **useful because:** This is the highest-value cross-surface capability: after a Mac/browser crash or a dropped conversation, the owner gets a safe continuation rather than a duplicate email, form submission, or file edit. It joins the pendant's spoken intent with the relay job, Mac workbench context, browser session, and durable receipts, then requires the physical approval latch only for a non-replay-safe step.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** planner for reconstructing the interrupted intent and selecting the next step; deterministic policy and receipts for replay gating; realtime only to explain the result over the pendant
- **latency:** 2–5 s to produce a spoken checkpoint; no action until the owner approves a blocked step; under 1 s to resume an idempotent/additive step after approval
- **cost:** Usually one planner call plus deterministic reads, roughly $0.01–$0.05; browser/Mac latency dominates, not tokens
- **security:** Never infer completion from a missing receipt. Bind continuation to jobId, workbench context, browser session, plan digest, and world fingerprint; auto-run only replaySafety idempotent/additive, block unrepeatable/unknown and off-machine actions; show redacted destinations before physical approval. Requires fixing false interrupted ledgers and adding relay job leases first.
- **missing:** Orchestrator must close successful ledgers; relay_jobs lease_until and requeue sweep; A production caller that turns GET /workbench/jobs/:jobId/handoff and /workbench/contexts/:contextId into a continuation plan; A delivery path for physical_transaction_approval_latch decisions; A dashboard/pendant checkpoint card that persists until resolved

### "“Before I leave my Mac, tell me what will expire, get stuck, or become unsafe while I’m away, and give me one safe action for each.”"
- **useful because:** The system currently exposes jobs, browser leases, routines, pending approvals, audio delivery, and device health as separate facts. This turns them into a departure check: the owner learns that a browser command lease is about to orphan, a relay job has no lease, an approval will expire, or an audio item is waiting, before the failure happens.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic deadline/lease classification first; background model only to rank and phrase the findings; realtime reads the short departure report
- **latency:** Under 2 s for a local snapshot and under 5 s if browser/relay probes are needed; repair actions are separately confirmed
- **cost:** <$0.01 per check; mostly HTTP snapshots and no model call when the rule engine can classify all items
- **security:** Read-only by default. Report exact expiry timestamps in America/New_York for Mac-resolved events and never invent a pendant timezone. Do not wake, cancel, or repair anything without an explicit second command; redact URLs, message text, and account names.
- **missing:** A normalized deadline schema across relay jobs, browser command leases, approval TTLs, routines, workbench contexts, and pendant inbox/outbox; A scheduler or launchd trigger for a departure check and a single owner acknowledgement; Typed safe-repair plans that distinguish wake/requeue/renew from destructive cancellation

### "“Show me every action I physically approved, what exact target it was bound to, and whether the world changed afterward.”"
- **useful because:** The pendant’s physical approval is a meaningful security boundary, but today there is no owner-facing ledger proving what that gesture authorized or whether the approved action actually completed. This gives the owner an audit they can understand: nonce, time, redacted target, plan digest, pre-state, post-state, result, and any mismatch—without conflating an approval with execution.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic receipt join and state comparison; a cheap background model may summarize a long list, but the facts and verdicts must never be model-inferred
- **latency:** Interactive lookup under 2 seconds for the last 30 days; export generation under 10 seconds
- **cost:** Near-zero model cost; dominated by receipt/index reads and optional dashboard rendering
- **security:** The audit must expose only redacted targets and never secrets or page contents. Bind each record to the physical nonce, plan digest, world fingerprint, executor receipt, and postcondition evidence. Make it append-only and distinguish approved, dispatched, completed, refused, expired, and world-moved. Do not allow the audit view itself to execute or undo actions.
- **missing:** A durable relay index for physical approval events and their delivery acknowledgements; A join key propagated from the pendant nonce through prepare/approve, execute, browser command, and postcondition receipt; A typed postcondition/evidence record for Mac and browser mutations; Dashboard and pendant speech views for the audit, plus export/redaction policy


## Changes it proposed to its own stack

### `browser-harness` — Add a field-level mutation guard around browser actions: before a submit/click that can change remote state, capture a redacted structural snapshot of the bound form/page; immediately before dispatch re-read it, compute a changed-field diff, and invalidate the command if the target or any user-visible value moved. Return a signed pre/post diff receipt rather than only success/failure.
- **owner gets:** A stale browser tab can otherwise submit the wrong price, recipient, appointment, or account setting after a page changes. The owner gets a concrete “the page changed, so I did not send it” instead of trusting a generic approval or a green job status.
- effort: Medium: browser bridge snapshot schema, canonical redaction/diffing, command binding, tests for navigation and dynamic forms.  ·  risk: Some legitimate dynamic pages will invalidate too often; recover by offering a fresh preview, never by silently retrying. Avoid retaining page contents; hash or redact sensitive values.
- cost: Negligible API cost; a few hundred milliseconds and small receipt storage per mutating command.  ·  latency: Adds one bounded inspect round-trip, typically 200–800 ms before mutation.
- security: Improves least privilege and prevents confused-deputy submits; snapshots must be scoped to the bound tab and must exclude secrets/password fields.
- depends on: A typed browser command target/session binding; GET /browser/status and browser session identity; POST /browser/inspect; POST /browser/result/:commandId; Physical transaction approval latch for actions that remain high-risk


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate directions: (1) the highest-value capability, safe continuation of interrupted work using replaySafety, workbench handoffs, browser state, receipts, and the physical approval latch; (2) a departure check that tells the owner what will expire or become unsafe while the Mac is away; and (3) a browser mutation guard that refuses stale-page submissions and returns a redacted pre/post diff receipt. The live system currently reports two interrupted ledgers, including one inflight step, so continuation is not hypothetical. I also found that the documented browser-inspect surface needs a typed snapshot/diff contract before the mutation guard can be built.

**Biggest unknown:** The orchestrator still needs to resolve the production handoff path: whether the workbench handoff/context routes are truly mounted in the live Mac agent, and how physical approval events are delivered back to the relay. I still need no owner policy re-request this round; the remaining work is implementation and validation of those missing bindings.

