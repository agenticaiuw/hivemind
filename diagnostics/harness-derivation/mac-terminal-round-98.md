# Harness derivation — mac-terminal — round 98

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac execution truth and readiness** — Live /ops/status and /observe show fullControlMode true but agent ready false: Accessibility is untrusted, Screen Recording is false, and synthesized UI events are not accepted; /browser/status reports browser offline with 9 pending commands. /journal retains 120 jobs, 146 actions, 18 failures, 0 undoable, and 112 unattributed tier receipts.
  - evidence: GET /ops/status, GET /observe, GET /journal at 2026-08-07T13:31Z

## Capabilities it proposed

### "“If something I asked you to do fails while I’m away, figure out whether it can be safely retried, retry it when the Mac or browser comes back, and tell me exactly what succeeded, what was skipped, and why.”"
- **useful because:** The live Mac currently reports browser offline with 9 pending commands, 18 failed actions in the retained job window, and Accessibility false even though UI receipts may say success. Today the owner must manually diagnose stale work. This gives the pendant a truthful, asynchronous recovery loop: relay preserves intent, Mac rechecks reachability and permissions, browser resumes only session-affine/idempotent steps, and the spoken result distinguishes confirmed execution from unverified UI success.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic state machine and idempotency classifier first; background gpt-4.1-mini only to summarize a failure cluster or propose a non-obvious recovery; realtime gpt-realtime-2.1 only for the owner's immediate spoken status question.
- **latency:** Immediate acknowledgement under 300 ms from the relay; health checks every 30–60 s while a job is waiting; retry on reconnect within 10 s; spoken completion under 2 s once receipts arrive.
- **cost:** Usually near-zero model cost for retries and classification; roughly 1 background call (about 2k prompt tokens) only for ambiguous failures, plus existing relay/storage costs. Avoids repeatedly spending planner-tier context on unchanged retries.
- **security:** Persist only the original intent, typed action metadata, and receipt evidence—not page contents or secrets. Never retry non-idempotent or UI actions when Accessibility/screen recording is untrusted; mark them unverified and require a fresh owner request. Browser retries remain bound to the original authenticated session/tab and must not copy credentials into relay summaries.
- **missing:** A durable retry/dead-letter coordinator that survives relay and Mac restarts; A shared action classification contract exposing idempotency, side-effect class, and preconditions in each receipt; Reconnect-triggered browser queue draining with command expiry and deduplication; Permission-aware verification after UI actions (Accessibility and Screen Recording are currently false); Pendant-friendly completion events that include confirmed/unverified/skipped counts

### "“After I approve a form, booking, or message from my pendant, submit it in my logged-in browser and prove that the service accepted exactly what I approved; if the result is ambiguous, stop and tell me instead of submitting twice.”"
- **useful because:** Today the system can prepare browser transactions and can record local action receipts, but the owner cannot get an independent, end-to-end confirmation that the remote service committed the intended change. A click receipt is not proof of server acceptance, especially with stale tabs, lost connectivity, or a post-submit error page. This capability closes the dangerous gap between local execution and the real-world outcome.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic transaction state machine for approval binding, submission, deduplication, and post-submit verification; background gpt-4.1-mini only to interpret an unfamiliar confirmation page; realtime gpt-realtime-2.1 only to ask for or report approval in the live conversation.
- **latency:** Pendant approval acknowledgement under 300 ms; submission normally under 10 s; verification within 5 s after navigation, with a durable pending state if the browser or relay disconnects.
- **cost:** Near-zero model cost for known confirmation selectors and hashes; at most one background call (roughly 2k prompt tokens) for an unfamiliar confirmation page. Existing browser and relay storage dominate.
- **security:** Bind approval to an immutable preview hash containing target account/session, destination, fields, and exact payload; never silently alter it. Keep credentials and sensitive page contents in the browser session, send the relay only redacted hashes and confirmation evidence. Require a new approval if any field or target changes. Ambiguous network outcomes must be treated as unknown and reconciled by reading the service's history/status page before any retry.
- **missing:** A durable transaction object shared by pendant, relay, Mac, and browser with preview hash, approval nonce, expiry, and state transitions; Browser-side post-submit verification recipes (confirmation URL, receipt number, history lookup, or idempotency key) and a generic fallback extractor; A remote-service idempotency/reconciliation strategy that distinguishes timeout-after-commit from never-submitted; A pendant event and dashboard view for committed, rejected, and unknown outcomes with evidence links; A typed receipt that separates local interaction success from verified remote commitment


