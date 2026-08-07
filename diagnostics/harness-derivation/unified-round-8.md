# Harness derivation — unified — round 8

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent readiness** — Mac agent v0.5.0 is live on localhost:8000 and relay is reachable/paired; browser extension is online. However readiness is false because Accessibility is not trusted and Screen Recording is missing, while no required automation permission is missing.
  - evidence: GET /ops/status returned ok=true, relay.reachable=true, browser.online=true, permissions.accessibility.trusted=false, screenRecording.granted=false, ready=false.
- **Current pendant audio implementation** — Remote prototype pendant captures I2S at 15,625 Hz and uploads Opus at 16 kHz/16 kbps; playback decodes Opus at 24 kHz/60 ms and resamples to 31,250 Hz I2S. ESP32 bridge resamples 31,250 to 44,100 and emits SBC-only A2DP stereo. Decode and encode together consume about 87% of one nRF9160 core.
  - evidence: get_hardware_spec pendant/audio/bridge responses.
- **Audio pipeline evidence** — Pipeline telemetry includes successful 24 kHz mono PCM TTS rendering and relay acceptance: one run rendered 164,650 bytes, 3,430 ms at 24,000 Hz with zero clipped samples, then relay accepted it for pendant download. Output WAV retrieval works for completed run; input audio was absent for that run.
  - evidence: GET /pipeline and GET /pipeline/job_612d.../audio/output returned 24 kHz WAV bytes; pipeline events report tts done and relay_result done, pcmBytes=164650.
- **Pipeline completion semantics** — Several nRF9160 and cloud-relay pipeline runs remain status=processing even after terminal-looking events, including alert delivery and relay response waiting. This suggests end-to-end playback/ack completion is not yet recorded or runs are not finalized.
  - evidence: GET /pipeline returned multiple runs with status=processing and events ending at alert_delivered or Response waiting for the pendant.
- **Relay retention** — Cloud relay stores roughly 100 recordings in R2 with 30-day retention, but the retention sweeper is disabled.
  - evidence: get_hardware_spec(component=stack) response.

## What it asked for

_Nothing._
## Its own summary

Reconnaissance complete. The Mac agent (v0.5.0) and Cloudflare relay are live and paired; browser bridge is online. The prototype audio chain is: 15,625-Hz mic capture → Opus uplink (16 kHz/16 kbps) → 24-kHz playback decode → 31,250-Hz I2S → ESP32 44,100-Hz resampling → SBC-only A2DP. Telemetry proves 24-kHz TTS rendering and relay acceptance, and output WAV retrieval works, but multiple runs remain stuck at processing after relay delivery/alert events, so end-to-end playback acknowledgement is not established. Relay audio retention is 30 days with the sweeper disabled. I recorded all findings.

**Biggest unknown:** The acceptance criteria and an executable validation path for the requested 24-kHz superwideband end-to-end audio change remain unavailable. I still need the previously requested audio_pipeline_validate capability, workspace-edit capability, and the owner’s pending Accessibility and Screen Recording grants; without them I cannot modify or objectively validate the implementation. The Mac status explicitly reports accessibility=false, screenRecording=false, ready=false.

