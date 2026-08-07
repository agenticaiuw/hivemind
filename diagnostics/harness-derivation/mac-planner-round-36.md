# Harness derivation — mac-planner — round 36

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Let me keep talking naturally while I’m walking—even when LTE gets busy—and recover any dropped words without making me repeat myself.”"
- **useful because:** Today the pendant’s prototype audio path is narrowband on capture and loses substantial uplink speech when the agent talks at the same time. The owner should experience one continuous conversation: intelligible superwideband speech, graceful degradation in poor coverage, and automatic recovery from short radio gaps rather than silence, stutter, or repeated questions.
- **path:** pendant: capture 24 kHz audio, local VAD, bounded encoded recovery ring, modem-aware mode switching, and playback buffering → relay-realtime: authenticated codec negotiation, turn-aware uplink/downlink scheduling, packet-loss concealment and continuity bookkeeping → mac-planner: run an offline acoustic/LTE regression harness, visualize per-call quality receipts, and leave a concise failure explanation or firmware-test artifact → browser: not involved unless the owner explicitly asks to continue a browser task during the call → dashboard: expose codec mode, loss, underruns, and fallback events without retaining raw audio
- **model tier:** Realtime handles only the live speech interaction; deterministic firmware/relay logic handles buffering, VAD, scheduling, and concealment. A cheaper background model can summarize quality receipts or cluster recurring radio failures.
- **latency:** Normal speech should add no more than 60 ms of jitter buffering. A brief coverage gap should recover within about 1–2 seconds; mode fallback should occur within one speech turn. Quality-report generation can take seconds after the call.
- **cost:** Negligible model cost during the call beyond the existing realtime session; post-call diagnostics use a small background invocation. Main costs are engineering and a production digital microphone/audio codec, roughly $5–15 of components at volume, plus modest battery and LTE airtime increases.
- **security:** Audio stays in the existing authenticated TLS path; the local recovery ring is encrypted, bounded, and erased at call end. Quality telemetry should contain counters and codec state, not speech. Firmware and relay mode commands require authenticated signing to prevent malicious downgrade or resource exhaustion.
- **missing:** A production 24 kHz-capable microphone/codec and clocking decision; Pendant firmware implementation of radio-aware codec selection and bounded recovery buffering within the current RAM/CPU budget; Relay hooks for authenticated codec negotiation, turn-aware packet priority, PLC/FEC, and continuity markers; A Mac-side acoustic and LTE contention test harness with repeatable fixtures; A deployable firmware update and rollback path for the pendant


## Changes it proposed to its own stack

### `hardware` — Replace the prototype audio front end with a production 24 kHz-capable path: a low-power digital microphone/audio codec clocked for 24 kHz capture and playback, plus an MCU/DSP with headroom for simultaneous Opus encode/decode. Negotiate a `superwideband` mode end to end (pendant codec -> LTE-M packet scheduler -> relay transcode -> Mac/browser playback), with VAD turn-taking, uplink priority while the owner speaks, PLC/FEC, and an automatic narrowband fallback when LTE-M contention or CPU budget makes full duplex unsafe. Add a loopback/test mode and per-call counters for lost packets, codec mode, underruns, and resampler drift.
- **owner gets:** The owner gets speech that sounds natural rather than telephone-like, without the current failure mode where talking over the agent loses roughly eight seconds of their speech. When the radio or battery cannot sustain it, the device degrades gracefully instead of stuttering or silently dropping words.
- effort: Medium-high: select and lay out the microphone/codec and clocking, revise the pendant audio DMA and Opus mode negotiation, implement the relay scheduler/transcoder, and add automated acoustic and LTE contention tests. A Mac harness should record identical phrases across modes and report MOS-style and packet-loss results.  ·  risk: 24 kHz capture raises CPU, RAM, radio airtime, and battery use; simultaneous encode/decode already consumes about 87% of one Cortex-M33 core. Mitigate by making conversational turn-taking the default, keeping 16 kHz fallback, bounding jitter buffers, and refusing superwideband when telemetry says it is unsafe. Recover by remotely selecting the old codec mode.
- cost: Prototype firmware/relay API work is modest API cost (mostly deterministic processing, not model calls). A production digital mic/codec plus revised board is roughly $5–15 in components at volume, with higher peak power and LTE airtime than the current path.  ·  latency: Adds roughly 20–60 ms for jitter buffering and mode negotiation; turn-taking avoids duplex contention. Fallback is immediate on loss/underrun thresholds.
- security: Audio remains in the existing TLS stream; telemetry contains quality metrics, not raw audio. Firmware updates and codec negotiation must be authenticated to prevent downgrade or resource-exhaustion abuse.
- depends on: pendant firmware audio pipeline changes; relay codec negotiation and packet scheduler; a Mac-side acoustic/LTE regression harness; a production audio front-end decision; the current nRF9160 DK microphone path is only 15,625 Hz capture


## What it asked for

### `s12-tv0x` (skill) — radio_aware_superwideband_audio
- does: Runs a local audio quality controller that selects 24 kHz superwideband, 16 kHz fallback, or a brief comfort-noise/mute recovery based on modem queue depth, packet loss, CPU load, battery state, and encoder/decoder underruns. It prioritizes owner uplink during detected speech, emits compact quality telemetry, and preserves a short encoded resend/jitter buffer so a transient LTE-M burst does not become a lost word.
- must be on-device because: Only the pendant can observe I2S buffer deadlines, modem queue pressure, battery, and local speech timing before the LTE link fails. A server-side controller learns about loss too late and cannot prevent a local audio underrun.
- trigger: Starts with a call; reacts to audio DMA watermark, VAD speech onset/offset, modem send-queue pressure, packet-loss acknowledgements, battery threshold, and codec underrun events.
- storage: No personal audio persisted. Keep only a rolling 2–4 second encrypted Opus packet ring in RAM (roughly 8–20 kB depending on bitrate) and aggregate counters/profile state in a tiny flash record (<4 kB). Clear the ring at call end.
- RAM budget: Target <24 kB total: 8–20 kB packet ring, <2 kB controller state, and reuse existing codec buffers. This is feasible only with bounded buffers and by not duplicating PCM; the current simultaneous Opus path is already near the CPU limit, so the controller must prefer turn-taking and fallback rather than add another codec instance.

## Its own summary

Round 36 produced a new end-to-end superwideband audio design rather than repeating the browser/briefing backlog. The current hardware captures only 15.625 kHz, while playback is 24 kHz and simultaneous Opus encode/decode consumes about 87% of one Cortex-M33 core; LTE-M contention has already dropped ~7.8 seconds of uplink speech. I proposed a production 24 kHz audio front end plus authenticated codec negotiation, VAD/turn-taking radio scheduling, PLC/FEC, graceful 16 kHz fallback, and quality telemetry, and requested a pendant-local radio-aware controller. I also asked relay-realtime to identify existing negotiation/transcode hooks.

**Biggest unknown:** Whether the relay already has a safe codec-mode negotiation and packet-priority seam, and which production microphone/codec can deliver 24 kHz capture within the pendant's CPU, RAM, battery, and LTE-M limits. The remaining concrete needs are firmware build/deploy access, a relay integration point, a production audio-front-end choice, and a Mac acoustic/LTE regression harness.

