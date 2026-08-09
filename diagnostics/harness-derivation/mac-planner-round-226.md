# Harness derivation — mac-planner — round 226

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness** — AI Pendant Agent has Accessibility and Screen Recording trusted, synthesized input verified, and 3 durable browser sessions are visible; current foreground is loginwindow. Browser inspection is currently ambiguous between action:browser_inspect and POST /browser/inspect, so the granted browser_tabs operation cannot resolve that call.
  - evidence: mac_readonly_inspect foreground_app/running_apps returned GET /observe HTTP 200 with accessibility.trusted=true, screenRecording=true, eventsPost=true; browser_tabs call returned unresolved ambiguity.

## Capabilities it proposed

### "After I finish an online purchase, quietly save the confirmation and delivery/return deadlines, create the right reminders, and let me ask the pendant “what did I order and when can I return it?”"
- **useful because:** Browser sessions contain confirmations that are otherwise lost in tabs and email. The browser can observe the authenticated order page, the Mac can create a durable local receipt and reminders, and the pendant provides a hands-free query later without exposing the whole page aloud.
- **path:** browser-extension → mac-planner → relay → pendant
- **model tier:** background extraction/classification; realtime only for the owner's later spoken lookup
- **latency:** Detect a confirmation within 15 seconds, persist a redacted receipt within 5 seconds, and create reminders in under 10 seconds.
- **cost:** $0.01–$0.06 per confirmation when OCR/LLM extraction is needed; structured pages should use no model call.
- **security:** Order IDs, addresses, prices, and account names are sensitive. Keep raw page content on the Mac, send only a redacted structured record to relay, hash the source URL, and never speak full addresses or payment details without an explicit request. Reminder creation must be visible in the local receipt.
- **missing:** A browser page classifier for purchase confirmation, delivery estimate, and return-policy fields across sites; A redaction/normalization schema for order records and deadlines; A durable local receipt store linked to reminder IDs and browser command IDs; A spoken retrieval route that returns only the minimum requested fields

### "While I use the browser, warn me on the pendant if a page is about to submit sensitive information—my address, an account number, or a long pasted text—and say which site and which fields are leaving the Mac."
- **useful because:** The browser has authenticated context and the pendant is the only surface that can interrupt without stealing the screen. This catches accidental oversharing at the moment it matters, including paste-heavy forms that ordinary password warnings miss.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** A small local classifier for field types and deterministic pattern matching; realtime model only for ambiguous text classification or the owner's follow-up question
- **latency:** Inspect a form submission in under 150 ms locally; deliver a concise pendant alert within 1 second; never block normal browsing unless the owner explicitly enables blocking.
- **cost:** Near-zero for deterministic field/pattern checks; $0.001–$0.01 for ambiguous classification, with no page body sent upstream by default.
- **security:** The scanner must process values locally and transmit only site origin, field categories, and a redacted preview. Do not log raw form values. A warning is advisory by default because owner approval policy is not configured; any future blocking mode must be an explicit owner setting.
- **missing:** A browser pre-submit hook that reports field labels/types and redacted value fingerprints before navigation; A relay event type for privacy warnings with deduplication and severity; A pendant alert renderer that can interrupt audio safely without persisting sensitive text; A Mac/browser settings surface for choosing warn-only versus owner-configured blocking

### "When I say “what am I looking at?”, use the current Mac window and browser tab to give me a short, source-grounded answer; if I ask a follow-up, point to the exact page or app and offer to open it, without changing anything automatically."
- **useful because:** The pendant has no display and the relay cannot see authenticated desktop context. Combining a live Mac foreground snapshot with the browser's current page gives the owner an eyes-free understanding of whatever is in front of them, instead of forcing them to read or dictate a URL.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime for the spoken answer and follow-up; deterministic extraction first, with a cheaper summarizer for long pages and no model call for simple titles/URLs
- **latency:** Return the visible app/tab identity within 700 ms and a grounded summary within 2 seconds; never perform an action unless the owner explicitly asks.
- **cost:** $0.005–$0.03 per question depending on page length; structured title/heading responses can be essentially free.
- **security:** Authenticated page text must remain on the Mac/browser bridge unless needed for the answer; redact passwords, form values, and hidden page content. Include source title/domain and a freshness timestamp in the spoken response. Opening a URL/file should produce a local action receipt.
- **missing:** A unified read-only snapshot that atomically captures foreground app, browser tab, visible text/heading and timestamp; A relay grounding envelope that binds every answer to snapshot IDs and source URLs; A browser extraction mode limited to visible content rather than full DOM/session data; A spoken answer contract that refuses to infer when the snapshot is stale or inaccessible

