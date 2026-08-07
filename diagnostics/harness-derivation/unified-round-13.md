# Harness derivation — unified — round 13

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent** — Mac local agent v0.5.0 is live at localhost:8000; relay reachable and bridge online, but agent readiness is false because Accessibility trusted=false and Screen Recording granted=false. Browser extension is offline with 0 pending commands.
  - evidence: GET /ops/status returned ok=true, version 0.5.0, permissions.accessibility.trusted=false, screenRecording.granted=false, browser.online=false; GET /browser/status matched.
- **audio-path** — Current hardware/audio path is prototype: microphone captures 15,625 Hz I2S and uplinks Opus at 16 kHz/16 kbps; playback decodes Opus at 24 kHz in 60 ms frames, resamples to 31,250 Hz I2S, then ESP32 resamples 31,250→44,100 for SBC-only A2DP.
  - evidence: get_hardware_spec(audio) and get_hardware_spec(bridge) returned these exact rates and constraints.
- **audio-validation** — A recorded pipeline run shows TTS rendered 24 kHz mono PCM, 164,650 bytes, 3.43 s, no clipping; however probing /pipeline/:id/audio/output returned a WAV header indicating 15,625 Hz, so direction/recording format needs authoritative validation before claiming end-to-end 24 kHz.
  - evidence: GET /pipeline showed TTS event meta sampleRate=24000; GET /pipeline/job_165a.../audio/output response began RIFF/WAVE header with sample rate bytes corresponding to 15625.
- **timezone** — Owner memory says America/Chicago, while live machine-context reports America/New_York; timezone is unresolved and should not be guessed for schedules.
  - evidence: owner discover remembered timezone America/Chicago; GET /machine-context returned timezone America/New_York.

## What it asked for

_Nothing._
