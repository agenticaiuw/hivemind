# Harness derivation — browser-extension — round 226

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Compare the statement I’m looking at in Safari with the matching receipt or file on my Mac, and tell me exactly what doesn’t match.”"
- **useful because:** Only the browser extension can read the owner’s authenticated statement while only the Mac can search local receipts/files. The relay can align amounts, dates, vendors, and line items, then the pendant can speak a concise discrepancy list without exposing either full document to a cloud store.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Background model for extraction and deterministic field comparison; realtime tier only for the owner’s follow-up question.
- **latency:** Under 20 seconds for two small documents; up to 60 seconds for a long statement.
- **cost:** About $0.02–$0.10 per comparison, dominated by OCR/long-document extraction; no recurring cost unless requested.
- **security:** The owner chooses the active tab and local file/folder. Use read-only browser actions and read-only Mac file access. Send normalized fields, not source HTML, screenshots, or full documents, and keep capsules short-lived. Never speak full account numbers; redact by default and let the owner configure category speech rules.
- **missing:** a joined browser-plus-local-file comparison job; field normalization and deterministic tolerance rules for money/date/vendor values; a user-selected local file picker/search action exposed to mac-planner; redacted discrepancy receipts with source URLs and local paths

### "“Turn the important rows on this logged-in dashboard into reminders, preserving the source link and deleting them automatically when they expire.”"
- **useful because:** This bridges a private web session to a durable, actionable Mac workflow: the browser extracts only the rows the owner points at, the relay ranks them, and the Mac creates reversible reminders with an expiry and source URL. The pendant can announce only newly created high-priority reminders, rather than reading the whole dashboard.
- **path:** browser → relay → mac-planner → pendant → dashboard
- **model tier:** Cheap background extraction/ranking model with deterministic date parsing; realtime only if the owner asks a question about one row.
- **latency:** 10–25 seconds after the owner selects a page; reminder creation should be visible in under 30 seconds.
- **cost:** Approximately $0.01–$0.04 per page, mostly extraction; Mac reminder creation is local and free.
- **security:** Read-only browser extraction and reversible local reminder creation. Start with an empty origin configuration and require the owner to choose the rows; never infer a site or scrape an entire account. Store only a short claim, URL, expiry, and provenance under existing browser TTL rules. Do not put private row details into reminder titles unless the owner’s category speech/persistence policy allows it.
- **missing:** row-selection/structured extraction from browser pages; mapping of extracted due dates and priorities to reminder fields; expiry/deletion reconciliation job and undo receipt; dashboard preview of fields before local creation

### "“Use the information already on my Mac to fill this logged-in web form, show me the exact values and destination, and wait until I tell you to submit.”"
- **useful because:** This removes tedious, error-prone transcription while preserving the browser’s unique access to authenticated forms. Safari supplies field names and session state; the Mac supplies local calendar/contact/document values; the relay produces a field-by-field preview; the owner can inspect it on the pendant or Mac before the irreversible submit step.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Realtime for interactive field questions and preview; background extraction for deterministic field mapping and redaction.
- **latency:** Initial form inspection under 10 seconds; fill preview under 30 seconds; no background polling.
- **cost:** About $0.02–$0.08 per form depending on fields and local document extraction; browser and Mac operations dominate latency.
- **security:** Do not persist credentials, raw field values, or page bodies. Use named source fields and per-field provenance; mask secrets and sensitive categories in the spoken preview. Browser action allow-set is read plus fill only; submit is a separate explicit action the owner invokes after seeing the exact payload. Preserve an undo/clear receipt for any local drafts.
- **missing:** DOM/accessibility-field extraction with stable field identifiers; a local-value resolver that asks for source and handles ambiguity; field-level preview/redaction sent to dashboard and pendant; a distinct submit action that is never included in the fill batch; rollback/clear for browser-filled-but-not-submitted fields

