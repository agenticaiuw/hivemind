# Harness derivation — mac-planner — round 171

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-permissions-and-hardware-readiness** — The Mac agent is now fully ready for computer use: Accessibility and Screen Recording are granted, input reachability verified, all listed automation permissions present, browser extension online with 9 tabs, relay reachable, and FULL_CONTROL_MODE remains enabled. The pendant and audio bridge are physically USB-connected but no serial exchange capability is available in this round, so real-device USB operation is still the largest practical gap.
  - evidence: GET /ops/status returned ready:true, accessibility.trusted:true, screenRecording.granted:true, automationMissing:[], relay.reachable:true, browser.online:true. The round context states both serial devices are physically connected and mac_serial_exchange remains pending.

## Capabilities it proposed

### "When I press the pendant's bookmark button, save what I was looking at on the Mac as a durable, private evidence capsule I can ask for later."
- **useful because:** A moment marker currently says only that something happened. This would capture the active browser page or foreground app, a redacted selected-text/clipboard excerpt, and timestamp together, so a fleeting idea, bug, or decision is recoverable without opening the Mac or speaking a long memo.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background for capsule extraction and redaction; realtime only for the spoken acknowledgement and later lookup
- **latency:** Acknowledge the button within 1 s; capture and persist within 5 s; later lookup under 2 s when the Mac and relay are online.
- **cost:** About $0.002–$0.01 per capture, dominated by optional extraction/summarization; raw page text should avoid a model call when a bounded excerpt is enough.
- **security:** The capsule can contain private page text or clipboard contents. Default to URL/title/app plus a short redacted excerpt, never passwords or secure fields; encrypt at rest, expire raw text, and require confirmation before sharing or sending it elsewhere.
- **missing:** A relay command/event that turns the existing offline_moment_bookmark into a Mac capture request; A typed Mac read of selected text/document identity beyond the current generic observation; A durable capsule lookup route and owner-configurable retention/redaction policy

### "Run a complete pendant audio diagnostic overnight, and in the morning give me a spoken pass/fail report plus a bug report file I can open in VS Code if anything regressed."
- **useful because:** The pendant is physically attached over USB today and the audio path has already had several subtle failures. This turns a low-level fixture into an owner-visible guarantee: it exercises both directions, correlates counters, preserves the exact failing evidence, and tells the owner whether their next call is safe.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** background/cheap model for threshold comparison and concise bug-report text; no realtime model needed unless the owner asks follow-up questions
- **latency:** Arm in under 10 s, run unattended for under 2 minutes, and deliver the morning result as one short spoken sentence plus an immediately available report.
- **cost:** Under $0.01 per run; almost all cost is optional report summarization, while fixture execution and counter comparison are local.
- **security:** The fixture must generate synthetic audio only and never persist microphone content. The report may include serial identifiers and filesystem paths; redact those from relay payloads and write the detailed report only to ~/AI-Pendant-Workspace. Opening VS Code is non-destructive; automatically changing firmware or deleting logs must never happen without an explicit request.
- **missing:** A USB-serial scheduler/transport from the Mac agent to /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay durable job that stores diagnostic runs and exposes pass/fail to the morning routine; A thresholded report formatter that links fixture counters to a specific firmware/build identity

### "While I am presenting or in a meeting, keep routine pendant alerts silent, but let a genuinely urgent event through and give me the rest as a catch-up when I am free."
- **useful because:** The Mac knows the foreground app and calendar context, the relay can rank events, and the pendant already has a durable alert inbox. Combining them prevents a low-value interruption at the exact moment it is costly while preserving urgent reachability and a reliable after-meeting queue.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background model for event ranking and meeting-state inference; realtime only for an urgent spoken alert
- **latency:** Update focus state within 2 s of a calendar/foreground change; deliver urgent alerts within 3 s; present the queued digest on the next explicit catch-up request.
- **cost:** Roughly $0.001–$0.005 per state transition and alert batch; most decisions are deterministic calendar/app rules, with model use only for ambiguous urgency.
- **security:** Calendar titles, browser URLs, and alert text are sensitive. Send the relay only a coarse state (meeting/presentation/free), urgency class, and expiry; keep event bodies on the Mac; never infer or announce meeting contents aloud. The owner must be able to clear the local latch offline.
- **missing:** A Mac state publisher that combines Calendar, foreground app, and browser tab signals into a coarse focus state; An urgency/expiry schema and relay policy that targets the existing offline_alert_inbox rather than creating another queue; A pendant-to-relay catch-up command and an owner-visible audit trail of suppressed versus delivered alerts

### "Use my pendant over its USB connection when cellular is unavailable: let me press the real button, speak through the attached audio bridge, and receive the same relay conversation with no LTE registration required."
- **useful because:** The hardware is live on this Mac now, but the current system treats the unregistered LTE device as absent. USB-tethered operation would make the real pendant—not a simulator—the fastest path to daily testing and an immediately usable fallback in dead zones, with the Mac acting only as transport.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** realtime for the voice turn; background for reconnect bookkeeping and telemetry compression
- **latency:** Button-to-session acknowledgement under 500 ms; audio round-trip under 1.5 s on the local USB path; automatic fallback/recovery after cable loss within 5 s.
- **cost:** No per-turn infrastructure cost beyond the normal realtime conversation; local USB framing and relay websocket are the dominant engineering work.
- **security:** USB serial is a local privileged boundary. Bind only to the two expected device identities, avoid arbitrary serial commands, encrypt the relay leg, and expose a clear LED/desktop indicator when audio is being forwarded. Never retain raw microphone audio after relay acknowledgement.
- **missing:** A tested Mac USB-serial transport for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay device mode that authenticates the USB bridge as a pendant session and multiplexes button, telemetry, uplink, and downlink audio; Cable-loss state handling that hands queued bookmarks/audio to the existing durable retry paths

