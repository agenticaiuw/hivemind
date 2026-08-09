# Harness derivation — browser-extension — round 179

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m looking at this page—answer my question about it, quote the exact relevant lines, and tell me what I should do next.”"
- **useful because:** It makes the pendant a private voice interface to whatever authenticated Safari page is in front of the owner. The owner need not copy URLs or expose page text; the browser supplies the active-page context, the relay answers with bounded evidence, and the Mac can offer a reversible next action such as drafting a reminder or opening the cited section. This is useful for policies, bills, forms, and account pages where public search cannot see the answer.
- **path:** pendant → browser-extension → relay-realtime → mac-planner
- **model tier:** Realtime for the spoken question and short answer; use a cheaper model only if the page is long and needs retrieval/chunking.
- **latency:** 3–6 seconds from question to spoken answer; page extraction under 2 seconds and no more than one follow-up extraction.
- **cost:** About $0.01–$0.04 per question, dominated by multimodal/text context; quote only the minimum matching passage to control tokens.
- **security:** Raw authenticated page text must be transient and origin-scoped. Apply existing redaction before model submission, never persist the full page, include URL/title and quoted-line provenance in the response, and refuse to read categories configured as must-not-speak. Any click, filing, or send action remains a separately described action, not implicit in the answer.
- **missing:** Active-tab context push from the extension into the voice turn (including tabId, origin, title, and a bounded page snapshot); A question-to-page retrieval adapter with quote offsets and redaction; A pendant trigger/voice protocol that binds one question to the current browser tab

### "“Before you use this logged-in page, show me exactly what information will leave Safari, what will be discarded, and why.”"
- **useful because:** The owner can safely use authenticated browser assistance without guessing what the model saw. Safari produces a local redaction preview with origin, fields, and byte counts; the relay receives only the approved excerpt; the pendant speaks a concise privacy receipt. This turns privacy from an invisible promise into something inspectable before every sensitive workflow, while remaining compatible with the owner's maximum-access policy because it informs rather than blocks.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** No expensive model for the preview: local extension rules and deterministic redaction first. Use a cheap classifier only for uncertain field labels; realtime is limited to the owner's spoken explanation.
- **latency:** Under 1 second for deterministic preview; under 3 seconds if a classifier is needed.
- **cost:** Near-zero API cost for ordinary previews; roughly $0.001–$0.01 only for ambiguous classification.
- **security:** The preview itself must not leak the very values it protects: display field names, types, hashes, and masked examples, never raw secrets. Store only a short receipt (origin, policy version, redaction counts, timestamp); do not retain page text. This is observability, not a confirmation gate.
- **missing:** Extension-side DOM field classification and redaction preview payload; A standard privacy receipt consumed by /execute and /pipeline/events; An owner-visible policy editor for per-origin read/extract/redact/never-store and category speak/persist rules

### "“Watch this exact authenticated page section and tell me only when its meaning changes—then keep the before/after evidence so I can act.”"
- **useful because:** A pinned section watcher is more useful than polling an entire site: it can monitor a renewal date, account status, appointment slot, shipment state, or policy notice inside an existing Safari session. The extension captures only the selected region, the relay performs semantic change detection, the Mac records a compact before/after receipt, and the pendant's offline alert inbox announces a meaningful change rather than noise.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Cheap scheduled/background model or deterministic DOM normalization for most comparisons; use realtime only when the owner asks what changed. No continuous realtime session.
- **latency:** Polling cadence configurable from 15 minutes to daily; alert generation under 10 seconds after a poll.
- **cost:** About $0.001–$0.02 per poll depending on page size; region hashes and DOM normalization should avoid model calls when unchanged.
- **security:** The owner explicitly pins the origin, locator, and allowed categories; configuration ships empty. Never store full page captures by default—retain redacted before/after snippets and hashes only. Expired sessions must produce an error alert, never silently claim no change. Any resulting action is proposed separately.
- **missing:** A durable per-tab/ per-origin watch definition with a region locator and expiry; A scheduled browser poll that can re-use the existing Safari session and detect login expiry; Semantic diff, redacted evidence receipts, and delivery to the already-accepted offline_alert_inbox

### "“While I’m in this browser meeting, quietly turn the live captions into decisions, owners, and deadlines, and give me a spoken recap when it ends.”"
- **useful because:** The browser is the only node that can see an authenticated web meeting and its captions; the relay can turn a long conversation into a compact decision log; the Mac can create draft reminders and calendar holds; and the pendant can deliver the recap without making the owner reopen the meeting. This is materially different from reading a page: it follows a changing, time-based private stream and preserves who committed to what.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Use a cheap streaming/background summarizer for caption chunks and a stronger model only for the final conflict-resolution and action-item synthesis; realtime is reserved for an owner interruption or “what did I miss?” question.
- **latency:** Chunk summaries within 5 seconds; final recap within 15 seconds after the meeting ends.
- **cost:** Approximately $0.03–$0.20 per hour depending on caption volume; send deduplicated caption deltas rather than screenshots or repeated context.
- **security:** Meeting content is highly sensitive. Require an explicit per-origin and meeting-mode policy, show a visible recording/processing indicator, never retain raw captions by default, redact participant emails and secrets, and persist only owner-approved decisions. Calendar/reminder creation should produce a draft and receipt, not silently send invitations.
- **missing:** Extension support for a user-started caption stream and meeting start/stop lifecycle; Streaming chunk storage with bounded retention and speaker/action attribution; A relay-to-Mac handoff that turns approved action items into drafts and a pendant delivery event

