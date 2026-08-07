# Harness derivation — mac-planner — round 70

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner round 70 tool availability** — Granted mac_readonly_inspect and mac_read_sources have schemas but no backend implementation; calls return explicit implementation-missing errors. /ops/status also reports Accessibility trusted=false, Screen Recording granted=false, browser offline with 4 pending commands, and ready=false.
  - evidence: Parallel calls to mac_readonly_inspect and mac_read_sources returned 'tool was granted a schema but has no implementation yet'; GET /ops/status HTTP 200 payload.

## Capabilities it proposed

### "“Remember this for me, and let me get back to the exact place later.”"
- **useful because:** The owner can be interrupted while reading a private webpage or document and resume without hunting through tabs or explaining the context again. The pendant gives a short spoken reminder; when they return to the Mac, the system reopens the same document or authenticated tab at the recorded location, while keeping the captured content minimal.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for the spoken capture/confirmation. Use a cheaper background model to normalize the bookmark, redact unnecessary text, and resolve the resume target. The Mac and extension do deterministic capture and reopening; the relay stores the durable handoff.
- **latency:** Acknowledge the capture within 1 second; save the handoff locally/relay within 3 seconds. Resume should take under 10 seconds when the Mac and browser are online, otherwise the pendant reports a queued handoff.
- **cost:** Low: one short realtime turn plus an occasional small background normalization call; storage is a tiny structured record and optional short audio, not a page archive. The dominant cost is only if the owner includes a long note.
- **security:** Authenticated URLs, tab identifiers, document paths, and selected text are sensitive. Store a redacted structured locator by default (app, tab/session binding, title, section/scroll anchor, timestamp), encrypt relay state, expire unreachable locators, and require the owner’s explicit spoken confirmation before reopening a private session on a different Mac/browser identity. Never transmit full page content unless requested.
- **missing:** A cross-surface 'attention cursor' schema linking pendant capture, relay job, Mac document locator, and browser tab/session without copying page contents; Mac and browser adapters that can capture the current selection/semantic anchor and later reopen it deterministically; Pendant playback and button control for browsing saved resume points offline; Encrypted, expiring relay storage and a dashboard for deleting or reviewing saved handoffs


## Changes it proposed to its own stack

### `integration` — Build a cross-surface connectivity supervisor with leases, not just a command queue: the relay, Mac agent, and browser extension each publish a heartbeat/capability lease; queued browser work is bound to the lease it was created under, automatically quarantined (never replayed) when that lease expires, and resumed only after the same tab/session is re-attested. The Mac agent should expose one actionable reconnect state, while the relay sends the pendant a concise 'paused / resumed / discarded' status and preserves the job receipt.
- **owner gets:** The owner will stop getting silent failures or four commands stuck behind an offline browser. If their Mac sleeps, the extension disappears, or a tab changes, work pauses safely and then continues only when it is genuinely safe, with an understandable spoken explanation.
- effort: Medium-high: lease protocol and state machine in relay + Mac bridge, extension heartbeat/reconnect handler, stale-command migration, receipt and pendant notification wiring, plus crash/restart tests.  ·  risk: A lease bug could quarantine legitimate work or duplicate a resumed job. Mitigate with idempotency keys, explicit terminal states (quarantined is not retryable without re-review), and a local/relay receipt for every transition. No page content needs to leave the Mac beyond the existing authorized extraction.
- cost: Negligible steady-state API cost; heartbeat traffic is small. One additional background model call only when a job needs re-planning after session loss, preferably a cheaper tier.  ·  latency: Heartbeat detection adds at most the lease interval (target 15–30 seconds) to failure recognition; normal browser actions are unchanged.
- security: Improves security by preventing replay into a different tab or stale authenticated session. Lease tokens must be short-lived, scoped to extension/tab/session, and never spoken or logged with secrets.
- depends on: A functioning browser extension heartbeat/reconnect endpoint; Durable browser job state and idempotency receipts; Relay-to-pendant job status delivery

### `mac-harness` — Finish the two newly granted read-only Mac surfaces in the host: implement mac_readonly_inspect (running apps, foreground app, accessibility/screen-recording state, UI snapshot, browser tabs, approved directory listings) and mac_read_sources (Calendar/Mail snippets with redaction and bounded limits), returning typed errors when a permission is absent instead of an unimplemented-tool error. Feed their results into the server plan context with timestamps and source labels.
- **owner gets:** The pendant can get a truthful answer about what is on the Mac and what needs attention without taking control, scraping the UI, or guessing. Workday briefs and safe browser handoffs can finally distinguish 'nothing there' from 'the Mac could not inspect it.'
- effort: Medium: implement host adapters, permission-aware error handling, redaction tests, and typed response schemas; no model training required.  ·  risk: Calendar/Mail or UI data could be over-collected. Keep defaults bounded and redacted, enforce approved paths and source allowlists, and omit snapshots unless explicitly requested or required for a task.
- cost: No meaningful API cost; local AppleScript/accessibility calls dominate. Optional UI snapshots add local compute and upload cost only when vision is consented.  ·  latency: Read calls should complete in roughly 0.2–2 seconds; UI snapshots may take longer. They are read-only and can run in parallel.
- security: These are sensitive local reads. Preserve account_scope, redaction, and permission checks at the host boundary; never place raw mail bodies or screenshots in general model context by default.
- depends on: Implementations behind the granted mac_readonly_inspect and mac_read_sources tools; Accessibility and Screen Recording permissions if UI snapshots are needed; A typed context/result envelope in the Mac-to-relay handoff


## What it asked for

_Nothing._
## Its own summary

Round 70 discovered concrete readiness blockers and recorded two changes: a cross-surface lease/heartbeat supervisor that quarantines stale browser work, and implementation of the newly granted read-only Mac inspection/source adapters. Live Mac bridge and relay are reachable, but the Mac reports ready=false, Accessibility untrusted, Screen Recording missing; browser extension is offline with four pending commands. The granted read-only tools currently have schemas but no implementation.

**Biggest unknown:** Whether the browser extension can reconnect and provide stable tab/session identity; waiting for browser-extension peer confirmation.

