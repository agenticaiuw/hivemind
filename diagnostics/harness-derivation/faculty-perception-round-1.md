# Harness derivation — faculty-perception — round 1

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent** — Live unauthenticated health probe reports AI Pendant Mac Local Agent v0.5.0 at the discovered localhost surface; /capabilities and other routes require bearer token.
  - evidence: GET /health returned {ok:true, service:'AI Pendant Mac Local Agent', version:'0.5.0', capabilities:'/capabilities'}; route discovery labels auth requirement.
- **Reachable devices** — Device discovery currently shows home-macbook-bridge online (mac_bridge; last seen 2026-08-07T08:49:33.751Z); fanout-probe-cleanup and cloudflare-contract-test are offline.
  - evidence: devices discovery response.
- **Pendant compute/audio** — Remote prototype pendant is Nordic nRF9160 DK, Cortex-M33 64MHz, 211,608B app RAM, 1MB flash; I2S mic capture 15,625Hz, Opus uplink 16kHz/16kbps, downlink decode 24kHz/60ms resampled to 31,250Hz wire clock; encode ~15ms and decode ~25.4ms, ~87% core when both run.
  - evidence: get_hardware_spec pendant and audio responses.
- **Pendant I/O/storage/power** — Prototype has one button and one LED, one full-duplex I2S peripheral; I2C/SPI free. microSD over SPI/FATFS/exFAT is failure buffer only. USB or battery supply, but no battery gauge exists, so charge cannot be read.
  - evidence: get_hardware_spec io, storage, power responses.
- **Audio bridge** — Remote prototype ESP32 HUZZAH32 bridge receives 31,250Hz I2S, resamples to 44,100Hz, and is SBC-only A2DP source; RAM is tight and a 44kB buffer previously starved Bluetooth into silence.
  - evidence: get_hardware_spec bridge response.
- **Pendant network** — Pendant uses LTE-M Cat-M1, one TLS WebSocket, half-duplex in practice; measured simultaneous 16kbps uplink +24kbps downlink caused 388 uplink packets (~7.8s speech) dropped; modem TLS records ~2kB.
  - evidence: get_hardware_spec network response.
- **Production stack** — Relay is Cloudflare Worker with D1 jobs/history/memory and R2 audio; audio retention 30 days, sweep disabled, about 100 recordings stored. Current realtime agent has exactly five tools: get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate.
  - evidence: get_hardware_spec stack response.
- **Owner operating constraints** — Owner timezone is America/Chicago; shell is zsh on Apple Silicon Mac; may read/click browser without asking; confirm before sending mail/deleting files/buying; replies prefer one short spoken sentence. Current stated goal is shipping 24kHz superwideband audio end-to-end on pendant.
  - evidence: owner discovery remembered text.

## What it asked for

### `c1-8jm4` (context) — 24 kHz superwideband audio objective
- why: Owner memory says this is the current goal, but reconnaissance does not establish acceptance criteria, current implementation status, or which artifacts/logs are authoritative.
- would change: I can report concrete blockers and distinguish observed behavior from target requirements when coordinating with judgement/action.

### `c2-u8cl` (context) — live pendant and firmware observability
- why: Hardware specs describe a remote prototype but do not establish whether a pendant is physically connected now, current firmware revision, or latest UART/audio diagnostics.
- would change: I can decide whether to rely on static specs or request a live probe/log acquisition before making state claims.

### `p1-s20c` (permission) — Bearer-authenticated Mac agent diagnostic routes (for example /ops/status, /machine-context, /pipeline, and /capabilities)
- why: Health is reachable but all operational routes are marked bearer-token protected; authenticated status would establish live Mac/pipeline state needed for useful perception.
- risk it sees: Read-only diagnostics may expose owner activity, app state, or stored context; no mutation would be attempted.

### `t1-ivj2` (tool) — read_pendant_diagnostics
- why: To establish current pendant firmware/audio state and verify the 24kHz path, perception needs read-only access to the connected device's UART diagnostics and optionally recent packet counters; existing production tools expose Mac/browser state but no pendant serial or firmware diagnostics.

```json
{
  "type": "object",
  "properties": {
    "source": {
      "type": "string",
      "enum": [
        "uart_live",
        "uart_latest_log",
        "audio_counters",
        "firmware_metadata"
      ]
    },
    "duration_ms": {
      "type": "integer",
      "minimum": 0,
      "maximum": 30000
    },
    "max_bytes": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100000
    }
  },
  "required": [
    "source"
  ]
}
```

## Its own summary

Recon complete. The reachable Mac bridge is online and its unauthenticated health endpoint identifies Mac Local Agent v0.5.0; operational routes require bearer auth. The hardware is a remote prototype: nRF9160 DK pendant (single full-duplex I2S, 16kbps Opus uplink/24kHz downlink, high CPU load), ESP32 HUZZAH32 SBC-only 44.1kHz A2DP bridge, LTE-M WebSocket link with measured ~7.8s speech loss under simultaneous traffic, microSD failure buffer, and no battery gauge. Owner context says America/Chicago, short spoken replies, browser read/click allowed, destructive confirmation required, and current objective is shipping 24kHz superwideband audio end-to-end. I recorded all findings and requested context on acceptance criteria/live firmware state, permission for authenticated diagnostics, and a read-only pendant diagnostics tool.

**Biggest unknown:** No live pendant connection, firmware revision, current UART/audio counters, or authenticated Mac pipeline status is established; these are the critical next facts for useful work.