### "“Find the right document on my Mac, attach it to the authenticated form I have open, verify the recipient and fields against the document, and leave it ready without submitting.”"
- **useful because:** This joins two capabilities that cannot complete the job alone: Safari holds the private session and form, while the Mac holds the files and can inspect their contents. The relay can reconcile names, dates, amounts, and recipient details, then return a precise diff; the browser leaves the form staged for the owner. It removes tedious upload-and-cross-check work while honoring the deliberate stop before an irreversible submission.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap local/document extraction first; use a stronger model only for field-to-document reconciliation and ambiguity. Realtime is used only to explain mismatches through the pendant.
- **latency:** 15–45 seconds for one document and a form; longer jobs should become a relay job with progress and a receipt.
- **cost:** Roughly $0.02–$0.10 per reconciliation, dominated by document parsing; send extracted fields and hashes rather than full documents when possible.
- **security:** Files and form data are sensitive. Keep raw documents on the Mac, redact before relay, scope browser actions to the named tab, and display the exact attachment, recipient, and field diff. Never submit, send, or upload to a different origin than the owner named; retain an undoable job receipt for staged edits.
- **missing:** A cross-surface attachment broker that can pass a Mac-local file reference into a browser upload control; Structured form-field extraction and document-field comparison with provenance; A browser action that stages uploads and edits while returning a complete pre-submit diff

### "“Read the code or reference number visible in this authenticated page, check it against the local task I’m doing, and tell me only the minimum I need.”"
- **useful because:** Many private portals expose one-time codes, shipment references, meter readings, invoice numbers, or pairing strings visually rather than as accessible text. The browser can inspect the rendered image/canvas, the Mac can compare it with the local task or terminal state, and the pendant can speak a short, masked result. This avoids retyping long strings and catches mismatches before they cause a failed or misdirected action.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Prefer local OCR and deterministic checksum/comparison; invoke realtime only when the owner asks a follow-up. Never send an entire screenshot to a model when a bounded crop suffices.
- **latency:** 1–3 seconds for a visible code; under 8 seconds if local comparison is required.
- **cost:** Near-zero for local OCR; about $0.001–$0.02 for difficult rendered text or an explanation.
- **security:** Treat OTPs, recovery codes, and access tokens as non-persistent and normally non-speakable unless the owner explicitly asks. Mask all but the last few characters in receipts, enforce a one-shot TTL, never log clipboard contents, and keep image crops local whenever possible.
- **missing:** Extension support for bounded image/canvas capture and local OCR with confidence; A classification step distinguishing harmless references from authentication secrets; A Mac comparison adapter for the owner's active local task, plus one-shot pendant delivery with expiry


## Changes it proposed to its own stack

### `browser-harness` — Add a one-shot browser-context envelope to POST /execute: when a browser action is requested, attach active tab identity, origin, title, locator, redaction policy version, content hash, and short-lived evidence references to the result and pipeline event. Keep page text in the extension/agent memory only until the turn ends, and make the envelope available to the relay without introducing a new browser command.
- **owner gets:** The pendant can answer about the exact Safari page the owner is viewing and explain what changed without the owner copying links, while the owner gets a trustworthy source and privacy receipt instead of an opaque “the AI saw your browser.”
- effort: Medium: extend browserBridge result schema, pipeline event propagation, and extension-side bounded snapshot/redaction; add tests for tab switches and expired sessions.  ·  risk: A tab switch could bind an answer to the wrong page, or an evidence reference could outlive its privacy window. Bind every envelope to commandId plus observed tabId/hash, expire references quickly, and return an explicit stale-context error rather than guessing.
- cost: Negligible storage; modest engineering cost and a small reduction in model tokens because citations become offsets rather than duplicated page text.  ·  latency: Adds roughly 50–150 ms for hashing/metadata; no extra model round trip.
- security: Improves provenance and reduces leakage if raw text is ephemeral, but requires strict TTLs and redaction before any relay event. Never include cookies, form values, or hidden DOM fields in the envelope.
- depends on: Owner supplies per-origin redaction/extraction policy; Browser extension exposes bounded snapshot and active-tab metadata; Relay accepts evidence references in pipeline events


## What it asked for

_Nothing._
## Its own summary

Fresh discovery: Safari is now online with 9 tabs (including authenticated Gmail and X), and POST /execute successfully completed browser_list_tabs with a receipt. I recorded three non-duplicate capabilities: page-grounded pendant Q&A with exact quotes, a preflight privacy/redaction receipt, and a pinned authenticated-section semantic watcher feeding the already-accepted offline alert inbox. I also recorded a browser-harness change to bind active-tab identity, origin, hash, redaction version, and expiring evidence references into pipeline results. The first generic “check open pages for attention” proposal collided with an existing backlog item and was not repeated.

**Biggest unknown:** The owner still needs to supply explicit per-origin rules (which authenticated origins may be read, what may be spoken, and what may be persisted). Technically, the remaining work is extension-side bounded snapshots/redaction, active-tab context propagation, scheduled section polling, and wiring semantic diffs into the existing alert inbox; I do not need another browser enqueue tool this round.

