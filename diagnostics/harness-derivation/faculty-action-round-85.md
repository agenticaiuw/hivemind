# Harness derivation — faculty-action — round 85

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **execution** — Current /jobs records browser actions as failed after ~45 seconds when extension is offline/unresponsive, with no automatic fallback or queued continuation; receipts correctly say no change occurred.
  - evidence: GET /jobs returned failed browser_navigate jobs with messages 'browser extension is offline'/'did not answer in time', durationMs ~45045, canUndo false, and unlinked evidence.

## Capabilities it proposed

### "“Do this wherever it can actually be done; if one device is unavailable, continue with the safe parts and tell me exactly what remains.”"
- **useful because:** The owner gets an honest completion rather than a false all-or-nothing success when browser/pendant links disappear. A single intent can read or act through the browser when online, fall back to granted Mac AppleScript for supported apps, and leave the blocked steps queued with per-step evidence.
- **path:** faculty-judgement → faculty-action → relay-realtime → mac-planner → browser-extension → mac-terminal → unified
- **model tier:** background for routing and recovery classification; planner only for ambiguous fallback mapping; deterministic executor for typed steps
- **latency:** Immediate acknowledgement under 2 seconds; reversible Mac steps begin within 5 seconds; long or offline-dependent steps continue as durable jobs and report completion later.
- **cost:** Usually one background call or no model call for typed plans; planner escalation only on ambiguous fallback, roughly 2–10k input tokens. Execution itself is negligible API cost.
- **security:** Never silently substitute a different account, recipient, or destructive operation. Private browser data remains on the Mac/bridge; relay stores only step status and redacted receipts. Require owner confirmation for sends, purchases, deletes, or irreversible submits. Record why a fallback was chosen and which precondition was unavailable.
- **missing:** A typed action-graph schema with per-step capability requirements, fallback policy, and safe/reversible classification; Durable step-level runner that can pause and resume across surface outages; Precondition and postcondition evidence for each step, plus explicit blocked/ skipped states; A cross-surface receipt that links compensating actions and never claims completion for unexecuted steps

### "“If this cannot be done now, keep it alive until the deadline, retry only when the missing device or account becomes available, and tell me before the deadline if it still cannot be finished.”"
- **useful because:** Today an unavailable browser or disconnected pendant turns a potentially time-sensitive request into a terminal 45-second failure. The owner should be able to delegate work with a deadline and receive either a verified completion or an early, actionable warning—without repeatedly re-running side effects or burning expensive planner turns.
- **path:** faculty-judgement → faculty-action → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic scheduler and health/event matching for retries; background model for concise status summaries; planner only when a failed precondition requires a new plan.
- **latency:** Acknowledge and persist the request in under 2 seconds. Retry on reachability/precondition events rather than polling; warn at configurable checkpoints (for example 24 hours and 1 hour before deadline).
- **cost:** Near-zero model cost for typed retry rules and health events; background summaries generally under 2k input tokens. Storage and event delivery dominate, not inference.
- **security:** Persist only the minimum task data, encrypted and with an explicit expiry. Never retry sends, purchases, deletions, or submissions without a fresh confirmation lease. Bind retries to the original account/tab/app and invalidate them if identity, page state, or authorization changes. Show every attempt and its reason.
- **missing:** A deadline/quiet-hours/expiry contract for delegated actions; Event-driven reachability and precondition notifications from Mac, browser, relay, and pendant; Retry classes separating safe reads, idempotent writes, and confirmation-bound irreversible actions; A scheduler that can wake durable jobs without repeatedly invoking the planner; Owner-facing deadline warnings and a final failure receipt with the exact unblock action


## Changes it proposed to its own stack

### `integration` — Add an action-graph executor between judgement and the surface tools. Compile a decision into typed steps with required surface, fallback surfaces, preconditions, reversibility, and confirmation class. Execute ready steps independently; when a surface is offline, mark only dependent steps blocked, attempt explicitly allowlisted fallbacks (for example granted AppleScript instead of browser UI), persist step receipts and evidence, and resume when reachability changes. The final response must distinguish completed, skipped, blocked, and awaiting-confirmation steps.
- **owner gets:** A broken browser bridge or missing pendant would no longer make the whole request appear to fail—or worse, appear complete. The owner can safely say “handle it” and receive a precise partial result plus automatic continuation when the missing hand becomes available.
- effort: Medium-high: shared schema, durable scheduler, surface capability registry, receipt aggregation, retry/backoff, and tests for partial completion and duplicate delivery.  ·  risk: Fallback could act in the wrong context if affinity is weak; require explicit account/tab/app identity and precondition hashes. Duplicate retries could repeat side effects; use idempotency keys and compensating undo where possible. Recover by pausing ambiguous or irreversible nodes and showing the exact blocked reason.
- cost: Low incremental API cost; deterministic routing for most graphs, background model only when choosing among semantic fallbacks. Storage increases modestly for step receipts/evidence.  ·  latency: Adds milliseconds for graph validation; offline steps return immediately as blocked/queued rather than waiting for timeout. Resume latency depends on bridge/device recovery.
- security: Improves security by making least-privilege fallback and confirmation explicit, but requires careful redaction of receipts and strict surface/account affinity.
- depends on: Durable browser job runner (chg-16bc5dee) or equivalent step persistence; Action receipt/undo foundation (chg-5fc73ce3); A live surface capability/health registry; Owner confirmation policy for irreversible actions


## What it asked for

_Nothing._
## Its own summary

Round 85 produced and recorded a new cross-surface action-graph capability/change: execute independent typed steps across Mac/browser/relay, use only explicit safe fallbacks when a surface is unavailable, persist step-level receipts, resume queued work, and distinguish completed, blocked, skipped, and awaiting-confirmation. Live evidence shows why this is needed: browser jobs currently wait about 45 seconds and fail with no fallback or continuation, while the Mac bridge is online and AppleScript is granted.

**Biggest unknown:** The judgement-to-action contract is still undefined: I need the typed decision metadata (required surface, account/tab affinity, preconditions, fallback permission, reversibility, and confirmation class) and the authoritative resume/expiry policy. Current device state also lacks a registered pendant, and the browser extension/UI accessibility remain unavailable; those are owner-side blockers, not solvable from this agent.

