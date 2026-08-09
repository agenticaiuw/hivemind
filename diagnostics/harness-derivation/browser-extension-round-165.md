# Harness derivation — browser-extension — round 165

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with 9 tabs; active tab is authenticated X home at https://x.com/home (tabId 1163292), and browser_read_page through POST /execute succeeded with live page text and provenance/receipt. Browser work is executable now, not hypothetical.
  - evidence: GET /browser/status returned online=true, tabCount=9, tabUrl=https://x.com; POST /execute browser_read_page returned status success, title Home / X, tabId 1163292, evidence capsule and receipt.

## Capabilities it proposed

### "“Check whether my travel booking, calendar, and email agree: flag any departure-time, date, passenger, or cancellation-policy mismatch, and tell me what I should fix.”"
- **useful because:** No single source contains the truth. The browser is the only node that can inspect the owner's authenticated booking and mail sessions, while the Mac/relay can correlate them and the pendant can deliver a concise actionable warning. It prevents missed flights and expensive policy mistakes without booking or cancelling anything.
- **path:** pendant → relay-realtime → browser → mac-planner → dashboard
- **model tier:** background for the three-way extraction and comparison; realtime only for the owner's follow-up question
- **latency:** 15–45 seconds for an on-demand check; under 2 minutes for several sites with slow sessions
- **cost:** Roughly $0.01–$0.08 per check, dominated by authenticated page extraction and a small comparison-model call; no model call for unchanged cached evidence
- **security:** Page text and booking identifiers leave Safari only as minimized, redacted evidence capsules; never persist full page text. Origin rules must be explicitly configured by the owner and default to empty. Never send cancellation or booking commands; show discrepancies and exact source URLs instead.
- **missing:** A multi-origin browser job that can read named authenticated tabs/sessions and return normalized fields with provenance; Owner-supplied per-origin read/redact/never-store rules; A correlation schema for itinerary, calendar event, email thread, and policy terms; A dashboard view of evidence and unresolved conflicts

### "“Answer this question using my private web accounts and the public web, and cite exactly which private pages support each claim. Don’t save the private page text.”"
- **useful because:** The owner can ask questions whose answer is split between an authenticated knowledge base, project portal, or account and public sources. Safari can reach sessions that the relay and Mac filesystem cannot; provenance lets the owner distinguish private evidence from guesses, while the no-save rule keeps the browser tier from becoming a secret archive.
- **path:** pendant → relay-realtime → browser → mac-planner → dashboard
- **model tier:** background retrieval and synthesis; realtime only to clarify an ambiguous question or read a short answer aloud
- **latency:** 20–90 seconds depending on number of origins; stream progress to the pendant after each source
- **cost:** $0.02–$0.15 per question, mostly browser extraction volume and synthesis; use a cheap model for query decomposition and a stronger model only for conflicting evidence
- **security:** Send only query-specific excerpts, origin, title, timestamp, and stable locators to the model; redact credentials, tokens, unrelated names, and page boilerplate locally. Store hashes and citations, not private text, with a short expiry. The owner must configure per-origin rules; never infer which private sites are allowed.
- **missing:** A browser research orchestrator supporting multiple authenticated origins and public search; Local relevance extraction/redaction before relay upload; Citation objects that survive a follow-up without retaining page text; An expiry/forget endpoint and an owner-visible audit of which origins were read

### "“Find the latest invoice in my logged-in vendor portal, download the original PDF, rename it with the vendor and billing period, and file it in my taxes folder. Tell me if the amount or due date looks unusual.”"
- **useful because:** This joins the browser's authenticated reach to the Mac's filesystem: today the owner must manually find a private invoice, download it, interpret it, and organize it. The workflow preserves the original document while making the resulting local file and anomaly explanation immediately useful from a one-sentence pendant request.
- **path:** pendant → relay-realtime → browser → mac-planner → mac-vision → dashboard
- **model tier:** background for extraction, naming, and anomaly comparison; realtime only for a clarification such as which tax year folder
- **latency:** 30–90 seconds; provide a pendant status cue while the portal loads and a final spoken receipt
- **cost:** $0.01–$0.06 per invoice, dominated by PDF/OCR parsing; subsequent duplicate checks should be local and nearly free
- **security:** The PDF intentionally leaves the browser and is written only to the owner-selected local folder. Do not send the PDF or account credentials to the relay; parse amount/date locally where possible and send only normalized fields. Require an explicit configured destination and retain a receipt with source origin, hash, and local path. Never pay the invoice or email it.
- **missing:** A browser download action/result with a verified local file handoff; A local-agent artifact intake that can hash, rename, and move files atomically with undo; Owner-configured per-origin rules allowing document download and a destination-folder map; Invoice normalization and historical comparison without uploading document contents

### "“Check my recent online purchases and tell me which ones are still inside their return window, what the deadline is in my timezone, and where the return process starts. Put the deadlines on my calendar, but do not start a return.”"
- **useful because:** Return eligibility is scattered across authenticated order pages, delivery records, and retailer-specific policies. The browser can reach those sessions; the relay can normalize dates; the Mac can create reminders; and the pendant can surface only the deadlines that matter. This prevents lost refunds without taking an irreversible return action.
- **path:** browser → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Background extraction and date normalization; realtime only for a follow-up such as choosing a calendar or excluding an item.
- **latency:** 30–90 seconds for a batch of recent orders, then immediate spoken confirmation of created reminders.
- **cost:** About $0.02–$0.10 per batch, dominated by authenticated page reads; reminder creation and deadline arithmetic are local.
- **security:** Order pages may contain addresses and payment fragments. Extract only merchant, item, order date, delivery date, return deadline, and return URL; redact everything else and do not persist raw pages. Never click the final return or refund control. Calendar entries should contain minimal data and be undoable.
- **missing:** A retailer-agnostic order/return field extractor with per-origin selectors and fallback semantic extraction; A browser job that follows order links across multiple authenticated origins; Timezone-aware deadline calculation and duplicate-reminder suppression; Owner-configured calendar destination and per-origin read permissions

