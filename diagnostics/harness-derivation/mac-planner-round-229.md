# Harness derivation — mac-planner — round 229

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m at my desk—make a handoff packet from what I’m looking at, what I said to remember, and the next calendar deadline.”"
- **useful because:** This turns a fleeting pendant bookmark into a durable, reviewable work packet instead of losing the connection between the owner’s spoken thought and the authenticated browser page. It works because the pendant supplies the moment and speech, the browser supplies session-bound evidence, the Mac supplies local files/calendar, and the relay joins them with one timestamped job.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Realtime for the short spoken acknowledgement; a cheaper background model extracts page title/claims and produces the packet. No expensive model is needed for file assembly.
- **latency:** Acknowledge the bookmark in under 2 seconds; collect browser/Mac context in under 15 seconds; packet is available within 30 seconds.
- **cost:** Roughly $0.01–$0.04 per packet, dominated by summarizing page text; local metadata and file assembly are negligible.
- **security:** Authenticated page contents and the spoken note leave the browser/Mac only to the relay/model unless redaction is applied. Default to title/URL plus a short selected excerpt, redact credentials and tokens, and make full-page capture an explicit owner policy. Do not silently upload arbitrary page bodies.
- **missing:** A relay primitive that atomically correlates a pendant bookmark, browser snapshot, and Mac context under one job id; Browser command for bounded, redacted page evidence export; A packet renderer that writes Markdown/PDF and links the next calendar deadline

### "“Watch this authenticated browser tab until the deadline, and interrupt me on the pendant only if something changes in a way that needs action.”"
- **useful because:** The owner gets attention filtering rather than another inbox. The browser keeps the private session, the relay performs cheap change detection while the Mac may be asleep, and the pendant delivers only actionable deltas; when action is needed, the Mac can reopen the exact tab without the owner searching for it.
- **path:** browser → relay → pendant → mac-planner → dashboard
- **model tier:** Cheap background polling/diff model for every check; realtime only when the owner asks what changed or dictates a response. Use deterministic selectors and hashes before invoking a model.
- **latency:** Poll cadence chosen by the owner (for example 5–15 minutes); alert delivery under 10 seconds after a detected change; no foreground Mac interaction during monitoring.
- **cost:** About $0.002–$0.02 per check depending on page text size; most checks should be hash/selector comparisons with no model call.
- **security:** Never send passwords, cookies, or full authenticated HTML to the relay. Keep extraction in the browser extension, transmit only redacted structured fields/diffs, enforce expiry and an explicit stop time, and expose the watch list in the dashboard. Opening or submitting a response must be a separate action.
- **missing:** A browser page-watch scheduler with selectors, hashes, expiry, and per-watch redaction; Relay-side alert deduplication and quiet-hours/priority routing into the existing pendant inbox; A Mac action that reopens a stored browser session and presents the diff without submitting anything

### "“Take the report I’m viewing in the browser, save the right download into my project folder, verify it, and tell me exactly what changed.”"
- **useful because:** Authenticated downloads are a common failure point: the wrong tab, an HTML login page, or a duplicate filename can look like success. The browser finds the current report, the Mac stages it atomically, computes/records its hash and source URL, and the pendant gives a short receipt. This is an actual cross-surface mutation, not merely a summary.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Deterministic browser/download and hashing path; a small model is used only to interpret ambiguous report names or explain the receipt.
- **latency:** Preview in under 5 seconds; download, verify, and atomic handoff in under 30 seconds; spoken receipt immediately after commit.
- **cost:** Under $0.01 per invocation; local hashing and transaction dominate wall time, not API calls.
- **security:** Keep authenticated content local where possible, transmit only metadata/hash unless the owner explicitly requests extraction, block path traversal and overwrites by default, and record source URL, timestamp, size, and SHA-256. The owner’s existing maximum-access policy means this should still expose a dry-run preview rather than guessing.
- **missing:** A browser download result that returns the concrete downloaded file identity and source metadata; A Mac transaction mode that stages an existing browser download into an allowlisted project root with hash verification; A compact cross-surface receipt queryable from the pendant

