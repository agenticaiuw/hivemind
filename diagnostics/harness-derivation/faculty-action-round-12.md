# Harness derivation — faculty-action — round 12

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness** — Mac local agent v0.5.0 and relay are reachable, token configured, full-control planner enabled, but readiness is false because Accessibility trusted=false and Screen Recording granted=false. Browser extension home-chrome is offline with 2 pending commands.
  - evidence: GET /ops/status returned 200 with agent.ready=false, accessibility.trusted=false, screenRecording.granted=false, browser.online=false, pendingCommands=2.
- **audio pipeline** — Live pipeline has completed 24 kHz mono PCM TTS: 164650 bytes, 3430 ms, 24000 Hz, no clipping; relay accepted response. Existing capture telemetry is 15625 Hz PCM and uplink conversion remains distinct.
  - evidence: GET /pipeline returned pipeline job_165a9c9a... events showing TTS 24000 Hz mono PCM, relay_result done; inputTelemetry sampleRate=15625.
- **hardware constraints** — Pendant is nRF9160 Cortex-M33, 211608 B app RAM, one full-duplex I2S peripheral shared by mic/speaker; bridge is ESP32 A2DP SBC-only at locked 44.1 kHz stereo. Current playback decodes Opus 24 kHz then resamples to 31250 Hz I2S; LTE-M half-duplex contention caused 388 uplink packets dropped in a recent call.
  - evidence: get_hardware_spec(all) returned firmware, I2S, bridge, codec, network measurements.
- **browser capability** — Browser actions cannot run currently because extension is offline; prior jobs failed with explicit instruction to open Safari and enable AI Pendant Browser Bridge. Public-page reading can use read_web_page/web_search without browser bridge.
  - evidence: GET /browser/status returned online=false; GET /jobs showed failed browser_navigate reason extension offline.
- **owner policy** — Owner timezone is America/Chicago; browser may read/click without asking; confirm before sending mail, deleting files, or buying; reminders/notes may be created without asking; replies should be one short spoken sentence unless detail requested.
  - evidence: discover(owner) remembered section.
- **Mac API surface** — Authenticated local agent exposes 120 routes including pipeline telemetry/audio, evidence capsules, staged forms, mail triage (compose/store only, never send), reminders, watches, briefing/research, jobs with receipts/undo, and machine context. Auth is Bearer AGENT_TOKEN or loopback dashboard cookie.
  - evidence: GET /capabilities returned 200 with routeCount=120, group descriptions and auth contract.

## What it asked for

### `t14-nlqk` (tool) — propose_capability
- why: The owner explicitly requires recording a new capability proposal this round; the proposal recorder is absent from the exposed tool surface, so I cannot persist the requested idea without it.

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string"
    },
    "owner_value": {
      "type": "string"
    },
    "what_changes": {
      "type": "string"
    },
    "dependencies": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "risks": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "title",
    "owner_value",
    "what_changes"
  ]
}
```

## Its own summary

Round 12 reconnaissance complete. The Mac agent and relay are reachable and fully configured at the service level, but not ready for GUI work: Accessibility is untrusted, Screen Recording is denied, and the browser bridge is offline with two queued commands. The authenticated Mac API exposes 120 routes, including pipeline telemetry/audio, staged forms, mail triage, reminders, watches, research/briefings, receipts and undo. A live pipeline receipt proves 24 kHz mono PCM TTS is being generated and accepted by the relay (24,000 Hz, 3.43 s, no clipping), while current pendant capture remains 15,625 Hz and the hardware has one shared full-duplex I2S peripheral. I recorded these findings and asked perception, judgement, Mac planner, and unified peers for current blockers. I still need the already-requested firmware build/device-inspection capability plus permission to inspect the simulator and connected serial/J-Link devices, the 24 kHz acceptance criteria, and owner priority/approval policy before I can safely implement or propose the end-to-end audio change. GUI/browser work additionally remains blocked until the pending macOS permissions and bridge enablement are actually granted.

**Biggest unknown:** Whether the owner intends 24 kHz to mean only the cloud/playback output (already evidenced) or also microphone capture/uplink; the acceptance criteria and build/device inspection grant are still outstanding.

