# Harness derivation — faculty-perception — round 63

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac input reachability** — At 2026-08-07T12:22:50Z, AI Pendant Agent accessibility is not trusted; screen recording false; inputReachability failed and ui_actions will report success without reaching screen. AppleScript automation grants are cached and requiredMissing is empty, but permissions.ready=false.
  - evidence: GET /observe and GET /ops/status responses.
- **Audio pipeline** — A completed relay job rendered 24,000 Hz mono s16le PCM (75,734 bytes, 1.578 s, no clipping), while another live pendant input event reported 15,625 Hz mono PCM (937,500 bytes).
  - evidence: GET /pipeline response events pipe_evt_d9e30c71... and pipe_evt_b716e091...
- **Browser bridge** — At 2026-08-07T12:22:50Z home-chrome browser extension is offline with 5 pending commands; no live tabs are currently reachable through browser bridge.
  - evidence: GET /browser/status and GET /ops/status.
- **Audio format interpretation** — The 15,625 Hz live input is the pendant's documented I2S microphone capture clock; firmware uplink is expected to Opus-encode at 16 kHz/16 kbps, while playback decodes at 24 kHz and resamples to a 31,250 Hz I2S wire clock. The pipeline's 15,625 Hz raw PCM field is therefore not by itself a defect, but conversion stages need explicit provenance to verify them.
  - evidence: Recalled get_hardware_spec:component=audio plus GET /pipeline live inputTelemetry.

## Capabilities it proposed

### "“Did that actually happen?” — Give me a one-sentence truth check for my last request, saying which legs are proven (heard, understood, Mac/browser action, response delivered, pendant played) and which are still unverified."
- **useful because:** Today the system can say a job is completed when the Mac only produced a plan, a shell step is waiting for approval, the relay accepted audio, or the pendant has not yet played it. This gives the owner an honest physical-world answer instead of a misleading success receipt.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for reconciliation; use realtime only to answer a live follow-up on the pendant
- **latency:** Under 2 seconds for an on-demand check; under 250 ms to surface a newly missing/failed leg from telemetry
- **cost:** Usually no model call: roughly <$0.001 in storage/compute per check. Reserve a small text model call only when evidence conflicts, roughly $0.005–$0.02.
- **security:** Private URLs, action details, and audio identifiers must remain in the local evidence store; expose only the minimum cited facts to the pendant. Never infer physical playback from relay upload. Sending, deleting, buying, or submitting still requires the existing confirmation policy.
- **missing:** An append-only, correlated evidence record keyed by requestId/pipelineId across pendant input, relay transcription, Mac job/receipt, browser command result, TTS upload, and pendant download/playback start/end.; Pendant playback acknowledgements (including interruption, underrun, and checksum/byte count) and an explicit terminal state for 'delivered to relay but not played'.; A canonical sample-rate/format field and conversion receipt: current evidence shows live input at 15,625 Hz while returned speech is 24,000 Hz PCM.; A reconciliation endpoint that emits per-leg status with source timestamp, freshness, and confidence, rather than treating pipeline status=completed as end-to-end success.

