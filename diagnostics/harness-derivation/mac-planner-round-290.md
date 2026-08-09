# Harness derivation — mac-planner — round 290

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Get me ready for my next meeting.” Read the next calendar event, gather the relevant files and currently open browser work, make a one-page prep brief in my workspace, open only the useful materials, and send a 30-second spoken checklist to my pendant.”"
- **useful because:** This is the single most useful cross-node action: the pendant supplies the request and last-minute bookmark context, the relay coordinates it, the Mac reads Calendar/files, the browser contributes authenticated meeting material, and the Mac leaves a durable brief instead of making the owner hunt across surfaces. It turns an imminent meeting into a prepared state in one command.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap planner/background model for calendar/file/browser synthesis; reserve realtime only for the spoken checklist and any follow-up conversation.
- **latency:** Under 20 seconds for calendar and local file discovery; up to 45 seconds if authenticated browser pages must be read; spoken checklist should begin within 2 seconds after the brief is saved.
- **cost:** Roughly $0.01–$0.05 per invocation depending on browser-page text and synthesis; realtime audio dominates only if the owner asks follow-ups.
- **security:** Browser pages may contain confidential meeting content and should stay on the Mac/relay only as redacted excerpts. Never send mail or modify calendar. Opening files is reversible; creating the brief is low-impact. The owner’s configured destructive-action confirmation must apply if a future version edits or shares anything.
- **missing:** A semantic Mac context read for document/window identity and selected text (the queued mac_semantic_context_read request).; A browser effect preview so the planner can show exactly which authenticated pages it will read/open before execution (the queued browser_effect_preview request).; A meeting relevance linker that maps calendar attendees/title to local files and browser tabs without uploading whole documents.; A relay orchestration job that correlates the prep brief, browser excerpts, and pendant audio receipt under one job id.

### "“Run the pendant bench diagnostic and file the bug report if it fails.” With the pendant connected by USB, collect the bounded UART fixture output, compare it with the measured audio acceptance thresholds, create a timestamped report and reproduction bundle in my workspace, and put the failure summary in my notes without sending anything externally."
- **useful because:** The owner explicitly wants a pendant that files its own bug reports. This makes that real today while LTE registration is absent: the physical pendant emits the diagnostic fixture, the Mac is the only node that can read the USB serial log, and the relay/model turns raw counters into a useful diagnosis. It prevents another audio regression from being discovered by listening manually.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** Use deterministic parsing and threshold checks first; use a small background model only to write the human diagnosis. No realtime model is needed.
- **latency:** A diagnostic run should finish in under 90 seconds; report generation under 10 seconds after the final UART frame.
- **cost:** Usually under $0.01 per run; the dominant cost is optional model-written explanation, not telemetry.
- **security:** UART output may contain accidental transcript or environment data, so redact payload-like lines and retain only counters/sequence numbers by default. Write only to ~/AI-Pendant-Workspace and Notes; do not upload raw audio or automatically file an external issue. A future external issue submission must require confirmation.
- **missing:** A bounded, implementation-backed USB serial diagnostic reader that exposes port selection, baud, timeout, and redacted line output; existing run_shell is too unstructured for reliable receipts.; A parser for the audio_path_diagnostic_fixture output and a versioned acceptance-threshold profile (alias rejection, CPU, mic drops, tx_starved, silence preamble).; A local report writer that atomically stores UART excerpt, parsed metrics, firmware/build identity, and pass/fail receipt.; A relay endpoint that accepts the redacted diagnostic receipt and returns a stable failure classification.

