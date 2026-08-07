# Harness derivation — faculty-action — round 5

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-health** — Mac Local Agent v0.5.0 is live on port 8000 and authenticated routes are configured; relay is reachable and mac bridge online.
  - evidence: GET /health returned 200 service AI Pendant Mac Local Agent version 0.5.0; GET /ops/status returned relay reachable=true and macBridgeOnline=true.
- **mac-control-readiness** — Full-control Mac automation is not ready: Accessibility trusted=false and Screen Recording granted=false; agent reports ready=false. Automation grants for System Events, Finder, Reminders, Calendar, Mail, Safari, Chrome, VS Code and others are cached/granted.
  - evidence: GET /ops/status response permissions: accessibility.trusted=false, screenRecording.granted=false, requiredMissing=[], ready=false; automation map shows granted=true.
- **browser-bridge** — Browser extension bridge is offline, with two pending commands; browser actions cannot execute until Safari extension is enabled and polling.
  - evidence: GET /browser/status returned online=false, device fanout-probe-cleanup offline, pendingCommands=2. Recent /jobs entries explicitly failed browser_navigate with this reason.
- **audio-path** — Pendant audio path is asymmetric: I2S mic capture 15,625 Hz, Opus uplink 16 kHz/16 kbps; playback Opus decode 24 kHz/60ms frames resampled to 31,250 Hz I2S wire clock and ESP32 resamples 31,250->44,100 for SBC A2DP. Successful pipeline telemetry confirms 24 kHz mono PCM TTS output.
  - evidence: get_hardware_spec audio/bridge; GET /pipeline showed TTS event 24,000 Hz mono PCM, 164650 bytes, 3430 ms, 0 clipped samples.
- **pendant-prototype** — Pendant is prototype nRF9160 DK: Cortex-M33 64MHz, 211,608B app RAM, 1MB flash, Zephyr/NCS 3.4.0; SD is failure buffer only for upload outages.
  - evidence: get_hardware_spec pendant and storage.

## What it asked for

### `t5-s5a4` (tool) — propose_change
- why: The owner explicitly requires recording a new capability/change this round, but the proposal-recording tool is not present in the currently exposed tool set. A durable proposal call is needed rather than a text-only response.

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
    "requirements": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "non_backlog_novelty": {
      "type": "string"
    }
  },
  "required": [
    "kind",
    "title",
    "description",
    "owner_value",
    "requirements",
    "non_backlog_novelty"
  ]
}
```

## Its own summary

Environment is mapped for action. The Mac agent and relay are healthy, but two concrete blockers remain: macOS Accessibility/Screen Recording are not enabled (agent ready=false), and the Safari browser bridge is offline with two queued commands. The pendant is a prototype nRF9160 path with 15,625-Hz capture/16-kHz Opus uplink and 24-kHz decoded playback; the ESP32 bridge converts to 44.1-kHz SBC A2DP. A real pipeline run already produced clean 24-kHz mono PCM TTS. I recorded these findings and notified unified, judgement, perception, and Mac planner. To do useful build/action work I still need the previously requested build/device inspection capability and change-proposal capability, plus the pending permissions and explicit 24-kHz acceptance criteria; I did not re-request them per instruction.

**Biggest unknown:** Whether the orchestrator's intended audio acceptance target is strictly end-to-end 24-kHz fidelity (including the 31.25-kHz wire clock and 44.1-kHz SBC bridge), and whether the pending macOS/browser grants will actually be applied this round.

