# Harness derivation — faculty-action — round 101

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-delivery-observability** — The live pipeline records TTS rendering as 24,000 Hz mono PCM and relay acceptance, but does not show a device download/decode/playback-complete acknowledgement; at least one pipeline remains processing. Browser status reports no pendant device, only home-chrome online and 9 pending browser commands.
  - evidence: GET /pipeline returned TTS event meta {sampleRate:24000, channels:1, pcmBytes:75734} followed by 'Response waiting for the pendant' with no playback completion event. GET /browser/status returned devices=[home-chrome] and pendingCommands=9.

## Capabilities it proposed

### "“Is my pendant audio path healthy? If not, diagnose it, switch to the safest working mode, and leave me a short report.”"
- **useful because:** The owner currently has no way to know whether 24 kHz playback is actually reaching the earbud/bridge. A closed-loop test would distinguish codec, timing, I2S wiring, radio loss, and battery problems, then recover without pretending the path works. It requires the worn endpoint, ESP32 bridge, Mac harness, and always-awake relay together.
- **path:** pendant → relay → mac-bridge → dashboard → unified
- **model tier:** Use deterministic firmware/bridge DSP and threshold rules for diagnosis; use a cheap background model only to turn telemetry into a human report. Reserve realtime for the owner's spoken question.
- **latency:** 15–30 seconds for a full test; under 2 seconds to select a local fallback after a failed frame or bridge health event.
- **cost:** Negligible API cost for thresholded telemetry; roughly $0.01–$0.05 only when a background model summarizes an anomalous run. Storage is a small per-run JSON receipt plus optional short waveform.
- **security:** The test may emit an audible tone, so require a low-volume mode and owner confirmation if outside a quiet window. Send only derived metrics by default (packet loss, clock drift, underruns, RMS/SNR); retain raw audio only for an explicitly enabled diagnostic run. Any mode switch must be nonce-bound and receipt-backed.
- **missing:** A pendant diagnostic command/event for loopback tone and microphone capture; ESP32 bridge-side I2S counters and clock-drift measurement; A relay schema for signed audio health receipts and fallback state; Mac harness job that runs the test and collects bridge/pendant telemetry; A verified postcondition tool for confirming the selected mode actually took effect

### "“Make my pendant audio sound right wherever I am: run a quiet calibration, compensate for the bridge and headphones, and keep the correction until the hardware changes.”"
- **useful because:** The current system can render 24 kHz PCM but cannot account for the ESP32 bridge’s 31,250→44,100 Hz resampling, SBC-only Bluetooth path, headphone latency, or per-device gain. The owner should hear speech that is intelligible and correctly timed without manually tuning an experimental chain. This is a new calibration-and-compensation capability, not merely a health check or delivery receipt.
- **path:** pendant → relay → mac-bridge → dashboard → unified
- **model tier:** Use deterministic swept-tone/MLS measurement, fixed-point DSP, and a small calibration profile; use a background model only to explain the result in one short spoken sentence. No realtime model is needed for the measurement.
- **latency:** Initial calibration 20–45 seconds while the owner explicitly invokes it; applying a stored profile adds under 1 ms of processing and no conversational latency.
- **cost:** Near-zero model cost; a few small telemetry records per calibration and at most a bounded diagnostic waveform. Computation runs on the ESP32/Mac, not an API.
- **security:** Calibration emits sound and may expose nearby audio if microphone loopback is used. Require an explicit start, cap volume, offer a speaker-only mode, and upload derived impulse-response/gain metrics rather than recordings. Bind the profile to authenticated pendant, bridge, and headphone identities; never apply a profile to an unknown device automatically.
- **missing:** A calibration command spanning pendant playback, ESP32 resampling, and headphone route; Bridge-side timestamped I2S capture and Bluetooth latency/gain telemetry; A compact profile format and authenticated storage keyed by hardware identities; A verified apply-and-postcondition acknowledgement from the pendant/bridge; A user-visible way to select or discard profiles when headphones change


## Changes it proposed to its own stack

### `firmware` — Add an offline-safe AUDIO_DIAGNOSTIC transaction to the pendant firmware: generate a bounded low-volume pseudorandom/MLS test frame, route it through the normal Opus decode → 24 kHz PCM → 31,250 Hz I2S playback path, collect sequence continuity, decode runtime, ring-buffer high-water, underrun, and I2S timing counters, then emit a compact signed result over the existing control channel. Add a second receive-loopback mode only when explicitly requested, with a hard 10-second timeout and no raw audio persistence.
- **owner gets:** They can ask one sentence and get a truthful answer about whether the part they wear is working, instead of discovering a broken audio path during an important conversation. A failed test can safely fall back before damage reaches the user experience.
- effort: Medium: firmware command/state machine and counters, bridge instrumentation, relay receipt schema, Mac orchestration, and integration tests against simulator fixtures.  ·  risk: A diagnostic tone could surprise the owner; cap volume and require an explicit test trigger. Counter bugs could report false health; validate against injected packet loss, drift, and underrun fixtures. Never auto-flash or alter persistent configuration; fallback must be reversible and receipt-recorded.
- cost: No per-run model cost; a few KB of firmware flash and under 2 KB RAM for counters/state. Small D1 receipt growth; raw waveform is opt-in and bounded.  ·  latency: Adds up to 30 seconds only when invoked; no steady-state audio latency. The diagnostic counters are collected in-band and should not affect normal decode scheduling.
- security: Authenticate and nonce-bind the diagnostic request; sign the receipt with a device key if available. Do not upload microphone samples by default. Fallback actions must be limited to an allowlisted set.
- depends on: physical pendant/bridge availability (currently no pendant is connected); 24 kHz acceptance criteria; verify_operation_step or equivalent postcondition verification; owner-controlled firmware build with secrets.conf

