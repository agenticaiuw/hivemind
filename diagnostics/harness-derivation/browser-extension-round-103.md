# Harness derivation — browser-extension — round 103

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge availability** — The live browser bridge is currently offline: /browser/status reports online=false for the only known device (home-chrome, no tab/user agent) and 9 pending commands. Yet /browser/sessions retains three Safari-created sessions, last used around 06:26, including default at time.is/UTC. No live inspection records exist.
  - evidence: GET /browser/status → online:false, pendingCommands:9; GET /browser/sessions → default/probe-form/probe-form2 with tab IDs and stale lastUsedAt; GET /browser/inspections → inspections:[]
- **browser queue corruption** — GET /browser/poll returns a processing command claimed by offline home-chrome with an empty navigate params object, created at 09:11 and attempted 16 times. This is not merely queued Safari work; the stub device is repeatedly claiming a malformed command, likely starving the real browser queue.
  - evidence: GET /browser/poll → commandId browser_fc12217f-842e-4751-8697-c6c71706bd52, action {type:navigate,params:{},label:navigate}, status processing, claimedBy home-chrome, attempts 16

## Capabilities it proposed

### "“Safari went offline while you were doing that—resume the private browser task when it reconnects, skip anything already completed, and tell me exactly where it stopped if it cannot continue.”"
- **useful because:** Today the browser bridge can accumulate pending commands while the real Safari device is offline; resuming safely across sleep/network loss is the distinctive value of an authenticated browser surface. The owner gets continuity without duplicated clicks or silently abandoned work.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** background for reconciliation and page comparison; realtime only to acknowledge the owner's request and report a concise status
- **latency:** Acknowledge immediately; reconcile on extension heartbeat and finish within 1–3 minutes after Safari returns, with a bounded retry window and a clear stalled result.
- **cost:** Usually 1–3 background-model calls per interrupted task (roughly $0.01–$0.08 depending on page extraction); dominant cost is re-reading changed authenticated pages, not the status checks.
- **security:** Private page contents remain on the authenticated browser path; only structured progress and extracted evidence should leave it. Never replay a submit/send/purchase step automatically. Resume only idempotent navigation/read/fill steps and surface the exact pending irreversible step for owner review.
- **missing:** A durable command journal that records step fingerprints and completed results independently of the in-memory pending queue; Reconnect reconciliation that matches stored browser session/tab identity and verifies page state before replay; A dead-letter/stalled-task status exposed to pendant and dashboard; An explicit resume policy distinguishing safe reads/fills from irreversible actions

### "“Make a private evidence packet from this logged-in page that I can ask about later—even if Safari closes—containing only the passages and fields I selected, with source links, capture time, and an automatic expiry.”"
- **useful because:** Today an authenticated page is trapped in a live Safari tab: once the tab changes or the browser disconnects, the owner must expose the page again to ask a follow-up. An expiring, selectively extracted evidence packet gives the pendant and Mac continuity without copying an entire private account or granting the relay a reusable login session.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Background model for selecting/normalizing requested passages and generating a concise index; realtime only for the owner's immediate spoken confirmation. The relay should transport encrypted metadata, not raw page contents unless the owner asks.
- **latency:** Capture in under 10 seconds for a normal page; later pendant questions answer in under 2 seconds from the packet index, with a fresh browser read required after expiry.
- **cost:** One extraction call at roughly $0.01–$0.05 per packet and near-zero cost for indexed follow-ups; storage and encryption dominate operational cost rather than inference.
- **security:** The browser performs extraction while authenticated; packet contents are field-level selected, encrypted at rest, bound to the owner's device identity, and expire automatically (default 24 hours). Never include cookies, tokens, hidden inputs, or unselected page regions. Dashboard must show exactly what was captured and support immediate deletion.
- **missing:** A browser-side selection/extraction operation that returns DOM-anchored snippets and field values without serializing the whole page; An encrypted, expiring evidence-capsule store with per-field sensitivity labels and deletion receipts; A retrieval endpoint usable by pendant voice and Mac planner that enforces capsule expiry and device binding; A user-facing capture affordance (voice command plus extension button/context-menu selection); Citation rendering that survives minor page layout changes and marks stale sources


## Changes it proposed to its own stack

