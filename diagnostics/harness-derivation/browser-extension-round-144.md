# Harness derivation — browser-extension — round 144

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Find every logged-in account deadline or expiring offer I need to act on this week, compare it with my calendar, and alert me only when there is a real conflict.”"
- **useful because:** This turns private browser access into prevention rather than another page summary: the system can notice a renewal window, expiring credit, appointment cutoff, or filing deadline across authenticated sites, test it against Calendar, and deliver one concise spoken alert through the pendant. No single Mac, browser, or relay node can do the whole job.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Background/cheap model for page extraction and date normalization; expensive realtime tier only for the owner's follow-up question or ambiguous conflict.
- **latency:** Initial scan 30–90 seconds across configured origins; alert delivery under 5 seconds after a newly detected deadline. Weekly scheduled scans should not occupy realtime.
- **cost:** Usually <$0.03 per scan with capped extraction; model cost is dominated by authenticated page text, not the calendar join. A realtime clarification is a normal voice turn.
- **security:** Requires an explicit, inspectable origin registry and per-origin read/redact/never-store rules; do not invent sites or categories. Persist only normalized deadline, source URL, evidence hash, and expiry, not page text. Alert wording must avoid speaking sensitive details in public. No purchase, renewal, or submission is performed.
- **missing:** Account/origin registry with owner-supplied origins; Deadline/expiry extraction and confidence model over browser results; Calendar conflict join and deduplication; Relay-to-offline_alert_inbox delivery with quiet hours

### "“Build me a private evidence packet for this dispute: pull the relevant receipt/order page from my logged-in account, find the matching policy, and give me a cited timeline I can review before I contact anyone.”"
- **useful because:** When a charge, delivery, warranty, or subscription is wrong, the owner currently has to hunt through authenticated pages and public policies manually. Browser sessions supply evidence nobody else can reach; the relay can normalize it; the Mac can save a reviewable packet; the pendant can explain the result while the owner is away. It stops before sending a complaint or contacting a merchant.
- **path:** browser-extension → mac-planner → relay-realtime → mac-terminal → unified
- **model tier:** Cheap background extraction for receipts, dates, amounts, and policy clauses; use the expensive model only to resolve contradictions and answer the owner's spoken questions.
- **latency:** Two to three minutes for a packet, with progressive spoken updates after each source. Review should be available even if Safari later goes offline.
- **cost:** Roughly $0.05–$0.20 per packet depending on page count; browser extraction and OCR dominate, while cited synthesis is a small fraction.
- **security:** Source pages may contain addresses, payment identifiers, and private correspondence. Require owner-supplied per-origin rules, redact secrets before relay storage, keep raw page text local and ephemeral, hash each citation, and show the exact proposed message without sending it. Never infer that a policy applies when evidence is missing.
- **missing:** Evidence-packet schema with source URL, timestamp, locator, quote hash, and confidence; Local encrypted artifact store and pendant-safe spoken redaction; Policy matching across authenticated and public origins; A review UI that supports approve/edit/export, but has no send side effect

### "“Answer questions about the logged-in pages I have open, but keep the page text on my Mac: tell me the answer, confidence, and exactly where on the page you found it.”"
- **useful because:** This is the browser's strongest unique role with a materially better privacy boundary: the owner can ask about bills, work portals, or private messages without shipping whole pages to the relay. Safari extracts only the minimum matching DOM spans locally, the Mac model answers with those spans, and the pendant speaks a short answer plus provenance. It works even when the owner is not willing to create a persistent watch or account registry.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → unified
- **model tier:** Local Mac model for retrieval and answer generation; realtime model receives only a redacted answer/citation when a spoken response is needed. Never use realtime for raw-page processing.
- **latency:** 1–4 seconds for one active page, under 10 seconds for up to five explicitly selected tabs. If local inference is unavailable, say so rather than silently falling back to cloud.
- **cost:** Near-zero API cost when the Mac model is available; occasional relay voice turn cost remains. CPU and battery use are the dominant cost.
- **security:** The extension must perform DOM-region selection and redaction before any result leaves Safari; credentials, payment fields, health data, and messages need conservative defaults. Store only a query hash and citation locator, not page text. The owner must explicitly select tabs or the active page; no background crawl.
- **missing:** A local-only browser extraction/QA endpoint with a hard no-cloud mode; Mac-side retrieval over returned DOM spans and citation locators; Extension redaction/classification applied before result serialization; A spoken response format that names origin/title and confidence without leaking the quote

