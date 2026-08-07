# Harness derivation — browser-extension — round 58

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser connectivity** — As of round 58, GET /browser/status reports offline=true with only home-chrome registered, no tab, and 4 pending commands. Route table does expose POST /browser/heartbeat, GET /browser/poll, POST /browser/result/:commandId, and browser session CRUD, but no attach/list-tabs route; heartbeat is extension-facing and was not invoked manually.
  - evidence: GET /browser/status response plus discover(routes) listing

## Capabilities it proposed

### "“While I have this logged-in page open, tell me immediately if something important changes—and if I’m offline, catch me up when I reconnect.”"
- **useful because:** This is the browser's unique value: it can observe pages behind existing logins. The owner gets timely alerts without a noisy polling briefing, and does not lose events during a sleeping Mac, disconnected relay, or dropped pendant link.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Safari performs local mutation filtering and redaction; a cheap background model classifies candidate changes and compares them with the watch baseline; realtime is used only to phrase an urgent pendant interruption or answer a follow-up. Mac-planner stores the cited review item and can correlate it with local calendar/files when requested.
- **latency:** For an open active tab, 2–10 seconds from meaningful DOM change to relay classification; under 30 seconds to pendant when urgent. Reconnect digest can be delivered within a minute, without blocking normal conversation.
- **cost:** Usually fractions of a cent per event because most mutations are discarded locally; occasional cheap-model classification dominates. Realtime audio tokens are spent only for urgent spoken alerts.
- **security:** Only explicitly watched tabs participate. Keep raw DOM local unless the owner requests evidence; send a semantic digest plus URL/tab/time, encrypt queued events, expire them, and visibly show watch state. Never click, submit, send, or purchase automatically; drafts and suggested next steps remain reviewable.
- **missing:** Extension content-script mutation observer with semantic redaction and bounded encrypted offline queue; Durable page-watch event ingestion, deduplication, and recovery markers; Relay-to-pendant urgent notification queue and Mac review-item integration; Owner controls for per-watch urgency, quiet hours, and snippet-sharing

### "“Use my logged-in pages to answer this, but show me exactly which private fields left Safari, keep the answer useful, and forget the raw page afterward.”"
- **useful because:** Today the browser can either expose page content to the agent or leave the owner guessing what was transmitted. This gives the owner a practical privacy contract: Safari produces a task-specific field-level disclosure manifest, the relay answers from only those fields, and the pendant can explain or revoke the disclosure. It enables useful cross-site assistance without making unrestricted page capture the default.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** The extension performs local DOM classification and redaction; a cheap background model selects the minimum fields needed for the stated task and generates the disclosure manifest. Mac-planner correlates only the resulting structured facts. Realtime is used only if the owner asks a spoken question or requests an audible disclosure summary.
- **latency:** 2–5 seconds to identify and present the proposed fields, then under 10 seconds for a normal answer after the owner accepts. Revocation and deletion confirmation should complete within a few seconds.
- **cost:** Low: local extraction does most work; a small background-model call for field selection and validation dominates. No raw-page replay or expensive realtime call unless explicitly requested.
- **security:** The manifest itself can reveal sensitive categories, so display it locally first and encrypt it in transit. Enforce field and purpose binding: the relay cannot request additional fields without a new proposal. Store only the structured answer and manifest, expire raw extracts immediately, and provide a pendant command to delete the active task's server-side artifacts. Never use this mechanism to submit forms, send messages, or make purchases.
- **missing:** Extension-side task-scoped extractor that labels fields and produces a local before-send disclosure preview; A relay protocol enforcing purpose-bound, minimum-field requests and rejecting undeclared data; A short-lived encrypted evidence store with verifiable deletion receipts; Pendant/dashboard UI for approve, narrow, revoke, and inspect disclosures; Mac-planner support for reasoning over typed disclosed fields rather than raw page text


## Changes it proposed to its own stack

