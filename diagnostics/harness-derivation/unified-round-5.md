# Harness derivation — unified — round 5

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent** — Mac local agent v0.5.0 is reachable on localhost:8000; bearer token configured; relay reachable and mac bridge online. Agent is not ready because Accessibility is untrusted and Screen Recording is not granted, despite no requiredMissing list entries.
  - evidence: GET /ops/status returned fullControlMode=true, permissions.accessibility.trusted=false, screenRecording.granted=false, ready=false; GET /health returned 200.
- **browser** — Browser extension bridge is currently offline with zero devices and five pending commands, so authenticated browser work cannot currently be relied upon.
  - evidence: GET /ops/status returned browserExtension.online=false, devices=[], pendingCommands=5.
- **audio-path** — Current audio path captures at 15,625 Hz, encodes uplink Opus at 16 kHz/16 kbps, and decodes downlink Opus at 24 kHz/60 ms before resampling to a 31,250 Hz I2S wire clock. A live trace successfully rendered 24 kHz mono PCM (164,650 bytes, 3.43 s, no clipping).
  - evidence: hardware audio description and GET /pipeline trace event tts done metadata.
- **audio-risk** — LTE-M is half-duplex in practice; measured simultaneous 16 kbps uplink + 24 kbps downlink caused 388 uplink packets (~7.8 s speech) to drop, so end-to-end 24 kHz acceptance still needs an explicit contention/drop criterion.
  - evidence: hardware network description.
- **retention** — Relay uses D1/R2 with 30-day audio retention, but automated sweep is disabled and approximately 100 recordings are stored.
  - evidence: hardware stack description.
- **devices** — Only home-macbook-bridge is online; cloudflare-contract-test mobile device is offline (last seen 2026-07-31).
  - evidence: devices discovery returned home-macbook-bridge · online and cloudflare-contract-test · offline.

## What it asked for

_Nothing._
