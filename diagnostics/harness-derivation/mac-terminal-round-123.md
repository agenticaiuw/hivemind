# Harness derivation — mac-terminal — round 123

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make the AI Pendant Browser Bridge available, wait for a fresh heartbeat, and tell me in one short sentence whether it is online—without replaying or executing any queued browser command."
- **useful because:** This is a recurring real failure: opening the app succeeds, but the planner then invokes the disabled computer-use loop and reports failure even though the extension may already be online. A deterministic reconnect-and-verify path would make the owner's browser reachable without touching private tabs or pending work.
- **path:** mac-planner → browser-extension → relay-realtime → unified
- **model tier:** deterministic routing and polling; no realtime or planner model unless the bridge remains unavailable and a concise explanation is needed
- **latency:** Open the bridge immediately, then poll browser status for up to 10 seconds at 500 ms; speak within 1–2 seconds when already online and never exceed 10 seconds.
- **cost:** Near-zero model cost; a few local status requests. Dominant cost is app launch and heartbeat wait, not tokens.
- **security:** Read-only status only. Must not drain or execute browser commands, navigate tabs, inspect page contents, or expose URLs. Freshness should be based on a heartbeat received after this request, not merely an old online flag.
- **missing:** A deterministic bridge_reconnect intent that can open the app and poll /browser/status or /browser/heartbeat with a request timestamp; A freshness-aware status response distinguishing online-now, online-but-stale, and unavailable; Planner routing that forbids computer_use_task fallback for this intent

### "If I speak while the Mac or relay is temporarily offline, keep my request on the pendant, show me that it is queued, and deliver it exactly once when the connection returns—then tell me whether it was accepted, completed, or needs me."
- **useful because:** Today a dropped link turns a spoken request into an ambiguous disappearance. The pendant is the one surface the owner still has, while the relay and Mac can recover later; durable, exactly-once handoff would make the system dependable during sleep, travel, Wi-Fi changes, or Mac restarts.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** No model for queueing, deduplication, or delivery receipts. Use the background tier only to summarize a completed or failed request when the owner asks; reserve realtime for the short spoken status.
- **latency:** Immediate local tactile/audio acknowledgement under 200 ms; sync on reconnection within 5 seconds; no blocking wait on the pendant.
- **cost:** Negligible per queued request beyond normal transcription when connectivity returns. Storage, retry traffic, and receipt retention dominate; summarization is optional and cheap background work.
- **security:** Queue entries must be encrypted at rest on the pendant and relay, bound to the owner's device/session, and expire or be cancellable. Never replay a command after an uncertain acknowledgement: use a globally unique request ID, an execution lease, and a durable terminal receipt. Destructive actions must retain their existing confirmation semantics when eventually delivered.
- **missing:** A pendant-side encrypted outbox with bounded size, local queue IDs, retry metadata, and a user-visible queued/sent state; Relay idempotency and a claim/lease protocol that survives duplicate reconnects and Mac restarts; Mac-agent admission of queued requests with request-ID propagation into jobs, receipts, and undo records; A compact pendant status protocol for queued, delivered, running, completed, failed, and expired states; Recovery rules for a lost acknowledgement, including reconciliation against the Mac job ledger before retrying


## Changes it proposed to its own stack