### `relay` — Add an audio-delivery state machine separate from TTS rendering: rendered → uploaded → downloaded-by-device → decode-started → playback-completed, with device/bridge acknowledgements, a 60-second lease, retry limits, and a terminal truthful failure. Reconcile orphaned `processing` pipeline runs on startup and emit a compact receipt containing sample rate, duration, packet counts, first/last acknowledgement, and failure reason.
- **owner gets:** Today the relay can truthfully say 24 kHz PCM was rendered and accepted while the owner still cannot know whether the pendant actually played it. This makes “waiting for the pendant” either complete or explicitly failed, and prevents stale jobs from looking alive forever.
- effort: Medium: schema and reducer in the Worker, idempotent acknowledgement endpoints in the pendant/bridge, retry watchdog, and dashboard/voice rendering of the terminal receipt.  ·  risk: A dropped acknowledgement could cause a duplicate replay; use delivery IDs and device-side deduplication. A device that is genuinely offline must not be marked failed until lease expiry. Preserve current playback behavior behind a feature flag and migrate existing processing rows safely.
- cost: Tiny D1 writes per state transition; no model calls. Optional R2 audio cleanup can reuse existing retention work.  ·  latency: No added rendering latency; first retry may add up to the lease interval. Normal completion becomes observable within one device round trip.
- security: Bind acknowledgements to authenticated device identity and delivery nonce; never accept a completion receipt without matching upload ID. Do not expose audio payload URLs in spoken receipts.
- depends on: connected pendant/ESP32 bridge (currently absent); a device-side playback acknowledgement event; existing /pipeline/audio and /pipeline/events wiring; durable job runner or equivalent watchdog

### `hardware` — Add a low-cost reference MEMS microphone and hardware timestamp line to the ESP32 headphone bridge, positioned near the headphone output (or provide a calibrated acoustic coupler during setup). Expose synchronized playback and reference-capture samples so the system can estimate end-to-end frequency response, gain, clipping, and latency instead of inferring them from I2S counters alone.
- **owner gets:** The owner gets speech that is measurably intelligible and synchronized on the headphones they actually use, rather than a calibration that only says the digital pipeline ran. It also makes later regressions diagnosable without sending raw conversations to the cloud.
- effort: Medium hardware revision and enclosure/acoustic design; firmware driver and timestamp synchronization; calibration flow and profile migration.  ·  risk: A poorly placed mic can measure leakage instead of ear-canal sound and produce a bad correction. Keep calibration opt-in, constrain equalization to safe bounded gains, and allow one-button/profile reset. Do not use the reference mic as an always-on conversation microphone.
- cost: Approximately $1–$3 BOM increase for a digital MEMS mic, PCB routing, and modest bridge firmware/RAM use; negligible steady-state power if powered only during calibration.  ·  latency: No normal playback latency when powered off outside calibration. Calibration adds tens of seconds and temporary bridge CPU/bandwidth use.
- security: Reference capture is local by default and discarded after deriving metrics. If diagnostics are exported, encrypt and minimize to response curves and timing values; require explicit owner initiation.
- depends on: calibration capability and profile schema; bridge PCB/firmware revision; authenticated apply-and-postcondition acknowledgement; an explicit acoustic safety limit and reset path


## What it asked for

_Nothing._
## Its own summary

Discovered live evidence and recorded three actionable changes. The pipeline renders 24 kHz mono PCM and accepts/uploads it, but has no device-side download/decode/playback-complete receipt; one run remains processing. Browser status has only home-chrome online, no pendant. Proposed a closed-loop owner capability (“Is my pendant audio path healthy? diagnose and safely fallback”), firmware AUDIO_DIAGNOSTIC transaction, and a relay audio-delivery state machine with authenticated acknowledgements, leases, retries, deduplication, and truthful terminal status. Hardware constraints captured: nRF9160 decode is ~25.4 ms per 60 ms frame and ~87% core with encode; ESP32 bridge is SBC-only 44.1 kHz stereo with tight RAM.

**Biggest unknown:** The actual 24 kHz acceptance thresholds and live pendant/bridge telemetry remain unavailable because no pendant is connected. Implementation still needs an owner-controlled firmware build (secrets/toolchain), device-side diagnostic and playback-ack events, and the pending verification/audio-probe capabilities; I did not re-request denied or already-pending items.