### "“Did you hear me clearly?” — Before acting on an important spoken request, tell me whether the pendant captured intelligible speech, which words are uncertain, and ask me to repeat only the uncertain part."
- **useful because:** Today a plausible transcription can hide clipped, noisy, or partially captured speech, causing the system to act on the wrong request. The owner needs an immediate, perceptual truth signal while wearing the device—not a later job receipt or a generic failure.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime for the live intelligibility decision; background processing may aggregate acoustic failure patterns without resending audio to the expensive tier.
- **latency:** 150–300 ms after end-of-utterance for a confidence signal; at most 1 second before asking for a targeted repeat.
- **cost:** Small incremental realtime tokens for confidence/uncertainty spans; roughly $0.001–$0.01 per utterance depending on audio duration. Local acoustic metrics should avoid extra model calls.
- **security:** Do not retain raw audio by default. Send only transient acoustic metrics and uncertainty spans to the relay; redact sensitive transcript text from diagnostics. Never proceed with an irreversible action when the intelligibility gate is uncertain.
- **missing:** A pendant-side acoustic-quality frame containing clipping, packet loss, VAD boundaries, noise estimate, and capture-clock continuity.; Realtime output that exposes word/phrase uncertainty or an explicit intelligibility verdict, rather than only a final transcript.; A cross-node policy that pauses planning when intelligibility is below threshold and requests a short targeted repeat.; A dashboard and spoken response that distinguish 'not heard', 'heard but ambiguous', and 'heard clearly'.


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio integrity probe that periodically sends a marked calibration utterance from the pendant, records the actual capture clock/rate and byte count, validates relay transcription metadata, verifies Mac TTS format, and compares pendant playback start/end plus underrun counters. Store a compact per-leg record and raise a diagnostic when declared and measured sample rates differ (the current live path reports 15,625 Hz input while rendered output is 24,000 Hz).
- **owner gets:** The owner gets speech that is reliably understood and played at the intended quality, and a precise explanation when audio is late, clipped, silent, or misreported—rather than spending time debugging an apparently successful conversation.
- effort: Medium: firmware telemetry fields and calibration command, relay correlation/storage, Mac pipeline event emission, and a read-only diagnostic view. No Accessibility permission is required.  ·  risk: A probe could briefly interrupt or add a small audio artifact; run only on idle or explicit request, mark synthetic audio clearly, and discard its content. If telemetry is missing, report unknown rather than passing. Recover by disabling the probe and preserving the last known-good format.
- cost: Negligible API cost; a few hundred bytes per probe and one occasional background reconciliation. Firmware flash/RAM impact should be kept below 8 KB flash and 2 KB RAM.  ·  latency: No impact on normal voice path; diagnostics run asynchronously. An explicit probe may take 2–5 seconds.
- security: Keep audio payload local/ephemeral and retain only hashes, rates, counters, and timestamps. Do not upload calibration speech unless the owner explicitly opts in.
- depends on: Pendant playback lifecycle telemetry; Correlated request IDs across relay and Mac pipeline events; A read-only audio-integrity diagnostic endpoint

### `interaction` — Introduce an uncertainty gate between speech recognition and planning: the relay must attach an intelligibility verdict and uncertain spans to each utterance; the Mac planner may only proceed when the verdict is clear, otherwise it returns a short targeted repeat prompt. The pendant renders that prompt locally when offline and queues the quality record for later synchronization.
- **owner gets:** The owner stops getting confident-sounding actions from half-heard speech, especially outdoors or while moving. They hear exactly what needs repeating instead of having to restart the entire request or discover the mistake afterward.
- effort: Medium across pendant firmware, relay schema/policy, realtime response handling, and Mac planner input validation; no GUI permission is needed.  ·  risk: Over-cautious gating could make conversation feel slow or repetitive. Use adaptive thresholds, allow the owner to say 'use your best guess' for reversible requests, and always require confirmation for irreversible ones. If telemetry is absent, fall back to the current behavior but label confidence unknown.
- cost: Minimal storage and compute; occasional extra short repeat turn increases realtime audio/token cost by roughly $0.001–$0.01. No raw audio retention required.  ·  latency: Adds approximately 150–300 ms to utterance finalization when quality is clear; degraded audio adds one short conversational turn.
- security: Quality metrics and uncertain spans are sensitive conversation metadata; retain transiently by default, encrypt queued records, and exclude raw audio from diagnostics.
- depends on: offline-capture-integrity-sentinel on the pendant; Relay schema for acoustic quality and uncertainty spans; Planner enforcement of an intelligibility verdict before action selection


## What it asked for

### `s3-k4kq` (skill) — offline-capture-integrity-sentinel
- does: While the owner speaks, locally measures VAD boundaries, packet-loss gaps, clipping, RMS/noise floor, and capture-clock continuity. At utterance end it emits a tiny quality verdict (clear / degraded / unusable) with a sequence number and requests a repeat locally when the capture is unusable. When connected, it forwards only the metrics so the relay can gate transcription and action.
- must be on-device because: The pendant is the only node that sees the microphone clock, packet gaps, and dropped frames before transport. It must warn offline and distinguish a quiet microphone from a broken uplink even when the relay is unreachable.
- trigger: Microphone VAD start/stop and transport packet-loss or clock-gap events; server push can update thresholds when connected.
- storage: A rolling ring of the last 32 utterance metrics plus the current threshold profile in flash; approximately 4–8 KB, no raw audio.
- RAM budget: Approximately 1–2 KB: rolling RMS/noise statistics, VAD state, counters, and one compact metric record. Fits within the 211,608 B application RAM budget without buffering audio.

