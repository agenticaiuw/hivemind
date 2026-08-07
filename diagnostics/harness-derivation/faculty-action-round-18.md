# Harness derivation — faculty-action — round 18

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness** — Mac local agent is live at localhost:8000, version 0.5.0, but reports ready=false because Accessibility and Screen Recording are not granted; browser extension is offline with 2 pending commands.
  - evidence: GET /ops/status returned tokenConfigured=true, accessibility.trusted=false, screenRecording.granted=false, browserExtension.online=false, pendingCommands=2.
- **browser execution** — Browser actions cannot currently run: home-chrome extension is offline and has no tabs; enabling/polling the browser bridge is required for logged-in page work.
  - evidence: GET /browser/status returned online=false, tabId=null, tabCount null; GET /jobs included repeated browser_navigate failures explicitly saying to open Safari and enable AI Pendant Browser Bridge.
- **relay and audio telemetry** — Cloud relay is reachable and Mac bridge online. Existing pipeline telemetry confirms macOS speech renders 24 kHz mono PCM successfully (example 160.8 KiB, 3430 ms, 24000 Hz), while pendant capture telemetry is 15625 Hz PCM; hardware spec says playback decodes at 24 kHz then outputs 31250 Hz I2S.
  - evidence: GET /ops/status relay payload reachable=true and macBridgeOnline=true; GET /pipeline includes tts metadata sampleRate=24000 and inputTelemetry sampleRate=15625; get_hardware_spec audio/io reported the decode/resampling path.
- **timezone conflict** — Owner memory says authoritative timezone America/Chicago, but live Mac machine-context reports America/New_York. I must not choose between them without the pending authoritative-owner-timezone context.
  - evidence: owner discovery remembered.text says timezone America/Chicago; GET /machine-context returned machine.timezone America/New_York.
- **hardware access** — Pendant and ESP32 bridge are remote prototype hardware; this agent cannot directly inspect or flash them. Pendant is nRF9160 DK with one full-duplex I2S peripheral; ESP32 bridge is HUZZAH32 with fixed SBC-only 44.1 kHz A2DP source.
  - evidence: get_hardware_spec pendant/io/bridge each states you are on MacBook and devices are remote; audio/io/bridge details.
- **available action surface** — Production voice tools available are status reads, reversible Mac actions, browser actions, public web search/page reads, Mac delegation, and relay job status. No firmware build/device-inspection capability is currently exposed in the discovered tools.
  - evidence: discover(tools) returned exactly 7 tools and none build firmware or inspect serial/J-Link devices; GET /capabilities describes Mac agent routes but not a firmware-specific tool.

## What it asked for

### `t20-vb7y` (tool) — propose_change
- why: The owner explicitly requires me to record a new capability/change this round, but propose_change is not present in the currently exposed tool namespace. I need the recording tool itself, not merely text output.

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
      "type": "string"
    },
    "prerequisites": {
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
    "prerequisites"
  ]
}
```

## Its own summary

Recon complete. The Mac local agent and Cloudflare relay are reachable, but Mac readiness is false: Accessibility and Screen Recording are still ungranted, and the browser bridge is offline with two queued commands, so browser work cannot execute. The live path is asymmetric: successful TTS is 24 kHz mono PCM, pendant capture is 15,625 Hz, playback decodes at 24 kHz and sends 31,250 Hz I2S; the nRF9160 and ESP32 are remote prototype hardware. I also found an unresolved timezone conflict (owner memory America/Chicago versus machine context America/New_York). No firmware build/serial/J-Link inspection tool is exposed. I have recorded all findings and alerted perception, planning, realtime, and judgement peers.

**Biggest unknown:** Whether the orchestrator's pending grants/context will arrive later: firmware build/device inspection access, the 24 kHz acceptance criteria, authoritative owner timezone and priorities/approval policy, plus macOS Accessibility/Screen Recording and browser-bridge enablement. Without those, I can route ordinary reversible Mac actions but cannot validate or ship the requested end-to-end pendant audio change.

