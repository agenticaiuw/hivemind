# Harness derivation — unified — round 129

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What was that thing I saw earlier about the pendant project?”"
- **useful because:** The pendant can mark a moment while worn, the Mac can capture the active app/browser evidence, and the relay can index it so the owner can recover a fleeting thought without remembering which surface contained it. This is a cross-surface episodic memory, not another scheduled brief.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** background for indexing and retrieval; realtime only for the spoken query and concise answer
- **latency:** Marking must be under 300 ms; answer within 3 s, with a short cited source list available on request.
- **cost:** Roughly $0.01–$0.05 per indexed day and under $0.01 per retrieval; storage/indexing dominates, not realtime inference.
- **security:** Active-tab titles, selected snippets, and voice markers leave the Mac only when marked or explicitly queried. Secret fields must be redacted locally; never index passwords or full page contents by default. Ask before exporting a memory.
- **missing:** pendant moment-marker firmware event; Mac active-context snapshot route with local redaction; relay episodic index and source-linked retrieval

### "“Don’t interrupt me unless something truly needs a decision; otherwise queue it and tell me why you waited.”"
- **useful because:** A single attention policy can arbitrate browser findings, Mac job completions, reminders, and pendant signals. It prevents the wearable from becoming noisy while still surfacing deadlines and irreversible decisions at the right moment.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** cheap background classifier for urgency; realtime model only when the owner engages or a high-confidence urgent event is detected
- **latency:** Classify events within 10 s; urgent delivery within 2 s; quiet events appear in a review queue by the next interaction.
- **cost:** About $0.005–$0.03 per event batch; event storage and notification delivery dominate.
- **security:** The policy needs calendar/task metadata and job state. Keep content minimized, explain every interruption with source and reason, and require confirmation for sends, purchases, deletion, or other irreversible work.
- **missing:** owner-configurable interruption policy; attention queue with urgency/expiry and quiet hours; pendant LED/haptic or audio indication for queued vs urgent items

### "“If the Mac is connected by USB, let me keep talking when the network drops, then reconcile the conversation when it comes back.”"
- **useful because:** This turns today’s physically connected nRF9160 and ESP32 into a useful continuity path: local capture/playback and a small pending transcript can preserve an interaction through a dropped relay link instead of silently losing it.
- **path:** pendant → bridge → mac-planner → relay-realtime
- **model tier:** small local model or deterministic VAD/transcription for buffering; realtime tier only for live cloud conversation after reconnection
- **latency:** Local acknowledgement under 150 ms; reconnect reconciliation under 5 s after link recovery.
- **cost:** Near-zero inference cost if buffering PCM/events only; optional local transcription is under $0.01 per incident. USB transfer and flash writes dominate power.
- **security:** Buffer only encrypted short-lived audio/transcript segments, with a physical clear action and automatic expiry. Never upload buffered audio without explicit session scope; expose a visible/LED recording state.
- **missing:** USB serial audio/event transport between nRF9160, ESP32, and Mac; encrypted bounded offline spool; reconnect merge protocol with duplicate suppression; local privacy/clear gesture

### "“When I say I’m on my way, keep track of the real-world plan and tell the people or services involved only if the evidence shows I’m actually late or blocked.”"
- **useful because:** The owner currently gets reminders and browser/Mac actions, but no system watches whether a spoken commitment, calendar event, travel state, and actual progress agree. A single hive mind could combine the pendant’s presence and voice, private browser reservations, Mac calendar, and relay timing to detect a genuine exception rather than nagging.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** background model for plan-state inference; realtime only for the owner-facing exception
- **latency:** Update plan state within 2 minutes; deliver a high-confidence exception within 10 seconds of detection.
- **cost:** $0.01–$0.08 per active plan, dominated by periodic browser/calendar reads; no model call on unchanged state.
- **security:** Location, travel, and third-party contact data are sensitive. Keep the plan private by default, never notify anyone automatically, and require confirmation before sending a status message. Store only derived state and expiry, not continuous audio or location.
- **missing:** commitment-to-plan state machine; optional pendant presence/location or travel signals; cross-source temporal correlation; exception-only notification and approval flow

