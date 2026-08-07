# Harness derivation — mac-terminal — round 116

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac execution readiness** — At 2026-08-07T14:37Z the live agent reports ready=false: Accessibility trusted=false and synthesized events rejected because Accessibility is granted to a different binary; Screen Recording is false; browser extension is offline with 10 pending commands. UI actions may report success while doing nothing.
  - evidence: GET /observe and GET /ops/status: accessibility.eventsPost=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false, browser.online=false pendingCommands=10.

## Capabilities it proposed

### "If my Mac or browser is offline, keep my request pending, and when it reconnects carry out only the safe, repeatable parts, then tell me from the pendant exactly what ran, what was skipped, and why."
- **useful because:** Today an offline browser leaves ten pending commands and repeated navigation failures with no owner-facing reconciliation. This gives the owner continuity without pretending unavailable actions succeeded, and uses the pendant as the final status surface.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for queue classification, retry reconciliation, and summaries; realtime only when the owner asks or receives the completion announcement; deterministic checks for connectivity, idempotency, and receipt aggregation.
- **latency:** Immediate acknowledgement under 1 s; reconnect reconciliation within 5 s of a healthy heartbeat; spoken summary under 10 s. No waiting on a live planner while offline.
- **cost:** Near-zero when offline or reconnecting: D1/job writes and deterministic checks dominate. One background-model call (roughly 2k–4k prompt tokens) only for ambiguous multi-step reconciliation or a final natural-language summary.
- **security:** Pending intents and results can contain private URLs, page text, or command data; encrypt or minimize relay payloads and retain only hashes plus references where possible. Never replay non-idempotent browser submissions, shell mutations, or sends; report them as skipped and require a new owner request. Reconnect must authenticate the paired extension and Mac.
- **missing:** A durable cross-surface intent record with action-level idempotency and replay policy; A browser-heartbeat-triggered and Mac-online-triggered reconciler (not just a command queue); Typed receipt states: pending, unavailable, replayed, verified, skipped, and reason codes; Pendant delivery of a compact reconciliation summary and dashboard drill-down

### "When I step away from my Mac during an AI task, keep my place privately and make the work safe to resume; when I return, let me continue from the pendant or Mac without reopening sensitive pages or losing the in-progress state."
- **useful because:** A wearable should know the owner is physically present or away in a way the Mac alone cannot. This prevents an unattended screen from exposing private browser or work content, while preserving the exact task checkpoint so returning does not mean reconstructing context. The pendant can provide a discreet resume cue even when the Mac display is locked.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic local state machine for proximity, lock/redaction, checkpointing, and resume eligibility; background model only to summarize a long interrupted task; realtime only for the owner's explicit resume or status question.
- **latency:** Detect departure and checkpoint within 2 seconds; redact or lock within 1 second after the policy threshold; restore a resumable state within 3 seconds of return or an explicit pendant button press.
- **cost:** Normally no model call: BLE/proximity events, local Mac actions, browser session state, and relay D1 metadata. Occasional background summary costs roughly 1k–3k prompt tokens. Hardware addition, if needed, is a BLE proximity beacon or UWB-capable pendant component (roughly $5–15 BOM, low duty-cycle power).
- **security:** Never transmit page contents or screenshots merely because presence changed. Store only an encrypted task checkpoint, tab/session identifiers, and redaction state; expire checkpoints quickly. Resume must require a local presence signal plus an explicit pendant action for sensitive tabs, account pages, or unsent forms. Failure recovery must prefer remaining locked/redacted over exposing content.
- **missing:** A signed, privacy-preserving presence signal from pendant to Mac/relay with hysteresis and configurable away timeout; A task checkpoint protocol spanning planner jobs, browser sessions, pipeline state, and action receipts; Mac/browser primitives to blur or lock sensitive surfaces and restore the prior task without reloading authenticated content; A pendant resume/status interaction that works while the Mac is locked; Owner-configurable sensitivity classes and checkpoint retention/expiry


## Changes it proposed to its own stack

### `mac-harness` — Add a non-blocking execution preflight and truthful delivery state to every Mac job. Before dispatch, snapshot Accessibility/inputReachability, Screen Recording, browser bridge connectivity, and target app presence; attach it to the job. After each action, distinguish dispatched, acknowledged-by-OS, and verified-effect (with reason when verification is impossible). If a known-failed prerequisite exists, mark the action unavailable and enqueue a retryable recovery record rather than claiming success; when the prerequisite or browser heartbeat returns, reconcile and replay only idempotent actions. Preserve FULL_CONTROL_MODE and do not add approval gates.
- **owner gets:** The owner will stop hearing that a task succeeded when the Mac could not receive input or the browser was offline, and will get an exact explanation plus automatic recovery when the connection returns.
- effort: Medium: shared preflight snapshot, receipt schema/status transitions, per-action verification hooks, and a small reconnect reconciler; existing job/receipt/journal endpoints can expose it.  ·  risk: Some actions cannot be independently verified, so receipts must say unknown rather than falsely verified. Replaying a non-idempotent command could duplicate work; recovery must default to no replay unless the action declares an idempotency key and safe replay semantics. Existing receipt consumers need backward-compatible fields.
- cost: Negligible API cost; a few local status probes and small JSON receipt growth. No extra cloud model calls.  ·  latency: Adds roughly 10–100 ms for local preflight; verification may add latency only for actions that opt in. Offline actions fail fast instead of waiting for the 120 s shell timeout.
- security: No reduction in owner-authorized access. Preflight metadata may reveal app/window state, so retain it with the existing job retention and avoid recording command contents or secrets.
- depends on: Existing /observe, /browser/status, /ops/status, jobTracker receipts and journal storage; A typed action outcome contract for each executor action (verification optional)


## What it asked for

_Nothing._
## Its own summary

Fresh live discovery: /observe and /ops/status show the Mac agent is not execution-ready. Accessibility is not trusted for the running AI Pendant Agent binary, synthesized input is rejected, Screen Recording is absent, and browser extension home-chrome is offline with 10 pending commands. I recorded this finding, informed mac-planner, and proposed two connective improvements: truthful preflight/delivery receipts and reconnect reconciliation of only idempotent queued work. I did not propose gates or reduce FULL_CONTROL_MODE.

**Biggest unknown:** Whether the owner will grant Accessibility to the exact running binary (/Users/evanliu/Applications/AI Pendant Agent.app) and reconnect the browser extension; until then UI receipts are not trustworthy and browser work cannot be verified.

