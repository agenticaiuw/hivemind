# Harness derivation — browser-extension — round 207

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Compare the two logged-in pages I have open and tell me whether they disagree about the same thing.”"
- **useful because:** No single Mac or relay node can see both authenticated sessions. The browser can read each private page, normalize dates/amounts/statuses, and the relay can explain a discrepancy through the pendant without storing either page. This is useful for invoices versus bank records, booking confirmations versus calendars, or order status versus refunds.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** A cheap background planner extracts typed claims and aligns entities; realtime is used only for the final concise spoken discrepancy report.
- **latency:** Read two existing tabs and produce a result in 10–20 seconds; speak the first material mismatch as soon as it is established.
- **cost:** About $0.02–$0.08 per comparison, mostly the structured cross-page alignment; page text is capped and discarded after extraction.
- **security:** Require explicit tab selection or owner-selected origins for each comparison; never merge unrelated accounts by URL alone. Persist only short claims with URL provenance under existing browser TTL rules, never HTML, screenshots, or full page text.
- **missing:** A multi-tab browser execution primitive that tags each read with tab identity and a comparison nonce; Entity/claim alignment for dates, totals, IDs, and statuses with an uncertainty result; An empty, inspectable per-origin configuration that the owner can populate later

### "“When this private portal says the transaction is complete, save only the receipt facts locally and remind me about the next date; if it isn’t complete, tell me exactly what is still missing.”"
- **useful because:** The browser is the only node with the logged-in transaction state, while the Mac can create local records/reminders and the pendant can deliver the result even when the owner walks away. It turns a private web status into a useful local follow-up without archiving the page.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background planner extracts a small typed status/date/amount record; Mac executes create_reminder or local filing; realtime is reserved for exceptions or a concise spoken result.
- **latency:** One-shot check in 10 seconds, with a reminder created immediately after a confident completion state.
- **cost:** Roughly $0.01–$0.04; dominated by extraction and date normalization, not audio.
- **security:** Owner must explicitly name the origin/task; persist only the minimal claim and provenance under current browser TTL limits. Never save receipt images or account identifiers by default. Treat ambiguous states as report-only and never invent a due date.
- **missing:** A browser-to-Mac typed handoff carrying status, amount, and due date with confidence and provenance; A date/amount normalization and ambiguity policy; Owner-supplied per-origin extraction rules; ship empty rather than guessing sites

### "“Before I commit to this private booking or purchase, inspect the final page, calculate the real total and cancellation window, compare it with my budget and calendar, and tell me whether anything conflicts—without changing the page.”"
- **useful because:** Authenticated checkout details and hidden cancellation terms are inaccessible to the relay alone. The browser reads them, the Mac contributes local budget/calendar context, and the pendant gives a hands-free go/no-go explanation before any mutation. This is a high-value decision aid, not an execution gate.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background planner for typed extraction and arithmetic; use realtime only for the short decision briefing and follow-up questions.
- **latency:** Under 15 seconds for a two-source comparison; stream the total and any hard conflict first, then details.
- **cost:** About $0.02–$0.06 per check; arithmetic is cheap, while extracting cancellation clauses is the dominant model work.
- **security:** Read-only browser allowlist for this task: navigate/read/scroll only, explicitly excluding click/type/select. Do not retain payment data or page bodies; retain at most short claims with URL evidence and current expiry. Never present an inferred cancellation policy as certain without quoting the source text.
- **missing:** A typed read-only “transaction facts” extractor that returns totals, fees, dates, cancellation clauses, and confidence; A local budget/calendar comparison contract with clear timezone and currency handling; Owner-provided per-origin rules and a browser tab-selection mechanism