## Changes it proposed to its own stack

### `integration` — Make every Mac UI action pass through a preflight/postflight reachability contract. Before ui_click, type_text, press_keys, or browser-bridge commands, capture the current /observe permission and extension state; after the action, require an observable effect (focused app/title change, DOM mutation, or typed-value readback). Store a three-state result—confirmed, unverified, or failed—in the existing receipt and journal, and emit a compact pendant event. If Accessibility is false or the browser is offline, automatically switch to a non-UI route when one exists (shell/app open/read-only) and otherwise explain the exact missing condition instead of reporting success.
- **owner gets:** Right now the Mac explicitly says synthesized events are not accepted and UI actions “report success while doing nothing”; browser is offline with nine queued commands. The owner gets truthful answers and useful fallback behavior instead of silently believing a failed click or typing action happened.
- effort: Medium: shared preflight/postflight wrapper, typed receipt schema, browser result correlation, and a small dashboard/pendant formatter; no new model required.  ·  risk: Some valid actions have no immediate observable effect and would be marked unverified; recover by allowing action-specific verification strategies and retaining raw receipts. Do not block execution—this is observability and fallback only, consistent with FULL_CONTROL_MODE.
- cost: Negligible storage and one /observe read per UI action; no model cost for normal paths. Optional background summarization only for repeated failures.  ·  latency: Adds roughly 50–200 ms for local preflight and postflight; skips vision/model calls unless the action explicitly requires visual confirmation.
- security: Improves privacy by keeping evidence local and emitting only status/counts to the relay; does not reduce the owner's unrestricted execution policy.
- depends on: A typed receipt extension in actionReceipts.js with confirmed/unverified/failed and verification evidence; A browser command result carrying session/tab correlation and DOM readback metadata; Existing GET /observe and GET /browser/status being callable from the executor; A pendant event schema over POST /pipeline/events

### `model-routing` — Propagate one correlation ID and routing receipt from the pendant/relay request through planner, Mac job, browser command, and final pipeline event. Add a deterministic context ledger recording selected context sections, estimated tokens, model tier, latency, and whether the result was confirmed or merely delegated; expose per-owner-task totals in /routing and the dashboard, and let background retries reuse the original plan digest instead of resending the full fleet context.
- **owner gets:** The live routing report shows 112 of 120 retained jobs unattributed to a model tier and planner requests averaging about 8.8k tokens. The owner cannot tell whether a delayed job cost one cheap retry or repeated expensive planning. This makes asynchronous work both cheaper and explainable without changing what the agent is allowed to do.
- effort: Medium: correlation propagation across relay, planner, executor, browser bridge, and journal; compact digest hashing; dashboard aggregation.  ·  risk: Missing propagation in one surface could create partial records; treat absent fields as unknown rather than infer them, and preserve existing job execution. Digest reuse must invalidate on changed permissions, tab, or task state.
- cost: Small local storage overhead; likely reduces planner-token spend substantially on retries and status questions. No additional model calls.  ·  latency: Negligible bookkeeping (single-digit milliseconds); avoids planner calls for deterministic status and retry decisions.
- security: Store hashes and metadata rather than prompt/page contents in the cross-surface ledger; keep sensitive browser payloads local to the session.
- depends on: Existing GET /routing and routingStats.js; Durable job IDs and receipts from /jobs and /journal; Relay pipeline event correlation on POST /pipeline/events; Typed browser request IDs/session affinity from browserBridge.js and browserSessions.js


## What it asked for

_Nothing._
## Its own summary

Fresh live discovery found a serious truthfulness gap: /ops/status says full control is enabled but agent ready=false because Accessibility and Screen Recording are unavailable; /observe confirms UI events can report success while doing nothing. Browser is offline with 9 pending commands. /journal reports 146 actions, 18 failures, 0 undoable, and 112 jobs without model-tier attribution. I recorded these findings and proposed (1) a cross-surface safe-retry/dead-letter capability, (2) a non-blocking UI preflight/postflight reachability contract with confirmed/unverified/failed receipts and fallbacks, and (3) end-to-end routing/cost correlation to avoid repeated planner context.

**Biggest unknown:** Implementation status of the newly proposed connective work and the exact durable relay/job lifecycle contract. I do not need another discovery tool this round; the outstanding need is engineering: receipt verification, reconnect retry coordination, and correlation propagation. Existing queued requests for lifecycle/tool grants should not be re-asked.

