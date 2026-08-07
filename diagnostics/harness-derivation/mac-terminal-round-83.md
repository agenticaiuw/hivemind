# Harness derivation — mac-terminal — round 83

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent reliability** — Live /ops/snapshot reports browser extension offline with 5 pending commands; /journal contains repeated identical Order 42 Processing→Shipped reports; /routing shows 112 unattributed actions in the current 120-job window and 14 failed actions.
  - evidence: GET /ops/snapshot, GET /journal, and GET /routing returned HTTP 200 at 2026-08-07T12:43Z; snapshot browser.online=false and pendingCommands=5; journal repeats the same report IDs/content; routing totals unattributedTier=112 and failed=14.

## Capabilities it proposed

### ""Keep my browser tasks reliable: if Safari disconnects, stop retrying blindly, tell me once what is waiting, resume when it reconnects, and never alert me about the same page change twice.""
- **useful because:** The live Mac snapshot shows the browser bridge offline with 5 pending commands; the journal contains repeated identical Order 42 change reports, and /ops data shows browser_list_tabs ran 37 times with 7 failures. Today the owner can receive duplicate alerts or wait through doomed retries without knowing the real state. A cross-surface liveness lease, durable queue, and semantic notification dedupe turns a flaky bridge into dependable background work.
- **path:** browser-extension → mac-planner → relay-realtime → unified → dashboard
- **model tier:** background for liveness classification, retry scheduling, and semantic fingerprint comparison; deterministic for queue state, lease expiry, and exact duplicate suppression; realtime only to speak one concise outage/resumption notice on the pendant.
- **latency:** Bridge heartbeat evaluation under 2 seconds; reconnect drain begins within 5 seconds of a healthy heartbeat. One outage notice immediately and one recovery summary after reconnect; no per-retry model call.
- **cost:** Near-zero when healthy (deterministic heartbeats and hashes). Roughly 1 cheap background call per genuinely changed watch batch, not per poll; realtime cost only if the owner is actively listening for the spoken notice.
- **security:** Queue metadata must retain only session/tab identifiers and encrypted private results, never expose page contents in relay logs. Reconnect must revalidate the browser session binding before replaying any action. Reads may resume automatically; queued writes need the existing action receipt/undo semantics and should remain explicitly marked in the spoken/dashboard summary. No URL or excerpt should be spoken unless the owner asks.
- **missing:** A durable per-session browser connection lease with monotonic heartbeat and explicit offline/online transitions; A queue state machine that coalesces superseded reads, applies bounded exponential backoff, and resumes idempotently after reconnect; A semantic watch fingerprint store keyed by watch id and source revision, so identical changes produce one report and later retries reference the original report; A notification acknowledgement/recovery record shared by relay and dashboard; A health-triggered command-drain worker; current /browser/poll and /browser/result/:commandId are transport endpoints, not a durable scheduler

### ""When you change something for me, don't just say the command ran—check that the intended result is actually true, keep watching it briefly, and tell me if it failed or was undone.""
- **useful because:** Today a Mac receipt can report that an action completed, but completion is not the same as the owner's desired state: a setting may be overwritten by another process, a file may be rejected by a sync service, or a browser form may display a stale success page. The owner needs outcome verification rather than execution theater, especially when they are away from the Mac and only have the pendant to hear the result.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard-ux
- **model tier:** Deterministic checks first (exit status, file hash, app state, browser DOM value, receipt evidence). Use the cheaper background model to select or interpret a verification probe when the request is ambiguous. Use realtime only for a concise success/failure report while the owner is engaged; do not spend the realtime tier on polling.
- **latency:** Initial verification within 2 seconds of a local action when possible; delayed checks at 10 seconds and 2 minutes for state likely to converge. Report provisional completion immediately only when labeled provisional, then replace it with a verified result.
- **cost:** Minimal for typed checks and hashes. One background-model call only when deriving a probe from a natural-language goal. Browser and Mac polling add small local/relay traffic but no recurring planner calls.
- **security:** Verification must not broaden access beyond the original task: do not inspect unrelated files, tabs, or account data. Store hashes and typed state where possible rather than raw private content. A failed verification must never silently trigger a compensating mutation; the owner should be told what was observed and what, if anything, is proposed next.
- **missing:** A goal-level contract separating intended outcome from the action steps that attempt it; A typed postcondition probe registry for Mac files/settings/apps, browser DOM values, and relay/persistent state; Delayed verification timers tied to the original job with cancellation and expiry; Evidence linking that records observed-after state and confidence, not merely action receipts; A unified result vocabulary such as verified, provisionally-complete, contradicted, or unverifiable across pendant speech and dashboard


## Changes it proposed to its own stack

### `relay` — Implement an exactly-once notification outbox for browser-watch and Mac-job events. Normalize each event to a stable fingerprint (watch/session + source revision + semantic change hash), store one outbox row with delivery states for pendant speech, dashboard, and optional iOS push, and require each consumer to acknowledge that row. Retries may redeliver transport packets but must not create a second spoken/dashboard item; recovery events should reference the original event. Add a compact reconciliation endpoint that reports pending, acknowledged, suppressed-duplicate, and expired notifications.
- **owner gets:** The owner hears one useful “your order shipped” rather than the same change repeatedly, and can see whether an important event is waiting, spoken, or merely failed delivery. It also prevents a disconnected browser or sleeping pendant from turning retries into notification spam.
- effort: Medium: D1 outbox schema and unique fingerprint constraint, relay delivery workers, acknowledgement plumbing in pendant/dashboard/iOS, and migration of existing page-watch reports.  ·  risk: An over-aggressive fingerprint could suppress a real update; include source revision and a bounded time window, and expose suppressed items in the dashboard for inspection. If speech delivery fails after acknowledgement, the dashboard remains the durable fallback. Do not put authenticated page excerpts in generic relay logs.
- cost: Tiny D1 writes per distinct event and no model calls for dedupe; one cheap background classifier only when raw watch payloads cannot be normalized deterministically. Speech cost falls because duplicate announcements disappear.  ·  latency: Sub-100 ms deterministic outbox write; delivery asynchronously within the existing relay heartbeat/pipeline cadence.
- security: Store opaque event IDs and encrypted/private payload references in relay; send excerpts only over the paired authenticated channel. Acknowledgements must be scoped to the paired owner/device, not a public URL.
- depends on: Existing page-watch reports in /logs and browser result receipts; Relay D1 job/history store and durable audio pipeline; GET /browser/status plus browser heartbeat transitions; Existing dashboard shared by web, menubar WKWebView, and iOS Capacitor; A per-watch source revision/fingerprint field, which does not currently exist


## What it asked for

_Nothing._
