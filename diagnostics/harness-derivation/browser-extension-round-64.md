# Harness derivation — browser-extension — round 64

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension** — Existing browser primitives are individually present (/execute, browser poll/result, /jobs, receipts, research), but there is no durable private-task state contract connecting them. A pause/resume bundle needs encrypted Mac-local state plus opaque relay handle and typed DOM fingerprint/field conflict results.
  - evidence: describe cap-bff5f829 and chg-16bc5dee: authenticated reads/origin fan-out and routing exist, but durable job runner/result stream and account/draft stores remain missing; proposed capability/change recorded this round.

## Capabilities it proposed

### "“Pause this browser task and let me resume it later—even if I close Safari.”"
- **useful because:** Authenticated web work is often interrupted by meetings, sleep, or a dropped Mac link. The browser can capture the private page and staged edits that only Safari can see; the Mac can keep a local encrypted task bundle; the relay can remember a resumable task handle while the pendant lets the owner pause/resume by voice. On resume it restores the URL/tab, verifies the page fingerprint, re-fills only the reversible staged fields, and presents the exact pending action instead of losing work or submitting anything.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime tier only for the short pause/resume voice exchange; use a cheaper background model to normalize page state, redact secrets, compare fingerprints, and generate the resume summary.
- **latency:** Pause acknowledgement under 2 seconds after the browser result; local capture 1–3 seconds. Resume summary under 5 seconds, with browser restoration/re-fill allowed up to 30 seconds and a durable queued result if Safari is offline.
- **cost:** About $0.002–$0.02 per pause/resume, dominated by background page-state extraction and any spoken realtime turn; storage and relay requests are negligible.
- **security:** Page text, URLs, and staged form values may contain private data. Keep the full bundle encrypted on the Mac, store only an opaque task id plus expiry/status on the relay, and never send passwords, cookies, or payment secrets to the model. Resume must stop before irreversible submit/send/purchase and show before/after values and the target URL. Expire and delete bundles on request.
- **missing:** A durable browser-task bundle schema and encrypted Mac storage, distinct from transient command receipts; A browser capture operation that returns tab URL/title, DOM fingerprint, staged editable fields, and evidence anchors; A resume executor that reattaches or navigates Safari, checks the fingerprint, and replays reversible edits with typed results; Relay task-handle persistence, expiry, reconnect notifications, and pendant pause/resume intents; A dashboard view showing captured state, stale-field conflicts, and the exact next irreversible action

### "“Before I submit this, verify that the customer, account, amount, and destination agree across all the logged-in sites involved, and tell me exactly what doesn’t match.”"
- **useful because:** Today the owner can read private pages or fill a form, but cannot reliably reconcile identities and transaction facts spread across separate authenticated systems. This would catch wrong-account, stale-amount, and mismatched-destination errors before they become irreversible, using evidence from the browser sessions the other surfaces cannot reach.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheaper background model for entity linking, field normalization, and contradiction detection; use realtime only to answer the owner's short spoken question and summarize the resulting evidence.
- **latency:** Collect and reconcile three to six authenticated pages in 10–30 seconds. Speak a concise result as soon as the first complete comparison is ready, while the dashboard retains the full evidence matrix.
- **cost:** Approximately $0.01–$0.08 per verification, dominated by extracting and normalizing several private pages; browser and Mac execution costs are negligible.
- **security:** Private business and financial data must remain on the Mac or in encrypted, short-lived relay job state. Send the model only the selected fields and provenance needed for comparison; redact credentials, tokens, unrelated page text, and payment secrets. Never alter or submit a page as part of verification. Expire evidence and provide deletion controls.
- **missing:** A declarative verification schema describing entities and fields to compare across named origins, with required/optional fields and normalization rules; Cross-origin entity resolution that links customer/account/order identifiers without silently guessing; A contradiction and freshness engine that distinguishes missing, stale, and genuinely conflicting values; Typed evidence packets with URL, tab/session identity, timestamp, locator, and source snippet for every compared field; A dashboard matrix and pendant-friendly result format showing pass, mismatch, or unable-to-verify per field


## Changes it proposed to its own stack

### `browser-harness` — Add a resumable private-task contract spanning Safari and the Mac: POST /browser/tasks/capture stores an encrypted local bundle keyed by taskId (tab/session binding, URL/title, DOM fingerprint, cited evidence, and only explicitly staged editable fields); POST /browser/tasks/:taskId/resume enqueues navigate/read/typed re-fill actions through the existing browser bridge, compares the current fingerprint, returns field-level stale/conflict records, and stops at the irreversible next step. Relay stores only taskId, expiry, status, and notification metadata; pendant intents pause/resume/list tasks. Emit journal/action-receipt events and expose a dashboard review card.
- **owner gets:** They can say “pause this” during a private web task and reliably pick it up hours later without losing careful form work or accidentally sending stale information. The owner gets a spoken reminder and an exact reviewable next step, while private content remains on the Mac.
- effort: Medium-high: schema and encrypted local persistence, bridge capture/resume handlers, DOM fingerprint/field normalization, relay metadata and reconnect notification, pendant intent wiring, and dashboard card; approximately 1–2 weeks including Safari failure and stale-page tests.  ·  risk: A page can change or expire its session, and replaying a field against the wrong control could corrupt a draft. Require locator plus label/name/value checks, record before/after values, skip conflicted fields rather than guessing, and allow deletion/expiry recovery. Never replay submit/send/payment actions.
- cost: Minimal relay/D1 metadata and local disk; one background extraction call per capture/resume, roughly $0.002–$0.02 depending on page size. No continuous browser polling beyond existing heartbeats.  ·  latency: Capture adds about 1–3 seconds; resume generally 5–30 seconds depending on Safari availability and page load. If offline, queue and notify when the extension returns.
- security: Improves security by keeping full private state encrypted on the Mac and only an opaque handle in the relay; must implement keychain-backed encryption, redaction of password/payment inputs, TTL deletion, and audit receipts.
- depends on: Durable browser job runner and result stream (chg-16bc5dee); Browser command idempotency/tab-session affinity (chg-14accc01, receipt half chg-5fc73ce3); A Mac keychain/encrypted-bundle primitive; Pendant intent routing for pause/resume; Dashboard task review UI


## What it asked for

_Nothing._
