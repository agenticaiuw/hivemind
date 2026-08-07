# Harness derivation — relay-realtime — round 156

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Record a quick voice note from the pendant and turn it into a reminder with a title, time, and context."
- **useful because:** Hands-free capture is a daily-driver feature. It turns fleeting thoughts into reliable follow-ups.
- **path:** pendant → relay → mac-bridge
- **model tier:** realtime for capture; cheaper transcription/structuring; Mac creates the reminder
- **latency:** <2s to confirm capture; transcription and reminder creation within ~10s
- **cost:** Small audio upload and transcription; reminder creation cheap
- **security:** Voice content is sensitive; retention should be short and user-controlled. Avoid sending audio beyond what’s necessary.
- **missing:** On-device buffering for dropped links; A reliable audio capture pipeline state context; Reminder creation route/tool wired to this flow

### "“When I’m in a meeting, quietly keep track of decisions and action items, then after it ends tell me only what I personally need to do and put the tasks in the right apps.”"
- **useful because:** The pendant is the only node physically present during a meeting, while the Mac and authenticated browser sessions can identify the meeting, relevant documents, and destination task systems. Today the owner must manually record notes and reconstruct commitments afterward.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime tier only handles a start/stop utterance and urgent spoken feedback; a cheaper background model performs diarization, decision/action extraction, and deduplication; Mac/browser agents execute app writes.
- **latency:** Acknowledge capture start/stop in under 500 ms; incremental private summaries may arrive every 30–60 seconds; post-meeting result within 2 minutes.
- **cost:** Approximately $0.05–$0.30 per hour depending on audio transcription and summary length; destination writes and browser control dominate latency, not the realtime reply.
- **security:** Meeting audio and transcripts leave the pendant for processing and may contain other people’s confidential information. Store encrypted, retain only extracted commitments by default, visibly indicate capture with the pendant LED, and require explicit spoken confirmation before sending or publishing any task/comment.
- **missing:** A pendant capture mode with local LED state and loss-tolerant audio chunking; A relay background transcription/summarization worker and post-meeting trigger; Meeting identity and document context from Calendar/browser sessions; Typed task/comment destinations plus an approval-aware commit step

### "“If something urgent happens in any of my signed-in services, interrupt me on the pendant in the least disruptive way; otherwise hold it and give me one spoken digest when I’m free.”"
- **useful because:** The owner is usually away from the Mac, and important events can currently remain trapped in Mail, Calendar, browser tabs, or Mac apps until they manually check each surface. A worn-device arbiter would make urgency actionable without turning every notification into noise.
- **path:** browser-extension → mac-planner → mac-vision → relay → pendant → dashboard
- **model tier:** Background model classifies and groups events; realtime model is used only to phrase a short interruption and handle the owner’s reply. Deterministic rules handle quiet hours, urgency classes, and deduplication.
- **latency:** Urgent event-to-pendant alert under 10 seconds; nonurgent events batched into a digest at the next detected availability window.
- **cost:** Roughly $0.01–$0.08 per day for event classification and grouping, dominated by polling/webhook volume; speech costs are negligible because alerts are short.
- **security:** The relay would receive metadata from authenticated services and infer availability from audio/device state. Keep content minimization and encrypted per-service tokens, never read message bodies for low-urgency events, provide a physical mute gesture, and make alert policy inspectable and reversible.
- **missing:** A persistent event ingress from Mac and browser sessions (push/webhook or safe polling); A durable relay queue with urgency grouping, quiet-hours, retry, and deduplication; Pendant push audio/LED notification and a local mute/availability signal; A cross-service policy model that learns the owner’s urgency preferences without exporting raw content

