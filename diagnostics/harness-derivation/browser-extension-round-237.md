# Harness derivation — browser-extension — round 237

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-tabs** — POST /execute successfully returned a live Safari tab list in the backend history: 5 tabs, including authenticated-looking Adafruit order history, USPS tracking, and DoorDash pages; active tab was USPS tracking. A read of USPS showed delivery to mailbox in Madison on Aug 8, 2026.
  - evidence: POST /execute browser_list_tabs/browser_read_page response at 2026-08-09T00:57:28–00:57:50Z, included in the 01:00:33 probe response.

## Capabilities it proposed

### "“For the order I’m viewing, make me a return packet: identify the item and deadline, draft the exact return message and checklist, and put a reminder on my Mac—but do not submit or send anything.”"
- **useful because:** It converts a private retail/account page into a usable outcome rather than a spoken summary. The owner gets the order facts, a ready-to-review message, and a time-bound reminder while irreversible actions remain visibly unexecuted. No single surface can both read the authenticated order and place the local follow-up.
- **path:** browser → mac-planner → pendant → relay
- **model tier:** Background model for structured extraction and draft generation; realtime only to announce the packet and ask whether to open it for review.
- **latency:** 10–20 seconds; browser read and local reminder creation are the critical path.
- **cost:** One low-cost extraction/drafting call plus one Mac action; browser latency dominates, with negligible storage if only claims and draft metadata are retained.
- **security:** Constrain the browser phase to read-only actions and redact account/payment identifiers. Draft is clearly labeled unsent; never click submit, purchase, or send. Persist only the bounded order claims and provenance under existing browser TTL limits; the draft can remain local on the Mac until the owner reviews it.
- **missing:** A structured browser extractor that returns order/item/deadline fields with provenance rather than a lossy page blob.; A local draft surface (note or file) that the owner can inspect and edit before any send.; A routine that can schedule deadline reminders from an authenticated-page finding without storing page text.

### "“Check the private order and carrier pages I already have open, tell me whether their statuses disagree, and alert me only if there’s a real mismatch.”"
- **useful because:** Retailer and carrier systems often disagree about shipment, delivery, cancellation, or refund state. A single authenticated browser surface can inspect both sessions, while the relay can normalize states and the pendant can alert without requiring the owner to remember to check. This is a cross-origin consistency check, not another page summary.
- **path:** browser → relay → pendant → mac-planner
- **model tier:** Cheap background classifier for field normalization and contradiction detection; realtime only when the owner asks for an explanation of a flagged mismatch.
- **latency:** Initial comparison under 20 seconds; subsequent checks can run on a schedule or page-change trigger and alert within a few minutes.
- **cost:** Small extraction/classification call per changed page, with most cost in browser polling; no need to resend unchanged content.
- **security:** Read-only pages and no interaction with checkout/support controls. Store only normalized status claims, timestamps, host, and provenance—not page bodies, addresses, or payment data. Alerts should say what differs and link the owner back to the originating tab, not speak sensitive detail by default.
- **missing:** A multi-origin browser watch that can bind two existing tabs to one comparison job.; A canonical order-status schema (ordered/shipped/delivered/refunded/exception) with confidence and timestamp handling.; A deduping alert policy and offline delivery through the already-accepted offline_alert_inbox.

### "“Take the two or three facts I name from this logged-in page and save them as a dated note on my Mac, with the source URL, but don’t save anything else from the page.”"
- **useful because:** The owner can turn a private web page into a small durable record without copying an entire page into cloud memory—for example, a tracking number, a warranty expiration, or a reference number. The browser supplies authenticated facts, the Mac supplies local durable storage, and the pendant makes the request hands-free.
- **path:** pendant → browser → mac-planner → relay
- **model tier:** Low-cost structured extraction; realtime is unnecessary except for a brief confirmation of the fields saved.
- **latency:** Under 10 seconds for extraction and local note creation.
- **cost:** One small extraction call and one local file/note action; bounded fields keep context and storage costs low.
- **security:** The owner explicitly names fields; reject or clarify any unbounded request such as “save the page.” Show the exact values and destination before writing if ambiguous. Keep the source URL and timestamp as provenance, but do not upload page text, screenshots, account IDs, or unrelated fields. The local note should be reversible and deletable.
- **missing:** A field-targeted browser extraction action with an explicit output schema and maximum field count.; A Mac note/file writer with an atomic create-and-receipt operation.; A compact pendant confirmation that reads back only the selected fields, not the page.

### "“If I start a complicated form in Safari and have to leave, preserve exactly where I was and what I entered, then let me resume it later from the pendant or Mac without losing the page state.”"
- **useful because:** Today an authenticated browser task is tied to a live tab and is easy to lose when Safari reloads, the Mac sleeps, or the owner changes devices. A resumable private workflow would make the browser a dependable extension of the pendant rather than a one-shot reader: the owner could pause an insurance claim, travel form, support case, or application and return to the same point later.
- **path:** browser → mac-planner → pendant → relay
- **model tier:** Background/local logic should capture and restore deterministic browser state; use realtime only for a short spoken status or for resolving an ambiguous field when resuming.
- **latency:** Checkpoint under 2 seconds after an explicit pause; restore under 10 seconds, with a clear report of anything that could not be reconstructed.
- **cost:** Low model cost when fields and DOM selectors are captured structurally; browser extension storage and local encrypted state dominate. No repeated page summarization is needed.
- **security:** Persist only an encrypted, owner-triggered checkpoint: origin, tab identity, safe field names, entered values, scroll/step position, and expiry. Never persist passwords, payment CVV, session cookies, screenshots, or raw page bodies. Restoration must detect origin and form-version changes and show a diff before writing fields; never silently submit.
- **missing:** An extension-side checkpoint/restore protocol for DOM fields, selectors, scroll position, and multi-step form state.; Encrypted local checkpoint storage and expiry/garbage collection on the Mac, with no cloud page-content copy.; A browser action that can restore a checkpoint transactionally and return a field-level diff when restoration is partial.; A pendant command and spoken status for listing, pausing, and resuming checkpoints.


## What it asked for

_Nothing._