### "“Use the one-time code I just received to finish signing me in to the page I’m looking at, but never show or store the code outside the Mac and never reuse it.”"
- **useful because:** Today the owner must copy a transient MFA or invitation code between devices, and a normal voice transcript or browser result can expose it. With the pendant as the physical presence signal, the Mac as the only secret-handling surface, and Safari as the session holder, the hive can complete a login without the relay learning the code or persisting it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** No expensive model for the secret itself. Realtime only interprets the owner's intent and confirms the target origin; deterministic local code capture, validation, and typing do the rest.
- **latency:** Under 5 seconds after the code arrives or is spoken. Abort on origin/tab change, timeout, or code mismatch.
- **cost:** Near-zero API cost; implementation cost is an extension/Mac protocol and secure memory handling. No page text or secret should be sent to the cloud.
- **security:** The code must be held only in volatile Mac memory, excluded from logs, receipts, model context, analytics, and speech transcripts; bind it to an origin, tab, and one attempt, then wipe it. Require an explicit physical pendant gesture to arm and never use this for passwords or recovery codes. The owner reviews the destination origin before typing.
- **missing:** A hardware-presence/one-time-secret channel between pendant and Mac; Origin-bound volatile secret vault and zeroization path; Safari extension operation that types a secret without returning it in results; A relay intent that carries only an opaque request and completion status

### "“Audit the security settings of my logged-in accounts, tell me which sessions, recovery methods, permissions, or API keys are stale or risky, and prepare a prioritized fix list without changing anything.”"
- **useful because:** The browser can reach security consoles behind existing logins while the relay and Mac can correlate findings across accounts. The owner gets a single spoken, prioritized posture report instead of manually visiting every account-security page, with exact evidence and no destructive remediation. This is a genuinely different use of private browser reach: discovering invisible account exposure rather than watching ordinary page changes.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Cheap deterministic extraction and rules for dates, scopes, and known risk indicators; a slower model summarizes conflicts and prioritizes. Realtime is reserved for the owner's follow-up questions.
- **latency:** 5–10 minutes for an initial audit of owner-selected origins; incremental rechecks can run overnight. Spoken result in under 10 seconds once the packet is ready.
- **cost:** Approximately $0.10–$0.50 per multi-account audit, dominated by authenticated page extraction and synthesis; no cost for accounts the owner excludes.
- **security:** This is highly sensitive. Ship empty origin/category policy until the owner configures it; never persist tokens, secrets, full security-page text, or backup codes. Store only redacted findings, evidence hashes, and timestamps. Do not revoke sessions, rotate keys, or modify MFA; the output is advisory and review-only.
- **missing:** Security-console discovery recipes per owner-supplied origin; Normalized account-risk schema and deterministic stale-session/API-key rules; Cross-origin deduplication and evidence retention policy; A local review/export surface for remediation steps

### "“Request and organize my personal-data exports from the logged-in services I choose, keep the archives on my Mac, and give me a spoken inventory of what each service disclosed.”"
- **useful because:** The owner cannot today coordinate data-export workflows across authenticated services without repeatedly finding the right privacy pages, waiting for asynchronous export emails, downloading archives, and organizing them. Safari can operate inside logged-in accounts, the Mac can download and index locally, the relay can track long waits, and the pendant can report progress. It stops before accepting terms, deleting data, or sending anything beyond the export request the owner explicitly reviews.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Background model for classifying export contents and producing an inventory; deterministic local code handles downloads, archive hashing, and file placement. Realtime is only for spoken progress or clarification.
- **latency:** Setup in 2–5 minutes per service; asynchronous export monitoring can run for days without an open voice session. A completion alert should reach the pendant within one polling interval.
- **cost:** Typically <$0.10 per service for classification; storage and download bandwidth dominate. Large archives must remain local and never enter model context wholesale.
- **security:** Exports may contain an entire personal history. Require an explicit owner-selected origin list, encrypted local destination, retention/expiry policy, malware-safe archive handling, and a manifest-only relay record. Show the exact request and destination before any irreversible submission; do not automatically share, delete, or upload the archive.
- **missing:** A durable browser workflow that can cross the request/download/email-wait phases; Encrypted local export vault with quotas, hashes, and archive scanning; A local classifier that inventories files without uploading them; Relay job tracking plus offline_alert_inbox completion delivery; Per-origin export recipes supplied by the owner rather than hardcoded


## What it asked for

_Nothing._
## Its own summary

Round 144 produced three distinct browser capabilities: (1) cross-origin authenticated deadline/expiry detection joined against Calendar and delivered through the pendant alert inbox; (2) a cited, review-only dispute evidence packet assembled from private receipts and public policy; and (3) local-only Q&A over explicitly selected logged-in pages, returning confidence and provenance without sending raw page text to the relay. I also verified the granted browser enqueue tool is still unusable: its list_tabs value is ambiguous between browser_list_tabs and browser_list_sessions, so no command was sent.

**Biggest unknown:** I still need the owner to supply an explicit origin registry and privacy rules (which sites may be read, what may be spoken, and what may be persisted), and I need a functioning narrowly-spelled browser command path plus confirmation of whether local Mac inference exists. Without those, authenticated browser automation remains demonstrable but not safely productized.

