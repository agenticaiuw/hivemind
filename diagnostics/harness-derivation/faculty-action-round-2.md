# Harness derivation — faculty-action — round 2

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent availability** — Local Mac agent v0.5.0 is live on port 8000 with bearer auth; relay and bridge are reachable, but browser extension is offline. Mac control is not ready because Accessibility and Screen Recording are both ungranted, although automation grants are cached.
  - evidence: GET /capabilities and GET /ops/status returned version 0.5.0, macBridgeOnline true, browser online false, accessibility trusted false, screenRecording granted false, ready false.
- **Owner current project** — Owner's active project is AI Pendant Simulator at /Users/evanliu/agentic-gadget/software/ai-pendant-simulator, with explicit goal to ship the 24 kHz superwideband audio path end to end on the pendant.
  - evidence: owner discovery remembered Now section and GET /projects/active returned proj_pendant at that path.
- **Pendant audio architecture** — Prototype captures I2S at 15,625 Hz, encodes Opus uplink at 16 kHz/16 kbps, decodes playback at 24 kHz in 60 ms frames, resamples to 31,250 Hz I2S wire clock, then ESP32 resamples to 44.1 kHz SBC Bluetooth output. Codec processing consumes about 87% of one core when encode/decode overlap.
  - evidence: get_hardware_spec audio and bridge.
- **Browser availability** — No browser extension is online, with zero pending commands; authenticated browser work cannot currently be executed through the browser surface.
  - evidence: GET /browser/status returned online false and pendingCommands 0.
- **Relay storage** — Cloud relay uses D1 and R2; audio retention is 30 days but sweeping is disabled and approximately 100 recordings are stored, creating an operational cleanup gap.
  - evidence: get_hardware_spec stack.
- **Pendant network bottleneck** — LTE-M uplink/downlink contention is a known failure: 16 kbps uplink plus 24 kbps downlink saturated the link and dropped 388 uplink packets (~7.8 seconds) during simultaneous speech/agent playback.
  - evidence: get_hardware_spec network returned measured diagnostic result.
- **Pendant I2S constraint** — The prototype has exactly one full-duplex I2S peripheral with byte-identical TX/RX configuration; any audio-path change must share it. I2C/SPI are currently unused except SD on SPI.
  - evidence: get_hardware_spec io and storage.
- **SD and power limits** — SD is intended only as a failure buffer when upload fails, not routine audio storage; no battery gauge exists, so charge state cannot be read from the pendant.
  - evidence: get_hardware_spec storage and power.
- **Unrecorded proposal due proposal tools unavailable** — Owner should be able to conduct a genuinely interruption-free, full-duplex wearable conversation during LTE-M contention: the device should preserve intelligibility in both directions, adapt bitrate and packet protection in real time, prioritize speech over nonessential traffic, conceal losses locally, and expose a simple call-quality indication. Achieving this requires a purpose-designed wearable audio/modem architecture (not the current dev kit), an end-to-end congestion controller with uplink/downlink scheduling, jitter/loss concealment and bounded local buffering, plus acceptance tests under simultaneous speech and playback. This is a product-level capability, not a reduction to the current wiring.
  - evidence: Hardware inspection established 388 uplink packets (~7.8 s speech) were dropped when 16 kbps uplink and 24 kbps downlink contended over LTE-M; current board is explicitly prototype and has one shared full-duplex I2S peripheral.

## What it asked for

### `c1-yoa6` (context) — 24 kHz audio path acceptance criteria
- why: The owner's current goal is to ship the 24 kHz superwideband audio path, but the hardware spec only describes the prototype pipeline and does not state the required end-to-end tests, latency/quality targets, or whether build-only validation is sufficient.
- would change: I would select the right read/build/test actions and report concrete pass/fail evidence instead of merely inspecting architecture.

### `t1-go53` (tool) — mac_read_build_and_devices
- why: The active owner goal is shipping the pendant's 24 kHz audio path, but this faculty-action agent has no direct shell/build or serial/J-Link inspection tool. A read-only Mac tool is needed to inspect the granted firmware tree, run bounded build/tests, and enumerate connected debug devices without flashing or modifying hardware.

```json
{
  "type": "object",
  "properties": {
    "working_directory": {
      "type": "string",
      "description": "Absolute path constrained to approved firmware repository."
    },
    "commands": {
      "type": "array",
      "description": "Read-only or build/test commands only; reject writes, flashing, and destructive operations.",
      "items": {
        "type": "string"
      }
    },
    "device_probe": {
      "type": "boolean",
      "description": "If true, enumerate serial ports and J-Link devices without opening or modifying them."
    },
    "timeout_seconds": {
      "type": "integer",
      "minimum": 1,
      "maximum": 600
    }
  },
  "required": [
    "working_directory",
    "commands",
    "device_probe"
  ]
}
```

### `t2-fos6` (tool) — propose_capability_or_change
- why: The requested proposal-recording tool is not exposed in this round, but the owner requires a durable proposal record rather than prose. I need the orchestrator's proposal endpoint to submit the new full-duplex LTE-resilient wearable capability.

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
    "owner_value": {
      "type": "string"
    },
    "required_changes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "evidence": {
      "type": "string"
    }
  },
  "required": [
    "kind",
    "title",
    "owner_value",
    "required_changes",
    "evidence"
  ]
}
```

## Its own summary

Environment is now mapped. The Mac local agent v0.5.0 is reachable and the relay/bridge are online, but agent readiness is false because Accessibility and Screen Recording permissions are missing; the browser extension is offline. The active project is /Users/evanliu/agentic-gadget/software/ai-pendant-simulator and the owner's explicit goal is the end-to-end 24 kHz audio path. Hardware evidence shows a prototype nRF9160 + ESP32 bridge, one shared full-duplex I2S peripheral, Opus decode at 24 kHz, and a serious LTE-M contention failure (388 uplink packets dropped during simultaneous playback). I recorded all findings. I requested a read/build/device-probe tool constrained to the approved repo and non-mutating operations, and requested acceptance criteria context.

**Biggest unknown:** Current firmware branch/build/test status and connected serial/J-Link devices remain unknown because I lack the granted shell/device inspection capability. Also unknown are the concrete acceptance criteria for the 24 kHz path (latency, packet-loss tolerance, audio quality, and whether hardware flashing is authorized).

