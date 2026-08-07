# Harness derivation — unified — round 14

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent health and readiness** — Mac local agent v0.5.0 is live on localhost:8000 and relay reachable, but readiness is false because Accessibility trusted=false and Screen Recording granted=false; browser extension is offline. Automation grants are cached and requiredMissing is empty, but those two permissions still block ready state.
  - evidence: GET /ops/snapshot returned agent.ready=false, accessibility.trusted=false, screenRecording.granted=false, browser.online=false; GET /health returned 200.
- **Pendant audio path** — Current prototype captures I2S at 15,625 Hz, Opus uplink is 16 kHz/16 kbps, playback decodes 24 kHz in 60 ms frames then resamples to 31,250 Hz I2S. Codec encode ~15 ms and decode ~25.4 ms per 60 ms packet, using roughly 87% of one Cortex-M33 core when both run.
  - evidence: get_hardware_spec(audio) returned firmware/audio_opus.c and cloud-relay/opusTranscode.js measurements.
- **Audio transport constraint** — LTE-M link is half-duplex in practice; simultaneous 16 kbps uplink + 24 kbps downlink saturates it, with a measured loss of 388 uplink packets (~7.8 seconds) during a recent call. TLS WebSocket modem records are limited to about 2 kB.
  - evidence: get_hardware_spec(network) returned measured link contention and packet loss.
- **Audio bridge constraint** — ESP32 bridge resamples 31,250 Hz to 44,100 Hz and uses SBC-only A2DP source locked to 44.1 kHz stereo; a 44 kB buffer previously starved Bluetooth into silence.
  - evidence: get_hardware_spec(bridge) returned bridge role and hard limits.
- **Pipeline telemetry** — Mac pipeline telemetry already records 24 kHz mono PCM TTS and relay delivery; a recent completed response was 164,650 PCM bytes, 3.43 seconds, 24,000 Hz mono, no clipping. The pipeline list also contains offline pendant-held alerts/bookmarks.
  - evidence: GET /pipeline returned events with sampleRate 24000, format s16le, and pendant offline-store events.
- **Live device inventory** — The discoverable live devices are an online Mac bridge, an offline browser cleanup probe, and an offline mobile contract test; no pendant device appears in the live device inventory. Hardware specs explicitly say pendant is remote and prototype.
  - evidence: discover(devices) returned only fanout-probe-cleanup, home-macbook-bridge, cloudflare-contract-test; get_hardware_spec says every device is remote.

## What it asked for

_Nothing._
## Its own summary

Reconnaissance is complete for this round. The Mac agent is live (v0.5.0) and relay-reachable, but not ready: Accessibility is untrusted, Screen Recording is missing, and the browser extension is offline. The prototype audio path is not truly superwideband end-to-end: capture is 15,625 Hz, uplink Opus is 16 kHz/16 kbps, playback is 24 kHz decoded then 31,250 Hz I2S, and the ESP32 bridge resamples to SBC-only 44.1 kHz A2DP. LTE-M contention already drops about 7.8 seconds of uplink in a measured call. Pipeline telemetry confirms 24 kHz mono TTS delivery works on the Mac/relay side. No live pendant appears in device inventory. To do useful implementation work I still need the already-pending mac_workspace_edit tool, audio_pipeline_validate tool, Accessibility + Screen Recording permission grant, the authoritative 24 kHz audio architecture and acceptance criteria, and authoritative timezone. I will not repeat those requests this round.

**Biggest unknown:** Whether the intended 24 kHz superwideband contract requires 24 kHz wire-rate capture/uplink, only 24 kHz playback/TTS, or a negotiated Opus mode—and what packet-loss, latency, and intelligibility thresholds define acceptance.

