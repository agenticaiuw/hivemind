# Harness derivation — faculty-action — round 50

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **action execution readiness** — Mac bridge is online and relay reachable, but local agent is not ready: Accessibility trusted=false and Screen Recording granted=false. Browser extension home-chrome is offline with 4 pending commands; browser actions cannot execute until extension polls.
  - evidence: GET /ops/status HTTP 200 and GET /browser/status HTTP 200 at round 50

## Capabilities it proposed

### "When I approve a Now Card, carry out its steps exactly once—even if the pendant loses LTE, the Mac wakes later, or the browser reconnects—and tell me which steps completed, which are waiting, and what I can safely retry."
- **useful because:** Judgement can select a multi-surface plan, but today action execution can duplicate work or lose place across pendant/relay/Mac/browser handoffs. A durable execution lease and step ledger would let the owner trust that 'approve' means one action per intended resource, with honest recovery after disconnection.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background planner creates a deterministic step graph; realtime only speaks the approval/result summary. Relay persists the graph and leases; Mac/browser perform typed steps; pendant shows compact state; dashboard exposes receipts and retry controls.
- **latency:** Approval acknowledgement under 500 ms from relay; each step may complete asynchronously. Reconnect reconciliation within 5 seconds. No low-latency model call is needed for retries or reconciliation.
- **cost:** ~$0.001–$0.01 per approved card, dominated by planner tokens; lease renewals, receipts, and retries are storage/edge operations.
- **security:** Only explicitly approved graphs may mutate. Each step carries an idempotency key, target surface, precondition hash, expiry, and reversible/irreversible classification. Browser credentials never leave the browser. Require a fresh pendant confirmation for irreversible or changed-precondition steps; redact receipt payloads and expire evidence.
- **missing:** A shared durable step-ledger/lease API across relay, Mac bridge, and browser extension (claim, heartbeat, complete, fail, reconcile, expire).; Executor adapters that honor idempotency keys and return typed receipts with before/after evidence; browser currently needs command deduplication and session reattachment.; Pendant/dashboard rendering for per-step states and a compact retry/continue interaction.; A policy evaluator that blocks stale plans and routes changed or irreversible steps back to judgement for confirmation.

### "Let me give you a goal once, then leave it running safely: coordinate the whole task across my logged-in browser and Mac, ask me only when a real decision is needed, and let one press of the pendant stop every pending action immediately."
- **useful because:** Today the mind can plan and execute isolated actions, but it cannot safely supervise a long-lived, multi-surface objective with a physical emergency stop and decision checkpoints. This would let the owner delegate chores such as arranging travel, resolving an account issue, or preparing a purchase without leaving an unbounded agent acting in the background.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A cheaper background model maintains the task graph and detects decision points; realtime is used only for spoken checkpoint questions and immediate stop acknowledgement. The relay coordinates state, Mac and browser perform scoped steps, and the dashboard shows the active delegation.
- **latency:** Stop signal should be accepted by the relay in under 300 ms and prevent any not-yet-started step. In-flight cancellation acknowledgement within 2 seconds; ordinary planning and browser work may be asynchronous.
- **cost:** Approximately $0.005–$0.05 per delegated objective, dominated by planner and checkpoint summaries; stop, lease, and event traffic is negligible.
- **security:** Delegation must have an explicit scope, expiry, allowed domains/apps, maximum spend or message count, and a deny-list for irreversible operations. The pendant button is a local stop signal that works even if speech or the Mac is unavailable. Browser secrets remain in-browser. Pauses at changed facts, external communication, purchases, authentication, and any action outside the approved scope; require fresh confirmation. Encrypt and TTL task context and receipts.
- **missing:** A relay-resident objective supervisor with scope, expiry, checkpoint, and cancellation state—not merely a one-shot job runner.; A priority stop channel from pendant to relay, plus cancellation propagation and acknowledgement in Mac and browser executors.; A policy/checkpoint protocol that turns planner uncertainty or changed page state into a compact spoken question and resumes only after the answer.; Executor sandboxing by app/domain and resource budget, with watchdogs for hung Mac/browser work.; Pendant and dashboard UI for active delegation, current step, pause reason, expiry, and emergency stop confirmation.


