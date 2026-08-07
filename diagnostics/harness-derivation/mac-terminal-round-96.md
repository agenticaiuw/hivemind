# Harness derivation — mac-terminal — round 96

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac UI reachability and observability** — Live agent is full-control but not ready for UI automation: /observe reports Accessibility trusted=false, eventsPost=false, screenRecording=false, inputReachability failed, and explicitly warns ui_click/type_text/press_keys report success while doing nothing. /ops/status also reports ready=false. The job journal currently has 120 retained jobs, 146 actions, 18 failures, 0 undoable, and 112 unattributed routing actions.
  - evidence: GET /observe and GET /journal at 2026-08-07T13:25Z

## Capabilities it proposed

### "“If you can’t control my Mac, fix the connection with me and tell me when it is genuinely ready.”"
- **useful because:** Today the agent can silently claim that clicks or typing succeeded even when macOS rejects its synthetic events. The owner needs a spoken, guided recovery flow that identifies the exact missing permission or stale bridge, opens the right System Settings pane, waits while they repair it, and then proves that control works before another task is attempted.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use deterministic local checks and a small background model for explaining the diagnosis; reserve realtime voice for the pendant conversation while the owner performs the repair.
- **latency:** Immediate diagnosis in under 2 seconds; each verification probe under 1 second; the owner-controlled permission repair may take several minutes.
- **cost:** Usually no model call for diagnosis or verification; roughly $0.001–$0.01 only when background explanation is needed. Main cost is local interaction time, not API usage.
- **security:** The flow must never weaken macOS permissions or claim readiness from a receipt alone. It should show the exact binary needing Accessibility/Screen Recording, avoid transmitting screenshots or private window contents, and require the owner to perform OS-level permission changes. Store only typed permission states and probe results.
- **missing:** A signed host-identity check tying permission status to the exact running AI Pendant Agent binary; A deterministic remediation state machine for Accessibility, Screen Recording, secure input, and stale browser-bridge pairing; A post-repair synthetic-event verification that has a real observable effect rather than trusting an action return value; Pendant-facing progress and completion events for this repair flow

### "“If my Mac loses control or goes offline, keep the task alive and let me finish it from the pendant without starting over.”"
- **useful because:** A long task currently has no owner-facing continuity across a failed Mac UI session: the owner cannot tell whether work stopped before or after a change, nor resume with the verified state already gathered. This capability would turn a Mac failure into a resumable handoff rather than a dead end. The pendant could summarize the last verified checkpoint, ask only for the missing decision, and continue when the Mac or authenticated browser returns.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic checkpoint and connectivity handling; use a cheaper background model to compress the existing evidence and formulate the next question. Use realtime only for the live pendant exchange.
- **latency:** Detect loss in 2–5 seconds; speak a short checkpoint within 5 seconds; resume within 10 seconds after the Mac/browser reconnects.
- **cost:** Typically one short background summarization, about $0.001–$0.02 per handoff. Durable relay storage and local checkpoint writes dominate operational cost, not inference.
- **security:** Persist only typed checkpoints, action IDs, hashes, and redacted evidence references; authenticated page contents remain in the browser session. Never replay a write after reconnect without checking its idempotency key and last verified postcondition. The pendant must clearly distinguish verified, attempted, and unknown state.
- **missing:** A durable cross-surface checkpoint protocol with monotonic sequence numbers and explicit verified/attempted/unknown states; Reconnect reconciliation between relay jobs, local Mac jobs, and browser command queues; Pendant events for checkpoint-ready, Mac-offline, and resume-complete; A resume planner that consumes checkpoint deltas instead of the original full prompt


## Changes it proposed to its own stack

