# Harness derivation — browser-extension — round 123

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with 3 tabs; one is the owner's authenticated Gmail inbox (tab 901464), and POST /execute browser_list_tabs successfully returns tab metadata and receipts. The prior 'tabCount=0' blocker is no longer true.
  - evidence: GET /browser/status at 2026-08-07T17:40:14Z and POST /execute browser_list_tabs at 17:40:23Z

## Capabilities it proposed

### "“Pause this browser task and bring me back to exactly where I was tomorrow.”"
- **useful because:** Long authenticated forms and research threads survive interruptions instead of forcing the owner to rediscover tabs, scroll position, field values, and intent. It deliberately stages only reversible work and never submits.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime model only for the short voice command and confirmation; a cheaper background model normalizes the page state and generates the resume summary.
- **latency:** Acknowledge in under 2 seconds; snapshot and persist the staged state within 10 seconds; scheduled resume notification runs in the background.
- **cost:** Roughly $0.01–$0.05 per pause/resume, dominated by page extraction and summary tokens; storage and routine execution are negligible.
- **security:** Authenticated URLs, visible form values, and page excerpts leave Safari for the relay/Mac agent. Encrypt staged state, redact password/payment fields, expire it by default, and stop before any submit/send/purchase. Resuming must show a before/after diff, not silently mutate the page.
- **missing:** Durable resumable browser-task record containing tab/session identity, URL, scroll/DOM anchors, redacted field state, and owner intent; Extension support for restoring a tab and scroll/field draft from a versioned snapshot; A scheduled reminder that can reopen the correct Safari session and speak a concise resume brief

### "“Save this private page as a memory card I can ask about from the pendant later.”"
- **useful because:** The owner can turn a logged-in invoice, policy, recipe, or research page into a durable, cited answer without copying text manually. Later the pendant can answer “what was the cancellation deadline on that page?” and point back to the exact source.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheaper background model extracts title, claims, dates, entities, and a short quote; realtime is used only when the owner later asks a spoken question.
- **latency:** Capture acknowledgement under 2 seconds, card ready within 15 seconds, later spoken lookup under 3 seconds when indexed.
- **cost:** $0.01–$0.08 per card depending on page length; embedding/indexing and encrypted local storage dominate less than model extraction.
- **security:** This intentionally stores private authenticated content. Keep the original URL and evidence hash, encrypt excerpts, default to 30-day expiry, redact secrets and authentication tokens, and expose deletion from the pendant/dashboard. Never claim a stale card is current; say when it was captured.
- **missing:** A user-invoked browser-to-memory-card route that extracts bounded semantic facts plus quoted evidence and provenance; A private-card index retrievable by pendant voice with source freshness and deletion/expiry semantics; A consented content-classification/redaction pass for pages containing credentials, payment data, or health information

### "“I can’t read this right now—give me a one-minute spoken digest of the private page I’m on, and remind me only if it contains a deadline.”"
- **useful because:** This is the highest-value browser-only moment: the extension can see the owner’s authenticated page while the pendant is the only practical output channel when their hands and eyes are occupied. It converts dense portals, notices, and documents into an immediate, cited audio brief and avoids noisy reminders.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use a cheap background summarizer for extraction, deadline/entity detection, and audio generation; use realtime only to acknowledge the request and answer follow-up questions.
- **latency:** Acknowledge immediately; begin playback within 8 seconds for ordinary pages, with progressive chunks for long pages; deadline reminder scheduling completes within 20 seconds.
- **cost:** About $0.02–$0.10 per digest, dominated by page text and speech synthesis; reminders and queue storage are trivial.
- **security:** Private page text and any detected deadlines transit the relay. Limit extraction to the active tab and bounded visible/main content, strip scripts and secrets, retain audio briefly, cite URL/title/timestamp in the dashboard, and do not infer or schedule a high-impact commitment without stating the detected date and timezone.
- **missing:** A one-shot browser action that returns bounded main-content text plus heading/link evidence and tab provenance without changing the active tab; A streaming text-to-speech queue addressed to the pendant with pause/resume and expiry; Deadline detection with timezone normalization and deduplicated reminder creation, including a clear “no deadline found” result

### "“Make this logged-in page readable while I’m walking, and let me ask follow-up questions about the simplified version.”"
- **useful because:** Dense authenticated portals and documents become usable hands-free: the browser creates a temporary reader representation preserving headings, tables, links, and warnings, while the pendant speaks it in sections and answers questions against the same page snapshot. This is accessibility and comprehension, not merely summarization.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** A cheaper model performs structure extraction and table/heading segmentation; realtime handles interruption, navigation (“next section”), and short follow-ups.
- **latency:** First section in 5 seconds, subsequent sections streamed; follow-up answers under 2 seconds from the retained snapshot.
- **cost:** $0.02–$0.12 per page depending on length and table complexity; speech generation dominates.
- **security:** Only the active authenticated tab is read. Preserve source links and page timestamp, strip scripts and hidden fields, avoid retaining the original content beyond the session, and explicitly distinguish extracted text from model interpretation.
- **missing:** A browser-side accessibility extraction mode that preserves semantic structure, tables, warnings, and link targets; A session-scoped page snapshot addressable by follow-up voice turns; Pendant playback controls for section navigation and interruption

### "“Take the tracking number, invoice total, or appointment address from this private page and put it into the Mac app I name.”"
- **useful because:** The browser can see values behind logins that ordinary Mac automation cannot safely locate. The owner gets a precise browser-to-desktop handoff instead of retyping sensitive structured data, while the page citation and extracted value remain visible for verification.
- **path:** pendant → browser-extension → mac-planner → mac-terminal → relay-realtime
- **model tier:** Cheap extraction model identifies the requested field and validates its type; realtime is only needed to resolve an ambiguous field or app name.
- **latency:** Extract and preview in 3 seconds; write to the named Mac destination within 8 seconds after the owner’s explicit voice command.
- **cost:** $0.005–$0.04 per handoff; extraction and validation tokens dominate, with negligible local execution cost.
- **security:** Values may be financial, medical, or identifying. Never use broad clipboard history: pass a one-shot typed payload directly to the named app, show source URL/field/value, redact it from logs, and provide immediate undo. Refuse only when the requested destination is ambiguous, not as a general confirmation gate.
- **missing:** Typed browser field extraction with source locator and confidence; A one-shot private browser-to-Mac payload channel that avoids persistent clipboard/history exposure; Destination adapters for common Mac apps with typed insertion and undo

### "“Download the document behind this logged-in page, file it in the right local project folder, and tell me what it is without uploading it anywhere.”"
- **useful because:** Authenticated invoices, statements, tickets, and policy PDFs can be turned into useful local records in one spoken request. The browser supplies access, the Mac supplies filesystem organization, and the pendant confirms the exact file and destination hands-free.
- **path:** pendant → browser-extension → mac-planner → mac-terminal → relay-realtime
- **model tier:** A background model classifies the document and proposes a filename/folder from local project context; realtime gives the short status response only.
- **latency:** Show the proposed filename and destination within 5 seconds; download and local filing within 15 seconds for ordinary documents.
- **cost:** $0.01–$0.08 per document for classification and metadata extraction; local transfer costs are negligible.
- **security:** The document is private and must remain on the Mac. Use a direct browser-to-local download, never relay file bytes, restrict extraction to metadata unless requested, preserve the source URL and hash, avoid overwriting existing files, and make filing undoable.
- **missing:** An extension download handoff that returns a local file handle without proxying document bytes through the relay; A local document classifier that maps content to the owner’s project folders and detects duplicates; A reversible file-placement action with collision-safe naming and source provenance


## What it asked for

_Nothing._
