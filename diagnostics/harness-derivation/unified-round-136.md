# Harness derivation — unified — round 136

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "During a meeting, let me quietly ask the pendant “who is this, what did we decide, and what should I say next?” Use my live calendar, the current private browser tab, and the conversation I just heard to give a one-sentence whispered answer; afterward, turn only confirmed decisions into a reviewable draft of follow-ups."
- **useful because:** This is the first genuinely wearable-plus-browser capability: the pendant is an always-available private channel while the Mac/browser can see the meeting and authenticated context. It reduces cognitive switching without sending or committing anything automatically.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime for the whispered low-latency question; a cheaper background model for post-meeting extraction and draft follow-ups.
- **latency:** Under 2 seconds for a short spoken answer; 1–3 minutes for the post-meeting draft.
- **cost:** Realtime turn dominated by a few seconds of audio/context; roughly $0.01–$0.05 per interruption. Background extraction roughly $0.01–$0.08 per meeting depending on transcript length.
- **security:** Meeting audio and private page text leave the device only when this mode is explicitly enabled. Never send messages or create calendar events without confirmation; show source snippets and a transcript-retention toggle.
- **missing:** A meeting-mode session that can receive a bounded rolling audio window from the pendant; A way to bind the active calendar event and selected browser tab to that session; Post-meeting decision extraction with explicit uncertainty and draft-only output

### "When I say “compare what I was promised with what I got,” inspect the relevant logged-in page and my local notes, reconcile the two, and tell me the mismatches with citations and a ready-to-send (but unsent) escalation draft."
- **useful because:** People lose hours proving that an order, appointment, invoice, or support promise changed. This uses browser-held sessions for private evidence and the Mac for local notes, while the pendant gives a fast spoken result; no single node can assemble the evidence safely.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Cheaper background model for extraction and comparison; Realtime only for the owner’s short query and spoken summary.
- **latency:** Initial spoken triage within 5 seconds; evidence bundle and draft within 60 seconds.
- **cost:** About $0.02–$0.15 per case, dominated by page extraction and document comparison; no recurring cost unless the owner asks.
- **security:** Only inspect the explicitly selected tab/note scope. Mask account numbers and secrets in relay logs. Draft must show every cited before/after field and require confirmation before sending.
- **missing:** Cross-source evidence bundle with stable citations and redaction; Local-note search route exposed to the planner; A draft-only escalation artifact with field-level provenance

### "Keep one conversation alive as I move between my desk and outside: if the pendant loses USB/Mac reach, preserve the exact turn and its pending evidence, then resume through the relay when a registered link returns—telling me whether the answer is fresh, delayed, or still waiting. Never replay a command or duplicate an action."
- **useful because:** Today the pendant is physically testable over USB but not LTE-registered, so a dropped link turns a spoken interaction into ambiguity. A transport-independent conversation receipt would make the system trustworthy in the real moments when the owner walks away from the Mac, without pretending an answer arrived live.
- **path:** pendant → relay-realtime → mac-planner → dashboard → iOS
- **model tier:** Realtime only for the active voice turn; no model call for handoff, deduplication, or status. Use a cheaper background model only if the owner asks to summarize delayed work.
- **latency:** Local USB handoff under 300 ms; reconnect status under 2 seconds; resumed response within the normal link round trip.
- **cost:** Negligible API cost for receipts and deduplication; roughly $0.001 or less per handoff in storage/egress. Model cost occurs only for a genuinely new turn.
- **security:** Bind each turn to a device/session key and monotonic sequence number; encrypt queued audio/results; expire stale sensitive content. Require confirmation if a delayed result would trigger an external action.
- **missing:** A transport-neutral conversation envelope with monotonic turn IDs and replay protection; A live pendant/USB transport adapter and eventual LTE device registration; A user-visible freshness state for delayed, superseded, and completed results

### "If I say “I’m not safe” to the pendant, start a private countdown, ask me for a spoken check-in, and—only if I fail to cancel—send a prewritten status and my latest known location to my chosen emergency contact. Let me cancel with a button press or voice phrase, even if the Mac is asleep."
- **useful because:** A wearable is the only surface that can hear a distress phrase and accept a physical cancellation when the owner cannot reach a screen. The relay can stay awake, while the Mac/browser can resolve the chosen contact and location permissions; this is a materially different safety function, not another task queue.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → iOS → dashboard
- **model tier:** No model for the emergency state machine; Realtime only for speech recognition and a short confirmation prompt. Use deterministic templates for the outbound status.
- **latency:** Detect and acknowledge within 1 second; escalation only after the owner-configured countdown.
- **cost:** Usually near-zero model cost; a few cents at most for a voice turn and notification delivery. Ongoing relay/device connectivity is the dominant cost.
- **security:** This must be opt-in, testable, and fail-closed against false escalation. Encrypt contact/location data, never infer danger from mood, require an explicit phrase, expose a loud local test mode, and require confirmation during setup—not during an active incident.
- **missing:** A pendant-local distress state machine and cancel gesture; A trusted-contact and location-permission store spanning iOS/Mac and relay; A notification provider with delivery receipts and explicit test/simulation mode; A registered independent pendant link; current USB attachment is not sufficient when the owner is away from the Mac


