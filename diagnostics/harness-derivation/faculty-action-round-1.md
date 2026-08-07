# Harness derivation — faculty-action — round 1

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac agent control readiness** — Mac Local Agent v0.5.0 is live on localhost:8000 and relay reachable, but full control is not ready because Accessibility trusted=false and Screen Recording granted=false; browser extension is offline with 0 tabs.
  - evidence: GET /ops/status returned agent ready:false, accessibility trusted:false, screenRecording granted:false, browser online:false; GET /health returned service/version.
- **available action surfaces** — Production action tools are get_mac_status, mac_run_actions (1–3 reversible actions), browser_run_actions, mac_delegate for complex workflows, web_search/read_web_page, and relay_job_status. Browser work is currently blocked by extension offline.
  - evidence: describe() for each tool plus GET /browser/status.
- **audio hardware path** — Pendant is prototype nRF9160 DK, one full-duplex I2S peripheral, 211,608B app RAM/1MB flash, LTE-M half-duplex; ESP32 bridge resamples 31.25kHz to 44.1kHz and SBC-only A2DP. Audio path cannot be changed remotely by this agent with current grants.
  - evidence: get_hardware_spec pendant/io/bridge/network and faculty-perception live telemetry.
- **owner constraints** — Owner wants end-to-end 24kHz audio and reminders/notes can be created without confirmation; confirmation is required before sending mail, deleting files, or buying. Work is on Apple Silicon Mac, zsh, America/Chicago; notes/drafts in ~/AI-Pendant-Workspace.
  - evidence: discover(owner) returned remembered owner policy and goals.

## What it asked for

### `p1-6562` (permission) — Read and build the pendant firmware in /Users/evanliu/agentic-gadget/software/ai-pendant-simulator, plus inspect connected serial/J-Link devices; do not flash or modify hardware without a separate approval
- why: Owner's explicit goal is to ship and verify the end-to-end 24 kHz audio path, but my current action surface only exposes Mac/browser orchestration and hardware is remote. I need repository/build/device visibility to determine whether an implementation is possible and produce evidence.
- risk it sees: Builds may create local artifacts and device inspection may expose serial metadata; no firmware flash or destructive changes would be performed under this grant. Accessibility and Screen Recording remain unnecessary for shell-only work if the shell route is authorized.

## Its own summary

Environment discovered. This agent runs on the owner's Apple Silicon MacBook and can orchestrate reversible Mac/browser actions, but the live Mac agent is not ready for GUI control (Accessibility and Screen Recording missing) and the browser extension is offline with zero tabs. Relay is online. The owner's project is AI Pendant Simulator at /Users/evanliu/agentic-gadget/software/ai-pendant-simulator; workspace is ~/AI-Pendant-Workspace. Hardware is a prototype nRF9160 DK with one shared full-duplex I2S peripheral, LTE-M half-duplex, 16 kHz/16 kbps uplink, 24 kHz decode, 31.25 kHz I2S, then ESP32 44.1 kHz SBC A2DP. I recorded these findings, notified judgement/perception/planner, and queued a permission request to inspect/build firmware and inspect serial/J-Link without flashing.

**Biggest unknown:** Whether the pendant firmware can actually be built and tested from this Mac, and whether a J-Link/serial device is connected. I need the queued read/build/device-inspection permission (and later a separate explicit flash grant if warranted) to turn the owner's 24 kHz goal into verified action.

