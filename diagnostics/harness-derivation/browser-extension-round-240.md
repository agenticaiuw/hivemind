# Harness derivation — browser-extension — round 240

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live authenticated browser access** — Safari is online with 5 tabs, and POST /execute directly executes browser_list_tabs and browser_read_page. Active tab is a USPS tracking page showing package 9200190323035201509394 delivered in Madison, WI on August 8, 2026 at 11:42 AM.
  - evidence: POST /execute browser_list_tabs and browser_read_page returned status 200 with tab list, active tab 7351218, and page text/evidence capsule.

## Capabilities it proposed

### "Tell me what changed in my authenticated web life since yesterday, but only interrupt me for something actionable."
- **useful because:** The browser is the only node with the owner's live logged-in sessions, while the relay and pendant are the only surfaces that can deliver a concise interruption away from the screen. This turns scattered portals and order pages into one useful exception feed instead of requiring manual checking.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background for scheduled page reads and change classification; realtime only when the owner asks a follow-up
- **latency:** Daily scheduled sweep in under 2 minutes; an on-demand query under 15 seconds; alert delivery within 30 seconds of detecting a change.
- **cost:** Low: one cheap extraction/classification call per changed page, dominated by authenticated page fetches; no expensive realtime model unless the owner asks.
- **security:** Page text stays ephemeral; persist only short claims, host, URL, hash, and 24-hour provenance using existing browser memory rules. Ship an empty per-origin configuration and require the owner to add origins and may-speak categories. Never submit forms or send messages during a sweep.
- **missing:** A scheduler that fans out read-only browser jobs over owner-supplied origins; Cross-origin change deduplication and actionable ranking; Relay event to offline_alert_inbox adapter for this alert class; Owner-supplied per-origin and spoken-category configuration

### "When I press the pendant while I’m on a web page, tell me what is on the current Safari page and what I should notice, without me copying a link."
- **useful because:** It joins the worn button, the browser's authenticated active tab, and the relay's speech path into a genuinely hands-free reading aid. It works for pages behind logins that public search cannot see, and it can answer while the owner's hands and eyes are occupied.
- **path:** pendant → browser-extension → relay-realtime → mac-planner
- **model tier:** cheap background summarizer for page extraction; realtime only for follow-up questions or conversational clarification
- **latency:** Active-tab capture in under 2 seconds; spoken first sentence within 5 seconds; follow-up under 3 seconds when the page has already been captured.
- **cost:** Low to moderate: one bounded page extraction and short summary per press, with follow-ups reusing the evidence capsule; browser latency dominates.
- **security:** Do not persist the page body or screenshot. Keep an ephemeral evidence capsule and store only a short, host-keyed claim if the owner explicitly asks to remember it. Speak only the visible page's salient facts, with owner-configurable categories for never-speak; never click or type from a press-only trigger.
- **missing:** Pendant event for 'summarize current browser tab' distinct from existing bookmark and alert controls; A reliable active-tab capture action and tab identity handoff from Safari extension; Relay route that binds the capture to the originating pendant press and streams speech; A short-lived page-context cache with automatic expiry

### "Make me a timestamped proof packet from this logged-in webpage and the matching files on my Mac, then tell me exactly what evidence it contains."
- **useful because:** The browser can see authenticated order, shipment, billing, or account pages while the Mac can collect local receipts and correspondence. Combining them creates a useful, verifiable record for disputes or reimbursements instead of an unverifiable screenshot or a manually assembled folder.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** background model for matching and contradiction detection; realtime only to answer questions about the packet
- **latency:** Under 90 seconds for a small packet; speak the evidence index within 5 seconds of completion.
- **cost:** Moderate: extraction and matching over a few bounded documents; local PDF assembly is cheap. Storage, not model tokens, dominates for retained packets.
- **security:** Persist only when explicitly requested. Keep original files local; include page URL, timestamp, content hash, and selected excerpts with redaction of credentials and unrelated personal data. Do not upload an entire authenticated page to third parties, and never take an action on the site as part of collection.
- **missing:** A user-directed evidence-packet job that joins browser evidence capsules to local files; Content-hash and timestamp manifest with selective redaction; Local encrypted packet storage and expiry/delete control; Pendant-readable evidence index and provenance trace

### "Reconcile my authenticated orders against local receipts and delivery pages, and tell me only when the price, item, status, or delivery evidence disagrees."
- **useful because:** The browser can inspect order and delivery portals behind the owner's logins while the Mac can inspect local receipts, but today they are separate silos. Cross-source reconciliation catches missing deliveries, duplicate charges, wrong prices, and stale order states without making the owner manually compare pages.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Background model for document matching, normalization, and discrepancy classification; realtime only when the owner asks for an explanation or the discrepancy is urgent.
- **latency:** Nightly reconciliation under 3 minutes for configured sources; urgent mismatch alert within 60 seconds of a new page or local receipt; explanation within 5 seconds on demand.
- **cost:** Moderate: one extraction and matching pass per changed order/receipt, with most cost from authenticated page access and OCR/PDF parsing rather than speech.
- **security:** Keep source documents and page bodies local or ephemeral. Persist only a bounded discrepancy claim, source URLs, hashes, timestamps, and provenance with short expiry. Never initiate refunds, contact merchants, or alter orders. Ship origin and category rules empty until the owner configures them; suppress account numbers and payment details from speech.
- **missing:** Order/receipt entity normalization across browser pages and local files; A durable but redacted discrepancy ledger with source-by-source provenance; Change-triggered joins between browser page watches and Mac file observation; Pendant alert wording that distinguishes uncertain matches from confirmed mismatches; Owner-configured origins and retention policy for financial and purchase data


## What it asked for

_Nothing._
