# Harness derivation — mac-planner — round 239

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-permissions** — Live ops status now reports AI Pendant Agent ready with Accessibility and Screen Recording granted, all listed Automation grants present, Safari browser bridge online, and relay reachable. This supersedes the stale earlier denial for this host.
  - evidence: GET /ops/status returned ready:true, accessibility.trusted:true, screenRecording.granted:true, requiredMissing:[], relay.reachable:true; GET /browser/status returned Safari tab 3186198 online.

## Capabilities it proposed

### "“I’m done for today—remember exactly what I was doing and put me back here tomorrow.”"
- **useful because:** Creates a durable end-of-day work capsule spanning the wearable's moment marker, the relay's durable state, Safari's authenticated tabs, and the Mac's open files/apps. Tomorrow one request restores the actual working set instead of a generic summary.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Background model for summarization and entity linking; realtime only for the spoken acknowledgement. Deterministic Mac/browser restoration should not spend model tokens.
- **latency:** Capture under 3 seconds; next-day summary under 20 seconds; restoration actions begin immediately and report a receipt.
- **cost:** About $0.01–$0.04 per capsule depending on document text; most cost is one bounded summary, not action execution.
- **security:** Authenticated URLs and selected document titles leave the browser/relay unless redacted. Never store page bodies or passwords by default; require an explicit per-site capture policy and show a restore preview for destructive tab/file changes.
- **missing:** A real cross-surface capsule schema joining pendant bookmark timestamps to browser tab identity, Mac foreground/document identity, and relay durable state; Browser command that returns stable tab/session identity plus bounded page title/selection (Safari is online now but capabilities reports empty); Restore executor that can reopen a recorded set idempotently and verify each target before acting

### "“Save this page for later, tell me why it matters, and put it in my research queue.”"
- **useful because:** A natural pendant command turns the currently authenticated Safari page into a useful, searchable research item: browser extracts a bounded title/selection, the relay summarizes and deduplicates it, and the Mac writes a dated note or queue entry without the owner copying URLs.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Cheap background model for extraction, deduplication, and a two-sentence importance note; realtime handles only intent capture and confirmation.
- **latency:** Acknowledge in under 2 seconds; queue item and Mac note within 15 seconds.
- **cost:** Roughly $0.005–$0.02 per page, dominated by page text extraction; URL/title-only saves should be near-zero.
- **security:** The active page may contain private authenticated content. Default to URL, title, visible selection, and a short redacted excerpt; never send cookies, forms, hidden DOM, or full page text without a site-specific opt-in. Require confirmation before sharing or posting externally.
- **missing:** Reliable browser read-current-tab and bounded-selection extraction; current Safari status shows tab 3186198 online but capabilities=[] and the resolver is still ambiguous; A relay research-queue record with deduplication and provenance linking the pendant utterance to the exact tab; A Mac note/queue writer that is idempotent and returns a receipt

### "“Keep an eye on the thing you’re doing on my Mac while I’m away; only interrupt me if it fails, needs a decision, or finishes.”"
- **useful because:** Makes the hive act as one asynchronous worker: the Mac performs a multi-step task, the relay tracks durable progress and retries safe stages, the browser supplies session-specific work when needed, and the pendant surfaces only meaningful state changes. The owner can leave instead of babysitting a screen.
- **path:** mac-planner → browser → relay → pendant → dashboard
- **model tier:** Cheap background model classifies receipts and drafts a concise exception; deterministic job state, retry, and completion checks should be code. Realtime is used only if the owner asks a follow-up by voice.
- **latency:** Start immediately; heartbeat every 10–30 seconds; alert within 5 seconds of a terminal failure or completion. Retries may run for hours without conversation.
- **cost:** Usually under $0.01 per job for classification; browser extraction and any page-specific reasoning dominate, not monitoring.
- **security:** A retry could duplicate an external side effect or continue with a changed authenticated page. Persist an idempotency key and touched-resource manifest; pause on unknown state, external sends/purchases/deletes, or session expiry. Send the pendant only a redacted status, never page content.
- **missing:** A single cross-surface job state machine that consumes Mac receipts, browser command results, and relay reachability with idempotent retry semantics; A typed distinction between safe retry, owner decision, and terminal side effect for existing FULL_CONTROL actions (without silently assuming current bypass behavior is policy); Pendant delivery of compact job exception/completion cards tied to a job id, with acknowledgement and deduplication

