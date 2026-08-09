# Harness derivation — faculty-perception — round 171

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser/relay observability** — At 2026-08-08T03:17:57Z, /ops/snapshot reports the AI Pendant Agent fully ready: Accessibility and Screen Recording granted, all required permissions present, browser extension online with 9 Safari tabs and 0 pending commands, relay reachable with D1 store and Mac bridge online. Device discovery still lists only home-macbook-bridge online and cloudflare-contract-test offline; no pendant registry row. /pipeline contains historical nrf9160 events, so those are not proof of a currently connected pendant.
  - evidence: GET /ops/snapshot HTTP 200 and discover:devices at 2026-08-08T03:18Z

## Capabilities it proposed

### "“When I come back, tell me exactly what changed in the browser while I was away, and show me only the items that need my attention.”"
- **useful because:** The browser is live and authenticated but today its state is scattered across inspection results, command history, and the owner's memory. A bounded before/after change report would turn an unattended browser into a trustworthy continuity surface instead of a tab dump.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception
- **model tier:** Background/cheap model computes normalized DOM and title diffs; realtime only summarizes the small set of material changes when the owner asks.
- **latency:** Capture on browser heartbeat under 1 s; diff in background under 5 s; spoken answer under 2 s once requested.
- **cost:** Usually <$0.01 per diff using local hashing and a cheap text model; realtime summary dominates when spoken.
- **security:** Never persist page bodies by default. Store URL/title/region hashes and redacted snippets; require confirmation before exposing changes from private tabs or executing any follow-up. A tab-close or navigation must invalidate the baseline.
- **missing:** A durable, per-tab baseline and diff store with explicit owner-started 'away window' and expiry; Browser extension event hook for navigation and meaningful DOM mutation, not just heartbeat; A redacted diff artifact joined to the existing browser command/session identifiers

### "“If I walk away or the pendant disappears, freeze anything that could send, buy, delete, or publish; when I return, show me the exact pending actions and let me resume only the ones I approve.”"
- **useful because:** A live Mac bridge and browser session can continue acting after the owner's wearable link is gone. This makes physical presence a safety boundary: loss of the pendant pauses risky work, while the returning owner gets a concise, reviewable queue rather than silent execution or blanket cancellation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic policy engine evaluates presence and action risk; cheap background model groups pending work; realtime is used only to explain the queue and collect approval.
- **latency:** Presence loss detected within 10 s (heartbeat/continuity bound); high-risk action gate under 100 ms; return summary under 3 s.
- **cost:** Negligible for policy and queue; <$0.01 only when a model is used to summarize multiple pending actions.
- **security:** A stale heartbeat must fail closed, but network loss must not create destructive retries. Store only action IDs, target domains/apps, risk class, and hashes of parameters; never retain secrets. Returning presence is not sufficient for irreversible actions—require explicit approval tied to the exact receipt.
- **missing:** A relay-issued presence lease bound to the pendant reality beacon and Mac/browser session; A risk-policy gate in mac_run_actions, browser commands, and relay jobs that pauses before commit; A resumable pending-action view with per-step approval and expiry

### "“I’m on this page—before I type anything, tell me whether it is the real site, what account it is asking for, and what would leave my machine.”"
- **useful because:** The browser extension can see the authenticated tab and the Mac now has Screen Recording and Accessibility, but there is no owner-facing pre-submit security check. A spoken, provenance-backed warning can catch lookalike domains, unexpected uploads, and account switching before a secret is entered.
- **path:** pendant → relay-realtime → browser-extension → mac-vision → mac-planner → faculty-perception → faculty-judgement
- **model tier:** Deterministic URL/origin/form classifier first; cheap vision/text model compares page structure and destination; realtime speaks only the verdict and asks for confirmation if risk is nonzero.
- **latency:** Under 1.5 s from button press for URL/form analysis; under 4 s if a screenshot comparison is needed.
- **cost:** <$0.01 per check using local URL/form rules; <$0.03 for an optional vision comparison. No cloud upload for low-risk checks.
- **security:** Never transmit field values, cookies, passwords, or page secrets. Redact input values locally and send only origin, labels, destinations, and a screenshot crop if the owner explicitly permits it. Verdict must say unknown when the site cannot be independently established; it must never claim safety from TLS alone.
- **missing:** A local pre-submit interception hook in the browser extension that can pause navigation/form submission; A signed allowlist/reputation feed and origin-change history, joined to the current tab identity; A redacted, expiring security-evidence record so the spoken warning can be audited without retaining secrets

### "“Before you do it, tell me exactly which of my data will leave this Mac, which service will receive it, how long each copy will remain, and give me one switch to allow only this transfer.”"
- **useful because:** Today the owner can approve an action, but cannot see the complete data path when a browser page, Mac agent, relay, model, and wearable are involved. A live data-flow receipt would make privacy legible at the moment it matters, rather than relying on vague trust in a tool or prompt.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic taint and routing analysis creates the receipt; a cheap model summarizes it. Realtime is used only for the owner's spoken question and one-time consent.
- **latency:** Static preview under 300 ms for known actions; under 2 s when a page must be inspected; consent prompt must block the commit until the receipt is ready.
- **cost:** Near-zero for local taint tracking; under $0.01 for summarizing a complex receipt. Storage is bounded metadata, not copied content.
- **security:** The ledger itself can reveal sensitive URLs and data classes, so encrypt it locally, redact values, and expire receipts. A missing or ambiguous data-flow edge must produce UNKNOWN and block high-risk transfers, never silently downgrade to safe.
- **missing:** A common taint vocabulary and per-field data-flow events shared by browser, Mac, relay, model, and pendant; Pre-commit interception points that can hold browser uploads, Mac tool calls, relay requests, and audio forwarding; An encrypted, expiring transfer receipt with a one-transfer capability token and an owner-readable revoke/abort operation