### "“Let me hand a task to the pendant while I’m away from the Mac, and have it return with exactly what changed, what it could not do, and what I need to decide.”"
- **useful because:** Today the wearable, Mac, browser, and relay are mostly request/response surfaces. This would let the owner issue a durable mission from the pendant, allow the Mac and authenticated browser to work independently, and return a structured result that distinguishes completed, blocked, and approval-required work.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** cheap background planner and verifier; realtime model only to interpret the initial spoken goal and summarize the receipt
- **latency:** Acknowledge handoff in 1 second; work asynchronously; deliver completion or blockage immediately when the mission reaches a terminal state.
- **cost:** $0.02–$0.20 per mission depending on browser/model steps; external-site latency dominates.
- **security:** Mission scope must be explicit and bounded. Never allow an inferred mission to send, buy, delete, or publish without a fresh approval. Receipts must include before/after evidence and redact secrets.
- **missing:** pendant-originated mission IDs over USB/LTE; checkpointed multi-surface mission state; terminal verifier that tests the intended outcome; compact spoken receipt with approval continuation

### "“When I’m in a conversation, quietly capture only the decisions and promises that involve me, then let me review them on the Mac before anything is sent or scheduled.”"
- **useful because:** The pendant is physically present when the owner cannot type. It could provide a private, low-friction way to preserve decisions from a meeting or hallway conversation, while the Mac and browser turn only owner-approved items into reminders, drafts, or calendar changes.
- **path:** pendant → bridge → relay-realtime → mac-planner → browser-extension
- **model tier:** small background transcription/extraction model for candidate decisions; realtime model only when the owner asks for a spoken recap
- **latency:** Local capture indication under 150 ms; candidate extraction within 60 seconds; review workspace ready within 2 minutes.
- **cost:** $0.03–$0.30 per hour of processed speech, dominated by transcription; process only explicit sessions, not ambient audio.
- **security:** This is inherently sensitive and must be opt-in per conversation with a physical indicator and a clear gesture. Do not identify or store other speakers unless needed; encrypt audio temporarily and retain extracted candidates only until review. Nothing gets sent or scheduled automatically.
- **missing:** explicit start/stop capture gesture and privacy indicator; speaker/owner relevance filtering; decision/promise extraction schema; Mac review workspace with approve/edit/reject actions


## Changes it proposed to its own stack

### `firmware` — Add a USB-serial diagnostic mode to the nRF9160 pendant that emits timestamped button, VAD, PCM frame counters, link state, queue depth, and reset reason, and accepts a bounded test command to play a generated tone or loopback marker. The ESP32 bridge should emit matching frame counters so the Mac can correlate both chips without parsing ad-hoc logs.
- **owner gets:** They can plug in the real worn hardware today and know whether a missed word came from the microphone, bridge, serial transport, relay, or model instead of guessing. It also makes the 24 kHz audio path verifiable before LTE registration exists.
- effort: Medium: firmware event schema, serial framing, bridge correlation, and a Mac-side decoder; no cloud dependency.  ·  risk: Diagnostic mode could expose audio metadata or interfere with normal streaming. Gate it behind a physical long-press and compile/runtime mode flag; recover by reset to normal mode.
- cost: No API cost; approximately 2–6 KB flash and under 2 KB RAM. Negligible power while USB-connected.  ·  latency: Adds one compact metadata frame per audio block, under 1% serial overhead at the current USB test link.
- security: Raw audio must never be included in diagnostics by default; use counters and hashes, and require an explicit test command for generated audio.
- depends on: Define the 24 kHz audio acceptance criteria; Mac serial reader for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA

### `integration` — Create a cross-surface 'evidence capsule' protocol: a pendant marker creates a signed capsule ID; the Mac attaches a redacted active-app/browser snapshot, the relay stores a short-lived index, and later retrieval returns source/time/confidence rather than injecting whole pages into every prompt.
- **owner gets:** A spoken 'mark that' becomes a dependable breadcrumb across the physical pendant, private browser sessions, and Mac work, without flooding every conversation with old context or leaking unrelated page contents.
- effort: Medium-high: event contract, local redaction, durable index, retrieval API, and expiry UI.  ·  risk: Wrong or overbroad snapshots could capture sensitive material. Default to title/URL/selection only, show a local capture indicator, support immediate deletion, and expire capsules automatically.
- cost: Low storage and background-model cost; roughly cents per week for ordinary use.  ·  latency: Marker acknowledgement is immediate; enrichment can finish asynchronously in 1–3 seconds.
- security: Capsules are encrypted, scoped to the owner, and carry provenance plus sensitivity labels; no cross-session browser data sharing without explicit scope.
- depends on: Pendant marker event; Mac active-context snapshot with redaction; Relay storage/index route


## What it asked for

_Nothing._