### "“Gather everything about my open support case from the logged-in support portal and related email, make a dated timeline of what happened and what they still need, then draft the reply in the portal without sending it.”"
- **useful because:** Support cases are split between a private ticket system and email, and the owner otherwise rereads long threads to reconstruct context. The browser supplies the inaccessible evidence; the model produces a bounded timeline and draft; the owner can inspect the exact unsent reply before committing.
- **path:** browser → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Background for thread retrieval, chronology, and draft composition; realtime for spoken status or a clarification about which case.
- **latency:** 45–120 seconds, with incremental progress after each source; drafting should complete before the owner needs to act.
- **cost:** $0.04–$0.20 per case, dominated by reading and summarizing long threads; cache only redacted message IDs and hashes.
- **security:** Support threads can contain account numbers and identity data. Keep raw messages on the Mac/browser side, redact secrets before model use, and show every source and proposed outgoing text. Fill the draft but stop before send, attachment, or escalation. Expire the working evidence after the case is closed.
- **missing:** Cross-origin case correlation between the support portal and authenticated mail; Thread-to-timeline extraction that preserves dates and quoted-message boundaries; A browser draft insertion operation with a hard unsent state and screenshot/evidence receipt; Configurable rules for which private mail labels/origins may be searched and what may be spoken

### "“Before my appointment, make me a private prep brief from the authenticated patient portal: upcoming appointment details, recent results, medication list, and unresolved messages. Highlight changes and questions I may want to ask, but do not interpret results or contact the clinic.”"
- **useful because:** The browser can access the portal session that the other nodes cannot, while the pendant makes a short, usable brief available without opening a laptop in the waiting room. It reduces missed messages and medication discrepancies without pretending to provide medical diagnosis or taking clinical action.
- **path:** browser → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Background extraction and structured change detection; realtime only to read a short owner-requested summary aloud.
- **latency:** 60–180 seconds for a portal with several sections; provide a completion alert and let the owner request individual sections.
- **cost:** $0.05–$0.30 per brief, dominated by page/PDF extraction; use local deterministic comparison for medication and result changes.
- **security:** This is highly sensitive health information. Keep source pages and PDFs on the Mac, redact identifiers before any model call, never speak the full brief automatically, and expire all working evidence. Require explicit per-origin authorization and a dashboard audit showing exactly which portal sections were read. No diagnosis, messaging, prescription, or appointment changes.
- **missing:** Portal-specific structured extraction for results, medications, appointments, and messages; On-device/local redaction and deterministic medication/result diffing; A sensitive-content policy that defaults to dashboard-only until the owner asks for spoken sections; Evidence expiry and deletion across browser sessions, relay, and Mac caches


## Changes it proposed to its own stack

### `integration` — Add an authenticated-browser artifact handoff: a browser download command returns a sandboxed file token and source metadata; the Mac agent consumes that token, atomically renames/moves the file, computes a hash, and emits a receipt plus undo operation. Keep document bytes on the Mac, and pass only normalized metadata to relay models.
- **owner gets:** The owner can say “file my latest invoice” and receive a trustworthy result instead of manually downloading, naming, and sorting a document from a private portal. It also makes the browser uniquely useful rather than merely another page reader.
- effort: Medium: browser extension download/result plumbing, local-agent artifact API, atomic filesystem operation, receipt/undo integration, and one end-to-end vendor fixture.  ·  risk: A portal may download the wrong attachment or a malicious file may be renamed into a sensitive folder. Recover by quarantining first, showing source URL/filename/size/hash, requiring a configured destination, and retaining an undo receipt; do not submit forms or send documents.
- cost: Negligible API cost; local disk and hashing only. One small background model call is optional for invoice field extraction.  ·  latency: Adds 1–5 seconds for download verification and hashing; portal load remains dominant.
- security: Improves security by keeping PDFs local and making origin, hash, destination, and undo visible. Requires strict per-origin download rules and no raw document upload.
- depends on: Owner-provided per-origin download permissions and destination-folder mapping; A real browser download action in the extension; Local-agent artifact intake and atomic move/undo primitives

### `browser-harness` — Add a local-only sensitive-session mode for authenticated browser jobs: the extension returns structured DOM/PDF fields and redacted diffs to the Mac, while raw medical, financial, or identity pages never enter relay model context. The owner can inspect a per-job origin/field audit and invoke explicit deletion.
- **owner gets:** They can safely use the pendant for high-value private portal tasks without turning the relay into a permanent copy of their health, financial, or identity records.
- effort: High: extension-side field extraction, local redaction, structured evidence capsules, deletion propagation, and dashboard audit UI.  ·  risk: Over-redaction could omit a necessary value; under-redaction could leak sensitive text. Recover with a local preview, field-level provenance, conservative defaults, and a manual retry that the owner explicitly enables. Keep raw data local and deletable.
- cost: Slightly higher local CPU/disk use; reduces token cost and cloud data exposure. No extra model call for deterministic extraction.  ·  latency: Adds roughly 1–3 seconds for local extraction/redaction; avoids relay upload latency.
- security: Strongly reduces sensitive data leaving the Mac, but requires careful extension permissions, encrypted local temporary storage, deletion tests, and audit integrity.
- depends on: Owner-defined per-origin sensitivity rules; Structured browser extraction primitives; Relay support for redacted evidence capsules and deletion acknowledgements


## What it asked for

_Nothing._
