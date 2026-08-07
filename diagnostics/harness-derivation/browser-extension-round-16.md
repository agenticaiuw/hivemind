# Harness derivation — browser-extension — round 16

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Every weekday morning, check my authenticated work portal for new high-priority items and tell me only what needs my attention."
- **useful because:** The browser is the only node that can use the owner's existing logged-in session. A persistent watch would turn a hidden portal into a concise morning briefing without asking the owner to copy links or credentials.
- **path:** browser → relay → pendant → dashboard
- **model tier:** Background/cheap model performs polling, DOM normalization, semantic diffing, and priority ranking; realtime model is used only if the owner asks follow-up questions by voice. Browser agent reads the authenticated page and relay stores the durable watch state.
- **latency:** Initial setup under 30 seconds; each scheduled check should complete within 60 seconds, with the pendant briefing available within 2 minutes of the scheduled time.
- **cost:** Low: one cheap background extraction/ranking invocation per poll plus small diff context; avoid sending unchanged page content to the realtime model. Dominant cost is authenticated page extraction frequency, so use adaptive polling and semantic hashes.
- **security:** The browser session can expose work-sensitive data. Keep raw page captures encrypted and short-lived, retain only extracted items and evidence references, and make the watch pauseable. Never submit, send, delete, or change portal data as part of the watch; surface proposed actions separately. Data leaves Safari only to the relay for ranking and the owner's briefing.
- **missing:** Durable browser watch scheduler and authenticated-session watch records; DOM-to-semantic extraction with stable item IDs and evidence snippets; Priority rules/owner labels for this portal; Ledger events with jobId,parentId,sequence,idempotency key, retryable error, and session status; A concise pendant audio briefing and dashboard drill-down to source evidence

### "When I say 'handle this' about something I found in Safari, gather the needed details across my logged-in tabs, fill the reversible parts, and show me exactly what will be sent before stopping."
- **useful because:** The browser node can combine private context from multiple authenticated tabs that public search and the Mac shell cannot access. This removes tedious copying while preserving the owner's control at the point of sending, purchasing, submitting, or deleting.
- **path:** browser → mac-vision → relay → pendant → dashboard
- **model tier:** Use a cheap background model for tab discovery, field mapping, cross-tab extraction, and deterministic form filling; use the realtime model only for the owner's spoken clarification and final concise review. Use a stronger model only when page structure or field semantics are ambiguous.
- **latency:** Collect context and fill a normal form within 1–3 minutes. The final review should be immediately available as text on the dashboard and a short spoken summary on the pendant.
- **cost:** Moderate but bounded: extraction and field mapping are sent as compact schemas rather than full pages; strongest-model calls only on ambiguity. Main cost is repeated page reads, reduced with per-tab snapshots and hashes.
- **security:** Cross-tab data aggregation can reveal sensitive personal or work information, and form filling can accidentally alter fields. Keep an action plan and before/after field diff, restrict automatic operations to drafts/reversible edits, redact secrets in logs, and stop before submit/send/purchase/delete. The owner explicitly reviews the exact payload and destination.
- **missing:** Cross-tab session graph with tab identity and provenance; Structured form-field extraction and before/after diff receipts; Draft-only browser action mode with a hard submit boundary; Owner-facing review card with exact payload, destination, attachments, and expiry; Idempotent resume/retry so a dropped link does not duplicate edits


## Changes it proposed to its own stack

### `browser-harness` — Build a durable authenticated page-watch service: named watch definitions store URL/tab/session binding, extraction selectors or an agentic extraction recipe, schedule, semantic fingerprint, last seen item IDs, evidence artifact TTL, and pause/reauthentication state. The scheduler leases each run and emits idempotent ledger events; the browser harness navigates/reads but cannot submit forms.
- **owner gets:** The owner gets ongoing awareness of logged-in sites—work queues, travel reservations, health portals, and bills—without repeatedly opening them or granting credentials to a new integration.
- effort: Medium-high: browser watch scheduler, robust DOM extraction, login/session expiry handling, semantic diffing, and dashboard controls.  ·  risk: Pages change structure, watches may misclassify or expose sensitive content, and stale sessions may cause false 'nothing new' results. Recover with health status, evidence snippets, explicit stale-session alerts, bounded retries, and a one-click pause/delete.
- cost: Low-to-moderate background token cost proportional to polling frequency; encrypted evidence storage is the main infrastructure cost.  ·  latency: Scheduled checks are asynchronous; a changed page should reach the owner in roughly 1–2 minutes. No impact on realtime voice.
- security: Read-only browser scope by default; encrypt artifacts, minimize retention, redact secrets, and never carry submit/click mutations in the watch worker.
- depends on: Durable ledger/event API; Browser command enqueue path that reliably navigates and reads Safari; Dashboard controls for watch setup and evidence review

### `browser-harness` — Add a provenance-aware browser workbench: every extraction and field mutation gets a tabId, URL, timestamp, DOM locator, source snippet hash, action plan, and before/after value. Group tabs into a task session and expose a generated 'ready to submit' review artifact; submission remains a distinct command that is never implicitly chained.
- **owner gets:** The owner can ask the system to prepare a complex task across logged-in sites and then trust the review because every value is traceable to a source and every change is visible before anything consequential leaves the browser.
- effort: High: stable locators across dynamic pages, tab/session correlation, reversible edit tracking, review rendering, and recovery after navigation or extension restarts.  ·  risk: Dynamic pages can invalidate locators; stale drafts could be submitted later with changed prices or recipients. Expire review artifacts, re-read critical fields before final review, mark stale data clearly, and provide undo/reload where supported.
- cost: Moderate storage for compact receipts and occasional re-read calls; cheaper than retaining full page snapshots.  ·  latency: Adds seconds for provenance capture and final verification; avoids costly and dangerous blind retries.
- security: Receipts may contain PII or payment details. Encrypt at rest, redact by field type, enforce TTL, and ensure logs contain hashes/labels rather than secret values.
- depends on: Reliable browser command enqueue and result correlation; Durable ledger with idempotency and leases; Dashboard/pendant review surface


## What it asked for

_Nothing._
