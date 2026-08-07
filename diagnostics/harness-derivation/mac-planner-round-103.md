# Harness derivation — mac-planner — round 103

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-device liveness** — Live /browser/status reports home-chrome online but 7 pending commands; browser status alone does not expose whether those commands are fresh, leased, or stale. This supports adding device epochs and quarantine before cross-surface replay.
  - evidence: GET /browser/status returned online:true, home-chrome online:true, pendingCommands:7 at 2026-08-07T12:58:09.383Z.

## Capabilities it proposed

### "“If you lose connection while working on something, keep the work safe and resume it exactly once when my Mac or browser comes back—then tell me what was completed, skipped, or still needs me.”"
- **useful because:** Today a pendant request can leave a stale browser command or an ambiguous Mac job after a disconnect. A single intent would survive relay, Mac, and browser outages, resume only idempotent steps, and provide one truthful completion report instead of duplicate submissions or guesswork.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for checkpoint reconciliation and receipt summarization; deterministic workers for lease/step replay; realtime only for the short spoken status when the owner asks
- **latency:** Immediate acknowledgement under 1 second; reconnect reconciliation within 5 seconds; spoken summary under 2 seconds after receipts arrive
- **cost:** Usually <$0.01 per recovery using deterministic replay and a small background summary; planner escalation only for ambiguous or non-idempotent steps. Storage/queue operations dominate, not model calls.
- **security:** Private URLs, file paths, and action receipts remain on the relay/Mac account scope; browser session tokens never enter the pendant. Non-idempotent sends, purchases, deletes, or submissions are marked blocked-after-disconnect and require an explicit new owner command. Dashboard must show device, lease, and before/after evidence.
- **missing:** A cross-surface intent ledger with durable step IDs, idempotency keys, leases, and a reconciliation state machine shared by Mac and browser workers; A device liveness/epoch protocol so an offline browser extension cannot claim commands after its lease expires; A unified receipt endpoint joining Mac action receipts and browser typed results under one intent ID; A pendant-friendly resume/status event and dashboard view for orphaned, replayed, and blocked steps

### "“Tell me when my Mac, browser, and pendant disagree about whether something happened, and help me reconcile it without repeating the action.”"
- **useful because:** Today a timeout, sleep, or reconnect can leave conflicting evidence: the browser may show a changed page while the Mac has no receipt, or the Mac may report completion while the authenticated page still shows the old state. The owner needs an evidence-based contradiction alert, not a guessed success or an unsafe retry.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic evidence matching and state-machine logic first; background model only to summarize the contradiction in plain language. Realtime is used only when the owner asks for the short spoken explanation.
- **latency:** Detect contradictions within 2 seconds of receiving a new receipt or page observation; spoken alert under 2 seconds when requested. Reconciliation can take up to 30 seconds because it may require a fresh browser read.
- **cost:** Under $0.01 per contradiction in the common case; most work is receipt comparison and one read-only verification. Planner escalation is reserved for genuinely ambiguous evidence.
- **security:** Evidence must remain account-scoped and redact private page contents in pendant audio. Never retry an uncertain mutation automatically. Show URLs, timestamps, action IDs, and before/after snippets only in the protected Mac/dashboard view; require a fresh owner instruction for any corrective mutation.
- **missing:** A typed shared state vocabulary for Mac actions, browser observations, and pendant acknowledgements, including unknown and contradicted states; A causal evidence graph that links receipts, page observations, device epochs, and timestamps rather than treating each surface's success flag as authoritative; A read-only verification workflow for authenticated browser pages and Mac state after a contradiction; A dashboard and pendant event format that explains the conflict and offers safe choices: verify again, mark resolved, or prepare (but not execute) a correction


## Changes it proposed to its own stack

### `integration` — Add a cross-surface intent coordinator between the relay, Mac job runner, and browser bridge. It should compile one user intent into typed steps, assign each step an idempotency key and device-epoch lease, persist checkpoints, reject stale claims, and merge Mac receipts plus browser typed results into one causal timeline. On reconnect it retries only steps declared safe-to-replay and emits an explicit blocked state for uncertain mutations.
- **owner gets:** A dropped Wi‑Fi link or sleeping laptop would no longer leave the owner wondering whether a page was changed twice, a file was written, or a form was submitted. They get one honest answer and safe continuation when devices return.
- effort: Medium-high: relay state machine and schema, Mac/browser adapters, failure-injection tests across reconnect and duplicate delivery, plus dashboard timeline.  ·  risk: A bad idempotency classification could replay a mutation or skip useful work. Default unknown steps to blocked; preserve raw receipts and allow manual reconciliation. Recover by replaying from the last durable checkpoint, never by guessing from a timeout.
- cost: Low ongoing API cost; deterministic state transitions dominate. Occasional background summarization is a few thousand tokens per recovery. Small durable KV/D1/R2 growth from receipts and checkpoints.  ·  latency: Sub-100 ms local lease/checkpoint overhead; reconnect reconciliation typically seconds. No added latency to ordinary single-step Mac actions once bypassed as already-complete.
- security: Requires strict account-scoped intent records and opaque step IDs; never copy browser cookies or private page bodies into pendant audio. Encrypt or redact receipt payloads and expire detailed evidence separately from status.
- depends on: Implement the durable browser runner and stale-device lease/epoch handling; Expose a stable Mac job/receipt correlation ID on POST /execute and GET /jobs/:jobId/receipts; Implement the missing read-only Mac inspection tool if foreground/browser context is needed for safe step selection

### `memory` — Create a contradiction-aware evidence graph rather than a flat action log. Normalize Mac receipts, browser observations, relay delivery events, and device liveness into immutable claims with source, timestamp, causal parent, confidence, and supersession rules; derive explicit states such as confirmed, unverified, contradicted, and resolved.
- **owner gets:** The owner would know exactly when the system is uncertain instead of receiving a confident but wrong 'done'. They could resume work after a crash without duplicating a submission, and later inspect why the system reached its conclusion.
- effort: Medium: shared schema, ingestion adapters for existing Mac/browser/relay records, conflict rules, retention/redaction policy, and a small protected timeline UI.  ·  risk: Incorrect normalization could create false conflicts or hide a real one. Keep raw source records immutable, expose both claims side by side, and default unresolved conflicts to non-action rather than silently choosing a winner.
- cost: Low storage and compute cost; deterministic graph updates are cheap. A small background model call may be used only to phrase a human-readable explanation.  ·  latency: Negligible for ordinary actions; conflict derivation should complete in under a second after each receipt, with verification reads adding network latency only when needed.
- security: Evidence may contain private URLs, filenames, and snippets. Enforce per-owner encryption and field-level redaction; pendant output should contain only minimal labels and no sensitive content by default.
- depends on: A shared typed claim schema across Mac, browser, relay, and pendant events; Stable causal IDs on Mac job receipts and browser command results; Read-only verification adapters for authenticated browser state and Mac state; A protected dashboard/timeline surface for raw evidence and resolution actions


## What it asked for

_Nothing._
