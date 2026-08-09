# Harness derivation — browser-extension — round 256

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with one active YouTube tab (tabId 52), and POST /execute accepts browser actions; a malformed navigate failed because URL was not passed in the action shape, while prior browser_read_page succeeded.
  - evidence: GET /browser/status 200 at 2026-08-09T03:32:41Z; POST /execute response includes successful browser_read_page receipt for YouTube and failed navigate receipt.

## Capabilities it proposed

### "“I’m looking at a page—tell me what matters, and answer follow-up questions about it through my pendant.”"
- **useful because:** This makes the browser’s unique reach feel like a wearable ability rather than a hidden Mac feature: the owner can ask about an authenticated page without copying URLs or page text, receive a concise spoken answer, and ask “which one,” “when,” or “what changed?” in the same voice turn. It works on the live Safari tab (currently demonstrably online).
- **path:** browser → relay → pendant
- **model tier:** Realtime for the short conversational answer and follow-ups; use a cheaper background model only when the owner asks for a long page summary.
- **latency:** First answer under 5 seconds after the browser read; follow-ups under 2 seconds when the page evidence is already in the turn context.
- **cost:** Usually one browser read plus a small realtime response, roughly $0.01–$0.05 depending on page length and audio duration; the browser read and speech transport dominate latency, not page storage.
- **security:** Read-only by default. Never send HTML or screenshots to durable memory; pass only the needed extracted text to the model, redact secrets, and retain only existing short claims (24-hour browser TTL, 200-character cap) with provenance. The empty per-origin configuration must remain explicit until the owner supplies sites/categories; do not invent an allowlist.
- **missing:** A browser-to-realtime request envelope carrying tab/session provenance and a bounded text excerpt; A spoken “page context is stale—refresh?” interaction; Owner-supplied per-origin read/extract/redact/never-store and may-speak/must-not-speak configuration

### "“Watch the authenticated pages I name, and alert me only when a meaningful change requires my attention—even if my Mac is asleep.”"
- **useful because:** An always-awake relay can poll a logged-in Safari session on a schedule, compare structured findings rather than noisy page text, and deliver a short alert to the pendant’s offline_alert_inbox. This is the browser-specific version of the previously denied work-portal request: it uses the browser harness for the authenticated read, not Calendar/Mail briefing. The owner gets actionable changes without opening the site repeatedly.
- **path:** browser → relay → pendant → Mac
- **model tier:** Cheaper background model for change classification and deduplication; realtime is used only if the owner asks a spoken follow-up. The relay scheduler owns execution while Safari is available; when it is not, spool a missed check rather than pretending the page was checked.
- **latency:** No interactive latency requirement; a scheduled check should complete within 30 seconds of its cadence and alert within 10 seconds after a confirmed meaningful change.
- **cost:** One browser read and compact classifier per check, approximately $0.002–$0.02 per page check depending on frequency; most cost is repeated authenticated reads, so use ETags/section hashes where sites support them.
- **security:** Ship with an empty per-origin configuration. The owner must name the first sites and specify categories that may be spoken or persisted. Store only short host-keyed claims with URL/evidence, using the existing 24-hour browser TTL and 200-character cap; never persist page HTML, screenshots, credentials, or unchanged content. Alert payloads must be redacted and expire locally; a change notification should identify the page and reason, not quote sensitive text by default.
- **missing:** Authenticated browser page-watch scheduler that can reacquire the owner’s Safari session without opening a second login; Semantic section selectors/hash baselines and a meaningful-change classifier; Relay-to-offline_alert_inbox delivery with expiry, deduplication, and a missed-check status; Owner-provided per-origin and category policy