### "“Remember this page and exactly why I marked it.” When I press the pendant’s moment button while browsing, capture the active tab’s URL/title, a redacted page excerpt, timestamp, and my nearest spoken context, then save a durable citation card in my workspace for later review."
- **useful because:** A physical bookmark is currently just a timestamp. This turns an involuntary moment of attention into a recoverable piece of work: the pendant works even if the link blips, the browser knows the authenticated page, the relay correlates timing, and the Mac writes a citation card. It is especially valuable for research, support tickets, and pages that will disappear or change.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use deterministic correlation and redaction; use a small background model only to summarize the spoken context into one sentence. Realtime is unnecessary unless the owner asks what was just saved.
- **latency:** A local bookmark acknowledgement is immediate; once connected, enrich and write the citation within 5 seconds. If the browser is offline, queue the bookmark and enrich it on the next heartbeat.
- **cost:** Usually below $0.01; model cost is limited to a short transcript/context summary, while page capture and storage are local.
- **security:** Authenticated pages can expose secrets and private records. Capture only the active tab, selected/visible text, URL and title; redact tokens, passwords, payment data, and page-wide hidden DOM. Never capture a page on a blocked-domain list. Store a provenance hash and let the owner delete the card; do not sync raw page content to the pendant.
- **missing:** A browser-side event hook that timestamps the active tab within a tight window of the pendant bookmark.; A redaction-aware browser excerpt endpoint and a durable citation-card schema with source hash and deletion semantics.; Relay correlation logic that joins offline_moment_bookmark events to the nearest browser heartbeat without guessing across long gaps.; A workspace index/search view for citation cards.

### "“Package this bug for the maintainer.” Starting from the failing pendant diagnostic, produce a minimal shareable issue bundle: sanitized reproduction steps, firmware and host versions, only the relevant UART counters, an audio-quality plot, and a patch-ready Markdown issue in a new Git worktree—without publishing or contacting anyone."
- **useful because:** Today the owner can collect pieces of a failure, but cannot turn a physical audio failure into a maintainer-ready artifact without manually reconstructing the environment and redacting logs. This would make the pendant a serious development instrument: hardware evidence, Mac repository state, and relay-generated diagnosis become one reproducible package.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** Deterministic fixture parsing, hashing, redaction, and worktree creation should do most of the work. A background coding model can draft the issue narrative and reproduction steps; realtime is unnecessary.
- **latency:** Five minutes for a complete diagnostic and bundle, with progress receipts after each stage. The owner should be able to inspect the package immediately even if the relay disconnects afterward.
- **cost:** Typically $0.03–$0.15 for log interpretation and issue drafting; local plotting and packaging dominate elapsed time, not API cost.
- **security:** Never include raw microphone/audio, bearer tokens, personal paths, or unrelated repository files. Worktree creation must be isolated and reversible. Publishing to GitHub, sending mail, or opening a pull request must remain a separate explicitly requested action.
- **missing:** A firmware/build manifest emitted by the diagnostic fixture.; A deterministic UART-to-metrics parser and audio plot generator.; A repository-aware worktree/package action with a manifest of included files and cryptographic hashes.; A redaction profile that understands Mac paths, tokens, serial identifiers, and accidental speech content.

### "“Screen my next phone call.” When my iPhone rings, tell me who is calling on the pendant, let me say ‘take it’, ‘send to voicemail’, or ‘text that I’m unavailable’, and only then operate the real iPhone through Mirroring; record the disposition in my day log."
- **useful because:** The owner currently has to stop what they are doing and reach for the phone. This would combine a worn, screenless alert, the Mac’s iPhone Mirroring reach, and a relay decision loop into a genuinely hands-free call gate. It is useful during focused work and safer than blindly answering because every disposition is explicit.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Use deterministic caller/event detection and a small intent classifier for the three commands. Realtime is appropriate only for the short spoken interaction; no large model is needed.
- **latency:** Caller identity should reach the pendant within 1 second of the ring event. The chosen disposition should be applied within 3 seconds of the owner’s reply.
- **cost:** Under $0.01 per call event; realtime audio and iPhone event polling dominate, not text generation.
- **security:** Caller identity and message contents are sensitive. Do not announce details aloud beyond the configured level. Sending a text is an external side effect and must require the owner’s explicit spoken command plus a final exact-message readback; never infer a message from context. Calls from an emergency-contact list may use a distinct local alert pattern.
- **missing:** A reliable iOS incoming-call event source exposed to the Mac bridge, rather than screen scraping.; A dedicated iPhone Mirroring action set for answer, decline, voicemail, and draft/send text with clear result receipts.; A pendant notification payload that carries caller identity and expires when the call ends.; A configurable spoken privacy policy for caller names and message previews.


## What it asked for

_Nothing._
