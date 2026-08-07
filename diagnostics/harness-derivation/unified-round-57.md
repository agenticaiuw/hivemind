# Harness derivation — unified — round 57

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio pipeline reality** — 24 kHz TTS rendering is already measured end-to-end through Mac bridge (24,000 Hz mono, 3.43 s, 0 clipped samples), but a recent relay response was explicitly delivered late after reconnection; pendant also held offline alerts/bookmarks. Therefore the missing product layer is not PCM generation but authenticated continuity/health semantics across link loss.
  - evidence: GET /pipeline returned job_165a9c9a-e5e3-4e29-b500-2fad63115ab9: TTS 24 kHz mono PCM and relay accepted response, alongside detail 'arrived late and was forwarded after the connection came back'; other runs show held alerts from pendant-offline-store and bookmark link_at_capture=down.

## Capabilities it proposed

### "Make the pendant sound like a reliable phone: test my microphone and speaker end to end, choose the best voice mode for the current LTE conditions, and tell me when the call is actually healthy."
- **useful because:** Today the 24 kHz claim is only a decode setting; capture, modem contention, relay transcoding, bridge output, and Mac playback are not verified as one path. This gives the owner a one-button preflight and a live, understandable quality state instead of discovering broken audio mid-conversation.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use firmware/relay DSP and deterministic measurements for the preflight and governor; use the cheaper background model to summarize the test. Reserve realtime for the spoken result and live call only.
- **latency:** A local loopback and link probe should complete in 3–5 seconds; quality state updates within one audio frame (60 ms). Spoken summary under 1 second after the test.
- **cost:** Negligible model cost for measurements; roughly $0.001–$0.01 only when a background model turns telemetry into a human summary. Main cost is LTE test traffic and R2 telemetry, capped to a few seconds and opt-in retention.
- **security:** Transmit only synthetic test tones, packet statistics, and aggregate quality metrics—not recorded speech. Require explicit confirmation before uploading a real voice sample. Dashboard shows the active codec/rate and provides delete/export for test telemetry.
- **missing:** A negotiated audio-session protocol shared by firmware, relay, and bridge (codec, sample rate, frame size, bitrate, sequence/repair policy).; A deterministic acoustic test fixture or owner-guided spoken phrase with acceptance thresholds for intelligibility, latency, and packet loss.; Firmware support for a short local loopback tone/recording and a user-visible health result; current single LED/button needs a defined gesture/state vocabulary.; Relay and Mac bridge endpoints that can echo timestamped test packets and return a signed end-to-end receipt.; A production pendant audio design; current nRF9160 DK has 15,625 Hz capture and is explicitly prototype hardware.

### "When I say “repeat that” or “go back ten seconds,” replay exactly what you just said from the pendant—even if LTE has dropped—and then continue from the same conversation point."
- **useful because:** A wearable conversation should be recoverable when speech is missed in noise, interruption, or a brief link failure. Today the owner can receive late audio or an offline alert, but cannot reliably revisit the exact spoken passage and resume without asking the system to reconstruct it.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use deterministic local audio buffering and timestamp alignment on the pendant; use the relay for durable transcript/segment indexes and the Mac bridge for conversation-state reconciliation. Use a cheap background model only to label segment boundaries or summarize, never for the low-latency replay decision.
- **latency:** Replay begins locally within 150 ms of the gesture or phrase. Reconciliation with relay/Mac state may take seconds and must not block playback. Preserve at least the last 60 seconds locally.
- **cost:** No realtime-model cost for replay; small relay metadata writes. Optional transcript labeling costs well under $0.01 per conversation and can be batched.
- **security:** The local replay buffer contains recent private speech. Keep it encrypted, bounded, and automatically expired; never upload raw replay audio unless the owner explicitly asks to save it. Dashboard must show and delete retained segments. Any transcript sent to the relay needs the existing sensitivity policy.
- **missing:** A firmware-local encrypted rolling playback ring buffer with segment timestamps and an eviction policy.; A bidirectional segment-clock protocol tying pendant playback offsets to relay transcript turns and Mac pipeline receipts.; A phrase/gesture parser that distinguishes replay requests from ordinary conversation without sending audio to the cloud first.; A resume marker so the next response starts after the replayed segment rather than duplicating or skipping context.; Acceptance tests for replay accuracy during LTE loss, reconnect, barge-in, and overlapping speech.