### "“Before I send this document, check the recipient, the attachment, and the browser form for accidental secrets, then read me a short send preview.”"
- **useful because:** The owner gets a meaningful last-mile safety check across surfaces: the Mac can inspect the local attachment and form fields, the browser retains the authenticated session, and the pendant gives a hands-free preview before any irreversible send. It catches wrong-recipient, stale-file, and credential-leak mistakes that no single node can see.
- **path:** mac-planner → browser → relay → pendant → dashboard
- **model tier:** Deterministic recipient/domain/attachment/hash checks first; a privacy classifier runs locally or on redacted text; realtime is used only to answer the owner’s spoken question. Sending remains a separate explicit action.
- **latency:** Preview in under 8 seconds for ordinary documents; under 20 seconds if a bounded text extraction/classification is needed.
- **cost:** $0.005–$0.03 per preview, dominated by document classification; metadata-only previews are near-zero.
- **security:** Never upload whole documents or secrets by default. Redact tokens, passwords, and hidden form fields; show the exact recipient, attachment hash/size, and detected sensitive categories. The send action must not be bundled into the preview and must obey the owner’s runtime policy configuration.
- **missing:** A browser inspection command for form recipients, attachment names, and hidden-field redaction; A local bounded document secret scanner exposed as a structured Mac action; A cross-surface preview receipt and explicit send continuation token

### "“Check whether this invoice is the one I’m expecting before I pay it: compare the browser page with my recent mail, calendar, and local project files, and tell me only about discrepancies.”"
- **useful because:** The owner gets a cross-surface fraud and mistake check, not a generic summary. The browser supplies the authenticated invoice, Mail and Calendar establish whether the transaction was expected, and the Mac supplies the local purchase context. The result is a discrepancy list with evidence and uncertainty, without making a payment.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Deterministic extraction and matching of vendor, amount, dates, account suffixes, and document hashes first; a cheaper reasoning model adjudicates conflicts. Realtime is only for the spoken verdict.
- **latency:** Initial checks in 10 seconds; full comparison in under 45 seconds; no automatic payment or form submission.
- **cost:** Approximately $0.01–$0.06 per check, dominated by extracting and comparing document text; metadata-only checks cost much less.
- **security:** Financial documents and mail are highly sensitive. Keep raw content on the Mac/browser where possible, send only extracted fields and redacted evidence, never expose full account numbers, and require a separate owner action for any payment or submission.
- **missing:** A cross-source evidence joiner that aligns browser, Mail, Calendar, and local-file entities by vendor/date/amount; Bounded local extraction of invoice fields and redacted supporting snippets; A discrepancy-specific spoken/UI result with confidence and links back to each source

### "“Give this website only the minimum information it needs from my Mac, keep a record of exactly what was shared, and remove the temporary copy when the task is done.”"
- **useful because:** The owner can use authenticated services without turning every browser upload into a permanent data leak. The browser identifies the requested fields, the Mac derives a minimized temporary artifact, the relay records the purpose and expiry, and cleanup happens after a verifiable completion signal.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Deterministic schema/field minimization and hashing; a small model resolves ambiguous field requirements. Realtime is only for explaining the preview.
- **latency:** Preview in under 10 seconds; artifact creation and upload handoff in under 30 seconds; cleanup receipt within 10 seconds of task completion.
- **cost:** About $0.005–$0.03 per task; local transformation and verification dominate.
- **security:** The system must never infer permission to share more than the site requests. Show the exact fields, destination, retention deadline, and artifact hash before upload; keep a local audit receipt; clean up on timeout as well as success; never claim deletion if the remote site gives no deletion acknowledgement.
- **missing:** Browser-side structured field/schema inspection for the active form; A Mac minimization transformer for approved files and structured records; Relay-managed expiry, cleanup, and proof-of-completion state across browser and Mac

### "“Ask me on the pendant before a high-impact browser or Mac action, and accept the action only when I physically press the button on the pendant.”"
- **useful because:** The owner gets a confirmation channel that cannot be accidentally triggered by a browser click, open Mac window, or injected voice text. The relay holds the action, the Mac/browser prepare a deterministic preview, and the worn device supplies a physical presence signal tied to that exact preview.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** No expensive model is needed for authorization; use deterministic action hashes and receipts. Realtime only explains the preview aloud.
- **latency:** Preview within 5 seconds; pendant prompt within 2 seconds; action dispatch within 3 seconds of the button press.
- **cost:** Below $0.01 per authorization; cryptographic verification and transport are negligible.
- **security:** A plain GPIO press is not cryptographically trustworthy against a compromised host. This needs a secure element or hardware-backed key, nonce-bound action hashes, expiry, replay protection, and a visible local indication. The owner must choose which action classes require it; it must never silently authorize an altered action.
- **missing:** Hardware-backed signing or a secure element on the pendant; Relay protocol for nonce-bound physical approvals and replay rejection; Mac/browser execution adapters that expose a stable action hash before dispatch; Owner-configurable high-impact action classes and an approval audit view


## What it asked for

_Nothing._
