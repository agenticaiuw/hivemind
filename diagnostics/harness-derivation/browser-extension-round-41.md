# Harness derivation — browser-extension — round 41

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Live /browser/status currently reports online=false, only home-chrome with no tab and 3 pending commands; Safari device is absent from current status payload despite prior established notes describing Safari online.
  - evidence: GET /browser/status returned online:false and devices:[home-chrome tabId:null tabCount:null], pendingCommands:3 at 2026-08-07.

## Capabilities it proposed

### "“Pin this page for me.” Later: “What was the deadline and contact from the page I pinned?”"
- **useful because:** The owner can turn a private, logged-in Safari page into a temporary spoken reference without keeping the tab open or trusting a cloud crawler. This is especially useful for travel confirmations, invoices, appointment portals, and work pages that disappear behind login. The answer can include a source link and captured timestamp, while the pendant remains useful when the Mac is closed or the browser session is unavailable.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheap background model on the Mac to normalize the explicitly pinned page/selection into a small field-and-citation capsule; use realtime only to answer the later spoken lookup and read back a concise result. Never send raw page text to the relay unless the owner explicitly asks for cloud access.
- **latency:** Pin acknowledgement under 2 seconds after extraction; field extraction under 10 seconds. Spoken lookup should answer from the local capsule in under 1.5 seconds, falling back to a Mac re-open only when the capsule is expired.
- **cost:** About $0.001–$0.01 per pin for local/background extraction depending on page length; near-zero for later lookups. The dominant cost is model extraction, not storage or voice.
- **security:** Pinning must be an explicit pendant phrase or extension button, never an ambient capture. Store the capsule encrypted on the Mac with a configurable expiry (default 7 days), retain URL/title/selection hash and field-level citations, and redact credentials, tokens, and hidden form values. The relay receives only an opaque capsule id and extracted answer when needed. Asking to share, export, or use the data in a form requires a separate explicit request; do not submit browser forms.
- **missing:** A browser-to-Mac 'private capsule' record and encrypted local store with TTL/deletion; An extension action that extracts the current tab or selected DOM region and returns stable citations; A relay lookup intent that routes capsule queries to the Mac without copying raw page contents into long-lived cloud context; Pendant/UI affordance for pin, list, forget, and expiry feedback; Dashboard controls to inspect, revoke, and delete capsules

### "“Verify that my booking details agree everywhere.”"
- **useful because:** Today the owner can ask for separate page reads, but cannot have the hive reconcile a private browser reservation against local Mail, Calendar, and saved documents as one evidence-backed consistency check. This catches changed times, wrong names, duplicate bookings, or stale confirmations before they cause a real problem, while showing exactly which source disagrees and what follow-up to prepare.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheap background model for parallel extraction and schema normalization; use a stronger model only to resolve ambiguous conflicts. Realtime is used only for the owner's spoken request and concise result.
- **latency:** Collect and normalize three to five sources within 20 seconds; speak a short verdict as soon as the first complete comparison is ready, with a dashboard evidence table arriving shortly after.
- **cost:** Roughly $0.01–$0.05 per verification, dominated by normalization and conflict resolution; browser and local reads are otherwise low-cost.
- **security:** All sources are private. Keep raw browser text and local message contents on the Mac where possible; send the relay only normalized fields, hashes, and source labels. Require explicit source selection or a clear scope, redact payment credentials and unrelated message text, preserve citations, and never alter or cancel a booking. Any draft correction should stop before sending.
- **missing:** A cross-surface verification job that can fan out to authenticated Safari tabs plus Mail/Calendar/files; A shared schema for reservations, appointments, orders, and account records with field-level provenance; Conflict scoring that distinguishes true disagreement from stale or duplicate sources; A dashboard evidence view and pendant result format for verdict, mismatched fields, and suggested next step; A durable job/receipt path for partial results when one private source is offline


## Changes it proposed to its own stack

### `browser-harness` — Add a Private Page Capsule protocol spanning Safari extension and Mac agent: `browser_pin_capsule` captures only the visible page or an explicitly selected region, runs local field extraction, stores an encrypted capsule keyed by random id with TTL, and records URL/title/timestamp plus DOM/source hashes for each field. Add `capsule_lookup`, `capsule_list`, and `capsule_revoke` intents; relay voice requests carry only the id/query, and the Mac returns a cited answer or an explicit expired/deleted result. Include redaction of password/token/input elements and a hard size limit with a clear 'selection only' fallback.
- **owner gets:** The owner gets durable memory for the private pages they deliberately choose, even after Safari closes or loses its login, without turning all browsing into surveillance or uploading sensitive pages to the cloud.
- effort: Medium: extension extraction and citation mapping, encrypted Mac persistence/TTL sweeper, three relay intents, pendant feedback, and dashboard deletion UI; add integration tests for tab loss, expiry, and redaction.  ·  risk: DOM citations can become stale and page extraction may miss visually rendered content. Mitigate with a captured text snippet hash, timestamp, source URL, and honest 'captured at' labeling; if the Mac is unavailable, report that rather than silently using cloud data. Revoke and expiry must delete both capsule body and index.
- cost: Small local storage and one inexpensive extraction call per pin; no recurring browser polling or cloud page-transfer cost. Dashboard and relay query paths add negligible API usage.  ·  latency: Pin may take up to 10 seconds for extraction; lookup is local and typically sub-second, with voice response dominated by speech turn latency.
- security: Improves privacy by keeping raw authenticated content on the Mac and limiting relay payloads to opaque ids. Requires OS keychain-backed encryption, strict redaction, audit receipts, and explicit user initiation.
- depends on: Authenticated Safari command execution and typed browser results; A durable Mac encrypted store with TTL deletion; Relay intent routing that can address the Mac by capsule id; Pendant command/feedback support; Dashboard revoke/delete surface


## What it asked for

_Nothing._
## Its own summary

Discovered a live regression: /browser/status currently has no Safari device, only offline home-chrome and 3 pending commands. I recorded it and notified mac-planner. Proposed a genuinely new cross-surface Private Page Capsule: the owner explicitly pins a private Safari page/selection, local Mac extraction stores an encrypted expiring capsule with field citations, and later pendant voice queries retrieve answers by opaque id without sending raw page content to the relay. Also proposed the browser-harness protocol and redaction/TTL/revocation details.

**Biggest unknown:** Whether Safari is actually disconnected or its heartbeat is being dropped, and whether the current browser command enqueue implementation can be repaired. The capsule feature additionally needs an encrypted Mac store, relay lookup intent, pendant affordances, and dashboard revoke/delete controls.

