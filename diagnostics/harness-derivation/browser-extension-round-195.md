# Harness derivation — browser-extension — round 195

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on this authenticated website task even if Safari reloads or my Mac briefly disconnects; tell me on the pendant exactly where you are, and resume only from a verified checkpoint rather than repeating or guessing."
- **useful because:** Long web workflows currently die at the least visible failure: a reload, expired page, or lost bridge can leave the owner unsure whether anything happened. A semantic checkpoint (origin, tab identity, step, extracted state, and last reversible action) lets the browser, relay, Mac, and pendant continue safely and makes the system's unique reach dependable rather than a one-shot demo.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Use the realtime model only for the owner's spoken checkpoint/resume decision; use a cheaper background model to normalize page state and compare checkpoints. Browser execution remains deterministic actions, not model improvisation.
- **latency:** Read/checkpoint under 2 seconds; recovery status under 5 seconds; no more than 30 seconds for a replan after reconnect.
- **cost:** Usually <$0.01 per checkpoint/recovery using a small background model; the dominant cost is page reads and any realtime spoken interruption, not storage.
- **security:** Bind every checkpoint to origin, tabId/windowId, URL pattern, and a content hash; invalidate it on identity or sensitive-field changes. Persist claims and hashes, never HTML/page text. Stop before irreversible submit/send/purchase and present the exact pending action on the pendant. The owner still needs to supply an explicit per-origin configuration; ship it empty.
- **missing:** browser checkpoint/resume state machine with verified page identity; reconnect-aware job runner that can replay only idempotent steps; pendant status event carrying workflowId and checkpoint summary; owner-supplied per-origin read/extract/redact/never-store rules

### "Read the form I have open, ask me the missing questions through the pendant one at a time, fill the answers into Safari, and give me a spoken preview of every field before I submit."
- **useful because:** Authenticated forms are where browser access becomes materially useful: the browser can see the real form and the pendant can collect answers while the owner's hands are busy. Field-level provenance and a final spoken diff prevent silent mis-entry, while the owner retains the irreversible submit decision.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** A cheaper text model maps labels and validates formats; realtime handles the short conversational question/answer loop only. Deterministic browser actions fill fields; do not use vision/realtime for routine typing.
- **latency:** Ask each next question within 1 second after an answer; parse and fill within 2 seconds; final preview within 5 seconds.
- **cost:** Roughly $0.02–$0.10 per form depending on number of fields and spoken turns; realtime audio turns dominate, while DOM extraction and deterministic fills are cheap.
- **security:** Treat values as ephemeral: redact secrets and never persist page text or raw answers beyond the active job unless the owner explicitly saves them. Show origin, field label, proposed value, and any ambiguity on the pendant/dashboard. Never submit, upload, send, or purchase automatically. Require explicit owner confirmation at the final preview (this is a final action confirmation, not a blanket gate). Empty per-origin rules remain the default until the owner configures them.
- **missing:** form-schema extraction that preserves field labels and ordering; field-value ephemeral vault with redaction and expiry; spoken field-by-field preview event on the pendant; browser fill action with undo snapshot and submit boundary detection; owner-provided origin and retention configuration

### "Compare the authenticated receipt or order page in Safari with the matching email or calendar entry on my Mac, and tell me on the pendant only if the amount, date, recipient, or status disagree."
- **useful because:** No single surface can establish whether a transaction is consistent: Safari has the logged-in source of truth, while Mail/Calendar contain the independent copy. A cross-surface reconciliation catches wrong charges, stale appointments, and delivery/status mismatches without making the owner manually copy sensitive details between apps.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Use deterministic extraction and normalization first; a small background model resolves labels and dates. Use realtime only to speak a compact discrepancy or ask one ambiguity question.
- **latency:** One reconciliation in under 10 seconds; background watch jobs can run on a slow schedule and only wake the pendant on a material mismatch.
- **cost:** About $0.01–$0.05 per reconciliation; model comparison is the dominant cost, with browser/Mail reads local. Persistent watching should use a cheap scheduled worker, not realtime.
- **security:** Keep raw receipt/email content on the Mac; send the relay only normalized claims (amount/date/status/recipient), with provenance and short TTL. Never speak full account numbers, addresses, or message bodies. Require explicit owner-configured origins and categories; configuration ships empty. Treat mismatches as warnings, not proof of fraud, and include links/evidence for inspection.
- **missing:** shared claim schema for browser and Mail/Calendar observations; local-only extraction adapters for Safari page and Mail/Calendar; entity matching with uncertainty and duplicate handling; materiality rules and pendant alert payload; owner-supplied origin/category speaking and retention configuration

