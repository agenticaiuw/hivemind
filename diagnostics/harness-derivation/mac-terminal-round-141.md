# Harness derivation — mac-terminal — round 141

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **usb-serial-observability** — Live device discovery currently reports home-macbook-bridge online, Safari on Mac online, and cloudflare-contract-test offline; it reports no pendant or ESP32 serial endpoint. The granted Mac diagnostic schemas are unimplemented, so USB port existence/responding cannot be established from this agent.
  - evidence: discover(devices) returned only Safari on MacIntel, home-macbook-bridge, cloudflare-contract-test; calls to mac_read_diagnostics and mac_readonly_diagnostics returned 'tool was granted a schema but has no implementation yet'.

## Capabilities it proposed

### "“I’m stuck—look at what I’m doing and tell me the next step.”"
- **useful because:** A single pendant press should turn the currently active Mac app, browser page, and recent agent work into a grounded answer, without opening the microphone. The pendant gives an always-available trigger; the Mac can inspect the private UI; the browser can read authenticated context; the relay can speak the answer back. No individual node can see all of that.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Realtime only for the short spoken response; use a cheaper background model to normalize active-window/browser/job evidence before handing the compact evidence bundle to realtime.
- **latency:** Under 5 seconds from button press to first spoken sentence; 1–2 seconds for Mac/browser evidence collection, then the realtime answer.
- **cost:** Roughly $0.01–$0.05 per invocation depending on screenshot and speech duration; the expensive parts are UI vision and realtime audio, so omit screenshots when accessibility/page text is sufficient.
- **security:** Private active-window and authenticated-page content leaves the Mac only to the relay/model. Redact passwords, payment fields, and hidden tabs; never perform an action from this trigger, only advise. The spoken answer may be overheard.
- **missing:** A USB/LTE pendant button event bridge with truthful delivery status; A Mac snapshot that atomically captures active app/window, selected browser tab, and recent job IDs; A browser command to return the currently focused tab's cited text without navigation; A compact evidence envelope shared by Mac, browser, and relay

### "“Quiet mode for the next hour.”"
- **useful because:** The pendant is the only control the owner can reach while away from the keyboard. One press should coordinate the Mac's notifications/audio, the browser's non-urgent watchers, and the relay's spoken interruptions, then restore the prior state automatically. Today each surface can be quieted separately, so the owner still gets interrupted or forgets to restore settings.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Use a cheap background model—or no model—for state capture and timer expiry; realtime is only needed to acknowledge the request in one short sentence.
- **latency:** Immediate local acknowledgement under 300 ms over USB; Mac and relay state convergence under 2 seconds; automatic restoration at expiry.
- **cost:** Near-zero model cost; one short realtime acknowledgement only when speech is enabled. Engineering cost is state snapshots and restoration, not inference.
- **security:** Persist only the prior notification/audio/watch state and expiry. Never mute emergency/owner-selected alerts. If the USB link drops, the relay must mark the mode unknown rather than claiming it is active; restoration must be idempotent.
- **missing:** A pendant button event and local LED acknowledgement path; A shared focus-state lease with expiry and owner-selected exceptions; Mac actions for notification focus and audio state snapshot/restore; Browser watch scheduler pause/resume that preserves due times; Relay policy to suppress non-urgent speech while retaining emergency events

### "“I just left that meeting—what did I promise, and put the follow-ups where I’ll see them?”"
- **useful because:** A worn button immediately after a meeting can combine the Mac's active meeting window and local transcript/notes, authenticated browser tabs, and calendar metadata into an evidence-backed commitment list. The relay speaks the short answer; the Mac creates reminders or drafts only after showing the owner the extracted commitments. This closes the gap between remembering a meeting and actually following through, without requiring an open microphone.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → unified
- **model tier:** Use a cheaper background model to extract candidate commitments and deduplicate them against existing reminders; use realtime only to read the final 20-second summary or answer a follow-up.
- **latency:** Candidate extraction within 10 seconds; spoken summary within 15 seconds; reminder creation is a separate explicit confirmation step.
- **cost:** About $0.02–$0.15 per meeting depending on transcript length and screenshots; token volume dominates, so pass timestamped excerpts rather than whole transcripts.
- **security:** Meeting content and private browser pages are sensitive. Keep raw transcript on the Mac, send only quoted evidence and hashes upstream, redact credentials/attendees outside the meeting, and never create/send an external message automatically. Require confirmation for each reminder destination and due date.
- **missing:** A pendant post-meeting button event over USB today and LTE later; Mac connector for local meeting transcript/notes and active meeting identity; Browser extraction of the meeting's authenticated notes/transcript tab with citations; A commitment schema linking quote, person, due date, confidence, and suggested reminder; A confirmation UI/voice flow and idempotent reminder creation

