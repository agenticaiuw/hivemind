# Harness derivation — faculty-action — round 3

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **pendant-audio** — Current audio implementation captures at 15,625 Hz, Opus uplink 16 kHz/16 kbps; playback decodes 24 kHz in 60 ms frames and resamples to 31,250 Hz I2S wire clock. Encode ~15 ms/call; decode ~25.4 ms/60 ms packet; both ~87% of one Cortex-M33 core.
  - evidence: functions.describe(audio)
- **mac-agent** — Mac local agent v0.5.0 is live at localhost:8000 and relay bridge is online, but agent readiness is false because Accessibility and Screen Recording permissions are missing. Browser extension is offline; no browser commands can run.
  - evidence: GET /ops/status and GET /browser/status returned online:false; GET /capabilities returned permission details.
- **project** — Active project is AI Pendant Simulator at /Users/evanliu/agentic-gadget/software/ai-pendant-simulator; owner goal explicitly includes shipping the 24 kHz superwideband audio path end to end on the pendant.
  - evidence: GET /projects/active and owner discover output.
- **hardware-inspection** — Mac inventory includes JFlash/JLinkConfig/JLink tools and nRF Connect for Desktop, but no connected serial/J-Link device state was exposed by current discovery or HTTP probes.
  - evidence: GET /machine-context listed relevant tools/apps; no device enumeration route/result appeared.
- **unrecorded-proposal** — Owner should have a genuinely end-to-end 24 kHz superwideband voice path, including microphone capture—not merely 24 kHz playback—with a hardware-in-the-loop release gate measuring sample-rate integrity, latency, clipping, packet-loss concealment, CPU headroom, and power. This requires coordinated microphone/I2S clocking, firmware scheduling/resource changes, Opus and relay sample-rate contract updates, and connected-device validation; it must not be reduced to a software-only shim.
  - evidence: Hardware discovery reports 15,625 Hz I2S capture and 16 kHz Opus uplink, while playback alone decodes at 24 kHz; owner memory states the goal is to ship the 24 kHz superwideband audio path end to end.

## What it asked for

_Nothing._