### "Check the security and activity pages of the authenticated accounts I choose, correlate new-login, password-change, recovery, and payment alerts across them, and tell me on the pendant immediately when several signals point to a possible account takeover."
- **useful because:** Today each service exposes isolated warnings and the owner must notice them separately. A cross-account correlation layer could identify a coherent attack pattern—such as a new login followed by recovery-email and payment changes—before any one site labels it fraud. The browser is uniquely able to reach the authenticated security pages, while the relay and pendant can deliver an urgent alert even when the Mac is unattended.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Use deterministic extraction and local rule correlation for known security-event fields; use a small background model only to normalize unfamiliar page labels. Reserve realtime for the urgent spoken alert and the owner's follow-up questions.
- **latency:** Poll or react to configured security pages within 1–5 minutes; correlate and alert within 10 seconds of receiving a new event. A follow-up explanation should take under 3 seconds.
- **cost:** Approximately $0.01–$0.05 per account sweep using a small model, with most cost from authenticated page reads. Realtime is used only for an actual alert, not for polling.
- **security:** This must be opt-in per origin and account category, with an empty configuration until the owner names accounts. Keep raw security-page content on the Mac; send only normalized event claims, confidence, timestamps, and provenance to the relay. Never persist credentials, recovery codes, payment numbers, or page HTML. Treat correlations as warnings, include the exact source pages, and let the owner inspect before taking any account action. Alerts should survive a disconnected Mac via the existing pendant inbox.
- **missing:** per-origin account/security-page configuration and polling cadence; authenticated browser page-watch scheduler with session-expiry detection; normalized security-event schema across unrelated sites; cross-origin correlation and deduplication engine; urgent alert priority and acknowledgement state shared by relay, dashboard, and pendant; recovery workflow that opens the exact source page without automatically changing account settings


## Changes it proposed to its own stack

### `browser-harness` — Add a user-visible tab lease and identity lock to every browser job. Before each read, click, type, or select, verify extensionId, tabId, windowId, origin, URL pattern, title, and a lightweight content hash; if any changes, pause the job, invalidate stale selectors, and send the owner a pendant/dashboard notice naming the new tab instead of acting there. Expose a one-tap 'use this tab' reassignment for reversible jobs.
- **owner gets:** With multiple Safari tabs and authenticated sessions, the system should never silently read or type into the wrong tab after a redirect, popup, or tab switch. This turns a dangerous ambiguity into a clear, recoverable prompt the owner can resolve without starting over.
- effort: Medium: extend browserBridge/browserSessions and action receipts; add lease renewal and a small Safari-extension identity payload, plus dashboard and pendant status rendering. No new model is needed for the core check.  ·  risk: A legitimate redirect or SPA route change may pause work more often than desired; recovery is explicit reassignment or a fresh read that establishes a new hash. A stale extension heartbeat should fail closed for the active job, never guess.
- cost: Negligible API cost; a few hundred bytes per action and one hash comparison. No hardware cost.  ·  latency: About 10–50 ms locally per action; one extra read only when identity changes.
- security: Meaningfully reduces cross-tab data leakage and wrong-recipient form fills. It does not decide which origins are allowed; the owner's empty-by-default per-origin configuration remains separate.
- depends on: browser extension reports stable tab/window identity and origin metadata; browser job receipts/provenance; owner-supplied per-origin configuration


## What it asked for

_Nothing._
## Its own summary

Recorded a new cross-origin account-takeover early-warning capability: authenticated security-page monitoring, normalized event correlation, and urgent durable pendant alerts. It requires owner-selected origins, a browser scheduler/session-expiry handler, a shared security-event schema, correlation logic, and acknowledgement/recovery UX.

**Biggest unknown:** Which accounts and security categories the owner would explicitly authorize for monitoring and speaking aloud.

