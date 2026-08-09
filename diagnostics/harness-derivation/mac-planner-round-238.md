# Harness derivation — mac-planner — round 238

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I press the pendant bookmark button, save exactly what I was doing so I can resume it later.”"
- **useful because:** A bookmark should preserve the task, not just a timestamp. The worn button supplies an intentional boundary; the Mac supplies the foreground app/document and browser tab; the relay makes a compact durable capsule. Later, “resume my last bookmark” can reopen the same work without reconstructing it from memory. This is the highest-value everyday loop because it turns interruptions into recoverable state.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** background for capsule extraction and redaction; realtime only for the spoken confirmation and later resume command
- **latency:** Acknowledge the button locally immediately; upload and capsule creation within 10 seconds; resume should begin reopening within 3 seconds.
- **cost:** About $0.01–$0.05 per bookmark depending on whether OCR/summarization is needed; most cost is a small background extraction call, not realtime inference.
- **security:** Capture only the active app, document URL/path, title, and a short redacted task summary by default; never copy passwords or page bodies. Reopening an authenticated page is allowed only under the owner's browser policy. The capsule must have a retention/erase control and must not include the bike-lock secret already present in memory.
- **missing:** A real semantic Mac context read for document identity and selected text (the pending mac_semantic_context_read request is still unavailable); A capsule schema with explicit redaction and retention fields; A browser command that can reopen a saved tab/session by stable identifier

### "“Run a complete pendant bench check now, and tell me whether the microphone, radio path, and speaker are healthy—not just whether a command ran.”"
- **useful because:** The pendant is physically attached over USB today but LTE is not registered, so this makes the real hardware useful now. The Mac launches a bounded serial diagnostic, the pendant's fixture exercises both audio directions, and the relay interprets counters against acceptance thresholds. The owner gets a meaningful pass/fail with the failing stage and an archived receipt instead of a misleading green shell exit.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → unified
- **model tier:** background/cheap model for threshold comparison and report generation; no realtime model is needed unless the owner asks by voice
- **latency:** Arm within 2 seconds, fixture run under 60 seconds, spoken result within 5 seconds of the final serial line.
- **cost:** Usually under $0.01 per run; dominant cost is local serial time, not tokens. Storage is a small JSON receipt plus optional bounded log.
- **security:** The serial procedure must be an explicit allowlisted diagnostic command, never arbitrary shell text from a remote plan. The fixture must use synthetic audio only and never persist microphone content. Redact modem identifiers from reports and retain logs for a configurable period.
- **missing:** A first-class bounded serial-exchange action with exit status and receipt correlation (today only the broad run_shell path can reach USB); A fixture runner that translates audio_path_diagnostic_fixture counters into named thresholds; A relay report route that joins the Mac receipt, pendant sequence numbers, and timestamp skew

### "“Watch the authenticated work I already have open, and alert me on the pendant only when a real deadline or blocking change needs action.”"
- **useful because:** This is not a morning portal scrape or a general briefing: it is a continuous, low-noise tripwire over pages the owner has explicitly opened. The browser extension extracts only deadline/status deltas, the relay deduplicates and ranks them against Calendar/Mail, and the pendant's existing alert inbox delivers one actionable alert even if the Mac later sleeps. It prevents both missed deadlines and notification fatigue.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified
- **model tier:** cheap background model for page-delta classification; realtime only when the owner asks what an alert means
- **latency:** Poll or event-process within 5 minutes of a page change; pendant alert delivery under 15 seconds when connected; no periodic spoken interruption.
- **cost:** Roughly $0.02–$0.10 per monitored page per day, dominated by authenticated page extraction and classification; use hashes and structural deltas to avoid resending full pages.
- **security:** Only monitor tabs/sessions explicitly opted in; send extracted deadline fields and redacted deltas rather than page contents. Never submit forms or change work-system state. Alerts need source URL, expiry, deduplication key, and a local dismiss path; browser credentials remain in the browser.
- **missing:** A browser-session watch/DOM-delta primitive with explicit per-session opt-in and redaction; A relay deadline entity/deduplication store and a Calendar/Mail conflict join; A way to label and expire these records in the existing offline_alert_inbox rather than creating another pendant queue

