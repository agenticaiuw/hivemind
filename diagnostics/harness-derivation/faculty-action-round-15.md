# Harness derivation — faculty-action — round 15

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent** — Mac local agent is live at localhost:8000, version 0.5.0; /health is public and /capabilities confirms 120 routes, bearer auth configured, and groups for pipeline audio, projects, jobs, browser, research, routines, and more.
  - evidence: GET /health returned 200 service AI Pendant Mac Local Agent version 0.5.0; GET /capabilities returned generatedAt 2026-08-07T09:24:55Z, routeCount 120, tokenConfigured true, and route groups.
- **audio** — Pendant audio currently captures I2S at 15,625 Hz and Opus-encodes uplink at 16 kHz/16 kbps; playback decodes Opus at 24 kHz/60 ms then resamples to 31,250 Hz I2S. Both encode/decode consume ~87% of one core. It is explicitly prototype hardware/firmware.
  - evidence: get_hardware_spec(audio) returned mic 15,625 Hz, uplink 16 kHz, playback 24 kHz, 31,250 Hz wire clock, libopus 1.6.1, and status PROTOTYPE.
- **owner-priority** — Owner memory says the next round should derive agent changes from harness ledger and ship the 24 kHz superwideband audio path end to end on the pendant; timezone is America/Chicago. Owner permits browser read/click and reminders/notes without asking, but requires confirmation before sending mail, deleting files, or buying.
  - evidence: discover(owner) returned remembered Now/Relevant text and permissions.
- **audio-bridge** — ESP32 HUZZAH32 bridge receives 31,250 Hz I2S, resamples to 44,100 Hz with polyphase FIR, then Bluetooth A2DP SBC-only output is hard-locked to 44.1 kHz stereo; RAM is tight and a 44 kB buffer previously starved Bluetooth into silence.
  - evidence: get_hardware_spec(bridge) returned role, fixed 44.1 kHz SBC limitation, and RAM starvation note.
- **audio-io** — Pendant has exactly one full-duplex I2S peripheral with byte-identical TX/RX configuration; a new audio path must share it. Only one button and LED exist; I2C/SPI are currently unused.
  - evidence: get_hardware_spec(io) returned full-duplex I2S constraint and available buses.
- **audio-storage** — Pendant microSD is a failure buffer only: audio is written to SD only when a chunk upload cannot be uploaded, despite FATFS/exFAT support.
  - evidence: get_hardware_spec(storage) returned owner standing rule and SD implementation.

## What it asked for

### `t17-5f7a` (tool) — propose_capability
- why: Owner explicitly requires recording a new capability proposal this round; the tool is not present in the available tool namespace, so text would be discarded and no proposal can be recorded.

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
        "change"
      ]
    },
    "owner_value": {
      "type": "string"
    },
    "implementation_requirements": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "title",
    "description",
    "rationale",
    "layer",
    "owner_value",
    "implementation_requirements"
  ]
}
```

## Its own summary

Environment recon complete for this round. The Mac agent is live (v0.5.0, 120 authenticated routes) and explicitly exposes pipeline/audio, jobs, browser, research, routines, and project surfaces. Hardware evidence shows the current path is not 24 kHz end-to-end: mic capture 15,625 Hz -> Opus uplink 16 kHz, playback Opus decode 24 kHz -> 31,250 Hz I2S -> ESP32 resample to 44.1 kHz SBC/A2DP. The single full-duplex I2S peripheral must be shared; bridge output is fixed 44.1 kHz and RAM constrained. Owner priority and approval rules are known. I recorded all findings. I still cannot inspect/build firmware or connected serial/J-Link devices because the previously requested permission/tool remain unanswered, and cannot propose/execute engineering changes because the requested proposal tool/grant remains unanswered.

**Biggest unknown:** The exact firmware/bridge implementation state and test/acceptance results for the desired 24 kHz superwideband path; resolving that requires the pending Mac read/build/device-inspection capability and owner-approved change proposal mechanism.

