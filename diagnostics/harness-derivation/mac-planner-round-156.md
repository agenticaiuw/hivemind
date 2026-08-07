# Harness derivation — mac-planner — round 156

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Run a full pendant audio check, fix what you can, and tell me whether it is ready to wear.”"
- **useful because:** This turns the currently USB-attached prototype into a one-command, end-to-end acceptance test: pendant capture/decode, serial transport, ESP32 resampling/Bluetooth output, and relay audio plumbing. It can catch silence and clock drift before the owner relies on it in the street.
- **path:** pendant → mac-planner → relay-realtime → mac-terminal → dashboard
- **model tier:** background for the test and measurements; realtime only to explain the short spoken result
- **latency:** 30–90 seconds for a complete test; under 2 seconds for the final spoken verdict
- **cost:** Usually under $0.03 per run; almost all cost is optional analysis of the captured telemetry, not device I/O.
- **security:** The test uses synthetic audio or a fixed local phrase and must not open the microphone. Serial logs and audio metrics stay local unless the owner explicitly enables upload. Firmware flashing or changing profiles should be reported and reversible.
- **missing:** A privileged USB-serial test runner that can address /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A deterministic pendant loopback/test-tone command and ESP32 bridge counters for underruns, resampler overruns, and A2DP disconnects; A small result schema and a repair playbook (restart bridge, reset stream, then optionally apply a known-good profile); A dashboard view of pass/fail thresholds and the raw receipt

### "“When I leave a meeting, make me the follow-up packet.”"
- **useful because:** Pressing the pendant's end button can mark the meeting boundary without opening a microphone. The Mac can identify the just-finished Calendar event, gather the relevant browser tabs and local notes, and produce a concise action list plus drafts—solving the gap between a conversation ending and work actually being captured.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** background synthesis; a tiny realtime acknowledgment only when the button event arrives
- **latency:** Acknowledge in 1 second; leave the packet within 2 minutes, with incremental status if browser reads are slow
- **cost:** About $0.05–$0.20 per meeting depending on tab count and synthesis length; source reads dominate, not the button event.
- **security:** Calendar, notes, and authenticated tabs may contain sensitive material. Keep excerpts local by default, attach URL/title provenance, redact secrets, and never send email or submit forms. Draft creation is allowed; sending remains a deliberate owner action.
- **missing:** A pendant event carrying a meeting-end marker over the current USB serial path (and later LTE); A correlation service that maps the marker to the most recent Calendar event and active browser session; A read-only meeting capsule schema joining Calendar, Mail/Notes, browser tab extracts, and timestamps; A local workbench artifact with editable next actions and unsent drafts

### "“Keep my conversation alive when I move between USB and LTE.”"
- **useful because:** Today the pendant is physically testable over USB but not relay-registered. A presence-aware handoff would let a conversation start locally, survive cable removal or a bridge restart, and resume on LTE later without losing queued audio, transcript context, or the owner's place.
- **path:** pendant → mac-planner → relay-realtime → mac-vision → dashboard
- **model tier:** deterministic state machine and cheap background reconciliation; realtime model only for the ongoing voice turn
- **latency:** Detect attach/detach in under 2 seconds; resume within 5 seconds when the alternate path is available
- **cost:** Negligible model cost during healthy handoff; roughly $0.01–$0.05 only if a recovery summary must be generated.
- **security:** Bind a session to a device nonce and authenticated Mac bridge, encrypt queued transcript/audio, expire queues quickly, and show the owner which transport is active. Never duplicate a command during retry; mutations need the existing job receipt/undo semantics.
- **missing:** A device-presence protocol for USB serial and LTE registration with monotonic sequence numbers; A relay session multiplexer that can switch transports without duplicating frames; Encrypted, bounded local queue storage on the Mac and pendant, with replay receipts; A user-visible transport indicator and recovery summary