### "“When you answer a question for me, leave a decision card I can replay later: the conclusion, the evidence, the alternatives rejected, and links opened on my Mac.”"
- **useful because:** The owner gets durable reasoning rather than a forgotten spoken answer. The relay can produce a short spoken conclusion, the browser can open or collect the cited sources, and the Mac can write a local card that the pendant can later replay or revise. This makes consequential research auditable without forcing the owner to remember which conversation contained it.
- **path:** relay-realtime → browser-extension → mac-planner → pendant → unified
- **model tier:** background model for synthesis and card maintenance; realtime only for the initial question and replay request
- **latency:** Speak the answer within 3 seconds; save the card and open cited sources within 10 seconds.
- **cost:** About $0.02–$0.08 per card, dominated by source extraction and synthesis; subsequent replay is nearly free.
- **security:** Store cards locally in the owner's workspace with source URLs and redacted excerpts, not full authenticated page contents. Never treat a cited source as permission to submit an action. Provide explicit delete/export controls and label model inferences separately from quoted evidence.
- **missing:** A decision-card data model with conclusion/evidence/alternatives/provenance fields; A browser citation extraction result that returns stable URLs and bounded excerpts; A Mac note/file writer that can update a card atomically and expose it to relay replay

### "“Prepare this web form for me, but do not submit it: read the fields aloud in one short summary, save a recoverable draft on my Mac, and let me approve or discard it from the pendant.”"
- **useful because:** This bridges the browser's authenticated reach and the pendant's physical presence without turning voice into an accidental submission. The owner can dictate or request a draft while away from the keyboard, inspect the exact intended values, and approve later; discard remains possible even if the Mac or browser link drops.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → unified
- **model tier:** realtime for concise field-summary conversation; background for normalization and validation of the draft
- **latency:** Draft extraction in under 8 seconds; spoken summary under 4 seconds; approval result within 10 seconds.
- **cost:** About $0.01–$0.05 per draft, mostly field normalization; no model call is needed for unchanged fields.
- **security:** Never transmit passwords, payment-card numbers, one-time codes, or hidden fields to the relay. Store drafts encrypted locally with a short expiry. Approval must bind to a page/session hash and exact field hash so a changed page cannot receive an old approval. Submission remains a separate, explicit operation.
- **missing:** A browser form-field read/write/draft primitive with sensitive-field classification; A Mac-side encrypted ephemeral draft store and exact-hash receipt; A pendant approval/discard command that carries the draft hash, not free-form speech

### "“I’m about to go offline. Package the task I’m in so I can continue it from the pendant and resume on my Mac later, including the next step, open references, unsaved local files, and what must not be repeated.”"
- **useful because:** Today a dropped link leaves the owner with scattered tabs, half-written files, and uncertainty about whether a step already ran. This creates a human-readable continuity packet: the pendant carries a tiny spoken checkpoint, the relay stores the durable handoff, and the Mac atomically stages local files and browser references. On return, it resumes from the checkpoint instead of rerunning side effects.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** background model for summarizing and checking idempotency; realtime only for the owner's short capture command and resume confirmation
- **latency:** Capture acknowledgement immediately; package within 15 seconds; resume inspection within 5 seconds of reconnection.
- **cost:** About $0.02–$0.10 per handoff, dominated by summarizing open work; file staging and receipts are local.
- **security:** Exclude credentials, page bodies, microphone audio, and secrets by default. Record hashes and completed-step receipts rather than copying sensitive state. Resume must show the exact pending side effect and require the owner's separately configured policy for any mutation; expired packets must be deletable from all surfaces.
- **missing:** A user-facing handoff schema joining Mac files, browser references, completed action receipts, and a next-step narrative; A browser export of stable tab/session references without page secrets; A pendant-sized checkpoint/restore protocol and relay retention/expiry controls


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: bookmark-to-resumable-context across pendant/Mac/browser/relay; a real USB-attached pendant bench health report using the synthetic bidirectional fixture; and an opt-in authenticated-work deadline tripwire that uses the existing pendant alert inbox. The live Mac bridge and browser are online; the pendant remains USB-testable but LTE-unregistered.

**Biggest unknown:** The key missing seams are still concrete rather than conceptual: a bounded, receipt-correlated serial diagnostic action; semantic Mac context (document identity/selected text); and an opted-in browser session delta/watch API. I did not re-request the already-pending semantic tool or denied permissions.

