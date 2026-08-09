# Harness derivation — mac-planner — round 261

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Run a complete pendant audio flight test over USB tonight and leave me a pass/fail report with the exact failing stage and an audio clip if playback failed."
- **useful because:** The owner is actively shipping the 24 kHz path and the hardware is physically attached now. A single repeatable job can distinguish capture, Opus encode, serial/modem transport, decode, and speaker timing failures instead of requiring a human to interpret UART output and rerun partial tests.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** Use deterministic firmware fixture generation and parsers first; use a cheap background model only to turn counters and logs into a concise diagnosis. Never spend realtime tokens on a bench test.
- **latency:** Start within 10 seconds of the scheduled job; fixture execution under 5 minutes; report available immediately after receipt verification.
- **cost:** Typically under $0.02 per run; nearly all cost is optional log summarization, while USB execution and storage are local.
- **security:** The fixture must use synthetic audio only and must not upload microphone content. USB commands should be limited to the known diagnostic trigger and bounded log reads; retain raw logs locally with a configurable expiry. A failed test must not silently flash firmware or alter production state.
- **missing:** A first-class bounded USB serial bench runner with exit status, port identity, timeout, and byte-counted receipts (the current run_shell route is not a reliable serial-session contract); A relay job type that accepts the fixture's structured counters and computes stage-level pass/fail against the established acceptance thresholds; A dashboard/audio artifact route to expose a failed synthetic playback clip and the exact packet sequence around the fault

### "Don't interrupt me while I'm presenting or in a meeting; queue only the alerts that matter, then give me a two-sentence catch-up when I become available."
- **useful because:** The pendant already has an alert inbox, but it does not know whether the owner is presenting, on a call, typing in an editor, or between calendar events. A cross-node arbiter prevents an urgent-sounding stream from becoming a distraction while preserving genuinely time-sensitive items and delivering a compact digest at the first safe window.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic rules classify availability from Calendar, foreground app, browser activity, and explicit privacy latch; a cheap background model ranks and compresses queued alerts. Realtime is only used if the owner asks for the catch-up aloud.
- **latency:** Local queueing is immediate; availability refresh every 15–30 seconds; catch-up generated within 2 seconds of an availability transition.
- **cost:** Usually below $0.01/day; most decisions are rule-based and the only model cost is digest compression.
- **security:** Calendar titles, app names, and alert text are sensitive. Keep raw context on the Mac/relay, send the pendant only the selected short alert, and never infer availability from microphone audio. The owner must be able to override with the existing local privacy latch.
- **missing:** A relay-side availability state machine with explicit states such as AVAILABLE, FOCUS, MEETING, PRESENTING, and PRIVACY; A safe event feed from Mac foreground/browser state plus Calendar range, with debouncing and redaction; Priority/expiry metadata and digest semantics added to the existing offline_alert_inbox rather than creating another queue

### "From the article I have open, extract the one thing worth acting on, save a cited note, and remind me next week—without making me copy or paste anything."
- **useful because:** This turns the authenticated browser and the Mac's Notes/Reminders into one spoken workflow: the owner can move from reading to a durable, attributed action in one sentence. It is especially useful for the research brief routine, where findings currently become prose but not an owned follow-up.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Use a small/cheap text model for page extraction and action ranking; use realtime only to resolve ambiguity in the owner's spoken request. Deterministic Mac actions create the note/reminder after the plan is explicit.
- **latency:** Read and draft within 5 seconds for a normal page; ask one clarification if needed; create the note/reminder within 2 seconds after the owner confirms the extracted action.
- **cost:** Roughly $0.005–$0.03 per invocation depending on page length; browser page extraction and local mutations dominate latency, not audio.
- **security:** The browser session may contain private or authenticated content. Send only the relevant page text to the model, redact credentials and hidden fields, include source URL and capture time in the note, and require confirmation before creating a reminder if the date or wording is inferred. Never submit forms or send mail as part of this workflow.
- **missing:** A structured browser-to-action extraction contract that returns source URL, quoted evidence, proposed action, confidence, and unresolved fields; A Mac planner operation that atomically creates a cited Note and Reminder and returns both identifiers; A spoken confirmation card on the pendant/browser showing exactly what will be saved before mutation

