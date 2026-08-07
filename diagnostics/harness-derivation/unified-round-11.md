# Harness derivation — unified — round 11

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent health and auth** — Mac local agent is live at localhost:8000, version 0.5.0, with 120 routes and bearer auth configured; /health is unauthenticated.
  - evidence: GET /health returned 200 service AI Pendant Mac Local Agent version 0.5.0; GET /capabilities returned tokenConfigured:true and routeCount:120.
- **Mac readiness** — Mac bridge is online and relay-reachable, but agent readiness is false because Accessibility and Screen Recording are not granted; browser extension is offline.
  - evidence: GET /ops/status returned ready:false, accessibility.trusted:false, screenRecording.granted:false, browser.online:false; relay macBridgeOnline:true.
- **Audio path current implementation** — The pipeline has produced 24 kHz mono PCM TTS successfully (3.43 s, 164650 bytes, no clipping), but pendant capture remains 15,625 Hz and uplink telemetry is PCM at 15,625 Hz; playback is decoded at 24 kHz then resampled to 31,250 Hz I2S for the ESP32.
  - evidence: GET /pipeline returned completed TTS event metadata sampleRate 24000/channels 1 and inputTelemetry sampleRate 15625; hardware audio spec states same playback chain.
- **Audio hardware constraints** — Prototype pendant is nRF9160 DK, Cortex-M33 64 MHz, 211,608 B app RAM, 1 MB flash; fixed-point Opus decode costs ~25.4 ms per 60 ms packet and encode ~15 ms, roughly 87% of one core together. ESP32 bridge uses SBC-only 44.1 kHz stereo A2DP and tight RAM.
  - evidence: get_hardware_spec(audio), get_hardware_spec(pendant), and get_hardware_spec(bridge).
- **Retention gap** — Audio retention sweeper remains proposed and inert: disabled, no scheduled invocation, capped at newest 100, binding/delete/error-handling and owner-pin gaps remain; no dashboard delete action.
  - evidence: describe chg-a813b918 reported status proposed and enumerated verified gaps.
- **Browser automation gap** — Browser backend router exists, but durable job runner with job IDs, persistence, retries, and result stream is still missing; current browser extension is offline with zero pending commands.
  - evidence: describe chg-16bc5dee status proposed/note says durable runner missing; GET /browser/status returned online:false and pendingCommands:0.
- **Timezone conflict** — Stored owner memory says America/Chicago, while live Mac machine-context and routing report America/New_York. Authoritative timezone is unresolved and must not be guessed for schedules.
  - evidence: owner discovery remembered timezone America/Chicago; GET /routing and GET /ops/status machine timezone America/New_York.
- **Relay storage** — Cloud relay is reachable, D1-backed, with durable audio enabled and approximately 100 recordings retained for 30 days; retention sweep is disabled.
  - evidence: get_hardware_spec(stack) returned relay storage configuration.

## What it asked for

_Nothing._
