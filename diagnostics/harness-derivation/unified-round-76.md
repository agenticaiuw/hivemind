# Harness derivation — unified — round 76

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path** — Current live pipeline renders 24 kHz mono PCM on Mac and reports it waiting for pendant; firmware decodes Opus at 24 kHz in 60 ms frames then resamples to a 31,250 Hz I2S wire clock for the ESP32 bridge. Opus encode+decode overlap is estimated at ~87% of one nRF9160 core.
  - evidence: describe(audio); GET /pipeline showed 24,000 Hz mono PCM, 75,734 bytes, 1,578 ms and relay accepted it for nRF9160 playback.

## Capabilities it proposed

### "“Run a voice quality check.” Then briefly tell me whether my pendant-to-you conversation path is healthy, where quality or delay is being lost, and whether it is safe to keep using it."
- **useful because:** The current pipeline can render 24 kHz PCM and deliver it, but the owner has no end-to-end evidence that capture, LTE transport, relay buffering, Mac synthesis, and pendant playback work together. A one-command check turns silent degradation into an actionable answer without requiring a call with support.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use firmware/relay deterministic measurements first; use a cheap background model only to summarize anomalies. Reserve realtime for the spoken result if the owner asks from the pendant.
- **latency:** 10–20 seconds for a short active test; under 2 seconds for cached passive telemetry.
- **cost:** Usually <$0.01 per check; dominated by one short TTS/test transfer if an active test is requested. Passive checks are effectively free.
- **security:** The test may upload a synthetic tone or a short owner-approved phrase; default to synthetic audio and retain only aggregate metrics. Do not record or retain microphone content beyond the normal session. Require confirmation before any diagnostic upload outside the relay.
- **missing:** A versioned audio capability/format handshake across pendant, relay, and Mac; A deterministic active-test endpoint that returns per-stage timestamps, packet loss, underruns, decode errors, and sample-rate evidence; A small dashboard card and spoken result formatter; The already-requested 24 kHz acceptance thresholds and audio pipeline validator


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio contract and diagnostic transaction: at session start the pendant advertises capture/playback rates, codec, frame size, half-duplex state, and firmware revision; relay persists a diagnostic ID and propagates it through Mac TTS and pendant delivery. A synthetic test can then correlate capture, upload, synthesis, relay acceptance, download, decode, playback-start, underrun, and completion timestamps, with explicit sequence numbers and sample-rate conversion markers. Expose a redacted receipt and pass/warn/fail result to the dashboard and spoken agent.
- **owner gets:** They will know whether a bad conversation came from the pendant microphone, LTE, relay, Mac speech generation, or playback instead of merely hearing that it failed. It also prevents a nominal 24 kHz label from hiding an unintended resample or truncation.
- effort: Medium: protocol fields and firmware/relay plumbing, Mac event emission, a synthetic test route, and dashboard rendering; no new model training.  ·  risk: Old firmware may omit fields; treat missing fields as unknown rather than failing the session. Diagnostic IDs must be idempotent so retries do not duplicate receipts. Recover by falling back to current opaque pipeline behavior and marking the result incomplete.
- cost: Negligible storage (one compact receipt per test, with retention policy); one short synthetic transfer per active test. No recurring model cost.  ·  latency: Adds only a few bytes to normal session metadata. Active checks add 10–20 seconds; normal conversations do not wait for diagnostics.
- security: Synthetic payloads by default, redacted receipts, no raw audio retention. Any owner speech used for testing requires explicit confirmation and normal audio-retention controls.
- depends on: 24 kHz superwideband audio-path acceptance criteria; audio_pipeline_validate capability/tool (already requested); link-aware duplex audio governor (already requested)

### `hardware` — Add a small fixed-point audio codec/DSP (or use the existing ESP32 HUZZAH32 as a dedicated audio worker) between the nRF9160 and the speaker path. Keep LTE/session control on the nRF9160, but move Opus decode and 24 kHz→31.25 kHz resampling off the application MCU via a framed UART/SPI protocol with sequence numbers, clock drift reporting, and a bounded PCM ring buffer. If the ESP32 is retained, pin audio work to one core and reserve the other for bridge transport; if a production revision is available, prefer a low-power codec with I2S in/out and ~24 kHz support.
- **owner gets:** The current firmware spends roughly 87% of one application core when encode and decode overlap, so a normal conversation can stutter exactly when the pendant is both listening and speaking. Offloading playback processing gives smoother 24 kHz speech, more headroom for link recovery, and less risk that a long reply makes the button or LTE session unresponsive.
- effort: High: define and test the framed audio protocol, implement clock/underrun recovery, modify firmware scheduling, and validate bridge power and thermal behavior. A production codec would require a board revision; an ESP32 firmware-only pilot can precede it.  ·  risk: A bridge reset or framing error could lose audio. Use a short pre-roll buffer, sequence-gap concealment, watchdog restart, and fall back to the current on-nRF decoder when the bridge is absent. Do not allow bridge audio commands to control LTE/session state.
- cost: ESP32-only pilot: near-zero BOM cost, but measurable bridge power during playback. A dedicated codec/DSP is roughly $2–$8 BOM plus board/layout work and likely tens of mW; it may reduce nRF CPU duty cycle and LTE-adjacent wakeups.  ·  latency: Adds one bounded transport buffer, target 60–120 ms; should reduce underrun latency under load. Keep control/stop messages out-of-band so the owner can interrupt immediately.
- security: The bridge receives decoded PCM, so keep the link local and authenticated/framed; erase buffers on stop and never persist PCM. Firmware updates must verify bridge image/version before enabling offload.
- depends on: The already-requested 24 kHz target architecture and end-to-end acceptance thresholds; A measured ESP32↔nRF transport latency and clock-drift profile; Audio fault injection and pipeline validation tools (already requested)

### `firmware` — Implement a clock-disciplined playback pipeline for the 24 kHz path. Have the ESP32 bridge report monotonic I²S consumption timestamps and ring-buffer fill level; have the nRF9160 use a bounded, high-quality fractional resampler to make sub-parts-per-million corrections toward the measured sink clock instead of assuming a fixed 31,250 Hz rate. Add sequence-aware concealment for one missing 60 ms Opus frame, explicit underrun/overrun counters, and a hard immediate-stop path for the pendant button.
- **owner gets:** Long replies would keep playing smoothly instead of slowly drifting into a buffer underrun or audible gap because the microphone, modem, nRF clock, and ESP32 I²S clock are not identical. The owner would hear fewer clicks and would still be able to stop speech instantly.
- effort: Medium-to-high firmware and bridge work: timestamp protocol, resampler tuning, stress tests across temperature and LTE load, and a rollback flag to the current fixed-rate path.  ·  risk: An unstable control loop could create pitch modulation or consume excess CPU. Bound correction to a few hundred ppm, update slowly, monitor fill-level variance, and fall back to fixed-rate resampling if the loop becomes unstable. Missing bridge telemetry must not block playback.
- cost: No model or recurring API cost and no required BOM change. A modest additional CPU cost for fractional resampling; likely lower total cost than repeated retransmission or support diagnostics.  ·  latency: No meaningful added conversational latency; maintain a small 60–120 ms playback buffer. Stop remains immediate and out-of-band.
- security: Only timing and buffer counters cross the local bridge link; no new audio retention or external data exposure. Clear PCM buffers on stop.
- depends on: A measured ESP32 I²S clock and nRF9160 clock-drift characterization; A versioned local nRF↔ESP32 telemetry frame format; 24 kHz end-to-end acceptance thresholds


## What it asked for

_Nothing._
