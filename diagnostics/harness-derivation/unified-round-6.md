# Harness derivation — unified — round 6

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **environment** — Mac Local Agent v0.5.0 is live on localhost:8000; health is unauthenticated, all other routes require Bearer token or loopback dashboard cookie. Route manifest reports 120 routes.
  - evidence: GET /health => 200 service AI Pendant Mac Local Agent version 0.5.0; GET /capabilities => auth tokenConfigured true, routeCount 120.
- **audio** — Current pendant audio path is prototype and CPU/network constrained: mic capture 15,625 Hz, uplink Opus 16 kHz/16 kbps; playback Opus 24 kHz/60 ms resampled to 31,250 Hz I2S; encode ~15 ms and decode ~25.4 ms per packet, ~87% one core when both run. LTE-M contention recently dropped 388 uplink packets (~7.8 s).
  - evidence: get_hardware_spec(audio/all) live specification.
- **permissions** — Mac computer-use loop is disabled in ops snapshot because Accessibility is untrusted and Screen Recording is not granted; browser extension is offline with 5 pending commands. Automation grants for System Events/Finder are cached.
  - evidence: GET /ops/snapshot live response.
- **hardware** — Pendant is nRF9160 DK Cortex-M33 64MHz with 211,608 B app RAM, 1MB flash; exactly one full-duplex I2S peripheral shared by mic/speaker. ESP32 bridge resamples 31,250->44,100 for SBC-only A2DP and is RAM constrained.
  - evidence: get_hardware_spec(all) live specification.
- **storage** — microSD is intended only as failure buffer when chunk upload fails; relay retains ~100 recordings for 30 days and sweep is disabled.
  - evidence: get_hardware_spec(storage/stack) live specification.
- **connectivity** — Relay is configured and reachable (Cloudflare Worker v1.1.0), speech/STT and durable audio enabled, Mac bridge online as of 2026-08-07T08:42:03Z. Browser extension remains offline with 5 pending commands.
  - evidence: GET /ops/status => relay.reachable true, capabilities pendantPipelineTelemetry/pendantSpeech/persistentAgentState/durableAudio true; browser.online false pendingCommands 5.
- **timezone** — Owner memory says timezone America/Chicago, while live machine-context reports Mac timezone America/New_York; scheduling and spoken time answers need an explicit precedence rule.
  - evidence: owner discover remembered.timezone=America/Chicago; GET /machine-context machine.timezone=America/New_York.

## What it asked for

_Nothing._