### "Let the conversation follow me safely: if I take the pendant off or move near my Mac or phone, move the audio to the device I am actually using, then return to the pendant when I pick it up—without repeating or exposing speech to the room."
- **useful because:** The owner cannot have a truly wearable assistant today because audio is tied to one LTE pendant path. This would make a single conversation survive charging, desk use, and movement while preserving the exact turn position and preventing duplicate playback.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Use deterministic proximity/session arbitration and audio sequence tracking; use no model for routing. Use a cheaper background model only to generate a short handoff receipt when a session changes devices.
- **latency:** Detect an intentional handoff in 1–2 seconds; mute the old output before enabling the new one, with no more than 300 ms of silence. Never hand off on a transient signal fluctuation.
- **cost:** No per-turn model cost. Small relay/session metadata overhead. Hardware cost depends on adding BLE/UWB proximity support and a reliable wear sensor.
- **security:** Audio must not jump to an untrusted nearby device. Pair devices cryptographically, require an explicit first-time approval, and use a local wear/gesture confirmation for ambiguous handoffs. Keep room-speaker routing disabled by default; retain only encrypted sequence metadata, not audio.
- **missing:** Authenticated multi-output session arbitration in the relay and Mac/iOS clients.; A pendant wear/removal signal or deliberate handoff gesture; RSSI alone is insufficient.; A shared audio sequence clock and replay protection across pendant, Mac, and iOS.; Client-side audio ducking/mute acknowledgement before the relay changes its target.; A privacy-visible handoff indicator and a recovery path when the target device disappears mid-transfer.


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio session contract and health receipt. At call start the pendant sends capabilities (capture/playback clocks, Opus modes, frame size, modem record ceiling); relay selects a mode and returns a signed session id. Timestamped sequence numbers, queue depth, PLC/FEC decisions, and bridge playback acknowledgements are emitted as compact telemetry. The Mac bridge and dashboard render one state (healthy/degraded/reconnecting), while the pendant gives a short local indication. A 3-second synthetic preflight exercises uplink, relay decode/encode, downlink, and ESP32 playback before enabling wideband mode.
- **owner gets:** The owner can trust that “24 kHz” means an end-to-end usable call, and gets an early warning or automatic fallback before lost speech—not a silent failure caused by LTE-M half duplex contention.
- effort: Medium-high: protocol schema and compatibility tests, firmware ring-buffer/telemetry changes, relay session state, bridge acknowledgement, dashboard state, and fault-injection tests.  ·  risk: Older firmware may not understand negotiation; preserve a versioned 16 kHz fallback and fail closed to the last known-good mode. Telemetry bugs could hide loss, so include monotonic counters and periodic signed receipts.
- cost: Low API cost; modest LTE overhead (target <1 kbps telemetry). Engineering cost is mostly cross-component integration and test fixtures.  ·  latency: Preflight adds 3–5 seconds only when requested or after repeated faults; normal call adds one frame of buffering at most.
- security: Session receipts must be authenticated and contain no audio content. Do not retain synthetic audio; aggregate counters expire quickly.
- depends on: production audio compatibility target and acceptance thresholds; a deterministic relay↔bridge audio echo/ack endpoint; firmware implementation of negotiated codec/rate and bounded telemetry; audio link fault injection in CI


## What it asked for

### `c10-iyoh` (context) — end-to-end audio acceptance thresholds
- why: The current device facts expose a concrete mismatch (15,625 Hz capture, 24 kHz decode, LTE contention) but no definition of what the owner considers a successful call.
- would change: I would set the preflight/governor thresholds and decide whether to favor intelligibility, continuity, or wideband quality; without this I can only propose instrumentation and safe fallback, not a shippable mode policy.

