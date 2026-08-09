# Harness derivation — browser-extension — round 185

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take the appointment details from this logged-in web page and put the right event on my calendar, including the location and a link back to the page.”"
- **useful because:** Authenticated booking, healthcare, school, and service portals often hide the authoritative date behind the owner’s session. Safari can read it where web search cannot; the Mac can create the calendar event; the relay resolves ambiguity and the pendant reports exactly what was added. This removes transcription errors without requiring the owner to copy private details into chat.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-action
- **model tier:** A background extraction model parses date/time/timezone/location and confidence; realtime is used only for a concise spoken result or an ambiguity question.
- **latency:** Extract and create within 10 seconds for a normal page; if timezone or multiple appointments are ambiguous, return a short question instead of guessing.
- **cost:** Low to moderate: one browser extraction and one structured parse; Mac calendar mutation is local and cheap.
- **security:** Only the selected page or active tab is read. Do not persist page body; retain only the event fields and source URL with an expiry. The owner configures origins and categories permitted for calendar capture. Creating an event is a reversible local mutation with a receipt and undo.
- **missing:** A browser-to-structured-record handoff that preserves source URL and extraction confidence; Calendar event creation with an undo receipt exposed to the relay; An explicit per-origin policy supplied by the owner

### "“Keep my logged-in web sessions usable: when one expires, tell me which site needs a login, open its sign-in page, and resume the waiting task after I log back in.”"
- **useful because:** Today a browser job simply fails after a session expires. This makes authenticated automation dependable without handling credentials: Safari detects the login wall, the relay tells the owner on the pendant exactly which origin is blocked, the Mac reopens the recovery page, and the queued job resumes from its last safe read step once the session returns.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-action
- **model tier:** Use deterministic page fingerprints for login-wall detection and a cheap background state machine; realtime is only for the brief owner notification.
- **latency:** Detect on the next command or heartbeat (under 5 seconds), speak immediately, and resume within 10 seconds after the extension reports the authenticated page again.
- **cost:** Very low: mostly extension/relay state transitions; one short spoken notification.
- **security:** Never collect or transmit credentials, OTPs, or password-field values. The extension reports only origin, title, and authenticated/blocked state. Recovery must pause before any form submission; the owner completes login in Safari. Persist only an expiring job checkpoint.
- **missing:** Login-wall and post-login success fingerprints in the Safari extension; A resumable read-step checkpoint attached to browser jobs; A pendant notification route that identifies the blocked origin

### "“Compare the balances and due dates across the private accounts I have open, flag anything inconsistent, and make me a short action list.”"
- **useful because:** The valuable answer is often relational rather than a single page read: authenticated Safari tabs can expose the authoritative figures from separate providers, while the relay normalizes currencies, dates, and account labels and the pendant gives a concise discrepancy list. No public search or single Mac app can see all of those logged-in pages together.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-judgement
- **model tier:** Use a background structured-extraction model per tab and a second cheap deterministic reconciliation pass; use realtime only to answer follow-up questions.
- **latency:** Process 2–6 tabs in under 30 seconds; speak a first discrepancy summary as soon as two comparable records are available.
- **cost:** Moderate: extraction scales with tab count, but structured records and a short final response keep token use bounded.
- **security:** This can expose financial or health information. The owner must explicitly choose the origins and fields allowed, with default no persistence and no cross-request memory. Never read password, payment, or message fields. Speak only category-approved summaries; retain source URLs and raw values only in a short-lived encrypted job record.
- **missing:** A user-defined cross-origin extraction recipe with typed fields and join keys; A reconciliation engine that reports evidence and confidence rather than inventing matches; An ephemeral, privacy-scoped multi-tab bundle delivered from Safari to the relay

### "“Save the report I’m viewing in this logged-in site as a clean, dated file on my Mac, and tell me exactly what was included.”"
- **useful because:** Owners can currently ask for a page summary, but cannot reliably turn a private, session-only report into a durable local artifact with provenance. Safari would read the authenticated report, the relay would remove navigation noise and produce a structured rendering, and the Mac would save it where the owner can use it offline. The pendant gives a concise receipt rather than making the owner inspect a screen.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-action
- **model tier:** Use a background extraction/formatting model; realtime is unnecessary except for a short spoken completion receipt or an ambiguity question.
- **latency:** Produce a preview in under 15 seconds and save within 30 seconds for a normal report. If the page is paginated or incomplete, state that before saving.
- **cost:** Low to moderate: one structured extraction and formatting pass; local file creation is inexpensive.
- **security:** The owner explicitly chooses the destination and allowed origin. Do not include passwords, hidden fields, or unrelated tabs. Save only the selected report, with source URL, capture time, completeness, and a content hash; offer expiration/deletion metadata. The spoken receipt must not read sensitive report contents unless the owner requests it.
- **missing:** A browser command that exports the selected authenticated page or report, including pagination completeness and selected-region boundaries; A privacy-scoped formatter that converts the result to Markdown/PDF/CSV without retaining the raw DOM; A Mac-side artifact writer with provenance metadata and a durable receipt/undo-delete operation

### "“Read the chart on this private page, give me the underlying trend and the one unusual point, and open the exact evidence when I ask.”"
- **useful because:** Authenticated dashboards often expose decisions only through graphs that ordinary page extraction misses. Safari can access the owner’s private dashboard, a vision/extraction pass can recover axes, legends, and plotted values, and the relay can explain the trend in spoken language while preserving a precise evidence location for the Mac to reopen.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant → faculty-perception
- **model tier:** Use a vision-capable background model for chart interpretation and a cheap deterministic sanity check for labels/units; realtime only handles the owner’s follow-up question.
- **latency:** Return a spoken first interpretation within 20 seconds for one chart; surface uncertainty rather than guessing when axes or units are unreadable.
- **cost:** Moderate: screenshot transfer and vision inference dominate; follow-up questions reuse a compact chart representation.
- **security:** Capture only the selected chart region, not the whole page or neighboring account data. Keep the screenshot and extracted points ephemeral unless the owner explicitly asks to save them. Preserve URL, region bounds, units, and confidence so the explanation is auditable.
- **missing:** A Safari selected-region/chart capture action with coordinates and page fingerprint; A chart-to-structured-series extractor with unit and confidence validation; A cross-surface evidence locator that can reopen and highlight the original chart

### "“Check this private form before I submit it: list every required field I missed, contradictions in my answers, and anything that will likely be rejected.”"
- **useful because:** The owner can have an agent fill or read a form, but not a reliable preflight that reasons across fields and site validation hints before an irreversible submission. Safari supplies the live authenticated form, the relay checks consistency and required-field coverage, and the pendant gives a short defect list while the Mac highlights each exact field.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant → faculty-judgement
- **model tier:** Use deterministic DOM/constraint checks first, then a cheap model for cross-field contradictions and unclear validation language; realtime is only for spoken interaction.
- **latency:** Complete a normal form preflight in under 10 seconds and highlight defects immediately; never block the owner’s own submission.
- **cost:** Low to moderate: DOM inspection is cheap, with model calls only for ambiguous labels or cross-field reasoning.
- **security:** Read only the selected form and redact password, payment, and secret fields before transmission. Do not persist answers. Report validation evidence and confidence, not guessed corrections. The owner explicitly supplies origins allowed for this workflow.
- **missing:** A form-specific browser inspection that returns required/invalid fields and validation messages without values for sensitive inputs; A cross-field consistency checker with typed dates, amounts, and identifiers; An evidence-highlighting command that focuses Safari on each defect and a spoken defect receipt


## What it asked for

_Nothing._
