# Harness derivation — unified — round 10

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio playback path** — Pendant decodes Opus at 24 kHz in 60 ms frames, then resamples to a 31,250 Hz I2S wire clock and outputs to ESP32 bridge.
  - evidence: hardware describe audio: playback Opus decode on-device at 24 kHz / 60 ms frames, resampled to 31,250 Hz I2S.
- **audio capture path** — Capture is I2S at 15,625 Hz; uplink is Opus encoded at 16 kHz/16 kbps complexity 0. Encode and decode together consume ~87% of one core.
  - evidence: hardware describe audio.
- **bridge constraints** — ESP32 bridge resamples 31,250→44,100 Hz and sends SBC-only A2DP at fixed 44.1 kHz stereo; 44 kB buffering starved Bluetooth, so RAM is tight.
  - evidence: hardware describe bridge.
- **mac agent** — Mac local agent is healthy at localhost:8000, version 0.5.0, with 120 routes and bearer auth except /health and dashboard paths.
  - evidence: GET /health and GET /capabilities live responses.
- **live audio telemetry** — A recent cloud-relay pipeline run captured PCM s16le mono at 15,625 Hz (audioBytes 937,500; duration 1,441 ms), and rendered output as 24,000 Hz mono PCM (164,650 bytes, 3,430 ms, no clipping).
  - evidence: GET /pipeline live response pipelineId job_165a9c9a... events inputTelemetry and TTS metadata.
- **Mac operational readiness** — Relay is reachable and Mac bridge online, but local agent reports ready=false because Accessibility is untrusted and Screen Recording is not granted; browser extension is offline and mac-vision loop disabled.
  - evidence: GET /ops/status live response.
- **timezone discrepancy** — Owner memory says America/Chicago, while Mac /machine-context reports America/New_York. Scheduling behavior needs an authoritative timezone decision.
  - evidence: owner discover remembered timezone vs GET /machine-context response.

## What it asked for

### `c3-n48u` (context) — authoritative timezone
- why: Owner memory projects America/Chicago but the live Mac machine-context reports America/New_York; this affects routines, reminders, and any audio-path acceptance timestamps.
- would change: I will use the confirmed timezone for scheduling and interpret pipeline timestamps consistently; until clarified I will not alter schedules or claim local-time correctness.