### "“Fill this web form from what I told you, but stop at the final review and read me exactly what would be submitted.”"
- **useful because:** This turns authenticated browser access into a practical assistant for applications, bookings, support requests, and settings without silently sending anything. The browser can fill many fields, while the pendant gives the owner a compact spoken diff (field, old value, new value, attachments and destination). The owner can then resume, edit, or abandon from Safari; no copy/paste is required.
- **path:** browser → pendant → relay → Mac
- **model tier:** Background model maps the owner’s supplied facts to fields and checks consistency; realtime speaks the final compact review and handles corrections. Use deterministic browser actions for filling, not model-generated clicks at submission time.
- **latency:** Drafting and filling a normal form within 15 seconds; review should be available within 3 seconds after the last field change.
- **cost:** Approximately $0.01–$0.08 per form depending on field count and document extraction; browser interaction and OCR/file inspection dominate. No charge for abandoned drafts after local cleanup.
- **security:** Do not submit, send, purchase, or commit the final mutation in this mode. Keep a field-level encrypted draft only for the session, redact secrets from model context, and preserve an undoable provenance receipt. Show destination, changed fields, attachments, and any validation warnings before offering a separate explicit submit action. The owner’s maximum-access policy remains intact: this is a review workflow, not a permission gate.
- **missing:** A form schema/extraction pass that identifies labels, required fields, validation errors, and attachment targets; A field-level draft store with automatic expiry and reliable cleanup after abandon; A compact pendant review renderer and a resume/edit protocol tied to the same tab; Submit as a separately addressable action after the review, rather than bundled into the fill plan

### "“Compare the options across my logged-in sites and tell me which one wins for my constraints, with evidence—not just a recommendation.”"
- **useful because:** A browser-only agent can inspect prices, availability, account-specific benefits, and terms that public search cannot see across multiple authenticated origins, normalize them, and speak a traceable comparison through the pendant. It stops at recommendation: no purchase or reservation. Each claim can be opened back to its source page and timestamp, which prevents stale logged-in data being mistaken for fact.
- **path:** browser → relay → pendant → Mac
- **model tier:** Cheaper background model extracts and normalizes the candidate rows; use realtime only to answer the owner’s constraint changes and narrate the winning trade-off.
- **latency:** Under 45 seconds for up to five sites and ten candidates; constraint follow-ups under 5 seconds if the extracted evidence is still fresh.
- **cost:** Roughly $0.03–$0.20 per comparison, dominated by authenticated page reads and model extraction across origins; persist compact rows rather than page bodies to control repeat cost.
- **security:** Requires the owner to explicitly provide origins and categories; ship empty rather than assuming shopping, banking, travel, or health sites. Never expose credentials or quote sensitive account details aloud unless the owner asks. Store only short, host-keyed claims under existing browser TTL/provenance rules; attach source URL, observed time, and confidence to every row. Any action that reserves, buys, or sends must remain outside the comparison plan.
- **missing:** Cross-origin session fan-out with per-origin extraction templates and failure isolation; A normalized evidence-table format with claim-level source links, timestamps, and confidence; Constraint-aware ranking that says “unknown” when a site could not be read; Owner-provided origins and category speech/retention policy

### "“Audit the accounts currently open in Safari and tell me which identity, organization, and security state each site is using—without changing anything.”"
- **useful because:** The owner cannot currently get a trustworthy inventory of which logged-in identity is active in each private web application. This would catch accidental use of a personal account for work, an expired session silently showing stale data, or a missing MFA/security warning before a consequential task. It is a read-only security and identity briefing, not a generic page summary.
- **path:** browser → relay → pendant → Mac
- **model tier:** A cheaper background model extracts account/org/security indicators from each authenticated origin; realtime is only needed to answer a spoken question about one origin.
- **latency:** Under 30 seconds for up to ten open tabs; a single-origin follow-up under 3 seconds.
- **cost:** Approximately $0.02–$0.10 per audit, dominated by private-page reads; retain only compact findings and hashes, not page text.
- **security:** This is highly sensitive metadata. Ship with no origins preconfigured; the owner selects tabs/origins explicitly. Speak only site name, account label, organization, and security warning unless asked for detail. Do not persist credentials, tokens, full email addresses, or screenshots. Findings expire quickly and carry source URL, observed time, and confidence.
- **missing:** DOM heuristics or site adapters for account identity, organization, and MFA/session indicators; A cross-tab audit result with explicit unknown/error states instead of guessing; A pendant summary format that avoids reading secrets aloud; Owner-supplied origins and speech/retention policy