### `browser-harness` — Add a reconnect reconciler, separate from the durable job runner: persist each browser command's precondition fingerprint, result receipt, and action class; when /browser/status changes offline→online, atomically mark commands as completed, safely resumable, or stalled. Before replaying a resumable command, verify the bound session's tabId/URL/title and a lightweight page fingerprint; if it differs, stop and emit a dashboard/pendant event instead of clicking again. Expire the nine currently pending commands as stale rather than replaying them blindly, and expose dead-letter records with the exact last safe step.
- **owner gets:** When Safari sleeps or loses its extension connection, the owner will not get duplicate clicks, lost drafts, or a task that appears to vanish. They can resume from a trustworthy checkpoint and see precisely what needs their attention.
- effort: Medium: journal schema and migration, reconnect state machine, page-fingerprint verification, and tests for duplicate delivery and tab replacement.  ·  risk: A changed page may be conservatively classified as stalled even when replay would have worked; recovery is manual resume after showing the new page evidence. Atomic receipt handling prevents duplicate replay after a result arrives just as the bridge disconnects.
- cost: Negligible storage and status polling; one cheap extraction/fingerprint check per resumed step. No meaningful model cost unless a stalled task requests semantic reconciliation.  ·  latency: Adds roughly 1–5 seconds per resumed step for verification; no impact on healthy connected tasks.
- security: Improves safety for authenticated sessions by preventing blind replay. Store hashes and metadata by default, not page bodies; redact form values in the journal. Irreversible actions remain stopped.
- depends on: Existing browser command request IDs and result receipts in local-agent/browserBridge.js and browserSessions.js; A durable job record/receipt store (GET /jobs/:jobId and GET /jobs/:jobId/receipts); A browser status transition signal from GET /browser/status or extension heartbeat; A typed distinction between read/reversible-fill and irreversible browser actions

### `browser-harness` — Fence browser-poll claims by live device eligibility and validate action payloads before delivery. A device may claim commands only if its heartbeat is fresh and its extension identity matches the target session; reject/quarantine malformed actions such as navigate with missing URL, cap attempts, and release commands claimed by an offline/stale device. Add an operator-safe cancel/requeue endpoint for the current processing command and expose claimant, age, attempts, and quarantine reason in inspections.
- **owner gets:** A dead stub browser cannot repeatedly consume the owner's private Safari work. Tasks will either reach the real logged-in browser or visibly pause with a repairable explanation, instead of silently timing out or looping sixteen times.
- effort: Small-to-medium: poll claim transaction changes, schema validation, heartbeat TTL enforcement, stale-claim lease expiry, and one queue inspection/cancel path.  ·  risk: A genuinely slow extension could lose its lease and cause a safe read to be retried; idempotency keys and result receipt matching prevent duplicate completion. Malformed or irreversible commands are quarantined for review, never auto-repaired.
- cost: Near-zero compute/storage; fewer wasted browser retries and model calls.  ·  latency: Adds sub-second validation to polling; stale-claim recovery waits one heartbeat TTL (target 30–60 seconds).
- security: Reduces cross-device command leakage by enforcing target device/session affinity. Quarantined records should retain metadata and hashes, not private page bodies or form secrets.
- depends on: GET /browser/status heartbeat data; GET /browser/poll and POST /browser/result/:commandId; Existing browser command IDs, attempts, and session records; A durable inspection/queue record rather than only in-memory pending state

### `browser-harness` — Add a field-level private evidence capsule format, distinct from page watches or job receipts. The extension extracts only an owner-highlighted DOM range or explicitly named fields, replaces volatile/secret values with redaction markers, records a salted content hash plus resilient DOM anchors, encrypts the capsule to the owner's device key, and gives it an automatic TTL. A later reader must return citation, capture time, freshness, and a stale/reopen-in-Safari state rather than treating the capsule as current truth.
- **owner gets:** The owner can ask a follow-up about a logged-in page after Safari closes without preserving a whole private page or repeatedly reopening the account. They get bounded, inspectable context instead of an opaque long-lived copy.
- effort: Medium: extension extraction API and selection UX, capsule encryption/TTL service, anchor validation, deletion receipts, and pendant/Mac retrieval integration.  ·  risk: A selected range may omit context or become stale; every answer must expose the capture timestamp and offer a fresh read. Incorrect redaction is mitigated by refusing to capture password, token, hidden-input, and payment fields by element type and requiring an explicit override for other sensitive labels.
- cost: Small encrypted storage cost per packet; one extraction/normalization model call at capture and no model call for simple indexed lookup.  ·  latency: Capture adds roughly 1–10 seconds depending on page size; later lookup is near-instant until a fresh browser read is requested.
- security: Reduces data exposure versus whole-page retention: least-privilege selection, device-bound encryption, TTL deletion, and no cookies/session tokens in the capsule. Relay sees only opaque ciphertext and packet identifiers by default.
- depends on: A browser extension selection/extraction primitive; Device-bound key management shared by pendant and Mac; A small encrypted TTL store and deletion audit; A retrieval bridge for POST /pipeline/audio and Mac planner answers


## What it asked for

_Nothing._
## Its own summary

Discovered a concrete live failure beyond the existing backlog: the bridge is offline, nine commands are pending, and /browser/poll is repeatedly delivering a malformed empty navigate command to the offline home-chrome stub (processing, 16 attempts). I recorded this, notified mac-planner, and proposed (1) reconnect checkpoint reconciliation and (2) device-eligibility fencing plus malformed-command quarantine. What I still need is a fresh Safari extension heartbeat/real tab (or an operator action to bring Safari online), and a queue-admin path to release/cancel the currently stuck command; without those, authenticated page work cannot execute safely.

**Biggest unknown:** Why the malformed command exists and whether home-chrome can be disabled or its stale claim released without affecting the real Safari device.

