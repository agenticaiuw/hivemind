# Harness derivation — faculty-action — round 11

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness** — Mac local agent is live (v0.5.0), relay reachable, full-control planner enabled, but readiness is false because Accessibility trusted=false and Screen Recording granted=false; no requiredMissing/optionalMissing fields despite those two explicit missing permissions.
  - evidence: GET /ops/status returned agent.permissions.accessibility.trusted=false, screenRecording.granted=false, ready=false; health/capabilities returned 200 and tokenConfigured=true.
- **audio pipeline** — Playback path is demonstrably 24 kHz mono PCM end-to-end at Mac TTS/upload, while current capture remains 15,625 Hz and telemetry indicates transcription duration from 15,625 Hz PCM; this is not yet a symmetric 24 kHz superwideband path.
  - evidence: get_hardware_spec(audio) says 15,625 Hz I2S capture and 24 kHz on-device decode playback; GET /pipeline latest completed run reports 24,000 Hz mono PCM, 164,650 bytes, 3,430 ms, and inputTelemetry sampleRate=15625.
- **browser bridge** — Browser device reports online but no active tab metadata and two pending commands; prior browser jobs failed because extension was not polling/offline. Browser work remains unreliable until polling is verified.
  - evidence: GET /browser/status: online=true, home-chrome online=true, tabId/tabUrl empty, pendingCommands=2. GET /jobs includes repeated browser_navigate failures stating extension offline and must be enabled/polling.
- **hardware constraints** — Pendant prototype is nRF9160 Cortex-M33 64 MHz with 211,608 B app RAM and ~87% one-core rough load when Opus encode+decode both run; ESP32 bridge is dual-core 240 MHz/320 kB DRAM and resamples 31,250→44,100 for SBC-only A2DP.
  - evidence: get_hardware_spec(pendant/audio/bridge).
- **active project** — Active Mac project is AI Pendant Simulator at /Users/evanliu/agentic-gadget/software/ai-pendant-simulator; goals include reliable voice interaction and current owner memory says ship 24 kHz superwideband audio path end to end.
  - evidence: GET /projects/active returned project id proj_pendant, path and goals; owner discover remembered Now item says ship 24 kHz superwideband audio path end to end.
- **grants visibility** — No newly granted capabilities are exposed in the granted category this round; previously requested build/device inspection tool and permissions are not available through the tool surface.
  - evidence: list_capabilities returned granted count 0; tools category contains only status/action/browser/search/delegation/job-status tools, with no mac_read_build_and_devices.

## What it asked for

### `t13-rlcc` (tool) — propose_capability_or_change
- why: The user explicitly requires recording a new owner-facing capability or implementation change, but no propose_capability/propose_change tool is present in the currently exposed tool surface. I need the recorder to persist the proposal rather than emit discarded text.

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
    "owner_outcome": {
      "type": "string"
    },
    "required_change": {
      "type": "string"
    },
    "layer": {
      "type": "string",
      "enum": [
        "pendant",
        "firmware",
        "bridge",
        "relay",
        "mac-agent",
        "browser-harness",
        "memory",
        "audio"
      ]
    },
    "why_not_backlog": {
      "type": "string"
    }
  },
  "required": [
    "kind",
    "title",
    "owner_outcome",
    "required_change",
    "layer",
    "why_not_backlog"
  ]
}
```

## Its own summary

Environment reconnaissance complete. The Mac agent and Cloudflare relay are live, project is AI Pendant Simulator, and the owner's active goal is shipping a 24 kHz superwideband audio path end to end. Playback already produces 24 kHz mono PCM, but capture/telemetry is still 15,625 Hz; the prototype's nRF9160 has tight CPU/RAM headroom. Mac readiness remains false because Accessibility and Screen Recording are not enabled. Browser status says online but has no active tab and prior browser jobs failed because the extension was not polling. No newly granted build/device-inspection tool or permissions are exposed this round.

**Biggest unknown:** Whether the intended 24 kHz acceptance criteria require 24 kHz microphone capture/uplink, or only a 24 kHz playback/output contract; and the actual build/serial/J-Link results, since the requested mac_read_build_and_devices capability is still unavailable. I still need that tool plus the already-requested hardware inspection permission, and the Accessibility/Screen Recording/browser-bridge grants before I can safely validate or change the system.