### "“Screen calls for me: if an unknown caller rings, answer with my short introduction, ask why they’re calling, tell me a one-sentence summary on the pendant, and connect me only when it sounds important.”"
- **useful because:** The pendant is the only interface the owner can reliably reach while away from the Mac, yet the Mac/browser may hold contacts, calendars, and call sessions. This would prevent interruptions and spam while preserving urgent human contact; nothing today can combine call audio, identity, conversational triage, and a wearable accept/reject gesture.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime speech model for call turn-taking and a short spoken summary; cheaper background classification checks contact/calendar context and records a transcript only when configured. Deterministic allow/deny rules should handle known contacts and emergency numbers.
- **latency:** Ring-to-screening answer under 2 seconds; caller response latency under 700 ms; owner summary within 3 seconds of the caller’s explanation.
- **cost:** About $0.05–$0.40 per screened call, dominated by telephony audio and realtime model duration; known-contact bypasses are nearly free.
- **security:** This processes private phone audio and could misclassify emergencies or impersonate the owner. Never auto-screen emergency services or allow the system to claim it is the owner; announce an AI receptionist, encrypt/discard recordings by policy, maintain a visible call state, and make connect/reject explicit via the physical button.
- **missing:** Telephony ingress/egress or a Mac phone-call bridge with bidirectional audio; A relay realtime call session manager resilient to handoffs and disconnects; Contact/calendar lookup from the Mac/browser and emergency-number bypass rules; Pendant call-state UX with accept/reject/hang-up and privacy indication


## Changes it proposed to its own stack

### `relay` — Expose a relay-level capability inventory route (like /capabilities) and a typed intent routing endpoint that accepts an intent label and payload, logs it, and forwards to the appropriate downstream tool without the relay inventing its own protocol.
- **owner gets:** More reliable handoffs: the owner’s requests don’t get lost or misrouted, and we can report what’s supported right now.
- effort: Medium: add route, schema validation, logging, and mapping to existing plan/execute paths.  ·  risk: Incorrect mappings could misroute actions. Mitigation: conservative allowlist and receipts.
- cost: Small; mostly validation and logging.  ·  latency: Minimal overhead per request.
- security: Needs strict auth; intent payloads must be validated to prevent injection.
- depends on: Existing plan/execute infrastructure

### `firmware` — Add a small offline voice-note buffer and retry queue on the pendant (using microSD if available) so short captures survive LTE/USB drops and upload later with metadata (timestamp, duration, sequence).
- **owner gets:** The pendant becomes dependable: you can capture ideas even with spotty connectivity.
- effort: Medium: storage format, queue management, retry logic, and upload handshake.  ·  risk: Storage corruption or queue growth. Mitigation: bounded retention, checksums, and compaction.
- cost: Minimal BOM change; some power/storage overhead.  ·  latency: None during capture; retries happen opportunistically.
- security: Sensitive audio at rest; should be encrypted and auto-expire.
- depends on: Capture pipeline state context; Server support for resumable uploads

### `hardware` — Add a low-power haptic actuator and a physical three-position privacy switch to the pendant, with firmware events for silent-alert, active-listening, and transmit-disabled states. Expose those states to the relay so every realtime workflow can fail closed when the switch is off and acknowledge urgent events without audio.
- **owner gets:** The owner can receive a discreet alert in a noisy place and can prove—by touch—that the pendant is not listening or transmitting. This enables safe call screening, meeting capture, and future ambient workflows without forcing the owner to look at a phone or trust an invisible software state.
- effort: Moderate hardware revision plus GPIO/firmware driver, battery characterization, relay state propagation, and a small set of end-to-end usability tests.  ·  risk: Added power draw, enclosure changes, accidental switch movement, and new firmware states. Recover with a default-off transmit state after reboot, watchdog-safe GPIO handling, and a software diagnostic that reports physical switch position.
- cost: Roughly $2–$8 in components and assembly at prototype quantity; haptic pulses add tens of milliwatts only while active, while the switch is effectively zero draw. No meaningful API cost.  ·  latency: Sub-100 ms local haptic response; relay acknowledgement remains network-dependent but is not required for privacy state enforcement.
- security: Strongly improves privacy by making transmit disable a physical, locally enforced state; switch position must override any server command and be included in audit receipts.
- depends on: A pendant firmware event/state protocol; A relay device-presence and push channel; Audio pipeline session state propagation


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities and one hardware change: private meeting commitment capture with task handoff, cross-service urgent-interruption arbitration, AI call screening through the pendant, and a physical haptic/privacy-switch revision. The translation idea was correctly rejected as already present in the backlog and was not restated. The main missing pieces are durable event/audio ingress, background workers, telephony integration, explicit pendant push/state handling, and physical privacy feedback—not another discovery pass.

**Biggest unknown:** Which authenticated services and telephony path the owner is willing to connect first; that determines whether event ingress should use browser-session polling, Mac APIs, webhooks, or a dedicated phone bridge.