### "If my cellular connection drops while I am talking to you, keep the conversation alive through my nearby Mac and switch back when LTE returns without making me repeat myself."
- **useful because:** A dropped link should be a transport change, not a conversational failure. The owner would hear a brief continuity tone or nothing at all, while queued speech and the model's turn remain ordered and deduplicated.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Realtime remains responsible for the active conversation; a deterministic transport coordinator handles failover, sequencing, and replay. No additional model call should be required during a handoff.
- **latency:** Detect failure within 1 second, resume through the Mac within 3 seconds, and reconcile duplicate or late audio without replaying a sentence twice.
- **cost:** Negligible model cost; local buffering and relay websocket traffic dominate. A small encrypted RAM ring is preferable to another inference call.
- **security:** The Mac must be explicitly paired with the pendant and relay, and audio buffers must be encrypted, bounded, and erased after acknowledgement. The Mac fallback must not expose microphone data to unrelated apps or silently continue after the privacy latch is engaged.
- **missing:** A paired pendant↔Mac transport protocol that is distinct from bench flashing/diagnostic USB use; Relay session migration with monotonic turn and audio sequence numbers, acknowledgements, and duplicate suppression; A Mac audio transport endpoint capable of receiving pendant uplink and returning 24 kHz downlink without routing through a general serial shell; A visible dashboard state showing active transport and buffered data

### "Before you act on conflicting information, tell me which source disagrees and ask one clear question—such as when my calendar says I am busy but the browser task says I am available."
- **useful because:** Today each surface can be individually read, but the owner has no dependable way to know when Calendar, Mail, browser state, and pending instructions disagree. Explicit conflict explanations prevent silent wrong scheduling, wrong reminders, or actions taken in the wrong account or project.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic source-specific precedence and conflict rules first; use a cheap model only to phrase the conflict in one sentence. Realtime is appropriate only for the owner's follow-up conversation.
- **latency:** Detect conflicts during planning in under 500 ms from cached context; speak one concise clarification immediately before any mutation.
- **cost:** Usually under $0.005 per conflict; deterministic comparison dominates and model phrasing is optional.
- **security:** Expose only the minimum conflicting fields, redact private mail bodies and page content, and identify source/account scope explicitly. Never resolve a high-impact contradiction by guessing.
- **missing:** A typed cross-surface fact model with provenance, freshness, account scope, and confidence; A conflict detector in the planner that blocks only the affected mutation while allowing unrelated work to continue; A pendant/dashboard clarification card that preserves the unresolved alternatives and the owner's choice

### "Find the thing I saw but did not save—across my recent browser pages, Notes, Mail, and pendant bookmarks—and show me the smallest matching evidence so I can recognize it."
- **useful because:** Human memory often retains a fragment, not a filename or exact phrase. A private, cross-surface recall index would make the pendant useful as an external memory without forcing the owner to maintain tags or remember which surface held the original.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Build embeddings and lexical indexes locally or in a privacy-scoped relay job; use a cheap background model to rerank a small candidate set. Realtime only handles the spoken query and follow-up disambiguation.
- **latency:** Return the first three candidates within 2 seconds for a one-week window; never block on indexing while the owner is speaking.
- **cost:** Small recurring embedding/indexing cost, roughly $0.01–$0.10 per day depending on page and mail volume; raw-data transfer and storage are the dominant costs, so local indexing is preferred.
- **security:** This is a high-sensitivity memory surface. Index only explicitly enabled sources, encrypt the index, exclude passwords, financial content, attachments, and message bodies by default, retain provenance and deletion controls, and show source snippets rather than uploading whole documents for ranking.
- **missing:** A consented, local-first unified index spanning browser history/page metadata, Notes, Mail metadata, and pendant bookmark events; A natural-language recall query route with time/source filters and deletion propagation; A redacted evidence renderer that can reopen the source only after the owner chooses a candidate


## Changes it proposed to its own stack

### `model-routing` — Add a confidence-and-cost router for Mac/browser plans: deterministic extraction and local actions first, cheap model for page summarization and routine briefs, realtime only for live spoken ambiguity or an active call. Every plan records confidence, estimated token cost, and the escalation reason in its receipt.
- **owner gets:** Routine requests become faster and cheaper without making the owner learn which model to ask for; difficult or ambiguous actions still get the conversational quality of realtime, while simple desktop work completes quietly.
- effort: Moderate: add a planner preflight classifier, model policy table, and receipt fields; exercise it against existing /plan, /execute, /research, /briefing, and browser jobs.  ·  risk: A low-confidence classifier could under-escalate and make a wrong assumption. Recovery is to require a clarification whenever required fields are missing, and to keep the original command plus an explanation in the receipt so the owner can retry with realtime.
- cost: Reduces unnecessary realtime usage; adds negligible local compute and a small amount of receipt storage. Background summarization remains the dominant API cost.  ·  latency: Simple actions should be faster by avoiding a model round trip; ambiguous requests may add one cheap classifier pass before escalation.
- security: The router must classify using redacted metadata where possible and must not log page bodies, mail contents, or secrets merely to explain model choice.
- depends on: POST /plan; POST /execute; POST /research; POST /briefing; GET /jobs/:jobId/receipts; GET /routing


## What it asked for

_Nothing._