### "“When Safari is showing something private, keep the contents out of the pendant and any screenshots automatically, but still tell me safely what kind of page it is.”"
- **useful because:** The browser is the only node that knows what authenticated origin and form context are actually on screen, while the pendant is the only surface that can accidentally speak into a room. A live privacy firewall would prevent a browser question, background alert, or screenshot from leaking page contents while preserving a useful generic state such as ‘a payment page is open’ or ‘a verification step needs you’. This is protection the owner cannot get from either Safari or the pendant alone.
- **path:** browser → relay → pendant → mac-planner → dashboard
- **model tier:** Cheap classifier on page metadata/accessibility labels; no generative model for the suppression decision. Realtime model may answer only after the redaction policy has produced a safe capsule.
- **latency:** Suppression must happen locally/in the browser bridge within 100 ms of a page snapshot or navigation; safe status under 2 seconds.
- **cost:** Under $0.01 per inspected page; the main cost is browser-bridge and pendant firmware work, not inference.
- **security:** Default-deny content for unknown origins/categories: emit only coarse page type and a redacted state. Ship the owner’s per-origin and per-category rules empty and inspectable; never invent sites. Do not persist raw HTML, OCR, screenshots, or form values. A deliberate owner request can temporarily reveal a redacted claim, but the policy engine must produce the safe capsule first and log that exception.
- **missing:** browser-bridge sensitive-context classifier using origin, accessibility labels, and field types; a redaction/suppression signal consumed by browser snapshots, relay speech, and pendant playback; safe coarse page-state vocabulary and policy editor in the dashboard; firmware/relay handling that drops queued page-content alerts when the privacy state changes; end-to-end tests proving a password/payment/identity page cannot reach audio or screenshot storage

### "“Answer my question from the private page I’m viewing, quote the exact supporting sentence, and highlight that sentence in Safari so I can verify it.”"
- **useful because:** Today a spoken answer from an authenticated page can be hard to audit. This makes the browser the evidence surface and the pendant the low-friction query surface: the relay returns a short answer plus a bounded quote, while Safari visibly highlights the source passage. It is especially useful for policies, invoices, benefits, and account terms where paraphrase can mislead.
- **path:** pendant → relay → browser → dashboard
- **model tier:** Cheap extraction/ranking for finding candidate passages; realtime model only for the owner’s natural-language question and answer synthesis after passage selection.
- **latency:** Under 8 seconds for a normal page; highlight should appear within 2 seconds after the answer is spoken.
- **cost:** Approximately $0.01–$0.04 per question; browser inspection and passage extraction dominate.
- **security:** Read-only browser actions and no form mutation. Persist only the short claim, URL, timestamp, and bounded quote under existing browser TTL/caps; never store the page. Apply the privacy firewall and category speech rules before sending any quote to audio. If no passage supports the answer, say so rather than guessing.
- **missing:** passage-level browser extraction with stable DOM ranges; a browser highlight/scroll action that is separate from clicking or typing; claim-to-passage evidence capsules in the browser provenance store; voice request correlation from pendant playback to the active Safari tab


## What it asked for

_Nothing._
## Its own summary

Discovered the real Safari extension is online with 2 tabs (active tab is YouTube, tabId 3186198), and /browser/provenance is live, read-only, empty, with a 524 KB budget and no stored records. Three non-duplicate capabilities were recorded: (1) compare an authenticated Safari statement to a local Mac receipt/file and speak only discrepancies (my strongest, most owner-useful proposal); (2) turn selected private-dashboard rows into expiring, undoable Mac reminders; (3) fill a logged-in form from Mac data with a field-level preview and a separate explicit submit step. I notified mac-planner. The authenticated-page change-watch idea collided with an existing backlog item, so I did not restate it.

**Biggest unknown:** I still need a functioning, unambiguous browser read/list command that resolves to browser_list_tabs/browser_read_page (the granted browser_read_or_navigate wrapper is ambiguous and performs nothing). I also still need owner-supplied origins/categories when he is ready, plus the missing field/row extraction and browser-plus-local-file comparison primitives identified in the proposals. I will not inspect the currently visible YouTube tab without an owner task.

