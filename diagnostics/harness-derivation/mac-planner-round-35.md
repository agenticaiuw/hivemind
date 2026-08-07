# Harness derivation — mac-planner — round 35

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make the pendant sound as clear as possible, and keep it clear when the connection is bad.”"
- **useful because:** This turns the owner's 24 kHz request into an everyday behavior rather than a lab setting: the pendant, relay, and Mac jointly negotiate the best profile, monitor quality, and recover without making the owner repeat themselves.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use gpt-realtime-2.1 only for the live voice path; use a cheaper background worker for telemetry aggregation, codec regression reports, and weekly quality summaries. The pendant performs local buffering and profile switching; relay performs negotiation and jitter control; Mac bridge supplies a diagnostic loop and dashboard evidence.
- **latency:** Profile selection within 1 second at session start; switch only at an Opus frame boundary. Keep conversational first audio under 500 ms; tolerate up to 2 seconds of buffered repair during a transient LTE-M gap, then degrade to a lower bitrate rather than stall.
- **cost:** Realtime inference cost is unchanged; relay bandwidth is the dominant variable, approximately 1.5–2x the current uplink audio bytes for the high-quality profile. Background quality reports are cheap batch work; local packet metrics add negligible cost.
- **security:** Audio remains sensitive. Do not upload raw diagnostic recordings by default; send packet loss, jitter, frame counters, negotiated profile, and hashed job IDs. Require explicit owner opt-in to attach a short sample to a bug report. Dashboard must show retention and provide deletion of any captured sample.
- **missing:** A shared audio capability-negotiation schema and versioning between firmware and relay; Firmware support for adaptive bitrate/frame duration and a bounded jitter buffer with offline concealment; Relay-side per-session quality controller and packet-loss telemetry; Mac bridge/dashboard support for a live quality receipt and a one-click redacted diagnostic bundle; A hardware capture path that genuinely supports 24 kHz input; the current microphone path is 15,625 Hz; Automated audio conformance tests across fallback profiles

### "“Let me move between my pendant and Mac without restarting the conversation—continue speaking on whichever device I’m using, and keep the same context and audio state.”"
- **useful because:** Today the pendant is the live voice surface and the Mac is an action surface; moving between them risks a new session, duplicated context, or lost audio. A live, resumable handoff would let the owner start a thought while walking, then continue reviewing evidence or approving an action at the Mac without repeating themselves.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use gpt-realtime-2.1 only for the active conversational stream and handoff phrase detection. Use a cheaper background model to compact the prior turn into a handoff capsule and reconcile late events. The relay is the session authority; pendant and Mac bridge are interchangeable endpoints.
- **latency:** Detect an intentional handoff in under 1 second and attach the new endpoint within 2 seconds. Preserve at most 1–2 seconds of buffered audio; if the old endpoint disappears, resume from the last acknowledged turn rather than replaying the entire conversation.
- **cost:** Small incremental realtime cost for endpoint-control events; context cost is reduced by sending a compact signed handoff capsule instead of replaying the full transcript. Bandwidth is dominated by the active audio stream, not handoff metadata.
- **security:** A nearby Mac must not silently inherit a private pendant conversation. Pair endpoints to the owner’s authenticated session, show the target app/window and a visible handoff state, and expire handoff capsules quickly. Never expose microphone audio to the Mac unless the owner explicitly starts or accepts the handoff; action approvals remain bound to the authenticated session.
- **missing:** A relay-owned live-session registry with endpoint leases, sequence numbers, and resumable turn checkpoints; A signed compact handoff capsule containing conversation state, pending action, audio sequence, and provenance—not a raw transcript dump; Pendant protocol support for handoff/return events and acknowledgement of the last played and last heard frames; Mac bridge support for attaching to a live session, presenting the capsule, and routing audio without opening the microphone until explicitly activated; A conflict policy for simultaneous endpoints, reconnects, duplicate speech, and stale approvals; A dashboard indicator and recovery control showing which endpoint currently owns listening and playback


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160 DK audio path with a production pendant audio front end that can capture 24 kHz (or 32 kHz) wideband I2S and provide a hardware sample-rate clock independent of the modem; pair it with a low-power codec/ADC and enough SRAM/CPU headroom for simultaneous 24 kHz Opus encode and decode. Keep the ESP32 bridge as the physical audio output for the first revision, but define an explicit negotiated format: capture rate, Opus mode/bitrate, frame duration, and playout rate.
- **owner gets:** The owner gets noticeably clearer speech in both directions instead of a 15.625 kHz capture path being upsampled and called superwideband; the pendant remains usable while the modem is transmitting and does not stutter when replies arrive.
- effort: High: board spin, codec clock/power design, Zephyr I2S/Opus pipeline changes, RF/audio regression testing, and an A/B listening test. A staged prototype can use the existing board's playback side while validating the negotiated protocol before hardware arrives.  ·  risk: Higher sample rate and concurrent codec work can cause underruns, heat, battery drain, or modem contention. Recover by capability negotiation falling back to the current 16 kHz uplink/24 kHz downlink profile, with sequence numbers and concealment for lost frames; never switch formats mid-stream without an explicit boundary.
- cost: Prototype hardware roughly $20–$60 BOM increase (codec, mic, power/clock parts), plus engineering cost. Network/API cost rises modestly with bitrate (roughly 1.5–2x uplink audio bytes); use the expensive realtime model unchanged and avoid sending silence.  ·  latency: 24 kHz Opus at 20–40 ms frames should reduce perceived codec delay versus the current 60 ms decode frame, but encoding and LTE-M airtime may increase. Target end-to-end first audio under 500 ms and fallback if jitter exceeds a bound.
- security: Raw microphone audio still traverses LTE-M and relay; retain current job/pipeline identifiers, encrypt transport, and do not persist raw frames by default. Negotiation metadata is low sensitivity but should be included in receipts for debugging.
- depends on: A firmware-side audio negotiation contract shared by pendant, relay, and Mac test harness; An end-to-end audio conformance test with packet loss/jitter simulation; A battery-current measurement fixture and an owner listening test


