# Harness derivation — mac-planner — round 222

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser availability round 222** — Mac bridge, relay, browser extension, Accessibility, Screen Recording, and all listed automation grants are live/ready. Safari has 2 tabs; active authenticated DoorDash order is preparing, on time, ETA 6:19–6:41 PM, step 2/4 and seeking Dasher. Existing browser reads already produce provenance capsules and receipts.
  - evidence: GET /ops/status, GET /browser/status, GET /jobs

## Capabilities it proposed

### "“Watch my authenticated DoorDash order and tell me through the pendant only when the status materially changes—driver assigned, pickup, nearby, delivered, or a problem.”"
- **useful because:** The owner should not repeatedly open a private Safari tab or miss a delivery while working. The browser extension can see the authenticated order that the relay cannot access, while the relay can summarize and the pendant can interrupt briefly; this is a real four-surface capability available now, not a generic web notification.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Use a cheap background classifier/scheduler for polling and transition detection; use realtime only to turn a detected transition into a short spoken alert. No page body should be sent to the model unless the status changed.
- **latency:** Poll every 60–90 seconds while an order is active; alert within one polling interval. A transition-to-speech response should start in under 2 seconds.
- **cost:** Low: roughly 1–2 small classification calls per status transition, with most polls handled by deterministic DOM/status extraction. Audio delivery dominates only when an alert is emitted.
- **security:** The browser session is private and must remain on the Mac/extension; send only a normalized status, ETA window, and redacted error code to relay. Never transmit address, payment details, or full page text. Require an explicit per-site watch start and automatic expiry after delivery.
- **missing:** A browser watcher that persists a normalized selector/schema and last-seen state instead of one-shot browser commands; A relay-side watcher schedule and deduplication keyed by order/session; A pendant alert payload carrying urgency and expiry, reusing the existing offline alert inbox

### "“Save what I’m looking at as a useful note.”"
- **useful because:** A spoken request from the pendant should turn the authenticated Safari page the owner is currently viewing into a durable, local, searchable artifact without copy/paste. The browser is the only node that can read the private page; the Mac is the only node that can place a file in the owner’s workspace; the relay supplies naming, extraction, and a compact confirmation.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Use a cheap extraction model on the relay only after the browser returns the current page title, URL, selection/reader text, and page metadata. Use realtime for the one-sentence confirmation; deterministic Mac actions create the file.
- **latency:** Capture the active page in 2 seconds, produce the note in under 8 seconds, and speak confirmation as soon as the atomic file write succeeds.
- **cost:** One small extraction call per save, typically under a few cents; browser extraction and local file creation dominate latency, not tokens.
- **security:** Keep authenticated cookies and raw page access on the browser bridge. Send the relay only the page text needed for extraction, with password/payment fields redacted and a configurable maximum (for example 12,000 characters). Write only inside an owner-selected notes root; include source URL and capture time so the note is auditable. If the page is private or exceeds the limit, say so rather than silently truncating.
- **missing:** A browser command that returns sanitized reader text and current selection from the active tab; A relay intent that binds the utterance to the active browser tab and returns a deterministic artifact plan; A Mac-side atomic note writer with stable slug/deduplication and a receipt that can be announced to the pendant

### "“When my Mac is available again, do this exact desktop task and tell me whether it actually finished.”"
- **useful because:** A pendant request should not be lost because the laptop is asleep, offline, or the browser bridge is temporarily disconnected. The relay can hold an idempotent intent, the Mac can execute it on reconnection, and the pendant can receive a durable success/failure result rather than the owner guessing whether the task happened. This is especially valuable for long-running exports, file preparation, and opening a work context after a commute.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use a cheap background state machine for retry, lease expiry, deduplication, and result handling. Use realtime only to parse the spoken command initially and to speak the final receipt. Never re-plan an already accepted action on every retry.
- **latency:** Acknowledge queueing immediately; execute within 10 seconds of the Mac heartbeat returning; deliver the receipt within 2 seconds of completion. Expire unstarted intents after an owner-configurable deadline.
- **cost:** Near-zero for retries and status checks; one small intent-parsing call per request. Cost is dominated by the requested desktop work, not orchestration.
- **security:** Persist an action hash, target resources, and owner-visible status, but not secrets or page contents. Retry only idempotent plans or plans carrying an explicit deduplication key. A crashed execution must remain 'unknown' until receipt inspection, never be replayed blindly. High-impact actions should be represented as queued but not auto-run unless the owner’s eventual policy explicitly allows them.
- **missing:** A reconnect worker that claims pending intents when the Mac bridge heartbeat returns; An idempotency key and lease/unknown-result state in the Mac job records; A pendant-facing result envelope that distinguishes queued, running, succeeded, failed, and needs-owner-attention