### "“Before I send this important message, let me rehearse it with you as the recipient.”"
- **useful because:** The system would gather the actual draft and relevant thread from Mail or an authenticated browser tab, identify the recipient’s likely concerns, and role-play a short exchange through the pendant. The owner gets confidence and a tightened draft without sending anything.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement
- **model tier:** Realtime for the spoken role-play; background model for extracting thread facts and improving the draft
- **latency:** Prepare context in 5–15 seconds; conversational turns under 1.5 seconds
- **cost:** About $0.10–$0.40 per rehearsal, dominated by realtime turns and thread-context synthesis
- **security:** Mail and logged-in pages are sensitive. Keep the source thread local where possible, explicitly label simulated replies, never send or modify the original draft, and discard the rehearsal transcript by default.
- **missing:** A read-only cross-source thread bundle with citations and sensitivity labels; A dedicated rehearsal session type that cannot call send/submit actions; A compact spoken handoff from browser/Mac context into relay realtime; A user-visible way to compare the original and revised draft

### "“Let this physical tag start the right work mode.”"
- **useful because:** A tap on an NFC tag at the desk, door, car, or workshop could switch the whole hive into a named context: open the right Mac apps and files, select the correct browser workspace, change the pendant audio behavior, and announce the current objective. This is faster and less error-prone than explaining context every time.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic routing for the tag and routine; cheap background model only when the owner asks for a context-specific plan
- **latency:** Recognize and acknowledge the tag within 1 second; complete the workspace transition within 5 seconds
- **cost:** Near-zero model cost for ordinary tags; under $0.02 when generating a new routine from a natural-language label
- **security:** Tags must carry opaque signed IDs, not secrets. Require explicit enrollment, show the resulting actions, and prevent a tag from silently sending messages, buying, deleting, or submitting forms.
- **missing:** NFC or equivalent proximity reader on the pendant (the current exposed I2C bus could support one); Signed tag enrollment and context profiles; A multi-surface context transition transaction with rollback; A pendant-to-Mac event bridge that works while USB-attached and later over LTE

### "“When two of my sources disagree, show me the conflict and help me resolve it.”"
- **useful because:** The hive would compare facts across Calendar, Mail, local files, and logged-in browser pages—such as two different deadlines or meeting locations—then present the evidence and a proposed resolution through the pendant and Mac. Today each source can be read, but no one reliably notices that they contradict one another.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Background model for entity matching and contradiction ranking; realtime only for the owner’s clarification dialogue
- **latency:** Run on demand in 10–30 seconds; spoken conflict explanation under 3 seconds once prepared
- **cost:** About $0.05–$0.25 per investigation, mostly proportional to the number of source excerpts
- **security:** Only inspect explicitly authorized sources, retain source URLs/timestamps and short quotations, redact unrelated private content, and never overwrite a source without an explicit owner command.
- **missing:** A normalized fact model with source, timestamp, confidence, and validity interval; Cross-source entity/date/location matching and contradiction scoring; A conflict workbench with side-by-side evidence and a chosen resolution; A clarification event that can update a project or create a reminder without mutating source systems


## Changes it proposed to its own stack

### `mac-harness` — Add a USB device supervisor to the Mac agent that discovers the nRF9160 and ESP32 serial paths by USB identity rather than suffix, opens no microphone, records framed health/transport telemetry, emits attach/detach events into /pipeline/events, and exposes a test/repair job with durable receipts. It should refuse to send arbitrary firmware commands: only the explicit diagnostic verbs are allowed, while still honoring the owner's maximum-access execution policy for normal Mac actions.
- **owner gets:** The owner can plug in the prototype and immediately know whether the pendant is actually usable, instead of guessing from an LED or discovering a silent Bluetooth path during a real conversation. Cable moves and bridge resets become visible events rather than lost sessions.
- effort: Medium: USB identity discovery, two serial readers, framed parser, watchdog, and a small diagnostic command set; firmware and bridge need counters/test verbs.  ·  risk: Serial framing bugs could interfere with the development firmware or leave a port held open. Use exclusive-open with short leases, never write except during an explicit diagnostic job, release on timeout, and retain raw logs locally for recovery.
- cost: No recurring model cost; roughly 1–3 MB local logs per day if verbose, capped and rotated. Engineering cost is firmware/bridge instrumentation plus Mac agent work.  ·  latency: Attach/detach detection under 2 seconds; negligible impact on ordinary Mac actions. A test run takes tens of seconds.
- security: USB serial can expose firmware control, so isolate diagnostic verbs, bind devices by VID/PID/serial, and redact raw audio. Do not upload logs by default.
- depends on: A stable framed diagnostic protocol in pendant and bridge firmware; An implementation (not just the granted schema) for a Mac serial read/write route; A relay event consumer that can associate device presence with a live session


## What it asked for

_Nothing._