## What it asked for

### `s11-gsg5` (skill) — adaptive_audio_profile
- does: At session start and on sustained link degradation, negotiate and switch among versioned audio profiles (24 kHz wideband, current fallback, and a low-bitrate emergency profile) only at packet boundaries. Maintain a bounded jitter buffer, packet sequence counters, PLC for missing Opus frames, and expose compact quality counters to the relay. Revert to high quality after a stable hysteresis window.
- must be on-device because: The pendant must continue playing intelligible audio during a dropped or delayed LTE-M link, must schedule codec/I2S work against local clocks, and must avoid a server-driven format switch that arrives too late. Local fallback and concealment survive a relay reconnect.
- trigger: Session start; relay profile-offer event; local jitter/packet-loss thresholds; button ending the conversation flushes metrics and closes the profile.
- storage: No audio persistence. Store only current profile and rolling counters (sequence, lost, concealed, jitter estimate, underrun count), under 1 KB in RAM/retained session state; optionally append a compact session receipt to microSD only when diagnostics are enabled.
- RAM budget: Target 8–16 KB additional RAM: 4–8 KB jitter/packet metadata and compressed frame references, 2–4 KB profile state/telemetry, remainder for queues. This must be validated against the 211,608 B application RAM and current ~87% single-core simultaneous Opus load; if it fails, require the hardware refresh rather than silently dropping frames.

## Its own summary

Round 35 produced a new end-to-end audio proposal rather than repeating the browser/briefing backlog. I recorded (1) a hardware change for genuine 24 kHz capture with independent clocks and sufficient codec headroom, (2) a cross-surface “make it clear under bad connectivity” capability, and (3) queued a pendant-resident adaptive_audio_profile skill for packet-boundary profile switching, jitter buffering, PLC, and compact telemetry. I also told relay-realtime and faculty-action the concrete constraints: current capture is 15,625 Hz, playback is 24 kHz/60 ms, and simultaneous Opus consumes about 87% of one core.

**Biggest unknown:** Whether the current firmware has enough real RAM/CPU margin for even a small jitter buffer and adaptive encoder, and what exact relay audio framing/protocol is deployed. I still need the implementation owners to establish a shared profile schema, run packet-loss/jitter and battery measurements, and validate a staged fallback path before claiming 24 kHz superwideband end to end.