### "“Take what I just said and put it into the exact place I’m editing—keep my formatting, show me the proposed insertion, and leave an undo trail.”"
- **useful because:** The owner could speak naturally while looking at a document, email, or web form and have the relay turn speech into a context-aware edit at the current cursor/selection. Today the pendant can capture speech and the Mac can execute actions, but no component reliably binds the utterance to the exact editable target or presents a structured diff before insertion.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime for transcription and immediate acknowledgement; a cheaper text model for formatting-preserving transformation. Target detection and insertion should be deterministic once the semantic context is supplied.
- **latency:** Proposed text in 2–5 seconds; insertion after owner confirmation within another second; undo receipt available immediately.
- **cost:** Approximately $0.01–$0.05 per edit, dominated by transformation context; simple dictation can be nearly free.
- **security:** The current document or authenticated page may contain private material. Send only the selected region and minimal surrounding structure, redact secrets and form credentials, show exact before/after diff, and never submit a web form automatically.
- **missing:** Typed semantic edit context from the Mac/browser: app, document, selection, cursor, editable target, and formatting constraints; A relay operation that converts a spoken utterance into a bounded patch rather than an unconstrained replacement; A reversible insertion primitive with an owner-visible diff and durable undo identity

### "“What changed while you were helping me? Show me the exact files, tabs, messages, and settings you touched, and let me undo only the ones I choose.”"
- **useful because:** The owner gets a trustworthy answer after an unattended or multi-step action instead of a vague success message. A single, redacted change ledger would span Mac mutations, browser commands, relay decisions, and pendant acknowledgements, with selective rollback where possible.
- **path:** relay → mac-planner → browser → pendant → dashboard
- **model tier:** Deterministic event aggregation and diffing first; a cheap model may summarize the ledger. Realtime is unnecessary unless the owner asks by voice.
- **latency:** Ledger available as each step completes; spoken summary in under 3 seconds; selective undo starts immediately.
- **cost:** Near-zero for event aggregation; under $0.01 for optional natural-language summarization. Storage and diff computation dominate.
- **security:** Logs can expose private paths, URLs, message subjects, or page snippets. Store hashes and redacted labels by default, retain full diffs only locally, and require an explicit owner request to reveal sensitive details. Never claim undo succeeded without a verified receipt.
- **missing:** One append-only correlation ID shared by relay plans, Mac receipts, browser command results, and pendant delivery; Resource-level before/after snapshots or hashes for files, tabs, settings, and messages; Selective inverse operations with verified post-undo state rather than the current coarse whole-job undo

### "“When I’m about to share something private, warn me if the destination, browser account, or visible audience is not what I intended—and let me cancel from the pendant.”"
- **useful because:** The owner gets a last-second cross-surface privacy check before sending an email, posting in a browser, sharing a file, or pasting into the wrong account. The browser knows the authenticated destination, the Mac knows the source and target app, the relay reasons over the mismatch, and the pendant remains available even when the owner is not looking at the screen.
- **path:** pendant → browser → mac-planner → relay → dashboard
- **model tier:** Deterministic checks for account, domain, recipient, visibility, and source classification; a small judgement model only for ambiguous sensitivity or intent. Realtime handles the short warning and cancellation command.
- **latency:** Check must complete in under 300 ms before an action; pendant cancellation must be honored within one action boundary; warning should be spoken in under 2 seconds.
- **cost:** Usually negligible because most checks are local metadata comparisons; occasional sensitivity classification costs roughly $0.001–$0.01.
- **security:** The safety service itself must not exfiltrate the sensitive content it is protecting. Use local hashes, MIME/type metadata, recipient/domain/account identifiers, and bounded redacted previews. Block or hold the outbound action until the owner explicitly dismisses the warning; cancellation must work offline for queued actions.
- **missing:** A pre-send interception seam for both browser submissions and Mac actions, before irreversible execution; Typed identity and visibility metadata from Safari, Mail, file-sharing dialogs, and the active Mac account; A pendant cancel/hold command correlated to the pending action, with a local fail-closed queue when the relay is unreachable


## What it asked for

_Nothing._
