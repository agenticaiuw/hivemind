# Harness derivation — browser-extension — round 70

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension availability round 70** — Live /browser/status reports Safari absent/offline and only stale home-chrome (tabCount null), with 5 pending browser commands. /browser/sessions still contains three historical sessions including default time.is/UTC, but they are not proof of a live extension.
  - evidence: GET /browser/status HTTP 200: online false, devices=[home-chrome offline], pendingCommands=5; GET /browser/sessions HTTP 200: historical sessions.

## Capabilities it proposed

### "If I ask you to check something in Safari while my laptop is asleep or the browser is disconnected, remember the request, run it automatically when Safari comes back, and tell me what you found (or that it could not run)."
- **useful because:** The pendant can capture an authenticated-browser task at the moment the owner thinks of it, while the browser is inherently intermittent. Today five commands are queued while the only registered browser device is offline, with no owner-facing durable handoff or clear outcome.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use realtime only to capture/confirm the short intent; use a cheap background model to classify the task and summarize extracted page deltas after reconnect. No model is needed for queue/retry state.
- **latency:** Acknowledge intent in under 1 second; retry on extension heartbeat with exponential backoff and quiet hours; summarize within 30 seconds of Safari reconnecting. Never spin a realtime session while offline.
- **cost:** Usually <$0.01 per completed task for background extraction/summarization; dominant cost is page text sent to the background model, not queueing. No cost for missed retries.
- **security:** Persist only encrypted task intent and target session/watch identifier, never page credentials or raw cookies. Authenticated page content leaves Safari only when the queued task runs and should have short retention. For mutations, preserve the owner's maximum-access policy but retain the existing stop-before-submit behavior and show the exact payload; notify on reconnect if the target/session changed.
- **missing:** A durable offline browser-intent queue with idempotency and retry/expiry state; Extension heartbeat recovery that distinguishes stale historical sessions from a live tab; A working enqueue implementation (all currently granted browser enqueue wrappers return implementation errors); Pendant/relay notification when a queued browser job completes or expires

### "While I’m looking at a logged-in webpage, let me ask the pendant “what am I looking at?” or “what should I notice here?” and get an answer about the currently visible section, without copying text or naming the site."
- **useful because:** The owner can physically see the page but cannot currently give the pendant reliable visual/page context hands-free. This is different from saving or watching a page: it is ephemeral, tied to the active viewport, and should disappear when the tab or focus changes.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Use realtime for the short spoken question and answer; use a small text/vision model only when the page contains complex layout or images. The extension supplies bounded active-viewport text and optional screenshot rather than sending an entire tab.
- **latency:** Under 2 seconds for ordinary text pages; under 4 seconds when a screenshot/layout interpretation is needed.
- **cost:** Typically <$0.01 per question for bounded extracted text; <$0.03 when a screenshot requires vision. Cost is controlled by viewport clipping and deduplication of unchanged page context.
- **security:** Only transmit the active tab’s visible region after a spoken request; exclude password fields, hidden DOM, other tabs, and background pages. Show the site/title in the reply so accidental context is detectable. Treat screenshot capture as sensitive, encrypt in transit, and retain no page payload after the response.
- **missing:** An extension event for active-tab focus and viewport/selection changes; A bounded browser_context result containing visible text, accessibility tree, URL/title, and optionally a redacted viewport screenshot; A relay voice route that passes this context to the realtime agent for one turn without persisting it; A redaction layer for password, payment, and hidden form controls


## Changes it proposed to its own stack

### `browser-harness` — Add an offline browser handoff coordinator between /execute and the extension bridge. When a browser task is requested, persist an intent envelope (jobId, session/watch id, action DAG, idempotency key, expiry, retry count, sensitivity, and result destination) instead of leaving opaque commands in the in-memory pending queue. On each real extension heartbeat, reconcile device identity and tab/session affinity, drain eligible intents in order, post typed results to the job receipt, and emit one completion/expiry event to relay and dashboard. Quarantine the current 5 stale pending commands rather than replaying them blindly; expose cancel/retry/resume operations.
- **owner gets:** A spoken request made while Safari is closed becomes reliable instead of silently timing out. When the Mac reconnects, the owner gets one clear result and can tell whether anything ran, rather than wondering why a private-page check disappeared.
- effort: Medium: coordinator/state schema, heartbeat reconciliation, result-to-job wiring, dashboard status, and migration of opaque pending commands.  ·  risk: A stale intent could run against the wrong logged-in account or changed page. Bind to extension identity plus session/tab fingerprint, expire on mismatch, and require re-planning on navigation changes. Recover by canceling or replaying a typed intent; do not replay mutations after an unknown result.
- cost: Negligible storage/compute; <$0.001 per queued task. Background summary model cost remains proportional to extracted page text.  ·  latency: Immediate local acknowledgment; completion waits for next heartbeat, typically seconds when Safari is open, unbounded but observable while offline.
- security: Improves security by removing opaque indefinite command retention and adding expiry/audit provenance. Encrypt intent metadata at rest; keep page contents only in short-lived job result storage.
- depends on: A working browser command enqueue implementation (currently all granted wrappers report no implementation); Stable extension heartbeat/device identity and tab/session affinity; Durable jobs/receipts integration

### `browser-harness` — Add a privacy-preserving active-viewport context channel: the Safari extension reports focus, URL/title, viewport bounds, accessibility text, and selection changes only on explicit one-shot requests, with sensitive-input redaction and a short-lived context token. /execute can consume that token for a single relay voice turn, and the token expires on tab navigation, blur, or 30 seconds.
- **owner gets:** The pendant can answer questions about the page the owner is actually viewing, hands-free, without requiring copy/paste and without leaving a persistent copy of private web content behind.
- effort: Medium: extension content-script/accessibility extraction, redaction tests, token binding to tab and navigation state, and one-turn relay integration.  ·  risk: A page could expose sensitive visible text or misleading accessibility labels. Default to text-only, redact known secret fields, bind context to the active tab, and make the spoken answer identify the source page. If extraction fails, return no context rather than a stale page.
- cost: Small relay/storage overhead and generally <$0.01 per text question; optional screenshot/vision is the expensive path and should be opt-in per request.  ·  latency: Adds roughly 200–800 ms for extraction and transport; complex visual interpretation adds 1–3 seconds.
- security: Reduces data exposure versus whole-page capture because context is viewport-bounded, explicitly requested, ephemeral, and never persisted. Requires careful redaction before relay upload.
- depends on: A functioning browser command/result path; Safari extension active-tab and viewport instrumentation; A one-turn relay context endpoint coupled to the realtime voice session


## What it asked for

_Nothing._
## Its own summary

I discovered a live reliability gap rather than re-proposing the already-known page-watch features: Safari is currently offline, only stale home-chrome is registered, and 5 browser commands are pending. I recorded this finding and proposed a durable offline browser handoff that persists spoken intents, reconciles real heartbeats/session identity, drains safely on reconnect, and reports completion or expiry through jobs, receipts, relay, and dashboard. I also notified mac-planner.

**Biggest unknown:** The actual Safari extension cannot currently be exercised: every granted enqueue wrapper still returns an implementation error, and /browser/status has no live Safari heartbeat. I still need a functioning enqueue path plus a real Safari heartbeat/tab before I can validate authenticated page reads, retries, or stale-command quarantine.

