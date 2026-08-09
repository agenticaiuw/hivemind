# Harness derivation — browser-extension — round 186

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Read this private page and turn its actual deadlines into reminders, keeping the source link and a one-line quote so I can verify each one.”"
- **useful because:** Authenticated dashboards often contain deadlines that public search and Mac calendar APIs cannot see. The browser extracts the page the owner already has open; a cheaper model identifies dates and confidence; Mac creates reversible reminders only after showing the proposed set, with the original URL and short evidence retained locally. The pendant can read back the compact result while the browser session remains private.
- **path:** browser-extension → mac-planner → relay-realtime
- **model tier:** background text extraction with a small model; realtime only for the spoken recap or a follow-up question
- **latency:** 15–30 seconds for extraction and reminder proposals; no need for a persistent low-latency loop
- **cost:** About $0.002–$0.02 per page depending on length; browser command wait and local reminder creation dominate latency, not tokens
- **security:** Never infer deadlines from hidden or unrelated page content. Store only URL, date, title, and a short redacted evidence snippet; let owner configure origins and categories. Before creating reminders, present the complete batch and allow correction; reminder creation is reversible.
- **missing:** A browser_read_page/browser_snapshot result that includes stable URL and selected text ranges; A date/deadline extraction schema with confidence and timezone handling; A reviewable dry-run response that can be confirmed as a batch before POST /execute reminder actions; Per-origin retention/redaction configuration

### "“From the private site I’m on, find every security or account-change notice since my last check, explain what changed, and prepare (but do not send) the safest next step.”"
- **useful because:** Security notices are high consequence and often visible only inside authenticated web sessions. This combines browser-only access with relay judgment and Mac execution without sending messages or changing account state: the owner gets a concise pendant alert, a local evidence bundle, and a prepared draft/action plan to inspect. It is materially different from generic page watching because it performs incident triage and produces a reversible response package.
- **path:** browser-extension → relay-realtime → mac-planner → relay-realtime
- **model tier:** Use a cheap background classifier for notice detection and deduplication; reserve realtime for urgent spoken alert and owner questions
- **latency:** On-demand triage in 20–45 seconds; urgent notices should interrupt within 10 seconds after extraction
- **cost:** Roughly $0.005–$0.05 per triage depending on page count; browser extraction and screenshot/evidence handling dominate
- **security:** Treat account-security pages as highly sensitive: no raw HTML or screenshots to relay by default, redact tokens and personal identifiers locally, keep evidence encrypted and ephemeral, and never submit a password reset, revoke a session, or send a message. Owner must explicitly configure origins and retention.
- **missing:** A browser session diff that can identify new notices since a stored cursor without storing page bodies; Local redaction/classification for security-notice categories; A draft-only action representation for next steps (open reset page, compose but do not send, create reminder); Pendant alert priority/expiry integration for security events

### "“Compare the private documents and offers open in my logged-in tabs, give me a decision table with the exact differences, and save a local packet I can review later.”"
- **useful because:** No single node can do this: Safari alone can see the private tabs but cannot reliably normalize them; the relay can reason across documents but should not receive raw secrets; the Mac can create a durable local packet; the pendant can deliver the short recommendation. It turns scattered authenticated pages into a verifiable comparison rather than an opaque summary.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** Use a background extraction/comparison model on redacted text; use realtime only when the owner asks follow-up questions about a row
- **latency:** 30–90 seconds for 2–8 tabs; stream progress after each tab so the owner is not waiting blindly
- **cost:** Approximately $0.02–$0.20 per packet depending on document length; local PDF/HTML rendering and browser extraction are the main latency costs
- **security:** Default to local processing and never upload raw documents. Redact account numbers, addresses, and payment data before model calls; persist only the comparison table and provenance links in a local encrypted packet. Show uncertainty and source tab for every cell. No purchase, acceptance, or submission is performed.
- **missing:** A multi-tab browser extraction command that returns bounded text plus tab IDs and URLs; A local redaction and structured-document parser for tables/PDF viewers; A provenance-aware comparison schema (claim, value, source, confidence); A local packet writer and a pendant-friendly summary/alert path

### "“Reconcile the same real-world commitment across my logged-in sites—calendar booking, vendor portal, and confirmation page—and tell me if any date, amount, or cancellation rule disagrees.”"
- **useful because:** Today each authenticated site is an isolated view. A single wrong date or cancellation term can cost the owner money, yet public search and ordinary Mac integrations cannot inspect those private pages together. This capability would produce a source-by-source reconciliation, identify the authoritative-looking conflict, and speak only the actionable discrepancy through the pendant; it would not change or submit anything.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** Use a background extraction and deterministic field-normalization model; use realtime only for the short spoken discrepancy and follow-up questions.
- **latency:** 30–90 seconds for three to six authenticated pages, with incremental progress after each page.
- **cost:** Approximately $0.02–$0.15 per reconciliation, dominated by document extraction; caching normalized fields keeps repeat checks cheap.
- **security:** Raw pages and credentials stay on the Mac. Send only redacted normalized fields and provenance hashes to the reasoning tier; retain the result locally with configurable expiry. Never infer consent to cancel, amend, or dispute a commitment.
- **missing:** Cross-origin authenticated session orchestration that can open and extract a declared set of URLs without mixing tabs; A typed normalized schema for dates, amounts, parties, status, and cancellation terms with source provenance; Local redaction and conflict detection before any model call; A compact pendant alert that names the conflict and lets the owner request the cited source