## Changes it proposed to its own stack

### `relay` — Add a cross-surface execution coordinator backed by D1: an immutable action_graph (graphId, approvalReceipt, parentId, intentHash, policyVersion), action_step rows with unique (graphId, stepKey), leaseOwner/leaseExpiry, preconditionHash, state, attempt, and typed receipt; expose claim/renew/complete/fail/reconcile endpoints. Executors must atomically claim a step, reject duplicate keys, and on reconnect reconcile leases before accepting new work. Emit one ordered event stream consumed by pendant and dashboard.
- **owner gets:** A single approval would survive LTE drops, Mac sleep, and browser reconnects without repeating a reminder, purchase, message, or other side effect; the owner can see precisely what happened and resume only the safe remainder.
- effort: Medium-high: D1 schema/API plus relay tests, then adapter changes in Mac bridge and browser extension; staged read-only reconciliation first, mutations behind feature flag.  ·  risk: A lease timeout can falsely look abandoned while an executor is still acting, or a receipt can be lost after the side effect. Use idempotency keys at every adapter, short transactional claim windows, explicit unknown outcome state, and require judgement confirmation before retrying unknown irreversible steps. Roll back by disabling coordinator and treating existing jobs as legacy.
- cost: Low edge/D1 cost (a few rows/events per step); no extra model call during execution. Dashboard and receipt storage increase modestly with retention TTL.  ·  latency: Sub-500 ms claim/ack on relay; each device action remains bounded by its local executor. Reconnect reconciliation adds up to ~5 seconds.
- security: Approval receipt and policy version are cryptographically bound to the graph; stale or altered plans are rejected. Browser auth stays local; receipts redact values and expire evidence.
- depends on: ActionIntent/receipt schema must be standardized across existing Mac and browser action paths; Mac bridge and browser extension must accept and persist idempotency keys; Judgement must expose preconditions and irreversible-step policy; Pendant needs a compact state/confirmation display

### `firmware` — Add a hard-priority delegation-stop event to the pendant firmware: a long press (distinct from conversation press) sets a local stop latch, gives immediate red/amber LED feedback, sends a tiny authenticated cancel frame when LTE is available, and persists the stop generation counter on microSD so a reconnect cannot resume an older delegated objective. The relay must treat that generation as authoritative until the owner explicitly clears it with a deliberate two-press gesture or spoken confirmation.
- **owner gets:** The owner gets a trustworthy physical kill switch for an agent that is acting across the Mac and logged-in browser, including when speech recognition fails or the Mac is busy. They can stop future actions immediately and know that reconnecting will not silently restart the task.
- effort: Medium: firmware button state machine and persisted counter, relay cancel-generation handling, and executor cancellation tests. Do not flash until bench-tested against the simulator and a disconnected/reconnected modem.  ·  risk: False long presses could pause a task; use a hold threshold and unmistakable LED/audio acknowledgement. A stop frame can be delayed by LTE half-duplex, so the relay also needs the persisted generation and executors need short leases. Recovery is explicit owner clearance; no automatic resume.
- cost: Negligible API cost. Firmware storage is a few bytes; no new hardware required. LTE stop packets are tiny. Battery impact is negligible except during transmission.  ·  latency: Local stop feedback is immediate; relay propagation depends on LTE, targeted under 2 seconds when connected. Pending steps stop at the next lease boundary.
- security: Authenticate and monotonically validate the stop generation to prevent replay or forged cancellation. Persist only the counter and task identifier hash, never task content or credentials.
- depends on: Relay-resident long-lived objective supervisor and cancellation protocol; Mac and browser executors honoring cancellation at step boundaries; A clearly specified owner confirmation gesture for clearing the stop latch


## What it asked for

_Nothing._