### "“I’m leaving now—check my private reservation or ticket, my calendar, and the route, then tell me the latest safe departure time and put the right boarding/check-in page in front of me. Don’t expose or save the barcode.”"
- **useful because:** Today the authenticated ticket is trapped in Safari, calendar and local machine state are elsewhere, and the pendant cannot combine them into a timely decision. This would give the owner one reliable departure answer while walking out the door, with the browser session still holding the sensitive barcode and the pendant speaking only the minimum needed.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap background planner for extracting departure/check-in deadlines and reconciling calendar and route data; use realtime only to speak the final departure time and exceptions.
- **latency:** First answer within 10 seconds; refresh route conditions once before speaking; browser should foreground the relevant private page without transmitting its barcode.
- **cost:** About $0.02–$0.08 per invocation, dominated by route/deadline reconciliation; no model call should receive the barcode or screenshot.
- **security:** Browser returns typed deadline/location claims, not QR/barcode pixels or full page text. The extension keeps the ticket page local and foregrounds it only on the owner’s device. Ambiguous timezone, venue, or check-in rules must be spoken as uncertainty rather than silently resolved. Store no travel credential; short claims use existing browser provenance and expiry rules.
- **missing:** A typed private-travel extractor for departure, check-in, gate/venue, and credential-presence without returning credential material; A route/departure-time service that can combine Mac location/traffic context with browser facts; A secure browser command to foreground a specific tab while returning zero page content; A pendant notification handoff that can speak the deadline and wake the owner without exposing the ticket

### "“Before my appointment, check the authenticated instructions page, compare it with my calendar and the notes on my Mac, and give me a spoken checklist of what to bring, do, and ask. Keep the private page out of storage.”"
- **useful because:** The owner currently has to manually reconcile private portal instructions with local notes and schedule. Safari supplies information unavailable to the relay, the Mac supplies the owner’s own context, and the pendant makes the result usable while preparing or traveling.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background planner extracts only checklist items and conflicts; realtime turns the compact result into an interactive spoken checklist.
- **latency:** Generate in under 15 seconds and answer follow-up checklist questions in under 2 seconds.
- **cost:** Approximately $0.02–$0.06, mainly for extracting and deduplicating instructions; no full-page context needs to reach the expensive tier.
- **security:** Return only typed actions, dates, and questions—not diagnoses, identifiers, or page screenshots unless explicitly requested. Keep the source page ephemeral and attach URL provenance to each claim. Owner must later provide origin/category rules; default configuration remains empty.
- **missing:** A private-page checklist extractor with source spans and confidence; A local-notes/calendar join that can flag contradictions without copying sensitive note bodies into the relay; A spoken checklist state (checked items and unanswered questions) that can survive a dropped browser link

### "“Check my logged-in account’s security page and tell me whether I could recover it if I lost this device; make a private, offline checklist of the missing recovery steps, but don’t change any settings.”"
- **useful because:** A relay or Mac alone cannot inspect the owner’s authenticated security posture. The browser can inventory whether recovery methods, backup codes, and trusted devices exist; the Mac can hold a minimal checklist, and the pendant can warn about gaps without speaking secrets aloud.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background planner to classify only the presence/absence of recovery controls; realtime speaks the short risk summary and can answer follow-ups without receiving codes or secret values.
- **latency:** Read-only audit in 10–20 seconds; urgent absence of all recovery paths should be spoken immediately.
- **cost:** About $0.02–$0.05, dominated by interpreting account-security UI; secret values are never sent to a model.
- **security:** Strictly exclude password, backup-code, security-answer, token, and recovery-address values from extraction. Store only boolean/typed posture claims with host provenance and short TTL. No clicks or changes are permitted in the audit. An owner-configured origin is required; no sites should be assumed.
- **missing:** A security-posture extractor that recognizes recovery controls while redacting their values; A browser read-only action manifest that excludes clicks, typing, and navigation away from the security page; A local encrypted checklist record and pendant alert path for a missing recovery route


## What it asked for

_Nothing._
## Its own summary

I discovered the newly granted browser_read_or_navigate resolver. It resolves correctly to browser_read_page, but its call is deliberately non-invoking in this harness; the live browser remains unusable until Safari has a tab (known state: tabCount=0). I recorded three distinct cross-surface capabilities: (1) compare claims across two authenticated tabs, (2) turn a private transaction-complete status into a minimal local reminder/receipt fact, and (3) the highest-value proposal: a read-only pre-commit purchase/booking rehearsal that extracts true total and cancellation terms, compares budget/calendar, and speaks conflicts through the pendant. A form-filling proposal was rejected as a duplicate, so I did not restate it.

**Biggest unknown:** I still need an owner-supplied, inspectable per-origin configuration (currently intentionally empty), at least one real authenticated site/task to exercise safely, and a reliable tab-selection/bootstrap path. I do not need another enqueue wrapper; the remaining gap is tab availability and typed multi-tab/read-only result contracts. The orchestrator should also expose whether /browser/provenance and /prepare are actually live before those are treated as implementation dependencies.