### "“Build me a private renewal map from the accounts I name: what renews, when, for how much, and what I must do to avoid an unwanted charge.”"
- **useful because:** The owner cannot get a trustworthy inventory of authenticated subscriptions from public search or Apple/Mac APIs. The browser can inspect the actual account pages, the Mac can maintain a local ledger and reminders, and the pendant can warn only about an imminent actionable renewal. This is a durable financial calendar, not a generic page-change alert.
- **path:** browser-extension → mac-planner → relay-realtime
- **model tier:** Background extraction plus deterministic recurrence/date parsing; realtime only for an imminent spoken warning.
- **latency:** Initial scan 1–3 minutes for several origins; incremental checks under 20 seconds per origin.
- **cost:** $0.01–$0.10 per initial origin scan, then pennies or less for field-only refreshes; browser session time dominates.
- **security:** Do not retain full billing pages, payment data, or credentials. Store merchant, plan, amount, currency, renewal date, cancellation route, and a redacted citation under owner-selected retention. Never cancel automatically; expose the exact next step.
- **missing:** A local subscription record schema with recurrence, confidence, and source cursor; Cross-origin browser extraction that can detect cancellation instructions without collecting payment details; A recurrence-aware reminder scheduler and deduplication logic; Per-origin redaction and never-store configuration

### "“When a private site asks me to verify identity or consent, show me exactly what it will disclose, why it is asking, and what alternatives exist—before I continue.”"
- **useful because:** The browser sees consent and identity prompts that the relay or Mac APIs cannot. Today the owner must interpret dense, changing disclosures alone. This would extract the visible request, compare it with the site's stated purpose and available alternatives, summarize the data categories on the pendant, and leave the page untouched until the owner chooses a next step.
- **path:** browser-extension → relay-realtime → mac-planner
- **model tier:** Use a local/cheap classifier and deterministic extraction for data categories; realtime only for an interactive explanation.
- **latency:** 5–15 seconds after a page snapshot, with immediate short alert and deeper detail on request.
- **cost:** Usually under $0.01 per prompt; screenshot/OCR fallback is the main cost and latency.
- **security:** Identity prompts are highly sensitive. Keep screenshots and raw disclosures on the Mac, redact identifiers before model use, never click consent automatically, and record only the owner-approved decision and site origin. Configuration must allow categories that may never be spoken aloud.
- **missing:** A browser event trigger for consent/identity dialogs and stable DOM capture; A local disclosure parser that identifies requested data, purpose, retention, and alternatives; A private on-device evidence store with expiry and source citation; Pendant interaction for hear-more, bookmark, or dismiss without advancing the page


## Changes it proposed to its own stack

### `browser-harness` — Implement a bounded multi-tab extraction transaction: snapshot/list tabs, select explicit tab IDs, extract only visible text and table structure with byte/token limits, apply local redaction, and return per-field provenance plus a cursor. Persist no raw page body and make the transaction resumable if Safari changes tabs.
- **owner gets:** The owner can ask the pendant to compare or act on several private pages without leaking whole authenticated documents or losing track of which tab supported an answer.
- effort: Medium: extension command schema, local-agent browser bridge, redaction and cursor storage, plus tests across Safari tab changes.  ·  risk: A page may expose stale or partial content; recover by marking fields unavailable and asking for a fresh snapshot. Never silently merge tabs after navigation; bind results to tab ID and URL.
- cost: Minimal API cost; bounded extraction lowers token spend. Local storage is small metadata plus redacted excerpts.  ·  latency: Adds one local extraction/redaction pass (usually under 2 seconds), but avoids repeated full-page model calls.
- security: Improves security by enforcing local bounds and redaction before relay/model upload; requires careful selector and URL provenance handling.
- depends on: Owner-supplied per-origin read/redact/never-store configuration; A working browser_read_page/browser_snapshot result schema with stable tab IDs; Local encrypted metadata storage


## What it asked for

_Nothing._
## Its own summary

Fresh discovery: Safari is online now (extension 1.2.0, two tabs; active tab is Google Maps), with no pending browser commands. I recorded three distinct browser-led capabilities: authenticated-page deadlines into evidence-backed reminders, security-notice triage with draft-only next steps, and multi-tab private-document comparison into a local provenance packet. I also recorded a concrete browser-harness change: bounded, redacted, resumable multi-tab extraction with tab/URL provenance. The first authenticated-page monitoring concept collided with an existing backlog item, so I did not count or restate it.

**Biggest unknown:** The owner still has not supplied the actual authenticated origins and per-origin rules (what may be read, spoken, retained, or never stored). The system should keep that configuration explicit and empty rather than guessing. Technically, the next missing bridge is a stable multi-tab browser extraction/result schema with local redaction and provenance; current live browser access is usable for on-demand work.