### `browser-harness` — Add an extension-local authenticated page event stream: for explicitly watched open tabs, a lightweight content script observes DOM mutations/navigation and computes a redacted semantic digest locally (ignoring timestamps, ads, counters, and cursor state). It batches only meaningful candidate changes, encrypts/buffers them while offline, and uploads event evidence when the relay reconnects. The relay de-duplicates events against the durable page-watch baseline, asks a cheap model to rank significance, and sends the pendant an interrupt only for owner-defined urgent changes; otherwise it leaves a cited Mac review item. Include tabId/URL/time and a recovery marker when the tab closes or login expires.
- **owner gets:** Important changes on a logged-in page reach the owner within seconds while the page is open instead of waiting for the next poll, without sending the page's full private contents continuously. It also catches changes that happen during a relay outage and makes clear whether a watch stopped because Safari lost the tab or login.
- effort: Medium-high: Safari extension content-script/event protocol, local redaction and encrypted queue, relay ingestion/deduplication, and Mac/pendant notification plumbing.  ·  risk: DOM-heavy sites can produce noisy or misleading mutations; malformed pages could increase CPU use. Mitigate with mutation coalescing, per-watch rate limits, semantic-digest tests, and explicit paused/error states. Never upload raw DOM by default; owner can opt into a quoted snippet for a specific watch.
- cost: Low ongoing API cost: local digesting and event filtering dominate; relay uses a cheap background model only for candidate significance, with expensive realtime tier reserved for spoken interruption.  ·  latency: Seconds for open-tab changes; offline events arrive on reconnect. Initial watch setup and semantic baseline may take 1–3 seconds.
- security: Adds a new private-data path from Safari to relay, so use per-watch encryption keys, least-content digests, bounded encrypted queue retention, and visible watch indicators. No automatic form submission or outbound message.
- depends on: A functioning Safari extension heartbeat/re-registration and command/result queue; Durable page-watch definitions and baseline/recovery state (chg-e767dfc0); A relay event-ingest route and pendant notification queue

### `browser-harness` — Add a local-query execution mode for authenticated tabs. The relay sends a signed, typed query plan (selectors, predicates, aggregation, and output schema) to Safari; the extension executes it inside the page context, returns only the typed result plus a proof of which selectors and record counts were used, and rejects arbitrary script or undeclared fields. Mac-planner can then join these minimal results with local files/calendar, while the pendant presents the answer and query receipt. Plans are single-use, short-lived, and cached nowhere after completion.
- **owner gets:** The owner can ask for useful answers from logged-in sites—such as totals, deadlines, or whether any item matches a condition—without shipping whole private pages to the server. This is materially safer and more reliable than asking a remote model to inspect every DOM node, while still allowing the Mac and pendant to combine the result into an actionable answer.
- effort: High: define and validate a portable query-plan schema, implement a constrained Safari executor and proof receipt, add relay verification and Mac join support, and handle sites whose DOM changes or requires navigation.  ·  risk: A selector or predicate bug could omit relevant records or expose more than intended; hostile pages could tamper with results. Mitigate with visible plan previews, bounded selectors, no arbitrary JavaScript, result-count/checksum receipts, schema validation, and an explicit 'incomplete/changed page' state. It must stop before any mutation or submission.
- cost: Low per request after implementation: local execution is free, with a small relay validation/model call only when translating natural language into a typed plan.  ·  latency: Typically 1–4 seconds on an open tab; cross-tab joins add a few seconds. It degrades clearly when Safari is offline or the page cannot satisfy the plan.
- security: Reduces raw private-page egress, but introduces a privileged in-page executor. Sign plans, bind them to tab/session/task, encrypt receipts, expire them quickly, and log the exact fields and predicates returned.
- depends on: A reconnecting Safari extension and stable tab/session identity; A signed browser command channel with typed results; Mac-planner support for joins over typed browser results; Pendant/dashboard controls to inspect or stop an active query


## What it asked for

_Nothing._
## Its own summary

Confirmed the browser is currently unusable: /browser/status is offline, only stale home-chrome is registered, there is no tab, and 4 commands are pending. The route table does expose POST /browser/heartbeat (extension-facing), poll, result, and session CRUD, but no attach/list-tabs route. Sent mac-planner this status and the heartbeat correction. Proposed a new event-driven, extension-local authenticated page mutation stream with redaction, encrypted offline buffering, relay significance ranking, and pendant/Mac delivery, plus the corresponding owner capability for immediate logged-in-page change alerts.

**Biggest unknown:** Whether the real Safari extension can reconnect and POST a valid heartbeat, and what exact heartbeat payload/device identity it requires; without that, browser work cannot be exercised or pending commands safely recovered.

