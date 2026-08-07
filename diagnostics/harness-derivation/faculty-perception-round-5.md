# Harness derivation — faculty-perception — round 5

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-capture-path** — The pendant currently captures microphone audio at 15,625 Hz, encodes uplink Opus at 16 kHz/16 kbps, while playback decodes 24 kHz frames and resamples to a 31,250 Hz I2S wire clock. Therefore the requested 24 kHz superwideband path is not currently end-to-end symmetric.
  - evidence: get_hardware_spec(all): audio.mic and audio.playback; describe(audio)
- **audio-link-reliability** — During simultaneous owner speech and agent speech, LTE-M uplink 16 kbps plus downlink 24 kbps saturates the half-duplex link; a recent call dropped 388 uplink packets, approximately 7.8 seconds of speech.
  - evidence: get_hardware_spec(all): network.measured
- **audio-compute-budget** — Pendant Opus encode takes about 15.0 ms per call and decode about 25.4 ms per 60 ms packet; both together consume roughly 87% of one Cortex-M33 core.
  - evidence: describe(audio)
- **audio-io-topology** — The pendant has exactly one I2S peripheral, full duplex with byte-identical TX/RX configuration, so any higher-quality audio path must share that peripheral. The ESP32 bridge then resamples 31,250 to 44,100 Hz and its A2DP source is SBC-only at fixed 44.1 kHz stereo.
  - evidence: get_hardware_spec(all): io and bridge
- **audio-retention** — The relay retains roughly 100 recordings in R2 for 30 days; the retention sweep is disabled. The owner's rule permits SD writes only as an upload-failure buffer, not routine recording.
  - evidence: get_hardware_spec(all): stack and storage

## Capabilities it proposed

### "“Keep my voice intelligible when you talk at the same time, and use the best audio quality the link can actually sustain.”"
- **useful because:** The current nominal audio settings demonstrably lose about 7.8 seconds of owner speech during duplex contention. This would turn the requested 24 kHz path into a usable experience: preserve owner speech first, raise quality only when measured LTE-M headroom allows it, and leave a short spoken quality receipt when conditions force a downgrade.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime for the live relay's low-latency negotiation and speech; firmware and relay control loops should be deterministic, not model calls. Background dashboard summaries use a cheaper non-realtime model.
- **latency:** No extra conversational turn. Firmware decisions within one 20–60 ms audio frame; relay control within 100 ms. Dashboard quality history can lag by minutes.
- **cost:** Negligible model cost during calls (rule-based control); modest telemetry storage and WebSocket bytes. A background summary is a cheap model invocation only when requested.
- **security:** Audio remains on the existing TLS WebSocket; telemetry should contain packet counts, jitter, codec mode, and timestamps—not transcript or raw audio. Require confirmation before exporting call-quality history. Retain telemetry no longer than audio policy.
- **missing:** A negotiated audio-profile protocol shared by nRF9160 firmware, Cloudflare relay, and ESP32 bridge; A sender-side congestion/packet-loss estimator and a bounded profile ladder (24 kHz, 16 kHz, robust fallback); Relay-side prioritization/FEC or retransmission policy that cannot block uplink speech behind downlink audio; Bridge firmware support for profile changes while preserving its fixed 44.1 kHz A2DP output; End-to-end test instrumentation and a dashboard quality receipt

### "“If my voice was lost or clipped, tell me immediately and recover the missing turn instead of silently continuing.”"
- **useful because:** Today the system can lose many seconds of owner speech during duplex contention while the conversation appears to continue. The owner should receive an immediate, trustworthy indication of what was missing, and the system should recover by replaying only the affected short utterance or asking for a concise repeat. This is different from merely changing bitrate: it makes loss observable and prevents silent misunderstanding.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic firmware and relay logic for sequence tracking, gap detection, and replay requests; realtime only for the live conversation's concise recovery prompt. Background models are unnecessary unless the owner later requests a loss report.
- **latency:** Detect a gap within one or two audio frames (roughly 60–120 ms); notify or request a repeat within 250 ms when possible. Recovery should add no more than one short conversational turn.
- **cost:** No routine model cost beyond an occasional realtime recovery utterance. Small overhead for sequence metadata and a bounded retransmission cache; dashboard reports can use inexpensive batch processing.
- **security:** The relay must retain only a short encrypted rolling audio cache during an active call, delete it at call end, and never expose raw clips in the dashboard by default. Recovery prompts and gap events should be logged without transcript unless explicitly requested. Replays and repeats must not trigger duplicate actions downstream.
- **missing:** Monotonic audio sequence numbers and timestamps carried through pendant, WebSocket relay, and bridge; A bounded encrypted rolling cache on the pendant or relay with explicit call-end deletion; Relay logic that distinguishes packet loss, late packets, and bridge playback underruns; A conversation-state guard that marks the affected user turn as untrusted until recovered; A pendant haptic/LED or spoken loss notification that works without waiting for a model response; A dashboard receipt showing which segment was recovered, repeated, or unavailable


## Changes it proposed to its own stack

### `hardware` — For the wearable revision, separate modem and audio workloads: retain an LTE-M modem but add a low-power audio MCU/DSP with native 24 kHz capture/playback (or replace the prototype with an nRF5340-class application MCU plus modem), add a real stereo audio codec/clock, and add a fuel-gauge IC. Keep the single-button interaction, but remove the prototype's 15.625 kHz mic and ESP32's mandatory 31.25→44.1 kHz conversion from the quality-critical path.
- **owner gets:** They get genuinely consistent 24 kHz wideband speech, fewer dropped words while the agent speaks, predictable battery warnings, and a smaller wearable that does not spend almost an entire Cortex-M33 core on simultaneous Opus work.
- effort: High: board spin, RF/audio certification, power profiling, firmware port, codec/clock driver, and bridge integration. Prototype with an external codec board before committing to enclosure.  ·  risk: New clock-domain and RF/power interactions can introduce audible glitches or reduce battery life. Keep the current nRF9160/ESP32 firmware as a fallback image and A/B test recorded fixtures plus live LTE-M duplex calls before rollout.
- cost: Roughly +$8–$20 BOM at low volume for audio codec, audio MCU/DSP, fuel gauge, clocks, and board changes; modest additional quiescent draw, offset by lower application-CPU duty cycle. No per-call API cost.  ·  latency: Potentially lower and more stable audio latency; hardware buffering should stay under 10 ms, with codec processing budgeted below the current 25.4 ms decode path.
- security: Adds firmware and peripheral attack surface; require signed MCU images, secure boot chain, and keep raw audio off persistent storage except the existing upload-failure buffer policy.
- depends on: A negotiated audio-profile protocol and congestion policy; Measured prototype power/audio benchmarks; A defined 24 kHz end-to-end wire format between pendant, relay, and bridge


## What it asked for

### `c3-0yy5` (context) — current 24 kHz implementation status
- why: The hardware facts establish the prototype's mismatch, but I cannot tell whether an in-progress firmware/relay branch already implements capture-side 24 kHz, adaptive profiles, or bridge switching. I need to avoid proposing work that is already shipped and to target the actual remaining gap.
- would change: If a 24 kHz branch exists, I will audit its runtime negotiation and loss behavior instead of proposing a hardware redesign; if not, I will treat the protocol and measurement plan as prerequisites.