### "“For this decision, show me the small set of facts you are relying on, where each came from, and let me correct one fact without restarting the task.”"
- **useful because:** The owner cannot currently inspect or amend the live context that connects a browser page, Mac files, relay conversation, and planned action. A fact-level challenge surface would prevent stale or misidentified context from silently steering a long workflow.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement
- **model tier:** Deterministic context extraction and source linking first; a cheap model compresses the evidence into a spoken/card-sized explanation; realtime handles the short correction dialogue.
- **latency:** Initial fact ledger under 1 s for existing records; correction propagated to dependent planning within 2 s; no action may commit while a depended-on fact is unresolved.
- **cost:** <$0.01 per fact ledger using local graph operations; model cost only for compression or ambiguous natural-language correction.
- **security:** Expose claims, not raw secrets; redact private values and separate asserted owner facts from observed evidence. Corrections need versioning and scope so one temporary correction cannot rewrite durable memory accidentally.
- **missing:** A versioned claim ledger joining context-graph entities, browser evidence capsules, pipeline jobs, and relay turns; Dependency edges from each planned action to the claims it used; A correction protocol that invalidates or replans affected actions without mutating source evidence


## Changes it proposed to its own stack

### `context` — Repair the granted read_continuity_snapshot resolution so it calls the authenticated GET /ops/snapshot plus GET /pipeline (and relay job state) as one bounded read-only operation. The current grant exists in the manifest but resolves to nothing; the nearest live route is /ops/snapshot with score 0.447, so perception cannot use its intended single-call contract.
- **owner gets:** When the owner asks “what happened while I was away?”, the system must answer from one coherent, freshness-bounded view instead of silently failing or mixing stale pipeline history with live status.
- effort: Small resolver/manifest correction plus a contract test against the already-live routes; medium if relay and browser event joins are added.  ·  risk: A bad join could overstate success. Keep source timestamps, explicit unknowns, and bounded maxItems; recover by falling back to the raw routes and label the result partial.
- cost: Negligible API cost; one local authenticated read instead of several model-mediated probes.  ·  latency: Adds one bounded snapshot read, typically under 500 ms locally plus relay timeout.
- security: Read-only bearer-authenticated data; preserve existing redaction and do not expose page bodies or secrets.
- depends on: The already-granted read_continuity_snapshot schema; GET /ops/snapshot; GET /pipeline; relay job status route; A resolver mapping that recognizes the granted tool rather than scoring it against its own route inventory

### `interaction` — Add a cross-surface interruption arbitration layer that converts system urgency into a negotiated modality plan: wearable haptic pulse when the owner is moving, a short spoken cue when stationary, Mac banner when the owner is in a meeting, and browser-local notice when the relevant tab is focused. It must log why that modality was selected and expose a single “why did you interrupt me?” explanation.
- **owner gets:** The owner gets important information at the least disruptive place and can understand or correct the decision; today each surface can speak or display independently, so the same event can be missed, duplicated, or arrive at the worst moment.
- effort: Large: requires presence/activity signals, a shared urgency model, modality leases across relay/Mac/browser/pendant, and firmware haptic control. It should be designed before implementation rather than constrained to today’s disconnected pendant state.  ·  risk: A wrong urgency classification can suppress something important or create interruption spam. Use fail-open for safety-critical events, expiry on all leases, duplicate suppression by event ID, and a visible audit trail; fall back to Mac notification if wearable state is unknown.
- cost: Minimal runtime cost; occasional cheap classification. Hardware firmware changes may require a small haptic driver and roughly tens of KB flash/RAM, with negligible average power if pulses are rare.  ·  latency: Urgency/modality selection under 100 ms locally; relay fallback under 1 s. Haptics should not wait on a model.
- security: Presence and activity signals stay local by default; only urgency class and opaque event ID leave the Mac. Do not transmit page contents or meeting titles.
- depends on: A shared event identity and urgency schema across relay, Mac, browser, and pendant; A pendant haptic actuator/driver or equivalent physical feedback path; Owner-configurable safety-critical categories and meeting/privacy detection; Per-surface acknowledgement and deduplication semantics that distinguish delivered from actually perceived


## What it asked for

_Nothing._
## Its own summary

Fresh discovery: GET /ops/snapshot is live and reports the exact AI Pendant Agent as fully ready—Accessibility and Screen Recording granted, all required permissions present, browser extension online with 9 Safari tabs, 0 pending commands, relay reachable on D1, and Mac bridge online. Device discovery still shows no registered pendant; only home-macbook-bridge is online, so nRF9160 pipeline rows remain historical rather than proof of current wearable presence. The newly granted read_continuity_snapshot tool is not actually callable: resolution fails against the live inventory (nearest routes /ops/snapshot and /pipeline). I recorded this reality fence. I also produced three non-duplicate owner capabilities: presence-loss fail-closed action freezing with explicit resume, pre-submit phishing/data-exfiltration checks for browser forms, and a bounded browser-change report (the recorder flagged that last one as close to an existing backlog item, so it should not be repeated).

**Biggest unknown:** There is still no authoritative, callable single snapshot that joins live pendant presence, relay delivery, Mac/browser state, and owner-heard playback. In particular, no pendant is registered or emitting current device telemetry, and the granted snapshot resolver must be repaired before this facet can answer continuity questions without stitching raw routes.

