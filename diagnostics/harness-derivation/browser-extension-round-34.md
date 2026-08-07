# Harness derivation — browser-extension — round 34

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge availability** — As of 2026-08-07T09:21:08Z, /browser/status reports online=false; Safari is not registered, home-chrome is offline with no tab, and pendingCommands=2. Browser execute jobs waited about 45 seconds before failing with an offline message.
  - evidence: GET /browser/status and GET /ops/status; GET /jobs showed two failed browser_navigate jobs with 45-second durations and no completed actions.

## Capabilities it proposed

### "When I say “save this page for later,” capture the logged-in Safari page I’m looking at, keep it private on my Mac, and let me ask the pendant about it later—even if the site logs me out."
- **useful because:** Authenticated pages disappear when a tab closes or a session expires. This creates a durable, searchable handoff from the browser’s private session to the Mac without making the owner keep the tab open or send sensitive content to a cloud service.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard-ux
- **model tier:** Use realtime only to recognize the short pendant command and acknowledge capture; use a cheaper background model on the Mac to clean page structure, title, dates, entities, and a compact local summary. Relay stores only the capture ID and status, not page text.
- **latency:** Acknowledge within 1 second; capture DOM/text and local encryption in under 5 seconds for a normal page; background indexing can take 10–30 seconds. If the bridge is offline, tell the owner immediately and offer to retry when it returns.
- **cost:** Near-zero relay cost beyond metadata; one small background text-model invocation per capture dominates (typically cents or less), with no model call needed for raw local storage.
- **security:** Page content may contain financial, health, or work secrets. Encrypt the snapshot and derived index at rest using a Mac-held key, keep relay payloads to opaque IDs/status, record source URL/tab/time, and let the owner delete one capture or all captures. Never capture password fields, hidden form values, or cross-origin iframes by default. This is a reversible local save and needs no confirmation, but any later form submission remains blocked by the existing stop-before-submit policy.
- **missing:** A browser-extension command to export a sanitized current-tab snapshot with field redaction and size limits; Mac-local encrypted capture store with full-text/semantic indexing and deletion controls; Relay metadata records and reconnect retry for capture jobs; Pendant intents such as save-page, list recent captures, and ask-about-capture; Dashboard UI showing source URL, capture time, retention, and delete/export actions

### "Let me have a private “talk to this page” mode: while I’m viewing a logged-in Safari page, I can ask the pendant questions such as “what does this clause mean?”, “where does it say that?”, or “compare this section with the one above,” and hear concise answers with the exact page location read back. Keep the conversation anchored to that tab until I say stop."
- **useful because:** Today the browser can be read as a one-off task, but the owner cannot naturally interrogate a private page hands-free while reading it. This would turn the authenticated browser session into an accessible conversational surface for contracts, dashboards, support pages, and long documents without repeatedly explaining the URL or copying text.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard-ux
- **model tier:** Use the realtime model for the short, low-latency question/answer loop. The extension extracts the visible region and nearby semantic sections locally; a cheaper background model can build a rolling section index and resolve references such as “above” or “the number in the second table.”
- **latency:** Under 1.5 seconds for a visible-text question and under 3 seconds for a cross-section comparison. The extension should send incremental region updates rather than the whole page on every turn.
- **cost:** Realtime conversation tokens dominate, but incremental page chunks and a bounded rolling context keep each turn materially cheaper than resending an entire page. Background indexing is a small per-page text-model charge and can be skipped for short pages.
- **security:** Authenticated page text can include sensitive work, financial, or health information. Keep extraction scoped to the bound tab and visible/selected DOM regions by default; redact password inputs and hidden fields; disclose the page title/domain on activation; expire the binding when the tab closes; and provide a one-button purge of the relay conversation and local index. No form submission, clicking, or other mutation is part of this mode.
- **missing:** A persistent browser-tab conversational binding with tab identity, URL, title, and expiry; An extension protocol for incremental visible-region/selection extraction and stable DOM location anchors; Relay support for a low-latency page-context stream with bounded rolling context instead of one-shot browser jobs; Pendant intents for activate-page-mode, follow-up references, and stop-page-mode; Spoken and dashboard citations that map answers back to headings, line ranges, or DOM anchors


## Changes it proposed to its own stack

### `browser-harness` — Add a cross-surface browser-health lease and recovery handoff. The relay/local agent should continuously normalize extension state into healthy, no-tab, stale, offline, or unknown using lastSeenAt/leaseExpiresAt, device identity, and pending-command age. Before dispatching any browser_* action, perform a cheap preflight: healthy dispatches; no-tab returns an immediate bootstrap instruction (or runs browser_navigate only when a live poller exists); stale/offline returns a typed receipt without waiting 45 seconds. Persist the requested browser task as a resumable job keyed to the Safari device, but do not enqueue duplicate commands; when the extension heartbeats again, surface one pendant notification and resume only idempotent read/extract steps. Include the exact recovery action (open Safari, enable bridge) and a link to the failed task in the Mac dashboard.
- **owner gets:** Today a private-page request burns roughly 45 seconds and fails twice because the bridge is offline, with no useful distinction between Safari being closed, the extension being stale, and there being no tab. The owner gets an immediate honest answer, can fix the one missing thing, and the task can continue after Safari returns instead of being forgotten or duplicated.
- effort: Medium: shared health state/lease, preflight in execute and relay dispatch, resumable read-step queue, duplicate suppression, dashboard and pendant receipt wording, plus extension heartbeat tests.  ·  risk: A stale lease could be misclassified and suppress a task while Safari is actually usable, or resume against the wrong tab. Bind jobs to extensionId plus tab/session affinity, require a fresh heartbeat before resume, and resume only navigation/read/extract actions; retain the existing stop-before-submit behavior. Failed queued jobs remain inspectable and cancellable.
- cost: Negligible API cost (health checks and receipts); modest D1/local JSON storage for lease and resumable step state. No page content leaves the device unless the requested extraction already sends it to the relay.  ·  latency: Healthy browser work gains one local health check (<100 ms); offline/stale requests fail in milliseconds instead of ~45 seconds. Recovery notification is event-driven on the next heartbeat.
- security: Preserves authenticated data on the Mac/extension path, exposes only device/lease metadata to the relay, and prevents accidental replay against a changed tab through explicit session binding.
- depends on: Safari extension heartbeat must report a stable extension/device identifier and lease timestamp; Browser job runner must support idempotent step IDs and resumable read-only steps; Pendant/relay notification path and Mac dashboard receipt surface


## What it asked for

_Nothing._
