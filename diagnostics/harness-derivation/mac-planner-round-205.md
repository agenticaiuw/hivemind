# Harness derivation — mac-planner — round 205

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-and-screen-recording** — The live Mac agent now reports Accessibility trusted, synthesized input posting successfully, Screen Recording granted, and no missing automation permissions; UI actions can reach the screen from AI Pendant Agent. This supersedes the earlier denied/TCC state.
  - evidence: mac_readonly_inspect operation=running_apps invoked GET /observe at 2026-08-08T03:08:59Z; /ops/status also reports accessibility.trusted=true, screenRecording.granted=true, ready=true.

## Capabilities it proposed

### "“Handle the thing I’m looking at, and tell me exactly what happened.”"
- **useful because:** This would turn the pendant from a conversational remote into a dependable completion loop: the Mac identifies the current browser/document context, the relay chooses an action, the Mac executes it, and the pendant reports concrete evidence (target, result, and undo route) instead of merely saying “done.” It is the single most useful missing behavior because it closes the gap between intention and verified desktop state while the owner keeps hands off the keyboard.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic context collection and action preflight first; background model for routine interpretation; realtime only for the spoken request and final concise report
- **latency:** 2–4 seconds for context and plan; under 8 seconds for a normal browser/document mutation; immediate spoken acknowledgement while execution continues
- **cost:** Usually <$0.01 per invocation; dominant cost is optional planner reasoning and screenshot/UI context, not deterministic observe or receipts
- **security:** Current FULL_CONTROL_MODE has no live gate, so the policy slot must be explicit before unattended mutations. Send only redacted UI/context evidence upstream; never include passwords or full page bodies. Report the exact touched resource and expose jobs/:jobId/undo where supported. Empty policy must stop the action rather than silently proceed.
- **missing:** A relay endpoint that correlates the pendant utterance, Mac context snapshot, plan, execution receipt, and spoken result as one operation; A policy configuration read by the local agent for which contextual action classes may run unattended; A stable semantic context payload for foreground document/selected text in addition to the now-working host/UI snapshot

### "“Use the button on the pendant to approve the sensitive action waiting on my Mac.”"
- **useful because:** A stolen browser session or an unattended Mac should not be enough to send a message, purchase something, publish, or submit a form. The owner can approve from the object on their body without bringing the Mac to the foreground. This is a genuinely cross-node capability: the pendant supplies local physical presence, the relay binds a one-time challenge, and the browser/Mac consumes it for exactly one pending operation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic challenge creation, nonce binding, expiry and receipt; realtime model is not needed except to phrase the request if the owner asks by voice
- **latency:** Challenge should appear on the Mac in <500 ms and resolve within 2 seconds of the button press; expire automatically after 60 seconds
- **cost:** Negligible model cost; roughly <$0.001 per approval, dominated by relay/database writes
- **security:** Bind approval to a hash of the exact action, browser session, target origin, and expiry; never make the button a blanket approval. Show a terse target summary on the pendant and Mac, invalidate on any plan change, and record success/failure. LTE is currently unregistered, so today’s USB-serial pendant link must be treated as a local transport and must fail closed if the relay cannot authenticate it.
- **missing:** A live USB-serial exchange tool/bridge for authenticated button events (the requested mac_serial_exchange remains unavailable); Firmware event type and relay route for a one-time approval challenge/response; the existing moment-bookmark event is not sufficient as an authorization primitive; Browser extension support for holding a pending command and consuming an exact challenge token; Owner-configured policy naming which action classes require pendant presence