### `mac-harness` — Add a non-blocking capability preflight and outcome verifier to every desktop action. Before UI actions, read the existing /observe reachability facts (Accessibility trusted/eventsPost, Screen Recording, secure input, foreground app, browser session); annotate the planned action with reachable/unreachable capabilities. After execution, run a typed postcondition probe appropriate to the action (frontmost app/window, volume, file hash, browser tab URL/title, or a bounded UI-state signal). If UI input is unreachable or the postcondition is false, mark the receipt as `not_verified` rather than success and automatically choose an equivalent available route (AppleScript/system API for app settings, shell for files/status, browser bridge for tabs), retaining the original attempt and fallback as one causal action group. Persist preflight, verification, fallback reason, and evidence IDs in /jobs/:id/receipts and expose aggregate unreachable-capability counts in /observe or /ops/snapshot. This is observability and recovery only: it must never block an action or add confirmation gates.
- **owner gets:** Today the Mac reports clicks, typing, and key presses as successful even though the live host says Accessibility is not trusted and synthesized events are rejected. The owner can believe a task completed when nothing changed. This makes spoken completion reports honest and lets the system finish the same goal through a working path automatically, while showing exactly why a UI attempt was replaced.
- effort: Medium: implement preflight/postcondition adapters for the existing executor action types, causal receipt grouping, and a small dashboard/relay rendering change; add integration tests with permissions false and true.  ·  risk: A weak postcondition could produce false negatives or trigger an inappropriate fallback; keep fallback selection deterministic and record all evidence. Never retry non-idempotent writes automatically; only fallback when the action declares an idempotency key and a safe equivalent. If probes fail, report unknown rather than success.
- cost: Negligible API cost for deterministic probes; saves planner tokens and repeated retries. Small local CPU/IO overhead per action. No new cloud data beyond existing receipt metadata and redacted evidence IDs.  ·  latency: Tens to a few hundred milliseconds for local probes; avoids multi-second planner retries and misleading completion turns.
- security: No new privileges and no restriction of FULL_CONTROL_MODE. Receipts must redact shell output, URLs/query strings, and private page text; store hashes/typed facts unless the owner explicitly requests detail.
- depends on: chg-5fc73ce3 receipt/undo implementation; GET /observe reachability facts; GET /ops/snapshot and GET /jobs/:jobId/receipts observability surfaces; existing typed action metadata/idempotency keys

### `model-routing` — Create a cross-surface execution lineage record keyed by one owner request ID, propagated unchanged through relay, planner routing, local job, browser command, and pendant audio. Each node appends only a compact event (tier/model, prompt/context digest and token counts, action IDs, latency, status, evidence IDs, and failure classification), while full private payloads stay at their origin. Add GET /lineage/:requestId and make /routing, /journal, /jobs, and relay_job_status join on that ID. Use the lineage's completed facts and failure reasons as a bounded continuation context when a long-running job resumes, instead of resending the whole fleet context.
- **owner gets:** A single spoken request currently becomes hard to explain across the Mac and relay: many jobs are unattributed (the live journal reports 112 unattributed actions), and the owner cannot tell whether a failure was the browser, permissions, network, or model. They would get one concise, trustworthy receipt—what each body did, what it cost, and what remains—while resumed work avoids repeating expensive context.
- effort: Medium-high: add request-ID propagation to relay/planner/executor/browser bridge, an append-only compact lineage store with bounded retention, and join views in the existing observability routes; no new action policy.  ·  risk: Correlating old jobs without IDs can be ambiguous; mark them legacy/unattributed rather than guessing. Digests must be one-way and payloads redacted. If the lineage store is unavailable, execution continues and local job receipts remain authoritative.
- cost: Small D1/local storage and deterministic hashing overhead; reduces planner prompt tokens on retries/resumptions and avoids duplicate model calls. No extra model invocation.  ·  latency: Under ~20 ms local append per event; cross-node propagation is header/field-only. Resumptions should be faster than rebuilding context.
- security: Improves auditability without centralizing private page or shell contents: only typed metadata, hashes, and sensitivity labels cross nodes. Keep lineage access bearer-protected and apply the existing retention policy.
- depends on: GET /routing live routing receipts; GET /journal and GET /jobs/:jobId/receipts; existing browser command request IDs/idempotency keys; relay persistent agent state and durable job records


## What it asked for

_Nothing._
