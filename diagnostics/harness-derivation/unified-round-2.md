# Harness derivation — unified — round 2

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent** — Mac local agent v0.5.0 is live on localhost:8000 and relay can reach it. Full-control planner is enabled, but computer-use loop is disabled; Accessibility and Screen Recording are ungranted, while requiredMissing is empty yet ready=false. Browser extension is offline.
  - evidence: GET /health returned ok; GET /ops/snapshot returned agent fullControlMode=true, computerUse.loopEnabled=false, accessibility.trusted=false, screenRecording.granted=false, browser.online=false.
- **audio** — Current pendant audio is not end-to-end 24 kHz superwideband: mic captures 15,625 Hz and uplinks Opus at 16 kHz/16 kbps; playback decodes Opus at 24 kHz in 60 ms frames then resamples to 31,250 Hz I2S. Relay TTS does produce 24 kHz mono PCM, but hardware path remains constrained.
  - evidence: get_hardware_spec(audio) reported mic 15,625 Hz, uplink 16 kHz/16 kbps, playback 24 kHz decode and 31,250 Hz I2S; /pipeline telemetry showed input sampleRate 15625 and TTS 24000 Hz mono PCM.
- **hardware** — Pendant is an nRF9160 DK prototype with 64 MHz Cortex-M33, 211,608 B app RAM, 1 MB flash, one full-duplex I2S peripheral with identical TX/RX config, one button and one LED. ESP32 bridge resamples 31,250→44,100 and uses SBC-only A2DP source; RAM is tight.
  - evidence: get_hardware_spec(pendant), (io), and (bridge) returned these constraints.
- **relay** — Cloud relay v1.1.0 is reachable, paired/configured, speech-to-text and durable audio enabled, with mac bridge online. Audio retention is 30 days with sweeping disabled and about 100 recordings stored.
  - evidence: GET /ops/snapshot relay payload and get_hardware_spec(stack) returned these values.
- **owner** — Owner timezone is America/Chicago and they want one short spoken sentence by default; browser reads/clicks are allowed, destructive actions need confirmation. Workspace is ~/AI-Pendant-Workspace; current goal is shipping 24 kHz superwideband audio end-to-end.
  - evidence: discover(owner) remembered projection.

## What it asked for

### `t2-h6u8` (tool) — mac_workspace_edit
- why: The owner's stated goal is to ship the 24 kHz superwideband pendant audio path end-to-end. Reconnaissance shows mismatched 15,625 Hz capture/16 kHz uplink, 24 kHz decode, and 31,250 Hz I2S; implementing and validating this requires editing firmware and relay source files in ~/AI-Pendant-Workspace, then running builds/tests without relying on destructive GUI automation.

```json
{
  "type": "object",
  "properties": {
    "files": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string"
          },
          "patch": {
            "type": "string"
          }
        },
        "required": [
          "path",
          "patch"
        ]
      }
    },
    "commands": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Allowlisted build/test commands to run after edits"
    },
    "dry_run": {
      "type": "boolean",
      "description": "If true, show proposed diffs and commands without writing or executing"
    }
  },
  "required": [
    "files",
    "commands",
    "dry_run"
  ]
}
```

