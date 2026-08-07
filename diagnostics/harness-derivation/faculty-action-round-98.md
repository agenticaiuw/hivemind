# Harness derivation — faculty-action — round 98

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If something I asked you to do partly fails, recover it safely: show me what actually changed, undo the reversible parts when possible, and continue only after asking about the one blocked step."
- **useful because:** Today a Mac/browser workflow can leave the owner unsure whether it stopped before or after a mutation. This gives the action layer a bounded recovery behavior: inspect receipts and live state, compensate reversible changes, preserve irreversible changes, and present a precise continuation request. It requires the action node, browser private-session node, Mac bridge, and always-awake relay together.
- **path:** faculty-judgement → faculty-action → mac-planner → mac-terminal → browser-extension → relay-realtime → unified
- **model tier:** Use the cheap background model for receipt classification, state diffing, and compensation planning; reserve realtime for the owner's short approval/continuation exchange.
- **latency:** Initial recovery report in 5–15 seconds after failure; compensation can run asynchronously with relay_job_status updates.
- **cost:** About $0.01–$0.05 per recovery, dominated by model calls over receipts and state diffs; most steps are deterministic.
- **security:** Private page contents and local action receipts remain on the authenticated Mac/relay path. Never compensate sends, purchases, deletions, or other irreversible actions automatically; require explicit approval and retain before/after evidence.
- **missing:** A transaction/compensation record that links each step to its precondition, observed before-state, after-state, reversibility class, and proof.; A deterministic state-diff and compensation executor for Mac and browser steps, with an explicit irreversible-step boundary.; A failure-injection test suite covering bridge loss, stale tabs, duplicate requests, and a mutation that succeeds but returns an error.

### "Give me an emergency stop for anything you are doing on my Mac or in my browser: when I press and hold the pendant button, stop new actions immediately, cancel queued work, and tell me whether anything was already changed."
- **useful because:** The owner can currently start work through the voice surface but cannot physically interrupt it when their attention is elsewhere or a workflow behaves unexpectedly. A local, tactile stop path is useful precisely when speech, the browser, or the Mac is busy or unresponsive. This is a cross-surface capability: the pendant detects the hold offline, the relay distributes a signed revocation, the Mac and browser executors enforce it between steps, and the relay reports the last proven state.
- **path:** pendant → relay-realtime → faculty-action → mac-planner → mac-terminal → browser-extension → unified
- **model tier:** No expensive model is needed for the stop itself. Use deterministic firmware and relay logic; use a cheaper background model only to summarize the resulting receipts after execution has halted.
- **latency:** Pendant-local stop indication within 100 ms; relay propagation target under 1 second; already-running indivisible OS/browser calls may complete, but no subsequent step may begin after revocation is observed.
- **cost:** Under $0.01 per stop, dominated by receipt summarization; negligible device power and storage overhead.
- **security:** A false press could cancel useful work, so require a deliberate hold and local vibration/LED confirmation. Revocation must be authenticated, monotonic, and fail closed for queued actions. It must not claim that an in-flight irreversible operation was undone; report unknown or completed with evidence.
- **missing:** A pendant firmware emergency-stop event and local acknowledgment path.; A relay-wide revocation sequence checked by every Mac and browser executor before each step.; Cancellation semantics for queued and in-flight jobs, including a final last-observed-step receipt.; A durable action lease/heartbeat so stale workers cannot continue after connectivity returns.


## Changes it proposed to its own stack

### `relay` — Add a cross-surface action transaction coordinator between /execute, the Mac action runner, and browser command queue. Before execution it assigns a transactionId and records each step's precondition, target surface, reversibility class, and expected proof. After every step it persists before/after evidence and a compensation recipe. On timeout or contradictory result, it freezes later steps, asks the Mac/browser surfaces for fresh state, runs only safe compensations in reverse order, and exposes a human-readable recovery packet through relay_job_status and job receipts. Irreversible steps become hard boundaries that require owner confirmation before continuation.
- **owner gets:** When a multi-step task half-completes, the owner will know exactly what changed and get the safe parts restored instead of manually investigating duplicate tabs, half-filled forms, or uncertain Mac state.
- effort: Medium-high: coordinator state machine, typed compensation metadata in both harnesses, fresh-state probes, and failure-injection tests.  ·  risk: A bad compensation could itself alter data or create duplicates. Default to no-op when proof is missing, use idempotency keys, and preserve receipts; recover by stopping and presenting the packet.
- cost: Low persistent storage and a few deterministic Mac/browser calls; roughly $0.01–$0.05 only when a failure needs model-assisted classification.  ·  latency: Adds ~1–3 seconds of receipt/state persistence per step; failure recovery takes 5–15 seconds.
- security: Improves auditability but stores more private before/after metadata. Encrypt sensitive values, store hashes/snippets by default, and never send private page contents to third-party services.
- depends on: A durable browser job runner and typed browser queue must expose step-level results.; Mac actions must return stable idempotency keys and before/after proof.; Owner approval policy must distinguish reversible compensation from irreversible continuation.

### `browser-harness` — Add a fast, non-mutating browser preflight gate before any browser_* step: verify the selected session/tab's bridge heartbeat, tab identity, and command-poll age within a short deadline (for example 2 seconds), then classify it as ready, stale, offline, or blocked-dialog. Do not enqueue a 45-second navigate when the bridge is known unavailable. For public URLs only, route a clearly labeled fallback to the server browser backend; for authenticated URLs, fail immediately with a one-line owner-repair instruction and preserve the intended action without retrying. Record the preflight result in the job receipt.
- **owner gets:** The current failure mode wastes nearly a minute per attempt and leaves the owner guessing whether Safari changed. The owner gets an immediate, honest answer and public research can still proceed while private pages remain protected.
- effort: Low-medium: heartbeat endpoint/command, session classification, router branch, and tests for stale/offline/blocked-dialog states.  ·  risk: A false-ready result could still time out; use a hard deadline and retain the existing timeout. A public fallback must never receive private URLs, cookies, or page text; require explicit URL classification.
- cost: Negligible storage; reduces failed realtime/model calls and Mac round trips.  ·  latency: Healthy actions add <2 seconds; unhealthy actions return in ~2 seconds instead of ~45 seconds.
- security: Positive if URL classification is deny-by-default and private session IDs cannot be sent to the public backend.
- depends on: A bridge heartbeat or last-poll timestamp exposed by the browser bridge.; The existing browser job router must distinguish authenticated session-bound work from public URL work.


## What it asked for

_Nothing._