### "“Build me a private case file from these logged-in sites: a dated chronology, the original source links, and the documents I need to review—then leave the bundle on my Mac without sending it.”"
- **useful because:** Today the owner must manually visit private portals, download or copy evidence, rename files, and reconstruct chronology. This would turn browser reach into a bounded, inspectable local dossier for an insurance issue, dispute, application, or project: sources remain traceable, duplicates are identified, missing documents are called out, and nothing is transmitted to a third party.
- **path:** browser → Mac → relay → pendant
- **model tier:** Background model performs OCR/metadata normalization, deduplication, and chronology extraction; realtime only answers questions or announces completion through the pendant.
- **latency:** A small case (up to 20 source pages/documents) in under two minutes; provide incremental progress and allow cancellation.
- **cost:** Approximately $0.05–$0.50 per case depending on OCR and document count; local storage and browser downloads dominate, while compact source metadata is cheap.
- **security:** The bundle is sensitive and must be local, encrypted, and explicitly named; no cloud upload, durable page-text memory, or automatic sharing. Preserve each source URL, timestamp, and content hash. Download only owner-selected file types, quarantine executable content, and report inaccessible or partially read sources instead of silently filling gaps.
- **missing:** A browser-to-Mac artifact transfer with safe filenames, content hashing, and cancellation; A local encrypted case-file workspace with manifest and source provenance; Document/OCR adapters that preserve page boundaries and dates; An owner-specified case scope and retention/cleanup date

### "“Before a site uploads a file or sends text, tell me what sensitive information is leaving my Mac and where it is going.”"
- **useful because:** The owner has no practical way to inspect the exact payload assembled by a private web form—especially hidden fields, attached PDFs, tracking parameters, or auto-filled text—before it leaves the device. A browser-side outbound receipt would expose destination, files, extracted sensitive categories, and the final text in a compact pendant/Mac review, helping the owner catch accidental disclosure while retaining maximum control over whether to continue.
- **path:** browser → Mac → pendant → relay
- **model tier:** Local deterministic inspection first (destination, bytes, filenames, form fields, metadata); a cheaper background model classifies likely sensitive categories. Realtime only narrates a compact warning or answers “what exactly is in that PDF?”
- **latency:** Under 1 second for metadata and destination; under 5 seconds for local document classification before the upload proceeds.
- **cost:** Near-zero API cost for metadata; roughly $0.01–$0.10 when document classification is needed. Local hashing and OCR dominate latency.
- **security:** Inspection must occur locally before network transmission where possible; do not upload the file to classify it. Never retain full payloads by default—store only a short receipt, destination, hash, and category counts. This is an observable advisory, not a blanket permission gate, consistent with the owner’s maximum-access policy; the owner can continue or cancel.
- **missing:** An extension/network boundary hook that exposes impending uploads and submitted field payloads before dispatch; Local file metadata/OCR and secret-category classifiers; A compact outbound receipt linked to the browser action and undo/cancel state; Owner-defined categories that should be highlighted or never spoken


## What it asked for

_Nothing._
## Its own summary

Established live browser reach: Safari is online with one active YouTube tab (tab 52), and POST /execute is the real command path. I recorded four new browser capabilities: wearable page companion, scheduled authenticated change watching into the already-granted offline alert inbox, staged form filling with a field-level final review, and cross-origin authenticated comparison with claim-level evidence. The recorder marked each as adjacent to existing backlog ideas, so I will not rephrase them next round; the useful next step is implementation of the missing browser/session and relay contracts rather than another proposal variant.

**Biggest unknown:** I still need the owner’s actual first authenticated origins and per-category rules (may speak / may persist / never read). The configuration should ship empty; without those inputs, any site-specific watcher or extraction template would be invented. Engineering gaps remain: authenticated session reacquisition/page-watch scheduling, semantic change baselines, field-level draft/review state, and claim-level cross-origin comparison.

