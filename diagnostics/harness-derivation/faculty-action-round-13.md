# Harness derivation — faculty-action — round 13

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent readiness** — Mac agent v0.5.0 is live and relay-connected, but ready=false because Accessibility is not trusted and Screen Recording is not granted; browser extension home-chrome is offline with 2 pending commands. Automation grants are present, but GUI/computer-use is unavailable until permissions are enabled.
  - evidence: GET /ops/status returned HTTP 200: accessibility.trusted=false, screenRecording.granted=false, browserExtension.online=false, pendingCommands=2, ready=false.
- **Pendant audio path** — Current prototype captures at 15,625 Hz, uplinks Opus 16 kHz/16 kbps, decodes at 24 kHz/60 ms, then outputs 31,250 Hz I2S to ESP32; libopus decode ~25.4 ms per 60 ms packet and encode ~15 ms, ~87% of one core combined.
  - evidence: get_hardware_spec(audio) returned codec, rates, timing, and CPU estimate.
- **Hardware topology** — Pendant is nRF9160 DK Cortex-M33 64 MHz with 211,608 B app RAM and 1 MB flash; exactly one full-duplex I2S peripheral shared by mic/speaker. ESP32 HUZZAH32 resamples 31,250→44,100 and A2DP SBC-only; 44 kB buffer previously starved Bluetooth.
  - evidence: get_hardware_spec(pendant), get_hardware_spec(io), and get_hardware_spec(bridge).
- **Mac agent routes** — Live manifest exposes 120 authenticated routes including execute/jobs, browser bridge, pipeline telemetry/audio, research, routines, reminders, mail triage, watches, and permissions/ops status. Only /health and dashboard are public; bearer token required for operational routes.
  - evidence: GET /capabilities HTTP 200 returned route manifest and auth policy.
- **Timezone conflict** — Mac machine-context reports timezone America/New_York, while owner memory says authoritative timezone America/Chicago; do not schedule or interpret times until orchestrator resolves this conflict.
  - evidence: GET /machine-context returned timezone America/New_York; owner discover returned remembered timezone America/Chicago.
- **GUI input safety** — Observation confirms synthesized UI events do not reach the screen: Accessibility is granted to a different binary, eventsPost=false, inputReachability=failed. UI actions may report success while doing nothing; do not trust receipts until AI Pendant Agent itself is granted Accessibility.
  - evidence: GET /observe HTTP 200 returned uiActionsWillReachTheScreen=false and consequence warning.
- **Browser state** — Although browser extension heartbeat is offline, local observation shows 3 durable browser sessions/tabs, including time.is/UTC and Selenium/httpbin test pages; browser commands remain unsafe/unavailable until extension polls.
  - evidence: GET /observe listed 3 browser sessions; GET /browser/status showed online=false and 2 pendingCommands.

## What it asked for

### `t15-ksu7` (tool) — propose_change
- why: The user explicitly requires recording a new capability/change this round, but the proposal tool is not present in the currently exposed tool set. Need to record an audio-path validation change without restating backlog items.

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "rationale": {
      "type": "string"
    },
    "layer": {
      "type": "string",
      "enum": [
        "capability",
        "relay",
        "firmware",
        "mac",
        "browser-harness",
        "memory",
        "audio",
        "hardware"
      ]
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
    "not_in_backlog": {
      "type": "boolean"
    }
  },
  "required": [
    "title",
    "description",
    "rationale",
    "layer",
    "owner_value",
    "required_changes",
    "not_in_backlog"
  ]
}
```

## Its own summary

Recon complete. The Mac local agent is live (v0.5.0) and relay-connected, with authenticated execution, pipeline telemetry/audio, jobs, browser, routines, research, and workspace routes. However, it is not action-ready for GUI work: Accessibility is not trusted for the actual AI Pendant Agent binary, Screen Recording is absent, synthesized input does not reach the screen, and the browser bridge is offline with 2 queued commands. The hardware path is confirmed as prototype 15,625-Hz mic capture → Opus 16 kHz uplink → 24-kHz decode → 31,250-Hz full-duplex I2S → ESP32 44.1-kHz SBC/A2DP. To do useful implementation work I still need the already-requested Mac build/device inspection capability, permission to inspect the firmware and connected serial/J-Link devices (without flashing), the owner's 24-kHz acceptance criteria, and the owner's priorities/approval policy. I also need resolution of the timezone conflict: owner memory says America/Chicago, machine-context says America/New_York. Browser work additionally requires the already-requested Accessibility/Screen Recording enablement and Safari bridge polling. I recorded all findings.

**Biggest unknown:** Whether the 24-kHz end-to-end path is actually acceptable under the owner's criteria, and what exact firmware/build/device state is present; I cannot inspect or change it until the pending tool and permission grants arrive.