### "“Read the thing I’m looking at, privately, and tell me what it means.”"
- **useful because:** The owner can be away from the keyboard or looking at a dense dialog, chart, or error that is not reliably extractable as webpage text. A pendant press should make the Mac capture the focused window, mac-vision OCR/describe only that region, and have the relay speak a short explanation through the wearable. This is not a generic computer-use action: it is an accessibility and comprehension channel that works without opening the microphone.
- **path:** pendant → mac-vision → mac-planner → relay-realtime
- **model tier:** Use a low-cost vision model for OCR/layout extraction and reserve realtime for the concise spoken explanation and follow-up question.
- **latency:** First spoken description in 4 seconds; under 10 seconds for charts or multi-region screens.
- **cost:** Approximately $0.01–$0.08 per request; screenshot tokenization/vision dominates, while speech is a small incremental cost.
- **security:** The focused window may contain secrets. Crop to the focused region, redact password/token-like strings locally, retain no screenshot after extraction, and visibly indicate when screen content is being sent upstream. Never click or type as a side effect.
- **missing:** A pendant press event that targets the currently focused Mac window; A Mac-vision endpoint for bounded focused-region OCR plus layout/chart descriptions; Local secret redaction before relay submission; A short-lived image/text evidence envelope consumed by relay-realtime

### "“Warn me only when something I’ve committed to is about to collide with something else.”"
- **useful because:** The owner’s real problem is not another morning summary; it is discovering too late that a browser task, calendar commitment, local reminder, and travel/meeting timing cannot all fit. A background agent should reconcile live calendar, authenticated task pages, Mac reminders and current location-free availability, then use the pendant only for a genuinely actionable collision with the two concrete choices. It must not nag about unchanged items.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → unified
- **model tier:** Cheap scheduled/background model for normalization and collision scoring; realtime only for the interrupt and a short clarification.
- **latency:** Run hourly or on source change; alert within 2 minutes of detecting a high-confidence collision; no response needed for ordinary updates.
- **cost:** About $0.01–$0.04 per scan with compact deltas; authenticated page extraction and calendar/task normalization dominate, not the spoken alert.
- **security:** Cross-source joins reveal work schedule and private accounts. Keep raw records on the Mac, send only candidate intervals and source citations, apply quiet hours, and never reschedule or cancel anything automatically.
- **missing:** A normalized interval/commitment schema spanning Calendar, Mac reminders, and authenticated browser task pages; Change-triggered or efficient delta polling rather than full-page scans; A collision scorer that explains the two conflicting commitments and confidence; A pendant interrupt policy with snooze/quiet-hours state and cited drill-down on Mac

### "“Handle this, but keep anything private on my Mac and tell me exactly what leaves it.”"
- **useful because:** The owner should be able to use the relay, browser, and Mac together without guessing whether a screenshot, tab, or file was uploaded. Before doing work, the system would classify each needed datum, run private extraction locally where possible, and show a compact spoken/visual egress manifest: source, fields, destination, and retention. This enables useful cross-surface work that is currently too opaque to trust.
- **path:** unified → mac-planner → mac-vision → browser-extension → relay-realtime → pendant
- **model tier:** Cheap local classifier for sensitivity and redaction; use the expensive realtime model only after the owner accepts the compact manifest and only with the minimized evidence bundle.
- **latency:** Manifest within 2 seconds for normal text and 5 seconds for a screenshot; execution starts immediately after the owner’s one-sentence confirmation.
- **cost:** Usually under $0.01 before execution; local classification is effectively free, while any accepted remote reasoning costs the underlying task’s normal inference amount.
- **security:** The manifest itself must not leak the sensitive values it describes. Default to local-only for credentials, health, financial, and private work data; hash or label fields in the preview; record an append-only egress receipt and allow the owner to revoke short-lived remote artifacts.
- **missing:** A sensitivity taxonomy and local redaction/classification service; A planner that can split a job into local-only and remote-minimized substeps; A preflight egress manifest rendered on Mac and acknowledged via pendant button; Relay-side enforcement that rejects payloads not matching the accepted manifest; Retention/deletion receipts for every remote evidence artifact


## What it asked for

_Nothing._
## Its own summary

Produced three new cross-surface capabilities: a pendant-triggered “I’m stuck” evidence brief, a timed coordinated Quiet Mode spanning pendant/Mac/browser/relay, and post-meeting commitment extraction with cited evidence and confirmed reminders. The strongest is the post-meeting flow: it uses the wearable trigger, private Mac/browser context, and relay speech to turn commitments into follow-through without opening the microphone. I also reported USB inspection limits to faculty-perception and recorded the live device-registry finding.

**Biggest unknown:** The USB serial reality is still unverified. The newly granted Mac diagnostic tools are schemas without implementations, so I still need an implemented narrowly scoped read-only serial-port probe (existence, permissions, and non-destructive open/response) for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA.

