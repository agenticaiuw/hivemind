# Harness derivation — mac-planner — round 95

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep my pendant conversation clear when the LTE-M connection gets crowded, and return to full-quality 24 kHz audio automatically when it recovers."
- **useful because:** Today the measured duplex link drops about 7.8 seconds of uplink while the agent speaks. This would preserve the owner's words first, degrade gracefully instead of going silent, and recover superwideband without making them manage audio settings.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime model only interprets the QoS profile when needed; deterministic firmware/relay rules handle adaptation. Use a cheaper background model for post-call quality summaries, never for the live control loop.
- **latency:** QoS telemetry every 2 seconds; profile changes applied within one 60 ms frame plus one relay scheduling interval (<300 ms target). No extra conversational model turn.
- **cost:** Negligible inference cost during calls; roughly a few hundred bytes of telemetry per minute. Optional post-call summary costs a small background-model invocation and is not required.
- **security:** Telemetry contains timing and quality counters, not microphone content or transcripts. Keep raw audio unchanged in the existing encrypted WebSocket; dashboard should redact session identifiers. Never store audio merely to diagnose loss.
- **missing:** Implement the requested pendant duplex_audio_congestion_guard skill; Relay-side adaptive profile scheduler that reserves uplink capacity and changes downlink Opus bitrate/frame profile; A negotiated Opus profile contract covering 24 kHz/60 ms and a low-bandwidth fallback with hysteresis; Dashboard quality timeline and a completion receipt proving when quality changed and recovered; End-to-end test using the measured half-duplex contention case

### "When I interrupt you or the connection drops during a spoken answer, preserve the unfinished turn and let me resume it later from the pendant or Mac without repeating myself."
- **useful because:** Today an interruption can leave the owner with a clipped answer and no reliable way to recover the missing context. This would make conversation resilient: the system remembers the exact assistant sequence and the owner's interruption point, then offers a concise continuation rather than replaying or guessing.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Use deterministic sequence tracking and a cheaper background model for reconstruction. Use the realtime model only when the owner explicitly asks for a natural-language continuation or clarification.
- **latency:** Detect interruption within one audio frame (<60 ms), persist a resumable turn within 1 second, and make a resume available immediately after reconnect. Reconstruction can take up to 2 seconds outside the live turn.
- **cost:** Minimal storage and telemetry per interrupted turn. One small background-model call only when audio is genuinely missing and a textual reconstruction is needed; do not retranscribe or regenerate intact audio.
- **security:** Persist only encrypted transcript fragments, sequence ranges, and redacted metadata with a short retention period. Never resume a turn aloud automatically if the pendant has been idle in a public setting; require a button press or explicit phrase. Mac receipts must identify whether content was original or reconstructed.
- **missing:** A cross-surface resumable-turn protocol with globally unique turn and audio sequence IDs; Pendant local marker for button/voice interruption and last-heard playback sequence; Relay durable checkpointing that stores encrypted turn metadata and bounded missing ranges; Mac planner endpoint that renders a continuation receipt and lets the owner choose resume, summarize, or discard; A deterministic reconciliation test for duplicate packets, reconnects, and partial TTS delivery


## Changes it proposed to its own stack

### `relay` — Add a deterministic duplex budget governor to the live WebSocket: reserve a minimum uplink budget for pendant capture, classify each 60 ms downlink frame by urgency, and when acknowledgements/loss exceed thresholds, stop enqueueing nonessential TTS frames, switch the transcoder to the negotiated fallback profile, and emit a signed session QoS event. On recovery, require 10 seconds of hysteresis before restoring 24 kHz. The relay should also attach a short continuity marker (sequence range and profile transition) so the pendant and Mac receipt can say exactly what was degraded.
- **owner gets:** The pendant stops competing with the assistant's speech for the same constrained radio link. The owner hears a complete answer more often, and if a transition still occurs they get an honest, concise indication rather than unexplained silence or clipped speech.
- effort: Medium: relay scheduler/transcoder changes, firmware profile negotiation, deterministic contention tests, and a small dashboard panel. No new model training.  ·  risk: Bad thresholds could make speech sound lower quality too often or cause profile flapping; hysteresis, bounded profiles, and a simulated loss test recover safely. If the relay crashes, the current fixed 24 kHz path remains the fallback. Never discard uplink frames solely to improve downlink quality.
- cost: No meaningful API increase; modest relay CPU and a few QoS events per call. Firmware RAM about 1.5 KB for counters/profile state; no raw audio retention.  ·  latency: Profile changes add at most one 60 ms frame and relay scheduling (<300 ms target); recovery waits for a 10-second stable window by design.
- security: Encrypted audio path remains unchanged. QoS events carry sequence numbers/counters only, with rotating session IDs and short retention.
- depends on: pendant duplex_audio_congestion_guard skill; A negotiated Opus profile identifier shared by firmware and cloud-relay/opusTranscode.js; POST /pipeline/events accepting typed QoS events and durable audio receipts; An end-to-end half-duplex contention test harness

### `hardware` — For the wearable revision, separate radio/control from audio timing: retain the LTE-M modem but add a small audio companion (or an SoC with a hardware audio/DSP block and DMA) responsible for I2S capture/playback, Opus encode/decode buffering, and congestion counters. Give it independent 24 kHz playback timing and at least 256 KB audio-working RAM, while the modem MCU handles TLS and policy.
- **owner gets:** Full-quality speech will not collapse merely because the pendant is simultaneously encoding their voice, decoding a reply, and servicing the modem. It creates enough headroom for the adaptive path instead of making the owner choose between clarity and connectivity.
- effort: High and product-level: schematic/PCB/firmware port, power and RF validation, enclosure redesign, and a real wearable prototype rather than the current DK.  ·  risk: More components increase BOM, board area, and power; a new codec/DSP can introduce clock drift or driver bugs. Retain the current fixed-path firmware as a manufacturing test mode and run A/B field trials before switching default hardware.
- cost: Rough prototype delta: approximately $8–$25 BOM depending on codec/MCU choice, plus board/NRE; likely 10–30 mW additional audio-domain power, offset by putting the companion to sleep between frames. No per-call API cost.  ·  latency: Should reduce encode/decode contention and jitter; target <60 ms added buffering, with deterministic I2S clocks.
- security: Audio remains inside the pendant's encrypted path; add secure boot/firmware signing for the companion and avoid exposing raw PCM over debug UART in production.
- depends on: Measured QoS traces from the current nRF9160 prototype; Negotiated adaptive Opus profiles and contention test results; Power-budget and enclosure study; Secure firmware-update chain covering both processors


## What it asked for

### `s15-rzms` (skill) — duplex_audio_congestion_guard
- does: Tracks rolling uplink packet loss, downlink underruns, modem retransmission hints, and decode CPU time during a call; emits a compact QoS frame to the relay and locally switches between 24 kHz/60 ms playback and a lower-bandwidth fallback when loss crosses thresholds. Restores superwideband only after hysteresis, avoiding oscillation.
- must be on-device because: Only the pendant can observe microphone queue underruns, decoder timing, and the exact moment audio becomes unintelligible; it must protect capture even when the LTE-M link or relay is degraded.
- trigger: Call start, every 2 seconds while streaming, and immediately on a 3-frame underrun or websocket reconnect.
- storage: No user audio persisted. Store only the current profile and 16-byte rolling counters in RAM; persist one last-known-safe profile byte in 16-byte settings/NVS so reboot starts conservatively.
- RAM budget: ~1.5 KB: 2 x 256-byte counter windows, timestamps/ack state, and profile state; well below the 211,608 B application RAM, though codec CPU headroom remains the constraint.