### "When I ask the pendant “what am I waiting on?”, tell me which people, websites, or tasks are blocking me, using my calendar, recent mail, reminders, and open browser work—not just a list of messages."
- **useful because:** People lose more time reconstructing pending commitments than answering new ones. A cross-surface dependency view would turn scattered evidence into a short prioritized spoken answer, with the exact source and age of each inferred waiting item, and let me mark one resolved from the pendant.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background model for extracting commitments and matching replies; realtime only for the final spoken answer and a follow-up mark-resolved command
- **latency:** Refresh asynchronously every 30 minutes and on explicit request; answer within 4 seconds; marking resolved should reach the Mac and relay within 2 seconds.
- **cost:** $0.01–$0.05 per refresh, dominated by mail/browser text classification; deterministic deduplication and age calculations should run locally.
- **security:** Mail and authenticated browser content must remain on the Mac whenever possible. Send the relay only normalized commitments, parties, timestamps, confidence, and source handles; never read message bodies aloud unless explicitly requested. Mark-resolved must be reversible and logged.
- **missing:** A local commitment extractor spanning Calendar/Mail/Reminders and authenticated browser sessions; A durable dependency record with confidence, source handles, expiry, and reversible resolution state; A relay query/command for spoken waiting-on and mark-resolved operations

### "Let me say “reconstruct my last decision” and hear a cited timeline assembled from the pendant bookmark, the active Mac app, browser page, calendar event, and any note or file created afterward."
- **useful because:** A bookmark records a moment but not the reasoning chain. This would make the system useful for decisions made while moving between a meeting, a browser, and the Mac: it can distinguish what was observed, what was decided, and what action followed instead of inventing a summary.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background model for timeline stitching and uncertainty labeling; realtime only to answer the spoken query
- **latency:** Capture metadata within 3 seconds of a bookmark; build a reconstruction within 10 seconds; speak a one-sentence answer first and offer detail on request.
- **cost:** $0.01–$0.08 per reconstruction, mostly context selection and citation generation; raw event collection is local and cheap.
- **security:** This creates a sensitive cross-surface history. Default to local storage with encrypted, short-lived content, expose source-by-source deletion, and clearly label inferred links and missing evidence. Never include secrets from clipboard/password fields.
- **missing:** A shared event schema with monotonic timestamps and source provenance across pendant, Mac, browser, Calendar, Notes, and files; A bounded local event journal that can correlate creations/edits without retaining full document contents; A relay reconstruction endpoint returning citations, confidence, and explicit unknowns

### "If my Mac crashes, the network drops, or I move away from it, resume the unfinished task from the pendant: tell me exactly what was completed, preserve the staged files, and let me continue without repeating work."
- **useful because:** Today a desktop task can leave partial files, a browser session, and a spoken instruction with no single recovery point. A cross-node handoff would make interruption survivable: the relay keeps the intent and receipt, the Mac keeps atomic staged artifacts, and the pendant provides a concise recovery choice when it reconnects.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background model for summarizing state and selecting the next safe step; realtime only for the owner's resume/discard choice
- **latency:** Checkpoint after each meaningful action within 2 seconds; detect a lost Mac within 10 seconds; speak recovery choices within 3 seconds of pendant reconnection.
- **cost:** Under $0.01 per checkpoint for deterministic receipts; $0.01–$0.03 only when a language model must summarize a partial task.
- **security:** Staged files and browser session handles are sensitive. Keep content on the Mac, send the relay hashes and capability-scoped handles, expire abandoned checkpoints, and never resume an external send, purchase, deletion, or other irreversible action automatically.
- **missing:** A cross-node checkpoint protocol joining Mac action receipts, workbench transactions, browser session state, and relay intent IDs; A pendant reconnect/resume command that works offline until it can deliver the choice; A recovery planner that verifies preconditions and offers continue, inspect, or discard without duplicating completed actions


## What it asked for

_Nothing._
## Its own summary

Discovered the newly live Mac state: Accessibility and Screen Recording are granted, input reachability is verified, automation permissions are complete, browser bridge is online with 9 tabs, relay is reachable, and the Mac computer-use loop is enabled. I recorded four owner-facing capabilities: bookmark-to-screen evidence capsules, overnight bidirectional audio diagnostics with a VS Code bug report, focus-aware urgent-only pendant delivery, and USB-tethered real-pendant voice operation when LTE is unregistered. The highest-value one is USB-tethered operation: the actual pendant is connected today but cannot yet participate as a relay session.

**Biggest unknown:** The pending mac_serial_exchange capability is still unavailable. Until a bounded serial transport exists for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, I cannot verify or run the real pendant/bridge path from this Mac; everything else needed for desktop-side observation and automation is now live.

