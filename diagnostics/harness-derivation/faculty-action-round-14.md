# Harness derivation — faculty-action — round 14

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent readiness** — Mac local agent v0.5.0 is healthy and bridge/relay reachable, but readiness is false because Accessibility trusted=false and Screen Recording granted=false; browser extension home-chrome is offline with 2 pending commands.
  - evidence: GET /health returned 200 service AI Pendant Mac Local Agent v0.5.0. GET /ops/status returned permissions.accessibility.trusted=false, screenRecording.granted=false, ready=false, and browser.online=false/pendingCommands=2.
- **24 kHz audio path** — Current prototype captures at 15,625 Hz, Opus uplink 16 kHz/16 kbps, decodes playback at 24 kHz in 60 ms frames, resamples to 31,250 Hz I2S wire clock; decode+encode consume about 87% of one Cortex-M33 core. ESP32 then resamples 31,250 to 44,100 for SBC A2DP.
  - evidence: get_hardware_spec(audio), get_hardware_spec(bridge), and get_hardware_spec(pendant) returned these exact firmware constraints.
- **Audio retention backlog** — Audio retention sweeper remains proposed and unimplemented; it is disabled/dry-run, scans only newest 100, has no scheduled invocation, lacks binding-safe deletion and owner pin concept.
  - evidence: describe(chg-a813b918) live backlog entry, status proposed, detailed verified gaps.
- **Browser durable runner** — Browser backend router exists, but durable browser job runner with persistence, retries, and planner result stream remains missing; authenticated private pages intentionally cannot fail over to relay when Safari is offline.
  - evidence: describe(chg-16bc5dee) status proposed and note explicitly says router done, durable runner missing, private-page no-failover.

## What it asked for

### `t16-6m4x` (tool) — propose_capability_or_change
- why: The owner explicitly requires recording a non-backlog capability or change proposal this round, and the previously requested proposal tool is now expected to be available.

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
    "summary": {
      "type": "string"
    },
    "why_now": {
      "type": "string"
    },
    "requirements": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "not_backlog": {
      "type": "boolean"
    }
  },
  "required": [
    "kind",
    "title",
    "summary",
    "why_now",
    "requirements",
    "not_backlog"
  ]
}
```

## Its own summary

Recon complete. The Mac local agent is healthy (v0.5.0), relay reachable, and the Mac bridge is online, but the machine is not ready for GUI/browser execution: Accessibility is untrusted, Screen Recording is not granted, and the browser extension is offline with 2 pending commands. The pendant audio implementation is still a prototype: 15,625-Hz capture, 16-kHz Opus uplink, 24-kHz/60-ms decode, 31,250-Hz I2S wire clock, then ESP32 resampling to 44.1 kHz SBC A2DP; encode+decode use ~87% of one Cortex-M33 core. The audio-retention sweeper and durable browser runner remain proposed/unimplemented. I still need the previously requested owner-side permission actions (Accessibility, Screen Recording, Safari bridge), authorization to inspect/build pendant firmware and connected devices, and the 24-kHz acceptance criteria/approved change plan before I can safely make or verify changes. I recorded all live findings and asked mac-planner, faculty-perception, and faculty-judgement for current status.

**Biggest unknown:** Whether the orchestrator's grants actually authorized firmware inspection/build and whether the owner has completed the required macOS privacy/browser-extension actions; live ops still show those permissions absent.

