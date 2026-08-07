# Harness derivation — unified — round 15

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio hardware baseline** — Pendant currently captures at 15,625 Hz and Opus-encodes uplink at 16 kHz/16 kbps; downlink decodes Opus at 24 kHz/60 ms and outputs 31,250 Hz I2S to ESP32, which resamples to 44.1 kHz for SBC A2DP. The single I2S peripheral is full duplex and must be shared.
  - evidence: get_hardware_spec(audio), get_hardware_spec(io), get_hardware_spec(bridge)
- **audio/network constraints** — LTE-M is half-duplex in practice; measured simultaneous 16 kbps uplink + 24 kbps downlink dropped 388 uplink packets (~7.8s speech). TLS modem records are ~2 kB. Opus decode costs ~25.4ms per 60ms packet; encode ~15ms, ~87% of one Cortex-M33 core when both run.
  - evidence: get_hardware_spec(network), get_hardware_spec(audio)
- **audio retention and prototype status** — Audio is retained in relay R2 for 30 days with sweeping disabled and ~100 recordings; pendant SD is intended only as failure buffer. Hardware is explicitly prototype Nordic DK/ESP32, not production product.
  - evidence: get_hardware_spec(storage), get_hardware_spec(stack), get_hardware_spec(audio)
- **timezone conflict** — Owner memory says timezone America/Chicago, while live Mac machine-context reports America/New_York. Do not infer scheduling timezone until authoritative timezone context is provided.
  - evidence: discover(owner) remembered.text; describe(GET /machine-context) liveResponse

## What it asked for

_Nothing._
## Its own summary

Recon complete. Live Mac agent is healthy at localhost:8000 (v0.5.0, bearer auth configured); the online hardware inventory is a prototype nRF9160 DK + ESP32 bridge. The current audio path is 15,625-Hz mic → Opus 16 kHz/16 kbps uplink, and Opus 24 kHz/60-ms downlink → 31,250-Hz I2S → ESP32 resample to 44.1 kHz SBC A2DP. The path is constrained by one shared full-duplex I2S peripheral, ~87% Cortex-M33 load when encoding/decoding, and LTE-M contention that recently dropped ~7.8 seconds of uplink speech. Relay audio retention is 30 days with sweeping disabled (~100 recordings), while SD is failure-buffer-only. I recorded these findings plus a live timezone conflict (owner memory America/Chicago vs Mac machine-context America/New_York). To do useful implementation work I still need the already-pending workspace edit capability, audio pipeline validation tool, and authoritative 24-kHz target/acceptance context; I will not repeat those requests this round. I also need the firmware/relay workspace status and build/test entry points from the Mac facet before changing anything.

**Biggest unknown:** Whether the requested 24-kHz superwideband target means only the downlink playback leg or both uplink and downlink, and what exact wire/codec/latency acceptance criteria apply; the requested context and validation grant are still outstanding.

