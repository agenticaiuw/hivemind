# Harness derivation — faculty-action — round 28

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **execution-readiness** — Mac agent is online/full-control configured but not ready: Accessibility trusted=false and Screen Recording granted=false; browser bridge offline with 3 pending commands. Browser navigate attempts fail after ~45 seconds rather than being preflight-blocked.
  - evidence: GET /ops/snapshot at 2026-08-07T10:18Z reports ready:false, accessibility.trusted:false, screenRecording.granted:false, browserExtension.online:false, pendingCommands:3; GET /jobs shows failed browser_navigate receipts with 45180ms and 45373ms durations.

## Capabilities it proposed

### "When I tell you to do something, start it from the pendant and finish it on whichever device becomes available—if Safari is closed or the Mac is locked, keep the intent queued, retry safely, and tell me exactly what completed, what is waiting, and what still needs my approval."
- **useful because:** Today a decided action can simply burn 45 seconds and fail because the browser bridge is offline, while the owner receives no useful handoff. This makes the hive act as one reliable hand: capture intent on the wearable, execute on Mac/browser when reachable, and deliver a truthful receipt back to the pendant.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard-ux
- **model tier:** background for queue classification, retry summaries, and receipts; planner only for ambiguous recovery; realtime only to acknowledge the owner's live request.
- **latency:** Immediate pendant acknowledgement under 1 second; preflight health decision under 2 seconds; retries in the background with exponential backoff and a quiet-hours policy; spoken completion within 5 seconds of terminal result.
- **cost:** Low: deterministic health checks and state transitions dominate; roughly one background-model call (1–3k input tokens) only for ambiguous failure/recovery summaries, not per retry.
- **security:** Private browser work must remain in the authenticated local extension; relay stores only encrypted job metadata and receipts. Never retry irreversible submit/send/purchase steps automatically; require explicit approval and re-check the target tab, URL, and before-state immediately before execution.
- **missing:** A cross-surface durable job state machine with idempotency keys and lease ownership; Preflight health/readiness checks for Mac permissions, bridge online state, browser tab affinity, and network; Safe retry policy distinguishing reversible/idempotent steps from irreversible approval gates; Pendant-visible pending/completed/blocked receipt queue and a wake-up push path; A recovery protocol when a device reconnects after a dropped link

### "Before you act across my Mac and logged-in browser, show me a trustworthy preview of the exact outcome—what files, messages, appointments, or web fields would change—and then carry it out only if the live state still matches that preview; if it changed, stop and explain the difference."
- **useful because:** The owner can currently approve an abstract plan, but cannot reliably know whether the world has changed between planning and execution. A cross-surface state-matched preview would make complex actions understandable and prevent stale plans from editing the wrong document, tab, account, or appointment.
- **path:** faculty-judgement → faculty-perception → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → dashboard-ux
- **model tier:** Background model for extracting and summarizing predicted diffs; planner tier only when the preview is ambiguous. Realtime should speak only the concise approval prompt and final result.
- **latency:** Generate a preview in under 8 seconds for ordinary Mac/browser tasks; approval prompt under 2 seconds after preview is ready; live-state revalidation under 2 seconds before execution.
- **cost:** Typically one background call of about 2–5k input tokens plus deterministic local diffing; pixel comparison and DOM/file hashing dominate latency, not model cost.
- **security:** Private page contents and local file metadata stay on the Mac/browser bridge where possible; relay receives only redacted diff summaries and hashes. Never claim a preview is complete when a surface is inaccessible. Require explicit approval for external communication, purchases, deletion, or permission changes.
- **missing:** A read-only shadow executor that resolves every planned target without mutating it; Canonical before-state snapshots for files, DOM regions, app records, and selected pixels; A typed predicted-diff format with confidence, omitted fields, and irreversible-effect classification; Atomic compare-and-execute semantics across Mac and browser surfaces; A pendant/dashboard diff viewer that supports approve, edit, reject, and inspect-source actions


## Changes it proposed to its own stack

### `integration` — Add an execution preflight barrier and resumable handoff protocol before any action job runs. The relay creates a durable job with a step-level idempotency key, required-surface contract, and approval class. Mac agent reports signed readiness (bridge/browser online, accessibility/screen-recording state, tab/session affinity, network) within a short TTL. The scheduler refuses doomed browser/computer-use steps immediately with a structured blocked receipt, parks the job, and resumes only after a heartbeat satisfies the contract. Reversible steps may retry with leases and bounded backoff; irreversible steps become approval checkpoints and are never auto-replayed. On reconnect, reconcile receipts by idempotency key before continuing, then push a concise result to the pendant and dashboard.
- **owner gets:** The owner gets fewer mysterious failures and no duplicate clicks, sends, or purchases. A command given while walking away from the Mac remains alive and finishes later, or clearly says 'waiting for Safari' instead of pretending to work.
- effort: Medium-high: shared schema and state machine across relay/local agent, readiness endpoint and heartbeat, receipt reconciliation, scheduler, pendant notification, and dashboard views; integration tests for disconnect/reconnect and duplicate delivery.  ·  risk: A stale readiness claim could still cause a failed step, and incorrect idempotency classification could skip needed work. Use short TTLs, explicit terminal states, per-step receipts, and manual recovery for uncertain outcomes. Roll back by disabling parked-job retries while preserving receipts.
- cost: Small storage/queue cost; background model calls only for human-readable summaries. No realtime call per retry.  ·  latency: Adds 0.5–2 seconds preflight when healthy, but avoids current ~45-second dead waits and makes offline cases immediate.
- security: Improves safety by enforcing local execution for private data, scoped leases, approval gates, and no replay of irreversible actions; relay sees metadata rather than page contents.
- depends on: Durable job runner and browser queue primitives; A readiness/heartbeat contract emitted by Mac bridge and browser extension; Persistent receipt ledger with idempotency-key lookup; Pendant push or polling for job status


## What it asked for

### `p3-4uh7` (permission) — Enable Accessibility and Screen Recording for AI Pendant Agent, and enable/poll the AI Pendant Browser Bridge extension in Safari/Chrome on the owner's Mac
- why: Execution is currently blocked: computer-use cannot interact and browser actions fail after 45 seconds because Accessibility=false, Screen Recording=false, and browser online=false with 3 pending commands. Granting this lets us verify the new preflight/handoff path against real actions.
- risk it sees: This gives the local agent UI observation and control, and the browser bridge access to authenticated tabs. Keep it opt-in per app, show active status, and retain approval gates for irreversible actions; do not enable or submit anything without the owner's explicit consent.

