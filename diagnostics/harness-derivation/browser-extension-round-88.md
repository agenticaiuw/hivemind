# Harness derivation — browser-extension — round 88

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser extension live availability** — As of this round browser status is offline with only home-chrome registered (no tab/user agent), 7 pending commands; prior Safari registration is absent from the live status. Three persisted sessions point at stale tabs from 06:26 or earlier, so no authenticated page can currently be read.
  - evidence: GET /browser/status returned online:false, devices=[home-chrome tabId:null tabCount:null], pendingCommands:7; GET /browser/sessions returned stale default/probe-form/probe-form2 sessions.

## Capabilities it proposed

### "“Resume the form I was working on in Safari, fill the remaining fields from what I tell you, and show me exactly what’s filled before I submit.”"
- **useful because:** This combines the pendant’s hands-free dictation, the relay’s durable state, and Safari’s existing authenticated session. A dropped connection or tab restart would no longer lose a half-completed application. The browser can read the real form labels and current values, while the pendant owner gets a concise field-by-field review; submission remains an explicit separate action.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Use realtime only to transcribe short dictated field values and ask clarifying questions; use a cheaper background model to map the transcript to extracted form labels, detect missing/ambiguous values, and produce the review diff.
- **latency:** Acknowledge dictation in under 1 second; extract/fill and return a field diff within 5–10 seconds. If the browser link drops, persist the draft and resume when it reconnects rather than retrying mutations blindly.
- **cost:** Roughly $0.01–$0.05 per form session depending on dictated audio and background extraction; browser and relay operations dominate latency, not inference.
- **security:** Draft values may include PII and must be encrypted at rest in the relay, scoped to the owner/session, and deleted on request. Read only the active form’s labels/values, redact passwords/payment fields from relay logs, and never submit, send, purchase, or upload without a distinct owner command. Rebinding must verify the same authenticated browser session and current page origin to prevent filling the wrong tab.
- **missing:** A real browser command enqueue implementation (the currently granted enqueue wrappers still return implementation errors); Extension reconnect handshake that leases a live tab and invalidates the seven stale queued commands; Form schema extraction with stable field identifiers and a durable, encrypted draft store; Field-level redacted receipts and a pendant review interaction before any submit action

### "“Compare the invoices in my vendor portal with the reimbursements in my company portal and tell me which ones don’t match.”"
- **useful because:** This would turn two separate authenticated browser sessions into a private reconciliation only this hive can perform. The browser holds the owner’s logged-in access, the Mac can normalize and compare records locally, the relay can retain a resumable job while the owner is away, and the pendant can report only the exceptions. It avoids uploading private financial records to a generic web service and does not mutate either portal.
- **path:** pendant → relay → browser → mac-planner → faculty-perception → faculty-judgement
- **model tier:** Use a cheaper background model for table extraction, normalization, duplicate detection, and confidence scoring. Use realtime only for the owner’s follow-up questions or clarification of an ambiguous record.
- **latency:** Initial portal reads and comparison within 30–90 seconds for ordinary pages; speak an interim status within 2 seconds and continue asynchronously if either portal is slow. The owner should be able to ask for the exception list while the full comparison continues.
- **cost:** Approximately $0.03–$0.20 per reconciliation, dominated by authenticated page extraction and model context for tables; cache page fingerprints and normalized rows to avoid resending unchanged records.
- **security:** Keep raw portal content on the Mac where possible; send only normalized rows, hashes, and exceptions to the relay. Bind each read to the active browser session and expected origin, redact account numbers and tokens from logs, encrypt retained artifacts with a short TTL, and expose citations back to the exact portal page/row. This is read-only by default; creating a dispute or sending a message must be a separate, explicit operation.
- **missing:** A cross-session extraction contract that turns authenticated pages into typed records with row-level citations; Local normalization and matching workers that can compare records from different portal schemas; A durable reconciliation job with partial results, confidence scores, and retry-after-reconnect behavior; Pendant speech/UI for an exception list with drill-down to the cited browser page


## Changes it proposed to its own stack

### `browser-harness` — Implement a resumable Form Draft transaction on top of the existing browser command/result bridge: snapshot the active tab’s same-origin form controls into a schema (stable DOM/accessibility IDs, labels, types, current values), accept a versioned set of proposed values, apply only those values, and emit a redacted field-level receipt. Persist the draft encrypted and bind it to extensionId + tab/session + origin + schema hash; on reconnect, require a fresh snapshot and rebase rather than replaying stale commands. Exclude password, payment, file-upload, and hidden controls by default.
- **owner gets:** The owner can dictate a form over several minutes, lose Wi‑Fi or close Safari, and continue without guessing which fields were changed. They see exactly what is populated and can correct it before submitting, while sensitive fields are not silently copied or logged.
- effort: Medium: extension command handlers and DOM extraction, local-agent schema/rebase logic, relay draft persistence and a small pendant review state machine; approximately 1–2 engineering weeks including reconnect tests.  ·  risk: DOMs can change or labels can be ambiguous; schema-hash and same-origin checks should stop unsafe replays. If extraction fails, leave the page untouched and retain only the draft text. Recovery is discard draft or take a new snapshot; never auto-submit.
- cost: No meaningful extra model cost for extraction; small relay D1/storage and encryption overhead. Background model cost only for ambiguous label/value mapping.  ·  latency: Initial snapshot and apply should add about 1–3 seconds; reconnect adds a fresh snapshot round trip. Dictation remains low-latency because it is separate.
- security: Redact PII from receipts and logs, encrypt drafts, short TTL plus owner deletion, origin/session binding, and explicit exclusion of credentials/payment/uploads. This is a safety boundary around data handling, not an approval gate for ordinary reversible filling.
- depends on: A functioning browser command enqueue path (the currently granted wrappers are still implementation stubs); Extension reconnect/tab lease and stale-command cleanup; A relay-backed encrypted draft store; A pendant review action that can show or speak the field diff


## What it asked for

_Nothing._
