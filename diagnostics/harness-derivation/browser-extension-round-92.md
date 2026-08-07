# Harness derivation — browser-extension — round 92

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser extension availability** — Fresh live status shows Safari is not registered/online right now; only home-chrome is offline and pendingCommands=9. Browser inspections are empty. Authenticated browser actions cannot be verified until Safari reconnects.
  - evidence: GET /browser/status returned online:false with devices=[home-chrome offline, tabCount:null] and pendingCommands:9; GET /browser/inspections returned inspections:[]

## Capabilities it proposed

### "“Check whether this purchase matches across my logged-in store, shipping, and payment pages, and tell me if anything is wrong. Draft a support message if it is.”"
- **useful because:** No single app can reconcile the owner’s private order, carrier, and payment records. The browser can see all three authenticated sessions, the Mac can normalize identifiers and dates, and the pendant can give a short discrepancy verdict without exposing full receipts aloud. It catches duplicate charges, wrong amounts, stalled delivery, and mismatched addresses while stopping before any message is sent.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model for field extraction, normalization, and matching; use the realtime tier only for the owner’s spoken question and final concise explanation. Escalate to the planner model only when portals disagree or selectors change.
- **latency:** About 30–60 seconds for three authenticated pages; under 2 seconds for a follow-up spoken explanation from the stored evidence capsule.
- **cost:** Roughly $0.01–$0.05 per check, dominated by page extraction and one reconciliation pass; no expensive realtime generation during the background check.
- **security:** Data stays in the authenticated browser and local Mac where possible; send only normalized fields, hashes, and small source snippets to the relay/model. Never read full payment numbers aloud or retain them. Drafting a support message is reversible, but sending it or changing an order requires an explicit owner command; show exact recipient/body before that step.
- **missing:** A durable multi-origin browser work item that binds three tabs/sessions and records source citations for each normalized field; A cross-page reconciliation schema for order ID, amount, currency, tax, fulfillment state, delivery estimate, and payment status; A private evidence capsule that the pendant can summarize without replaying sensitive page content; A browser reconnect/lease mechanism so the comparison can resume safely when Safari goes offline

### "“Warn me through the pendant if a page I open looks like a fake login or payment page, and tell me the safe official site to use instead.”"
- **useful because:** The browser is the only surface that can see the owner’s existing session, page origin, redirects, certificate-facing metadata, and rendered login/payment form. A Mac-local detector can catch lookalike domains, suspicious redirects, injected fields, and brand mismatches before credentials or card data are entered; the relay can interrupt the pendant even when the owner is away from the Mac. Today the owner has no cross-surface warning that combines the actual page with an immediate spoken alternative.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** Run a small local/cheap classifier first using URL, origin, redirect chain, DOM labels, and visual branding. Use the expensive realtime model only if signals conflict and the owner asks a spoken follow-up; never upload passwords, form values, cookies, or page screenshots by default.
- **latency:** Under 500 ms for deterministic domain/redirect checks and under 3 seconds for local visual/DOM analysis; the pendant warning should arrive before the owner submits or types into a newly detected credential form.
- **cost:** Near-zero for allowlists, URL reputation, and local heuristics; roughly $0.001–$0.01 for an ambiguous local-model classification. Realtime cost occurs only on explicit follow-up.
- **security:** This must be detection-only: no automatic credential handling, form submission, or navigation to a replacement site. Keep sensitive page data on the Mac; transmit only risk category, domain, confidence, and a safe destination candidate. False positives must be dismissible, and the detector must never claim a page is safe—only that it found no known warning signs.
- **missing:** A browser-extension event stream for navigation, redirect, form-focus, and submit-intent events rather than command polling alone; A signed, locally cached registry of the owner’s known official domains and preferred recovery links; A Mac-local URL/DOM/visual phishing detector with explainable signals and a strict no-secret-data input contract; A low-latency relay interrupt that can deliver a security warning to the pendant and accept “dismiss” or “read reasons”; A browser-side pre-submit observation hook that can warn without blocking or requiring a confirmation gate


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-safe command lease and recovery protocol for the authenticated browser bridge. Every queued browser command gets an expiry/lease state and an explicit retry policy; when /browser/status reports the extension offline, stop dispatching and collapse duplicate stale reads, while preserving one resumable job checkpoint. On reconnect via GET /browser/poll, revalidate tab/session identity before replaying, post typed terminal results to /browser/result/:commandId, and expose orphaned/expired commands plus recovery reason in /browser/inspections. Existing irreversible-action semantics remain unchanged; this is reliability/observability, not a gate.
- **owner gets:** The owner will not hear repeated timeouts or have nine invisible pending commands pile up when Safari sleeps or the extension restarts. A private-page task resumes once the browser returns, without accidentally replaying clicks or typing into a different tab.
- effort: Medium: command-store schema/state machine, poll dispatcher, reconnect tests, and dashboard diagnostics.  ·  risk: A reconnect could replay a stale navigation or reversible action; mitigate by expiring action steps, replaying reads automatically, requiring exact tab/session identity for mutations, and marking uncertain jobs paused for the local planner. Recovery is manual retry from the inspection record.
- cost: Negligible API/storage cost (a few metadata fields per command); no additional model calls unless a paused job needs replanning.  ·  latency: Adds a small status/lease check before dispatch; avoids 45-second waits while offline and reduces duplicate work after reconnect.
- security: Do not persist page contents in the lease record; retain only command type, target/session hash, timestamps, and result reference. Never replay a mutation against a changed tab identity.
- depends on: A working Safari extension heartbeat and the existing GET /browser/status, GET /browser/poll, POST /browser/result/:commandId, and POST /execute browser action path.


## What it asked for

_Nothing._