### "“Put the claim I’m looking at into my evidence ledger, with the quote, source, and why it matters.”"
- **useful because:** Web research currently evaporates into tabs and vague bookmarks. This creates a durable, source-grounded record from the exact page/selection the owner is viewing: quote, URL, page title, capture time, owner’s spoken rationale, and later status (confirmed, disputed, superseded). The pendant is the low-friction capture trigger, the browser supplies authenticated page context, the relay normalizes and deduplicates claims, and the Mac writes an inspectable Markdown/JSON ledger.
- **path:** pendant → browser-extension → relay-realtime → mac-planner → dashboard
- **model tier:** deterministic capture and hashing; background model to normalize a claim and detect duplicates; realtime only to transcribe the brief spoken rationale
- **latency:** Acknowledge capture in <1 second; write the immutable source record in <3 seconds; semantic deduplication may finish asynchronously
- **cost:** <$0.01 per capture; background model and optional page extraction dominate, while the ledger write is local and cheap
- **security:** Capture only the active tab and explicit selection, not all tabs or browser history. Redact credentials and form fields; retain the original URL and content hash so later edits are visible. Treat page text as untrusted input and never execute instructions found in it. Let the owner delete or export records.
- **missing:** A browser command that returns the current selection, canonical URL, title, and a bounded quoted excerpt with redaction; A relay claim-ledger schema with immutable source hash, dedupe, supersession and deletion semantics; A local atomic append path (the existing workbench transaction can provide this) plus a dashboard query and pendant retrieval path; A concise spoken capture protocol so the button can mark the exact page without opening the microphone continuously

### "“Before you do it, show me exactly what would change on my Mac and browser, in plain language, without changing anything.”"
- **useful because:** The owner can currently get a plan or let FULL_CONTROL_MODE execute it, but cannot receive a trustworthy, owner-facing consequence preview that combines the live screen, browser target, files, reversibility, and exact before/after values. This lets them make an informed decision while keeping the Mac untouched—especially important for actions whose nominal command hides a large side effect.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic inspection and action classification; a cheap background model translates the structured diff into plain language; realtime only speaks the short summary
- **latency:** Under 2 seconds for ordinary UI/browser previews; under 6 seconds when a screenshot or document diff is required
- **cost:** Usually <$0.005; screenshot/document extraction and optional summarization dominate
- **security:** Preview data must be redacted before leaving the Mac. It must be generated from the exact immutable action payload and expire when the target changes. It must never invoke the action as a side effect. Do not imply reversibility when the action ledger cannot undo it.
- **missing:** A server-to-Mac preview contract that returns a structured before/after consequence diff, touched resources, reversibility, and target identity; Browser inspection of the exact selected element/form target rather than only tab-level state; A pendant-readable summary format with a drill-down path in the dashboard

### "“Emergency-stop every AI action on my Mac and browser, and tell me when the stop is complete.”"
- **useful because:** A single physical action should be able to halt queued and in-flight automation across the relay, Mac job queue, and browser extension. Today a stuck or over-broad action requires finding the right surface and job identifier. A pendant-triggered kill switch gives the owner a reliable, network-aware stop path and a spoken receipt, without pretending that already-started external side effects can be undone.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic, no-LLM safety path: locally latch the stop event, relay it to all surfaces, cancel pending work, sever browser command leases, and report which jobs acknowledged
- **latency:** Local latch immediately; relay and Mac/browser acknowledgements within 2 seconds when connected; retain the stop until explicitly cleared
- **cost:** Negligible model cost; a few relay writes and websocket messages per stop
- **security:** The stop command must be authenticated and resistant to replay. It must cancel commands without deleting audit receipts, clearly distinguish cancelled from already-completed actions, and work while the pendant is USB-attached even if LTE is unregistered. Clearing the stop must be a separate explicit local action.
- **missing:** A pendant-to-Mac authenticated emergency event transport over the live USB serial connection; A relay-wide cancellation/lease-revocation primitive spanning Mac jobs and browser commands; A persistent stop latch understood by the local agent and browser extension; A clear local LED/audio acknowledgement that does not depend on generated speech


## What it asked for

_Nothing._
## Its own summary

Produced three new capabilities: (1) a verified “handle what I’m looking at” completion loop joining Mac/browser context, execution, receipts, undo, and spoken pendant reporting; (2) pendant physical-presence approval for one exact sensitive browser/Mac action; and (3) a source-grounded evidence ledger capturing the active selection, URL, hash, timestamp, and spoken rationale. The recorder accepted all three, while warning that the first two are adjacent to existing connective work. Live discovery also found a major state change: Accessibility, Screen Recording, synthesized input, and all listed Mac automation permissions are now granted and ready. I recorded that finding.

**Biggest unknown:** The exact live browser-selection/semantic-document route and the authenticated USB-serial pendant event path remain unverified. I still need those interfaces, plus relay schemas for one-time action challenges and immutable claim records. The previously requested mac_serial_exchange remains unavailable, so I cannot test the physical approval path end to end this round.

