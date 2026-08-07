# Harness derivation — faculty-action — round 6

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness** — Mac local agent v0.5.0 is reachable and relay-connected, but not ready for GUI automation: Accessibility trusted=false and Screen Recording granted=false. Computer-use loop is disabled; vision upload consent is false. Required permissions are currently missing despite automation grants being cached.
  - evidence: GET /ops/status returned permissions.accessibility.trusted=false, screenRecording.granted=false, computerUse.loopEnabled=false, ready=false.
- **browser bridge** — Authenticated browser work cannot execute now: browser bridge is offline with two pending commands; last seen extension fanout-probe-cleanup is offline. Safari/bridge polling must be restored before browser actions can run.
  - evidence: GET /browser/status returned online=false, pendingCommands=2; recent GET /jobs entries failed browser_navigate with explicit offline error.
- **audio pipeline** — The live pipeline has produced a valid 24 kHz mono PCM TTS response (160.8 KiB, 3430 ms, 0 clipped samples), while pendant capture telemetry is 15,625 Hz PCM. Hardware remains prototype nRF9160 DK + ESP32 bridge with 24 kHz playback decode and 31,250 Hz I2S wire clock.
  - evidence: GET /pipeline returned TTS event metadata sampleRate=24000, channels=1, bitsPerSample=16, pcmBytes=164650, clippedSamples=0 and inputTelemetry sampleRate=15625.
- **project state** — Active project is AI Pendant Simulator at /Users/evanliu/agentic-gadget/software/ai-pendant-simulator; current recorded last work was an order-page status copy task, and open threads include notes recent and project-directory investigation.
  - evidence: GET /projects/active returned project path, summary, goals, and openThreads.
- **pendant hardware constraints** — Pendant has one full-duplex I2S peripheral shared by mic/speaker, mic capture 15,625 Hz, SD over SPI only for failed-upload buffering, and no battery gauge. Any 24 kHz end-to-end change must preserve byte-identical full-duplex I2S TX/RX configuration and account for limited 211,608 B app RAM.
  - evidence: get_hardware_spec(io), get_hardware_spec(storage), get_hardware_spec(power), get_hardware_spec(pendant), get_hardware_spec(audio).

## What it asked for

### `t6-ttgt` (tool) — propose_capability_or_change
- why: The owner explicitly requires recording a novel capability/change, and the proposal-recording tool is not present in my currently exposed tool set. Without it, any proposal text is discarded.

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
    "rationale": {
      "type": "string"
    },
    "requirements": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "novelty_note": {
      "type": "string"
    }
  },
  "required": [
    "kind",
    "title",
    "description",
    "rationale",
    "requirements",
    "novelty_note"
  ]
}
```

### `t7-0qz8` (tool) — propose_change
- why: The owner requires a persisted proposal, but no propose_change tool is exposed in this round. This is needed to record a hardware-level capability without pretending current wiring is sufficient.

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
    "requirements": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "novelty_note": {
      "type": "string"
    }
  },
  "required": [
    "title",
    "description",
    "rationale",
    "requirements",
    "novelty_note"
  ]
}
```

## Its own summary

Recon complete. The Mac local agent (v0.5.0) and Cloudflare relay are reachable, relay pairing is configured, and the active project is AI Pendant Simulator at /Users/evanliu/agentic-gadget/software/ai-pendant-simulator. The action surface can run reversible Mac actions and status reads, but GUI automation is not ready: Accessibility is untrusted, Screen Recording is missing, and the computer-use loop is disabled. Browser actions are blocked because the Safari/browser bridge is offline with two pending commands. The audio path currently demonstrates valid 24 kHz mono PCM TTS (24 kHz, 16-bit, 0 clipped samples), but pendant capture remains 15,625 Hz and the prototype has one shared full-duplex I2S peripheral, limited RAM, SD-only failure buffering, and no battery gauge. I recorded these findings and notified perception, judgement, and unified.

**Biggest unknown:** Whether the orchestrator's pending permission/tool grants will actually be applied this round. To do useful firmware work I still need the previously requested Mac build/device inspection capability and permission to inspect the simulator and connected serial/J-Link devices; to validate audio I still need the pending 24 kHz acceptance criteria. To do GUI/browser work, Accessibility + Screen Recording must become granted and the browser bridge must be enabled/polling. I did not repeat those requests because they were already outstanding.