### "“Fill in the sensitive fields, but make me confirm that this is the right site and exactly what will be submitted.”"
- **useful because:** Today the browser can automate a form and the pendant can speak, but there is no field-level safety handshake joining them. This would let the owner use voice to complete repetitive forms without silently exposing an address, identity number, or payment instrument to a lookalike site. The pendant gives a physical, out-of-band confirmation channel while the browser retains the session and the Mac performs the fill.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Use deterministic browser origin and field-type inspection first. Use a small text model only to explain ambiguous labels. Realtime handles the short spoken confirmation; no model should receive field values unless the owner explicitly chooses to hear them.
- **latency:** Inspect the page in under 1 second, speak a compact preview in under 3 seconds, and fill immediately after the owner's confirmation.
- **cost:** Usually negligible: deterministic inspection plus one short explanation call only for ambiguous fields. The expensive model is unnecessary.
- **security:** Never read passwords, full card numbers, or security codes into relay context. The browser extension should hash or classify fields locally, send only origin, field categories, and redacted previews, and require exact-origin binding. A confirmation must expire after navigation or field mutation; submit remains a separate explicit step.
- **missing:** Browser-local sensitive-field classification and origin binding; A pendant confirmation protocol carrying a one-time form intent hash; A browser action that applies only the approved field subset and reports changed fields without secrets

### "“Translate this conversation for me live, and put the translated text on my Mac so I can refer to it without interrupting the speaker.”"
- **useful because:** The pendant is the always-present audio interface, while the Mac has the screen and keyboard-sized workspace. Combining them would provide live two-way translation with a private rolling transcript on the Mac, instead of forcing the owner to hold a phone or interrupt the conversation. The pendant can speak only the translated turns when requested, while the Mac keeps the visual context.
- **path:** pendant → relay-realtime → mac-planner → mac-vision
- **model tier:** Realtime speech and translation for low latency; a cheaper background model periodically cleans punctuation and speaker turns on the Mac transcript. Do not send the transcript to browser services unless the owner asks.
- **latency:** Translated speech should begin within 700 ms of an utterance boundary; Mac text should appear within 1 second. Keep a bounded rolling window and finalize turns asynchronously.
- **cost:** Realtime audio translation dominates, approximately continuous voice-session pricing; local Mac rendering is negligible. The background cleanup model should run only on finalized turns.
- **security:** Conversation audio and transcript leave the pendant for relay processing, so this must be an explicit session mode with a visible LED/state indicator and local privacy-latch override. Default retention is none; the Mac transcript is opt-in, encrypted at rest, and auto-deleted at session end unless saved.
- **missing:** A relay translation mode with language selection and turn segmentation; A Mac-side streaming transcript sink with bounded retention and speaker labels; A pendant mode that can switch between translated playback, original playback, and silent visual-only operation

### "“Before I send this, check the attachment, recipients, and quoted claims against the source material, then tell me only what could embarrass me.”"
- **useful because:** This is a high-value pre-send review that no single node can perform reliably: the Mac has the draft and local attachments, Safari may hold the source page, and the relay can compare claims and identify contradictions. The owner gets a concise spoken risk report before an irreversible email or post, rather than discovering a wrong attachment or unsupported statement afterward.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use deterministic checks for recipient expansion, attachment existence, file type, and source URL matching. Use a strong but non-realtime text model for claim comparison and reputational-risk ranking; use realtime only to read the final short report.
- **latency:** Review a normal email or post in under 15 seconds; report obvious mechanical issues in under 3 seconds while deeper claim checking continues. Never submit automatically as a side effect of review.
- **cost:** One bounded document-comparison call per review, with tokens dominated by the draft and selected source excerpts. Mechanical checks are local and free.
- **security:** Drafts, attachments, recipients, and private source pages are sensitive. Keep raw attachments on the Mac, extract only quoted passages and hashes for model review, redact secrets and unrelated thread history, and expire the review bundle after the result. Sending remains a separate owner action.
- **missing:** A Mac draft/attachment reader that returns structured metadata and redacted text; A browser source-selection operation that supplies only explicitly selected or cited passages; A cross-surface comparison job with a short-lived encrypted bundle and evidence-linked findings


## What it asked for

_Nothing._