### "When I say “preserve this page,” capture a tamper-evident record of the authenticated browser page—including the visible rendering, URL, timestamp, and relevant network metadata—store it locally, and give me a short receipt I can later prove has not changed."
- **useful because:** A normal bookmark or saved URL is not evidence: pages, prices, policies, and account statements change or disappear. This would let the owner preserve a delivery promise, policy, receipt, or dispute record at the moment they saw it, while keeping the sensitive page on the Mac.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** No model for capture or hashing; background model only to label the artifact and extract a human-readable summary after the cryptographic record is complete.
- **latency:** Acknowledge the spoken command within 1 second and finish capture within 5 seconds; the owner must receive a durable receipt even if relay connectivity drops.
- **cost:** Essentially zero model cost; local storage and hashing dominate. Optional summarization should cost under $0.02 per artifact.
- **security:** Authenticated pages may contain passwords, addresses, and financial data. Keep the raw artifact encrypted on the Mac, redact secrets from any relay receipt, use content hashes and a signed timestamp, and provide explicit retention/deletion controls. Network metadata must be minimized because it can reveal account and session details.
- **missing:** A browser capture primitive that records visible pixels plus DOM/text and response metadata without executing page actions; An encrypted, append-only local evidence store with SHA-256 manifests and deletion audit records; A relay receipt format that binds pendant utterance, capture time, source origin, and artifact hash without uploading raw content; A later verification command that recomputes the hash and reports exactly what changed

### "When I open an invoice, booking, or delivery page, compare it with the matching email and calendar entry and tell me if the amount, date, vendor, or destination conflicts before I act on it."
- **useful because:** Fraud and booking mistakes often look plausible in one surface but contradict a confirmation elsewhere. The browser has the live authenticated page, while Mac Mail and Calendar hold independent evidence; the pendant can surface only the discrepancy instead of making the owner manually cross-check three apps.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background structured matching first; a small model only for ambiguous vendor/entity matching; realtime for the short spoken discrepancy report.
- **latency:** Return a preliminary match in 2 seconds and a full discrepancy report within 6 seconds; never modify a booking, email, or calendar entry automatically.
- **cost:** $0.01–$0.05 per comparison when fuzzy matching is needed; exact IDs and dates should be handled without a model.
- **security:** Mail bodies, booking numbers, addresses, and amounts are sensitive. Perform extraction on the Mac, send only normalized discrepancy fields to the relay, redact account and payment identifiers, and preserve source links locally for audit.
- **missing:** A bounded cross-source matcher joining a browser page with Mail and Calendar records by vendor, amount, date, and identifier; A Mac-side extraction contract that returns only the minimum matching fields and confidence; A relay event type for contradiction findings with source references and expiry; A pendant response format that distinguishes confirmed conflict from uncertain match

### "Before I upload a file in the browser, inspect it for hidden metadata and sensitive content—EXIF location, document authors, comments, tracked changes, hidden spreadsheet tabs, and embedded files—and offer me a cleaned copy without altering the original."
- **useful because:** Uploading a document can disclose far more than its visible page. The browser knows when the file is about to leave an authenticated session, and the Mac can inspect and sanitize the actual local file; the pendant can warn hands-free before the irreversible upload.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Local deterministic parsers for metadata and archive structure; background model only for ambiguous sensitive-content classification; realtime only for a concise warning or follow-up.
- **latency:** Metadata-only checks under 1 second, full document scan under 5 seconds, and a cleaned-copy preview under 10 seconds. Never replace the original silently.
- **cost:** Usually zero model cost; $0.01–$0.08 for ambiguous text classification in long documents. Local CPU and temporary storage dominate.
- **security:** The file must remain on the Mac during inspection. Never upload the original or extracted contents to the relay. Store sanitized copies with explicit names, preserve a local audit of removed fields, and warn that semantic secrets can evade automated detection.
- **missing:** A browser upload interception event exposing the selected local path and destination origin before submission; A Mac sandboxed file-inspection and sanitization service for common office, PDF, image, and archive formats; A diff/manifest preview showing exactly which metadata or content was removed; A pendant warning protocol that can defer or cancel the browser upload without pretending the current owner-approval policy exists


## What it asked for

_Nothing._