### `integration` — Add a deterministic bridge_reconnect executor and planner intent. It records startedAt, launches AI Pendant Browser Bridge only if needed, then polls the existing browser heartbeat/status state until it observes a heartbeat newer than startedAt. Return a typed result {online, heartbeatAt, pendingCommands, executedCommands:0, freshness}; explicitly prohibit computer_use_task and browser command polling/execution for this intent. Surface the same typed result in the Mac job receipt and relay/pendant spoken completion.
- **owner gets:** The owner can reliably reconnect the browser from the pendant and get an honest answer. Today the app-open step succeeds but the planner attempts a disabled screen-driving loop, producing a false failure; this removes that confusing dead end while protecting private tabs and queued commands.
- effort: Small-to-medium: deterministic intent, heartbeat freshness comparison, bounded polling, receipt schema, and one relay response formatter; add integration tests for already-online, newly-online, stale, and timeout cases.  ·  risk: A stale heartbeat could be mistaken for success if timestamps are not compared to the request start; clock skew must use server receipt time and sequence/monotonic heartbeat IDs where possible. App launch can be idempotent. On timeout, report unavailable without deleting commands or changing tabs.
- cost: Negligible API/model cost; status polling and one local app launch dominate.  ·  latency: 1–2 seconds when already online; up to 10 seconds only while waiting for a fresh heartbeat.
- security: Improves safety by avoiding computer-use and command execution. No page content, URLs, or pending command payloads should enter the spoken result.
- depends on: A freshness-aware /browser/status or /browser/heartbeat response (timestamp or monotonic sequence); A deterministic router intent before planner escalation; Receipt fields for typed status outcomes

### `mac-harness` — Make every UI-mutating receipt proof-aware without blocking execution: before and after ui_click, type_text, press_keys, and computer_use_task, attach the /observe inputReachability snapshot, foreground app, and target evidence when available. If eventsPost is false or accessibility is untrusted, set receipt.status to executed_unverified (not success), include the exact reason, and let the planner choose a shell/AppleScript/browser route or tell the owner verification is impossible. Preserve the owner's FULL_CONTROL_MODE and never add an approval gate.
- **owner gets:** The Mac currently reports UI actions as successful while /observe proves they can do nothing because Accessibility belongs to a different binary. Honest receipts prevent silent failures and let the agent recover through another surface instead of claiming a task is complete.
- effort: Medium: receipt status extension, pre/post observation hooks, planner fallback mapping, and tests for trusted versus untrusted Accessibility.  ·  risk: Some actions genuinely have no visible state change, so the result must remain executed_unverified rather than failed; fallback could duplicate an action unless idempotency keys and before-state evidence are carried forward.
- cost: Small local overhead for two observation snapshots per UI job; no additional model call unless recovery is needed.  ·  latency: Roughly tens to hundreds of milliseconds per UI action; recovery may add a planner turn only after an unverified result.
- security: No restriction added. Observation metadata may contain app names and window titles, so redact sensitive text before relay; do not upload screenshots without existing consent.
- depends on: Existing GET /observe reachability endpoint; Existing action receipts and undo records; Deterministic fallback routing for browser, shell, or AppleScript

### `integration` — Create a cross-surface causality ledger that assigns one immutable conversation/request ID at the pendant, propagates it through relay audio/transcription, planner decisions, Mac jobs, browser commands, and final spoken output, and materializes a compact timeline with explicit gaps (received, forwarded, claimed, executed, acknowledged). Reconcile late events by ID rather than timestamp and expose a redacted owner-facing 'what happened' view plus machine-readable diagnostics.
- **owner gets:** When a request crosses the pendant, cloud relay, Mac, and browser, today the owner cannot reliably distinguish lost, duplicated, still-running, or completed work. One causal timeline would let them ask 'what happened to that?' and receive a truthful answer even after a restart or delayed callback.
- effort: Medium-to-large: schema and propagation headers across relay and local-agent boundaries, durable append-only storage with retention, reconciliation of late/duplicate events, and a concise spoken formatter.  ·  risk: A ledger can accidentally retain sensitive transcripts or URLs; store hashes and redacted summaries by default, encrypt durable records, and apply short retention. Clock differences must never determine causality; IDs and sequence numbers must.
- cost: Small storage and write overhead per event; no extra model calls for the ledger. Background summarization is optional.  ·  latency: Negligible request-path overhead if events are appended asynchronously; owner-facing history lookup should return in under 1 second locally.
- security: Improves accountability but increases metadata concentration. Separate content from event metadata, enforce per-owner access, redact browser/private-page fields, and allow deletion by request ID.
- depends on: A propagated immutable request ID at pipeline ingress; Relay and Mac job schemas accepting correlation and parent IDs; Browser command and action receipt records exposing the same correlation ID; A retention/redaction policy and owner-facing history endpoint


## What it asked for

_Nothing._