## Changes it proposed to its own stack

### `hardware` — Add a small always-on companion board in the wearable enclosure with a real-time clock, inertial sensor, and secure nonvolatile event counter; have it timestamp button presses, link drops, and audio underruns, then forward signed event markers over the existing UART when the nRF9160 reconnects. Keep raw audio off this board.
- **owner gets:** The pendant could explain failures honestly (“your question was captured at 8:42, playback dropped for 1.2 seconds”) and recover the right interaction after a dead zone, instead of silently losing trust. Timestamps also make meeting and task history reliable when the Mac is asleep.
- effort: Moderate hardware spin and firmware integration: low-power MCU/RTC/IMU, signed event schema, UART driver, relay ingestion, and dashboard timeline.  ·  risk: Extra board, battery drain, enclosure complexity, and clock drift. Recover with a feature flag and fall back to nRF9160 timestamps; never block audio on marker writes.
- cost: Roughly $4–$12 in components at prototype volume and tens of microwatts in standby; negligible API cost, with small D1 event storage.  ·  latency: No audio-path delay if markers use a nonblocking ring buffer; reconnect upload adds under a second.
- security: Signed markers improve tamper evidence but introduce a device key that must be provisioned and rotated; no raw audio or message content is stored.
- depends on: A durable unified event/receipt schema spanning pendant, relay, and Mac; A reconnect uploader for offline markers; A production wearable board rather than the current nRF9160 DK prototype

### `hardware` — Replace the ESP32 A2DP bridge in the wearable product with a modern Bluetooth LE Audio-capable companion (LC3, bidirectional headset profile), retaining a small wired debug path but removing the fixed 44.1 kHz SBC-only conversion from the production audio route. Add a hardware mute switch that physically disconnects the microphone power rail.
- **owner gets:** The owner would get clearer, lower-latency speech through ordinary LE Audio earbuds and a microphone that can be guaranteed off—not the current prototype’s SBC-only 44.1 kHz bridge, expensive resampling, and software-only privacy assumptions.
- effort: High: select and certify a LE Audio chipset, redesign RF/power/enclosure, port the audio protocol, validate coexistence with the nRF9160, and add a physical mute-state report to the relay.  ·  risk: Bluetooth interoperability, antenna layout, certification, and battery life can regress. Keep the current ESP32 path as a debug fallback and ship a hardware revision behind a capability flag.
- cost: Prototype increase roughly $8–$25 for the companion/RF/mute components; modest firmware work and no per-call API increase. Power should improve versus the always-on SBC bridge, but must be measured.  ·  latency: Potentially removes one resampling/A2DP buffering stage and should reduce end-to-end delay, subject to LE Audio buffering and RF testing.
- security: A physical mic disconnect gives a stronger privacy guarantee; new Bluetooth pairing keys and firmware signing must be provisioned securely.
- depends on: A production wearable board replacing the nRF9160 DK; End-to-end 24 kHz audio acceptance tests; A LE Audio-capable earbud compatibility matrix; A signed hardware mute-state event in the relay


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities and one hardware change. New proposals: (1) a private in-meeting whisper that combines the pendant’s rolling audio with the active calendar event and authenticated browser tab, then drafts sourced follow-ups; (2) a “compare what I was promised with what I got” evidence reconciliation across logged-in pages and local notes, with an unsent escalation draft; (3) transport-independent conversation continuity that preserves turn IDs and freshness across USB/Mac loss and later relay/LTE return. I also proposed a companion wearable event-marker board (RTC/IMU/signed counters) so link drops, button presses, and audio underruns become explainable receipts. The first two are connective wiring, not absent primitives; the missing work is the meeting session boundary, cross-source provenance, local-note search, and transport-neutral replay-safe envelopes. Current reality remains important: the nRF9160 and ESP32 are physically USB-connected and testable, while LTE registration is still absent.

**Biggest unknown:** Whether the owner wants meeting audio retained at all, and what exact privacy/retention boundary should govern a rolling meeting window. The queued context requests for audio acceptance, privacy behavior, and transport policy remain unanswered; those determine implementation details, but do not block the capability designs.

