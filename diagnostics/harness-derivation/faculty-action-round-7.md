# Harness derivation — faculty-action — round 7

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent readiness** — Local Mac agent v0.5.0 is reachable on localhost:8000, bearer-authenticated, full-control and LLM planner enabled, but ready=false because Accessibility trusted=false and Screen Recording granted=false. Automation grants are cached for System Events, Finder, Reminders, Calendar, Mail, Notes, Messages, Safari, Chrome, etc.
  - evidence: GET /health and GET /ops/status returned status 200 with these fields.
- **Browser bridge** — Browser extension bridge is currently offline; one stale device fanout-probe-cleanup last seen 2026-08-07T08:44:07.733Z, with 2 pending commands.
  - evidence: GET /browser/status returned online:false and pendingCommands:2.
- **Mac inventory** — Owner Mac is MacBook-Air-6.local, Darwin arm64, macOS 26.5.2, timezone America/New_York, with 123 applications including AI Pendant Agent, Safari, Google Chrome, Xcode, J-Link tools, and many productivity apps.
  - evidence: GET /machine-context and GET /ops/status returned host inventory.
- **Relay connectivity** — Cloud relay v1.1.0 is configured and reachable, pairing required, speech-to-text configured, mac bridge online; pendant pipeline telemetry, speech, persistent state, and durable audio are enabled. Voice model gpt-realtime-2.1; TTS is macOS say 24kHz PCM with tts-1 fallback.
  - evidence: GET /ops/snapshot payload.relay returned these fields.
- **Pendant hardware constraints** — Remote prototype pendant is nRF9160 DK Cortex-M33 64MHz, 211,608B app RAM, 1MB flash, one button/LED, single full-duplex I2S; mic capture 15,625Hz, Opus uplink 16kHz/16kbps, playback decode 24kHz/60ms then 31,250Hz I2S. ESP32 HUZZAH32 bridge resamples 31,250→44,100 and SBC A2DP source; RAM is tight.
  - evidence: get_hardware_spec pendant/io/audio/bridge.

## What it asked for

### `t8-rb0y` (tool) — propose_capability_or_change
- why: The owner explicitly requires this round's proposal to be recorded through the proposal tool, but that tool is not present in my available tool namespace. I need the proposal recorder rather than merely writing text.

```json
{
  "type": "object",
  "properties": {
    "kind": {
      "type": "string",
      "enum": [
        "capability",
        "change"
      ]
    },
    "title": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "owner_value": {
      "type": "string"
    },
    "required_changes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "kind",
    "title",
    "description",
    "owner_value",
    "required_changes"
  ]
}
```

